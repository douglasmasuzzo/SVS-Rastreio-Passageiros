"""Dependências compartilhadas: autenticação de serviço e limitação de taxa."""

from __future__ import annotations

import hmac

from fastapi import Header, HTTPException, Request, status

from ..config import settings
from ..security import ler_token_motorista
from ..services.ratelimit import RateLimiter

limitador_publico = RateLimiter(settings.public_rate_limit, settings.public_rate_window)
limitador_consulta = RateLimiter(max(5, settings.public_rate_limit // 6), settings.public_rate_window)
limitador_sessao = RateLimiter(max(5, settings.public_rate_limit // 6), settings.public_rate_window)


def _aplicar(limitador: RateLimiter, chave: str) -> None:
    permitido, espera = limitador.verificar(chave)
    if not permitido:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas requisições. Aguarde e tente novamente.",
            headers={"Retry-After": str(espera)},
        )


def ip_do_cliente(request: Request) -> str:
    encaminhado = request.headers.get("x-forwarded-for")
    if encaminhado:
        return encaminhado.split(",")[0].strip()
    return request.client.host if request.client else "desconhecido"


def limitar_publico(request: Request) -> None:
    _aplicar(limitador_publico, ip_do_cliente(request))


def limitar_consulta(request: Request) -> None:
    _aplicar(limitador_consulta, "consulta:" + ip_do_cliente(request))


def limitar_sessao(request: Request) -> None:
    _aplicar(limitador_sessao, "sessao:" + ip_do_cliente(request))


def exigir_chave_ingestao(x_ingest_key: str = Header(default="")) -> None:
    if not hmac.compare_digest(x_ingest_key, settings.ingest_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credencial inválida")


def exigir_admin(x_admin_key: str = Header(default="")) -> None:
    if not hmac.compare_digest(x_admin_key, settings.admin_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credencial inválida")


def motorista_autenticado(authorization: str = Header(default="")) -> dict:
    esquema, _, token = authorization.partition(" ")
    if esquema.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão inválida")
    payload = ler_token_motorista(token.strip())
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão inválida")
    return payload
