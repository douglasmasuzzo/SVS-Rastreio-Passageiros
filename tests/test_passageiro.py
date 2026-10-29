"""Consulta do passageiro: segundo fator, mascaramento, histórico e auditoria."""

from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import select

from app.models import AuditLog
from app.security import mascarar_cpf
from app.seed import gerar_cpf

CPF_ALFA = gerar_cpf("900000101")
CPF_BETA = gerar_cpf("900000102")
CPF_GAMA = gerar_cpf("900000103")


def _consulta(client, cpf, nascimento, data=None):
    corpo = {"cpf": cpf, "data_nascimento": nascimento}
    if data:
        corpo["data"] = data
    return client.post("/api/v1/passageiro/consulta", json=corpo)


def test_consulta_com_agendamento_e_acompanhamento(client):
    resposta = _consulta(client, CPF_ALFA, "1990-05-12")
    assert resposta.status_code == 200, resposta.text
    dados = resposta.json()
    assert dados["possui_agendamento"] is True
    assert dados["viagem_hoje"]["veiculo"]["placa"] == "SVS1A23"
    assert dados["viagem_hoje"]["acompanhamento_em_tempo_real"] is True
    assert dados["viagem_hoje"]["embarcado"] is True
    assert dados["viagem_hoje"]["motorista"] == "Carlos A."
    assert dados["paciente"]["nome"] == "Paciente Demonstração Alfa"


def test_cpf_sempre_mascarado_na_resposta(client):
    resposta = _consulta(client, CPF_ALFA, "1990-05-12")
    assert CPF_ALFA not in resposta.text
    assert resposta.json()["paciente"]["cpf_mascarado"] == mascarar_cpf(CPF_ALFA)


def test_historico_traz_viagens_anteriores(client):
    dados = _consulta(client, CPF_ALFA, "1990-05-12").json()
    assert len(dados["historico"]) >= 1
    assert all(item["acompanhamento_em_tempo_real"] is False for item in dados["historico"])


def test_sem_agendamento_mas_com_historico(client):
    # Gama tem viagem aprovada hoje (T2) e uma autorização pendente (T1)
    dados = _consulta(client, CPF_GAMA, "1978-02-20").json()
    assert dados["possui_agendamento"] is True
    assert dados["viagem_hoje"]["destino"].startswith("Hospital das Clínicas")
    pendentes = [h for h in dados["historico"] if h["status_autorizacao"] == "PENDENTE"]
    assert len(pendentes) == 1


def test_consulta_de_data_passada(client):
    anterior = (date.today() - timedelta(days=40)).isoformat()
    resposta = _consulta(client, CPF_BETA, "1985-11-03", data=anterior)
    assert resposta.status_code == 200
    assert resposta.json()["possui_agendamento"] is False


def test_data_de_nascimento_errada_retorna_generico(client):
    resposta = _consulta(client, CPF_ALFA, "1990-05-13")
    assert resposta.status_code == 404
    assert "CPF" in resposta.json()["detail"] or "cadastro" in resposta.json()["detail"]


def test_cpf_inexistente_retorna_mesma_mensagem(client):
    errada = _consulta(client, CPF_ALFA, "1990-05-13")
    inexistente = _consulta(client, gerar_cpf("900000199"), "1990-05-12")
    assert errada.status_code == inexistente.status_code == 404
    assert errada.json() == inexistente.json()


def test_cpf_invalido_e_rejeitado_na_validacao(client):
    resposta = _consulta(client, "111.111.111-11", "1990-05-12")
    assert resposta.status_code == 422


def test_consulta_gera_registro_de_auditoria(client, db_session):
    _consulta(client, CPF_ALFA, "1990-05-12")
    db_session.expire_all()
    registros = db_session.scalars(
        select(AuditLog).where(AuditLog.acao == "consulta_agendamento")
    ).all()
    assert len(registros) == 1
    assert registros[0].recurso == "paciente"
    assert registros[0].ip_hash is not None


def test_falha_de_consulta_tambem_e_auditada(client, db_session):
    _consulta(client, CPF_ALFA, "2000-01-01")
    db_session.expire_all()
    falhas = db_session.scalars(select(AuditLog).where(AuditLog.acao == "consulta_falha")).all()
    assert len(falhas) == 1
