# 06 — API

## 1. Convenções

| Item | Definição |
| --- | --- |
| Base local | `http://localhost:8000` |
| Prefixo | `/api/v1` |
| Formato | JSON UTF-8; CSV na exportação |
| Datas | `YYYY-MM-DD` |
| Data/hora | ISO 8601 em UTC, com sufixo `Z` |
| Erro | `{"detail": "mensagem"}` |
| Versionamento | Prefixo de caminho (`/v1`); mudanças incompatíveis → `/v2` |
| Contrato | [`openapi/openapi.yaml`](../openapi/openapi.yaml) (18 caminhos) |
| Docs interativas | `/docs` (Swagger UI) e `/redoc` |

## 2. Autenticação e autorização

| Grupo | Esquema | Cabeçalho | Validade |
| --- | --- | --- | --- |
| Público | nenhum | — | — |
| Passageiro | dois fatores no corpo | — | por requisição |
| Motorista | Bearer HMAC | `Authorization: Bearer <token>` | 8 h |
| Telemetria | chave de serviço | `X-Ingest-Key: <chave>` | estática (protótipo) |
| Administração | chave de serviço | `X-Admin-Key: <chave>` | estática (protótipo) |

- As chaves são comparadas com `hmac.compare_digest`.
- Credencial ausente ou inválida → `401 {"detail": "Credencial inválida"}` ou
  `{"detail": "Sessão inválida"}`.
- Não há escopos/RBAC no protótipo: a chave administrativa dá acesso a todo o
  grupo `/admin`. Isso está registrado como risco residual.

### 2.1 Rate limit

| Escopo | Limite padrão | Janela | Configuração |
| --- | --- | --- | --- |
| Rotas públicas | 60 req | 60 s | `SVS_PUBLIC_RATE_LIMIT` / `SVS_PUBLIC_RATE_WINDOW` |
| Consulta do passageiro | 10 req | 60 s | derivado (mín. 5) |
| Sessão do motorista | 10 req | 60 s | derivado (mín. 5) |

Ao exceder: `429` com `Retry-After` em segundos. O limitador é em memória e
por processo; em produção deve ser distribuído (Redis/API Gateway).

## 3. Rastreamento público

### 3.1 `GET /api/v1/publico/veiculos`

Lista veículos ativos com status e posição aproximada.

| Parâmetro | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `busca` | string (≤ 8) | não | Trecho da placa; ignora hífen/espaços |

```http
GET /api/v1/publico/veiculos?busca=svs
```

```json
{
  "total": 2,
  "veiculos": [
    {
      "placa": "SVS1A23",
      "modelo": "110-MASTER",
      "tipo": "VAN",
      "acessivel": true,
      "operadora": "Transporte Saúde Litoral (demo)",
      "status": "ONLINE",
      "online": true,
      "ultima_atualizacao": "2026-10-29T20:15:00Z",
      "idade_segundos": 42,
      "posicao": {
        "latitude": -23.9351,
        "longitude": -46.3921,
        "velocidade_kmh": 44.0,
        "rumo": 310.0,
        "precisao_m": 12.0,
        "posicao_aproximada": false,
        "capturada_em": "2026-10-29T20:15:00Z",
        "distancia_ate_voce_km": null
      },
      "viagem_ativa": {
        "id": 1,
        "status": "EM_ANDAMENTO",
        "destino": "Hospital Estadual de Referência — Diadema (demo)",
        "trajeto": "IDA_E_VOLTA",
        "partida_prevista": "2026-10-29T06:00:00Z"
      }
    }
  ]
}
```

### 3.2 `GET /api/v1/publico/veiculos/{placa}`

Detalhe do veículo. Aceita `lat` e `lon` **em conjunto** para calcular
`distancia_ate_voce_km`.

| Parâmetro | Tipo | Regra |
| --- | --- | --- |
| `placa` | path | Mercosul/antiga; normalizada |
| `lat` | query | −90…90; exige `lon` |
| `lon` | query | −180…180; exige `lat` |

- `404` genérico para placa inválida **ou** inexistente (evita enumeração).
- `422` se apenas um dos dois parâmetros for enviado.
- Se não houver telemetria, `posicao` é `null` e `status` é `OFFLINE`.

