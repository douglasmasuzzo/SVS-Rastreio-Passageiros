#!/usr/bin/env python3
"""Exporta o contrato OpenAPI da aplicação para YAML e JSON.

Uso:
    python3 scripts/exportar_openapi.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "backend"))

from app.main import app  # noqa: E402


def main() -> None:
    destino = RAIZ / "openapi"
    destino.mkdir(parents=True, exist_ok=True)
    esquema = app.openapi()

    (destino / "openapi.json").write_text(
        json.dumps(esquema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (destino / "openapi.yaml").write_text(
        yaml.safe_dump(esquema, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8",
    )
    caminhos = len(esquema.get("paths", {}))
    print(f"OpenAPI {esquema['info']['version']} exportado: {caminhos} caminhos.")
    print(f"  {destino / 'openapi.yaml'}")
    print(f"  {destino / 'openapi.json'}")


if __name__ == "__main__":
    main()
