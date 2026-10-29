# syntax=docker/dockerfile:1
#
# Imagem de referência da API + PWA.
# Contexto de build: raiz do repositório.
#   docker build -f infra/Dockerfile -t svs-rastreio .
#
# A imagem não inclui dados, testes, evidências ou segredos. O banco padrão do
# contêiner é PostgreSQL (ver docker-compose.yml); SQLite continua disponível
# para desenvolvimento local fora do Docker.

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dependências do sistema: curl é usado apenas pelo healthcheck da imagem.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
# psycopg é opcional no projeto (extra `postgres`), mas obrigatório na imagem.
RUN pip install --no-cache-dir -r requirements.txt "psycopg[binary]>=3.2,<4.0"

COPY backend ./backend
COPY scripts ./scripts
COPY db ./db

# Usuário sem privilégios; /app é gravável para o SQLite de demonstração.
RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin svs \
    && mkdir -p /app/data \
    && chown -R svs:svs /app

USER svs
WORKDIR /app/backend

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/healthz || exit 1

# Um worker: o rate limit em memória e o SQLite não são compartilhados entre
# processos. Para múltiplas réplicas, ver roadmap I5 (Redis) e I4 (Postgres).
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
