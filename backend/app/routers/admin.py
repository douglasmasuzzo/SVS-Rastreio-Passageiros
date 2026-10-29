"""Painel administrativo: indicadores, viagens, validação e exportação."""

from __future__ import annotations

import csv
import io
from datetime import date, timedelta
from statistics import fmean

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from ..db import get_db
from ..domain import STATUS_AUTORIZACAO
from ..models import Autorizacao, Embarque, Posicao, Veiculo, Viagem
from ..schemas import (
    AutorizacaoAdminOut,
    AutorizacaoOut,
    KpisOut,
    ListaAutorizacoesAdminOut,
    ListaViagensAdminOut,
    ValidacaoIn,
    ViagemAdminOut,
)
from ..services import audit, tracking
from ..timeutil import utcnow
from .deps import exigir_admin, ip_do_cliente

router = APIRouter(prefix="/api/v1/admin", tags=["Administração"], dependencies=[Depends(exigir_admin)])

TOLERANCIA_OTIF_MIN = 15
LIMITE_EXPORTACAO = 50_000


def _viagens_do_dia(db: Session, dia: date) -> list[Viagem]:
    return list(
        db.scalars(
            select(Viagem)
            .where(Viagem.data == dia)
            .options(joinedload(Viagem.veiculo), joinedload(Viagem.motorista))
            .order_by(Viagem.partida_prevista)
        ).all()
    )


def _contagens(db: Session, ids: list[int]) -> tuple[dict[int, int], dict[int, int]]:
    if not ids:
        return {}, {}
    aprovadas = {
        viagem_id: total
        for viagem_id, total in db.execute(
            select(Autorizacao.viagem_id, func.count(Autorizacao.id))
            .where(Autorizacao.viagem_id.in_(ids), Autorizacao.status == "APROVADA")
            .group_by(Autorizacao.viagem_id)
        )
    }
    embarques = {
        viagem_id: total
        for viagem_id, total in db.execute(
            select(Autorizacao.viagem_id, func.count(Embarque.id))
            .join(Embarque, Embarque.autorizacao_id == Autorizacao.id)
            .where(Autorizacao.viagem_id.in_(ids))
            .group_by(Autorizacao.viagem_id)
        )
    }
    return aprovadas, embarques


@router.get("/kpis", response_model=KpisOut, summary="Indicadores operacionais do dia")
def kpis(
    data: date | None = Query(None, description="Padrão: hoje"),
    db: Session = Depends(get_db),
) -> KpisOut:
    dia = data or date.today()
    veiculos = tracking.listar_veiculos(db)
    viagens = _viagens_do_dia(db, dia)
    ids = [v.id for v in viagens]
    aprovadas, embarques = _contagens(db, ids)

    autorizacoes = db.scalar(
        select(func.count(Autorizacao.id))
        .join(Viagem, Viagem.id == Autorizacao.viagem_id)
        .where(Viagem.data == dia, Autorizacao.status == "APROVADA")
    )
    pendentes = db.scalar(
        select(func.count(Autorizacao.id))
        .join(Viagem, Viagem.id == Autorizacao.viagem_id)
        .where(Viagem.data == dia, Autorizacao.status == "PENDENTE")
    )

    concluidas = [v for v in viagens if v.status == "CONCLUIDA" and v.iniciada_em]
    pontuais = [
        v
        for v in concluidas
        if v.iniciada_em <= v.partida_prevista + timedelta(minutes=TOLERANCIA_OTIF_MIN)
    ]
    atrasos = [
        max(0.0, (v.iniciada_em - v.partida_prevista).total_seconds() / 60)
        for v in viagens
        if v.iniciada_em
    ]

    return KpisOut(
        data=dia,
        veiculos_total=len(veiculos),
        veiculos_online=sum(1 for v in veiculos if v.online),
        viagens_total=len(viagens),
        viagens_em_andamento=sum(1 for v in viagens if v.status == "EM_ANDAMENTO"),
        autorizacoes_aprovadas=autorizacoes or 0,
        autorizacoes_pendentes=pendentes or 0,
        passageiros_embarcados=sum(embarques.values()),
        otif_percentual=round(100 * len(pontuais) / len(concluidas), 1) if concluidas else 0.0,
        atraso_medio_min=round(fmean(atrasos), 1) if atrasos else 0.0,
    )


@router.get("/viagens", response_model=ListaViagensAdminOut, summary="Viagens da data")
def listar_viagens(
    data: date | None = Query(None),
    db: Session = Depends(get_db),
) -> ListaViagensAdminOut:
    dia = data or date.today()
    viagens = _viagens_do_dia(db, dia)
    aprovadas, embarques = _contagens(db, [v.id for v in viagens])
    itens = []
    for viagem in viagens:
        atraso = None
        if viagem.iniciada_em:
            atraso = int((viagem.iniciada_em - viagem.partida_prevista).total_seconds() / 60)
        itens.append(
            ViagemAdminOut(
                id=viagem.id,
                data=viagem.data,
                placa=viagem.veiculo.placa,
                motorista=viagem.motorista.nome,
                status=viagem.status,
                trajeto=viagem.trajeto,
                destino=viagem.destino_texto,
                partida_prevista=viagem.partida_prevista,
                iniciada_em=viagem.iniciada_em,
                concluida_em=viagem.concluida_em,
                autorizacoes=aprovadas.get(viagem.id, 0),
                embarques=embarques.get(viagem.id, 0),
                atraso_min=atraso,
            )
        )
    return ListaViagensAdminOut(data=dia, total=len(itens), viagens=itens)


