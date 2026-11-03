# 13 — Backlog priorizado do projeto

> **Status: proposta de planejamento.** Este backlog organiza trabalho para a demonstração técnica e validação de hipóteses do produto. Não representa compromisso de prazo, aprovação regulatória ou autorização para uso de dados reais. O projeto deve continuar usando dados sintéticos até que as aprovações e controles necessários a qualquer uso real sejam definidos e concluídos.
>
> Complementa [`docs/12-pendencias-regulatorias.md`](12-pendencias-regulatorias.md), [`docs/09-roadmap-incremental.md`](09-roadmap-incremental.md) e [`docs/08-plano-de-testes.md`](08-plano-de-testes.md). Não substitui esses documentos.

## 1. Objetivo e regras de priorização

O objetivo imediato é tornar o protótipo **fácil de executar e avaliar com dados sintéticos**, depois validar as necessidades antes de ampliar a solução. O backlog está organizado por sequência de valor e aprendizado:

1. **P0 — Demonstração reproduzível:** preparar uma demo confiável para avaliação.
2. **P1 — Validação de necessidades:** confirmar problema, usuários e requisitos com evidências adequadas.
3. **P2 — Qualidade técnica:** fortalecer testes e operação de desenvolvimento conforme as necessidades validadas.
4. **P3 — Gate de governança:** condição bloqueadora para qualquer piloto operacional ou lançamento que envolva dados ou operação reais.
5. **P4 — Evoluções futuras:** considerar somente após validação de valor, dependências e dados necessários.

Prioridade indica ordem recomendada, não uma promessa de entrega ou autorização para implantação. Para ordenar itens dentro de uma faixa, considerar valor para o usuário, redução de risco, aprendizado, dependências e esforço. Preferir incrementos pequenos que produzam evidência cedo.

## 2. Estado inicial

Os estados deste documento são propostas iniciais a serem confirmadas pela equipe. O CI aprovado atesta apenas as verificações automatizadas configuradas; não comprova qualidade de todas as jornadas, validação com usuários ou prontidão para produção.

| Faixa | Resultado esperado | Estado inicial proposto |
| --- | --- | --- |
| P0 | Demo sintética clara, testável e repetível | A planejar; confirmar o que já existe |
| P1 | Hipóteses e requisitos priorizados com evidências | A planejar |
| P2 | Qualidade adicional de acordo com o escopo validado | Planejado; selecionar após P0/P1 |
| P3 | Decisões e controles aprovados antes de operação real | Bloqueado até avaliação e aprovação aplicáveis |
| P4 | Capacidades de expansão ou analytics | Futuro; depende de evidência e justificativa |

## 3. P0 — Demonstração sintética reproduzível

### DEMO-01 — Conferir o procedimento de instalação e inicialização

- **Objetivo:** permitir que uma pessoa execute a demonstração sem assistência direta do autor.
- **Trabalho:** testar as instruções em ambiente limpo; corrigir pré-requisitos, comandos, configuração e erros encontrados.
- **Critérios de aceite:**
  - uma pessoa que não preparou o ambiente consegue seguir o guia a partir de um clone limpo;
  - a aplicação inicia com dados sintéticos;
  - nenhum segredo real ou dado pessoal é necessário;
  - erros e limitações conhecidos ficam documentados.
- **Dependências:** acesso ao repositório e ambiente de desenvolvimento compatível.
- **Tamanho inicial:** pequeno/médio.
- **Estado:** a confirmar.

### DEMO-02 — Documentar reinicialização e restauração da demo

- **Objetivo:** tornar a demonstração repetível entre execuções.
- **Trabalho:** documentar como limpar e recriar o banco local de demonstração sem confundir a ação com procedimentos de produção.
- **Critérios de aceite:**
  - o guia distingue claramente dados locais de demonstração de dados persistentes;
  - a reinicialização deixa um estado sintético conhecido;
  - não há risco de apagar dados fora do ambiente local da demo;
  - o procedimento é verificado em ambiente limpo.
- **Dependências:** DEMO-01.
- **Tamanho inicial:** pequeno.
- **Estado:** a confirmar.

### DEMO-03 — Criar roteiro de demonstração ponta a ponta

