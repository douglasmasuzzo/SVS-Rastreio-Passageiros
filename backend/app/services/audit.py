"""Trilha de auditoria (LGPD art. 37 — registro das operações de tratamento)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import AuditLog
from ..security import hash_ip


def registrar(
    db: Session,
    *,
    ator_tipo: str,
    acao: str,
    recurso: str,
    ator_ref: str | None = None,
    recurso_id: str | int | None = None,
    ip: str | None = None,
    detalhe: str | None = None,
) -> None:
    db.add(
        AuditLog(
            ator_tipo=ator_tipo,
            ator_ref=ator_ref,
            acao=acao,
            recurso=recurso,
            recurso_id=str(recurso_id) if recurso_id is not None else None,
            ip_hash=hash_ip(ip),
            detalhe=detalhe,
        )
    )
