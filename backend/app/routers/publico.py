"""Endpoints públicos: rastreamento por placa, sem autenticação.

Superfície mínima de dados. Qualquer campo novo aqui deve ser avaliado contra
o princípio da minimização (LGPD art. 6º, III) e registrado em docs/07.
"""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas import (
    ListaVeiculosOut,
    ResumoViagensOut,
    TrilhaOut,
    VeiculoPublicoOut,
)
from ..services import tracking
from .deps import limitar_publico

router = APIRouter(prefix="/api/v1/publico", tags=["Rastreamento público"])


def _veiculo_ou_404(db: Session, placa: str):
    veiculo = tracking.buscar_veiculo(db, placa)
    if veiculo is None:
        # mensagem idêntica para placa inválida e inexistente: evita enumeração
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    return veiculo


@router.get(
    "/veiculos",
    response_model=ListaVeiculosOut,
    summary="Lista veículos ativos com status online/offline",
    dependencies=[Depends(limitar_publico)],
)
def listar_veiculos(
    busca: str | None = Query(None, max_length=8, description="Trecho da placa"),
    db: Session = Depends(get_db),
) -> ListaVeiculosOut:
    itens = tracking.listar_veiculos(db, busca)
    veiculos = [
        VeiculoPublicoOut.model_validate(tracking.posicao_publica(db, s.veiculo)) for s in itens
    ]
    return ListaVeiculosOut(total=len(veiculos), veiculos=veiculos)


@router.get(
    "/veiculos/{placa}",
    response_model=VeiculoPublicoOut,
    summary="Posição atual e status do veículo",
    dependencies=[Depends(limitar_publico)],
)
def obter_veiculo(
    placa: str,
    request: Request,
    lat: float | None = Query(None, ge=-90, le=90, description="Latitude do usuário"),
    lon: float | None = Query(None, ge=-180, le=180, description="Longitude do usuário"),
    db: Session = Depends(get_db),
) -> VeiculoPublicoOut:
    if (lat is None) != (lon is None):
        raise HTTPException(status_code=422, detail="Informe lat e lon em conjunto")
    veiculo = _veiculo_ou_404(db, placa)
    return VeiculoPublicoOut.model_validate(tracking.posicao_publica(db, veiculo, lat, lon))


@router.get(
    "/veiculos/{placa}/trilha",
    response_model=TrilhaOut,
    summary="Trilha aproximada das últimas 12 horas",
    dependencies=[Depends(limitar_publico)],
)
def obter_trilha(
    placa: str,
    limite: int = Query(60, ge=2, le=200),
    db: Session = Depends(get_db),
) -> TrilhaOut:
    veiculo = _veiculo_ou_404(db, placa)
    return TrilhaOut(
        placa=veiculo.placa, pontos=tracking.trilha_publica(db, veiculo, limite=limite)
    )


@router.get(
    "/veiculos/{placa}/viagens",
    response_model=ResumoViagensOut,
    summary="Resumo agregado das viagens por data (sem dados de pacientes)",
    dependencies=[Depends(limitar_publico)],
)
def resumo_viagens(
    placa: str,
    data: date | None = Query(None, description="Padrão: hoje"),
    db: Session = Depends(get_db),
) -> ResumoViagensOut:
    veiculo = _veiculo_ou_404(db, placa)
    dia = data or date.today()
    return ResumoViagensOut.model_validate(tracking.resumo_viagens_publico(db, veiculo, dia))
