# 11 — Ética e conformidade

## 1. Finalidade

Este documento registra as decisões éticas, legais e de conformidade que
sustentam o trabalho. Ele não substitui parecer jurídico nem aprovação de
Comitê de Ética em Pesquisa (CEP); organiza o raciocínio, os limites e as
evidências para que essa avaliação seja possível.

O projeto tem três compromissos não negociáveis:

1. **Não usar dados reais de pacientes** no protótipo, em testes ou em
   exemplos.
2. **Não identificar** o sistema observado, seus fornecedores, operadores ou
   municípios nas evidências publicadas.
3. **Não reproduzir** código, marca, layout ou ativo do sistema original.

## 2. Natureza da pesquisa

| Aspecto | Decisão |
| --- | --- |
| Tipo | Pesquisa aplicada, qualitativa, exploratória, com desenvolvimento tecnológico |
| Objeto | Comportamento observável de um sistema em uso, por capturas de tela |
| Participantes | Nenhum ser humano recrutado; nenhum dado pessoal coletado |
| Dados | 100% sintéticos, gerados por seed determinístico |
| Risco aos participantes | Inexistente no protótipo; risco de reidentificação tratado nas evidências |
| Benefício esperado | Método reprodutível e artefato de referência para políticas públicas |

Como não há coleta de dados pessoais nem intervenção com seres humanos, a
pesquisa pode ser enquadrada como de risco mínimo ou dispensada de registro no
CEP, conforme avaliação da instituição. Ainda assim, o protocolo abaixo é
mantido para transparência.

## 3. Protocolo de ética em pesquisa

### 3.1 Princípios

- **Autonomia:** nenhuma pessoa foi exposta a risco ou abordada sem
  consentimento.
- **Beneficência:** o resultado é um artefato de referência e um método
  auditável.
- **Não maleficência:** nenhuma informação publicada permite identificar
  pacientes, motoristas, operadores ou o sistema observado.
- **Justiça:** o acesso ao conhecimento é aberto e o custo de execução é baixo.
- **Transparência:** limitações, hipóteses e riscos são declarados.

### 3.2 Alinhamento às resoluções CNS

| Resolução | Exigência | Como o trabalho atende |
| --- | --- | --- |
| CNS nº 466/2012 | Consentimento, confidencialidade, benefícios e riscos | Sem participantes; dados sintéticos; riscos declarados |
| CNS nº 510/2016 | Pesquisas em Ciências Humanas e Sociais | Método documentado; evidências anonimizadas |

### 3.3 O que não foi feito

- Nenhum acesso a conta, painel, banco, API interna ou infraestrutura.
- Nenhuma varredura de endpoints, *fuzzing* em sistema de terceiros ou
  tentativa de contornar autenticação.
- Nenhuma captura de tráfego, interceptação ou engenharia social.
- Nenhum contato com pacientes, motoristas ou gestores para obter dados.
- Nenhum uso de dados reais em treinamento, demonstração ou teste.

## 4. Clean-room e propriedade intelectual

### 4.1 Declaração

O protótipo foi desenvolvido em regime **clean-room**: a equipe que implementou
não teve acesso a código-fonte, binários, banco de dados, contratos ou
documentação interna do sistema observado. O ponto de partida foram capturas de
tela públicas/fornecidas no contexto acadêmico e conhecimento geral do domínio.

### 4.2 Regras aplicadas

1. Nenhum trecho de código, texto, ícone, layout ou marca foi copiado.
2. Nomes de endpoints, campos e tabelas foram definidos a partir dos requisitos,
   não reproduzidos de URLs observadas.
3. A identidade visual é original e neutra.
4. O sistema observado não é nomeado; usa-se “sistema observado”.
5. As evidências são cópias anonimizadas, não os originais.

### 4.3 Limites da proteção

Engenharia reversa de comportamento observável é, em regra, lícita para fins
acadêmicos e de interoperabilidade, mas a análise jurídica depende de
jurisdição, contrato de acesso e finalidade. Este projeto não afirma que
qualquer uso específico esteja autorizado; recomenda parecer jurídico antes de
qualquer publicação que identifique o sistema ou seus operadores.

## 5. Proteção de dados e LGPD

### 5.1 Papéis

