# Aviso de uso, originalidade e dados

## 1. Natureza do projeto

Este repositório é um **trabalho acadêmico de conclusão de curso**. Ele
apresenta uma reimplementação de referência, desenvolvida em regime de
**clean-room**, de funcionalidades observáveis em um sistema de rastreio de
transporte sanitário. O objetivo é demonstrar método de engenharia reversa,
análise logística e boas práticas de segurança e privacidade — não substituir,
competir com ou operar o sistema original.

## 2. Ausência de vínculo

O projeto **não possui vínculo** com o sistema observado, com seus
desenvolvedores, fornecedores, operadoras de transporte ou órgãos públicos
municipais/estaduais. Nomes de instituições, marcas e produtos citados
pertencem aos seus respectivos titulares e são usados apenas para contexto
descritivo. Não há endosso, patrocínio ou autorização implícita.

## 3. Clean-room

O desenvolvimento seguiu as seguintes regras:

1. **Nenhum código-fonte, binário, banco de dados, contrato interno, credencial
   ou ativo** do sistema observado foi acessado, copiado, descompilado ou
   reutilizado.
2. A análise partiu exclusivamente de **comportamento observável** em capturas
   de tela fornecidas no contexto acadêmico (telas públicas e de operação).
3. O modelo de domínio, os nomes de tabelas, os contratos de API e a interface
   foram **projetados de novo**, a partir dos requisitos descritos em
   [`docs/03-requisitos.md`](docs/03-requisitos.md).
4. Sempre que o comportamento não pôde ser observado, a decisão foi registrada
   como **hipótese** no dossiê ([`docs/02-dossie-engenharia-reversa.md`](docs/02-dossie-engenharia-reversa.md)),
   com o risco correspondente.
5. Nenhuma marca, logotipo, ícone, texto ou folha de estilo do sistema original
   foi reproduzida. A identidade visual da PWA é original.

## 4. Dados

- **Todos os dados são sintéticos.** Nomes, CPFs, placas, unidades de saúde,
  operadoras e coordenadas de exemplo foram criados para demonstração.
- Os CPFs partem da base reservada `900000xxx` e recebem dígitos verificadores
  válidos apenas para que passem pela validação algorítmica. Essa faixa foi
  escolhida por não ser emitida para pessoas naturais.
- As coordenadas de rota são aproximações de eixos viários reais usadas para dar
  plausibilidade geográfica; não representam itinerários oficiais.
- **É proibido** carregar dados reais de pacientes, motoristas ou veículos neste
  protótipo. O sistema não possui controles de produção suficientes para isso
  (ver [`SECURITY.md`](SECURITY.md)).

## 5. Evidências

As capturas originais **não são versionadas**. As cópias em
[`reverse-engineering/evidencias/`](reverse-engineering/evidencias/) passaram por
tarjas opacas para remover CPF, nomes, placas e operadoras; cada arquivo tem
hash SHA-256 registrado em `manifesto.json`. O processo é reproduzível por
[`scripts/redact_evidencias.py`](scripts/redact_evidencias.py), que exige os
originais fora do repositório.

## 6. Licenças de terceiros

O protótipo usa bibliotecas de código aberto sob suas próprias licenças:

- FastAPI, Starlette, Pydantic, SQLAlchemy, Uvicorn — MIT/BSD.
- Leaflet — BSD-2-Clause (carregado via CDN no navegador).
- pytest, httpx, Ruff — MIT/BSD/Apache-2.0.
- Fonte do sistema operacional e ícones: criações originais em SVG/PNG.

Consulte os metadados de cada pacote em `pip show <pacote>` para os textos
completos.

## 7. Uso permitido e garantias

Uso permitido para **estudo, pesquisa acadêmica, avaliação e demonstração**.
É vedado:

- operar o protótipo com dados pessoais reais;
- apresentar o protótipo como produto do sistema observado;
- remover avisos de originalidade ou atribuir autoria indevida.

O software é fornecido **“como está”**, sem garantias de qualquer natureza,
inclusive de adequação a um propósito específico. O autor não se responsabiliza
por uso indevido, danos ou violações de direitos decorrentes de modificações.

## 8. Contato

Dúvidas sobre originalidade, remoção de conteúdo ou uso acadêmico devem ser
direcionadas ao autor do trabalho, identificado no cabeçalho do repositório.
Falhas de segurança seguem o processo de [`SECURITY.md`](SECURITY.md).
