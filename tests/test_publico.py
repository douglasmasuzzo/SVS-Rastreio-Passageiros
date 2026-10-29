"""Rastreamento público: contrato, status online/offline e minimização de dados."""

from __future__ import annotations

from datetime import date

import pytest

from app.seed import gerar_cpf
from app.services.geo import distancia_km


def test_lista_veiculos_com_status(client):
    resposta = client.get("/api/v1/publico/veiculos")
    assert resposta.status_code == 200
    dados = resposta.json()
    assert dados["total"] == 4
    status = {v["placa"]: v["status"] for v in dados["veiculos"]}
    assert status["SVS1A23"] == "ONLINE"
    assert status["SVS2B34"] == "ONLINE"
    assert status["DEM0C56"] == "OFFLINE"
    assert status["TST9D87"] == "OFFLINE"


def test_busca_parcial_por_placa(client):
    dados = client.get("/api/v1/publico/veiculos", params={"busca": "svs"}).json()
    assert {v["placa"] for v in dados["veiculos"]} == {"SVS1A23", "SVS2B34"}


@pytest.mark.parametrize("placa", ["svs1a23", "SVS-1A23", " svs 1a23 "])
def test_placa_tolerante_a_formato(client, placa):
    assert client.get(f"/api/v1/publico/veiculos/{placa}").status_code == 200


def test_placa_inexistente_retorna_mesma_mensagem(client):
    invalida = client.get("/api/v1/publico/veiculos/ABC")
    inexistente = client.get("/api/v1/publico/veiculos/ZZZ9Z99")
    assert invalida.status_code == inexistente.status_code == 404
    assert invalida.json() == inexistente.json()


def test_posicao_publica_nao_expoe_dados_pessoais(client):
    resposta = client.get("/api/v1/publico/veiculos/SVS1A23")
    assert resposta.status_code == 200
    corpo = resposta.text.lower()
    assert "cpf" not in corpo
    assert "motorista" not in corpo
    assert "paciente" not in corpo
    dados = resposta.json()
    assert dados["operadora"]
    assert dados["posicao"]["posicao_aproximada"] is False
    # coordenadas arredondadas para 4 casas (~11 m)
    assert len(str(dados["posicao"]["latitude"]).split(".")[1]) <= 4


def test_distancia_ate_o_usuario(client):
    referencia = (-23.9608, -46.3336)
    dados = client.get(
        "/api/v1/publico/veiculos/SVS1A23",
        params={"lat": referencia[0], "lon": referencia[1]},
    ).json()
    posicao = dados["posicao"]
    esperado = distancia_km(referencia[0], referencia[1], posicao["latitude"], posicao["longitude"])
    assert posicao["distancia_ate_voce_km"] == pytest.approx(esperado, abs=0.05)
    assert posicao["distancia_ate_voce_km"] > 0


def test_lat_sem_lon_e_rejeitado(client):
    resposta = client.get("/api/v1/publico/veiculos/SVS1A23", params={"lat": -23.9})
    assert resposta.status_code == 422


def test_trilha_ordenada_e_limitada(client):
    dados = client.get("/api/v1/publico/veiculos/SVS1A23/trilha").json()
    pontos = dados["pontos"]
    assert len(pontos) == 25
    momentos = [p["capturada_em"] for p in pontos]
    assert momentos == sorted(momentos)


def test_resumo_de_viagens_sem_dados_de_pacientes(client):
    dados = client.get(
        "/api/v1/publico/veiculos/SVS1A23/viagens", params={"data": date.today().isoformat()}
    ).json()
    assert dados["total_autorizacoes"] == 2
    assert len(dados["viagens"]) == 1
    assert "pacientes" not in client.get(
        "/api/v1/publico/veiculos/SVS1A23/viagens"
    ).text.lower()


def test_veiculo_sem_viagem_no_dia(client):
    dados = client.get("/api/v1/publico/veiculos/DEM0C56/viagens").json()
    assert dados["total_autorizacoes"] == 0
    assert dados["viagens"] == []


def test_cpf_nao_aparece_em_nenhum_endpoint_publico(client):
    for placa in ["SVS1A23", "SVS2B34", "DEM0C56", "TST9D87"]:
        assert gerar_cpf("900000101") not in client.get(
            f"/api/v1/publico/veiculos/{placa}"
        ).text
