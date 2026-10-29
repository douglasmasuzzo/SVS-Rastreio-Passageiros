# Infraestrutura

Referência de execução em contêiner: **API + PWA** e **PostgreSQL 16**. Serve
para demonstrar o caminho de produção; o desenvolvimento do dia a dia continua
usando SQLite e `make run` (ver `README.md` da raiz).

## Arquivos

| Arquivo | Papel |
| --- | --- |
| `Dockerfile` | Imagem Python 3.12 sem privilégios, com healthcheck |
| `docker-compose.yml` | Banco, seed idempotente e API |
| `.env.example` | Modelo de variáveis; copie para `.env` |
| `../db/schema.sql` | DDL aplicado na inicialização do PostgreSQL |
| `../.dockerignore` | Exclusões do contexto de build |

## Subir

```bash
cp infra/.env.example infra/.env
# edite infra/.env e troque todos os segredos
docker compose --env-file infra/.env -f infra/docker-compose.yml up --build
```

Acesse <http://localhost:8000>. O `seed` roda uma vez, depois que o banco está
saudável, e é idempotente: se já houver veículos, não faz nada.

Para derrubar **e apagar** os dados do volume:

```bash
docker compose -f infra/docker-compose.yml down -v
```

## Decisões operacionais

- **`SVS_ENV=prod`** — a aplicação recusa os segredos de demonstração e exige
  `SVS_AUTO_CREATE=0`. O schema vem de `db/schema.sql`, não do ORM.
- **Banco não publicado** — a porta 5432 fica restrita à rede do Compose. Para
  inspecionar, descomente o mapeamento em `127.0.0.1`.
- **Um worker Uvicorn** — o rate limit é em memória e o SQLite não é
  compartilhado. Múltiplas réplicas exigem Redis e PostgreSQL (roadmap I5).
- **Sem migrações** — o DDL é aplicado no `initdb`. Alterações posteriores
  exigem Alembic (roadmap I4) ou recriação do volume em demonstração.
- **Dados sintéticos** — o seed cria CPFs da faixa `900000xxx`. Não use com
  dados reais.
- **TLS** — o Compose não termina TLS. Em produção, coloque um proxy reverso
  (Nginx/Traefik) ou um balanceador com certificado à frente da API.

## Verificações

```bash
curl -fsS http://localhost:8000/healthz
curl -fsS http://localhost:8000/api/v1/publico/veiculos
docker compose -f infra/docker-compose.yml ps
docker compose -f infra/docker-compose.yml logs -f api
```

## Limitações declaradas

- Não há backup automático, replicação, monitoramento ou *secrets manager*.
- Não há teste de restauração nem de carga.
- Não há isolamento por município/operadora nas chaves de serviço.
- A imagem é uma referência acadêmica, não um artefato homologado.

Antes de qualquer piloto com dados reais, cumpra o checklist de
`docs/11-etica-e-conformidade.md` e o de `SECURITY.md`.
