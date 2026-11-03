# 12 — Brief de produto e pendências regulatórias

> **Status: rascunho de trabalho.** Este documento organiza hipóteses de produto e questões que precisam de validação. Não é parecer jurídico, avaliação de impacto aprovada, registro oficial de tratamento nem autorização para tratar dados reais ou lançar o sistema em produção.
>
> Enquanto as pendências aplicáveis não forem avaliadas e aprovadas pelas pessoas responsáveis, a demonstração deve usar exclusivamente dados sintéticos.

## 1. Objetivo deste documento

Consolidar um brief inicial do produto e registrar decisões regulatórias e operacionais ainda pendentes, evitando que hipóteses sejam confundidas com requisitos confirmados. O documento deverá _complementar_ e **ão substituir** os demais documentos:
- [`docs/07-seguranca-lgpd.md`](07-seguranca-lgpd.md)
- [`docs/11-etica-e-conformidade.md`](11-etica-e-conformidade.md)
- [`SECURITY.md`](../SECURITY.md).

As afirmações sobre o problema e os benefícios abaixo são hipóteses para validação com potenciais usuários e responsáveis pela operação. As questões legais devem ser avaliadas pelo controlador e por profissionais competentes, considerando o contexto concreto de eventual implantação.

## 2. Brief inicial do produto

### 2.1 Nome provisório

Plataforma de apoio ao transporte de saúde> SVS Rastreio de Passageiros ( S.R.P ).

### 2.2 Problema a investigar

A operação de embarque e desembarque de passageiros gera grandes desafios durante o processo de execução do transporte de passegeiros para o envio e cumprimento de consultas e exames na rede estadual hospitalar. O serviço prestado demonstra uma funcionalidade operacional limitada devido ao encargo de responsabilidades e funções exautivas, que sobrecarrega os respectivos responsáveis por cada tarefa exigida durante a operação destas atividades.
Contudo, a proposta deste sistema visa agrupar dados operacionais e projetar  mecanismos funcionais para obter-se melhor entendimento de estruturas e atividades operacionais, através da articularização de uma aplicação multi-plataforma para a validação de questões informativas identificadas entre períodos operacionais de passageiros, motoristas e gestores. 

**Hipótese a validar:** Como o desenvolvimento e implementação de uma aplicação multi-plataforma pode contribuir com o gerenciamento e realização de tarefas operacionais presentes no trasporte de passageiros para rede estadual hospitalar? 

### 2.3 Usuários previstos e necessidades hipotéticas

| Perfil | Necessidade a validar | Demonstração existente no protótipo |
| --- | --- | --- |
| Passageiro | Consultar informações da própria viagem, identificar informações pública sobre o veículo, o responsável e o destino final | Consulta de viagem com credenciais sintéticas de demonstração, e verificar o rastreamento e posicionamento veicular |
| Motorista | Consultar escala de locais e passageiros, emitir notificação sobre posicionamento e registrar eventos | Fluxo de operação com identificação autorizada, confirmação de atividades e comunicação com operadores |
| Gestor | Acompanhar viagens, emitir notificações, registrar autorizações e indicadores | Painel administrativo com dados sintéticos |

### 2.4 Proposta de valor — hipótese

Oferecer um ponto de consulta e acompanhamento da operação, com potencial para facilitar, agilizar e organizar a comunicação entre passageiros, motoristas e equipe de gestão.

### 2.5 Estado atual e limites

O repositório contém uma API FastAPI, uma PWA, fluxos para os perfis acima, indicadores, dados sintéticos, documentação e verificações automatizadas. Isso demonstra uma base técnica executável em ambiente de demonstração. Não comprova prontidão para produção, adequação jurídica, segurança operacional completa, usabilidade validada ou eficácia em uma operação real.

O protótipo não operará com dados reais de pacientes ou de operação sem uma avaliação e preparação separadas. As limitações notificadas estão previstas e registradas em artefatos documentáveis:
- [`SECURITY.md`](../SECURITY.md) (restrições, permissões e medidas limitantes por acordos e termos consentidos)

### 2.6 Próxima entrega de produto sugerida

