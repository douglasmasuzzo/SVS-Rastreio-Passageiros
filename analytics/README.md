# Análise logística — trilha CRISP-DM

Este diretório organiza a leitura analítica da operação simulada pelo protótipo.
O objetivo é demonstrar como os dados de rastreio se convertem em indicadores de
gestão, sem transformar o TCC em um exercício de *machine learning* sobre dados
sintéticos.

> **Aviso.** Todos os dados são sintéticos. Os números servem para demonstrar o
> método e reconciliar as fórmulas, não para inferir desempenho de municípios
> reais. Nenhuma informação pessoal é necessária para os indicadores.

## 1. Estrutura

```text
analytics/
  README.md
  src/
    indicadores.py          # CLI sem dependências externas
  notebooks/
    01-analise-exploratoria.ipynb
    02-indicadores-operacionais.ipynb
  saida/                    # gerada localmente, fora do versionamento
```

## 2. Fases CRISP-DM

| Fase | Pergunta | Produto |
| --- | --- | --- |
| **Business understanding** | Como reduzir faltas, espera e ligações? | Definição de OTIF, atraso, ocupação |
| **Data understanding** | Que dados a operação gera? | Dicionário de viagens, autorizações, embarques, posições |
| **Data preparation** | Como limpar e agregar? | Recorte por data, exclusão de duplicatas, junções |
| **Modeling** | Quais indicadores respondem à pergunta? | Cálculo descritivo por data e veículo |
| **Evaluation** | Os números fazem sentido? | Reconciliação com o painel e sensibilidade |
| **Deployment** | Como reutilizar? | `indicadores.py`, CSV e notebooks |

## 3. Dicionário de dados

| Tabela | Campos usados | Uso analítico |
| --- | --- | --- |
| `viagem` | `data`, `status`, `partida_prevista`, `iniciada_em`, `concluida_em`, `veiculo_id` | Pontualidade, volume, duração |
| `veiculo` | `placa`, `capacidade`, `acessivel` | Dimensão por veículo |
| `autorizacao` | `viagem_id`, `status` | Demanda autorizada |
| `embarque` | `autorizacao_id`, `embarcado_em`, `metodo` | Comparecimento e ocupação |
| `posicao` | `veiculo_id`, `viagem_id`, `capturada_em`, `velocidade_kmh` | Distância, ociosidade, cobertura |
| `evento_viagem` | `tipo`, `ocorrido_em` | Incidentes e atrasos |

Não são usados nome, CPF, telefone, data de nascimento ou coordenada bruta. Se
houver necessidade de análise geoespacial, trabalhe com agregados por rota ou
com a telemetria pseudonimizada e sob base legal específica.

## 4. Fórmulas

Seja `T` o conjunto de viagens do dia:

- **Viagem concluída:** `status = CONCLUIDA` e `iniciada_em` preenchido.
- **Viagem pontual:** `iniciada_em <= partida_prevista + tolerância`.
- **OTIF:** `viagens pontuais / viagens concluídas × 100`.
- **Atraso (min):** `max(0, iniciada_em − partida_prevista)`.
- **Atraso médio:** média dos atrasos das viagens iniciadas.
- **Ocupação:** `embarques / autorizações aprovadas × 100`.
- **Veículo online:** posição com `capturada_em` nos últimos 300 s.

A tolerância padrão é **15 minutos**, a mesma do painel (`TOLERANCIA_OTIF_MIN`).
Ela é uma decisão de negócio, não um detalhe técnico: sem tolerância, atrasos de
segundos derrubariam o indicador e produziriam leitura equivocada.

## 5. Como executar

```bash
# a partir da raiz do repositório, com o banco de desenvolvimento já semeado
make seed
python analytics/src/indicadores.py --db data/svs.db

# uma data específica, em JSON
python analytics/src/indicadores.py --db data/svs.db --data 2026-10-29 --json

# exportar CSV
mkdir -p analytics/saida
python analytics/src/indicadores.py --db data/svs.db --csv-saida analytics/saida/indicadores.csv
```

O script é somente leitura (`mode=ro`) e usa apenas a biblioteca padrão. Para
PostgreSQL, exporte as tabelas necessárias ou adapte a conexão; o notebook
mostra o caminho com pandas/SQLAlchemy.

### Notebooks

```bash
pip install -r requirements-analytics.txt
jupyter lab analytics/notebooks
```

- `01-analise-exploratoria.ipynb` — volume por status, distribuição de atrasos,
  ocupação e qualidade dos dados.
- `02-indicadores-operacionais.ipynb` — comparação entre cálculo local e painel,
  sensibilidade da tolerância de OTIF e série por veículo.

Os notebooks não são executados no CI (dependem de dados e de Jupyter); o script
é a fonte reproduzível dos números.

## 6. Leitura dos resultados

| Pergunta | Indicador | Ação possível |
| --- | --- | --- |
| A operação é pontual? | OTIF, atraso médio | Ajustar escala, saída e tolerância |
| Os veículos estão cheios? | Ocupação | Redimensionar capacidade ou demanda |
| Há ociosidade? | Viagens × capacidade | Consolidar rotas |
| Os pacientes embarcam? | Embarques / aprovadas | Reforçar comunicação e confirmação |
| A telemetria cobre a operação? | Pontos por viagem, lacunas | Corrigir gateway/app |
| Um veículo é outlier? | OTIF e atraso por placa | Manutenção, motorista, rota |

## 7. Qualidade e limitações

- **Dados sintéticos** — o cenário é determinístico e pequeno; não há
  sazonalidade, trânsito real nem falhas de campo.
- **Amostra curta** — um dia de operação não sustenta inferência estatística.
- **Viés de seleção** — viagens só existem se foram planejadas; faltas não
  aparecem como registro próprio.
- **Sem denominador populacional** — não há dados de demanda reprimida.
- **Sem geolocalização de pacientes** — distância até o veículo não é indicador
  de acesso.
- **Sem ETA** — previsão de chegada exige histórico real e validação (I9).

## 8. Reprodutibilidade

1. Suba o sistema com `make run` ou aplique o seed.
2. Execute o script e compare com `GET /api/v1/admin/kpis`.
3. Regenera o CSV e versione apenas o código, nunca os dados.
4. Se alterar a fórmula, atualize este README, o painel e os testes.

## 9. Produto esperado

- Um CSV de indicadores por data e por veículo.
- Um gráfico de OTIF e atraso ao longo do tempo (notebook).
- Uma tabela de reconciliação painel × script.
- Um parágrafo de leitura crítica no relatório técnico (`docs/10`).

## 10. O que este diretório não faz

- Não prevê chegada (ETA), não classifica risco clínico e não ranqueia
  motoristas.
- Não usa dados pessoais nem geolocalização individual de pacientes.
- Não automatiza decisão de regulação ou de elegibilidade.
- Não substitui avaliação de política pública com dados reais e base legal.
