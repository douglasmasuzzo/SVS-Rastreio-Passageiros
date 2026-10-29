# ADR 0005 — PWA vanilla sem etapa de build

- **Status:** aceito
- **Data:** 2026-10-29
- **Decisores:** autor do TCC
- **Relacionados:** `backend/static/`, ADR 0001, `docs/03-requisitos.md`

## Contexto

A interface precisa funcionar em celular, ser instalável, tolerar conectividade
instável e ser avaliável por alguém sem familiaridade com Node.js. O escopo
inclui quatro páginas (público, paciente, motorista, gestão), mapa com Leaflet e
formulários simples.

As alternativas foram: React/Vue com *bundler*, framework CSS, PWA vanilla com
JavaScript moderno e aplicativo nativo.

## Decisão

Implementar uma **PWA sem etapa de build**, com HTML semântico, CSS puro e
JavaScript ES2020 carregado como módulo. Leaflet é carregado por CDN com
*fallback* textual quando o mapa não estiver disponível. O service worker faz
cache da casca e dos ícones, sem cachear respostas de API sensíveis.

Não há `package.json`, `node_modules` ou pipeline de frontend. Os estáticos são
servidos pelo FastAPI em `/`.

## Justificativa

1. **Reprodutibilidade** — clonar e rodar `make run` é suficiente; não há
   toolchain adicional.
2. **Auditabilidade** — o código entregue ao navegador é o código do
   repositório, sem transpilação ou minificação que dificulte a revisão.
3. **Escopo pequeno** — quatro páginas e formulários não justificam a
   complexidade de um framework.
4. **Acessibilidade e semântica** — HTML nativo favorece leitores de tela,
   navegação por teclado e contraste controlado por CSS.
5. **Resiliência** — *fallback* textual garante que coordenadas e status
   continuem visíveis sem mapa ou CDN.

## Consequências

### Positivas

- Nenhuma dependência de npm, bundler ou versão de Node.
- Deploy estático trivial e cache previsível.
- Menor superfície de ataque de *supply chain* no frontend.
- Tempo de carregamento baixo em conexões ruins.

### Negativas

- Sem componentização automática; duplicação de HTML é possível.
- Sem tipagem no frontend; erros só aparecem em execução.
- Sem testes de UI automatizados no MVP.
- Leaflet via CDN depende de terceiro; o *fallback* mitiga, mas não elimina.
- Service worker mal configurado pode servir versão antiga.

### Mitigações

- `js/comum.js` centraliza utilidades (formatação, fetch, mapa, estado vazio).
- `sw.js` usa versão de cache explícita e não intercepta `/api/`.
- Revisão manual de acessibilidade e *fallback* documentada em `docs/08`.
- Roadmap I8: Playwright + axe e teste de *cache busting*.

## Alternativas descartadas

| Alternativa | Motivo do descarte |
| --- | --- |
| React/Vite | Build, dependências e complexidade sem ganho funcional |
| Vue/Alpine | Ainda exigiria dependência e build (Alpine minimiza, mas não resolve) |
| Framework CSS | CSS próprio é pequeno e suficiente |
| App nativo | Fora do escopo; duas lojas e duas bases de código |
| SPA com roteamento | Quatro páginas não exigem roteador |

## Critérios de reversão

Adotar build se: a interface crescer para dezenas de telas, houver necessidade
de componentização compartilhada entre equipes, ou testes de UI exigirem
ferramentas que dependam de módulos npm. Mesmo assim, manter a API como fonte
da verdade.

## Referências

- `backend/static/`
- `docs/03-requisitos.md` — RF-36…RF-39
- `docs/04-arquitetura.md`
