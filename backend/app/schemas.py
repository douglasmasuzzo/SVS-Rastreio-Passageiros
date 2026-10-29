"""Contratos de entrada/saída (Pydantic v2) — base do OpenAPI publicado em /docs."""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer, field_validator

from .security import cpf_valido


def _iso_z(valor: datetime) -> str:
    if valor.tzinfo is None:
        valor = valor.replace(tzinfo=UTC)
    return valor.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


UTCDateTime = Annotated[datetime, PlainSerializer(_iso_z, return_type=str)]

StatusVeiculo = Literal["ONLINE", "OFFLINE"]
MetodoEmbarque = Literal["QRCODE", "CPF", "MANUAL"]
TipoEvento = Literal["INICIO", "CHEGADA_DESTINO", "FIM", "ATRASO", "INCIDENTE", "OBSERVACAO"]
FontePosicao = Literal["APP_MOTORISTA", "GATEWAY", "SIMULADOR"]


class ErroOut(BaseModel):
    detail: str


# --------------------------------------------------------------------------- #
# Rastreamento público
# --------------------------------------------------------------------------- #
class ViagemAtivaOut(BaseModel):
    id: int
    status: str
    destino: str
    trajeto: str
    partida_prevista: UTCDateTime


class PosicaoOut(BaseModel):
    latitude: float
    longitude: float
    velocidade_kmh: float
    rumo: float | None = None
    precisao_m: float
    posicao_aproximada: bool
    capturada_em: UTCDateTime
    distancia_ate_voce_km: float | None = None


class VeiculoPublicoOut(BaseModel):
    placa: str
    modelo: str
    tipo: str
    acessivel: bool
    operadora: str
    status: StatusVeiculo
    online: bool
    ultima_atualizacao: UTCDateTime | None = None
    idade_segundos: int | None = None
    posicao: PosicaoOut | None = None
    viagem_ativa: ViagemAtivaOut | None = None


class ListaVeiculosOut(BaseModel):
    total: int
    veiculos: list[VeiculoPublicoOut]


class PontoTrilhaOut(BaseModel):
    latitude: float
    longitude: float
    capturada_em: UTCDateTime


class TrilhaOut(BaseModel):
    placa: str
    pontos: list[PontoTrilhaOut]


class ViagemResumoOut(BaseModel):
    id: int
    status: str
    trajeto: str
    destino: str
    partida_prevista: UTCDateTime
    autorizacoes: int


class ResumoViagensOut(BaseModel):
    placa: str
    data: date
    total_autorizacoes: int
    viagens: list[ViagemResumoOut]


# --------------------------------------------------------------------------- #
# Passageiro
# --------------------------------------------------------------------------- #
class ConsultaPassageiroIn(BaseModel):
    cpf: str = Field(..., examples=["111.444.777-35"])
    data_nascimento: date = Field(..., examples=["1990-05-12"])
    data: date | None = Field(None, description="Data da viagem; padrão = hoje")

    @field_validator("cpf")
    @classmethod
    def _cpf_valido(cls, valor: str) -> str:
        if not cpf_valido(valor):
            raise ValueError("CPF inválido")
        return valor


class PacienteResumoOut(BaseModel):
    nome: str
    cpf_mascarado: str
    municipio: str


class VeiculoResumoOut(BaseModel):
    placa: str
    modelo: str
    acessivel: bool
    operadora: str


class ViagemHojeOut(BaseModel):
    viagem_id: int
    autorizacao_id: int
    numero_autorizacao: str
    status: str
    trajeto: str
    destino: str
    partida_prevista: UTCDateTime
    retorno_previsto: UTCDateTime | None = None
    veiculo: VeiculoResumoOut
    motorista: str
    acompanhamento_em_tempo_real: bool
    embarcado: bool


class HistoricoItemOut(BaseModel):
    viagem_id: int
    data: date
    status: str
    status_autorizacao: str
    destino: str
    trajeto: str
    placa: str
    acompanhamento_em_tempo_real: bool


class ConsultaPassageiroOut(BaseModel):
    paciente: PacienteResumoOut
    data_consulta: date
    possui_agendamento: bool
    viagem_hoje: ViagemHojeOut | None = None
    historico: list[HistoricoItemOut]


