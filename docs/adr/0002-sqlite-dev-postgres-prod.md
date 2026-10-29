# ADR 0002 — SQLite em desenvolvimento e PostgreSQL em produção

- **Status:** aceito
- **Data:** 2026-10-29
- **Decisores:** autor do TCC
- **Relacionados:** ADR 0001, `db/schema.sql`, `docs/05-modelo-de-dados.md`

## Contexto

O protótipo precisa rodar em qualquer máquina de avaliador sem instalação de
servidor de banco, mas também precisa demonstrar um caminho crível para
produção com dados de saúde e telemetria. O volume estimado em produção é de
aproximadamente 180 mil pontos de posição por dia para 50 veículos, com leitura
pública 10–20× superior à ingestão no pico.

As alternativas foram: SQLite apenas, PostgreSQL apenas, banco embarcado
proprietário e serviço gerenciado.

## Decisão

Usar **SQLite em desenvolvimento e demonstração** e **PostgreSQL 16+ em
produção**, com SQLAlchemy 2.0 como camada de abstração. O DDL PostgreSQL de
referência é gerado a partir dos modelos e versionado em `db/schema.sql`.

- SQLite roda com `PRAGMA journal_mode=WAL`, `foreign_keys=ON` e
  `busy_timeout`, para reduzir bloqueios e preservar integridade referencial.
- PostgreSQL é o alvo do Docker Compose em `infra/` e do roadmap I4.
- PostGIS é opcional; o protótipo calcula distância com Haversine em memória
  para manter portabilidade.
- Migrações versionadas com Alembic ficam no roadmap I4; até lá, o schema é
  criado a partir dos modelos em desenvolvimento.

## Justificativa

1. **Zero instalação** — `make run` funciona em Linux, macOS e Windows sem
   serviço externo; essencial para banca e CI.
2. **Testes rápidos** — o banco em memória/arquivo temporário recria o cenário
   por teste, sem containers.
3. **Caminho de produção explícito** — o mesmo modelo ORM gera DDL PostgreSQL;
   tipos, índices e constraints são documentados.
4. **Custo** — não há dependência de nuvem nem de licença.

## Consequências

### Positivas

- Reprodutibilidade e onboarding triviais.
- Suíte de 79 testes rápida e determinística.
- CI sem serviço de banco.
- Schema PostgreSQL revisável e regenerável.

### Negativas

- Diferenças de dialeto: tipos, `NULLS LAST`, `ILIKE`, *upsert* e recursos
  geoespaciais não são idênticos.
- SQLite não suporta concorrência de escrita intensa nem réplicas.
- Sem migrações, alterações de schema exigem recriação em dev.
- O DDL gerado pode divergir do banco real se alguém editar modelos sem
  regenerar.

### Mitigações

- Evitar SQL específico de dialeto; usar ORM e expressões portáveis.
- CI regenera o schema e confere `CREATE TABLE`.
- Testes de integração com PostgreSQL efêmero no roadmap I4.
- Aviso explícito de que SQLite é apenas desenvolvimento.

## Alternativas descartadas

| Alternativa | Motivo do descarte |
| --- | --- |
| SQLite em produção | Sem concorrência adequada, backup e replicação limitados |
| PostgreSQL apenas | Exigiria serviço externo para qualquer avaliação |
| MongoDB | Modelo relacional é mais adequado a autorizações e invariantes |
| Banco gerenciado | Dependência de provedor e custo sem ganho no escopo |

## Critérios de reversão

Migrar integralmente para PostgreSQL quando: houver dados reais, múltiplas
réplicas ou necessidade de particionamento. A decisão já está prevista no
roadmap I4; o SQLite permanece apenas para testes rápidos.

## Referências

- `db/schema.sql`
- `docs/04-arquitetura.md`, seção 9
- `infra/docker-compose.yml`
