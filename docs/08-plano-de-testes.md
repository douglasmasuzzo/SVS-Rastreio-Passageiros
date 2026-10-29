# 08 — Plano e evidências de testes

## 1. Objetivo

Verificar que o protótipo:

1. cumpre os contratos descritos em [`06-api.md`](06-api.md);
2. aplica os controles de segurança e privacidade de [`07-seguranca-lgpd.md`](07-seguranca-lgpd.md);
3. mantém a integridade do domínio (autorizações, embarques, viagens);
4. é reprodutível em ambiente limpo e no CI.

## 2. Estratégia

A pirâmide é intencionalmente achatada: o custo de um teste de contrato com
`TestClient` é baixo e o valor é alto, pois cobre rota + dependência + serviço +
banco em memória.

```text
        ▲  fumaça manual (navegador/servidor real)
       ╱ ╲
      ╱   ╲  contrato + segurança + LGPD (pytest/TestClient)
     ╱─────╲
    ╱       ╲ unitários (normalização, HMAC, token, rate limit, geo)
   ╱─────────╲
```

| Nível | Ferramenta | Escopo |
| --- | --- | --- |
| Unitário | pytest | CPF, placa, máscara, HMAC, token, rate limit, distância |
| Contrato/integração | pytest + `TestClient` | Rotas, status, esquemas, erros, banco em memória |
| Fumaça | `curl`/navegador | PWA, manifest, service worker, ícones, healthz, fluxo real |
| Estático | Ruff | Estilo, imports, bugs comuns |
| CI | GitHub Actions | Python 3.11/3.12, lint, testes, OpenAPI, schema |

## 3. Ambiente de teste

`tests/conftest.py` configura o ambiente **antes** de importar a aplicação:

```python
SVS_ENV=test
SVS_DB_URL=sqlite+pysqlite:///:memory:
SVS_AUTO_CREATE=0
SVS_AUTO_SEED=0
SVS_PUBLIC_RATE_LIMIT=100000
```

Fixtures:

| Fixture | Papel |
| --- | --- |
| `db_session` | Recria as tabelas e aplica o seed canônico a cada teste |
| `client` | `TestClient` com lifespan da aplicação |
| `sessao_motorista` | Sessão autenticada de `SVS1A23` / PIN `1234` |

O banco em memória com `StaticPool` garante isolamento e velocidade. O seed é
recriado por teste, evitando dependência de ordem.

## 4. Suíte atual

**79 testes**, distribuídos em:

| Arquivo | Testes | Foco |
| --- | --- | --- |
| `tests/test_admin.py` | 18 | KPIs, viagens, autorizações, validação, CSV, telemetria, OpenAPI, healthz |
| `tests/test_motorista.py` | 12 | Sessão, escopo por veículo, passageiros, embarque, eventos, GPS |
| `tests/test_passageiro.py` | 10 | Segundo fator, máscara, histórico, erros genéricos, auditoria |
| `tests/test_publico.py` | 13 | Lista, busca, placa, posição, distância, trilha, resumo, minimização |
| `tests/test_seguranca.py` | 26 | Placa, CPF, máscara, HMAC, PIN, token, expiração, rate limit |
| **Total** | **79** | |

### 4.1 Casos cobertos por requisito

| Requisitos | Casos representativos |
| --- | --- |
| RF-01…RF-07 | Lista com 4 veículos e status; busca “svs”; placa em 3 formatos; 404 idêntico; ausência de CPF/motorista/paciente; `lat` sem `lon` → 422; trilha ordenada; resumo agregado |
| RF-08…RF-15 | Consulta Alfa com agendamento e embarque; CPF mascarado; histórico; Gama com pendência; data passada; nascimento errado; CPF inexistente; CPF inválido 422; auditoria de sucesso e falha |
| RF-16…RF-23 | PIN errado; placa inexistente; token/veículo; sem token 401; viagens do dia; passageiros; embarque idempotente; pendente 409; `INICIO` publica viagem ativa; `FIM` conclui; viagem de outro veículo 404; GPS atualiza posição |
| RF-24…RF-28 | Sem chave 401; telemetria atualiza status; placa inexistente 404; horário futuro 422; viagem de outro veículo 422 |
| RF-29…RF-35 | Admin exige chave; KPIs; viagens; autorizações e filtro; status inválido 422; validação; viagem planejada → autorizada; inexistente 404; CSV; intervalo inválido 422 |
| RF-36…RF-41 | Fumaça manual (PWA) e CI (OpenAPI/healthz) |
| RNF-01…RNF-15 | HMAC, máscara, token, rate limit, minimização, erros genéricos, auditoria |
| RNF-16…RNF-30 | Limites, índices, regeneração, lint, CI |

### 4.2 Casos de segurança detalhados

