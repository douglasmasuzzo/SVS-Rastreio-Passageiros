"""Operação do motorista: sessão, viagens do dia, passageiros e embarque."""

from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..models import Autorizacao, Embarque, EventoViagem, Motorista, Posicao, Veiculo, Viagem
from ..schemas import (
    EmbarqueIn,
    EmbarqueOut,
    EventoIn,
    EventoOut,
    ListaPassageirosOut,
    ListaViagensMotoristaOut,
    PassageiroViagemOut,
    SessaoMotoristaIn,
    SessaoMotoristaOut,
    TelemetriaIn,
    TelemetriaOut,
    VeiculoResumoOut,
    ViagemMotoristaOut,
)
from ..security import emitir_token_motorista, normalizar_placa, verificar_pin
from ..services import audit
from ..timeutil import utcnow
from .deps import ip_do_cliente, limitar_sessao, motorista_autenticado

router = APIRouter(prefix="/api/v1/motorista", tags=["Motorista"])

CREDENCIAL_INVALIDA = "Placa ou PIN inválidos"


def _resumo_veiculo(veiculo: Veiculo) -> VeiculoResumoOut:
    return VeiculoResumoOut(
        placa=veiculo.placa,
        modelo=veiculo.modelo,
        acessivel=veiculo.acessivel,
        operadora=veiculo.operadora.nome,
    )


def _sessao(
    payload: dict = Depends(motorista_autenticado), db: Session = Depends(get_db)
) -> tuple[Motorista, Veiculo]:
    motorista = db.get(Motorista, int(payload.get("sub", 0)))
    veiculo = db.get(Veiculo, int(payload.get("vei", 0)))
    if motorista is None or veiculo is None or not motorista.ativo or not veiculo.ativo:
        raise HTTPException(status_code=401, detail="Sessão inválida")
    return motorista, veiculo


@router.post(
    "/sessao",
    response_model=SessaoMotoristaOut,
    summary="Autentica motorista por placa + PIN",
    dependencies=[Depends(limitar_sessao)],
)
def criar_sessao(
    corpo: SessaoMotoristaIn,
    request: Request,
    db: Session = Depends(get_db),
) -> SessaoMotoristaOut:
    placa = normalizar_placa(corpo.placa)
    veiculo = (
        db.scalar(select(Veiculo).where(Veiculo.placa == placa, Veiculo.ativo.is_(True)))
        if placa
        else None
    )
    if veiculo is None:
        raise HTTPException(status_code=401, detail=CREDENCIAL_INVALIDA)

    candidatos: dict[int, Motorista] = {}
    if veiculo.motorista_id:
        motorista = db.get(Motorista, veiculo.motorista_id)
        if motorista:
            candidatos[motorista.id] = motorista
    do_dia = db.scalars(
        select(Motorista)
        .join(Viagem, Viagem.motorista_id == Motorista.id)
        .where(Viagem.veiculo_id == veiculo.id, Viagem.data == date.today())
    ).all()
    for motorista in do_dia:
        candidatos[motorista.id] = motorista

    autenticado = next(
        (m for m in candidatos.values() if m.ativo and verificar_pin(corpo.pin, m.pin_hash)),
        None,
    )
    if autenticado is None:
        audit.registrar(
            db,
            ator_tipo="MOTORISTA",
            acao="sessao_falha",
            recurso="motorista",
            ip=ip_do_cliente(request),
            detalhe=f"placa={veiculo.placa}",
        )
        db.commit()
        raise HTTPException(status_code=401, detail=CREDENCIAL_INVALIDA)

    token = emitir_token_motorista(autenticado.id, veiculo.id)
    audit.registrar(
        db,
        ator_tipo="MOTORISTA",
        acao="sessao_iniciada",
        recurso="motorista",
        ator_ref=str(autenticado.id),
        recurso_id=autenticado.id,
        ip=ip_do_cliente(request),
    )
    db.commit()
    return SessaoMotoristaOut(
        token=token,
        expira_em=utcnow() + timedelta(hours=settings.driver_session_hours),
        motorista={
            "id": autenticado.id,
            "nome": autenticado.nome,
            "cpf_mascarado": autenticado.cpf_mascarado,
        },
        veiculo=_resumo_veiculo(veiculo),
    )


