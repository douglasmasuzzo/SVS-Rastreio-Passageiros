#!/usr/bin/env python3
"""Gera o DDL PostgreSQL a partir do metadata do SQLAlchemy.

O runtime de desenvolvimento usa SQLite; este arquivo é a referência para o
alvo de produção (PostgreSQL 16+). Em produção, use migrações versionadas
(Alembic) em vez de aplicar o DDL manualmente.

Uso:
    python3 scripts/gerar_schema_sql.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex, CreateTable

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "backend"))

from app.models import Base  # noqa: E402

CABECALHO = """-- SVS Rastreio — schema de referência para PostgreSQL 16+
-- Gerado automaticamente por scripts/gerar_schema_sql.py.
-- Não edite manualmente: altere backend/app/models.py e regenere.
--
-- Observações:
--   * CPF não existe em texto claro: apenas cpf_hash (HMAC-SHA256 + pepper) e
--     cpf_mascarado.
--   * Posições são append-only; a trilha pública é limitada em consulta.
--   * Para evolução de produção, adote Alembic e habilite PostGIS se for
--     necessário calcular distâncias/rotas no banco.

BEGIN;

"""

RODAPE = """
COMMIT;
"""


def main() -> None:
    dialeto = postgresql.dialect()
    partes = [CABECALHO]

    for tabela in Base.metadata.sorted_tables:
        ddl = str(CreateTable(tabela).compile(dialect=dialeto)).strip()
        partes.append(f"{ddl};\n")
        for indice in sorted(tabela.indexes, key=lambda i: i.name or ""):
            partes.append(f"{str(CreateIndex(indice).compile(dialect=dialeto)).strip()};\n")
        partes.append("\n")

    partes.append(RODAPE)
    destino = RAIZ / "db" / "schema.sql"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("".join(partes), encoding="utf-8")
    print(f"Schema gerado: {destino} ({len(Base.metadata.sorted_tables)} tabelas)")


if __name__ == "__main__":
    main()