### 3.3 `GET /api/v1/publico/veiculos/{placa}/trilha`

| Parâmetro | Padrão | Faixa |
| --- | --- | --- |
| `limite` | 60 | 2–200 |

Retorna pontos das últimas **12 horas**, em ordem cronológica crescente,
coordenadas arredondadas.

```json
{
  "placa": "SVS1A23",
  "pontos": [
    {"latitude": -23.9351, "longitude": -46.3921, "capturada_em": "2026-10-29T20:12:00Z"}
  ]
}
```

### 3.4 `GET /api/v1/publico/veiculos/{placa}/viagens`

Resumo agregado por data (padrão: hoje). Não contém nomes, CPF ou IDs de
pacientes.

```json
{
  "placa": "SVS1A23",
  "data": "2026-10-29",
  "total_autorizacoes": 2,
  "viagens": [
    {
      "id": 1,
      "status": "EM_ANDAMENTO",
      "trajeto": "IDA_E_VOLTA",
      "destino": "Hospital Estadual de Referência — Diadema (demo)",
      "partida_prevista": "2026-10-29T06:00:00Z",
      "autorizacoes": 2
    }
  ]
}
```

> Risco residual A-04: a contagem agregada pode permitir inferência de fluxo.
> Ver [`07-seguranca-lgpd.md`](07-seguranca-lgpd.md).

## 4. Passageiro

### 4.1 `POST /api/v1/passageiro/consulta`

Autentica por **CPF + data de nascimento** e retorna a viagem do dia e o
histórico.

```json
{
  "cpf": "900.000.101-38",
  "data_nascimento": "1990-05-12",
  "data": "2026-10-29"
}
```

```json
{
  "paciente": {
    "nome": "Paciente Demonstração Alfa",
    "cpf_mascarado": "***.***.***-38",
    "municipio": "Santos"
  },
  "data_consulta": "2026-10-29",
  "possui_agendamento": true,
  "viagem_hoje": {
    "viagem_id": 1,
    "autorizacao_id": 1,
    "numero_autorizacao": "AUT-20261029-001",
    "status": "EM_ANDAMENTO",
    "trajeto": "IDA_E_VOLTA",
    "destino": "Hospital Estadual de Referência — Diadema (demo)",
    "partida_prevista": "2026-10-29T06:00:00Z",
    "retorno_previsto": "2026-10-29T18:00:00Z",
    "veiculo": {
      "placa": "SVS1A23",
      "modelo": "110-MASTER",
      "acessivel": true,
      "operadora": "Transporte Saúde Litoral (demo)"
    },
    "motorista": "Carlos A.",
    "acompanhamento_em_tempo_real": true,
    "embarcado": true
  },
  "historico": [
    {
      "viagem_id": 3,
      "data": "2026-10-28",
      "status": "CONCLUIDA",
      "status_autorizacao": "APROVADA",
      "destino": "Hospital Estadual de Referência — Diadema (demo)",
      "trajeto": "IDA_E_VOLTA",
      "placa": "SVS1A23",
      "acompanhamento_em_tempo_real": false
    }
  ]
}
```

Erros:

| Situação | HTTP | Corpo |
| --- | --- | --- |
| CPF matematicamente inválido | 422 | `{"detail": [...]}` (validação) |
| CPF inexistente/inativo/nascimento divergente | 404 | `{"detail": "Dados não conferem com nenhum cadastro ativo. Verifique CPF e data de nascimento."}` |
| Muitas tentativas | 429 | `{"detail": "Muitas requisições. Aguarde e tente novamente."}` |

A resposta nunca contém o CPF em claro; o histórico é limitado a 180 dias e 30
registros.

## 5. Motorista

### 5.1 `POST /api/v1/motorista/sessao`

```json
{"placa": "SVS1A23", "pin": "1234"}
```

```json
{
  "token": "v1.eyJzdWIiOjEsInZlaSI6MSwiZXhwIjoxNzYxODQ0MDAwfQ.…",
  "expira_em": "2026-10-30T04:15:00Z",
  "motorista": {"id": 1, "nome": "Carlos Andrade (demo)", "cpf_mascarado": "***.***.***-75"},
  "veiculo": {
    "placa": "SVS1A23",
    "modelo": "110-MASTER",
    "acessivel": true,
    "operadora": "Transporte Saúde Litoral (demo)"
  }
}
```

