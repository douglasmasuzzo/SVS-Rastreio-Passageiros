"""Geometria e distâncias.

Haversine é suficiente na escala urbana/metropolitana do caso (Baixada
Santista → Grande São Paulo). Para cálculo de rota real, usar um motor de
roteamento (OSRM/Valhalla) — previsto no roadmap como incremento I3.
"""

from __future__ import annotations

from math import asin, cos, radians, sin, sqrt

RAIO_TERRA_KM = 6371.0088


def distancia_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distância em quilômetros entre dois pontos (fórmula de Haversine)."""
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return round(2 * RAIO_TERRA_KM * asin(min(1.0, sqrt(a))), 3)


def arredondar_coordenada(valor: float, casas: int) -> float:
    """Reduz a precisão de uma coordenada publicamente exposta."""
    return round(valor, casas)


def interpolacao_linear(
    inicio: tuple[float, float], fim: tuple[float, float], fracao: float
) -> tuple[float, float]:
    fracao = max(0.0, min(1.0, fracao))
    return (
        inicio[0] + (fim[0] - inicio[0]) * fracao,
        inicio[1] + (fim[1] - inicio[1]) * fracao,
    )
