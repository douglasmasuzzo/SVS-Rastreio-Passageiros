# Changelog

Todas as mudanças relevantes deste projeto são registradas aqui. O formato
segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e o
versionamento segue [SemVer](https://semver.org/lang/pt-BR/).

## [Não lançado]

### Planejado

- OTP por SMS para a consulta do passageiro (I2).
- Migrações Alembic e implantação PostgreSQL/PostGIS (I4).
- Rate limit distribuído com Redis (I5).
- Painel administrativo com RBAC e MFA (I6).

## [0.1.0] — 2026-10-29

### Adicionado

- API FastAPI com rastreamento público por placa, consulta do passageiro,
  operação do motorista, ingestão de telemetria e painel administrativo.
- PWA sem build com telas de rastreio, consulta do passageiro, motorista,
  administração e página “Sobre”, incluindo manifesto, service worker e ícones.
- Modelo de dados com 12 tabelas: municípios, operadoras, veículos, motoristas,
  pacientes, unidades de saúde, viagens, autorizações, embarques, posições,
  eventos de viagem e trilha de auditoria.
- Pseudonimização de CPF/PIN com HMAC-SHA256 + pepper, CPF mascarado e consulta
  com segundo fator (data de nascimento).
- Posição pública arredondada (~11 m), trilha limitada a 12 h e ausência de
  dados pessoais nos endpoints públicos.
- Sessão de motorista stateless assinada por HMAC (8 h), chaves de serviço
  `X-Ingest-Key` e `X-Admin-Key`, limitação de taxa por IP e trilha de auditoria.
- Cenário sintético reprodutível com CPFs da base reservada `900000xxx`.
- Simuladores de telemetria (`backend/app/simulator.py` e
  `scripts/simular_telemetria.py`) com rota interpolada e descoberta de viagem
  ativa.
- Scripts de anonimização de evidências, exportação de OpenAPI, geração de
  schema PostgreSQL e snapshot do seed.
- Suíte com 79 testes de contrato, segurança e LGPD.
- Documentação: dossiê de engenharia reversa, requisitos, arquitetura, modelo
  de dados, API, segurança/LGPD, plano de testes, roadmap, relatório técnico e
  ADRs.
- Infraestrutura de demonstração com Dockerfile e docker-compose (API +
  PostgreSQL) e workflow de CI.

### Segurança

- A aplicação recusa iniciar em `SVS_ENV=prod` com segredos padrão ou
  `SVS_AUTO_CREATE` habilitado.
- Erros de consulta e de sessão são genéricos para dificultar enumeração.
- Telemetria é append-only e valida janela temporal e vínculo com o veículo.
- Exportação de telemetria é limitada a 50 mil linhas e auditada.

[0.1.0]: https://example.invalid/svs-rastreio/releases/tag/v0.1.0