| Papel | Quem é | Observação |
| --- | --- | --- |
| Controlador | Órgão público de saúde | Define finalidade e base legal |
| Operador | Equipe de TI/fornecedor | Trata dados em nome do controlador |
| Encarregado (DPO) | Designado pelo controlador | Canal com titulares e ANPD |
| Titular | Paciente/acompanhante | Direitos do art. 18 da LGPD |

No protótipo acadêmico não há controlador real nem tratamento de dados
pessoais. A tabela serve de referência para implantação.

### 5.2 Bases legais propostas

| Tratamento | Base legal proposta | Fundamento |
| --- | --- | --- |
| Autorização e execução do transporte | Execução de políticas públicas de saúde | LGPD, art. 7º, III |
| Dados de saúde e localização | Tutela da saúde | LGPD, art. 11, II, f |
| Comunicação ao paciente | Execução de política pública | LGPD, art. 7º, III |
| Auditoria e segurança | Cumprimento de obrigação legal/regulatória e legítimo interesse | LGPD, art. 7º, II e IX |
| Analytics agregado | Anonimização/agregação | LGPD, art. 12 |

A base legal definitiva depende de parecer do controlador e da natureza do
serviço. O protótipo não coleta consentimento porque não trata dados reais; em
produção, o consentimento não deve ser usado como base genérica quando existe
política pública aplicável.

### 5.3 Princípios aplicados

| Princípio | Implementação |
| --- | --- |
| Finalidade | Consulta pública de posição; consulta do titular; operação; gestão |
| Adequação | Cada endpoint expõe apenas o necessário para sua finalidade |
| Necessidade | Posição arredondada, trilha de 12 h, histórico de 180 dias |
| Transparência | Página “Sobre”, aviso de privacidade e documentação |
| Segurança | HMAC, segundo fator, rate limit, auditoria, segregação de chaves |
| Prevenção | Minimização desde o contrato; erros genéricos; sem CPF em log |
| Responsabilização | ROPA, auditoria, ADRs e riscos residuais |

### 5.4 Direitos do titular

| Direito | Como atender |
| --- | --- |
| Confirmação e acesso | Consulta autenticada do paciente |
| Correção | Fluxo administrativo com registro de auditoria |
| Eliminação | Expurgo conforme temporalidade (roadmap I7) |
| Portabilidade | Exportação estruturada sob solicitação |
| Informação sobre compartilhamento | ROPA e política de privacidade |
| Revogação de consentimento | Aplicável apenas quando a base for consentimento |

O protótipo implementa acesso e correção parcial; eliminação automatizada e
portabilidade estão no roadmap. Nenhum direito é atendido por telefone sem
verificação de identidade.

### 5.5 Retenção proposta

| Dado | Retenção | Justificativa |
| --- | --- | --- |
| Posição bruta | 90 dias | Operação e contestação |
| Trilha pública | 12 horas | Finalidade de acompanhamento |
| Histórico do paciente | 180 dias na consulta | Minimização; base legal a definir |
| Autorizações e viagens | 5 anos | Prestação de contas pública |
| Auditoria | 5 anos | Responsabilização |
| Logs de aplicação | 30 dias | Segurança |

Prazos são propostas sujeitas a parecer jurídico e à tabela de temporalidade do
órgão. O importante é que existam, sejam documentados e sejam executáveis.

## 6. Anonimização das evidências

### 6.1 Procedimento

1. Originais mantidos fora do repositório, em diretório temporário.
2. Tarjas opacas sobre CPF, nomes, placas, telefones, e-mails e operadoras.
3. Exportação em PNG, sem metadados sensíveis.
4. Cálculo de SHA-256 e registro em `reverse-engineering/evidencias/manifesto.json`.
5. Conferência por OCR auxiliar para verificar ausência de texto sensível.
6. Descarte dos originais ao final do trabalho.

### 6.2 Limitações

Tarjas opacas reduzem, mas não eliminam, risco de reidentificação por contexto
(por exemplo, combinação de horário, trajeto e unidade). Por isso:

- as evidências não incluem nome de município, unidade ou operadora;
- o manifesto não registra a origem nominal;
- a publicação deve ser avaliada pelo orientador e, se necessário, pelo CEP;
- imagens não são usadas para treinar modelos ou alimentar serviços.

