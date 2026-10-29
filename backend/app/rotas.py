"""Rotas sintéticas usadas pelo seed e pelo simulador de telemetria.

Coordenadas aproximadas de eixos reais (Baixada Santista → Grande São Paulo),
usadas apenas para dar plausibilidade geográfica à demonstração. Não são
rotas oficiais nem representam itinerários de linhas existentes.
"""

from __future__ import annotations

from .services.geo import distancia_km, interpolacao_linear

ROTAS: dict[str, list[tuple[float, float]]] = {
    "santos-diadema": [
        (-23.9608, -46.3336),  # Santos — Centro
        (-23.9360, -46.3520),  # Alemoa
        (-23.9150, -46.3880),  # Ponte dos Barreiros
        (-23.8950, -46.4250),  # Cubatão
        (-23.8600, -46.4650),  # Serra do Mar (Rod. Anchieta)
        (-23.7600, -46.5300),  # Riacho Grande
        (-23.6900, -46.5650),  # São Bernardo do Campo
        (-23.6500, -46.5900),  # Diadema
    ],
    "santos-sao-paulo": [
        (-23.9608, -46.3336),
        (-23.9150, -46.3880),
        (-23.8950, -46.4250),
        (-23.7600, -46.5300),
        (-23.6900, -46.5650),
        (-23.6100, -46.6100),
        (-23.5614, -46.6559),  # São Paulo — Av. Paulista
    ],
}


def _comprimentos(rota: list[tuple[float, float]]) -> list[float]:
    return [
        distancia_km(rota[i][0], rota[i][1], rota[i + 1][0], rota[i + 1][1])
        for i in range(len(rota) - 1)
    ]


def ponto_na_rota(nome: str, fracao: float) -> tuple[float, float]:
    """Interpola um ponto na rota, com `fracao` entre 0 e 1 da distância total."""
    rota = ROTAS[nome]
    trechos = _comprimentos(rota)
    alvo = max(0.0, min(1.0, fracao)) * sum(trechos)
    percorrido = 0.0
    for indice, comprimento in enumerate(trechos):
        if percorrido + comprimento >= alvo or indice == len(trechos) - 1:
            restante = 0.0 if comprimento == 0 else (alvo - percorrido) / comprimento
            return interpolacao_linear(rota[indice], rota[indice + 1], restante)
        percorrido += comprimento
    return rota[-1]