def _viagem_da_sessao(db: Session, viagem_id: int, veiculo: Veiculo) -> Viagem:
    viagem = db.get(Viagem, viagem_id)
    if viagem is None or viagem.veiculo_id != veiculo.id:
        raise HTTPException(status_code=404, detail="Viagem não encontrada para este veículo")
    return viagem


@router.get(
    "/viagens",
    response_model=ListaViagensMotoristaOut,
    summary="Viagens do veículo na data",
)
def listar_viagens(
    data: date | None = Query(None, description="Padrão: hoje"),
    sessao: tuple[Motorista, Veiculo] = Depends(_sessao),
    db: Session = Depends(get_db),
) -> ListaViagensMotoristaOut:
    _, veiculo = sessao
    dia = data or date.today()
    viagens = db.scalars(
        select(Viagem)
        .where(Viagem.veiculo_id == veiculo.id, Viagem.data == dia)
        .order_by(Viagem.partida_prevista)
    ).all()
    itens = []
    for viagem in viagens:
        autorizacoes = db.scalar(
            select(func.count(Autorizacao.id)).where(
                Autorizacao.viagem_id == viagem.id, Autorizacao.status == "APROVADA"
            )
        )
        embarques = db.scalar(
            select(func.count(Embarque.id))
            .join(Autorizacao, Autorizacao.id == Embarque.autorizacao_id)
            .where(Autorizacao.viagem_id == viagem.id)
        )
        itens.append(
            ViagemMotoristaOut(
                id=viagem.id,
                data=viagem.data,
                status=viagem.status,
                trajeto=viagem.trajeto,
                destino=viagem.destino_texto,
                partida_prevista=viagem.partida_prevista,
                retorno_previsto=viagem.retorno_previsto,
                autorizacoes=autorizacoes or 0,
                embarques=embarques or 0,
            )
        )
    return ListaViagensMotoristaOut(data=dia, veiculo=_resumo_veiculo(veiculo), viagens=itens)


@router.get(
    "/viagens/{viagem_id}/passageiros",
    response_model=ListaPassageirosOut,
    summary="Pacientes autorizados para a viagem",
)
def listar_passageiros(
    viagem_id: int,
    sessao: tuple[Motorista, Veiculo] = Depends(_sessao),
    db: Session = Depends(get_db),
) -> ListaPassageirosOut:
    _, veiculo = sessao
    viagem = _viagem_da_sessao(db, viagem_id, veiculo)
    autorizacoes = db.scalars(
        select(Autorizacao)
        .where(Autorizacao.viagem_id == viagem.id, Autorizacao.status == "APROVADA")
        .order_by(Autorizacao.id)
    ).all()
    passageiros = [
        PassageiroViagemOut(
            autorizacao_id=a.id,
            paciente_id=a.paciente_id,
            nome=a.paciente.nome,
            cpf_mascarado=a.paciente.cpf_mascarado,
            unidade=viagem.destino_texto,
            status_autorizacao=a.status,
            embarque=(
                EmbarqueOut(
                    autorizacao_id=a.id,
                    embarcado_em=a.embarque.embarcado_em,
                    metodo=a.embarque.metodo,
                )
                if a.embarque
                else None
            ),
        )
        for a in autorizacoes
    ]
    return ListaPassageirosOut(
        viagem_id=viagem.id, total=len(passageiros), passageiros=passageiros
    )


