"""Fixtures compartilhadas.

O ambiente é configurado ANTES de importar a aplicação, pois `settings` é
avaliado no import (padrão de 12-factor: configuração imutável por processo).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "backend"))

os.environ.update(
    {
        "SVS_ENV": "test",
        "SVS_DB_URL": "sqlite+pysqlite:///:memory:",
        "SVS_AUTO_CREATE": "0",
        "SVS_AUTO_SEED": "0",
        "SVS_PUBLIC_RATE_LIMIT": "100000",
        "SVS_PUBLIC_RATE_WINDOW": "60",
        "SVS_CPF_PEPPER": "pepper-de-teste",
        "SVS_DRIVER_SECRET": "segredo-de-teste",
        "SVS_INGEST_KEY": "chave-de-teste",
        "SVS_ADMIN_KEY": "admin-de-teste",
    }
)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

CHAVE_INGESTAO = "chave-de-teste"
CHAVE_ADMIN = "admin-de-teste"


@pytest.fixture()
def db_session():
    from app.db import SessionLocal, engine
    from app.models import Base
    from app.seed import seed

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as sessao:
        seed(sessao)
        yield sessao


@pytest.fixture()
def client(db_session):
    from app.main import app

    with TestClient(app) as cliente:
        yield cliente


@pytest.fixture()
def sessao_motorista(client):
    resposta = client.post(
        "/api/v1/motorista/sessao", json={"placa": "SVS1A23", "pin": "1234"}
    )
    assert resposta.status_code == 200, resposta.text
    return resposta.json()
