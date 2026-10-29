# ADR 0007 — Chaves de serviço estáticas para ingestão e administração

- **Status:** aceito (com dívida técnica declarada)
- **Data:** 2026-10-29
- **Decisores:** autor do TCC
- **Relacionados:** `backend/app/routers/deps.py`, `docs/07-seguranca-lgpd.md`, ADR 0001

## Contexto

Dois tipos de cliente não são pessoas: o gateway/operadora que envia telemetria
e o painel administrativo usado pela regulação. Ambos precisam de autenticação
simples no MVP, sem provedor de identidade, sem OAuth2 e sem cadastro de
usuários. O protótipo precisa ser executável localmente e testável.

As alternativas foram: chave estática em header, OAuth2 *client credentials*,
mTLS, JWT emitido por um provedor e ausência de autenticação (inaceitável).

## Decisão

Usar **chaves de serviço estáticas e distintas**, enviadas por header:

- `X-Ingest-Key` para `POST /api/v1/telemetria`;
- `X-Admin-Key` para todas as rotas `/api/v1/admin/*`.

As chaves são configuradas por variáveis de ambiente (`SVS_INGEST_KEY`,
`SVS_ADMIN_KEY`), comparadas com `hmac.compare_digest` e nunca aceitas com os
valores padrão em `SVS_ENV=prod`. A aplicação recusa iniciar se as chaves forem
iguais ou se permanecerem nos valores de demonstração em produção.

## Justificativa

1. **Escopo** — são dois clientes de máquina e um painel de demonstração; um
   provedor de identidade seria desproporcional.
2. **Simplicidade** — configuração por ambiente, sem banco de usuários, fluxo
   de consentimento ou *refresh token*.
3. **Testabilidade** — testes podem injetar chave válida/inválida sem mock de
   provedor.
4. **Separação de privilégios** — chaves distintas impedem que o gateway leia
   KPIs ou que o painel envie telemetria.
5. **Caminho de evolução** — a interface por header pode ser substituída por
   OAuth2/mTLS sem alterar a regra de negócio.

## Consequências

### Positivas

- Autenticação de máquina funcional em minutos.
- Nenhuma dependência externa.
- Chaves separadas por finalidade.
- Recusa de valores padrão em produção.

### Negativas

- **Sem identidade por operadora**: uma chave compartilhada não distingue
  gateways nem permite revogação individual.
- Rotação manual e sem sobreposição; trocar a chave exige atualizar o cliente.
- Sem escopo por município ou por rota.
- Chave em variável de ambiente pode vazar em logs, backups ou *dumps*.
- Não há auditoria de “qual operadora enviou” além da chave.

### Mitigações

- Chaves longas e aleatórias, geradas por `secrets.token_urlsafe`.
- Nunca logar headers de autenticação.
- Rotação documentada em `docs/07` e checklist de produção.
- Rate limit por IP e por rota.
- Roadmap I5: OAuth2 *client credentials* ou mTLS por operadora, com rotação e
  auditoria por credencial.
- Roadmap I6: OIDC + MFA + RBAC para o painel.

## Alternativas descartadas

| Alternativa | Motivo do descarte |
| --- | --- |
| Sem autenticação | Inaceitável para telemetria e dados de pacientes |
| OAuth2 completo | Exige provedor, cadastro e fluxo; roadmap I5/I6 |
| mTLS | Exige PKI e configuração de clientes; roadmap I5 |
| JWT de longa duração | Mesmos problemas de revogação, com mais complexidade |
| Basic Auth | Credencial em base64; sem ganho sobre header |

## Dívida técnica assumida

Esta é uma decisão **provisória e declarada**. O protótipo não deve ir a
produção com uma única chave compartilhada por todas as operadoras. A condição
de saída é: múltiplas operadoras, necessidade de revogação individual ou
auditoria por credencial — o que deve ocorrer antes de qualquer piloto real.

## Referências

- `backend/app/routers/deps.py`
- `backend/app/config.py`
- `docs/07-seguranca-lgpd.md` — riscos R-02 e R-03
- OWASP ASVS 4.0.3, seção 2 (Authentication)