- **Objetivo:** mostrar as jornadas previstas de forma consistente.
- **Trabalho:** preparar passos, dados sintéticos, resultados esperados e duração aproximada para cada perfil.
- **Critérios de aceite:**
  - o roteiro cobre cidadão, passageiro, motorista e gestor;
  - as credenciais usadas são exclusivamente as de demonstração;
  - cada etapa informa o resultado esperado e uma alternativa caso falhe;
  - não sugere vínculo com o sistema observado nem prontidão para produção.
- **Dependências:** DEMO-01, DEMO-02.
- **Tamanho inicial:** pequeno.
- **Estado:** a planejar.

### DEMO-04 — Preparar cenários de exceção com dados sintéticos

- **Objetivo:** demonstrar como a aplicação se comporta além do caminho feliz.
- **Trabalho:** escolher e preparar cenários como veículo sem sinal, viagem cancelada e embarque pendente, respeitando o domínio existente.
- **Critérios de aceite:**
  - pelo menos três cenários de exceção são reproduzíveis;
  - cada cenário tem estado inicial, ação e resultado esperado documentados;
  - os cenários não exigem dados reais;
  - os comportamentos importantes têm teste automatizado ou justificativa para teste manual.
- **Dependências:** DEMO-03; confirmar suporte atual do domínio antes de implementar novos estados.
- **Tamanho inicial:** médio.
- **Estado:** a planejar.

### DEMO-05 — Cobrir jornadas prioritárias no navegador

- **Objetivo:** detectar regressões de interface que a suíte de API não cobre.
- **Trabalho:** avaliar ferramenta e adicionar testes de navegador para as jornadas prioritárias, incluindo mensagens de erro e estados vazios.
- **Critérios de aceite:**
  - pelo menos uma jornada principal acordada é executada automaticamente no navegador;
  - o teste funciona em CI com ambiente e dados sintéticos;
  - falhas de interface são distinguíveis de indisponibilidade externa;
  - não são usados serviços externos ou contas reais como dependência do teste.
- **Dependências:** DEMO-03; escolher jornadas antes de escolher a cobertura completa.
- **Tamanho inicial:** médio.
- **Estado:** planejado; o plano de testes registra E2E como lacuna.

## 4. P1 — Validação do problema e dos requisitos

### VALID-01 — Identificar participantes e limites da validação

- **Objetivo:** definir com quem e sob quais condições as hipóteses podem ser discutidas.
- **Trabalho:** identificar potenciais usuários e pessoas que conheçam o processo operacional; confirmar requisitos institucionais ou éticos aplicáveis antes de qualquer atividade com participantes.
- **Critérios de aceite:**
  - perfis e critérios de seleção estão descritos;
  - objetivo e limites da atividade estão claros;
  - dados pessoais ou dados operacionais reais não são solicitados sem avaliação e autorização prévias;
  - aprovações institucionais necessárias são confirmadas antes da coleta.
- **Dependências:** DEMO-03; orientação institucional conforme contexto.
- **Tamanho inicial:** pequeno/médio.
- **Estado:** a planejar.

### VALID-02 — Elaborar roteiro de perguntas não indutivas

- **Objetivo:** compreender o processo existente, dificuldades e necessidades sem vender antecipadamente uma solução.
- **Trabalho:** elaborar perguntas sobre tarefas, informação necessária, exceções e soluções atuais.
- **Critérios de aceite:**
  - perguntas não induzem respostas favoráveis ao protótipo;
  - não solicitam CPF, informação clínica, localização ou outros dados identificáveis desnecessários;
  - há orientação de registro minimizado e anonimizado;
  - o roteiro é revisado pela pessoa responsável pela atividade.
- **Dependências:** VALID-01.
- **Tamanho inicial:** pequeno.
- **Estado:** a planejar.

### VALID-03 — Registrar descobertas e incertezas

- **Objetivo:** separar evidências de observações, relatos, interpretações e hipóteses.
- **Trabalho:** consolidar feedback sem identificar participantes e relacioná-lo às necessidades do produto.
- **Critérios de aceite:**
  - cada achado indica sua origem e nível de confiança;
  - observações, relatos, inferências e hipóteses não são tratados como equivalentes;
  - dados identificáveis são omitidos ou minimizados;
  - conclusões negativas e divergentes também são registradas.
- **Dependências:** VALID-01, VALID-02.
- **Tamanho inicial:** pequeno.
- **Estado:** a planejar.

### VALID-04 — Revisar requisitos e critérios de aceite

