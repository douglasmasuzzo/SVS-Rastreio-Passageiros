"""Painel administrativo, ingestão de telemetria e contrato OpenAPI."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select

from app.models import Autorizacao, Paciente

CHAVE_ADMIN = "admin-de-teste"
CHAVE_INGESTAO = "chave-de-teste"

CAB_ADMIN = {"X-Admin-Key": CHAVE_ADMIN}
CAB_INGESTAO = {"X-Ingest-Key": CHAVE_INGESTAO}


def test_admin_exige_chave(client):
    assert client.get("/api/v1/admin/kpis").status_code == 401
    assert client.get("/api/v1/admin/kpis", headers={"X-Admin-Key": "errada"}).status_code == 401


def test_kpis_do_dia(client):
    resposta = client.get("/api/v1/admin/kpis", headers=CAB_ADMIN)
    assert resposta.status_code == 200, resposta.text
    dados = resposta.json()
    assert dados["veiculos_total"] == 4
    assert dados["veiculos_online"] == 2
    assert dados["viagens_total"] == 2
    assert dados["viagens_em_andamento"] == 1
    assert dados["autorizacoes_aprovadas"] == 3
    assert dados["autorizacoes_pendentes"] == 1
    assert dados["passageiros_embarcados"] == 1
    assert dados["atraso_medio_min"] == 5.0
    assert dados["otif_percentual"] == 0.0


def test_lista_de_viagens_do_admin(client):
    dados = client.get("/api/v1/admin/viagens", headers=CAB_ADMIN).json()
    assert dados["total"] == 2
    assert {v["placa"] for v in dados["viagens"]} == {"SVS1A23", "SVS2B34"}


def test_lista_autorizacoes_do_dia(client):
    dados = client.get("/api/v1/admin/autorizacoes", headers=CAB_ADMIN).json()
    assert dados["total"] == 4
    assert {a["status"] for a in dados["autorizacoes"]} == {"APROVADA", "PENDENTE"}
    assert all(a["cpf_mascarado"].startswith("***") for a in dados["autorizacoes"])
    assert all("cpf" not in a for a in dados["autorizacoes"])


def test_lista_autorizacoes_filtra_por_status(client):
    dados = client.get(
        "/api/v1/admin/autorizacoes", params={"status": "PENDENTE"}, headers=CAB_ADMIN
    ).json()
    assert dados["total"] == 1
    assert dados["autorizacoes"][0]["status"] == "PENDENTE"


def test_lista_autorizacoes_rejeita_status_invalido(client):
    resposta = client.get(
        "/api/v1/admin/autorizacoes", params={"status": "QUALQUER"}, headers=CAB_ADMIN
    )
    assert resposta.status_code == 422


def test_validar_autorizacao_pendente(client, db_session):
    db_session.expire_all()
    pendente = db_session.scalar(
        select(Autorizacao).where(Autorizacao.status == "PENDENTE")
    )
    resposta = client.post(
        f"/api/v1/admin/autorizacoes/{pendente.id}/validar",
        json={"status": "APROVADA", "validador": "Regulação Municipal"},
        headers=CAB_ADMIN,
    )
    assert resposta.status_code == 200, resposta.text
    dados = resposta.json()
    assert dados["status"] == "APROVADA"
    assert dados["validada_por"] == "Regulação Municipal"


def test_validar_autorizacao_de_viagem_planejada_muda_status(client, db_session):
    from app.models import Viagem

    db_session.expire_all()
    viagem = db_session.scalar(select(Viagem).where(Viagem.status == "PLANEJADA"))
    paciente = db_session.scalar(select(Paciente).where(Paciente.nome.like("%Alfa%")))
    nova = Autorizacao(
        viagem_id=viagem.id,
        paciente_id=paciente.id,
        numero="AUT-TESTE-999",
        status="PENDENTE",
    )
    db_session.add(nova)
    db_session.commit()

    resposta = client.post(
        f"/api/v1/admin/autorizacoes/{nova.id}/validar",
        json={"status": "APROVADA", "validador": "Regulação Municipal"},
        headers=CAB_ADMIN,
    )
    assert resposta.status_code == 200
    db_session.expire_all()
    assert db_session.get(Viagem, viagem.id).status == "AUTORIZADA"


def test_autorizacao_inexistente(client):
    resposta = client.post(
        "/api/v1/admin/autorizacoes/99999/validar",
        json={"status": "NEGADA", "validador": "Regulação"},
        headers=CAB_ADMIN,
    )
    assert resposta.status_code == 404


def test_exportacao_csv(client):
    resposta = client.get("/api/v1/admin/posicoes.csv", headers=CAB_ADMIN)
    assert resposta.status_code == 200
    assert resposta.headers["content-type"].startswith("text/csv")
    linhas = resposta.text.strip().splitlines()
    assert linhas[0].startswith("placa,viagem_id,latitude")
    assert len(linhas) > 20


def test_exportacao_com_intervalo_invalido(client):
    resposta = client.get(
        "/api/v1/admin/posicoes.csv",
        params={"inicio": "2026-10-10", "fim": "2026-10-01"},
        headers=CAB_ADMIN,
    )
    assert resposta.status_code == 422


def test_telemetria_exige_chave(client):
    corpo = {"placa": "SVS1A23", "latitude": -23.9, "longitude": -46.3}
    assert client.post("/api/v1/telemetria", json=corpo).status_code == 401
    assert (
        client.post(
            "/api/v1/telemetria", json=corpo, headers={"X-Ingest-Key": "errada"}
        ).status_code
        == 401
    )


def test_telemetria_atualiza_status(client):
    corpo = {
        "placa": "TST9D87",
        "latitude": -23.95,
        "longitude": -46.33,
        "velocidade_kmh": 22,
        "precisao_m": 15,
        "fonte": "GATEWAY",
    }
    resposta = client.post("/api/v1/telemetria", json=corpo, headers=CAB_INGESTAO)
    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["status"] == "ONLINE"
    publico = client.get("/api/v1/publico/veiculos/TST9D87").json()
    assert publico["online"] is True


def test_telemetria_placa_inexistente(client):
    resposta = client.post(
        "/api/v1/telemetria",
        json={"placa": "ZZZ9Z99", "latitude": -23.9, "longitude": -46.3},
        headers=CAB_INGESTAO,
    )
    assert resposta.status_code == 404


def test_telemetria_com_horario_futuro_e_rejeitada(client):
    futuro = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    resposta = client.post(
        "/api/v1/telemetria",
        json={
            "placa": "SVS1A23",
            "latitude": -23.9,
            "longitude": -46.3,
            "capturada_em": futuro,
        },
        headers=CAB_INGESTAO,
    )
    assert resposta.status_code == 422


def test_telemetria_com_viagem_de_outro_veiculo_e_rejeitada(client, db_session):
    from app.models import Viagem

    db_session.expire_all()
    viagem = db_session.scalar(select(Viagem).where(Viagem.veiculo.has(placa="SVS2B34")))
    resposta = client.post(
        "/api/v1/telemetria",
        json={
            "placa": "SVS1A23",
            "latitude": -23.9,
            "longitude": -46.3,
            "viagem_id": viagem.id,
        },
        headers=CAB_INGESTAO,
    )
    assert resposta.status_code == 422


def test_openapi_publicado(client):
    esquema = client.get("/openapi.json").json()
    assert esquema["info"]["version"] == "0.1.0"
    assert "/api/v1/publico/veiculos/{placa}" in esquema["paths"]
    assert "/api/v1/passageiro/consulta" in esquema["paths"]
    assert "/api/v1/motorista/sessao" in esquema["paths"]


def test_healthz(client):
    dados = client.get("/healthz").json()
    assert dados["status"] == "ok"
    assert dados["ambiente"] == "test"
