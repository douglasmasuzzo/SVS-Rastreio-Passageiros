# ADR 0004 — Sessão de motorista sem estado com token HMAC

- **Status:** aceito
- **Data:** 2026-10-29
- **Decisores:** autor do TCC
- **Relacionados:** `backend/app/security.py`, `backend/app/deps.py`, ADR 0003

## Contexto

O motorista acessa a PWA em campo, muitas vezes em celular compartilhado, com
conectividade instável. A sessão precisa ser simples de usar, resistente a
adulteração e não pode expor passageiros de outro veículo.

As alternativas foram: sessão em memória, sessão em banco, JWT assinado,
token opaco com tabela de sessões e token HMAC no formato `payload.assinatura`.

## Decisão

Emitir um **token sem estado** no formato `base64url(payload).hmac_sha256`,
com payload contendo `motorista_id`, `veiculo_id`, `exp` e um `nonce`. O token é
assinado com `SVS_SESSION_SECRET`, validado em tempo constante e expira em 8
horas. Não há tabela de sessões no MVP.

O token é enviado em `Authorization: Bearer <token>`. A dependência
`motorista_autenticado` valida assinatura, expiração e existência/atividade do
motorista e do veículo; em seguida, o router confirma que a viagem pertence ao
veículo da sessão.

## Justificativa

1. **Simplicidade** — não há estado de sessão a limpar, replicar ou expirar em
   banco; reiniciar a API não derruba todos os motoristas.
2. **Adequação ao turno** — 8 horas cobrem um turno típico sem exigir login
   repetido em cada parada.
3. **Resistência a adulteração** — HMAC-SHA256 com segredo do servidor; qualquer
   alteração no payload invalida a assinatura.
4. **Escopo explícito** — o token carrega motorista e veículo, e o servidor
   valida o vínculo com a viagem, impedindo acesso cruzado.
5. **Sem dependência de biblioteca JWT** — formato mínimo, auditável e testável.

## Consequências

### Positivas

- API stateless, compatível com múltiplas réplicas.
- Nenhuma tabela de sessão para manter ou expurgar.
- Testes simples de expiração, adulteração e escopo.
- Login rápido em campo.

### Negativas

- **Revogação imediata é limitada**: um token roubado continua válido até
  expirar. Não há lista de revogação no MVP.
- Troca de PIN ou desligamento do motorista não invalida tokens já emitidos,
  exceto pela checagem de atividade no banco.
- 8 horas podem ser longas em dispositivo compartilhado.
- Rotação de segredo invalida todas as sessões de uma vez.

### Mitigações

- Checagem de motorista/veículo ativo a cada requisição.
- Expiração curta o suficiente para o turno e auditoria de login.
- Roadmap I3: revogação por motorista/veículo, *device binding* e lista de
  revogação (ou versão de segredo por motorista).
- Em produção, segredo forte e rotação planejada.

## Alternativas descartadas

| Alternativa | Motivo do descarte |
| --- | --- |
| Sessão em memória | Não sobrevive a reinício nem a múltiplas réplicas |
| Tabela de sessões | Complexidade de expurgo e consulta; desnecessária no MVP |
| JWT completo | *Overhead* de biblioteca e tentações de claims desnecessárias |
| Cookie de sessão | PWA e app usam header; CORS e CSRF complicariam |
| Token opaco | Exige armazenamento e consulta por requisição |

## Critérios de reversão

Adotar sessão com revogação (tabela ou Redis) quando houver: múltiplos
dispositivos por motorista, exigência de logout remoto, incidente de token
roubado ou mais de um turno por dia no mesmo aparelho.

## Referências

- `backend/app/security.py`
- `backend/app/routers/deps.py`
- `tests/test_seguranca.py`
- OWASP ASVS 4.0.3, seção 3 (Session Management)