Preparar um piloto **demonstrativo, isolado e reproduzível**, com dados exclusivamente sintéticos, capaz de percorrer uma jornada completa: configurar uma viagem fictícia, consultar informações do veículo e do responsável, visualizar o registro de passageiros, notificar rastreamento simultâneo entre trajetos, efetuar atividades práticas de embarque/desembarque, simular o início e fim de viagem, emitir alertas sobre o posicionamento de passageiros, projetar painel visual para coleta de informações aos gestores e acompanhar orientações gerenciais.

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

### 3.1 Resolução de pendências
 
Esta seção abrange a identificação e o compartilhamento de informações para complementar e solucionar questões regulatórias pendentes neste projeto.   

| ID | Questão pendente | Validação necessária / evidência de conclusão | Responsável a designar | Impacto potencial |
| --- | --- | --- | --- | --- |
| SRP-01 | Papéis das partes e finalidade do tratamento | Identificar quem determinaria as finalidades e os meios do tratamento, eventuais operadores e as responsabilidades de cada parte. Registrar decisão aprovada | Autoridades Responsáveis, Contratantes, Operadores, Equipe Técnica e Equipe Júridica | Contratos, permissões, operações e documentações |
| SRP-02 | Base legal e dados tratados | Avaliar as categorias de dados, finalidades e bases aplicáveis ao contexto concreto. Obter decisão documentada do controlador com apoio jurídico | Autoridades Responsáveis, Contratantes, Operadores, Equipe Técnica e Equipe Júridica | Coleta, autenticação, retenção e fluxos do produto |
| SRP-03 | ROPA e transparência | Validar operações, titulares, dados, destinatários, prazos e informações a apresentar às pessoas; aprovar os registros e avisos pertinentes | Operadores e Equipe Técnica | Telas, avisos de privacidade, processos e contratos |
| SRP-04 | Avaliação de impacto | Determinar, com as pessoas responsáveis, a avaliação de impacto necessária para dados de saúde inferidos e localização; registrar medidas, riscos e aprovação | Autoridades Responsáveis, Contratantes, Equipe Técnica | Arquitetura, minimização, acesso e mitigação de riscos |
| SRP-05 | Direitos e solicitações de titulares | Definir canais, verificação de identidade, responsáveis, prazos e fluxos para solicitações aplicáveis; Comprovar o procedimento em teste ou evidência operacional | Operadores e Equipe Técnica | Processos administrativos e funcionalidades futuras |
| SRP-06 | Retenção, expurgo e preservação | Aprovar prazos por categoria de dados e regras de exceção; demonstrar expurgo verificável em banco, backups e dados derivados | Equipe Técnica | Modelo de dados, tarefas agendadas, backups e analytics |
| SRP-07 | Encarregado e canal de contato | Confirmar a necessidade, designação e forma de publicação de um canal de contato adequado antes de eventual operação | Autoridades Responsáveis e Contratantes  | Avisos, atendimento e resposta a solicitações |
| SRP-08 | Contratos e compartilhamento | Identificar destinatários e fornecedores; revisar responsabilidades, instruções, segurança, incidentes, retenção e encerramento nos acordos pertinentes | Autoridades Responsáveis e Contratantes | Integrações, hospedagem, suporte e operação |
| SRP-09 | Incidentes e comunicações | Definir responsáveis, avaliação, contenção, preservação de evidências e processo de decisão sobre comunicações; realizar exercício documentado | Operadores e Equipe Técnica | Operação, monitoramento e resposta a incidentes |
| SRP-10| Publicação e apresentação do projeto | Revisar nome, avisos, evidências anonimizadas, licenças e declarações de independência; confirmar que a comunicação não sugere vínculo ou validação inexistente | Autoridades Responsáveis, Contratante e Equipe Técnica | README, demonstração, materiais públicos e distribuição |

### 3.2 Modelo de acompanhamento por pendência

Para cada linha do registro, mantenha uma _note_ ou _issue_ com os campos abaixo. Não registre dados pessoais ou informações confidenciais desnecessárias no repositório público.

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
| 2026-11-02 | Criação do rascunho inicial de brief e registro de pendências | Douglas Masuzzo Brasilio |
| 2026-11-03 | Desenvolvimento e definição de elementos pendentes | Douglas Masuzzo Brasilio |

