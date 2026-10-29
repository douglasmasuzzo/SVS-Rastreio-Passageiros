#!/usr/bin/env python3
"""Cria o cenário sintético e imprime as credenciais de demonstração.

Uso:
    python3 scripts/seed_demo.py
    SVS_DB_URL=postgresql+psycopg://... python3 scripts/seed_demo.py
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "backend"))

from app.db import SessionLocal, engine  # noqa: E402
from app.models import Base  # noqa: E402
from app.seed import gerar_cpf, seed  # noqa: E402


def main() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as sessao:
        criado = seed(sessao)
    if criado:
        print("Cenário sintético criado.")
    else:
        print("O banco já possui veículos; nenhum dado foi alterado.")

    print("\nCredenciais de demonstração")
    print("  Pacientes (CPF / nascimento):")
    for base, nascimento, rotulo in (
        ("900000101", "1990-05-12", "Alfa"),
        ("900000102", "1985-11-03", "Beta"),
        ("900000103", "1978-02-20", "Gama"),
    ):
        print(f"    {rotulo}: {gerar_cpf(base)} / {nascimento}")
    print("  Motoristas (placa / PIN):")
    for placa, pin, nome in (
        ("SVS1A23", "1234", "Carlos"),
        ("SVS2B34", "4321", "Marina"),
        ("DEM0C56", "5678", "João"),
        ("TST9D87", "8765", "Rita"),
    ):
        print(f"    {placa} / {pin}  ({nome})")
    print("  Painel: chave definida em SVS_ADMIN_KEY (padrão dev: dev-admin-key).")
    print("  Ingestão: chave definida em SVS_INGEST_KEY (padrão dev: dev-ingest-key).")
    print("\nTodos os dados são fictícios. Não use em produção.")


if __name__ == "__main__":
    main()
