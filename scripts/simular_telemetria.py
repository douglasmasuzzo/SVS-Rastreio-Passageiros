#!/usr/bin/env python3
"""Envia telemetria simulada para a API de referência.

O script descobre a viagem em andamento do veículo pelo endpoint público,
escolhe uma rota sintética compatível com o destino e envia posições em
intervalos regulares usando `X-Ingest-Key`.

Uso:
    python3 scripts/simular_telemetria.py --placa SVS1A23
    python3 scripts/simular_telemetria.py --placa SVS2B34 --intervalo 5 --voltas 2
    SVS_URL=http://localhost:8000 python3 scripts/simular_telemetria.py

Em produção o simulador não é implantado: a ingestão real vem do gateway da
operadora ou do app do motorista.
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
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "backend"))

from app.rotas import ROTAS, ponto_na_rota  # noqa: E402

URL_PADRAO = "http://localhost:8000"
CHAVE_PADRAO = "dev-ingest-key"


def _get_json(url: str) -> dict:
    requisicao = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(requisicao, timeout=10) as resposta:  # noqa: S310
        return json.loads(resposta.read().decode())


def _post_json(url: str, chave: str, corpo: dict) -> dict:
    requisicao = urllib.request.Request(
        url,
        data=json.dumps(corpo).encode(),
        headers={"Content-Type": "application/json", "X-Ingest-Key": chave},
        method="POST",
    )
    with urllib.request.urlopen(requisicao, timeout=10) as resposta:  # noqa: S310
        return json.loads(resposta.read().decode())


def _base_e_endpoint(bruto: str) -> tuple[str, str]:
    """Aceita a raiz da API ou a URL completa do endpoint de telemetria."""
    url = bruto.rstrip("/")
    sufixo = "/api/v1/telemetria"
    if url.endswith(sufixo):
        return url[: -len(sufixo)] or URL_PADRAO, url
    return url, url + sufixo


def _rota_para_destino(destino: str | None) -> str:
    texto = (destino or "").lower()
    if "diadema" in texto:
        return "santos-diadema"
    if "paulo" in texto:
        return "santos-sao-paulo"
    return "santos-diadema"


def descobrir_viagem(base: str, placa: str) -> tuple[int | None, str]:
    """Retorna (viagem_id, rota sugerida) a partir do endpoint público."""
    url = f"{base}/api/v1/publico/veiculos/{placa}"
    try:
        dados = _get_json(url)
    except urllib.error.HTTPError as erro:
        print(f"Aviso: veículo {placa} não encontrado (HTTP {erro.code}).", file=sys.stderr)
        return None, "santos-diadema"
    except urllib.error.URLError as erro:
        print(f"Aviso: falha ao consultar viagem ativa: {erro.reason}", file=sys.stderr)
        return None, "santos-diadema"

    viagem = dados.get("viagem_ativa") or {}
    return viagem.get("id"), _rota_para_destino(viagem.get("destino"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Simulador de telemetria do SVS (demo)")
    parser.add_argument("--placa", default="SVS1A23", help="placa do veículo (padrão: SVS1A23)")
    parser.add_argument(
        "--rota",
        default="auto",
        choices=["auto", *sorted(ROTAS)],
        help="rota sintética; 'auto' usa o destino da viagem ativa",
    )
    parser.add_argument("--intervalo", type=float, default=3.0, help="segundos entre envios")
    parser.add_argument(
        "--velocidade",
        type=float,
        default=0.012,
        help="fração da rota percorrida por envio",
    )
    parser.add_argument("--viagem-id", type=int, default=None, help="viagem fixa (opcional)")
    parser.add_argument(
        "--url",
        default=os.getenv("SVS_URL", URL_PADRAO),
        help="raiz da API ou URL completa de /api/v1/telemetria",
    )
    parser.add_argument(
        "--chave", default=os.getenv("SVS_INGEST_KEY", CHAVE_PADRAO), help="chave de ingestão"
    )
    parser.add_argument("--voltas", type=int, default=0, help="0 = infinito")
    args = parser.parse_args(argv)

    base, endpoint = _base_e_endpoint(args.url)
    placa = args.placa.strip().upper()
    viagem_id = args.viagem_id
    rota = args.rota
    if rota == "auto" or viagem_id is None:
        descoberta, sugerida = descobrir_viagem(base, placa)
        if viagem_id is None:
            viagem_id = descoberta
        if rota == "auto":
            rota = sugerida

    if args.velocidade <= 0:
        parser.error("--velocidade deve ser maior que zero")
    if args.intervalo < 0:
        parser.error("--intervalo não pode ser negativo")

    print(f"Simulando {placa} em {rota} → {endpoint}")
    print(f"Viagem: {viagem_id or 'sem viagem ativa'} | Ctrl+C para parar")

    fracao = 0.0
    voltas = 0
    try:
        while True:
            fracao += args.velocidade
            if fracao >= 1.0:
                fracao = 0.0
                voltas += 1
                if args.voltas and voltas >= args.voltas:
                    print("Voltas concluídas.")
                    return 0

            lat, lon = ponto_na_rota(rota, fracao)
            lat += random.uniform(-0.00012, 0.00012)
            lon += random.uniform(-0.00012, 0.00012)
            corpo = {
                "placa": placa,
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
                "velocidade_kmh": round(max(0.0, 35 + 18 * math.sin(fracao * math.pi * 6)), 1),
                "rumo": 310.0,
                "precisao_m": round(random.uniform(5, 25), 1),
                "fonte": "SIMULADOR",
                "capturada_em": datetime.now(UTC).isoformat(),
            }
            if viagem_id is not None:
                corpo["viagem_id"] = viagem_id

            try:
                resposta = _post_json(endpoint, args.chave, corpo)
                print(
                    f"[{fracao:5.2%}] {corpo['velocidade_kmh']:5.1f} km/h "
                    f"→ id={resposta.get('id')} status={resposta.get('status')}"
                )
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
