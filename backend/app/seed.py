"""Popula o banco com um cenário sintético e reprodutível.

Todos os nomes, CPFs, placas e unidades são fictícios. Os CPFs são gerados
com dígitos verificadores válidos a partir de bases reservadas (900000xxx),
justamente para que jamais colidam com um CPF real.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .db import SessionLocal, engine
from .models import (
    Autorizacao,
    Base,
    Embarque,
    Motorista,
    Municipio,
    Operadora,
    Paciente,
    Posicao,
    UnidadeSaude,
    Veiculo,
    Viagem,
)
from .rotas import ponto_na_rota
from .security import hash_cpf, hash_pin, mascarar_cpf
from .timeutil import utcnow


def gerar_cpf(base9: str) -> str:
    """Gera CPF sintético com dígitos verificadores válidos a partir de 9 dígitos."""

    def digito(parcial: str) -> str:
        soma = sum(int(n) * (len(parcial) + 1 - i) for i, n in enumerate(parcial))
        return str((soma * 10) % 11 % 10)

    d1 = digito(base9)
    d2 = digito(base9 + d1)
    return base9 + d1 + d2


def _em(dia: date, hora: int, minuto: int = 0) -> datetime:
    return datetime.combine(dia, time(hora, minuto))


def seed(db: Session, hoje: date | None = None) -> bool:
    """Cria o cenário. Retorna False se o banco já tiver veículos."""
    if db.scalar(select(func.count(Veiculo.id))):
        return False

    hoje = hoje or date.today()
    agora = utcnow()

    municipios = {
        "santos": Municipio(codigo_ibge="3548500", nome="Santos", uf="SP"),
        "sao_vicente": Municipio(codigo_ibge="3551009", nome="São Vicente", uf="SP"),
        "cubatao": Municipio(codigo_ibge="3513504", nome="Cubatão", uf="SP"),
        "sao_paulo": Municipio(codigo_ibge="3550308", nome="São Paulo", uf="SP"),
        "diadema": Municipio(codigo_ibge="3513801", nome="Diadema", uf="SP"),
    }
    db.add_all(municipios.values())
    db.flush()

    operadoras = {
        "litoral": Operadora(
            nome="Transporte Saúde Litoral (demo)",
            contato="operacao@litoral.exemplo",
        ),
        "metropolitana": Operadora(
            nome="Mobilidade Assistencial SP (demo)",
            contato="operacao@metropolitana.exemplo",
        ),
    }
    db.add_all(operadoras.values())
    db.flush()

    motoristas = {
        "carlos": Motorista(
            nome="Carlos Andrade (demo)",
            cpf_hash=hash_cpf(gerar_cpf("900000001")),
            cpf_mascarado=mascarar_cpf(gerar_cpf("900000001")),
            pin_hash=hash_pin("1234"),
            operadora_id=operadoras["litoral"].id,
        ),
        "marina": Motorista(
            nome="Marina Souza (demo)",
            cpf_hash=hash_cpf(gerar_cpf("900000002")),
            cpf_mascarado=mascarar_cpf(gerar_cpf("900000002")),
            pin_hash=hash_pin("4321"),
            operadora_id=operadoras["litoral"].id,
        ),
        "joao": Motorista(
            nome="João Pereira (demo)",
            cpf_hash=hash_cpf(gerar_cpf("900000003")),
            cpf_mascarado=mascarar_cpf(gerar_cpf("900000003")),
            pin_hash=hash_pin("5678"),
            operadora_id=operadoras["metropolitana"].id,
        ),
        "rita": Motorista(
            nome="Rita Lima (demo)",
            cpf_hash=hash_cpf(gerar_cpf("900000004")),
            cpf_mascarado=mascarar_cpf(gerar_cpf("900000004")),
            pin_hash=hash_pin("8765"),
            operadora_id=operadoras["metropolitana"].id,
        ),
    }
    db.add_all(motoristas.values())
    db.flush()

    veiculos = {
        "SVS1A23": Veiculo(
            placa="SVS1A23",
            modelo="110-MASTER",
            tipo="VAN",
            capacidade=15,
            acessivel=True,
            operadora_id=operadoras["litoral"].id,
            motorista_id=motoristas["carlos"].id,
        ),
        "SVS2B34": Veiculo(
            placa="SVS2B34",
            modelo="109-MASTER",
            tipo="VAN",
            capacidade=12,
            acessivel=False,
            operadora_id=operadoras["litoral"].id,
            motorista_id=motoristas["marina"].id,
        ),
        "DEM0C56": Veiculo(
            placa="DEM0C56",
            modelo="Micro-ônibus urbano",
            tipo="MICROONIBUS",
            capacidade=26,
            acessivel=True,
            operadora_id=operadoras["metropolitana"].id,
            motorista_id=motoristas["joao"].id,
        ),
        "TST9D87": Veiculo(
            placa="TST9D87",
            modelo="Van executiva",
            tipo="VAN",
            capacidade=10,
            acessivel=False,
            operadora_id=operadoras["metropolitana"].id,
            motorista_id=motoristas["rita"].id,
        ),
    }
    db.add_all(veiculos.values())

    pacientes = {
        "alfa": Paciente(
            nome="Paciente Demonstração Alfa",
            cpf_hash=hash_cpf(gerar_cpf("900000101")),
            cpf_mascarado=mascarar_cpf(gerar_cpf("900000101")),
            data_nascimento=date(1990, 5, 12),
            telefone_mascarado="(13) ****-0001",
            municipio_id=municipios["santos"].id,
            consentimento_em=agora - timedelta(days=30),
        ),
        "beta": Paciente(
            nome="Paciente Demonstração Beta",
            cpf_hash=hash_cpf(gerar_cpf("900000102")),
            cpf_mascarado=mascarar_cpf(gerar_cpf("900000102")),
            data_nascimento=date(1985, 11, 3),
            telefone_mascarado="(13) ****-0002",
            municipio_id=municipios["sao_vicente"].id,
            consentimento_em=agora - timedelta(days=20),
        ),
        "gama": Paciente(
            nome="Paciente Demonstração Gama",
            cpf_hash=hash_cpf(gerar_cpf("900000103")),
            cpf_mascarado=mascarar_cpf(gerar_cpf("900000103")),
            data_nascimento=date(1978, 2, 20),
            telefone_mascarado="(13) ****-0003",
            municipio_id=municipios["santos"].id,
            consentimento_em=agora - timedelta(days=10),
        ),
    }
    db.add_all(pacientes.values())

    unidades = {
        "ubs": UnidadeSaude(
            nome="UBS Nossa Senhora das Neves (demo)",
            tipo="UBS",
            municipio_id=municipios["santos"].id,
            latitude=-23.9380,
            longitude=-46.3600,
        ),
        "upa": UnidadeSaude(
            nome="UPA Central de Santos (demo)",
            tipo="UPA",
            municipio_id=municipios["santos"].id,
            latitude=-23.9530,
            longitude=-46.3320,
        ),
        "diadema": UnidadeSaude(
            nome="Hospital Estadual de Referência — Diadema (demo)",
            tipo="HOSPITAL",
            municipio_id=municipios["diadema"].id,
            latitude=-23.6860,
            longitude=-46.6200,
        ),
        "hc": UnidadeSaude(
            nome="Hospital das Clínicas — São Paulo (demo)",
            tipo="HOSPITAL",
            municipio_id=municipios["sao_paulo"].id,
            latitude=-23.5570,
            longitude=-46.6700,
        ),
        "cer": UnidadeSaude(
            nome="CER Baixada Santista (demo)",
            tipo="CER",
            municipio_id=municipios["santos"].id,
            latitude=-23.9650,
            longitude=-46.3400,
        ),
    }
    db.add_all(unidades.values())
    db.flush()

    viagens = {
        "t1": Viagem(
            data=hoje,
            veiculo_id=veiculos["SVS1A23"].id,
            motorista_id=motoristas["carlos"].id,
            origem_municipio_id=municipios["santos"].id,
            destino_unidade_id=unidades["diadema"].id,
            destino_texto="Hospital Estadual de Referência — Diadema (demo)",
            trajeto="IDA_E_VOLTA",
            status="EM_ANDAMENTO",
            partida_prevista=_em(hoje, 6, 0),
            retorno_previsto=_em(hoje, 18, 0),
            iniciada_em=_em(hoje, 6, 5),
        ),
        "t2": Viagem(
            data=hoje,
            veiculo_id=veiculos["SVS2B34"].id,
            motorista_id=motoristas["marina"].id,
            origem_municipio_id=municipios["sao_vicente"].id,
            destino_unidade_id=unidades["hc"].id,
            destino_texto="Hospital das Clínicas — São Paulo (demo)",
            trajeto="IDA_E_VOLTA",
            status="PLANEJADA",
            partida_prevista=_em(hoje, 7, 30),
            retorno_previsto=_em(hoje, 19, 0),
        ),
        "t3": Viagem(
            data=hoje - timedelta(days=1),
            veiculo_id=veiculos["SVS1A23"].id,
            motorista_id=motoristas["carlos"].id,
            origem_municipio_id=municipios["santos"].id,
            destino_unidade_id=unidades["diadema"].id,
            destino_texto="Hospital Estadual de Referência — Diadema (demo)",
            trajeto="IDA_E_VOLTA",
            status="CONCLUIDA",
            partida_prevista=_em(hoje - timedelta(days=1), 6, 0),
            retorno_previsto=_em(hoje - timedelta(days=1), 18, 0),
            iniciada_em=_em(hoje - timedelta(days=1), 6, 12),
            concluida_em=_em(hoje - timedelta(days=1), 17, 40),
        ),
        "t4": Viagem(
            data=hoje - timedelta(days=30),
            veiculo_id=veiculos["SVS2B34"].id,
            motorista_id=motoristas["marina"].id,
            origem_municipio_id=municipios["sao_vicente"].id,
            destino_unidade_id=unidades["hc"].id,
            destino_texto="Hospital das Clínicas — São Paulo (demo)",
            trajeto="IDA_E_VOLTA",
            status="CONCLUIDA",
            partida_prevista=_em(hoje - timedelta(days=30), 7, 0),
            retorno_previsto=_em(hoje - timedelta(days=30), 18, 0),
            iniciada_em=_em(hoje - timedelta(days=30), 7, 0),
            concluida_em=_em(hoje - timedelta(days=30), 18, 10),
        ),
    }
    db.add_all(viagens.values())
    db.flush()

    autorizacoes = [
        Autorizacao(
            viagem_id=viagens["t1"].id,
            paciente_id=pacientes["alfa"].id,
            numero=f"AUT-{hoje:%Y%m%d}-001",
            status="APROVADA",
            origem="SISTEMA",
            validada_em=agora - timedelta(days=2),
            validada_por="Central de Regulação (demo)",
        ),
        Autorizacao(
            viagem_id=viagens["t1"].id,
            paciente_id=pacientes["beta"].id,
            numero=f"AUT-{hoje:%Y%m%d}-002",
            status="APROVADA",
            origem="OFICIO",
            validada_em=agora - timedelta(days=2),
            validada_por="Central de Regulação (demo)",
        ),
        Autorizacao(
            viagem_id=viagens["t1"].id,
            paciente_id=pacientes["gama"].id,
            numero=f"AUT-{hoje:%Y%m%d}-003",
            status="PENDENTE",
            origem="SMS",
        ),
        Autorizacao(
            viagem_id=viagens["t2"].id,
            paciente_id=pacientes["gama"].id,
            numero=f"AUT-{hoje:%Y%m%d}-004",
            status="APROVADA",
            origem="SISTEMA",
            validada_em=agora - timedelta(days=1),
            validada_por="Central de Regulação (demo)",
        ),
        Autorizacao(
            viagem_id=viagens["t3"].id,
            paciente_id=pacientes["alfa"].id,
            numero=f"AUT-{hoje - timedelta(days=1):%Y%m%d}-001",
            status="APROVADA",
            origem="SISTEMA",
        ),
        Autorizacao(
            viagem_id=viagens["t4"].id,
            paciente_id=pacientes["beta"].id,
            numero=f"AUT-{hoje - timedelta(days=30):%Y%m%d}-001",
            status="APROVADA",
            origem="SISTEMA",
        ),
    ]
    db.add_all(autorizacoes)
    db.flush()

    db.add(
        Embarque(
            autorizacao_id=autorizacoes[0].id,
            embarcado_em=_em(hoje, 6, 12),
            metodo="QRCODE",
            registrado_por=motoristas["carlos"].nome,
        )
    )

    # Telemetria: trilha de 3h do veículo em operação + posições recentes/antigas
    for indice in range(25):
        fracao = 0.25 + 0.30 * (indice / 24)
        lat, lon = ponto_na_rota("santos-diadema", fracao)
        db.add(
            Posicao(
                veiculo_id=veiculos["SVS1A23"].id,
                viagem_id=viagens["t1"].id,
                latitude=lat,
                longitude=lon,
                velocidade_kmh=42 + (indice % 5) * 4,
                rumo=310.0,
                precisao_m=12.0,
                fonte="GATEWAY",
                capturada_em=agora - timedelta(minutes=3 * (24 - indice)),
                recebida_em=agora - timedelta(minutes=3 * (24 - indice)),
            )
        )
    lat, lon = ponto_na_rota("santos-sao-paulo", 0.18)
    db.add(
        Posicao(
            veiculo_id=veiculos["SVS2B34"].id,
            latitude=lat,
            longitude=lon,
            velocidade_kmh=38.0,
            rumo=300.0,
            precisao_m=18.0,
            fonte="GATEWAY",
            capturada_em=agora - timedelta(seconds=90),
            recebida_em=agora - timedelta(seconds=88),
        )
    )
    lat, lon = ponto_na_rota("santos-diadema", 0.10)
    db.add(
        Posicao(
            veiculo_id=veiculos["DEM0C56"].id,
            latitude=lat,
            longitude=lon,
            velocidade_kmh=0.0,
            precisao_m=35.0,
            fonte="GATEWAY",
            capturada_em=agora - timedelta(days=3),
            recebida_em=agora - timedelta(days=3),
        )
    )

    db.commit()
    return True


if __name__ == "__main__":  # pragma: no cover
    Base.metadata.create_all(engine)
    with SessionLocal() as sessao:
        criado = seed(sessao)
    print("Seed aplicado." if criado else "Banco já possui dados; nada a fazer.")
    print("Placas demo: SVS1A23 (PIN 1234), SVS2B34 (PIN 4321), DEM0C56, TST9D87")
