"""Modelo de dados (SQLAlchemy 2.0).

Decisões relevantes de LGPD já no schema:
- nenhum CPF em texto claro: guardamos `cpf_hash` (HMAC-SHA256 com pepper) e
  `cpf_mascarado` para exibição;
- nenhum PIN em texto claro: `pin_hash`;
- telemetria é imutável (append-only) e auditável por `recebida_em`;
- `AuditLog` registra acesso a dados sensíveis (consulta de paciente, check-in).
"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from .domain import (
    FONTES_POSICAO,
    METODOS_EMBARQUE,
    ORIGENS_AUTORIZACAO,
    STATUS_AUTORIZACAO,
    STATUS_VIAGEM,
    TIPOS_EVENTO,
    TIPOS_TRAJETO,
    TIPOS_UNIDADE,
)
from .timeutil import utcnow


class Base(DeclarativeBase):
    pass


def _em_lista(coluna: str, valores: tuple[str, ...]) -> str:
    itens = ", ".join(f"'{v}'" for v in valores)
    return f"{coluna} IN ({itens})"


class Municipio(Base):
    __tablename__ = "municipio"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo_ibge: Mapped[str] = mapped_column(String(7), unique=True)
    nome: Mapped[str] = mapped_column(String(120), index=True)
    uf: Mapped[str] = mapped_column(String(2))


class Operadora(Base):
    __tablename__ = "operadora"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), unique=True)
    cnpj: Mapped[str | None] = mapped_column(String(18))
    contato: Mapped[str | None] = mapped_column(String(160))
    ativa: Mapped[bool] = mapped_column(Boolean, default=True)

    veiculos: Mapped[list[Veiculo]] = relationship(back_populates="operadora")


class Veiculo(Base):
    __tablename__ = "veiculo"

    id: Mapped[int] = mapped_column(primary_key=True)
    placa: Mapped[str] = mapped_column(String(8), unique=True, index=True)
    modelo: Mapped[str] = mapped_column(String(80))
    tipo: Mapped[str] = mapped_column(String(30), default="VAN")
    capacidade: Mapped[int] = mapped_column(Integer, default=15)
    acessivel: Mapped[bool] = mapped_column(Boolean, default=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    operadora_id: Mapped[int] = mapped_column(ForeignKey("operadora.id"))
    motorista_id: Mapped[int | None] = mapped_column(ForeignKey("motorista.id"))

    operadora: Mapped[Operadora] = relationship(back_populates="veiculos")
    motorista: Mapped[Motorista | None] = relationship(foreign_keys=[motorista_id])

    __table_args__ = (
        CheckConstraint("capacidade > 0", name="ck_veiculo_capacidade_positiva"),
    )


class Motorista(Base):
    __tablename__ = "motorista"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    cpf_hash: Mapped[str] = mapped_column(String(64), unique=True)
    cpf_mascarado: Mapped[str] = mapped_column(String(14))
    pin_hash: Mapped[str] = mapped_column(String(64))
    cnh_categoria: Mapped[str] = mapped_column(String(5), default="D")
    operadora_id: Mapped[int] = mapped_column(ForeignKey("operadora.id"))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    operadora: Mapped[Operadora] = relationship()


class Paciente(Base):
    __tablename__ = "paciente"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    cpf_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    cpf_mascarado: Mapped[str] = mapped_column(String(14))
    data_nascimento: Mapped[date] = mapped_column(Date)
    telefone_mascarado: Mapped[str | None] = mapped_column(String(20))
    municipio_id: Mapped[int] = mapped_column(ForeignKey("municipio.id"))
    consentimento_em: Mapped[datetime | None] = mapped_column(DateTime)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    municipio: Mapped[Municipio] = relationship()


class UnidadeSaude(Base):
    __tablename__ = "unidade_saude"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(160))
    tipo: Mapped[str] = mapped_column(String(30))
    municipio_id: Mapped[int] = mapped_column(ForeignKey("municipio.id"))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

    municipio: Mapped[Municipio] = relationship()

    __table_args__ = (
        CheckConstraint(_em_lista("tipo", TIPOS_UNIDADE), name="ck_unidade_tipo"),
        CheckConstraint("latitude BETWEEN -90 AND 90", name="ck_unidade_lat"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="ck_unidade_lon"),
    )


class Viagem(Base):
    __tablename__ = "viagem"

    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[date] = mapped_column(Date, index=True)
    veiculo_id: Mapped[int] = mapped_column(ForeignKey("veiculo.id"), index=True)
    motorista_id: Mapped[int] = mapped_column(ForeignKey("motorista.id"))
    origem_municipio_id: Mapped[int] = mapped_column(ForeignKey("municipio.id"))
    destino_unidade_id: Mapped[int | None] = mapped_column(ForeignKey("unidade_saude.id"))
    destino_texto: Mapped[str] = mapped_column(String(160))
    trajeto: Mapped[str] = mapped_column(String(15), default="IDA_E_VOLTA")
    status: Mapped[str] = mapped_column(String(20), default="PLANEJADA", index=True)
    partida_prevista: Mapped[datetime] = mapped_column(DateTime)
    retorno_previsto: Mapped[datetime | None] = mapped_column(DateTime)
    iniciada_em: Mapped[datetime | None] = mapped_column(DateTime)
    concluida_em: Mapped[datetime | None] = mapped_column(DateTime)
    observacao: Mapped[str | None] = mapped_column(Text)

    veiculo: Mapped[Veiculo] = relationship()
    motorista: Mapped[Motorista] = relationship()
    origem: Mapped[Municipio] = relationship()
    destino: Mapped[UnidadeSaude | None] = relationship()

    autorizacoes: Mapped[list[Autorizacao]] = relationship(
        back_populates="viagem", cascade="all, delete-orphan"
    )
    posicoes: Mapped[list[Posicao]] = relationship(back_populates="viagem")

    __table_args__ = (
        CheckConstraint(_em_lista("status", STATUS_VIAGEM), name="ck_viagem_status"),
        CheckConstraint(_em_lista("trajeto", TIPOS_TRAJETO), name="ck_viagem_trajeto"),
        Index("ix_viagem_veiculo_data", "veiculo_id", "data"),
    )


class Autorizacao(Base):
    """Autorização municipal que vincula um paciente a uma viagem."""

    __tablename__ = "autorizacao"

    id: Mapped[int] = mapped_column(primary_key=True)
    viagem_id: Mapped[int] = mapped_column(ForeignKey("viagem.id", ondelete="CASCADE"), index=True)
    paciente_id: Mapped[int] = mapped_column(ForeignKey("paciente.id"), index=True)
    numero: Mapped[str] = mapped_column(String(40), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDENTE", index=True)
    origem: Mapped[str] = mapped_column(String(20), default="SISTEMA")
    emitida_em: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    validada_em: Mapped[datetime | None] = mapped_column(DateTime)
    validada_por: Mapped[str | None] = mapped_column(String(120))

    viagem: Mapped[Viagem] = relationship(back_populates="autorizacoes")
    paciente: Mapped[Paciente] = relationship()
    embarque: Mapped[Embarque | None] = relationship(
        back_populates="autorizacao", uselist=False, cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(_em_lista("status", STATUS_AUTORIZACAO), name="ck_autorizacao_status"),
        CheckConstraint(_em_lista("origem", ORIGENS_AUTORIZACAO), name="ck_autorizacao_origem"),
        UniqueConstraint("viagem_id", "paciente_id", name="uq_autorizacao_viagem_paciente"),
    )


class Embarque(Base):
    __tablename__ = "embarque"

    id: Mapped[int] = mapped_column(primary_key=True)
    autorizacao_id: Mapped[int] = mapped_column(
        ForeignKey("autorizacao.id", ondelete="CASCADE"), unique=True
    )
    embarcado_em: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    desembarcado_em: Mapped[datetime | None] = mapped_column(DateTime)
    metodo: Mapped[str] = mapped_column(String(15), default="MANUAL")
    registrado_por: Mapped[str | None] = mapped_column(String(120))

    autorizacao: Mapped[Autorizacao] = relationship(back_populates="embarque")

    __table_args__ = (CheckConstraint(_em_lista("metodo", METODOS_EMBARQUE), name="ck_embarque_metodo"),)


class Posicao(Base):
    """Ponto de telemetria — append-only, nunca atualizado."""

    __tablename__ = "posicao"

    id: Mapped[int] = mapped_column(primary_key=True)
    veiculo_id: Mapped[int] = mapped_column(ForeignKey("veiculo.id"), index=True)
    viagem_id: Mapped[int | None] = mapped_column(ForeignKey("viagem.id"), index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    velocidade_kmh: Mapped[float] = mapped_column(Float, default=0.0)
    rumo: Mapped[float | None] = mapped_column(Float)
    precisao_m: Mapped[float] = mapped_column(Float, default=10.0)
    fonte: Mapped[str] = mapped_column(String(20), default="GATEWAY")
    capturada_em: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)
    recebida_em: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    viagem: Mapped[Viagem | None] = relationship(back_populates="posicoes")

    __table_args__ = (
        CheckConstraint("latitude BETWEEN -90 AND 90", name="ck_posicao_lat"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="ck_posicao_lon"),
        CheckConstraint("velocidade_kmh >= 0", name="ck_posicao_velocidade"),
        CheckConstraint(_em_lista("fonte", FONTES_POSICAO), name="ck_posicao_fonte"),
        Index("ix_posicao_veiculo_capturada", "veiculo_id", "capturada_em"),
    )


class EventoViagem(Base):
    __tablename__ = "evento_viagem"

    id: Mapped[int] = mapped_column(primary_key=True)
    viagem_id: Mapped[int] = mapped_column(ForeignKey("viagem.id", ondelete="CASCADE"), index=True)
    tipo: Mapped[str] = mapped_column(String(20))
    observacao: Mapped[str | None] = mapped_column(Text)
    ator: Mapped[str | None] = mapped_column(String(120))
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    __table_args__ = (CheckConstraint(_em_lista("tipo", TIPOS_EVENTO), name="ck_evento_tipo"),)


class AuditLog(Base):
    """Trilha de auditoria para acessos a dados pessoais e ações de operação."""

    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    ator_tipo: Mapped[str] = mapped_column(String(20))
    ator_ref: Mapped[str | None] = mapped_column(String(80))
    acao: Mapped[str] = mapped_column(String(60), index=True)
    recurso: Mapped[str] = mapped_column(String(60))
    recurso_id: Mapped[str | None] = mapped_column(String(60))
    ip_hash: Mapped[str | None] = mapped_column(String(64))
    detalhe: Mapped[str | None] = mapped_column(Text)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)