- **Objetivo:** garantir que o backlog atende necessidades identificadas, não apenas funcionalidades imaginadas.
- **Trabalho:** mapear necessidades prioritárias aos requisitos e determinar como cada uma será verificada.
- **Critérios de aceite:**
  - cada requisito prioritário tem perfil afetado, evidência, justificativa e critério de verificação;
  - requisitos não validados permanecem marcados como hipótese;
  - requisitos regulatórios não são considerados aprovados por inferência técnica;
  - escopo e itens excluídos ficam registrados.
- **Dependências:** VALID-03.
- **Tamanho inicial:** médio.
- **Estado:** a planejar.

## 5. P2 — Qualidade técnica após confirmar o escopo

### QUAL-01 — Testes E2E e de acessibilidade

- **Objetivo:** cobrir jornadas reais da interface e identificar barreiras comuns.
- **Critérios de aceite:** jornadas prioritárias têm teste automatizado no navegador; verificações de acessibilidade são executadas e os problemas encontrados são corrigidos ou registrados com justificativa.
- **Dependências:** VALID-04 e DEMO-05.
- **Tamanho inicial:** médio.
- **Estado:** planejado; relacionado à lacuna I8 do roadmap.

### QUAL-02 — Medir cobertura e escolher zonas de risco

- **Objetivo:** usar cobertura como instrumento de diagnóstico, não como única medida de qualidade.
- **Critérios de aceite:** relatório de cobertura é reproduzível; módulos críticos e áreas sem cobertura são identificados; metas e exceções são justificadas e não substituem testes de comportamento.
- **Dependências:** P0 estável e critérios de risco definidos.
- **Tamanho inicial:** pequeno/médio.
- **Estado:** planejado.

### QUAL-03 — Validar comportamento em PostgreSQL

- **Objetivo:** detectar diferenças entre SQLite de desenvolvimento e o banco de referência.
- **Critérios de aceite:** testes relevantes executam em PostgreSQL efêmero; o processo funciona em banco vazio; diferenças e requisitos de inicialização são documentados.
- **Dependências:** definição de evolução de esquema; pode ser combinado com INFRA-01.
- **Tamanho inicial:** médio.
- **Estado:** planejado; relacionado à lacuna I4/I8.

### INFRA-01 — Adicionar migrações versionadas

- **Objetivo:** evoluir o esquema sem depender de recriação do banco.
- **Critérios de aceite:** migração inicial e incremental são reproduzíveis em banco vazio e atualizado; caminho de rollback ou estratégia de recuperação está documentado e testado; CI verifica a migração.
- **Dependências:** decisão técnica sobre banco e compatibilidade.
- **Tamanho inicial:** médio.
- **Estado:** planejado; roadmap I4.

### INFRA-02 — Demonstrar backup e restauração em ambiente de teste

- **Objetivo:** comprovar que um backup de teste pode ser restaurado.
- **Critérios de aceite:** procedimento, retenção de teste, resultado e duração da restauração ficam documentados; dados usados são sintéticos; falhas e limites são registrados.
- **Dependências:** banco e ambiente de teste definidos.
- **Tamanho inicial:** médio.
- **Estado:** planejado.

### SEC-01 — Refinar requisitos de identidade, autorização e sessão

- **Objetivo:** substituir credenciais compartilhadas e controles de demonstração por requisitos verificáveis, se o uso pretendido exigir isso.
- **Critérios de aceite:** perfis, permissões, expiração, revogação, auditoria e recuperação estão especificados; ameaças e fluxos de falha são revisados; a implementação é tratada em tarefa separada com testes.
- **Dependências:** VALID-04 e decisões dos responsáveis pela operação.
- **Tamanho inicial:** médio/grande.
- **Estado:** a especificar; não implica que um provedor de identidade esteja escolhido.

## 6. P3 — Gate obrigatório antes de operação real

P3 é uma **condição de bloqueio**, não uma aprovação automática ao concluir P0–P2. Nenhum item abaixo deve ser marcado como aprovado apenas com base no CI, documentação preliminar ou demonstração local.

### GATE-01 — Governança e finalidade

- Identificar e documentar controlador, operadores, finalidade e responsabilidades.
- Obter as decisões necessárias das pessoas responsáveis e do jurídico.
- **Saída verificável:** decisão e responsáveis registrados em local apropriado.

### GATE-02 — Privacidade, transparência e direitos

