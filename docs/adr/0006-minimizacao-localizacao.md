# ADR 0006 — Minimização de localização no endpoint público

- **Status:** aceito
- **Data:** 2026-10-29
- **Decisores:** autor do TCC
- **Relacionados:** `backend/app/services/geo.py`, `docs/07-seguranca-lgpd.md`, achado A-05

## Contexto

O sistema observado exibe posição, velocidade e precisão de veículos de saúde em
um mapa. Localização de um veículo que transporta pacientes pode revelar
indiretamente quem embarcou, onde mora e quando acessa tratamento. A utilidade
pública de saber “o veículo está chegando” não exige precisão de metros nem
histórico ilimitado.

As alternativas foram: expor a posição exata, arredondar coordenadas, aplicar
ruído geoespacial e não expor posição pública.

## Decisão

Expor no endpoint público apenas uma **posição aproximada**:

- coordenadas arredondadas para 4 casas decimais (~11 m no equador);
- campo explícito `posicao_aproximada: true`;
- velocidade e precisão arredondadas ou omitidas quando não essenciais;
- trilha limitada às **últimas 12 horas** e a **200 pontos**;
- status `ONLINE` apenas se houver posição nos últimos 300 segundos, com limite
  configurável por `SVS_ONLINE_WINDOW_SECONDS`.

A distância até o usuário é calculada a partir da posição arredondada, com
Haversine, e não é persistida.

## Justificativa

1. **Necessidade** — para acompanhar a chegada, 11 m são suficientes; precisão
   submétrica não agrega valor ao cidadão.
2. **Proporcionalidade** — reduz a capacidade de inferir endereço exato de
   pacientes e de reconstruir rotinas.
3. **Simplicidade técnica** — arredondamento é determinístico, testável e não
   exige biblioteca geoespacial.
4. **Transparência** — o campo `posicao_aproximada` informa o limite ao cliente,
   em vez de simular precisão inexistente.
5. **Retenção** — a janela de 12 h limita a reconstrução histórica pública.

## Consequências

### Positivas

- Redução de risco de vigilância e *stalking*.
- Nenhum dado pessoal de paciente no endpoint público.
- Teste objetivo: coordenadas com no máximo 4 casas.
- Trilha previsível e limitada.

### Negativas

- A posição pode parecer “imprecisa” para quem espera o veículo na esquina.
- Arredondamento não impede correlação com outras fontes (risco residual).
- O detalhe administrativo continua com telemetria bruta; a minimização é
  apenas pública.
- 12 h ainda permitem inferir padrões de turno.

### Mitigações

- Exibir idade da última atualização e status para calibrar expectativa.
- Rate limit no público para dificultar coleta massiva.
- Auditoria de exportações administrativas.
- Roadmap I7: agregação e expurgo; avaliação de ruído geoespacial em pesquisa.

## Alternativas descartadas

| Alternativa | Motivo do descarte |
| --- | --- |
| Posição exata | Risco desproporcional e desnecessário à finalidade |
| Não expor posição | Esvazia a utilidade principal do serviço |
| Ruído aleatório | Dificulta testes e pode produzir trajetórias incoerentes |
| Grade geográfica (geohash) | Menos intuitiva para o cidadão; arredondamento é suficiente |
| Posição apenas para o paciente autenticado | Exclui o cidadão sem cadastro, que é o caso de uso central |

## Critérios de reversão

Reavaliar apenas com estudo de necessidade e base legal específicos. Se a
operação exigir posição exata para o cidadão, limitar a um raio de proximidade,
exigir contexto de emergência e documentar a mudança em nova ADR.

## Referências

- `backend/app/services/geo.py`
- `backend/app/services/tracking.py`
- `tests/test_publico.py`
- `docs/02-dossie-engenharia-reversa.md` — A-05
