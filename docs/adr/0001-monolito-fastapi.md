# ADR 0001 — Monólito modular FastAPI

- **Status:** aceito
- **Data:** 2026-10-29
- **Decisores:** autor do TCC
- **Relacionados:** `docs/04-arquitetura.md`, ADR 0002, ADR 0005

## Contexto

O protótipo precisa entregar quatro jornadas (público, paciente, motorista e
gestão), ingestão de telemetria, auditoria e uma PWA em um semestre, com uma
pessoa e sem infraestrutura dedicada. O sistema observado não revela sua
arquitetura; portanto, a decisão é de projeto, não de reprodução.

As alternativas consideradas foram: microsserviços, *serverless* e monólito
modular.

## Decisão

Adotar um **monólito modular** em FastAPI, com um único processo Uvicorn e
camadas explícitas:

- `routers/` — transporte HTTP, autenticação de borda e mapeamento de erros;
- `services/` — regras de negócio, consultas e auditoria;
- `models/` — persistência SQLAlchemy;
- `schemas/` — contratos Pydantic;
- `security/` — criptografia, normalização e tokens.

A PWA é servida pelo mesmo processo, em `backend/static/`. O banco é acessado
por uma sessão SQLAlchemy injetada. Não há chamada de rede interna entre
componentes.

## Justificativa

1. **Complexidade proporcional** — o domínio tem doze entidades e poucos
   fluxos; microsserviços adicionariam rede, deploy e observabilidade sem
   benefício mensurável.
2. **Consistência transacional** — embarque, validação e auditoria precisam da
   mesma transação; um monólito elimina *sagas* e consistência eventual.
3. **Testabilidade** — `TestClient` sobe a aplicação inteira em memória; a suíte
   cobre contratos e segurança sem infraestrutura externa.
4. **Reprodutibilidade acadêmica** — `make run` sobe tudo; a banca consegue
   executar sem Docker, Kubernetes ou nuvem.

## Consequências

### Positivas

- Um único artefato para implantar e versionar.
- Transações ACID simples para embarque e autorização.
- Menos latência e menos pontos de falha.
- Curva de leitura baixa para avaliadores.

### Negativas

- Escala vertical antes de horizontal; réplicas exigem banco e rate limit
  compartilhados (roadmap I5).
- Fronteiras entre módulos dependem de disciplina; imports cruzados podem
  degradar o desenho.
- Um deploy afeta todas as jornadas ao mesmo tempo.

### Mitigações

- Regras de camada documentadas em `docs/04-arquitetura.md`.
- Testes que falham se um router importar modelo diretamente para regra de
  negócio (revisão de código).
- Separação de routers por domínio, facilitando extração futura se necessário.
- Rate limit em memória isolado em serviço, substituível por Redis.

## Alternativas descartadas

| Alternativa | Motivo do descarte |
| --- | --- |
| Microsserviços | Custo operacional e de teste desproporcional ao escopo |
| *Serverless* | Cold start, limites de execução e dependência de provedor |
| API + SPA com build | Etapa de build e toolchain extras sem ganho funcional |
| Framework com admin pronto | Menos controle sobre contratos e privacidade |

## Critérios de reversão

Reavaliar se: houver mais de duas equipes independentes; a ingestão de
telemetria precisar escalar separadamente; ou o tempo de deploy passar a
bloquear a operação. Nesses casos, extrair primeiro a ingestão e a leitura
pública, mantendo o núcleo transacional.

## Referências

- `docs/04-arquitetura.md`
- `docs/08-plano-de-testes.md`
- FIELDING, Roy T. *Architectural Styles and the Design of Network-based
  Software Architectures*. 2000. Tese (Doutorado) — University of California,
  Irvine.
