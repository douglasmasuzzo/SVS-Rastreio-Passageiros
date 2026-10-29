"""Consulta do passageiro por CPF + data de nascimento.

Diferença deliberada em relação ao sistema observado: o CPF sozinho NÃO é
aceito como credencial (achado A-01). Exigimos um segundo fator fraco
(data de nascimento) no protótipo e prevemos OTP por SMS no roadmap (I2).
Respostas de erro são genéricas para impedir enumeração de CPFs.
"""

from __future__ import annotations

import re
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Autorizacao, Paciente, Viagem
from ..security import hash_cpf, normalizar_cpf

JANELA_HISTORICO_DIAS = 180


class ConsultaInvalida(Exception):
    """Erro genérico, sem indicar qual campo falhou."""


def localizar_paciente(db: Session, cpf: str | None, nascimento: date | None) -> Paciente:
    numeros = normalizar_cpf(cpf)
    if not numeros or not nascimento:
        raise ConsultaInvalida
    paciente = db.scalar(select(Paciente).where(Paciente.cpf_hash == hash_cpf(numeros)))
    if (
        paciente is None
        or not paciente.ativo
        or paciente.data_nascimento != nascimento
    ):
        raise ConsultaInvalida
    return paciente


def consultar(db: Session, paciente: Paciente, dia: date) -> dict:
    limite = dia - timedelta(days=JANELA_HISTORICO_DIAS)
    registros = db.execute(
        select(Autorizacao, Viagem)
        .join(Viagem, Viagem.id == Autorizacao.viagem_id)
        .where(
            Autorizacao.paciente_id == paciente.id,
            Viagem.data >= limite,
            Viagem.data <= dia,
            Viagem.status != "CANCELADA",
        )
        .order_by(Viagem.data.desc(), Viagem.partida_prevista.desc())
        .limit(30)
    ).all()

    hoje = [r for r in registros if r[1].data == dia and r[0].status == "APROVADA"]
    viagem_hoje = None
    if hoje:
        autorizacao, viagem = hoje[0]
        viagem_hoje = {
            "viagem_id": viagem.id,
            "autorizacao_id": autorizacao.id,
            "numero_autorizacao": autorizacao.numero,
            "status": viagem.status,
            "trajeto": viagem.trajeto,
            "destino": viagem.destino_texto,
            "partida_prevista": viagem.partida_prevista,
            "retorno_previsto": viagem.retorno_previsto,
            "veiculo": {
                "placa": viagem.veiculo.placa,
                "modelo": viagem.veiculo.modelo,
                "acessivel": viagem.veiculo.acessivel,
                "operadora": viagem.veiculo.operadora.nome,
            },
            "motorista": _primeiro_nome(viagem.motorista.nome),
            "acompanhamento_em_tempo_real": viagem.status == "EM_ANDAMENTO",
            "embarcado": bool(autorizacao.embarque),
        }

    historico = [
        {
            "viagem_id": viagem.id,
            "data": viagem.data,
            "status": viagem.status,
            "status_autorizacao": autorizacao.status,
            "destino": viagem.destino_texto,
            "trajeto": viagem.trajeto,
            "placa": viagem.veiculo.placa,
            "acompanhamento_em_tempo_real": False,
        }
        for autorizacao, viagem in registros
        if viagem.data != dia or autorizacao.status != "APROVADA"
    ]

    return {
        "paciente": {
            "nome": paciente.nome,
            "cpf_mascarado": paciente.cpf_mascarado,
            "municipio": paciente.municipio.nome,
        },
        "data_consulta": dia,
        "possui_agendamento": viagem_hoje is not None,
        "viagem_hoje": viagem_hoje,
        "historico": historico,
    }


def _primeiro_nome(nome: str) -> str:
    # Remove sufixos de demonstração como "(demo)" antes de abreviar.
    limpo = re.sub(r"\([^)]*\)", " ", nome or "").strip()
    partes = [p for p in limpo.split() if p]
    if not partes:
        return "Motorista"
    return f"{partes[0]} {partes[-1][0]}." if len(partes) > 1 else partes[0]
