#!/usr/bin/env python3
"""Exporta um snapshot SQL do cenário sintético (PostgreSQL).

O cenário canônico é criado por `backend/app/seed.py`. Este script materializa
o mesmo cenário em INSERTs para inspeção e para cargas rápidas em PostgreSQL.
O snapshot usa o pepper de desenvolvimento; **não use em produção**.

Uso:
    python3 scripts/exportar_seed_sql.py
"""

from __future__ import annotations

import os
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "backend"))

TMP = Path(tempfile.gettempdir()) / "svs-seed-snapshot.db"
TMP.unlink(missing_ok=True)
os.environ.setdefault("SVS_DB_URL", f"sqlite+pysqlite:///{TMP}")
os.environ.setdefault("SVS_ENV", "dev")

from sqlalchemy import select  # noqa: E402

from app.db import SessionLocal, engine  # noqa: E402
from app.models import (  # noqa: E402
    AuditLog,
    Autorizacao,
    Base,
    Embarque,
    EventoViagem,
    Motorista,
    Municipio,
    Operadora,
    Paciente,
    Posicao,
    UnidadeSaude,
    Veiculo,
    Viagem,
)
from app.seed import seed  # noqa: E402

DATA_REFERENCIA = date(2026, 10, 29)
TABELAS = [
    Municipio,
    Operadora,
    Motorista,
    Veiculo,
    Paciente,
    UnidadeSaude,
    Viagem,
    Autorizacao,
    Embarque,
    EventoViagem,
    Posicao,
    AuditLog,
]
CABECALHO = f"""-- SVS Rastreio — snapshot do cenário sintético (PostgreSQL)
-- Gerado por scripts/exportar_seed_sql.py em {datetime.now().isoformat(timespec="seconds")}.
-- Data de referência: {DATA_REFERENCIA.isoformat()}.
--
-- AVISO: este arquivo contém hashes gerados com o pepper de DESENVOLVIMENTO.
-- Para qualquer ambiente real, use backend/app/seed.py com segredos próprios
-- ou um processo de migração/carga governado.
--
-- Ordem de carga respeita as chaves estrangeiras. Os IDs são explícitos e as
-- sequências são ajustadas ao final.

BEGIN;

"""


def valor_sql(valor: object) -> str:
    if valor is None:
        return "NULL"
    if isinstance(valor, bool):
        return "TRUE" if valor else "FALSE"
    if isinstance(valor, (int, float)):
        return repr(valor)
    if isinstance(valor, datetime):
        return f"'{valor.isoformat(sep=' ')}'"
    if isinstance(valor, date):
        return f"'{valor.isoformat()}'"
    texto = str(valor).replace("'", "''")
    return f"'{texto}'"


def main() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as sessao:
        criado = seed(sessao, hoje=DATA_REFERENCIA)
        if not criado:
            raise SystemExit("O banco temporário já possuía dados; remova-o e tente novamente.")

        partes = [CABECALHO]
        for modelo in TABELAS:
            registros = sessao.scalars(select(modelo).order_by(modelo.id)).all()
            if not registros:
                continue
            tabela = modelo.__tablename__
            colunas = [coluna.name for coluna in modelo.__table__.columns]
            partes.append(f"-- {tabela}: {len(registros)} registro(s)\n")
            for registro in registros:
                valores = ", ".join(valor_sql(getattr(registro, nome)) for nome in colunas)
                partes.append(
                    f"INSERT INTO {tabela} ({', '.join(colunas)}) VALUES ({valores});\n"
                )
            partes.append(
                "SELECT setval(pg_get_serial_sequence("
                f"'{tabela}', 'id'), (SELECT MAX(id) FROM {tabela}));\n\n"
            )
        partes.append("COMMIT;\n")

    destino = RAIZ / "db" / "seed.sql"
    destino.write_text("".join(partes), encoding="utf-8")
    print(f"Snapshot gerado: {destino}")


if __name__ == "__main__":
    main()
