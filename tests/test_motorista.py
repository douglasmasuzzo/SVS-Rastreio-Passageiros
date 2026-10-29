"""Jornada do motorista: sessão, escopo por veículo, passageiros e eventos."""

from __future__ import annotations

from datetime import date

from sqlalchemy import select

from app.models import Viagem


def _auth(sessao):
    return {"Authorization": f"Bearer {sessao['token']}"}


def _viagens(client, sessao):
    resposta = client.get("/api/v1/motorista/viagens", headers=_auth(sessao))
    assert resposta.status_code == 200, resposta.text
    return resposta.json()


def test_sessao_com_pin_errado(client):
    resposta = client.post(
        "/api/v1/motorista/sessao", json={"placa": "SVS1A23", "pin": "9999"}
    )
    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "Placa ou PIN inválidos"


def test_sessao_de_placa_inexistente(client):
    resposta = client.post(
        "/api/v1/motorista/sessao", json={"placa": "ZZZ9Z99", "pin": "1234"}
    )
    assert resposta.status_code == 401


def test_sessao_valida_retorna_token_e_veiculo(client, sessao_motorista):
    assert sessao_motorista["veiculo"]["placa"] == "SVS1A23"
    assert sessao_motorista["motorista"]["nome"].startswith("Carlos")
    assert sessao_motorista["token"]


def test_endpoint_sem_token_e_bloqueado(client):
    assert client.get("/api/v1/motorista/viagens").status_code == 401
    assert (
        client.get(
            "/api/v1/motorista/viagens", headers={"Authorization": "Bearer invalido"}
        ).status_code
        == 401
    )


def test_lista_viagens_do_dia(client, sessao_motorista):
    dados = _viagens(client, sessao_motorista)
    assert dados["data"] == date.today().isoformat()
    assert len(dados["viagens"]) == 1
    assert dados["viagens"][0]["autorizacoes"] == 2
    assert dados["viagens"][0]["embarques"] == 1


def test_lista_passageiros_autorizados(client, sessao_motorista):
    viagem_id = _viagens(client, sessao_motorista)["viagens"][0]["id"]
    resposta = client.get(
        f"/api/v1/motorista/viagens/{viagem_id}/passageiros", headers=_auth(sessao_motorista)
    )
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["total"] == 2
    assert all(p["cpf_mascarado"].startswith("***") for p in dados["passageiros"])
    assert any(p["embarque"] is not None for p in dados["passageiros"])


def test_registrar_embarque_idempotente(client, sessao_motorista):
    viagem_id = _viagens(client, sessao_motorista)["viagens"][0]["id"]
    passageiros = client.get(
        f"/api/v1/motorista/viagens/{viagem_id}/passageiros", headers=_auth(sessao_motorista)
    ).json()["passageiros"]
    pendente = next(p for p in passageiros if p["embarque"] is None)

    primeira = client.post(
        f"/api/v1/motorista/viagens/{viagem_id}/embarques",
        json={"autorizacao_id": pendente["autorizacao_id"], "metodo": "CPF"},
        headers=_auth(sessao_motorista),
    )
    segunda = client.post(
        f"/api/v1/motorista/viagens/{viagem_id}/embarques",
        json={"autorizacao_id": pendente["autorizacao_id"], "metodo": "MANUAL"},
        headers=_auth(sessao_motorista),
    )
    assert primeira.status_code == 200
    assert segunda.status_code == 200
    assert primeira.json()["embarcado_em"] == segunda.json()["embarcado_em"]
    assert primeira.json()["metodo"] == "CPF"


def test_embarque_de_autorizacao_pendente_e_bloqueado(client, sessao_motorista, db_session):
    from app.models import Autorizacao

    viagem_id = _viagens(client, sessao_motorista)["viagens"][0]["id"]
    db_session.expire_all()
    pendente = db_session.scalar(
        select(Autorizacao).where(
            Autorizacao.viagem_id == viagem_id, Autorizacao.status == "PENDENTE"
        )
    )
    resposta = client.post(
        f"/api/v1/motorista/viagens/{viagem_id}/embarques",
        json={"autorizacao_id": pendente.id, "metodo": "MANUAL"},
        headers=_auth(sessao_motorista),
    )
    assert resposta.status_code == 409


def test_evento_inicio_muda_status_e_publica_viagem_ativa(client):
    sessao = client.post(
        "/api/v1/motorista/sessao", json={"placa": "SVS2B34", "pin": "4321"}
    ).json()
    viagem_id = _viagens(client, sessao)["viagens"][0]["id"]
    resposta = client.post(
        f"/api/v1/motorista/viagens/{viagem_id}/eventos",
        json={"tipo": "INICIO"},
        headers=_auth(sessao),
    )
    assert resposta.status_code == 200
    assert resposta.json()["tipo"] == "INICIO"

    publico = client.get("/api/v1/publico/veiculos/SVS2B34").json()
    assert publico["viagem_ativa"]["id"] == viagem_id
    assert publico["viagem_ativa"]["status"] == "EM_ANDAMENTO"


def test_evento_fim_conclui_viagem(client, sessao_motorista, db_session):
    viagem_id = _viagens(client, sessao_motorista)["viagens"][0]["id"]
    resposta = client.post(
        f"/api/v1/motorista/viagens/{viagem_id}/eventos",
        json={"tipo": "FIM", "observacao": "Retorno concluído"},
        headers=_auth(sessao_motorista),
    )
    assert resposta.status_code == 200
    db_session.expire_all()
    viagem = db_session.get(Viagem, viagem_id)
    assert viagem.status == "CONCLUIDA"
    assert viagem.concluida_em is not None


def test_motorista_nao_acessa_viagem_de_outro_veiculo(client, sessao_motorista, db_session):
    db_session.expire_all()
    viagem_id = db_session.scalar(
        select(Viagem.id).where(Viagem.veiculo.has(placa="SVS2B34"))
    )
    resposta = client.get(
        f"/api/v1/motorista/viagens/{viagem_id}/passageiros", headers=_auth(sessao_motorista)
    )
    assert resposta.status_code == 404


def test_app_do_motorista_envia_posicao(client, sessao_motorista):
    resposta = client.post(
        "/api/v1/motorista/posicao",
        json={
            "placa": "IGNORADA",
            "latitude": -23.95,
            "longitude": -46.34,
            "velocidade_kmh": 33.5,
            "precisao_m": 8,
        },
        headers=_auth(sessao_motorista),
    )
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "ONLINE"

    publico = client.get("/api/v1/publico/veiculos/SVS1A23").json()
    assert publico["posicao"]["velocidade_kmh"] == 33.5
