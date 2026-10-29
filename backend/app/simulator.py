"""Simulador de telemetria — percorre uma rota sintética e publica posições.

Uso (com a API no ar):
    cd backend
    python -m app.simulator --placa SVS1A23 --intervalo 2

O envio usa `X-Ingest-Key` (padrão de dev: `dev-ingest-key`). Em produção,
o simulador não é implantado.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime

from .rotas import ROTAS, ponto_na_rota


def _enviar(url: str, chave: str, corpo: dict) -> dict:
    dados = json.dumps(corpo).encode()
    requisicao = urllib.request.Request(
        url,
        data=dados,
        headers={"Content-Type": "application/json", "X-Ingest-Key": chave},
        method="POST",
    )
    with urllib.request.urlopen(requisicao, timeout=10) as resposta:  # noqa: S310
        return json.loads(resposta.read().decode())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Simulador de telemetria do SVS (demo)")
    parser.add_argument("--placa", default="SVS1A23")
    parser.add_argument("--rota", default="santos-diadema", choices=sorted(ROTAS))
    parser.add_argument("--intervalo", type=float, default=3.0, help="segundos entre envios")
    parser.add_argument("--velocidade", type=float, default=0.012, help="fração da rota por envio")
    parser.add_argument("--viagem-id", type=int, default=None)
    parser.add_argument("--url", default=os.getenv("SVS_URL", "http://localhost:8000/api/v1/telemetria"))
    parser.add_argument("--chave", default=os.getenv("SVS_INGEST_KEY", "dev-ingest-key"))
    parser.add_argument("--voltas", type=int, default=0, help="0 = infinito")
    args = parser.parse_args(argv)

    fracao = 0.0
    voltas = 0
    print(f"Simulando {args.placa} em {args.rota} → {args.url} (Ctrl+C para parar)")
    try:
        while True:
            fracao += args.velocidade
            if fracao >= 1.0:
                fracao = 0.0
                voltas += 1
                if args.voltas and voltas >= args.voltas:
                    print("Voltas concluídas.")
                    return 0
            lat, lon = ponto_na_rota(args.rota, fracao)
            lat += random.uniform(-0.00012, 0.00012)
            lon += random.uniform(-0.00012, 0.00012)
            velocidade = max(0.0, 35 + 18 * math.sin(fracao * math.pi * 6))
            corpo = {
                "placa": args.placa,
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
                "velocidade_kmh": round(velocidade, 1),
                "rumo": 310.0,
                "precisao_m": round(random.uniform(5, 25), 1),
                "fonte": "SIMULADOR",
                "capturada_em": datetime.now(UTC).isoformat(),
            }
            if args.viagem_id:
                corpo["viagem_id"] = args.viagem_id
            try:
                resposta = _enviar(args.url, args.chave, corpo)
                print(f"[{fracao:5.2%}] {corpo['velocidade_kmh']:5.1f} km/h → id={resposta.get('id')}")
            except urllib.error.HTTPError as erro:
                print(f"HTTP {erro.code}: {erro.read().decode()[:200]}", file=sys.stderr)
            except urllib.error.URLError as erro:
                print(f"Falha de conexão: {erro.reason}", file=sys.stderr)
            time.sleep(args.intervalo)
    except KeyboardInterrupt:
        print("\nEncerrado.")
        return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