# --------------------------------------------------------------------------- #
# Motorista
# --------------------------------------------------------------------------- #
class SessaoMotoristaIn(BaseModel):
    placa: str = Field(..., examples=["SVS1A23"])
    pin: str = Field(..., min_length=4, max_length=12)


class MotoristaResumoOut(BaseModel):
    id: int
    nome: str
    cpf_mascarado: str


class SessaoMotoristaOut(BaseModel):
    token: str
    expira_em: UTCDateTime
    motorista: MotoristaResumoOut
    veiculo: VeiculoResumoOut


class ViagemMotoristaOut(BaseModel):
    id: int
    data: date
    status: str
    trajeto: str
    destino: str
    partida_prevista: UTCDateTime
    retorno_previsto: UTCDateTime | None = None
    autorizacoes: int
    embarques: int


class ListaViagensMotoristaOut(BaseModel):
    data: date
    veiculo: VeiculoResumoOut
    viagens: list[ViagemMotoristaOut]


class EmbarqueOut(BaseModel):
    autorizacao_id: int
    embarcado_em: UTCDateTime
    metodo: str


class PassageiroViagemOut(BaseModel):
    autorizacao_id: int
    paciente_id: int
    nome: str
    cpf_mascarado: str
    unidade: str | None = None
    status_autorizacao: str
    embarque: EmbarqueOut | None = None


class ListaPassageirosOut(BaseModel):
    viagem_id: int
    total: int
    passageiros: list[PassageiroViagemOut]


class EmbarqueIn(BaseModel):
    autorizacao_id: int
    metodo: MetodoEmbarque = "MANUAL"


class EventoIn(BaseModel):
    tipo: TipoEvento
    observacao: str | None = Field(None, max_length=500)


class EventoOut(BaseModel):
    id: int
    viagem_id: int
    tipo: str
    observacao: str | None = None
    criado_em: UTCDateTime


# --------------------------------------------------------------------------- #
# Telemetria
# --------------------------------------------------------------------------- #
class TelemetriaIn(BaseModel):
    placa: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    velocidade_kmh: float = Field(0, ge=0, le=200)
    rumo: float | None = Field(None, ge=0, le=360)
    precisao_m: float = Field(10, ge=0, le=5000)
    capturada_em: datetime | None = None
    viagem_id: int | None = None
    fonte: FontePosicao = "GATEWAY"


class TelemetriaOut(BaseModel):
    id: int
    recebida_em: UTCDateTime
    status: StatusVeiculo


# --------------------------------------------------------------------------- #
# Administração
# --------------------------------------------------------------------------- #
class KpisOut(BaseModel):
    data: date
    veiculos_total: int
    veiculos_online: int
    viagens_total: int
    viagens_em_andamento: int
    autorizacoes_aprovadas: int
    autorizacoes_pendentes: int
    passageiros_embarcados: int
    otif_percentual: float
    atraso_medio_min: float


class ViagemAdminOut(BaseModel):
    id: int
    data: date
    placa: str
    motorista: str
    status: str
    trajeto: str
    destino: str
    partida_prevista: UTCDateTime
    iniciada_em: UTCDateTime | None = None
    concluida_em: UTCDateTime | None = None
    autorizacoes: int
    embarques: int
    atraso_min: int | None = None


class ListaViagensAdminOut(BaseModel):
    data: date
    total: int
    viagens: list[ViagemAdminOut]


class ValidacaoIn(BaseModel):
    status: Literal["APROVADA", "NEGADA"]
    validador: str = Field(..., min_length=3, max_length=120)


class AutorizacaoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: str
    status: str
    paciente_id: int
    viagem_id: int
    validada_em: UTCDateTime | None = None
    validada_por: str | None = None


class AutorizacaoAdminOut(BaseModel):
    id: int
    numero: str
    status: str
    origem: str
    paciente: str
    cpf_mascarado: str
    data: date
    placa: str
    destino: str
    viagem_id: int
    partida_prevista: UTCDateTime
    validada_em: UTCDateTime | None = None
    validada_por: str | None = None
    embarcado_em: UTCDateTime | None = None


class ListaAutorizacoesAdminOut(BaseModel):
    data: date
    total: int
    autorizacoes: list[AutorizacaoAdminOut]