- Validar as operações de tratamento, avisos, ROPA e fluxos de solicitação aplicáveis.
- Avaliar a necessidade e aprovação de DPIA ou avaliação equivalente.
- **Saída verificável:** documentação aprovada pelo controlador e responsáveis competentes.

### GATE-03 — Segurança e infraestrutura

- Definir e verificar TLS, cabeçalhos, gestão de segredos, banco, backups, controle de acesso, monitoramento e processo de incidentes.
- Verificar a configuração de produção contra os riscos e limitações descritos em `SECURITY.md`.
- **Saída verificável:** configuração revisada, testes e evidências operacionais registrados.

### GATE-04 — Contratos e fornecedores

- Revisar hospedagem, integrações, operadoras, acesso, responsabilidades, retenção e encerramento de serviço.
- **Saída verificável:** acordos e aprovações necessários concluídos antes de transferir dados.

### GATE-05 — Verificação independente e autorização de lançamento

- Definir escopo e autorização de revisão de segurança; conduzir avaliações apropriadas sem atingir sistemas ou dados sem permissão.
- Exercitar restauração e resposta a incidentes.
- Obter decisão formal de lançamento das pessoas responsáveis.
- **Saída verificável:** riscos residuais aceitos por responsáveis identificados e gate de lançamento registrado.

Os requisitos concretos podem variar conforme controlador, finalidade, dados e contexto. Este backlog não determina sozinho quais obrigações legais se aplicam.

## 7. P4 — Evoluções futuras sujeitas a validação

| ID | Capacidade candidata | Condição antes de priorizar |
| --- | --- | --- |
| FUT-01 | OTP ou canal adicional para passageiro | Necessidade validada, acessibilidade, custo, fornecedor e alternativa para quem não usa o canal avaliados |
| FUT-02 | Suporte a múltiplos municípios/operadoras | Patrocínio, segregação de acesso, responsabilidades e requisitos de integração definidos |
| FUT-03 | Rate limit distribuído e escala horizontal | Carga ou implantação com múltiplas instâncias justificar a complexidade |
| FUT-04 | Notificações operacionais | Finalidade, preferências, dados compartilhados, custos e falhas do fornecedor definidos |
| FUT-05 | ETA ou analytics avançado | Dados adequados e autorizados, métrica de avaliação e riscos de inferência analisados; sem automatizar decisões de saúde/regulação |

## 8. Dependências sugeridas

```text
DEMO-01 → DEMO-02 → DEMO-03 → DEMO-04
                         └────→ DEMO-05
DEMO-03 → VALID-01 → VALID-02 → VALID-03 → VALID-04
VALID-04 → seleção de QUAL-01/02/03, INFRA-01/02 e SEC-01
P0/P1/P2 não substituem GATE-01…GATE-05 antes de operação real
```

As dependências são um guia inicial. Ajuste-as quando o escopo e os achados forem conhecidos; não implemente dependências regulatórias por suposição.

## 9. Modelo de cartão para novos itens

Use este modelo ao criar tarefas adicionais:

```text
ID e título:
Faixa/prioridade:
Perfil afetado:
Necessidade ou risco:
Evidência (observação, relato, requisito aprovado ou hipótese):
Resultado esperado:
Critérios de aceite verificáveis:
Dependências:
Dados usados (confirmar que são sintéticos quando aplicável):
Responsável:
Tamanho estimado: pequeno / médio / grande
Estado: proposta / pronta / em andamento / bloqueada / concluída
Risco residual ou decisão pendente:
```

Não inclua credenciais, dados pessoais ou informação confidencial nos cartões do repositório público.

## 10. Próximas ações recomendadas

1. Confirmar o estado real de DEMO-01 e DEMO-02 executando o procedimento em clone/ambiente limpo.
2. Selecionar DEMO-03 como primeira entrega observável e definir roteiro e critérios de aceite.
3. Identificar se e como VALID-01 pode ser conduzida, incluindo aprovações institucionais aplicáveis.
4. Atualizar estados, responsáveis e estimativas somente após a conferência; manter P3 bloqueado até as aprovações necessárias.
5. Abrir issues pequenas para os itens aprovados para execução e manter este arquivo como visão do backlog.

## 11. Histórico de revisão

| Data | Alteração | Responsável |
| --- | --- | --- |
| 2026-11-03 | Criação da estrutura inicial do backlog priorizado | A preencher |
