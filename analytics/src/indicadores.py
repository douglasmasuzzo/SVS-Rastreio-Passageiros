#!/usr/bin/env python3
"""Indicadores operacionais do SVS Rastreio (trilha CRISP-DM).

Lê o banco SQLite de desenvolvimento (ou um snapshot exportado) e calcula
indicadores de pontualidade, ocupação e volume por data e por veículo.

O objetivo é analítico e demonstrativo: os dados são sintéticos. As fórmulas
seguem as mesmas decisões do painel administrativo (`routers/admin.py`), para
que o número exibido na PWA e o número do relatório sejam reconciliáveis.

Uso:
    python analytics/src/indicadores.py --db data/svs.db
    python analytics/src/indicadores.py --db data/svs.db --data 2026-10-29 --json
    python analytics/src/indicadores.py --db data/svs.db --csv-saida /tmp/ind.csv

Sem dependências além da biblioteca padrão.
"""

from __future__ import annotations

import argparse
import csv
import json
import sqlite3
import sys
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from statistics import fmean

TOLERANCIA_OTIF_MIN = 15
STATUS_CONCLUIDA = "CONCLUIDA"
STATUS_EM_ANDAMENTO = "EM_ANDAMENTO"
STATUS_APROVADA = "APROVADA"


@dataclass(frozen=True)
class Viagem:
    id: int
    data: date
    placa: str
    status: str
    partida_prevista: datetime
    iniciada_em: datetime | None
    concluida_em: datetime | None


@dataclass(frozen=True)
class Indicadores:
    data: date
    viagens_total: int
    viagens_concluidas: int
    viagens_em_andamento: int
    viagens_pontuais: int
    otif_percentual: float
    atraso_medio_min: float
    atraso_max_min: float
    autorizacoes_aprovadas: int
    embarques: int
    ocupacao_percentual: float


@dataclass(frozen=True)
class IndicadoresVeiculo:
    placa: str
    viagens: int
    concluidas: int
    otif_percentual: float
    atraso_medio_min: float
    embarques: int
    autorizacoes_aprovadas: int
    ocupacao_percentual: float


def _parse_data(valor: str | None) -> date | None:
    if not valor:
        return None
    return date.fromisoformat(valor)


def _parse_dt(valor: str | None) -> datetime | None:
    if not valor:
        return None
    # SQLite/SQLAlchemy grava "YYYY-MM-DD HH:MM:SS[.ffffff]" sem fuso.
    return datetime.fromisoformat(valor.replace("Z", "+00:00")).replace(tzinfo=None)


def conectar(caminho: Path) -> sqlite3.Connection:
    if not caminho.exists():
        raise FileNotFoundError(
            f"Banco não encontrado: {caminho}. Rode `make seed` ou informe --db."
        )
    conexao = sqlite3.connect(f"file:{caminho}?mode=ro", uri=True)
    conexao.row_factory = sqlite3.Row
    return conexao


def carregar_viagens(conexao: sqlite3.Connection, dia: date | None = None) -> list[Viagem]:
    sql = """
        SELECT v.id, v.data, ve.placa, v.status, v.partida_prevista,
               v.iniciada_em, v.concluida_em
        FROM viagem v
        JOIN veiculo ve ON ve.id = v.veiculo_id
    """
    parametros: tuple = ()
    if dia is not None:
        sql += " WHERE v.data = ?"
        parametros = (dia.isoformat(),)
    sql += " ORDER BY v.data, v.partida_prevista"
    linhas = conexao.execute(sql, parametros).fetchall()
    return [
        Viagem(
            id=linha["id"],
            data=date.fromisoformat(str(linha["data"])[:10]),
            placa=linha["placa"],
            status=linha["status"],
            partida_prevista=_parse_dt(linha["partida_prevista"]) or datetime.min,
            iniciada_em=_parse_dt(linha["iniciada_em"]),
            concluida_em=_parse_dt(linha["concluida_em"]),
        )
        for linha in linhas
    ]


