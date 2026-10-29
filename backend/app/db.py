"""Conexão com o banco de dados.

SQLite é o padrão de desenvolvimento (zero configuração). PostgreSQL + PostGIS
é o alvo de produção — ver `db/schema.sql` e `docs/04-arquitetura.md`.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from .config import settings

_url = settings.database_url
_conexao: dict = {}

if _url.startswith("sqlite"):
    if ":memory:" in _url:
        _conexao = {"connect_args": {"check_same_thread": False}, "poolclass": StaticPool}
    else:
        caminho = _url.split("///")[-1]
        Path(caminho).parent.mkdir(parents=True, exist_ok=True)
        _conexao = {"connect_args": {"check_same_thread": False, "timeout": 15}}

engine = create_engine(_url, future=True, **_conexao)

if _url.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def _configurar_sqlite(dbapi_conexao, _registro):  # pragma: no cover
        cursor = dbapi_conexao.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)


def get_db() -> Iterator[Session]:
    with SessionLocal() as sessao:
        yield sessao
