"""Ingestão de telemetria por gateway/operadora (autenticada por chave)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Posicao, Viagem
from ..schemas import TelemetriaIn, TelemetriaOut
from ..services import tracking
from ..timeutil import utcnow
from .deps import exigir_chave_ingestao

router = APIRouter(prefix="/api/v1", tags=["Telemetria"])

DRIFT_MAX_FUTURO = timedelta(minutes=5)
DRIFT_MAX_PASSADO = timedelta(hours=24)


def _ingenuo_utc(momento: datetime | None) -> datetime:
    if momento is None:
        return utcnow()
    if momento.tzinfo is not None:
        return momento.astimezone(UTC).replace(tzinfo=None)
    return momento


@router.post(
    "/telemetria",
    response_model=TelemetriaOut,
    summary="Recebe um ponto de GPS de um veículo",
    dependencies=[Depends(exigir_chave_ingestao)],
)
def receber_telemetria(corpo: TelemetriaIn, db: Session = Depends(get_db)) -> TelemetriaOut:
    veiculo = tracking.buscar_veiculo(db, corpo.placa)
    if veiculo is None:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")

    capturada = _ingenuo_utc(corpo.capturada_em)
    agora = utcnow()
    if capturada > agora + DRIFT_MAX_FUTURO or capturada < agora - DRIFT_MAX_PASSADO:
        raise HTTPException(status_code=422, detail="Horário da captura fora da janela aceitável")

    if corpo.viagem_id is not None:
        viagem = db.get(Viagem, corpo.viagem_id)
        if viagem is None or viagem.veiculo_id != veiculo.id:
            raise HTTPException(status_code=422, detail="Viagem não pertence ao veículo")

    posicao = Posicao(
        veiculo_id=veiculo.id,
        viagem_id=corpo.viagem_id,
        latitude=corpo.latitude,
        longitude=corpo.longitude,
        velocidade_kmh=corpo.velocidade_kmh,
        rumo=corpo.rumo,
        precisao_m=corpo.precisao_m,
        fonte=corpo.fonte,
        capturada_em=capturada,
        recebida_em=agora,
    )
    db.add(posicao)
    db.commit()
    db.refresh(posicao)
    status = tracking.status_veiculo(db, veiculo)
    return TelemetriaOut(
        id=posicao.id,
        recebida_em=posicao.recebida_em,
        status="ONLINE" if status.online else "OFFLINE",
    )