def carregar_contagens(conexao: sqlite3.Connection, dia: date | None = None) -> dict[int, dict[str, int]]:
    """Retorna {viagem_id: {aprovadas, embarques}}."""
    filtro_viagem = "WHERE v.data = ?" if dia is not None else ""
    parametros: tuple = (dia.isoformat(),) if dia is not None else ()

    aprovadas = {
        linha["viagem_id"]: linha["total"]
        for linha in conexao.execute(
            f"""
            SELECT a.viagem_id, COUNT(*) AS total
            FROM autorizacao a
            JOIN viagem v ON v.id = a.viagem_id
            {filtro_viagem}
            {"AND" if filtro_viagem else "WHERE"} a.status = ?
            GROUP BY a.viagem_id
            """,
            (*parametros, STATUS_APROVADA),
        )
    }
    embarques = {
        linha["viagem_id"]: linha["total"]
        for linha in conexao.execute(
            f"""
            SELECT a.viagem_id, COUNT(*) AS total
            FROM embarque e
            JOIN autorizacao a ON a.id = e.autorizacao_id
            JOIN viagem v ON v.id = a.viagem_id
            {filtro_viagem}
            GROUP BY a.viagem_id
            """,
            parametros,
        )
    }
    return {
        viagem_id: {
            "aprovadas": aprovadas.get(viagem_id, 0),
            "embarques": embarques.get(viagem_id, 0),
        }
        for viagem_id in set(aprovadas) | set(embarques)
    }


def _atraso_min(viagem: Viagem) -> float | None:
    if viagem.iniciada_em is None:
        return None
    return max(0.0, (viagem.iniciada_em - viagem.partida_prevista).total_seconds() / 60)


def _otif(viagens: list[Viagem], tolerancia_min: int) -> tuple[int, float]:
    concluidas = [v for v in viagens if v.status == STATUS_CONCLUIDA and v.iniciada_em]
    pontuais = [
        v
        for v in concluidas
        if v.iniciada_em <= v.partida_prevista + timedelta(minutes=tolerancia_min)
    ]
    if not concluidas:
        return 0, 0.0
    return len(pontuais), round(100 * len(pontuais) / len(concluidas), 1)


def calcular(
    viagens: list[Viagem],
    contagens: dict[int, dict[str, int]],
    tolerancia_min: int = TOLERANCIA_OTIF_MIN,
) -> list[Indicadores]:
    """Agrega indicadores por data, em ordem cronológica."""
    por_data: dict[date, list[Viagem]] = {}
    for viagem in viagens:
        por_data.setdefault(viagem.data, []).append(viagem)

    resultado: list[Indicadores] = []
    for dia in sorted(por_data):
        do_dia = por_data[dia]
        atrasos = [a for v in do_dia if (a := _atraso_min(v)) is not None]
        pontuais, otif = _otif(do_dia, tolerancia_min)
        aprovadas = sum(contagens.get(v.id, {}).get("aprovadas", 0) for v in do_dia)
        embarques = sum(contagens.get(v.id, {}).get("embarques", 0) for v in do_dia)
        resultado.append(
            Indicadores(
                data=dia,
                viagens_total=len(do_dia),
                viagens_concluidas=sum(1 for v in do_dia if v.status == STATUS_CONCLUIDA),
                viagens_em_andamento=sum(
                    1 for v in do_dia if v.status == STATUS_EM_ANDAMENTO
                ),
                viagens_pontuais=pontuais,
                otif_percentual=otif,
                atraso_medio_min=round(fmean(atrasos), 1) if atrasos else 0.0,
                atraso_max_min=round(max(atrasos), 1) if atrasos else 0.0,
                autorizacoes_aprovadas=aprovadas,
                embarques=embarques,
                ocupacao_percentual=(
                    round(100 * embarques / aprovadas, 1) if aprovadas else 0.0
                ),
            )
        )
    return resultado


def calcular_por_veiculo(
    viagens: list[Viagem],
    contagens: dict[int, dict[str, int]],
    tolerancia_min: int = TOLERANCIA_OTIF_MIN,
) -> list[IndicadoresVeiculo]:
    por_placa: dict[str, list[Viagem]] = {}
    for viagem in viagens:
        por_placa.setdefault(viagem.placa, []).append(viagem)

    resultado: list[IndicadoresVeiculo] = []
    for placa in sorted(por_placa):
        do_veiculo = por_placa[placa]
        atrasos = [a for v in do_veiculo if (a := _atraso_min(v)) is not None]
        _, otif = _otif(do_veiculo, tolerancia_min)
        aprovadas = sum(contagens.get(v.id, {}).get("aprovadas", 0) for v in do_veiculo)
        embarques = sum(contagens.get(v.id, {}).get("embarques", 0) for v in do_veiculo)
        resultado.append(
            IndicadoresVeiculo(
                placa=placa,
                viagens=len(do_veiculo),
                concluidas=sum(1 for v in do_veiculo if v.status == STATUS_CONCLUIDA),
                otif_percentual=otif,
                atraso_medio_min=round(fmean(atrasos), 1) if atrasos else 0.0,
                embarques=embarques,
                autorizacoes_aprovadas=aprovadas,
                ocupacao_percentual=(
                    round(100 * embarques / aprovadas, 1) if aprovadas else 0.0
                ),
            )
        )
    return resultado