@router.post(
    "/viagens/{viagem_id}/embarques",
    response_model=EmbarqueOut,
    summary="Registra embarque (idempotente por autorização)",
)
def registrar_embarque(
    viagem_id: int,
    corpo: EmbarqueIn,
    request: Request,
    sessao: tuple[Motorista, Veiculo] = Depends(_sessao),
    db: Session = Depends(get_db),
) -> EmbarqueOut:
    motorista, veiculo = sessao
    viagem = _viagem_da_sessao(db, viagem_id, veiculo)
    autorizacao = db.get(Autorizacao, corpo.autorizacao_id)
    if autorizacao is None or autorizacao.viagem_id != viagem.id:
        raise HTTPException(status_code=404, detail="Autorização não encontrada nesta viagem")
    if autorizacao.status not in {"APROVADA"}:
        raise HTTPException(status_code=409, detail="Autorização não está aprovada")

    if autorizacao.embarque:
        return EmbarqueOut(
            autorizacao_id=autorizacao.id,
            embarcado_em=autorizacao.embarque.embarcado_em,
            metodo=autorizacao.embarque.metodo,
        )

    embarque = Embarque(
        autorizacao_id=autorizacao.id,
        metodo=corpo.metodo,
        registrado_por=motorista.nome,
    )
    db.add(embarque)
    audit.registrar(
        db,
        ator_tipo="MOTORISTA",
        ator_ref=str(motorista.id),
        acao="registrar_embarque",
        recurso="autorizacao",
        recurso_id=autorizacao.id,
        ip=ip_do_cliente(request),
        detalhe=f"metodo={corpo.metodo}",
    )
    db.commit()
    db.refresh(embarque)
    return EmbarqueOut(
        autorizacao_id=autorizacao.id,
        embarcado_em=embarque.embarcado_em,
        metodo=embarque.metodo,
    )


@router.post(
    "/viagens/{viagem_id}/eventos",
    response_model=EventoOut,
    summary="Registra evento operacional (início, chegada, fim, atraso, incidente)",
)
def registrar_evento(
    viagem_id: int,
    corpo: EventoIn,
    sessao: tuple[Motorista, Veiculo] = Depends(_sessao),
    db: Session = Depends(get_db),
) -> EventoOut:
    motorista, veiculo = sessao
    viagem = _viagem_da_sessao(db, viagem_id, veiculo)
    agora = utcnow()

    evento = EventoViagem(
        viagem_id=viagem.id,
        tipo=corpo.tipo,
        observacao=corpo.observacao,
        ator=motorista.nome,
    )
    if corpo.tipo == "INICIO" and viagem.status in {"PLANEJADA", "AUTORIZADA"}:
        viagem.status = "EM_ANDAMENTO"
        viagem.iniciada_em = agora
    elif corpo.tipo == "FIM":
        viagem.status = "CONCLUIDA"
        viagem.concluida_em = agora
    db.add(evento)
    db.commit()
    db.refresh(evento)
    return EventoOut(
        id=evento.id,
        viagem_id=evento.viagem_id,
        tipo=evento.tipo,
        observacao=evento.observacao,
        criado_em=evento.criado_em,
    )


@router.post(
    "/posicao",
    response_model=TelemetriaOut,
    summary="Envia posição GPS do app do motorista",
)
def enviar_posicao(
    corpo: TelemetriaIn,
    sessao: tuple[Motorista, Veiculo] = Depends(_sessao),
    db: Session = Depends(get_db),
) -> TelemetriaOut:
    _, veiculo = sessao
    posicao = Posicao(
        veiculo_id=veiculo.id,
        viagem_id=corpo.viagem_id,
        latitude=corpo.latitude,
        longitude=corpo.longitude,
        velocidade_kmh=corpo.velocidade_kmh,
        rumo=corpo.rumo,
        precisao_m=corpo.precisao_m,
        fonte="APP_MOTORISTA",
        capturada_em=corpo.capturada_em or utcnow(),
        recebida_em=utcnow(),
    )
    db.add(posicao)
    db.commit()
    db.refresh(posicao)
    return TelemetriaOut(
        id=posicao.id,
        recebida_em=posicao.recebida_em,
        status="ONLINE",
    )