### 6.3 Verificação

O script `scripts/redact_evidencias.py` documenta as regiões tarjadas. A
conferência por OCR é auxiliar e não substitui revisão humana. O manifesto
contém hashes para detectar alteração posterior.

## 7. Segurança da informação

| Controle | Estado no protótipo | Produção |
| --- | --- | --- |
| Gestão de segredos | `.env` e padrões de dev | Cofre de segredos e rotação |
| Controle de acesso | Chaves e token HMAC | OIDC, MFA, RBAC |
| Criptografia em trânsito | HTTPS no proxy | TLS 1.2+, HSTS |
| Criptografia em repouso | Não aplicável ao SQLite de demo | Disco/banco criptografado |
| Backup | Não automatizado | Diário, testado, retido |
| Monitoramento | Auditoria e healthz | Métricas, alertas, tracing |
| Resposta a incidentes | `SECURITY.md` | Plano formal e comunicação à ANPD |
| Terceiros | Nenhum | Contrato de tratamento e due diligence |

A ausência de criptografia em repouso no protótipo é aceitável apenas porque os
dados são sintéticos. Com dados reais, é requisito obrigatório.

## 8. Uso responsável de IA e automação

O projeto pode usar ferramentas de IA para apoio à redação, revisão e geração de
código. Regras:

- nenhuma ferramenta recebe dados pessoais reais;
- código gerado é revisado, testado e compreendido pelo autor;
- referências são verificadas na fonte;
- a responsabilidade intelectual e acadêmica é humana;
- o uso de IA é declarado conforme as normas da instituição.

O protótipo não toma decisões clínicas, de regulação ou de elegibilidade. Toda
decisão sensível permanece humana e auditável.

## 9. Conflitos de interesse e financiamento

Não há vínculo com o fornecedor do sistema observado, com o órgão que o utiliza
ou com concorrentes. Não há financiamento privado condicionado a resultados. Se
houver bolsa ou apoio institucional, deve ser declarado nos agradecimentos.

## 10. Licenciamento e uso

O código e a documentação são disponibilizados para uso acadêmico e
educacional, sem garantia, conforme `NOTICE.md`. É proibido:

- usar o protótipo com dados pessoais reais sem adequação legal e técnica;
- apresentar o artefato como o sistema original ou como produto homologado;
- remover avisos de originalidade e limitações;
- usar marcas de terceiros para sugerir endosso.

## 11. Checklist de conformidade

### 11.1 Para o TCC

- [x] Dados 100% sintéticos.
- [x] Evidências anonimizadas com manifesto e hashes.
- [x] Nenhum original versionado.
- [x] Sistema observado não identificado.
- [x] Código e texto originais (clean-room).
- [x] Limitações e riscos declarados.
- [x] Referências verificáveis.
- [ ] Parecer do orientador/instituição sobre CEP.
- [ ] Declaração de uso de IA conforme normas locais.

### 11.2 Antes de qualquer piloto com dados reais

- [ ] Parecer jurídico sobre base legal e papéis.
- [ ] DPIA concluída e aprovada.
- [ ] ROPA publicada internamente.
- [ ] Encarregado designado e canal divulgado.
- [ ] Contrato de tratamento com operadores.
- [ ] Retenção e expurgo automatizados.
- [ ] Criptografia em trânsito e repouso.
- [ ] Gestão de identidade com MFA e menor privilégio.
- [ ] Backup testado e plano de continuidade.
- [ ] Monitoramento, alertas e resposta a incidentes.
- [ ] Teste de carga e de segurança independente.
- [ ] Treinamento de operadores e motoristas.
- [ ] Canal de direitos do titular e prazo definido.
- [ ] Revisão de acessibilidade e de linguagem.

## 12. Contato e responsabilidade

Dúvidas éticas, pedidos de remoção de conteúdo ou relatos de vulnerabilidade
devem ser encaminhados ao autor e ao orientador pelo canal institucional. Falhas
de segurança seguem `SECURITY.md`; questões de dados seguem o encarregado do
órgão competente, quando houver.

A responsabilidade por uso indevido do artefato é de quem o implanta. O
protótipo é uma referência técnica e acadêmica, não um produto certificado.
