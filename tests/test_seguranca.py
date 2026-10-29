"""Testes unitários de segurança, normalização e limitação de taxa."""

from __future__ import annotations

import time

import pytest

from app.security import (
    cpf_valido,
    emitir_token_motorista,
    hash_cpf,
    hash_pin,
    ler_token_motorista,
    mascarar_cpf,
    normalizar_cpf,
    normalizar_placa,
    verificar_pin,
)
from app.services.ratelimit import RateLimiter


@pytest.mark.parametrize(
    "entrada,esperado",
    [
        ("abc1d23", "ABC1D23"),
        ("ABC-1D23", "ABC1D23"),
        (" abc 1d23 ", "ABC1D23"),
        ("ABC1234", "ABC1234"),
        ("ABC-1234", "ABC1234"),
    ],
)
def test_normalizar_placa_aceita_formatos(entrada, esperado):
    assert normalizar_placa(entrada) == esperado


@pytest.mark.parametrize("entrada", ["", None, "AB1234", "ABCD123", "1234ABC", "ABC1D234"])
def test_normalizar_placa_rejeita_invalidos(entrada):
    assert normalizar_placa(entrada) is None


@pytest.mark.parametrize(
    "cpf", ["529.982.247-25", "111.444.777-35", "52998224725", "39053344705"]
)
def test_cpf_valido_aceita_cpf_real_matematicamente_valido(cpf):
    assert cpf_valido(cpf)


@pytest.mark.parametrize("cpf", ["111.111.111-11", "529.982.247-24", "123", ""])
def test_cpf_valido_rejeita(cpf):
    assert not cpf_valido(cpf)


def test_normalizacao_e_mascara_de_cpf():
    assert normalizar_cpf("529.982.247-25") == "52998224725"
    assert normalizar_cpf("529.982.247-24") is None
    assert mascarar_cpf("52998224725") == "***.***.***-25"


def test_hash_e_hmac_nao_revelam_cpf():
    primeiro = hash_cpf("52998224725")
    segundo = hash_cpf("529.982.247-25")
    assert primeiro == segundo
    assert "52998224725" not in primeiro
    assert len(primeiro) == 64


def test_pin_com_hash_e_verificacao():
    guardado = hash_pin("1234")
    assert verificar_pin("1234", guardado)
    assert not verificar_pin("4321", guardado)


def test_token_motorista_roundtrip():
    token = emitir_token_motorista(7, 3, horas=1)
    payload = ler_token_motorista(token)
    assert payload is not None
    assert payload["sub"] == 7
    assert payload["vei"] == 3


def test_token_motorista_rejeita_adulteracao():
    token = emitir_token_motorista(7, 3, horas=1)
    cabecalho, corpo, assinatura = token.split(".")
    corpo_adulterado = corpo[:-1] + ("A" if corpo[-1] != "A" else "B")
    assert ler_token_motorista(f"{cabecalho}.{corpo_adulterado}.{assinatura}") is None
    assert ler_token_motorista("lixo") is None
    assert ler_token_motorista(None) is None


def test_token_motorista_rejeita_expirado():
    token = emitir_token_motorista(1, 1, horas=0)
    time.sleep(1.1)
    assert ler_token_motorista(token) is None


def test_rate_limiter_bloqueia_apos_limite():
    limitador = RateLimiter(limite=2, janela_segundos=60)
    assert limitador.verificar("ip-a")[0] is True
    assert limitador.verificar("ip-a")[0] is True
    permitido, espera = limitador.verificar("ip-a")
    assert permitido is False
    assert espera >= 1
    assert limitador.verificar("ip-b")[0] is True
