"""Vocabulário do domínio — constantes de estado e tipos.

Mantidas como strings (e não Enum do Python) para facilitar persistência,
serialização e evolução do schema sem migração de tipo.
"""

from __future__ import annotations

STATUS_VIAGEM = ("PLANEJADA", "AUTORIZADA", "EM_ANDAMENTO", "CONCLUIDA", "CANCELADA")
STATUS_VIAGEM_ATIVA = ("PLANEJADA", "AUTORIZADA", "EM_ANDAMENTO")

STATUS_AUTORIZACAO = ("PENDENTE", "APROVADA", "NEGADA", "CANCELADA")
STATUS_AUTORIZACAO_VALIDA = ("APROVADA",)

TIPOS_UNIDADE = ("UBS", "UPA", "HOSPITAL", "CAPS", "LABORATORIO", "CER")

TIPOS_TRAJETO = ("IDA", "VOLTA", "IDA_E_VOLTA")

METODOS_EMBARQUE = ("QRCODE", "CPF", "MANUAL")

TIPOS_EVENTO = ("INICIO", "CHEGADA_DESTINO", "FIM", "ATRASO", "INCIDENTE", "OBSERVACAO")

FONTES_POSICAO = ("APP_MOTORISTA", "GATEWAY", "SIMULADOR")

ORIGENS_AUTORIZACAO = ("SMS", "OFICIO", "SISTEMA")
