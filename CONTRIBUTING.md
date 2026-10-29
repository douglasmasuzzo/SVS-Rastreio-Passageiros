# Como contribuir

Obrigado pelo interesse. Este é um projeto acadêmico; contribuições devem
preservar a **originalidade clean-room**, a **privacidade por padrão** e a
**reprodutibilidade** dos artefatos.

## Antes de começar

1. Leia [`NOTICE.md`](NOTICE.md) e [`docs/07-seguranca-lgpd.md`](docs/07-seguranca-lgpd.md).
2. Não inclua dados reais, capturas não tratadas, credenciais ou trechos do
   sistema observado.
3. Para mudanças de comportamento, abra uma issue descrevendo o problema e o
   requisito afetado (`RF-xx`/`RNF-xx` em [`docs/03-requisitos.md`](docs/03-requisitos.md)).

## Ambiente

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
make test
make lint
```

## Padrões de código

- **Idioma:** código, nomes de domínio, mensagens de erro e documentação em
  português (pt-BR), exceto termos técnicos consagrados.
- **Python:** 3.11+, tipagem moderna (`from __future__ import annotations`),
  Ruff com `E, F, I, B, UP` e linha de 100 caracteres. `B008` é ignorado por
  causa do padrão `Depends(...)` do FastAPI.
- **SQLAlchemy:** modelos declarativos 2.0; toda regra de negócio fica em
  `services/`, não nos routers.
- **PWA:** JavaScript puro, sem framework e sem build; acessibilidade
  (rótulos, foco, contraste) e fallback textual quando o mapa não carregar.
- **API:** mudanças de contrato exigem atualização de `docs/06-api.md` e
  regeneração de `openapi/`.

## Testes

- Toda correção ou funcionalidade nova deve vir com teste em `tests/`.
- Segurança e LGPD têm prioridade: pseudonimização, segundo fator, mensagens
  genéricas, limites de trilha e auditoria.
- Rode a suíte completa antes de abrir PR:

```bash
PYTHONPATH=backend python3 -m pytest -q
python3 -m ruff check backend tests scripts analytics
```

- Testes **não** podem depender de rede, relógio real além de tolerâncias
  pequenas, ou de dados pessoais.

## Evidências e anonimização

- Novas capturas devem ser tratadas com `scripts/redact_evidencias.py` antes de
  entrar no repositório.
- Atualize `reverse-engineering/evidencias/manifesto.json` com título,
  descrição, redações aplicadas e SHA-256.
- Tarjas devem cobrir CPF, nome, placa, telefone, e-mail e operadora. Em caso
  de dúvida, tarje.
- Os arquivos originais ficam fora do repositório (diretório ignorado).

## Commits e pull requests

- Commits pequenos, no imperativo e com escopo: `api: valida janela de
  telemetria`, `docs: detalha achado A-04`.
- Um PR deve explicar **problema, solução, impacto de privacidade e como foi
  testado**.
- Não misture refatoração ampla com mudança funcional.
- Atualize [`CHANGELOG.md`](CHANGELOG.md) quando a mudança for visível ao
  usuário ou ao contrato.

## Artefatos gerados

Não edite manualmente:

- `db/schema.sql` — gerado de `backend/app/models.py`;
- `db/seed.sql` — snapshot do cenário canônico;
- `openapi/openapi.yaml|json` — exportados da aplicação.

Regenere com:

```bash
python3 scripts/gerar_schema_sql.py
python3 scripts/exportar_seed_sql.py
python3 scripts/exportar_openapi.py
```

## Conduta

Seja respeitoso e objetivo. Não são aceitas contribuições que exponham dados
pessoais, incentivem vigilância indiscriminada, discriminem pessoas ou violem
a LGPD e os princípios éticos descritos em
[`docs/11-etica-e-conformidade.md`](docs/11-etica-e-conformidade.md).