| Cenário | Resultado esperado | Teste |
| --- | --- | --- |
| Token adulterado | `ler_token_motorista` → `None` | `test_token_motorista_rejeita_adulteracao` |
| Token expirado | `None` após validade | `test_token_motorista_rejeita_expirado` |
| PIN errado | 401 genérico | `test_sessao_com_pin_errado` |
| Rota do motorista sem token | 401 | `test_endpoint_sem_token_e_bloqueado` |
| Admin sem chave/chave errada | 401 | `test_admin_exige_chave` |
| Ingestão sem chave/chave errada | 401 | `test_telemetria_exige_chave` |
| CPF inexistente vs. nascimento errado | mesma resposta 404 | `test_cpf_inexistente_retorna_mesma_mensagem` |
| Placa inválida vs. inexistente | mesma resposta 404 | `test_placa_inexistente_retorna_mesma_mensagem` |
| Rate limit | bloqueia após limite e libera outra chave | `test_rate_limiter_bloqueia_apos_limite` |
| CPF em claro | ausente nas respostas públicas e autenticadas | `test_cpf_sempre_mascarado...`, `test_cpf_nao_aparece...` |
| Coordenada precisa | no máximo 4 casas | `test_posicao_publica_nao_expoe_dados_pessoais` |
| Telemetria de outra viagem | 422 | `test_telemetria_com_viagem_de_outro_veiculo_e_rejeitada` |
| Viagem de outro veículo | 404 | `test_motorista_nao_acessa_viagem_de_outro_veiculo` |

## 5. Como executar

```bash
# suíte completa
make test

# equivalente, sem make
PYTHONPATH=backend python3 -m pytest -q

# por arquivo
PYTHONPATH=backend python3 -m pytest -q tests/test_seguranca.py

# com saída detalhada
PYTHONPATH=backend python3 -m pytest -vv

# lint
make lint
```

Saída esperada (resumo):

```text
79 passed
```

No ambiente deste trabalho, as dependências ficam em um diretório externo
(`/tmp/opencode/pylibs-app`), então o comando usado foi:

```bash
PYTHONPATH=/tmp/opencode/pylibs-app python3 -m pytest -q
```

Em uma instalação normal com `venv` e `requirements-dev.txt`, use
`PYTHONPATH=backend`.

## 6. Teste de fumaça (servidor real)

Executado com a API em `localhost:8000` e seed automático.

| # | Verificação | Comando | Resultado |
| --- | --- | --- | --- |
| F1 | Raiz serve a PWA | `curl -sI localhost:8000/` | 200, `text/html` |
| F2 | Página do paciente | `curl -sI localhost:8000/paciente.html` | 200 |
| F3 | Página do motorista | `curl -sI localhost:8000/motorista.html` | 200 |
| F4 | Página do admin | `curl -sI localhost:8000/admin.html` | 200 |
| F5 | Manifesto | `curl -s localhost:8000/manifest.webmanifest` | JSON com ícones 192/512 |
| F6 | Service worker | `curl -sI localhost:8000/sw.js` | 200, `javascript` |
| F7 | Ícone | `curl -sI localhost:8000/icons/icon-192.png` | 200, `image/png` |
| F8 | Healthz | `curl -s localhost:8000/healthz` | `{"status":"ok",...}` |
| F9 | Consulta do paciente | `POST /api/v1/passageiro/consulta` | 200 com viagem do dia |
| F10 | Sessão do motorista | `POST /api/v1/motorista/sessao` | 200 com token |
| F11 | KPIs | `GET /api/v1/admin/kpis` com chave | 200 |
| F12 | Autorizações | `GET /api/v1/admin/autorizacoes` | 200 com 4 itens |
| F13 | Simulador | `make sim` por alguns segundos | posições gravadas, status ONLINE |

Comandos de referência:

```bash
# terminal 1
cd backend && SVS_AUTO_SEED=1 PYTHONPATH=../backend uvicorn app.main:app --port 8000

# terminal 2
curl -s localhost:8000/healthz
curl -s -X POST localhost:8000/api/v1/passageiro/consulta \
  -H 'Content-Type: application/json' \
  -d '{"cpf":"90000010138","data_nascimento":"1990-05-12"}'
curl -s localhost:8000/api/v1/admin/autorizacoes -H 'X-Admin-Key: dev-admin-key'
```

## 7. Integração contínua

Workflow: [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).

| Etapa | Comando |
| --- | --- |
| Lint | `python -m ruff check backend tests scripts analytics` |
| Testes | `python -m pytest -q` |
| OpenAPI | exporta e valida ≥ 18 caminhos |
| Schema | regenera e confere `CREATE TABLE` |

Matriz: Python **3.11** e **3.12**, com `fail-fast: false`. Variáveis de
ambiente de teste são definidas no workflow; nenhum segredo real é usado.

## 8. Lacunas e próximos testes

| Lacuna | Risco | Próximo passo |
| --- | --- | --- |
| Sem E2E de navegador | Regressão visual/JS não detectada | Playwright + axe-core (I8) |
| Sem teste de carga | Gargalo desconhecido | k6/Locust com 100–1000 usuários |
| Sem cobertura medida | Zonas cegas | `pytest-cov` com meta ≥ 85% |
| Sem teste de migração | Falha em upgrade | Alembic + banco efêmero (I4) |
| Sem fuzzing | Entradas adversariais | Hypothesis para CPF/placa/JSON |
| Sem teste de acessibilidade automatizado | Barreiras | axe/Lighthouse no CI |
| Sem teste de PostgreSQL real | Diferença SQLite/Postgres | Testcontainers no CI |
| Sem teste de rate limit distribuído | Comportamento multi-réplica | Redis no CI |
| Sem pentest | Vulnerabilidades desconhecidas | Revisão externa antes de produção |

## 9. Critérios de saída (definition of done)

Um incremento só é considerado pronto quando:

1. `ruff check` passa sem erros;
2. `pytest` passa integralmente;
3. novos requisitos têm teste ou justificativa documentada;
4. OpenAPI e schema são regenerados quando o contrato muda;
5. nenhuma resposta expõe CPF/nome em claro indevidamente;
6. documentação afetada foi atualizada;
7. o changelog registra a mudança visível.