- PIN errado, placa inexistente ou inativa → `401 {"detail": "Placa ou PIN inválidos"}`.
- O token é assinado com `SVS_DRIVER_SECRET` e contém `sub` (motorista), `vei`
  (veículo) e `exp`.
- A sessão é **stateless**: não há revogação antes de expirar no protótipo.

### 5.2 `GET /api/v1/motorista/viagens`

Cabeçalho `Authorization: Bearer <token>`. Parâmetro opcional `data`
(padrão: hoje). Retorna apenas viagens do veículo da sessão.

### 5.3 `GET /api/v1/motorista/viagens/{viagem_id}/passageiros`

Retorna passageiros com autorização **APROVADA**, nome, CPF mascarado, unidade
e embarque (se houver). Viagem de outro veículo → `404`.

### 5.4 `POST /api/v1/motorista/viagens/{viagem_id}/embarques`

```json
{"autorizacao_id": 1, "metodo": "QRCODE"}
```

- `metodo`: `QRCODE`, `CPF` ou `MANUAL`.
- **Idempotente:** repetir a chamada devolve o embarque existente, sem duplicar.
- Autorização de outra viagem → `404`; não aprovada → `409`.

### 5.5 `POST /api/v1/motorista/viagens/{viagem_id}/eventos`

```json
{"tipo": "INICIO", "observacao": "Saída do ponto"}
```

- `tipo`: `INICIO`, `CHEGADA_DESTINO`, `FIM`, `ATRASO`, `INCIDENTE`,
  `OBSERVACAO`.
- `INICIO` muda a viagem para `EM_ANDAMENTO` e grava `iniciada_em`.
- `FIM` muda para `CONCLUIDA` e grava `concluida_em`.

### 5.6 `POST /api/v1/motorista/posicao`

Envia posição do app. O campo `placa` é ignorado; o veículo vem da sessão e a
fonte é forçada para `APP_MOTORISTA`.

```json
{
  "placa": "SVS1A23",
  "latitude": -23.95,
  "longitude": -46.34,
  "velocidade_kmh": 33.5,
  "precisao_m": 8
}
```

## 6. Telemetria

### 6.1 `POST /api/v1/telemetria`

Cabeçalho `X-Ingest-Key`. Usado por gateway/operadora/simulador.

```json
{
  "placa": "SVS1A23",
  "latitude": -23.95,
  "longitude": -46.34,
  "velocidade_kmh": 42.0,
  "rumo": 310.0,
  "precisao_m": 12.0,
  "capturada_em": "2026-10-29T20:15:00Z",
  "viagem_id": 1,
  "fonte": "GATEWAY"
}
```

| Validação | Falha |
| --- | --- |
| Chave | 401 |
| Placa existente/ativa | 404 |
| Lat/lon/velocidade/rumo/precisão | 422 |
| `capturada_em` > agora + 5 min ou < agora − 24 h | 422 |
| `viagem_id` de outro veículo | 422 |

Resposta:

```json
{"id": 128, "recebida_em": "2026-10-29T20:15:01Z", "status": "ONLINE"}
```

## 7. Administração

Todas as rotas exigem `X-Admin-Key`.

### 7.1 `GET /api/v1/admin/kpis`

| Parâmetro | Padrão |
| --- | --- |
| `data` | hoje |

```json
{
  "data": "2026-10-29",
  "veiculos_total": 4,
  "veiculos_online": 2,
  "viagens_total": 2,
  "viagens_em_andamento": 1,
  "autorizacoes_aprovadas": 3,
  "autorizacoes_pendentes": 1,
  "passageiros_embarcados": 1,
  "otif_percentual": 0.0,
  "atraso_medio_min": 5.0
}
```

Definições:

- **OTIF**: percentual de viagens concluídas cujo início ocorreu até 15 min
  após a partida prevista.
- **Atraso médio**: média, em minutos, entre `iniciada_em` e
  `partida_prevista`, considerando viagens já iniciadas (nunca negativo).

### 7.2 `GET /api/v1/admin/viagens`

