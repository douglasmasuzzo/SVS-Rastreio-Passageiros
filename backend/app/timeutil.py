"""Utilidades de tempo — todo o sistema opera em UTC ingênuo (sem tzinfo).

A conversão para o fuso local (America/Sao_Paulo) é responsabilidade da
apresentação. Manter o banco em UTC evita ambiguidade em horário de verão,
mudanças de fuso e comparações entre fontes de telemetria.
"""

from __future__ import annotations

from datetime import UTC, datetime


def utcnow() -> datetime:
    """Agora, em UTC, sem tzinfo (compatível com SQLite e PostgreSQL)."""
    return datetime.now(UTC).replace(tzinfo=None)


def idade_segundos(momento: datetime | None, referencia: datetime | None = None) -> int | None:
    if momento is None:
        return None
    ref = referencia or utcnow()
    return max(0, int((ref - momento).total_seconds()))
