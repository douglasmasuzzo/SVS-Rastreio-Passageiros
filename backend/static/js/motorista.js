/* Área do motorista: sessão por placa + PIN, viagens, passageiros, eventos e GPS. */
(() => {
  "use strict";

  const { api, el, fmtData, fmtDataHora, fmtHora, normalizarPlaca, avatar, toast } = SVS;

  const CHAVE_TOKEN = "svs.motorista.token";
  const CHAVE_SESSAO = "svs.motorista.sessao";
  const INTERVALO_GPS_MS = 15000;

  const viewLogin = document.getElementById("view-login");
  const viewApp = document.getElementById("view-app");
  const formLogin = document.getElementById("form-login");
  const placaInput = document.getElementById("placa");
  const pinInput = document.getElementById("pin");
  const atalhos = document.getElementById("atalhos-motorista");
  const appTitulo = document.getElementById("app-titulo");
  const appVeiculo = document.getElementById("app-veiculo");
  const sessaoExpira = document.getElementById("sessao-expira");
  const dataOperacao = document.getElementById("data-operacao");
  const listaViagens = document.getElementById("lista-viagens");
  const detalheVazio = document.getElementById("detalhe-vazio");
  const detalheConteudo = document.getElementById("detalhe-conteudo");

  const ROTULOS_VIAGEM = {
    PLANEJADA: "Planejada",
    AUTORIZADA: "Autorizada",
    EM_ANDAMENTO: "Em andamento",
    CONCLUIDA: "Concluída",
    CANCELADA: "Cancelada",
  };

  const ROTULOS_TRAJETO = {
    IDA: "Somente ida",
    VOLTA: "Somente volta",
    IDA_E_VOLTA: "Ida e volta",
  };

  const ROTULOS_EVENTO = {
    CHEGADA_DESTINO: "Chegada ao destino",
    ATRASO: "Atraso",
    INCIDENTE: "Incidente",
    OBSERVACAO: "Observação",
  };

  let token = SVS.recuperar(CHAVE_TOKEN);
  let sessao = lerSessao();
  let dataAtual = hojeLocal();
  let viagens = [];
  let selecionada = null;
  let gpsAtivo = false;
  let relogioGps = null;
  let ultimoEnvio = 0;
  let enviando = false;
  let ultimaPosicao = null;

  function hojeLocal() {
    return new Date().toLocaleDateString("sv-SE", { timeZone: "America/Sao_Paulo" });
  }

  function lerSessao() {
    try {
      return JSON.parse(SVS.recuperar(CHAVE_SESSAO) || "null");
    } catch {
      return null;
    }
  }

  function primeiroNome(nome) {
    return String(nome || "Motorista").trim().split(/\s+/)[0];
  }

  function pillStatus(status) {
    const classe =
      status === "EM_ANDAMENTO"
        ? "pill-on"
        : status === "CONCLUIDA"
          ? "pill-off"
          : status === "CANCELADA"
            ? "pill-erro"
            : "pill-alerta";
    return el("span", { class: `pill ${classe}`, text: ROTULOS_VIAGEM[status] || status });
  }

  function dado(rotulo, valor, complemento) {
    return el(
      "div",
      { class: "dado" },
      el("dt", { text: rotulo }),
      el("dd", {}, valor, complemento ? el("small", { text: complemento }) : null),
    );
  }

  async function apiMotorista(caminho, opcoes = {}) {
    const cabecalhos = { ...(opcoes.headers || {}) };
    if (token) cabecalhos.Authorization = `Bearer ${token}`;
    try {
      return await api(caminho, { ...opcoes, headers: cabecalhos });
    } catch (erro) {
      if (erro.status === 401) encerrarSessao(true);
      throw erro;
    }
  }

  function mostrarApp() {
    viewLogin.hidden = true;
    viewApp.hidden = false;
    const motorista = sessao && sessao.motorista ? sessao.motorista : { nome: "Motorista" };
    const veiculo = sessao && sessao.veiculo ? sessao.veiculo : null;
    appTitulo.textContent = `Olá, ${primeiroNome(motorista.nome)}`;
    appVeiculo.textContent = veiculo
      ? `${veiculo.placa} · ${veiculo.modelo} · ${veiculo.operadora}${veiculo.acessivel ? " · acessível" : ""}`
      : "";
    sessaoExpira.textContent = sessao && sessao.expira_em
      ? `Sessão válida até ${fmtDataHora(sessao.expira_em)}. Encerrada automaticamente ao fechar o navegador.`
      : "";
    dataOperacao.value = dataAtual;
  }

  function mostrarLogin() {
    viewApp.hidden = true;
    viewLogin.hidden = false;
    detalheVazio.hidden = false;
    detalheConteudo.hidden = true;
    listaViagens.replaceChildren();
    listaViagens.setAttribute("aria-busy", "true");
    placaInput.focus();
  }

  function encerrarSessao(expirou = false) {
    pararGps(false);
    token = null;
    sessao = null;
    viagens = [];
    selecionada = null;
    SVS.apagar(CHAVE_TOKEN);
    SVS.apagar(CHAVE_SESSAO);
    mostrarLogin();
    if (expirou) toast("Sessão expirada. Entre novamente.", "erro");
  }

  function iniciarSessao(dados) {
    token = dados.token;
    sessao = {
      motorista: dados.motorista,
      veiculo: dados.veiculo,
      expira_em: dados.expira_em,
    };
    SVS.armazenar(CHAVE_TOKEN, token);
    SVS.armazenar(CHAVE_SESSAO, JSON.stringify(sessao));
    dataAtual = hojeLocal();
    mostrarApp();
    carregarViagens();
  }

  async function entrar(evento) {
    evento.preventDefault();
    const placa = normalizarPlaca(placaInput.value);
    const pin = pinInput.value.trim();
    if (!placa || placa.length !== 7) {
      toast("Informe uma placa válida com 7 caracteres.", "erro");
      placaInput.focus();
      return;
    }
    if (pin.length < 4) {
      toast("O PIN deve ter pelo menos 4 dígitos.", "erro");
      pinInput.focus();
      return;
    }
    const botao = formLogin.querySelector('button[type="submit"]');
    botao.disabled = true;
    botao.textContent = "Entrando…";
    try {
      const dados = await api("/motorista/sessao", {
        method: "POST",
        body: JSON.stringify({ placa, pin }),
      });
      pinInput.value = "";
      iniciarSessao(dados);
      toast(`Sessão iniciada para ${dados.veiculo.placa}.`);
    } catch (erro) {
      if (erro.status === 401) {
        toast("Placa ou PIN inválidos. A mensagem é a mesma para qualquer falha.", "erro");
      } else if (erro.status === 429) {
        toast("Muitas tentativas. Aguarde um minuto.", "erro");
      } else {
        toast(erro.message || "Não foi possível entrar.", "erro");
      }
    } finally {
      botao.disabled = false;
      botao.textContent = "Entrar";
    }
  }

  async function carregarViagens(opcoes = {}) {
    listaViagens.setAttribute("aria-busy", "true");
    try {
      const dados = await apiMotorista(`/motorista/viagens?data=${encodeURIComponent(dataAtual)}`);
      viagens = dados.viagens;
      if (sessao && dados.veiculo) sessao.veiculo = dados.veiculo;
      renderizarLista();
      const idDesejado = opcoes.selecionar || (selecionada && selecionada.id);
      const alvo = viagens.find((v) => v.id === idDesejado) || viagens[0] || null;
      if (alvo) selecionarViagem(alvo.id);
      else {
        selecionada = null;
        mostrarDetalheVazio("Nenhuma viagem nesta data", "A escala do veículo ainda não foi publicada.");
      }
    } catch (erro) {
      if (erro.status === 401) return;
      listaViagens.setAttribute("aria-busy", "false");
      listaViagens.replaceChildren(
        el("div", { class: "vazio" }, el("strong", {}, "Não foi possível carregar as viagens"), erro.message),
      );
    }
  }

  function renderizarLista() {
    listaViagens.setAttribute("aria-busy", "false");
    if (!viagens.length) {
      listaViagens.replaceChildren(
        el("div", { class: "vazio" }, el("strong", {}, "Sem viagens"), "Nenhuma escala para esta data."),
      );
      return;
    }
    listaViagens.replaceChildren(
      el(
        "ul",
        { class: "lista-viagens" },
        ...viagens.map((viagem) =>
          el(
            "li",
            {},
            el(
              "button",
              {
                type: "button",
                "data-id": String(viagem.id),
                "aria-pressed": String(selecionada && selecionada.id === viagem.id),
                onclick: () => selecionarViagem(viagem.id),
              },
              el(
                "span",
                { class: "hora", text: fmtHora(viagem.partida_prevista) },
              ),
              el(
                "span",
                { class: "cresce" },
                el("span", { class: "destino", text: viagem.destino }),
                el("span", { class: "meta", text: `${ROTULOS_TRAJETO[viagem.trajeto] || viagem.trajeto} · ${viagem.embarques}/${viagem.autorizacoes} embarques` }),
              ),
              el("span", { class: "fim" }, pillStatus(viagem.status)),
            ),
          ),
        ),
      ),
    );
  }

  function mostrarDetalheVazio(titulo, texto) {
    detalheVazio.hidden = false;
    detalheConteudo.hidden = true;
    detalheVazio.replaceChildren(el("strong", {}, titulo), texto);
  }

  function selecionarViagem(id) {
    const viagem = viagens.find((v) => v.id === id);
    if (!viagem) return;
    selecionada = viagem;
    renderizarLista();
    renderizarDetalhe();
    carregarPassageiros();
  }

  function renderizarDetalhe() {
    if (!selecionada) return;
    const viagem = selecionada;
    detalheVazio.hidden = true;
    detalheConteudo.hidden = false;

    const emAndamento = viagem.status === "EM_ANDAMENTO";
    const podeIniciar = viagem.status === "PLANEJADA" || viagem.status === "AUTORIZADA";
    const encerrada = viagem.status === "CONCLUIDA" || viagem.status === "CANCELADA";

    const acoes = [];
    if (podeIniciar) {
      acoes.push(
        el(
          "button",
          { class: "botao", type: "button", onclick: () => registrarEvento("INICIO") },
          "Iniciar viagem",
        ),
      );
    }
    if (emAndamento) {
      acoes.push(
        el(
          "button",
          { class: "botao secundario", type: "button", onclick: () => registrarEvento("CHEGADA_DESTINO") },
          "Registrar chegada",
        ),
        el(
          "button",
          {
            class: "botao perigo",
            type: "button",
            onclick: () => {
              if (window.confirm("Encerrar a viagem? O embarque de novos passageiros será bloqueado.")) {
                registrarEvento("FIM");
              }
            },
          },
          "Encerrar viagem",
        ),
      );
    }
    if (encerrada) {
      acoes.push(el("span", { class: "miudo", text: "Viagem encerrada — somente leitura." }));
    }

    const seletorTipo = el(
      "select",
      { id: "tipo-evento" },
      ...Object.entries(ROTULOS_EVENTO).map(([valor, rotulo]) => el("option", { value: valor }, rotulo)),
    );
    const observacao = el("textarea", {
      id: "observacao-evento",
      rows: "2",
      maxlength: "500",
      placeholder: "Descreva o atraso, incidente ou observação (opcional para chegada).",
    });
    const formEvento = el(
      "form",
      {
        class: "form-evento",
        onsubmit: (evento) => {
          evento.preventDefault();
          registrarEvento(seletorTipo.value, observacao.value.trim());
          observacao.value = "";
        },
      },
      el("div", { class: "linha" }, el("div", { class: "campo" }, el("label", { for: "tipo-evento" }, "Tipo de evento"), seletorTipo)),
      el("div", { class: "campo" }, el("label", { for: "observacao-evento" }, "Observação"), observacao),
      el("button", { class: "botao secundario pequeno", type: "submit", disabled: encerrada }, "Registrar evento"),
    );

    const gps = el(
      "div",
      { class: "gps-painel" },
      el(
        "div",
        { class: "card-cabecalho", style: "margin-bottom:.4rem" },
        el(
          "div",
          { class: "cresce" },
          el("h3", { style: "margin:0", text: "Compartilhar posição" }),
          el("p", { class: "miudo", style: "margin:0" }, "Envia GPS do aparelho a cada 15 s enquanto a viagem estiver aberta."),
        ),
        el("span", { class: gpsAtivo ? "pill pill-on" : "pill pill-off", id: "gps-pill", text: gpsAtivo ? "Ativo" : "Inativo" }),
      ),
      el(
        "div",
        { class: "acoes" },
        el(
          "button",
          { class: `botao ${gpsAtivo ? "perigo" : ""}`, type: "button", id: "btn-gps", onclick: alternarGps, disabled: encerrada },
          gpsAtivo ? "Parar compartilhamento" : "Iniciar compartilhamento",
        ),
        el(
          "button",
          { class: "botao secundario", type: "button", onclick: enviarPosicaoUnica, disabled: encerrada },
          "Enviar posição agora",
        ),
      ),
      el("p", { class: "miudo", id: "gps-status", style: "margin:.6rem 0 0" }, textoStatusGps()),
    );

    detalheConteudo.replaceChildren(
      el(
        "div",
        { class: "card-cabecalho" },
        el(
          "div",
          { class: "cresce" },
          el("span", { class: "etiqueta", text: `Viagem #${viagem.id}` }),
          el("h2", { style: "margin:.2rem 0", text: viagem.destino }),
          el("p", { class: "miudo", style: "margin:0", text: `${fmtData(viagem.data)} · ${ROTULOS_TRAJETO[viagem.trajeto] || viagem.trajeto}` }),
        ),
        pillStatus(viagem.status),
      ),
      el(
        "dl",
        { class: "dados" },
        dado("Partida prevista", fmtHora(viagem.partida_prevista), fmtData(viagem.partida_prevista)),
        dado("Retorno previsto", viagem.retorno_previsto ? fmtHora(viagem.retorno_previsto) : "—"),
        dado("Autorizações", String(viagem.autorizacoes)),
        dado("Embarques", String(viagem.embarques)),
      ),
      el("div", { class: "acoes", style: "margin-bottom:1rem" }, ...acoes),
      gps,
      el("h3", { style: "margin-top:1.2rem", text: "Registrar ocorrência" }),
      formEvento,
      el("h3", { style: "margin-top:1.2rem", text: "Passageiros autorizados" }),
      el("div", { id: "lista-passageiros", "aria-live": "polite", "aria-busy": "true" }, el("div", { class: "esqueleto" })),
    );
  }

  function textoStatusGps() {
    if (!ultimaPosicao) return "Nenhuma posição enviada nesta sessão.";
    const { quando, precisao, viagemId } = ultimaPosicao;
    return `Último envio: ${fmtDataHora(quando)} · precisão ${Math.round(precisao)} m · viagem #${viagemId}.`;
  }

  function atualizarStatusGps() {
    const alvo = document.getElementById("gps-status");
    if (alvo) alvo.textContent = textoStatusGps();
    const pill = document.getElementById("gps-pill");
    if (pill) {
      pill.textContent = gpsAtivo ? "Ativo" : "Inativo";
      pill.className = gpsAtivo ? "pill pill-on" : "pill pill-off";
    }
    const botao = document.getElementById("btn-gps");
    if (botao) {
      botao.textContent = gpsAtivo ? "Parar compartilhamento" : "Iniciar compartilhamento";
      botao.className = gpsAtivo ? "botao perigo" : "botao";
    }
  }

  async function registrarEvento(tipo, observacao) {
    if (!selecionada) return;
    if (tipo === "ATRASO" || tipo === "INCIDENTE" || tipo === "OBSERVACAO") {
      if (!observacao) {
        toast("Descreva a ocorrência antes de registrar.", "erro");
        return;
      }
    }
    try {
      await apiMotorista(`/motorista/viagens/${selecionada.id}/eventos`, {
        method: "POST",
        body: JSON.stringify({ tipo, observacao: observacao || null }),
      });
      toast(`Evento ${ROTULOS_EVENTO[tipo] || tipo} registrado.`);
      await carregarViagens({ selecionar: selecionada.id });
    } catch (erro) {
      if (erro.status !== 401) toast(erro.message || "Não foi possível registrar o evento.", "erro");
    }
  }

  function renderizarPassageiros(dados) {
    const alvo = document.getElementById("lista-passageiros");
    if (!alvo) return;
    alvo.setAttribute("aria-busy", "false");
    if (!dados.passageiros.length) {
      alvo.replaceChildren(
        el("div", { class: "vazio" }, el("strong", {}, "Nenhum passageiro autorizado"), "A central de regulação ainda não aprovou autorizações para esta viagem."),
      );
      return;
    }
    alvo.replaceChildren(
      ...dados.passageiros.map((passageiro) =>
        el(
          "div",
          { class: "passageiro" },
          avatar(passageiro.nome),
          el(
            "div",
            { class: "cresce" },
            el("div", { class: "nome", text: passageiro.nome }),
            el(
              "div",
              { class: "sub" },
              `CPF ${passageiro.cpf_mascarado}`,
              passageiro.embarque
                ? ` · embarcou ${fmtHora(passageiro.embarque.embarcado_em)} (${passageiro.embarque.metodo})`
                : " · embarque pendente",
            ),
          ),
          passageiro.embarque
            ? el("span", { class: "pill pill-on", text: "Embarcado" })
            : el(
                "button",
                {
                  class: "botao pequeno",
                  type: "button",
                  onclick: (evento) => registrarEmbarque(passageiro, evento.currentTarget),
                },
                "Check-in",
              ),
        ),
      ),
    );
  }

  async function carregarPassageiros() {
    if (!selecionada) return;
    const alvo = document.getElementById("lista-passageiros");
    if (alvo) alvo.setAttribute("aria-busy", "true");
    try {
      const dados = await apiMotorista(`/motorista/viagens/${selecionada.id}/passageiros`);
      renderizarPassageiros(dados);
    } catch (erro) {
      if (erro.status === 401) return;
      if (alvo) {
        alvo.setAttribute("aria-busy", "false");
        alvo.replaceChildren(el("div", { class: "aviso erro" }, erro.message));
      }
    }
  }

  async function registrarEmbarque(passageiro, botao) {
    if (!selecionada) return;
    botao.disabled = true;
    botao.textContent = "Registrando…";
    try {
      await apiMotorista(`/motorista/viagens/${selecionada.id}/embarques`, {
        method: "POST",
        body: JSON.stringify({ autorizacao_id: passageiro.autorizacao_id, metodo: "MANUAL" }),
      });
      toast(`Embarque de ${passageiro.nome} confirmado.`);
      await carregarViagens({ selecionar: selecionada.id });
    } catch (erro) {
      if (erro.status !== 401) toast(erro.message || "Não foi possível registrar o embarque.", "erro");
      botao.disabled = false;
      botao.textContent = "Check-in";
    }
  }

  function alternarGps() {
    if (gpsAtivo) {
      pararGps(true);
      return;
    }
    if (!navigator.geolocation) {
      toast("Geolocalização indisponível neste navegador.", "erro");
      return;
    }
    if (!selecionada) {
      toast("Selecione uma viagem antes de compartilhar a posição.", "erro");
      return;
    }
    gpsAtivo = true;
    ultimoEnvio = 0;
    atualizarStatusGps();
    relogioGps = navigator.geolocation.watchPosition(
      (posicao) => {
        const agora = Date.now();
        if (agora - ultimoEnvio < INTERVALO_GPS_MS) return;
        enviarPosicao(posicao);
      },
      (erro) => {
        if (erro.code === erro.PERMISSION_DENIED) {
          toast("Permissão de localização negada. O compartilhamento foi interrompido.", "erro");
          pararGps(false);
        } else {
          toast("Não foi possível obter o GPS. Tentando novamente.", "erro");
        }
      },
      { enableHighAccuracy: true, maximumAge: 5000, timeout: 15000 },
    );
    toast("Compartilhamento de posição iniciado.");
  }

  function pararGps(avisar) {
    if (relogioGps !== null && navigator.geolocation) {
      navigator.geolocation.clearWatch(relogioGps);
    }
    relogioGps = null;
    if (gpsAtivo && avisar) toast("Compartilhamento de posição interrompido.");
    gpsAtivo = false;
    atualizarStatusGps();
  }

  function enviarPosicaoUnica() {
    if (!navigator.geolocation) {
      toast("Geolocalização indisponível neste navegador.", "erro");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (posicao) => enviarPosicao(posicao, true),
      () => toast("Não foi possível obter a posição do aparelho.", "erro"),
      { enableHighAccuracy: true, timeout: 12000, maximumAge: 0 },
    );
  }

  async function enviarPosicao(posicao, avisar = false) {
    if (enviando || !selecionada || !sessao || !sessao.veiculo) return;
    const { coords } = posicao;
    enviando = true;
    try {
      await apiMotorista("/motorista/posicao", {
        method: "POST",
        body: JSON.stringify({
          placa: sessao.veiculo.placa,
          viagem_id: selecionada.id,
          latitude: coords.latitude,
          longitude: coords.longitude,
          velocidade_kmh: coords.speed && coords.speed > 0 ? Math.round(coords.speed * 3.6) : 0,
          rumo: coords.heading !== null && !Number.isNaN(coords.heading) ? coords.heading : null,
          precisao_m: coords.accuracy || 25,
          capturada_em: new Date(posicao.timestamp).toISOString(),
        }),
      });
      ultimoEnvio = Date.now();
      ultimaPosicao = {
        quando: new Date().toISOString(),
        precisao: coords.accuracy || 25,
        viagemId: selecionada.id,
      };
      atualizarStatusGps();
      if (avisar) toast("Posição enviada.");
    } catch (erro) {
      if (erro.status === 401) return;
      if (avisar) toast(erro.message || "Falha ao enviar a posição.", "erro");
      const alvo = document.getElementById("gps-status");
      if (alvo) alvo.textContent = `Falha no último envio: ${erro.message || "erro de rede"}.`;
    } finally {
      enviando = false;
    }
  }

  function restaurarSessao() {
    if (!token || !sessao) return false;
    const expira = sessao.expira_em ? new Date(sessao.expira_em).getTime() : 0;
    if (!expira || expira <= Date.now()) {
      encerrarSessao(true);
      return false;
    }
    mostrarApp();
    carregarViagens();
    return true;
  }

  formLogin.addEventListener("submit", entrar);

  placaInput.addEventListener("input", () => {
    placaInput.value = normalizarPlaca(placaInput.value);
  });

  atalhos.addEventListener("click", (evento) => {
    const botao = evento.target.closest("button[data-placa]");
    if (!botao) return;
    placaInput.value = botao.dataset.placa;
    pinInput.value = botao.dataset.pin;
    formLogin.requestSubmit();
  });

  dataOperacao.addEventListener("change", () => {
    dataAtual = dataOperacao.value || hojeLocal();
    selecionada = null;
    carregarViagens();
  });

  document.getElementById("btn-atualizar").addEventListener("click", () => {
    carregarViagens({ selecionar: selecionada && selecionada.id });
  });

  document.getElementById("btn-sair").addEventListener("click", () => encerrarSessao(false));

  window.addEventListener("pagehide", () => pararGps(false));

  if (!restaurarSessao()) {
    dataOperacao.value = dataAtual;
    placaInput.focus();
  }
})();
