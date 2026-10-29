#!/usr/bin/env python3
"""Gera cópias anonimizadas das capturas usadas como evidência.

As imagens originais nunca são versionadas. Este script aplica tarjas opacas
sobre CPF, nomes de pacientes, placas e nomes de operadoras, converte para PNG
(sem perda) e grava um manifesto com hashes para verificação de integridade.

Uso:
    python3 scripts/redact_evidencias.py \
        --origem /caminho/para/capturas \
        --caixas /caminho/para/boxes.json

O arquivo `boxes.json` é opcional: contém caixas de OCR no formato
`{arquivo: [{txt, x0, y0, x1, y1}, ...]}` e permite detectar automaticamente
CPF e placas que tenham sido reconhecidos.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parents[1]
DESTINO_PADRAO = RAIZ / "reverse-engineering" / "evidencias"

# Mapeamento explícito das capturas. As coordenadas estão em pixels da imagem
# original (720x1600) e foram levantadas por inspeção + OCR.
EVIDENCIAS = {
    "WhatsApp Image 2026-10-29 at 15.54.41.jpeg": {
        "id": "E01",
        "titulo": "Lista pública de veículos",
        "descricao": "Busca por placa com status online/offline, operadora e última atualização.",
        "redigir": [
            ((44, 914, 180, 958), "placa"),
            ((44, 1160, 178, 1203), "placa"),
            ((44, 1405, 172, 1450), "placa"),
            ((46, 978, 360, 1019), "operadora"),
            ((46, 1223, 360, 1264), "operadora"),
            ((45, 1468, 230, 1511), "operadora"),
        ],
    },
    "WhatsApp Image 2026-10-29 at 15.54.41 (2).jpeg": {
        "id": "E02",
        "titulo": "Detalhe do veículo no mapa",
        "descricao": "Mapa Leaflet, status online, velocidade, distância, precisão e última posição.",
        "redigir": [((34, 102, 267, 160), "placa")],
    },
    "WhatsApp Image 2026-10-29 at 15.54.42.jpeg": {
        "id": "E03",
        "titulo": "Consulta por CPF com histórico",
        "descricao": "Consulta por CPF retornando histórico de viagens e veículos.",
        "redigir": [
            ((40, 336, 252, 378), "cpf"),
            ((42, 580, 392, 630), "nome"),
            ((42, 1012, 392, 1060), "nome"),
            ((42, 1443, 392, 1492), "nome"),
            ((515, 676, 640, 719), "placa"),
            ((516, 1108, 637, 1152), "placa"),
            ((533, 1541, 641, 1583), "placa"),
        ],
    },
    "WhatsApp Image 2026-10-29 at 15.54.41 (3).jpeg": {
        "id": "E04",
        "titulo": "Consulta por CPF sem agendamento",
        "descricao": "CPF localizado sem autorização aprovada para o dia; histórico continua visível.",
        "redigir": [
            ((40, 330, 252, 378), "cpf"),
            ((42, 1438, 392, 1488), "nome"),
            ((532, 1535, 641, 1579), "placa"),
        ],
    },
    "WhatsApp Image 2026-10-29 at 15.54.41 (1).jpeg": {
        "id": "E05",
        "titulo": "Visão do motorista",
        "descricao": "Seleção de placa e data; ausência de autorizações municipais para o dia.",
        "redigir": [
            ((62, 174, 125, 220), "placa"),
            ((21, 805, 545, 854), "placa"),
        ],
    },
    "WhatsApp Image 2026-10-29 at 15.54.40.jpeg": {
        "id": "E06",
        "titulo": "Contexto do dispositivo (launcher)",
        "descricao": "Tela inicial do aparelho usada apenas como contexto; não contém dados do sistema.",
        "redigir": [],
    },
    "WhatsApp Image 2026-10-29 at 15.54.40 (1).jpeg": {
        "id": "E07",
        "titulo": "Contexto do dispositivo (tela limpa)",
        "descricao": "Captura auxiliar sem conteúdo do sistema; mantida para rastreabilidade do conjunto.",
        "redigir": [],
    },
}

PADROES = {
    "cpf": re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"),
    "placa": re.compile(r"\b[A-Z]{3}-?[0-9][A-Z0-9][0-9]{2}\b"),
}

NOMES_SENSIVEIS = (
    "Douglas Masuzzo Brasilio",
    "DouglasMasuzzoBrasilio",
)


def caixas_do_ocr(caminho: Path | None) -> dict[str, list[dict]]:
    if caminho is None or not caminho.exists():
        return {}
    return json.loads(caminho.read_text(encoding="utf-8"))


def redigir_imagem(
    origem: Path,
    destino: Path,
    regioes: list[tuple[tuple[int, int, int, int], str]],
    ocr: list[dict],
) -> Counter:
    imagem = Image.open(origem).convert("RGB")
    largura, altura = imagem.size
    desenho = ImageDraw.Draw(imagem)
    motivos: Counter = Counter()

    for (x0, y0, x1, y1), motivo in regioes:
        desenho.rectangle((x0, y0, x1, y1), fill=(15, 23, 42))
        motivos[motivo] += 1

    for caixa in ocr:
        texto = str(caixa.get("txt", ""))
        tipo = next((nome for nome, padrao in PADROES.items() if padrao.fullmatch(texto.strip())), None)
        if tipo is None and any(nome in texto for nome in NOMES_SENSIVEIS):
            tipo = "nome"
        if tipo is None:
            continue
        x0 = max(0, int(caixa["x0"]) - 6)
        y0 = max(0, int(caixa["y0"]) - 4)
        x1 = min(largura, int(caixa["x1"]) + 6)
        y1 = min(altura, int(caixa["y1"]) + 4)
        desenho.rectangle((x0, y0, x1, y1), fill=(15, 23, 42))
        motivos[tipo] += 1

    destino.parent.mkdir(parents=True, exist_ok=True)
    imagem.save(destino, format="PNG", optimize=True)
    return motivos


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--origem", type=Path, required=True, help="Diretório das capturas originais")
    parser.add_argument("--caixas", type=Path, help="JSON com caixas de OCR (opcional)")
    parser.add_argument("--destino", type=Path, default=DESTINO_PADRAO)
    parser.add_argument("--manifesto", type=Path, default=DESTINO_PADRAO / "manifesto.json")
    args = parser.parse_args()

    if not args.origem.is_dir():
        raise SystemExit(f"Diretório de origem não encontrado: {args.origem}")

    caixas = caixas_do_ocr(args.caixas)
    manifesto = {
        "gerado_em": datetime.now(UTC).isoformat(timespec="seconds"),
        "observacao": (
            "Cópias anonimizadas de capturas observacionais. Os originais não são versionados. "
            "Tarjas opacas removem CPF, nomes, placas e operadoras antes da conversão para PNG."
        ),
        "evidencias": [],
    }

    for nome_original, meta in EVIDENCIAS.items():
        origem = args.origem / nome_original
        if not origem.exists():
            print(f"[aviso] ausente: {nome_original}")
            continue
        destino = args.destino / f"{meta['id']}.png"
        motivos = redigir_imagem(origem, destino, meta["redigir"], caixas.get(nome_original, []))
        digest = hashlib.sha256(destino.read_bytes()).hexdigest()
        manifesto["evidencias"].append(
            {
                "id": meta["id"],
                "arquivo": f"{meta['id']}.png",
                "titulo": meta["titulo"],
                "descricao": meta["descricao"],
                "origem": nome_original,
                "redacoes": dict(motivos),
                "sha256": digest,
            }
        )
        print(f"{meta['id']}: {destino.name} ({sum(motivos.values())} tarjas)")

    args.manifesto.parent.mkdir(parents=True, exist_ok=True)
    args.manifesto.write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Manifesto: {args.manifesto}")


if __name__ == "__main__":
    main()
