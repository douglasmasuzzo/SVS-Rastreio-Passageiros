# 00 — Visão geral

## 1. Contexto

Municípios brasileiros executam o **Transporte Social em Saúde** (TSS): levam
pacientes da rede pública a consultas, exames e tratamentos em unidades de
referência, muitas vezes em outro município. A operação envolve regulação,
autorização municipal, escala de veículos e motoristas, embarque e comunicação
com o paciente e seus acompanhantes.

Quando o paciente não sabe onde está o veículo — ou se a autorização foi
validada — crescem ligações para a central, faltas em consultas, espera em
pontos de embarque e custo por viagem. Do lado da gestão, a ausência de dados
confiáveis impede medir pontualidade, ocupação e ociosidade.

Este trabalho parte da observação de um sistema real em uso, por meio de
capturas de tela, e reconstrói seu comportamento em um **protótipo de
referência executável**, com ênfase em privacidade e segurança.

## 2. Problema

> Como reimplementar, de forma independente e auditável, o núcleo funcional de
> um sistema de rastreio logístico de passageiros do transporte público de
> saúde, corrigindo fragilidades de privacidade observáveis e mantendo a
> operação simples para cidadão, motorista e gestor?

O problema se desdobra em três dimensões:

1. **Engenharia reversa** — compreender funcionalidades, entidades e fluxos a
   partir apenas de evidências externas, sem acesso ao código.
2. **Logística e análise** — transformar a operação em indicadores (OTIF,
   atraso, ocupação, embarques) que apoiem decisão.
3. **Privacidade e segurança** — tratar dados de saúde e localização com
   minimização, pseudonimização, finalidade e auditoria (LGPD).

## 3. Objetivos

### 3.1 Objetivo geral

Construir um protótipo executável de rastreio logístico de passageiros do
transporte público de saúde, derivado de engenharia reversa de caixa-preta,
acompanhado de dossiê, relatório técnico, contrato OpenAPI e schema de dados.

### 3.2 Objetivos específicos

1. Registrar e anonimizar as evidências observacionais, com hashes e manifesto.
2. Inventariar telas, funcionalidades, entidades e fluxos do sistema observado.
3. Identificar fragilidades de privacidade/segurança e propor correções.
4. Especificar requisitos funcionais e não funcionais rastreáveis.
5. Implementar API, banco e PWA sem dependência de código original.
6. Instrumentar a operação com indicadores logísticos e trilha de auditoria.
7. Validar o protótipo com suíte automatizada e teste de fumaça ponta a ponta.
8. Documentar decisões, limitações, ética e conformidade.

## 4. Escopo

### 4.1 Dentro do escopo

- Rastreamento **público** por placa, com posição aproximada e status.
- Consulta do **passageiro** por CPF + data de nascimento, com histórico.
- Operação do **motorista**: escala, passageiros autorizados, embarque,
  eventos e envio de posição.
- **Gestão**: KPIs, viagens, autorizações e exportação de telemetria.
- **Ingestão** de telemetria por gateway/app, com autenticação de serviço.
- Modelo de dados, contrato OpenAPI, schema PostgreSQL e snapshot sintético.
- PWA responsiva, instalável e com fallback quando o mapa não carrega.
- Análise CRISP-DM sobre os dados sintéticos gerados pela operação.

### 4.2 Fora do escopo

- Integração real com prontuários, e-SUS, regulação municipal ou faturamento.
- Aplicativo nativo (Android/iOS) e publicação em lojas.
- Hardware embarcado, rastreamento por satélite ou telemetria veicular OBD.
- Autenticação federada (gov.br), assinatura digital ou blockchain.
- Produção com dados reais, SLA, alta disponibilidade e suporte 24×7.
- Reprodução de marca, layout ou código do sistema observado.

## 5. Personas e jornadas

