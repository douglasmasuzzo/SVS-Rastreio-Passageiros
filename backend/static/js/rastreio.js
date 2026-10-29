/* Rastreamento público por placa. */
(() => {
  "use strict";

  const { api, el, fmtDataHora, fmtIdade, fmtKm, fmtNumero, normalizarPlaca, pill, toast } = SVS;

  const listaEl = document.getElementById("lista-veiculos");
  const painelVazio = document.getElementById("painel-vazio");
  const painelConteudo = document.getElementById("painel-conteudo");
  const form = document.getElementById("form-busca");
  const inputPlaca = document.getElementById("placa");

  let selecionado = null;
  let veiculoAtual = null;
  let mapa = null;
  let camada = null;
  let mapaTentado = false;
  let ajustarMapa = true;
  let usuario = null;
  let timer = null;

  const ROTULOS_STATUS = {
    PLANEJADA: "Planejada",
    AUTORIZADA: "Autorizada",
    EM_ANDAMENTO: "Em andamento",
    CONCLUIDA: "Concluída",
    CANCELADA: "Cancelada",
  };

  const refs = {};

  function montarEsqueleto() {
    refs.placa = el("h2", { id: "det-placa" });
    refs.meta = el("p", { class: "miudo", id: "det-meta" });
    refs.status = el("div", { id: "det-status" });
    refs.dados = el("dl", { class: "dados", id: "det-dados" });
    refs.mapa = el("div", {
      id: "mapa",
      role: "region",
      "aria-label": "Mapa com a posição do veículo",
    });
    refs.notaMapa = el("p", { class: "miudo", id: "det-mapa-nota" });
    refs.viagens = el("div", { id: "det-viagens" });
    refs.acoes = el("div", { class: "acoes", id: "det-acoes" });

    painelConteudo.replaceChildren(
      el(
        "div",
        { class: "card-cabecalho" },
        el("div", { class: "cresce" }, refs.placa, refs.meta),
        refs.status,
      ),
      refs.dados,
      refs.mapa,
      refs.notaMapa,
      el("h3", { style: "margin-top:1rem" }, "Viagens de hoje"),
      refs.viagens,
      refs.acoes,
    );
  }

  function dado(rotulo, valor, complemento) {
    return el(
      "div",
      { class: "dado" },
      el("dt", { text: rotulo }),
      el(
        "dd",
        {},
        valor,
        complemento ? el("small", { text: complemento }) : null,
      ),
    );
  }

  function garantirMapa() {
    if (mapa || mapaTentado) return mapa;
    mapaTentado = true;
    mapa = SVS.criarMapa("mapa");
    if (mapa) camada = SVS.camadaVeiculo(mapa);
    return mapa;
  }

  function atualizarMapa(posicao, trilha) {
    if (!garantirMapa()) {
      refs.notaMapa.textContent =
        "Mapa interativo indisponível; use as coordenadas para abrir no OpenStreetMap.";
      return;
    }
    const pontos = (trilha || []).map((p) => [p.latitude, p.longitude]);
    camada.trilha.setLatLngs(pontos);

    if (posicao) {
      camada.marcador.setLatLng([posicao.latitude, posicao.longitude]);
      camada.marcador.setStyle({ opacity: 1, fillOpacity: 0.9 });
      camada.marcador.bindTooltip(
        `${veiculoAtual.placa} · ${fmtNumero(posicao.velocidade_kmh)} km/h`,
        { permanent: false },
      );
    } else {
      camada.marcador.setStyle({ opacity: 0, fillOpacity: 0 });
    }

    if (usuario) {
      camada.usuario.setLatLng(usuario).addTo(mapa);
    } else {
      camada.usuario.remove();
    }

    if (ajustarMapa) {
      const limites = L.latLngBounds(pontos);
      if (posicao) limites.extend([posicao.latitude, posicao.longitude]);
      if (usuario) limites.extend(usuario);
      if (limites.isValid()) {
        mapa.fitBounds(limites, { padding: [28, 28], maxZoom: 14 });
        ajustarMapa = false;
      }
    }
  }

  function renderizarViagens(resumo) {
    if (!resumo.viagens.length) {
      refs.viagens.replaceChildren(
        el(
          "div",
          { class: "vazio" },
          el("strong", {}, "Nenhuma viagem registrada para hoje"),
          "A operação ainda não publicou escala para esta placa.",
        ),
      );
      return;
    }
    const linhas = resumo.viagens.map((viagem) =>
      el(
        "tr",
        {},
        el("td", { class: "num", text: fmtDataHora(viagem.partida_prevista).split(" ")[1] || fmtDataHora(viagem.partida_prevista) }),
        el("td", { text: viagem.destino }),
        el("td", {}, el("span", { class: `pill ${viagem.status === "EM_ANDAMENTO" ? "pill-on" : "pill-off"}`, text: ROTULOS_STATUS[viagem.status] || viagem.status })),
        el("td", { class: "num", text: fmtNumero(viagem.autorizacoes) }),
      ),
    );

    refs.viagens.replaceChildren(
      el(
        "div",
        { class: "tabela-envoltorio" },
        el(
          "table",
          {},
          el(
            "thead",
            {},
            el(
              "tr",
              {},
              el("th", { scope: "col", text: "Partida" }),
              el("th", { scope: "col", text: "Destino" }),
              el("th", { scope: "col", text: "Status" }),
              el("th", { scope: "col", text: "Autorizações" }),
            ),
          ),
          el("tbody", {}, ...linhas),
        ),
      ),
      el(
        "p",
        { class: "miudo", style: "margin-top:.6rem" },
        `Total de autorizações municipais aprovadas hoje: ${fmtNumero(resumo.total_autorizacoes)}.`,
      ),
    );
  }

  function renderizar(veiculo, trilha, resumo) {
    veiculoAtual = veiculo;
    painelVazio.classList.add("oculto");
    painelConteudo.classList.remove("oculto");

    refs.placa.textContent = `${veiculo.placa} · ${veiculo.modelo}`;
    refs.meta.textContent = `${veiculo.operadora} · ${veiculo.tipo}${veiculo.acessivel ? " · acessível" : ""}`;
    refs.status.replaceChildren(
      pill(veiculo.online),
      el("div", { class: "miudo", style: "margin-top:.35rem;text-align:right" }, fmtIdade(veiculo.idade_segundos)),
    );

    const posicao = veiculo.posicao;
    const distancia = posicao ? posicao.distancia_ate_voce_km : null;
    refs.dados.replaceChildren(
      dado("Velocidade", posicao ? `${fmtNumero(posicao.velocidade_kmh)} km/h` : "—"),
      dado("Distância até você", fmtKm(distancia), usuario ? null : "ative sua localização"),
      dado(
        "Precisão do GPS",
        posicao ? `${fmtNumero(posicao.precisao_m)} m` : "—",
        posicao && posicao.posicao_aproximada ? "posição aproximada" : null,
      ),
      dado("Última posição", posicao ? fmtDataHora(posicao.capturada_em) : "sem registro"),
    );

    if (posicao) {
      refs.notaMapa.textContent =
        "Posição aproximada, arredondada para ~11 m. A trilha cobre as últimas 12 horas.";
    } else {
      refs.notaMapa.textContent =
        "Este veículo não enviou posição recente. O status permanece offline até nova telemetria.";
    }

    atualizarMapa(posicao, trilha);
    renderizarViagens(resumo);

    const acoes = [
      el(
        "button",
        { class: "botao secundario pequeno", type: "button", onclick: () => carregar() },
        "Atualizar agora",
      ),
      el(
        "button",
        { class: "botao secundario pequeno", type: "button", onclick: usarLocalizacao },
        "Usar minha localização",
      ),
      el("a", { class: "botao secundario pequeno", href: "/paciente.html" }, "Consultar minha viagem"),
    ];
    if (posicao) {
      acoes.push(
        el(
          "a",
          {
            class: "botao secundario pequeno",
            href: `https://www.openstreetmap.org/?mlat=${posicao.latitude}&mlon=${posicao.longitude}#map=15/${posicao.latitude}/${posicao.longitude}`,
            target: "_blank",
            rel: "noopener",
          },
          "Abrir no OpenStreetMap",
        ),
      );
    }
    refs.acoes.replaceChildren(...acoes);
  }

  function usarLocalizacao() {
    if (!navigator.geolocation) {
      toast("Geolocalização indisponível neste navegador.", "erro");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (posicao) => {
        usuario = [posicao.coords.latitude, posicao.coords.longitude];
        toast("Localização obtida. Calculando distância.");
        carregar();
      },
      () => toast("Não foi possível obter sua localização.", "erro"),
      { enableHighAccuracy: true, timeout: 8000, maximumAge: 30000 },
    );
  }

  async function carregar(opcoes = {}) {
    if (!selecionado) return;
    const consulta = usuario ? `?lat=${usuario[0]}&lon=${usuario[1]}` : "";
    try {
      const [veiculo, trilha, resumo] = await Promise.all([
        api(`/publico/veiculos/${selecionado}${consulta}`),
        api(`/publico/veiculos/${selecionado}/trilha?limite=60`),
        api(`/publico/veiculos/${selecionado}/viagens`),
      ]);
      renderizar(veiculo, trilha.pontos, resumo);
    } catch (erro) {
      if (!opcoes.silencioso) {
        painelVazio.classList.remove("oculto");
        painelConteudo.classList.add("oculto");
        painelVazio.replaceChildren(
          el("strong", {}, "Veículo não encontrado"),
          "Confira a placa informada. A mensagem é a mesma para placa inválida ou inexistente.",
        );
        toast(erro.message, "erro");
      }
    }
  }

  function marcarSelecionado() {
    listaEl.querySelectorAll("button[data-placa]").forEach((botao) => {
      botao.setAttribute("aria-pressed", String(botao.dataset.placa === selecionado));
    });
  }

  async function selecionar(placa, opcoes = {}) {
    const normalizada = normalizarPlaca(placa);
    if (normalizada.length !== 7) {
      toast("Informe uma placa com 7 caracteres.", "erro");
      return;
    }
    selecionado = normalizada;
    inputPlaca.value = normalizada;
    ajustarMapa = true;
    if (!opcoes.silencioso) {
      history.replaceState(null, "", `/?placa=${normalizada}`);
    }
    marcarSelecionado();
    await carregar();

    if (!timer) {
      timer = setInterval(() => {
        if (!selecionado) return;
        carregar({ silencioso: true });
        carregarFrota();
      }, 15000);
    }
  }

  function renderizarLista(veiculos) {
    listaEl.setAttribute("aria-busy", "false");
    if (!veiculos.length) {
      listaEl.replaceChildren(el("li", { class: "vazio" }, "Nenhum veículo ativo no momento."));
      return;
    }
    listaEl.replaceChildren(
      ...veiculos.map((veiculo) =>
        el(
          "li",
          {},
          el(
            "button",
            {
              type: "button",
              "data-placa": veiculo.placa,
              "aria-pressed": String(veiculo.placa === selecionado),
              onclick: () => selecionar(veiculo.placa),
            },
            el(
              "span",
              { class: "cresce" },
              el("span", { class: "placa", text: veiculo.placa }),
              el("span", { class: "meta", text: `${veiculo.modelo} · ${veiculo.operadora}` }),
            ),
            el(
              "span",
              { class: "fim" },
              pill(veiculo.online),
              el("span", { class: "meta", text: fmtIdade(veiculo.idade_segundos) }),
            ),
          ),
        ),
      ),
    );
  }

  async function carregarFrota() {
    try {
      const dados = await api("/publico/veiculos");
      renderizarLista(dados.veiculos);
    } catch (erro) {
      listaEl.setAttribute("aria-busy", "false");
      listaEl.replaceChildren(
        el(
          "li",
          { class: "vazio" },
          el("strong", {}, "Não foi possível carregar a frota"),
          erro.message,
        ),
      );
    }
  }

  form.addEventListener("submit", (evento) => {
    evento.preventDefault();
    selecionar(inputPlaca.value);
  });

  inputPlaca.addEventListener("input", () => {
    inputPlaca.value = normalizarPlaca(inputPlaca.value);
  });

  document.getElementById("sugestoes").addEventListener("click", (evento) => {
    const botao = evento.target.closest("button[data-placa]");
    if (botao) selecionar(botao.dataset.placa);
  });

  montarEsqueleto();
  carregarFrota();

  const inicial = SVS.lerParametro("placa");
  if (inicial) {
    selecionar(inicial, { silencioso: true });
  }
})();
