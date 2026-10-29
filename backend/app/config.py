"""Configuração da aplicação, carregada de variáveis de ambiente.

Nenhum segredo é versionado: os valores padrão existem apenas para o modo
`dev`/`test`. Em `prod` a aplicação se recusa a iniciar com os padrões.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DIR_DADOS = RAIZ / "data"

_PADROES_DEV = {
    "cpf_pepper": "dev-pepper-nao-use-em-producao",
    "driver_secret": "dev-secret-nao-use-em-producao",
    "ingest_key": "dev-ingest-key",
    "admin_key": "dev-admin-key",
}


def _bool(valor: str | None, default: bool = False) -> bool:
    if valor is None:
        return default
    return valor.strip().lower() in {"1", "true", "yes", "on"}


def _int(nome: str, padrao: int, minimo: int = 1) -> int:
    bruto = os.getenv(nome)
    if bruto is None or bruto.strip() == "":
        return padrao
    try:
        return max(minimo, int(bruto))
    except ValueError as exc:  # pragma: no cover - configuração inválida
        raise ValueError(f"{nome} deve ser um inteiro, recebido: {bruto!r}") from exc


@dataclass(frozen=True)
class Settings:
    ambiente: str
    database_url: str
    cpf_pepper: str
    driver_secret: str
    ingest_key: str
    admin_key: str
    offline_after_seconds: int
    public_rate_limit: int
    public_rate_window: int
    position_decimals: int
    auto_seed: bool
    auto_create: bool
    cors_origins: tuple[str, ...]
    driver_session_hours: int = 8

    @property
    def producao(self) -> bool:
        return self.ambiente == "prod"

    @classmethod
    def from_env(cls) -> Settings:
        ambiente = os.getenv("SVS_ENV", "dev").strip().lower()
        url = os.getenv("SVS_DB_URL", f"sqlite+pysqlite:///{DIR_DADOS / 'svs.db'}")
        settings = cls(
            ambiente=ambiente,
            database_url=url,
            cpf_pepper=os.getenv("SVS_CPF_PEPPER", _PADROES_DEV["cpf_pepper"]),
            driver_secret=os.getenv("SVS_DRIVER_SECRET", _PADROES_DEV["driver_secret"]),
            ingest_key=os.getenv("SVS_INGEST_KEY", _PADROES_DEV["ingest_key"]),
            admin_key=os.getenv("SVS_ADMIN_KEY", _PADROES_DEV["admin_key"]),
            offline_after_seconds=_int("SVS_OFFLINE_AFTER", 300, 10),
            public_rate_limit=_int("SVS_PUBLIC_RATE_LIMIT", 60),
            public_rate_window=_int("SVS_PUBLIC_RATE_WINDOW", 60),
            position_decimals=_int("SVS_POSITION_DECIMALS", 4, 0),
            auto_seed=_bool(os.getenv("SVS_AUTO_SEED"), default=ambiente != "prod"),
            auto_create=_bool(os.getenv("SVS_AUTO_CREATE"), default=ambiente != "prod"),
            cors_origins=tuple(
                o.strip() for o in os.getenv("SVS_CORS_ORIGINS", "").split(",") if o.strip()
            ),
        )
        settings.validar()
        return settings

    def validar(self) -> None:
        if not self.producao:
            return
        inseguros = [campo for campo, valor in _PADROES_DEV.items() if getattr(self, campo) == valor]
        if inseguros:
            nomes = ", ".join(inseguros)
            raise RuntimeError(
                "Configuração insegura em produção. Defina variáveis próprias para: " + nomes
            )
        if self.auto_create:
            raise RuntimeError("SVS_AUTO_CREATE deve ser 0 em produção; use migrações controladas.")


settings = Settings.from_env()
