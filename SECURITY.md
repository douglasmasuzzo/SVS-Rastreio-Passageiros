# Política de segurança

## Versões suportadas

| Versão | Suporte |
| --- | --- |
| `0.1.x` | Sim — protótipo acadêmico |

O projeto é um artefato de pesquisa. Não há SLA, canal 24×7 ou compromisso de
correção em prazo definido.

## Como reportar

Não abra issue pública para vulnerabilidades. Envie um relato privado ao autor
do repositório (ver perfil no GitHub) com:

- descrição do problema e impacto esperado;
- passos de reprodução mínimos (sem dados pessoais reais);
- versão/commit testado e ambiente (SO, Python, banco);
- sugestão de correção, se houver;
- se desejar, sua preferência de crédito.

Você receberá confirmação de recebimento e uma avaliação inicial. Divulgue
publicamente apenas após alinhamento com o autor.

## Escopo

**Dentro do escopo:** API FastAPI (`backend/app`), PWA (`backend/static`),
scripts de geração/anonimização, schema SQL, configuração de exemplo e
dependências declaradas.

**Fora do escopo:** sistemas de terceiros, CDN do Leaflet, infraestrutura de
hospedagem, dados sintéticos em si e o sistema original observado (não é
operado por este projeto).

## Modelo de segurança resumido

O protótipo adota *secure by default* no que é proporcional a um trabalho
acadêmico:

- **Pseudonimização:** CPF e PIN somente como HMAC-SHA256 com pepper; exibição
  por máscara. Nenhum CPF em texto claro no banco ou nos logs.
- **Dois fatores na consulta do passageiro:** CPF + data de nascimento, com
  mensagem de erro genérica e limitação de taxa para reduzir enumeração.
- **Minimização:** posição pública arredondada a 4 casas (~11 m), trilha de
  12 h, limite de pontos, ausência de dados pessoais em endpoints públicos.
- **Serviços autenticados:** `X-Ingest-Key` para telemetria, `X-Admin-Key` para
  administração, token de motorista assinado (HMAC, 8 h, stateless).
- **Integridade:** telemetria append-only; trilha de auditoria para consultas,
  validações e exportações; IP pseudonimizado.
- **Configuração segura:** em `SVS_ENV=prod` a aplicação recusa segredos padrão
  e `SVS_AUTO_CREATE`; CORS fica desabilitado por padrão.

Detalhes, ativos e riscos residuais: [`docs/07-seguranca-lgpd.md`](docs/07-seguranca-lgpd.md).

## Limitações conhecidas (não são falhas aceitáveis em produção)

Este protótipo **não deve operar com dados reais**. Limitações conscientes:

1. Limitador de taxa em memória, por processo — não compartilhado entre réplicas.
2. `X-Admin-Key` é uma chave estática única, sem RBAC, MFA ou rotação.
3. PIN do motorista tem 4–12 dígitos e a sessão não é revogável antes de expirar.
4. Data de nascimento é um segundo fator fraco; OTP por SMS está no roadmap.
5. Sem migrações versionadas (Alembic); `create_all` é apenas para demo.
6. `audit_log` é append-only por convenção da aplicação, não por permissão de
   banco.
7. Banco padrão SQLite, sem replicação ou backup gerenciado.
8. Sem WAF, proteção DDoS, varredura de dependências ou testes de intrusão.

## Checklist mínimo antes de qualquer exposição pública

- [ ] `SVS_ENV=prod` e todos os segredos próprios, longos e aleatórios.
- [ ] TLS terminado em proxy reverso confiável; `X-Forwarded-For` controlado.
- [ ] PostgreSQL gerenciado, backup testado e migrações Alembic.
- [ ] Rate limit distribuído (Redis/API Gateway) e bloqueio progressivo.
- [ ] Substituir chaves estáticas por OAuth2/OIDC com RBAC e MFA.
- [ ] OTP para passageiro e PIN individual com bloqueio por tentativas.
- [ ] Retenção, anonimização e descarte automatizados; DPIA aprovado.
- [ ] Logs sem dados pessoais e monitoramento de abuso.
- [ ] Revisão jurídica e contrato de operador (LGPD art. 39).
