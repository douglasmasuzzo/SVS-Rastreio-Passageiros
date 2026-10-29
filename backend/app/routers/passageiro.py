"""Consulta do passageiro — endpoint sensível, com segundo fator e auditoria."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas import ConsultaPassageiroIn, ConsultaPassageiroOut
from ..services import audit, passageiro
from .deps import ip_do_cliente, limitar_consulta

router = APIRouter(prefix="/api/v1/passageiro", tags=["Passageiro"])

MENSAGEM_GENERICA = "Dados não conferem com nenhum cadastro ativo. Verifique CPF e data de nascimento."


@router.post(
    "/consulta",
    response_model=ConsultaPassageiroOut,
    summary="Consulta viagem do dia e histórico (CPF + data de nascimento)",
    dependencies=[Depends(limitar_consulta)],
    responses={404: {"description": "Dados não conferem (mensagem genérica)"}},
)
def consultar(
    corpo: ConsultaPassageiroIn,
    request: Request,
    db: Session = Depends(get_db),
) -> ConsultaPassageiroOut:
    dia = corpo.data or date.today()
    ip = ip_do_cliente(request)
    try:
        paciente = passageiro.localizar_paciente(db, corpo.cpf, corpo.data_nascimento)
    except passageiro.ConsultaInvalida:
        audit.registrar(
            db,
            ator_tipo="PASSAGEIRO",
            acao="consulta_falha",
            recurso="paciente",
            ip=ip,
            detalhe="credenciais não conferem",
        )
        db.commit()
        raise HTTPException(status_code=404, detail=MENSAGEM_GENERICA) from None

    resultado = passageiro.consultar(db, paciente, dia)
    audit.registrar(
        db,
        ator_tipo="PASSAGEIRO",
        acao="consulta_agendamento",
        recurso="paciente",
        recurso_id=paciente.id,
        ip=ip,
        detalhe=f"data={dia.isoformat()}",
    )
    db.commit()
    return ConsultaPassageiroOut.model_validate(resultado)
