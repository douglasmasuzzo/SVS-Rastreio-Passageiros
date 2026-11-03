# 12 — Brief de produto e pendências regulatórias

> **Status: rascunho de trabalho.** Este documento organiza hipóteses de produto e questões que precisam de validação. Não é parecer jurídico, avaliação de impacto aprovada, registro oficial de tratamento nem autorização para tratar dados reais ou lançar o sistema em produção.
>
> Enquanto as pendências aplicáveis não forem avaliadas e aprovadas pelas pessoas responsáveis, a demonstração deve usar exclusivamente dados sintéticos.

## 1. Objetivo deste documento

Consolidar um brief inicial do produto e registrar decisões regulatórias e operacionais ainda pendentes, evitando que hipóteses sejam confundidas com requisitos confirmados. O documento complementa — não substitui — [`docs/07-seguranca-lgpd.md`](07-seguranca-lgpd.md), [`docs/11-etica-e-conformidade.md`](11-etica-e-conformidade.md) e [`SECURITY.md`](../SECURITY.md).

As afirmações sobre o problema e os benefícios abaixo são hipóteses para validação com potenciais usuários e responsáveis pela operação. As questões legais devem ser avaliadas pelo controlador e por profissionais competentes, considerando o contexto concreto de eventual implantação.

## 2. Brief inicial do produto

### 2.1 Nome provisório

Plataforma de apoio ao transporte de saúde (nome de trabalho: SVS Rastreio).

### 2.2 Problema a investigar

A operação de transporte de saúde pode envolver consultas sobre o status dos veículos e viagens, confirmação de embarque e acompanhamento da execução do serviço. O projeto propõe centralizar informações operacionais em uma API e interfaces destinadas a cidadãos, passageiros, motoristas e gestores.

**Hipótese a validar:** esses problemas ocorrem nas operações consideradas e são suficientemente importantes para justificar uma solução dedicada. Não se presume que o protótipo reduza ligações, faltas, atrasos ou custos sem evidências de avaliação.

### 2.3 Usuários previstos e necessidades hipotéticas

| Perfil | Necessidade a validar | Demonstração existente no protótipo |
| --- | --- | --- |
| Cidadão | Consultar informação pública e aproximada sobre um veículo | Consulta pública de veículos, status e posição aproximada |
| Passageiro | Consultar informações da própria viagem | Consulta de viagem com credenciais sintéticas de demonstração |
| Motorista | Consultar escala, registrar eventos e enviar posição | Fluxo de motorista com PIN e telemetria simulada |
| Gestor/operador | Acompanhar viagens, autorizações e indicadores | Painel administrativo com dados sintéticos |

Os perfis e necessidades da tabela são uma proposta de produto, não uma confirmação de papéis oficiais, permissões institucionais ou requisitos de um órgão público.

### 2.4 Proposta de valor — hipótese

Oferecer um ponto de consulta e acompanhamento da operação, com potencial para facilitar a comunicação entre passageiros, motoristas e equipe de gestão. A utilidade, a adequação do fluxo e qualquer benefício operacional precisam ser validados; não devem ser anunciados como resultados comprovados.

### 2.5 Estado atual e limites

O repositório contém uma API FastAPI, uma PWA, fluxos para os perfis acima, indicadores, dados sintéticos, documentação e verificações automatizadas. Isso demonstra uma base técnica executável em ambiente de demonstração. Não comprova prontidão para produção, adequação jurídica, segurança operacional completa, usabilidade validada ou eficácia em uma operação real.

O protótipo não deve operar com dados reais de pacientes ou de operação sem uma avaliação e preparação separadas. Ver as limitações registradas em [`SECURITY.md`](../SECURITY.md) e no documento de segurança e LGPD.

### 2.6 Próxima entrega de produto sugerida

Preparar um piloto **demonstrativo, isolado e reproduzível**, com dados exclusivamente sintéticos, capaz de percorrer uma jornada completa: configurar uma viagem fictícia, consultar um veículo, simular início e fim da viagem, enviar posições simuladas e apresentar o resultado no painel.

O termo “piloto” nesta seção significa apenas uma demonstração técnica sem dados reais e sem operação pública. Um piloto operacional com pessoas, veículos ou dados reais exige escopo, aprovações, controles e acordos próprios.

### 2.7 Fora do escopo desta entrega

- Uso de dados reais de pacientes, motoristas ou veículos.
- Integração com sistemas municipais, de saúde ou de operadoras.
- Disponibilidade, suporte ou SLA de produção.
- Promessa de redução de custos, faltas, atrasos ou espera.
- Representação de que o projeto é oficial, autorizado ou vinculado ao sistema observado.
- Decisão automatizada sobre elegibilidade, regulação ou atendimento de saúde.

### 2.8 Critérios de aceite propostos para a demonstração

1. Uma pessoa consegue iniciar a demonstração seguindo as instruções documentadas.
2. Os fluxos demonstrados para cada perfil funcionam usando dados fictícios.
3. Há cenários de exceção controlados, como veículo sem sinal, viagem cancelada ou embarque pendente.
4. A demonstração não depende de segredos reais nem expõe dados pessoais.
5. Resultados, limitações, pré-requisitos e procedimento de reinicialização estão documentados.

Os critérios devem ser ajustados ao escopo acordado antes do desenvolvimento da entrega.

## 3. Registro de pendências regulatórias e de governança

Todos os itens começam como **pendentes de validação**. A existência de uma descrição ou proposta nos documentos do repositório não equivale a aprovação. Defina responsáveis e evidências antes de marcar qualquer item como concluído.

