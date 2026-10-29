# SVS Rastreio — protótipo de referência (clean-room)

Reimplementação acadêmica, **independente e clean-room**, de uma plataforma de
rastreio logístico de passageiros do transporte público de saúde. O ponto de
partida é a observação de caixa-preta de um sistema em uso (capturas de tela),
sem acesso a código-fonte, banco de dados, contratos ou infraestrutura.

O repositório entrega quatro artefatos complementares:

| Artefato | Onde está |
| --- | --- |
| Dossiê de engenharia reversa | [`docs/02-dossie-engenharia-reversa.md`](docs/02-dossie-engenharia-reversa.md) |
| Relatório técnico (ABNT) | [`docs/10-relatorio-tecnico.md`](docs/10-relatorio-tecnico.md) |
| Contrato OpenAPI + schema SQL | [`openapi/`](openapi/) e [`db/`](db/) |
| Protótipo executável (API + PWA) | [`backend/`](backend/) |

> **Aviso.** Projeto sem vínculo com o sistema observado, com seus fornecedores
> ou com qualquer órgão público. Todos os dados são sintéticos. Nenhum ativo,
> código ou base de dados original foi copiado. Leia [`NOTICE.md`](NOTICE.md).

## O que o protótipo faz

- **Cidadão (público)** — consulta veículos por placa, vê posição aproximada no
  mapa, status online/offline, trilha das últimas 12 h e resumo de viagens do
  dia, sem qualquer dado pessoal.
- **Passageiro** — consulta a própria viagem com **CPF + data de nascimento**,
  vê veículo, destino, horários, se já embarcou e o histórico de 180 dias.
- **Motorista** — autentica com placa + PIN, consulta a escala do dia, a lista
  de passageiros autorizados, registra embarque (idempotente), eventos da
  viagem e envia posição GPS.
- **Administração** — KPIs operacionais (OTIF, atraso médio, embarques),
  viagens do dia, autorizações municipais (listagem e validação) e exportação
  de telemetria em CSV.

## Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic v2.
- **Banco:** SQLite em desenvolvimento; PostgreSQL 16+ (PostGIS opcional) em
  produção — DDL em [`db/schema.sql`](db/schema.sql).
- **Frontend:** PWA sem etapa de build (HTML, CSS e JavaScript puros), Leaflet
  via CDN com fallback textual, service worker para casca offline.
- **Testes:** pytest + httpx/TestClient (79 testes).
- **Qualidade:** Ruff, CI no GitHub Actions.

## Início rápido

Pré-requisitos: Python 3.11+ e `make` (opcional).

```bash
git clone <url-do-repositorio> && cd Sistema-Rastreio-Passageiros
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

# sobe a API + PWA com dados sintéticos em http://localhost:8000
make run
```

Sem `make`:

```bash
cd backend
SVS_AUTO_SEED=1 uvicorn app.main:app --reload
```

Abra <http://localhost:8000>. A documentação interativa da API fica em
<http://localhost:8000/docs> e o contrato versionado em
[`openapi/openapi.yaml`](openapi/openapi.yaml).

Para simular o deslocamento de um veículo em outro terminal:

```bash
make sim                 # veículo SVS1A23
make sim PLACA=SVS2B34   # outro veículo
```

### Credenciais de demonstração

| Perfil | Credencial |
| --- | --- |
| Passageiro Alfa | CPF `90000010138`, nascimento `1990-05-12` |
| Passageiro Beta | CPF `90000010219`, nascimento `1985-11-03` |
| Passageiro Gama | CPF `90000010308`, nascimento `1978-02-20` |
| Motorista SVS1A23 | PIN `1234` |
| Motorista SVS2B34 | PIN `4321` |
| Motorista DEM0C56 | PIN `5678` |
| Motorista TST9D87 | PIN `8765` |
| Painel administrativo | chave `dev-admin-key` |
| Ingestão de telemetria | chave `dev-ingest-key` |

Os CPFs são gerados a partir da base reservada `900000xxx`, com dígitos
verificadores válidos, e não correspondem a pessoas reais. As credenciais
acima existem **apenas** no modo `dev`; em `prod` a aplicação se recusa a
iniciar com os segredos padrão.

## Estrutura do repositório