def resumo_txt(dia: Indicadores) -> str:
    return (
        f"{dia.data.isoformat()}  viagens={dia.viagens_total:>3} "
        f"concluídas={dia.viagens_concluidas:>3} "
        f"OTIF={dia.otif_percentual:>5.1f}%  "
        f"atraso médio={dia.atraso_medio_min:>5.1f} min  "
        f"embarques={dia.embarques:>3}/{dia.autorizacoes_aprovadas:<3} "
        f"ocupação={dia.ocupacao_percentual:>5.1f}%"
    )


def imprimir(indicadores: list[Indicadores], por_veiculo: list[IndicadoresVeiculo]) -> None:
    if not indicadores:
        print("Nenhuma viagem encontrada no período.")
        return
    print("== Indicadores por data ==")
    for item in indicadores:
        print(resumo_txt(item))
    print("\n== Indicadores por veículo ==")
    print(
        f"{'placa':<9} {'viagens':>7} {'concl.':>6} {'OTIF%':>6} "
        f"{'atraso':>7} {'emb.':>5} {'aprov.':>6} {'ocup.%':>6}"
    )
    for item in por_veiculo:
        print(
            f"{item.placa:<9} {item.viagens:>7} {item.concluidas:>6} "
            f"{item.otif_percentual:>6.1f} {item.atraso_medio_min:>7.1f} "
            f"{item.embarques:>5} {item.autorizacoes_aprovadas:>6} "
            f"{item.ocupacao_percentual:>6.1f}"
        )


def exportar_csv(
    caminho: Path,
    indicadores: list[Indicadores],
    por_veiculo: list[IndicadoresVeiculo],
) -> None:
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["escopo", *[campo for campo in asdict(indicadores[0])]])
        for item in indicadores:
            escritor.writerow(["data", *asdict(item).values()])
        if por_veiculo:
            escritor.writerow(["placa", *[campo for campo in asdict(por_veiculo[0])]])
            for item in por_veiculo:
                escritor.writerow(["veiculo", *asdict(item).values()])
    print(f"CSV gravado em {caminho}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Indicadores operacionais do SVS Rastreio")
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("data/svs.db"),
        help="Caminho do SQLite (padrão: data/svs.db)",
    )
    parser.add_argument("--data", help="Filtra uma data específica (AAAA-MM-DD)")
    parser.add_argument(
        "--tolerancia",
        type=int,
        default=TOLERANCIA_OTIF_MIN,
        help="Tolerância de OTIF em minutos (padrão: 15)",
    )
    parser.add_argument("--json", action="store_true", help="Saída JSON em vez de tabela")
    parser.add_argument("--csv-saida", type=Path, help="Grava os indicadores em CSV")
    args = parser.parse_args(argv)

    dia = _parse_data(args.data)
    try:
        conexao = conectar(args.db)
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return 2

    try:
        viagens = carregar_viagens(conexao, dia)
        contagens = carregar_contagens(conexao, dia)
    finally:
        conexao.close()

    indicadores = calcular(viagens, contagens, args.tolerancia)
    por_veiculo = calcular_por_veiculo(viagens, contagens, args.tolerancia)

    if args.json:
        print(
            json.dumps(
                {
                    "tolerancia_otif_min": args.tolerancia,
                    "por_data": [
                        {**asdict(item), "data": item.data.isoformat()} for item in indicadores
                    ],
                    "por_veiculo": [asdict(item) for item in por_veiculo],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        imprimir(indicadores, por_veiculo)

    if args.csv_saida and indicadores:
        exportar_csv(args.csv_saida, indicadores, por_veiculo)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