Lista viagens da data com placa, motorista, status, atraso e contagens.

### 7.3 `GET /api/v1/admin/autorizacoes`

| Parâmetro | Valores | Padrão |
| --- | --- | --- |
| `data` | `YYYY-MM-DD` | hoje |
| `status` | `PENDENTE`, `APROVADA`, `NEGADA`, `CANCELADA` | todos |

Status inválido → `422`. A listagem é auditada (`listar_autorizacoes`).

### 7.4 `POST /api/v1/admin/autorizacoes/{id}/validar`

```json
{"status": "APROVADA", "validador": "Regulação Municipal"}
```

- `status`: `APROVADA` ou `NEGADA`.
- Grava `validada_em` e `validada_por`.
- Se a viagem estiver `PLANEJADA` e a autorização for aprovada, a viagem passa
  para `AUTORIZADA`.
- Cancelada → `409`; inexistente → `404`.

### 7.5 `GET /api/v1/admin/posicoes.csv`

| Parâmetro | Padrão |
| --- | --- |
| `inicio` | 7 dias antes de `fim` |
| `fim` | hoje |

- Limite de 50.000 linhas.
- `inicio > fim` → `422`.
- `Content-Type: text/csv; charset=utf-8` e `Content-Disposition` com nome
  `posicoes_{inicio}_{fim}.csv`.
- Colunas: `placa, viagem_id, latitude, longitude, velocidade_kmh, precisao_m,
  fonte, capturada_em, recebida_em`.
- Exportação auditada (`exportar_telemetria`).

## 8. Infra e estáticos

| Rota | Descrição |
| --- | --- |
| `GET /healthz` | `{"status":"ok","versao":"0.1.0","ambiente":"dev"}` |
| `GET /docs` | Swagger UI |
| `GET /redoc` | ReDoc |
| `GET /openapi.json` | Contrato em tempo de execução |
| `GET /` | PWA (rastreio público) |
| `GET /paciente.html` | Consulta do passageiro |
| `GET /motorista.html` | Operação do motorista |
| `GET /admin.html` | Painel administrativo |
| `GET /sobre.html` | Transparência, limites e privacidade |
| `GET /manifest.webmanifest` | Manifesto PWA |
| `GET /sw.js` | Service worker |
| `GET /icons/*` | Ícones SVG/PNG/maskable |

## 9. Códigos de status usados

| Código | Uso |
| --- | --- |
| 200 | Sucesso |
| 401 | Chave/token ausente ou inválido |
| 404 | Recurso inexistente ou credenciais que não conferem |
| 409 | Conflito de estado (autorização não aprovada/cancelada) |
| 422 | Validação de entrada, janela temporal ou vínculo inválido |
| 429 | Rate limit |
| 500 | Erro não tratado |

## 10. Exemplos rápidos

```bash
# público
curl -s localhost:8000/api/v1/publico/veiculos/SVS1A23 | jq

# passageiro
curl -s -X POST localhost:8000/api/v1/passageiro/consulta \
  -H 'Content-Type: application/json' \
  -d '{"cpf":"90000010138","data_nascimento":"1990-05-12"}' | jq

# sessão do motorista
TOKEN=$(curl -s -X POST localhost:8000/api/v1/motorista/sessao \
  -H 'Content-Type: application/json' \
  -d '{"placa":"SVS1A23","pin":"1234"}' | jq -r .token)
curl -s localhost:8000/api/v1/motorista/viagens \
  -H "Authorization: Bearer $TOKEN" | jq

# telemetria
curl -s -X POST localhost:8000/api/v1/telemetria \
  -H 'Content-Type: application/json' -H 'X-Ingest-Key: dev-ingest-key' \
  -d '{"placa":"SVS1A23","latitude":-23.95,"longitude":-46.34}' | jq

# administração
curl -s localhost:8000/api/v1/admin/kpis -H 'X-Admin-Key: dev-admin-key' | jq
```

## 11. Regeneração do contrato

```bash
python3 scripts/exportar_openapi.py
```

O script exporta `openapi/openapi.yaml` e `openapi/openapi.json` a partir da
aplicação. Alterações de contrato devem ser refletidas em
[`03-requisitos.md`](03-requisitos.md) e testadas em `tests/`.