| ID | Questão pendente | Validação necessária / evidência de conclusão | Responsável a designar | Impacto potencial |
| --- | --- | --- | --- | --- |
| REG-01 | Papéis das partes e finalidade do tratamento | Identificar quem determinaria as finalidades e os meios do tratamento, eventuais operadores e as responsabilidades de cada parte; registrar decisão aprovada | Controlador proposto, jurídico e encarregado | Contratos, permissões, operação e documentação |
| REG-02 | Base legal e dados tratados | Avaliar as categorias de dados, finalidades e bases aplicáveis ao contexto concreto; obter decisão documentada do controlador com apoio jurídico | Controlador e jurídico | Coleta, autenticação, retenção e fluxos do produto |
| REG-03 | ROPA e transparência | Validar operações, titulares, dados, destinatários, prazos e informações a apresentar às pessoas; aprovar os registros e avisos pertinentes | Controlador e encarregado | Telas, avisos de privacidade, processos e contratos |
| REG-04 | Avaliação de impacto | Determinar, com as pessoas responsáveis, a avaliação de impacto necessária para dados de saúde inferidos e localização; registrar medidas, riscos e aprovação | Controlador, encarregado, segurança e jurídico | Arquitetura, minimização, acesso e mitigação de riscos |
| REG-05 | Direitos e solicitações de titulares | Definir canais, verificação de identidade, responsáveis, prazos e fluxos para solicitações aplicáveis; comprovar o procedimento em teste ou evidência operacional | Controlador e encarregado | Processos administrativos e funcionalidades futuras |
| REG-06 | Retenção, expurgo e preservação | Aprovar prazos por categoria de dados e regras de exceção; demonstrar expurgo verificável em banco, backups e dados derivados | Controlador, jurídico e equipe técnica | Modelo de dados, tarefas agendadas, backups e analytics |
| REG-07 | Encarregado e canal de contato | Confirmar a necessidade, designação e forma de publicação de um canal de contato adequado antes de eventual operação | Controlador | Avisos, atendimento e resposta a solicitações |
| REG-08 | Contratos e compartilhamento | Identificar destinatários e fornecedores; revisar responsabilidades, instruções, segurança, incidentes, retenção e encerramento nos acordos pertinentes | Controlador, jurídico e responsáveis por compras/fornecedores | Integrações, hospedagem, suporte e operação |
| REG-09 | Incidentes e comunicações | Definir responsáveis, avaliação, contenção, preservação de evidências e processo de decisão sobre comunicações; realizar exercício documentado | Controlador, encarregado e segurança | Operação, monitoramento e resposta a incidentes |
| REG-10 | Publicação e apresentação do projeto | Revisar nome, avisos, evidências anonimizadas, licenças e declarações de independência; confirmar que a comunicação não sugere vínculo ou validação inexistente | Autor, orientador/instituição quando aplicável e revisão jurídica se necessária | README, demonstração, materiais públicos e distribuição |

### 3.1 Modelo de acompanhamento por pendência

Para cada linha do registro, mantenha uma nota ou issue com os campos abaixo. Não registre dados pessoais ou informações confidenciais desnecessárias no repositório público.

- **ID e questão:**
- **Status:** pendente / em avaliação / decisão registrada / fora do escopo, com justificativa
- **Responsável pela decisão:**
- **Consultados:**
- **Fonte ou evidência analisada:**
- **Decisão e data:**
- **Impacto em código, operação ou contrato:**
- **Risco residual e aceite, se aplicável:**
- **Próxima ação e prazo:**

Uma pendência só deve ser marcada como concluída após decisão pelo responsável competente e registro da evidência correspondente. “Fora do escopo” também requer justificativa e aprovação apropriada, se afetar eventual tratamento ou implantação.

## 4. Condições para avançar de fase

### Fase A — demonstração sintética

Pode avançar como atividade de desenvolvimento e demonstração, mantendo dados sintéticos, ambiente controlado, credenciais de demonstração e avisos claros. Não apresentar essa fase como produção ou piloto com dados reais.

### Fase B — avaliação com potenciais usuários

Definir previamente objetivo, roteiro, dados coletados, participantes, consentimentos ou outras condições aplicáveis, armazenamento das anotações e aprovações institucionais necessárias. Preferir feedback não identificável e evitar coletar dados de saúde ou localização real. Se a atividade envolver pessoas ou dados reais, validar o protocolo com a instituição e os responsáveis competentes antes de iniciá-la.

### Fase C — piloto operacional ou lançamento

Não iniciar com base apenas neste brief, no CI aprovado ou na demonstração. Exige escopo e patrocinador definidos; decisões documentadas para as pendências regulatórias aplicáveis; controles técnicos e operacionais verificados; contratos e infraestrutura adequados; teste de restauração e resposta a incidentes; e autorização formal dos responsáveis. A lista técnica de produção permanece em [`SECURITY.md`](../SECURITY.md) e [`docs/07-seguranca-lgpd.md`](07-seguranca-lgpd.md).

## 5. Próximas ações

1. Revisar este brief e confirmar o escopo da demonstração sintética.
2. Identificar potenciais usuários e responsáveis pela operação, sem presumir que as hipóteses do documento foram validadas.
3. Registrar feedback de forma minimizada e atualizar problema, perfis e critérios de aceite.
4. Designar quem pode responder a cada pendência regulatória; encaminhar questões legais ao controlador e aos profissionais competentes.
5. Converter somente os requisitos confirmados em backlog técnico priorizado, mantendo itens não aprovados fora da implementação de produção.

## 6. Histórico de revisão

| Data | Alteração | Responsável |
| --- | --- | --- |
| 2026-11-03 | Criação do rascunho inicial de brief e registro de pendências | A preencher |
