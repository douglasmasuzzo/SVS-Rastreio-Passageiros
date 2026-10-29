"""Regras de rastreamento e montagem de respostas públicas.

Toda informação exposta sem autenticação passa por aqui. O contrato é
deliberadamente pobre em dados pessoais: placa, operadora, posição aproximada
e status. Nunca nome de motorista, paciente ou CPF.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import settings
from ..models import Autorizacao, Posicao, Veiculo, Viagem
from ..security import normalizar_placa
from ..timeutil import idade_segundos, utcnow
from .geo import arredondar_coordenada, distancia_km

PRECISAO_APROXIMADA_M = 100.0


@dataclass(frozen=True)
class StatusVeiculo:
    veiculo: Veiculo
    posicao: Posicao | None
    online: bool
    idade_s: int | None
    viagem: Viagem | None


def ultima_posicao(db: Session, veiculo_id: int) -> Posicao | None:
    return db.scalar(
        select(Posicao)
        .where(Posicao.veiculo_id == veiculo_id)
        .order_by(Posicao.capturada_em.desc(), Posicao.id.desc())
        .limit(1)
    )


def viagem_em_curso(db: Session, veiculo_id: int) -> Viagem | None:
    return db.scalar(
        select(Viagem)
        .where(Viagem.veiculo_id == veiculo_id, Viagem.status == "EM_ANDAMENTO")
        .order_by(Viagem.partida_prevista.desc())
        .limit(1)
    )


def status_veiculo(db: Session, veiculo: Veiculo, referencia: datetime | None = None) -> StatusVeiculo:
    ref = referencia or utcnow()
    posicao = ultima_posicao(db, veiculo.id)
    idade = idade_segundos(posicao.capturada_em, ref) if posicao else None
    online = bool(idade is not None and idade <= settings.offline_after_seconds)
    return StatusVeiculo(veiculo, posicao, online, idade, viagem_em_curso(db, veiculo.id))


def buscar_veiculo(db: Session, placa: str) -> Veiculo | None:
    normalizada = normalizar_placa(placa)
    if not normalizada:
        return None
    return db.scalar(select(Veiculo).where(Veiculo.placa == normalizada, Veiculo.ativo.is_(True)))


def listar_veiculos(db: Session, busca: str | None = None) -> list[StatusVeiculo]:
    consulta = select(Veiculo).where(Veiculo.ativo.is_(True)).order_by(Veiculo.placa)
    if busca:
        termo = busca.strip().upper().replace("-", "").replace(" ", "")
        consulta = consulta.where(Veiculo.placa.contains(termo))
    return [status_veiculo(db, v) for v in db.scalars(consulta).all()]


def posicao_publica(
    db: Session,
    veiculo: Veiculo,
    lat_usuario: float | None = None,
    lon_usuario: float | None = None,
) -> dict:
    status = status_veiculo(db, veiculo)
    posicao = status.posicao
    casas = settings.position_decimals
    dados: dict = {
        "placa": veiculo.placa,
        "modelo": veiculo.modelo,
        "tipo": veiculo.tipo,
        "acessivel": veiculo.acessivel,
        "operadora": veiculo.operadora.nome,
        "status": "ONLINE" if status.online else "OFFLINE",
        "online": status.online,
        "ultima_atualizacao": posicao.capturada_em if posicao else None,
        "idade_segundos": status.idade_s,
        "posicao": None,
        "viagem_ativa": None,
    }
    if posicao:
        dados["posicao"] = {
            "latitude": arredondar_coordenada(posicao.latitude, casas),
            "longitude": arredondar_coordenada(posicao.longitude, casas),
            "velocidade_kmh": round(posicao.velocidade_kmh, 1),
            "rumo": posicao.rumo,
            "precisao_m": round(posicao.precisao_m, 1),
            "posicao_aproximada": posicao.precisao_m > PRECISAO_APROXIMADA_M,
            "capturada_em": posicao.capturada_em,
            "distancia_ate_voce_km": (
                distancia_km(lat_usuario, lon_usuario, posicao.latitude, posicao.longitude)
                if lat_usuario is not None and lon_usuario is not None
                else None
            ),
        }
    if status.viagem:
        dados["viagem_ativa"] = {
            "id": status.viagem.id,
            "status": status.viagem.status,
            "destino": status.viagem.destino_texto,
            "trajeto": status.viagem.trajeto,
            "partida_prevista": status.viagem.partida_prevista,
        }
    return dados


def trilha_publica(db: Session, veiculo: Veiculo, limite: int = 60) -> list[dict]:
    """Últimos pontos do dia, do mais antigo para o mais recente."""
    desde = utcnow() - timedelta(hours=12)
    pontos = db.scalars(
        select(Posicao)
        .where(Posicao.veiculo_id == veiculo.id, Posicao.capturada_em >= desde)
        .order_by(Posicao.capturada_em.desc())
        .limit(min(limite, 200))
    ).all()
    casas = settings.position_decimals
    return [
        {
            "latitude": arredondar_coordenada(p.latitude, casas),
            "longitude": arredondar_coordenada(p.longitude, casas),
            "capturada_em": p.capturada_em,
        }
        for p in reversed(pontos)
    ]


def resumo_viagens_publico(db: Session, veiculo: Veiculo, dia: date) -> dict:
    """Resumo agregado por placa/data.

    Não revela nomes de pacientes. A contagem de autorizações é mantida porque
    é o dado que a operação usa para confirmar a escala do veículo; o risco de
    inferência é discutido em docs/07-seguranca-lgpd.md (achado A-04).
    """
    viagens = db.scalars(
        select(Viagem)
        .where(Viagem.veiculo_id == veiculo.id, Viagem.data == dia)
        .order_by(Viagem.partida_prevista)
    ).all()
    total = 0
    itens = []
    for viagem in viagens:
        autorizacoes = db.scalar(
            select(func.count(Autorizacao.id)).where(
                Autorizacao.viagem_id == viagem.id, Autorizacao.status == "APROVADA"
            )
        )
        total += autorizacoes or 0
        itens.append(
            {
                "id": viagem.id,
                "status": viagem.status,
                "trajeto": viagem.trajeto,
                "destino": viagem.destino_texto,
                "partida_prevista": viagem.partida_prevista,
                "autorizacoes": autorizacoes or 0,
            }
        )
    return {
        "placa": veiculo.placa,
        "data": dia,
        "total_autorizacoes": total,
        "viagens": itens,
    }