| Persona | Objetivo | Dor observada | Resposta no protótipo |
| --- | --- | --- | --- |
| **Cidadão** (sem cadastro) | Saber se o veículo está a caminho | Não encontra informação confiável; liga para a central | Lista e detalhe por placa, mapa, status, trilha e distância até você |
| **Paciente** | Confirmar sua viagem e horário | Não sabe se foi autorizado nem se já embarcou | Consulta com CPF + nascimento, viagem do dia e histórico |
| **Motorista** | Conferir passageiros e registrar embarque | Lista em papel, seleção manual de placa/data | Sessão por placa + PIN, lista nominal mascarada, embarque idempotente |
| **Gestor/regulação** | Validar autorizações e medir operação | Falta de visão consolidada e de auditoria | Painel com KPIs, viagens, autorizações e exportação |

### 5.1 Jornada do cidadão

1. Acessa a PWA e busca a placa (ou escolhe na lista).
2. Vê status online/offline, última atualização, modelo, acessibilidade e
   operadora.
3. Abre o mapa com posição **aproximada** e, opcionalmente, sua distância até o
   veículo.
4. Consulta a trilha das últimas 12 h e o resumo das viagens do dia.

### 5.2 Jornada do paciente

1. Informa CPF e data de nascimento (segundo fator).
2. Recebe apenas os próprios dados: nome, CPF mascarado, município.
3. Vê a viagem de hoje (se aprovada), veículo, destino, horários, primeiro
   nome do motorista e se o embarque foi registrado.
4. Consulta o histórico dos últimos 180 dias.

### 5.3 Jornada do motorista

1. Autentica com placa e PIN; recebe token de sessão de 8 h.
2. Consulta a escala do dia e os passageiros **aprovados**.
3. Registra embarque por QR code, CPF ou modo manual (idempotente).
4. Registra início, chegada, fim, atraso ou incidente.
5. Envia posições GPS periódicas pelo app.

### 5.4 Jornada do gestor

1. Autentica com a chave administrativa.
2. Acompanha KPIs do dia: veículos online, viagens, autorizações, embarques,
   OTIF e atraso médio.
3. Filtra autorizações por data/status e aprova ou nega.
4. Exporta telemetria em CSV para análise externa.

## 6. Entregas

| # | Entrega | Artefato |
| --- | --- | --- |
| E1 | Dossiê de engenharia reversa | `docs/02-dossie-engenharia-reversa.md` + evidências E01–E07 |
| E2 | Relatório técnico v2 (ABNT) | `docs/10-relatorio-tecnico.md` |
| E3 | Contrato de API | `openapi/openapi.yaml` e `.json` |
| E4 | Schema de dados | `db/schema.sql`, `db/seed.sql` |
| E5 | Protótipo executável | `backend/` (API + PWA) |
| E6 | Análise logística | `analytics/` |
| E7 | Governança | `NOTICE.md`, `SECURITY.md`, `CONTRIBUTING.md`, ADRs |

## 7. Indicadores de sucesso do trabalho

| Indicador | Meta | Verificação |
| --- | --- | --- |
| Cobertura funcional observada | 100% das telas E01–E05 reimplementadas | Dossiê × rotas da PWA |
| Suíte automatizada | ≥ 70 testes verdes | `make test` (79) |
| Rastreabilidade de requisitos | 100% dos RF com teste ou rota | `docs/03` × `tests/` |
| Exposição de CPF em claro | zero no banco, API e logs | schema + testes |
| Precisão da posição pública | ≥ ~11 m de imprecisão | `SVS_POSITION_DECIMALS=4` |
| Artefatos reprodutíveis | OpenAPI e schema regeneráveis | scripts + CI |
| Documentação ética | dossiê + LGPD + riscos residuais | `docs/07`, `docs/11` |

## 8. Como navegar

- Entenda o método em [`01-metodologia.md`](01-metodologia.md).
- Veja as evidências e achados em [`02-dossie-engenharia-reversa.md`](02-dossie-engenharia-reversa.md).
- Consulte requisitos e arquitetura em [`03`](03-requisitos.md) e [`04`](04-arquitetura.md).
- Para executar, volte ao [`README.md`](../README.md).
