# ADR 0003 — Pseudonimização de CPF e PIN com HMAC-SHA256

- **Status:** aceito
- **Data:** 2026-10-29
- **Decisores:** autor do TCC
- **Relacionados:** `backend/app/security.py`, `docs/07-seguranca-lgpd.md`, ADR 0004

## Contexto

O sistema lida com CPF de pacientes e PIN de motoristas. O CPF é identificador
semiaberto no Brasil e, combinado com data de nascimento, permite consultar
dados de saúde. O PIN, se armazenado em claro ou com hash rápido, pode ser
recuperado por força bruta.

As alternativas foram: armazenar em claro, criptografar de forma reversível,
usar hash sem sal, usar hash com sal por registro e usar HMAC com *pepper*.

## Decisão

Não armazenar CPF nem PIN em texto claro. Persistir apenas:

- `cpf_hash = HMAC-SHA256(cpf_normalizado, pepper)`, com `pepper` fornecido por
  variável de ambiente (`SVS_CPF_PEPPER`) e sem rotação automática no MVP;
- `cpf_mascarado`, no formato `***.***.***-NN`, para exibição;
- `pin_hash = HMAC-SHA256(pin, pepper_de_pin)`, comparado com
  `hmac.compare_digest`.

A normalização remove pontuação e valida os dígitos verificadores antes do
cálculo. O CPF em claro existe apenas no corpo da requisição, em memória, e não
é registrado em log nem em auditoria.

## Justificativa

1. **Busca determinística** — a consulta precisa localizar o paciente pelo CPF;
   um hash com sal aleatório por registro inviabilizaria a busca direta sem
   tabela auxiliar.
2. **Resistência a *rainbow tables*** — o CPF tem espaço pequeno; sem *pepper*,
   um hash simples seria trivialmente reversível por dicionário. O segredo
   externo ao banco eleva o custo de ataque.
3. **Comparação em tempo constante** — `compare_digest` evita vazamento por
   temporização.
4. **Minimização** — a máscara permite exibir o suficiente para o titular e o
   motorista sem revelar o número completo.
5. **Simplicidade operacional** — HMAC é nativo, rápido e não exige biblioteca
   criptográfica adicional.

## Consequências

### Positivas

- Vazamento do banco não entrega CPFs diretamente.
- Consulta continua eficiente com índice em `cpf_hash`.
- PIN não é recuperável a partir do banco.
- Nenhum CPF em log, resposta ou auditoria.

### Negativas

- **Perda de *pepper*** torna todos os hashes inúteis; exige backup seguro e
  plano de rotação.
- Não é possível recuperar o CPF para exibição; a máscara precisa ser
  armazenada separadamente.
- Colisões são improváveis, mas o sistema deve tratar `cpf_hash` como único.
- Rotação de *pepper* exige recomputar hashes com o CPF em claro, o que não é
  possível sem uma janela de migração assistida.

### Mitigações

- *Pepper* em cofre de segredos em produção, nunca no repositório.
- Em `SVS_ENV=prod`, a aplicação recusa os valores padrão.
- Plano de rotação documentado: gerar novo *pepper*, manter ambos por janela,
  recomputar no próximo acesso autenticado e aposentar o antigo.
- Testes que verificam ausência de CPF em respostas e auditoria.

## Alternativas descartadas

| Alternativa | Motivo do descarte |
| --- | --- |
| Texto claro | Viola minimização e expõe dados em backup/log |
| Criptografia reversível | Chave comprometida revela todos os CPFs; complexidade de gestão |
| SHA-256 sem segredo | CPF tem baixa entropia; *rainbow table* viável |
| bcrypt/Argon2 | Adequado a senhas, mas impede busca determinística por CPF |
| Tokenização com serviço externo | Dependência e custo fora do escopo |

## Observação sobre PIN

PIN de 4 dígitos tem apenas 10 mil combinações; o HMAC protege o armazenamento,
não a força bruta online. Por isso o rate limit e o bloqueio progressivo são
obrigatórios. O roadmap I3 prevê PIN de 6 dígitos e *device binding*.

## Referências

- `backend/app/security.py`
- `docs/07-seguranca-lgpd.md`
- NIST SP 800-63B — *Digital Identity Guidelines*