@router.get(
    "/autorizacoes",
    response_model=ListaAutorizacoesAdminOut,
    summary="Autorizações municipais da data (opcionalmente por status)",
)
def listar_autorizacoes(
    request: Request,
    data: date | None = Query(None),
    status: str | None = Query(None, description="PENDENTE, APROVADA, NEGADA ou CANCELADA"),
    db: Session = Depends(get_db),
) -> ListaAutorizacoesAdminOut:
    dia = data or date.today()
    if status and status not in STATUS_AUTORIZACAO:
        raise HTTPException(status_code=422, detail="Status de autorização inválido")

    consulta = (
        select(Autorizacao)
        .join(Viagem, Viagem.id == Autorizacao.viagem_id)
        .where(Viagem.data == dia)
        .options(
            joinedload(Autorizacao.paciente),
            joinedload(Autorizacao.embarque),
            joinedload(Autorizacao.viagem).joinedload(Viagem.veiculo),
        )
        .order_by(Viagem.partida_prevista, Autorizacao.id)
    )
    if status:
        consulta = consulta.where(Autorizacao.status == status)
    autorizacoes = db.scalars(consulta).all()

    itens = [
        AutorizacaoAdminOut(
            id=autorizacao.id,
            numero=autorizacao.numero,
            status=autorizacao.status,
            origem=autorizacao.origem,
            paciente=autorizacao.paciente.nome,
            cpf_mascarado=autorizacao.paciente.cpf_mascarado,
            data=autorizacao.viagem.data,
            placa=autorizacao.viagem.veiculo.placa,
            destino=autorizacao.viagem.destino_texto,
            viagem_id=autorizacao.viagem_id,
            partida_prevista=autorizacao.viagem.partida_prevista,
            validada_em=autorizacao.validada_em,
            validada_por=autorizacao.validada_por,
            embarcado_em=autorizacao.embarque.embarcado_em if autorizacao.embarque else None,
        )
        for autorizacao in autorizacoes
    ]

    audit.registrar(
        db,
        ator_tipo="ADMIN",
        acao="listar_autorizacoes",
        recurso="autorizacao",
        ip=ip_do_cliente(request),
        detalhe=f"data={dia.isoformat()} status={status or 'TODOS'} total={len(itens)}",
    )
    db.commit()
    return ListaAutorizacoesAdminOut(data=dia, total=len(itens), autorizacoes=itens)


@router.get(
    "/posicoes.csv",
    summary="Exporta telemetria em CSV (máx. 50 mil linhas)",
    response_class=StreamingResponse,
)
def exportar_posicoes(
    request: Request,
    inicio: date | None = Query(None, description="Padrão: 7 dias atrás"),
    fim: date | None = Query(None, description="Padrão: hoje"),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    fim = fim or date.today()
    inicio = inicio or (fim - timedelta(days=7))
    if inicio > fim:
        raise HTTPException(status_code=422, detail="inicio deve ser menor ou igual a fim")

    registros = db.execute(
        select(Posicao, Veiculo.placa)
        .join(Veiculo, Veiculo.id == Posicao.veiculo_id)
        .where(
            Posicao.capturada_em >= inicio,
            Posicao.capturada_em < fim + timedelta(days=1),
        )
        .order_by(Posicao.capturada_em)
        .limit(LIMITE_EXPORTACAO)
    ).all()

    buffer = io.StringIO()
    escritor = csv.writer(buffer)
    escritor.writerow(
        [
            "placa",
            "viagem_id",
            "latitude",
            "longitude",
            "velocidade_kmh",
            "precisao_m",
            "fonte",
            "capturada_em",
            "recebida_em",
        ]
    )
    for posicao, placa in registros:
        escritor.writerow(
            [
                placa,
                posicao.viagem_id or "",
                f"{posicao.latitude:.6f}",
                f"{posicao.longitude:.6f}",
                f"{posicao.velocidade_kmh:.1f}",
                f"{posicao.precisao_m:.1f}",
                posicao.fonte,
                posicao.capturada_em.isoformat(),
                posicao.recebida_em.isoformat(),
            ]
        )

    audit.registrar(
        db,
        ator_tipo="ADMIN",
        acao="exportar_telemetria",
        recurso="posicao",
        ip=ip_do_cliente(request),
        detalhe=f"{inicio}..{fim} linhas={len(registros)}",
    )
    db.commit()

    nome = f"posicoes_{inicio}_{fim}.csv"
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{nome}"'},
    )


@router.post(
    "/autorizacoes/{autorizacao_id}/validar",
    response_model=AutorizacaoOut,
    summary="Aprova ou nega uma autorização municipal",
)
def validar_autorizacao(
    autorizacao_id: int,
    corpo: ValidacaoIn,
    request: Request,
    db: Session = Depends(get_db),
) -> AutorizacaoOut:
    autorizacao = db.get(Autorizacao, autorizacao_id)
    if autorizacao is None:
        raise HTTPException(status_code=404, detail="Autorização não encontrada")
    if autorizacao.status in {"CANCELADA"}:
        raise HTTPException(status_code=409, detail="Autorização cancelada não pode ser validada")

    autorizacao.status = corpo.status
    autorizacao.validada_em = utcnow()
    autorizacao.validada_por = corpo.validador
    viagem = db.get(Viagem, autorizacao.viagem_id)
    if corpo.status == "APROVADA" and viagem and viagem.status == "PLANEJADA":
        viagem.status = "AUTORIZADA"

    audit.registrar(
        db,
        ator_tipo="ADMIN",
        ator_ref=corpo.validador,
        acao="validar_autorizacao",
        recurso="autorizacao",
        recurso_id=autorizacao.id,
        ip=ip_do_cliente(request),
        detalhe=corpo.status,
    )
    db.commit()
    db.refresh(autorizacao)
    return AutorizacaoOut.model_validate(autorizacao)
