"""Ponto de entrada da API + PWA.

Execução local:
    cd backend && SVS_AUTO_SEED=1 uvicorn app.main:app --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, select

from .config import settings
from .db import SessionLocal, engine
from .models import Base, Veiculo
from .routers import admin, motorista, passageiro, publico, telemetria
from .seed import seed

VERSAO = "0.1.0"
STATIC = Path(__file__).resolve().parents[1] / "static"


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.auto_create:
        Base.metadata.create_all(engine)
    if settings.auto_seed:
        with SessionLocal() as db:
            if not db.scalar(select(func.count(Veiculo.id))):
                seed(db)
    yield


DESCRICAO = """
API de referência de uma plataforma de rastreio logístico de passageiros do
transporte público de saúde. Construída como **reimplementação clean-room** a
partir de comportamento observável (ver `docs/02-dossie-engenharia-reversa.md`).

- Nenhum dado real de paciente, motorista ou veículo é utilizado.
- CPF é pseudonimizado; a consulta do passageiro exige segundo fator.
- A posição pública é arredondada e a trilha é limitada às últimas 12 horas.
"""

app = FastAPI(
    title="SVS Rastreio — API de referência",
    version=VERSAO,
    description=DESCRICAO,
    lifespan=lifespan,
    license_info={"name": "Uso acadêmico — ver NOTICE.md"},
)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type", "X-Ingest-Key", "X-Admin-Key"],
    )

app.include_router(publico.router)
app.include_router(passageiro.router)
app.include_router(motorista.router)
app.include_router(telemetria.router)
app.include_router(admin.router)


@app.get("/healthz", tags=["Infra"], summary="Verificação de saúde")
def healthz() -> dict:
    return {"status": "ok", "versao": VERSAO, "ambiente": settings.ambiente}


@app.get("/", include_in_schema=False)
def raiz() -> FileResponse:
    return FileResponse(STATIC / "index.html")


app.mount("/", StaticFiles(directory=STATIC, html=True), name="pwa")