```text
backend/
  app/            API FastAPI (routers, serviços, modelos, seed, simulador)
  static/         PWA (index, paciente, motorista, admin, sobre)
db/
  schema.sql      DDL PostgreSQL gerado a partir dos modelos
  seed.sql        snapshot do cenário sintético
docs/             dossiê, requisitos, arquitetura, LGPD, relatório e ADRs
openapi/          contrato OpenAPI 3.1 (YAML e JSON)
reverse-engineering/
  evidencias/     capturas anonimizadas E01–E07 + manifesto com SHA-256
scripts/          anonimização, exportação de artefatos, seed e simulador
analytics/        trilha CRISP-DM e indicadores operacionais
infra/            Dockerfile e docker-compose (API + PostgreSQL)
tests/            contrato, segurança e LGPD (79 testes)
```

## Segurança e LGPD em uma página

- CPF nunca é armazenado em texto claro: `HMAC-SHA256(CPF, pepper)` +
  `cpf_mascarado` (`***.***.***-NN`). PIN do motorista também é pseudonimizado.
- A consulta do passageiro exige **dois fatores** (CPF + data de nascimento) e
  devolve mensagem genérica em caso de falha, evitando enumeração.
- A posição pública é arredondada para 4 casas decimais (~11 m) e a trilha é
  limitada às últimas 12 h; nenhum nome, CPF ou telefone é exposto.
- Telemetria é **append-only**; acessos sensíveis e exportações geram registro
  em `audit_log`, com IP pseudonimizado.
- Limitação de taxa por IP, chaves de serviço distintas (`X-Ingest-Key`,
  `X-Admin-Key`), sessão de motorista assinada (HMAC, 8 h, sem estado).
- Em produção: `SVS_ENV=prod` obriga segredos próprios e desativa
  `AUTO_CREATE`; ver [`docs/07-seguranca-lgpd.md`](docs/07-seguranca-lgpd.md).

## Testes e artefatos

```bash
make test                     # 79 testes
make lint                     # Ruff
python3 scripts/exportar_openapi.py
python3 scripts/gerar_schema_sql.py
python3 scripts/exportar_seed_sql.py
python3 scripts/redact_evidencias.py   # requer Pillow e os originais fora do repo
```

O CI em [`.github/workflows/ci.yml`](.github/workflows/ci.yml) executa lint e
testes em Python 3.11 e 3.12.

## Documentação

| Documento | Conteúdo |
| --- | --- |
| [`docs/00-visao-geral.md`](docs/00-visao-geral.md) | Problema, escopo, personas e entregas |
| [`docs/01-metodologia.md`](docs/01-metodologia.md) | Engenharia reversa de caixa-preta + CRISP-DM |
| [`docs/02-dossie-engenharia-reversa.md`](docs/02-dossie-engenharia-reversa.md) | Evidências, inventário funcional e achados |
| [`docs/03-requisitos.md`](docs/03-requisitos.md) | Requisitos funcionais, não funcionais e rastreabilidade |
| [`docs/04-arquitetura.md`](docs/04-arquitetura.md) | Visão de componentes, implantação e decisões |
| [`docs/05-modelo-de-dados.md`](docs/05-modelo-de-dados.md) | DER, tabelas, invariantes e retenção |
| [`docs/06-api.md`](docs/06-api.md) | Catálogo de endpoints, autenticação e erros |
| [`docs/07-seguranca-lgpd.md`](docs/07-seguranca-lgpd.md) | Modelo de ameaças, controles e ROPA |
| [`docs/08-plano-de-testes.md`](docs/08-plano-de-testes.md) | Estratégia, matriz e evidências de execução |
| [`docs/09-roadmap-incremental.md`](docs/09-roadmap-incremental.md) | Incrementos I1–I8 e critérios de aceite |
| [`docs/10-relatorio-tecnico.md`](docs/10-relatorio-tecnico.md) | Relatório técnico v2 em estrutura ABNT |
| [`docs/11-etica-e-conformidade.md`](docs/11-etica-e-conformidade.md) | Ética em pesquisa e conformidade |
| [`docs/adr/`](docs/adr/) | Registros de decisão de arquitetura |

## Licença e uso

Uso acadêmico e educacional, sem garantia. O texto integral das condições,
incluindo a declaração de clean-room e a proibição de uso com dados reais, está
em [`NOTICE.md`](NOTICE.md). Contribuições seguem [`CONTRIBUTING.md`](CONTRIBUTING.md);
falhas de segurança devem ser reportadas conforme [`SECURITY.md`](SECURITY.md).
