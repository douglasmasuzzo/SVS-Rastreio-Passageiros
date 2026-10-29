# 03 — Requisitos

## 1. Convenções

- **RF**: requisito funcional; **RNF**: requisito não funcional.
- **Prioridade**: M (must), S (should), C (could), W (won't neste ciclo).
- **Rastreabilidade**: rota/arquivo que implementa e teste que verifica.
- Requisitos derivados das evidências E01–E05 (ver
  [`02-dossie-engenharia-reversa.md`](02-dossie-engenharia-reversa.md)).
- O comportamento é sempre validado no servidor; a PWA é uma cliente.

## 2. Atores

| Ator | Descrição | Autenticação |
| --- | --- | --- |
| Cidadão | Qualquer pessoa | Nenhuma (dados públicos) |
| Paciente | Titular de autorização | CPF + data de nascimento |
| Motorista | Condutor do veículo | Placa + PIN → token HMAC |
| Gestor/regulação | Administração municipal | `X-Admin-Key` |
| Gateway/operadora | Fonte de telemetria | `X-Ingest-Key` |

## 3. Requisitos funcionais

### 3.1 Rastreamento público

| ID | Requisito | Prior. | Implementação | Verificação |
| --- | --- | --- | --- | --- |
| RF-01 | Listar veículos ativos, com filtro por trecho da placa e status online/offline | M | `GET /api/v1/publico/veiculos` | `tests/test_publico.py` |
| RF-02 | Exibir detalhe do veículo: placa, modelo, tipo, acessibilidade, operadora, status, última atualização, posição aproximada e viagem ativa | M | `GET /api/v1/publico/veiculos/{placa}` | `tests/test_publico.py` |
| RF-03 | Calcular distância até o usuário quando `lat`/`lon` forem informados em conjunto | S | `services/tracking.posicao_publica` | `tests/test_publico.py` |
| RF-04 | Retornar trilha dos últimos 12 h, limitada a 200 pontos, do mais antigo ao mais recente | M | `GET /api/v1/publico/veiculos/{placa}/trilha` | `tests/test_publico.py` |
| RF-05 | Retornar resumo agregado das viagens do dia por placa, sem dados pessoais | S | `GET /api/v1/publico/veiculos/{placa}/viagens` | `tests/test_publico.py` |
| RF-06 | Normalizar placas nos padrões Mercosul e antigo; rejeitar formatos inválidos | M | `security.normalizar_placa` | `tests/test_seguranca.py` |
| RF-07 | Não revelar se a placa é inválida ou inexistente (mensagem única) | M | `publico._veiculo_ou_404` | `tests/test_publico.py` |

### 3.2 Passageiro

| ID | Requisito | Prior. | Implementação | Verificação |
| --- | --- | --- | --- | --- |
| RF-08 | Consultar viagem mediante CPF válido + data de nascimento | M | `POST /api/v1/passageiro/consulta` | `tests/test_passageiro.py` |
| RF-09 | Retornar erro genérico (404) para CPF inexistente, inativo ou nascimento divergente | M | `routers/passageiro.py` | `tests/test_passageiro.py` |
| RF-10 | Exibir viagem do dia com veículo, destino, horários, motorista abreviado, embarque e acompanhamento | M | `services/passageiro.consultar` | `tests/test_passageiro.py` |
| RF-11 | Exibir histórico dos últimos 180 dias, limitado a 30 registros | S | `services/passageiro.consultar` | `tests/test_passageiro.py` |
| RF-12 | Informar explicitamente quando não há agendamento aprovado no dia | M | `possui_agendamento` | `tests/test_passageiro.py` |
| RF-13 | Mascarar CPF e telefone em todas as respostas | M | `security.mascarar_cpf` | `tests/test_seguranca.py`, `tests/test_passageiro.py` |
| RF-14 | Registrar auditoria de consultas bem-sucedidas e falhas, sem CPF no detalhe | M | `services/audit` | `tests/test_passageiro.py` |
| RF-15 | Aplicar rate limit específico à consulta | M | `deps.limitar_consulta` | `tests/test_seguranca.py` |

### 3.3 Motorista

| ID | Requisito | Prior. | Implementação | Verificação |
| --- | --- | --- | --- | --- |
| RF-16 | Autenticar por placa + PIN e emitir token com validade de 8 h | M | `POST /api/v1/motorista/sessao` | `tests/test_motorista.py` |
| RF-17 | Vincular a sessão ao motorista e ao veículo; rejeitar veículo/motorista inativo | M | `deps.motorista_autenticado`, `motorista._sessao` | `tests/test_motorista.py` |
| RF-18 | Listar viagens do veículo na data (padrão: hoje) | M | `GET /api/v1/motorista/viagens` | `tests/test_motorista.py` |
| RF-19 | Listar passageiros com autorização aprovada, CPF mascarado e status de embarque | M | `GET /api/v1/motorista/viagens/{id}/passageiros` | `tests/test_motorista.py` |
| RF-20 | Registrar embarque de forma idempotente, apenas para autorização aprovada da viagem | M | `POST .../embarques` | `tests/test_motorista.py` |
| RF-21 | Registrar evento operacional e atualizar status da viagem em INICIO/FIM | M | `POST .../eventos` | `tests/test_motorista.py` |
| RF-22 | Enviar posição GPS do app com fonte `APP_MOTORISTA` | S | `POST /api/v1/motorista/posicao` | `tests/test_motorista.py` |
| RF-23 | Impedir acesso a viagem de outro veículo | M | `motorista._viagem_da_sessao` | `tests/test_motorista.py` |

### 3.4 Telemetria

| ID | Requisito | Prior. | Implementação | Verificação |
| --- | --- | --- | --- | --- |
| RF-24 | Receber ponto de GPS autenticado por chave de ingestão | M | `POST /api/v1/telemetria` | `tests/test_publico.py` |
| RF-25 | Validar faixa de latitude/longitude, velocidade, rumo e precisão | M | `schemas.TelemetriaIn` | `tests/test_publico.py` |
| RF-26 | Rejeitar captura fora da janela (5 min no futuro, 24 h no passado) | M | `routers/telemetria.py` | `tests/test_publico.py` |
| RF-27 | Garantir que `viagem_id` pertence ao veículo informado | M | `routers/telemetria.py` | `tests/test_publico.py` |
| RF-28 | Persistir telemetria como append-only, com `capturada_em` e `recebida_em` | M | `models.Posicao` | `tests/test_publico.py` |

### 3.5 Administração

| ID | Requisito | Prior. | Implementação | Verificação |
| --- | --- | --- | --- | --- |
| RF-29 | Calcular KPIs do dia: veículos, viagens, autorizações, embarques, OTIF e atraso médio | M | `GET /api/v1/admin/kpis` | `tests/test_admin.py` |
| RF-30 | Listar viagens da data com placa, motorista, status, atraso e contagens | M | `GET /api/v1/admin/viagens` | `tests/test_admin.py` |
| RF-31 | Listar autorizações por data e status, com CPF mascarado | S | `GET /api/v1/admin/autorizacoes` | `tests/test_admin.py` |
| RF-32 | Aprovar ou negar autorização, registrando validador e data | M | `POST /api/v1/admin/autorizacoes/{id}/validar` | `tests/test_admin.py` |
| RF-33 | Promover viagem `PLANEJADA` para `AUTORIZADA` ao aprovar a primeira autorização | S | `routers/admin.py` | `tests/test_admin.py` |
| RF-34 | Exportar telemetria em CSV por intervalo, com limite de 50 mil linhas | S | `GET /api/v1/admin/posicoes.csv` | `tests/test_admin.py` |
| RF-35 | Auditar listagens, validações e exportações | M | `services/audit` | `tests/test_admin.py` |

### 3.6 Interface e operação

| ID | Requisito | Prior. | Implementação | Verificação |
| --- | --- | --- | --- | --- |
| RF-36 | PWA instalável com manifesto, ícones, tema e service worker | S | `static/manifest.webmanifest`, `static/sw.js` | fumaça manual |
| RF-37 | Funcionar em celular, com navegação por teclado e rótulos acessíveis | S | `static/css/app.css`, HTML semântico | revisão manual |
| RF-38 | Exibir fallback textual quando o mapa/Leaflet não carregar | S | `static/js/comum.js` | revisão manual |
| RF-39 | Página “Sobre” com finalidade, limites e aviso de dados sintéticos | S | `static/sobre.html` | revisão manual |
| RF-40 | Health check e documentação OpenAPI publicada | S | `/healthz`, `/docs` | CI |
| RF-41 | Seed sintético determinístico e credenciais de demonstração | M | `app/seed.py`, `scripts/seed_demo.py` | `tests/conftest.py` |

## 4. Requisitos não funcionais

### 4.1 Segurança

| ID | Requisito | Verificação |
| --- | --- | --- |
| RNF-01 | CPF e PIN nunca em texto claro; usar HMAC-SHA256 com pepper | inspeção do schema + testes |
| RNF-02 | Comparações de segredos com tempo constante (`hmac.compare_digest`) | revisão + testes |
| RNF-03 | Token de sessão assinado, com expiração e detecção de adulteração | `tests/test_seguranca.py` |
| RNF-04 | Erros de autenticação/consulta não distinguem causa | `tests/test_passageiro.py`, `test_motorista.py` |
| RNF-05 | Rate limit por IP nas rotas públicas, de consulta e de sessão | `tests/test_seguranca.py` |
| RNF-06 | Em produção, recusar segredos padrão e `AUTO_CREATE` | `config.Settings.validar` |
| RNF-07 | CORS desabilitado por padrão; habilitar por lista explícita | `config` |
| RNF-08 | Telemetria validada contra injeção de viagem e horário | `tests/test_publico.py` |

### 4.2 Privacidade e LGPD

| ID | Requisito | Verificação |
| --- | --- | --- |
| RNF-09 | Minimização: nenhum dado pessoal em endpoints públicos | `tests/test_publico.py` |
| RNF-10 | Posição pública arredondada (4 casas, ~11 m) e trilha ≤ 12 h | `tests/test_publico.py` |
| RNF-11 | CPF mascarado em toda resposta que o exibe | `tests/test_passageiro.py`, `test_motorista.py`, `test_admin.py` |
| RNF-12 | Auditoria de acesso sensível com IP pseudonimizado | `tests/test_passageiro.py`, `test_admin.py` |
| RNF-13 | Consulta limitada a 180 dias e 30 registros | `tests/test_passageiro.py` |
| RNF-14 | Finalidade e aviso de privacidade visíveis na PWA | revisão manual |
| RNF-15 | Dados 100% sintéticos, CPFs na faixa reservada `900000xxx` | `app/seed.py` |

### 4.3 Desempenho e escalabilidade

| ID | Requisito | Verificação |
| --- | --- | --- |
| RNF-16 | Resposta típica < 500 ms em ambiente local para consultas simples | fumaça |
| RNF-17 | Exportação limitada a 50 mil linhas para evitar exaustão | código |
| RNF-18 | Índices em placa, data, status, `cpf_hash` e telemetria | `db/schema.sql` |
| RNF-19 | Suportar SQLite (dev) e PostgreSQL 16+ (prod) | `db/schema.sql` |
| RNF-20 | Limite de pontos da trilha (200) e de histórico (30) | código |

### 4.4 Confiabilidade e operação

| ID | Requisito | Verificação |
| --- | --- | --- |
| RNF-21 | Embarque idempotente (repetição não duplica) | `tests/test_motorista.py` |
| RNF-22 | Health check independente do banco | `/healthz` |
| RNF-23 | Configuração por variáveis de ambiente (12-factor) | `config.py`, `.env.example` |
| RNF-24 | Logs e auditoria sem CPF, nome de paciente ou coordenada bruta | revisão |
| RNF-25 | Migrações e backup documentados para produção | `docs/04`, `SECURITY.md` |

### 4.5 Usabilidade, acessibilidade e manutenibilidade

| ID | Requisito | Verificação |
| --- | --- | --- |
| RNF-26 | Interface em pt-BR, mobile-first, contraste e foco visível | revisão manual |
| RNF-27 | Nenhum build de frontend; servir estáticos diretamente | estrutura |
| RNF-28 | Lint Ruff e testes no CI (Python 3.11/3.12) | `.github/workflows/ci.yml` |
| RNF-29 | OpenAPI e schema regeneráveis por script | `scripts/` |
| RNF-30 | Documentação rastreável e em Markdown versionado | `docs/` |

## 5. Casos de uso principais

### UC-01 — Consultar veículo no mapa

- **Ator:** cidadão.
- **Pré-condição:** veículo ativo cadastrado.
- **Fluxo:** informa placa → API normaliza → busca veículo → última posição →
  calcula status → arredonda coordenadas → retorna.
- **Pós-condição:** nenhum dado pessoal exposto; se não houver posição, retorna
  veículo com `posicao: null` e status `OFFLINE`.
- **Exceções:** placa inválida/inexistente → 404 genérico; `lat` sem `lon` → 422.

### UC-02 — Consultar a própria viagem

- **Ator:** paciente.
- **Pré-condição:** paciente ativo com CPF pseudonimizado.
- **Fluxo:** informa CPF + nascimento → API valida formato → calcula HMAC →
  compara hash e nascimento → busca autorizações → monta viagem/histórico →
  audita → responde.
- **Pós-condição:** somente dados do titular; CPF mascarado.
- **Exceções:** qualquer divergência → 404 genérico + auditoria de falha.

### UC-03 — Registrar embarque

- **Ator:** motorista autenticado.
- **Pré-condição:** viagem do veículo da sessão; autorização aprovada.
- **Fluxo:** seleciona passageiro → API valida vínculo → cria embarque se não
  existir → audita → responde.
- **Pós-condição:** no máximo um embarque por autorização.
- **Exceções:** autorização de outra viagem → 404; não aprovada → 409.

### UC-04 — Validar autorização municipal

- **Ator:** gestor.
- **Pré-condição:** autorização existente e não cancelada.
- **Fluxo:** escolhe status (APROVADA/NEGADA) e validador → API atualiza,
  promove viagem planejada para autorizada se aplicável → audita.
- **Pós-condição:** autorização com `validada_em` e `validada_por`.
- **Exceções:** cancelada → 409; inexistente → 404; status inválido → 422.

### UC-05 — Ingerir telemetria

- **Ator:** gateway/operadora.
- **Pré-condição:** chave válida e veículo existente.
- **Fluxo:** envia ponto → API autentica → valida janela → valida viagem →
  grava append-only → calcula status → responde id e status.
- **Pós-condição:** ponto imutável; veículo pode ficar online.
- **Exceções:** chave inválida → 401; veículo inexistente → 404; janela/viagem
  inválida → 422.

## 6. Matriz de rastreabilidade (resumo)

| Origem | Requisitos | Rotas | Testes |
| --- | --- | --- | --- |
| E01/E02 — lista e mapa | RF-01…RF-07 | `/publico/*` | `test_publico.py` |
| E03/E04 — consulta por CPF | RF-08…RF-15 | `/passageiro/consulta` | `test_passageiro.py` |
| E05 — visão do motorista | RF-16…RF-23 | `/motorista/*` | `test_motorista.py` |
| Operação de campo | RF-24…RF-28 | `/telemetria` | `test_publico.py` |
| Gestão municipal | RF-29…RF-35 | `/admin/*` | `test_admin.py` |
| Produto/PWA | RF-36…RF-41 | `/`, `/sobre`, `/docs` | fumaça + CI |
| Segurança/LGPD | RNF-01…RNF-15 | transversal | `test_seguranca.py` + demais |
| Operação | RNF-16…RNF-30 | transversal | CI + revisão |

## 7. Requisitos descartados neste ciclo

| ID | Requisito | Motivo |
| --- | --- | --- |
| W-01 | OTP por SMS | Depende de provedor e custo; roadmap I2 |
| W-02 | Notificações push | Fora do escopo do MVP |
| W-03 | Integração com regulação/e-SUS | Requer convênio e dados reais |
| W-04 | App nativo | PWA cobre o caso de uso |
| W-05 | Roteirização/otimização | Complexidade e dados insuficientes |
| W-06 | Faturamento | Fora do núcleo de rastreio |
| W-07 | RBAC/MFA no painel | Roadmap I6 |
| W-08 | Migrações Alembic | Roadmap I4 |

## 8. Critérios de aceite do MVP

1. `make run` sobe a API e a PWA com dados sintéticos.
2. Todas as rotas do OpenAPI respondem conforme o contrato.
3. `make test` executa 79 testes verdes.
4. Nenhum CPF em claro no banco, na API ou nos logs.
5. Consulta do passageiro exige dois fatores e falha de forma genérica.
6. Posição pública arredondada e trilha limitada a 12 h.
7. Telemetria autenticada, validada e append-only.
8. Painel permite listar/validar autorizações e exportar CSV com auditoria.
9. Documentação cobre método, evidências, riscos e ética.
10. CI verde em Python 3.11 e 3.12.
