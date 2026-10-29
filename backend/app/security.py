"""Normalização, pseudonimização e sessões.

Princípios:
- dados pessoais nunca são comparados em texto claro;
- CPF é pseudonimizado com HMAC-SHA256 + pepper (segredo de aplicação);
- sessão de motorista é um token assinado (HMAC), sem estado no servidor;
- todas as comparações sensíveis usam `hmac.compare_digest`.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import time
from datetime import date

from .config import settings

PLACA_MERCOSUL = re.compile(r"^[A-Z]{3}[0-9][A-Z][0-9]{2}$")
PLACA_ANTIGA = re.compile(r"^[A-Z]{3}[0-9]{4}$")
_TOKEN_VERSAO = "v1"


# --------------------------------------------------------------------------- #
# Placas
# --------------------------------------------------------------------------- #
def normalizar_placa(bruta: str | None) -> str | None:
    """Aceita 'abc-1d23', 'ABC1D23', 'abc 1d23' e devolve 'ABC1D23'.

    Retorna None para formatos inválidos (nem Mercosul, nem padrão antigo).
    """
    if not bruta:
        return None
    limpa = re.sub(r"[^A-Za-z0-9]", "", bruta).upper()
    if PLACA_MERCOSUL.match(limpa) or PLACA_ANTIGA.match(limpa):
        return limpa
    return None


# --------------------------------------------------------------------------- #
# CPF
# --------------------------------------------------------------------------- #
def apenas_digitos(valor: str | None) -> str:
    return re.sub(r"\D", "", valor or "")


def cpf_valido(cpf: str | None) -> bool:
    numeros = apenas_digitos(cpf)
    if len(numeros) != 11 or numeros == numeros[0] * 11:
        return False
    for tamanho in (9, 10):
        soma = sum(int(numeros[i]) * (tamanho + 1 - i) for i in range(tamanho))
        digito = (soma * 10) % 11 % 10
        if digito != int(numeros[tamanho]):
            return False
    return True


def normalizar_cpf(cpf: str | None) -> str | None:
    numeros = apenas_digitos(cpf)
    return numeros if cpf_valido(numeros) else None


def mascarar_cpf(cpf: str | None) -> str:
    numeros = apenas_digitos(cpf)
    if len(numeros) != 11:
        return "***.***.***-**"
    return f"***.***.***-{numeros[-2:]}"


def _hmac(texto: str, segredo: str) -> str:
    return hmac.new(segredo.encode(), texto.encode(), hashlib.sha256).hexdigest()


def hash_cpf(cpf: str) -> str:
    return _hmac(apenas_digitos(cpf), settings.cpf_pepper)


def hash_pin(pin: str) -> str:
    return _hmac(pin.strip(), settings.cpf_pepper)


def verificar_pin(pin: str, pin_hash: str) -> bool:
    return hmac.compare_digest(hash_pin(pin), pin_hash)


def data_nascimento_valida(valor: date | None) -> bool:
    if valor is None:
        return False
    hoje = date.today()
    return date(1900, 1, 1) <= valor <= hoje


# --------------------------------------------------------------------------- #
# Token de sessão do motorista (stateless, assinado)
# --------------------------------------------------------------------------- #
def _b64(texto: bytes) -> str:
    return base64.urlsafe_b64encode(texto).decode().rstrip("=")


def _unb64(texto: str) -> bytes:
    return base64.urlsafe_b64decode(texto + "=" * (-len(texto) % 4))


def emitir_token_motorista(motorista_id: int, veiculo_id: int, horas: int | None = None) -> str:
    validade = settings.driver_session_hours if horas is None else horas
    payload = {
        "sub": motorista_id,
        "vei": veiculo_id,
        "exp": int(time.time()) + validade * 3600,
    }
    corpo = _b64(json.dumps(payload, separators=(",", ":")).encode())
    assinatura = hmac.new(settings.driver_secret.encode(), corpo.encode(), hashlib.sha256).digest()
    return f"{_TOKEN_VERSAO}.{corpo}.{_b64(assinatura)}"


def ler_token_motorista(token: str | None) -> dict | None:
    if not token:
        return None
    partes = token.split(".")
    if len(partes) != 3 or partes[0] != _TOKEN_VERSAO:
        return None
    _, corpo, assinatura = partes
    esperado = hmac.new(
        settings.driver_secret.encode(), corpo.encode(), hashlib.sha256
    ).digest()
    try:
        if not hmac.compare_digest(_unb64(assinatura), esperado):
            return None
        payload = json.loads(_unb64(corpo))
    except (ValueError, json.JSONDecodeError):
        return None
    if int(payload.get("exp", 0)) < int(time.time()):
        return None
    return payload


def hash_ip(ip: str | None) -> str | None:
    return _hmac(ip, settings.cpf_pepper) if ip else None
