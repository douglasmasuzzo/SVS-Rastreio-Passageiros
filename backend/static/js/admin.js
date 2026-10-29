/* Painel administrativo: KPIs, viagens, autorizações e exportação CSV. */
(() => {
  "use strict";

  const { api, el, fmtData, fmtHora, fmtNumero, toast } = SVS;

  const CHAVE_ADMIN = "svs.admin.chave";
  const CHAVE_VALIDADOR = "svs.admin.validador";

  const viewLogin = document.getElementById("view-login");
  const viewApp = document.getElementById("view-app");
  const formAdmin = document.getElementById("form-admin");
  const chaveInput = document.getElementById("chave");
  const dataAdmin = document.getElementById("data-admin");
  const validadorInput = document.getElementById("validador");
  const kpis = document.getElementById("kpis");
  const tabelaViagens = document.getElementById("tabela-viagens");
  const tabelaAutorizacoes = document.getElementById("tabela-autorizacoes");
  const contagemAutorizacoes = document.getElementById("contagem-autorizacoes");
  const adminDataRotulo = document.getElementById("admin-data-rotulo");
  const exportInicio = document.getElementById("export-inicio");
  const exportFim = document.getElementById("export-fim");
  const exportStatus = document.getElementById("export-status");

  const ROTULOS_VIAGEM = {
    PLANEJADA: "Planejada",
    AUTORIZADA: "Autorizada",
    EM_ANDAMENTO: "Em andamento",
    CONCLUIDA: "Concluída",
    CANCELADA: "Cancelada",
  };

  const ROTULOS_AUTORIZACAO = {
    PENDENTE: "Pendente",
    APROVADA: "Aprovada",
    NEGADA: "Negada",
    CANCELADA: "Cancelada",
  };

  let chave = SVS.recuperar(CHAVE_ADMIN);
  let dataAtual = hojeLocal();

  function hojeLocal() {
    return new Date().toLocaleDateString("sv-SE", { timeZone: "America/Sao_Paulo" });
  }

  function diasAtras(dias) {
    const base = new Date(`${hojeLocal()}T12:00:00`);
    base.setDate(base.getDate() - dias);
    return base.toLocaleDateString("sv-SE");
  }

  async function apiAdmin(caminho, opcoes = {}) {
    const cabecalhos = { ...(opcoes.headers || {}), "X-Admin-Key": chave || "" };
    try {
      return await api(caminho, { ...opcoes, headers: cabecalhos });
    } catch (erro) {
      if (erro.status === 401) sair(true);
      throw erro;
    }
  }

  function pillStatus(status) {
    const classe =
      status === "EM_ANDAMENTO" || status === "APROVADA"
        ? "pill-on"
        : status === "CONCLUIDA"
          ? "pill-off"
          : status === "CANCELADA" || status === "NEGADA"
            ? "pill-erro"
            : "pill-alerta";
    return el("span", { class: `pill ${classe}`, text: ROTULOS_VIAGEM[status] || ROTULOS_AUTORIZACAO[status] || status });
  }

  function mostrarApp() {
    viewLogin.hidden = true;
    viewApp.hidden = false;
    dataAdmin.value = dataAtual;
    validadorInput.value = SVS.recuperar(CHAVE_VALIDADOR) || "Regulação Municipal (demo)";
    exportFim.value = hojeLocal();
    exportInicio.value = diasAtras(7);
    adminDataRotulo.textContent = `Data de referência: ${fmtData(dataAtual)} · dados sintéticos`;
  }

  function sair(expirou = false) {
    chave = null;
    SVS.apagar(CHAVE_ADMIN);
    viewApp.hidden = true;
    viewLogin.hidden = false;
    chaveInput.value = "";
    tabelaViagens.replaceChildren();
    tabelaAutorizacoes.replaceChildren();
    kpis.replaceChildren(el("div", { class: "kpi" }, el("span", {}, "Sessão encerrada"), el("strong", {}, "—")));
    if (expirou) toast("Chave administrativa inválida ou sessão encerrada.", "erro");
    chaveInput.focus();
  }

  async function entrar(evento) {
    evento.preventDefault();
    const valor = chaveInput.value.trim();
    if (valor.length < 8) {
      toast("Informe a chave administrativa completa.", "erro");
      chaveInput.focus();
      return;
    }
    chave = valor;
    const botao = formAdmin.querySelector('button[type="submit"]');
    botao.disabled = true;
    botao.textContent = "Verificando…";
    try {
      await apiAdmin("/admin/kpis");
      SVS.armazenar(CHAVE_ADMIN, chave);
      mostrarApp();
      await carregarTudo();
      toast("Painel liberado.");
    } catch (erro) {
      chave = null;
      if (erro.status === 429) toast("Muitas tentativas. Aguarde um minuto.", "erro");
      else if (erro.status !== 401) toast(erro.message || "Não foi possível validar a chave.", "erro");
    } finally {
      botao.disabled = false;
      botao.textContent = "Entrar";
    }
  }

  function cartaoKpi(rotulo, valor, complemento) {
    return el(
      "div",
      { class: "kpi" },
      el("span", { text: rotulo }),
      el("strong", { text: valor }),
      el("small", { text: complemento || "" }),
    );
  }

  function renderizarKpis(dados) {
    kpis.setAttribute("aria-busy", "false");
    kpis.replaceChildren(
      cartaoKpi("Frota online", `${dados.veiculos_online}/${dados.veiculos_total}`, "veículos ativos"),
      cartaoKpi("Viagens", String(dados.viagens_total), `${dados.viagens_em_andamento} em andamento`),
      cartaoKpi("Autorizações", String(dados.autorizacoes_aprovadas), `${dados.autorizacoes_pendentes} pendentes`),
      cartaoKpi("Embarques", String(dados.passageiros_embarcados), "check-ins registrados"),
      cartaoKpi("OTIF", `${fmtNumero(dados.otif_percentual, 1)}%`, "tolerância de 15 min"),
      cartaoKpi("Atraso médio", `${fmtNumero(dados.atraso_medio_min, 1)} min`, "viagens iniciadas"),
    );
  }

  function renderizarViagens(dados) {
    if (!dados.viagens.length) {
      tabelaViagens.replaceChildren(
        el("div", { class: "vazio" }, el("strong", {}, "Nenhuma viagem"), "Não há escala publicada para a data."),
      );
      return;
    }
    const linhas = dados.viagens.map((viagem) =>
      el(
        "tr",
        {},
        el("td", { class: "num", text: fmtHora(viagem.partida_prevista) }),
        el("td", { class: "num", text: viagem.placa }),
        el("td", { text: viagem.motorista }),
        el("td", { text: viagem.destino }),
        el("td", {}, pillStatus(viagem.status)),
        el("td", { class: "num", text: fmtNumero(viagem.autorizacoes) }),
        el("td", { class: "num", text: fmtNumero(viagem.embarques) }),
        el("td", {
          class: "num",
          text: viagem.atraso_min === null ? "—" : `${viagem.atraso_min} min`,
        }),
      ),
    );
    tabelaViagens.replaceChildren(
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
              el("th", { scope: "col", text: "Placa" }),
              el("th", { scope: "col", text: "Motorista" }),
              el("th", { scope: "col", text: "Destino" }),
              el("th", { scope: "col", text: "Status" }),
              el("th", { scope: "col", text: "Autor." }),
              el("th", { scope: "col", text: "Emb." }),
              el("th", { scope: "col", text: "Atraso" }),
            ),
          ),
          el("tbody", {}, ...linhas),
        ),
      ),
    );
  }

  function acoesAutorizacao(autorizacao) {
    if (autorizacao.status !== "PENDENTE") {
      return el("span", { class: "miudo", text: autorizacao.validada_por || "—" });
    }
    const validar = async (status) => {
      const validador = validadorInput.value.trim();
      if (validador.length < 3) {
        toast("Informe o nome do validador (mínimo 3 caracteres).", "erro");
        validadorInput.focus();
        return;
      }
      if (status === "NEGADA" && !window.confirm(`Negar a autorização ${autorizacao.numero}?`)) return;
      try {
        await apiAdmin(`/admin/autorizacoes/${autorizacao.id}/validar`, {
          method: "POST",
          body: JSON.stringify({ status, validador }),
        });
        SVS.armazenar(CHAVE_VALIDADOR, validador);
        toast(`Autorização ${autorizacao.numero} ${status === "APROVADA" ? "aprovada" : "negada"}.`);
        await carregarTudo();
      } catch (erro) {
        if (erro.status !== 401) toast(erro.message || "Não foi possível validar.", "erro");
      }
    };
    return el(
      "div",
      { class: "acoes" },
      el("button", { class: "botao pequeno", type: "button", onclick: () => validar("APROVADA") }, "Aprovar"),
      el("button", { class: "botao perigo pequeno", type: "button", onclick: () => validar("NEGADA") }, "Negar"),
    );
  }

  function renderizarAutorizacoes(dados) {
    contagemAutorizacoes.textContent = `${dados.total} registro${dados.total === 1 ? "" : "s"}`;
    if (!dados.autorizacoes.length) {
      tabelaAutorizacoes.replaceChildren(
        el("div", { class: "vazio" }, el("strong", {}, "Nenhuma autorização"), "Não há autorizações municipais para a data."),
      );
      return;
    }
    const linhas = dados.autorizacoes.map((autorizacao) =>
      el(
        "tr",
        {},
        el("td", { class: "num", text: autorizacao.numero }),
        el(
          "td",
          {},
          el("div", { text: autorizacao.paciente }),
          el("div", { class: "miudo", text: autorizacao.cpf_mascarado }),
        ),
        el(
          "td",
          {},
          el("div", { class: "num", text: autorizacao.placa }),
          el("div", { class: "miudo", text: autorizacao.destino }),
        ),
        el("td", { class: "num", text: fmtHora(autorizacao.partida_prevista) }),
        el("td", {}, pillStatus(autorizacao.status)),
        el(
          "td",
          { class: "miudo" },
          autorizacao.embarcado_em ? `Embarcou ${fmtHora(autorizacao.embarcado_em)}` : "Sem embarque",
        ),
        el("td", {}, acoesAutorizacao(autorizacao)),
      ),
    );
    tabelaAutorizacoes.replaceChildren(
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
              el("th", { scope: "col", text: "Autorização" }),
              el("th", { scope: "col", text: "Paciente" }),
              el("th", { scope: "col", text: "Veículo / destino" }),
              el("th", { scope: "col", text: "Partida" }),
              el("th", { scope: "col", text: "Status" }),
              el("th", { scope: "col", text: "Embarque" }),
              el("th", { scope: "col", text: "Ação / validador" }),
            ),
          ),
          el("tbody", {}, ...linhas),
        ),
      ),
    );
  }

  async function carregarTudo() {
    kpis.setAttribute("aria-busy", "true");
    adminDataRotulo.textContent = `Data de referência: ${fmtData(dataAtual)} · dados sintéticos`;
    try {
      const [dadosKpis, dadosViagens, dadosAutorizacoes] = await Promise.all([
        apiAdmin(`/admin/kpis?data=${encodeURIComponent(dataAtual)}`),
        apiAdmin(`/admin/viagens?data=${encodeURIComponent(dataAtual)}`),
        apiAdmin(`/admin/autorizacoes?data=${encodeURIComponent(dataAtual)}`),
      ]);
      renderizarKpis(dadosKpis);
      renderizarViagens(dadosViagens);
      renderizarAutorizacoes(dadosAutorizacoes);
    } catch (erro) {
      if (erro.status === 401) return;
      kpis.setAttribute("aria-busy", "false");
      kpis.replaceChildren(el("div", { class: "aviso erro" }, erro.message));
      tabelaViagens.replaceChildren();
      tabelaAutorizacoes.replaceChildren();
    }
  }

  async function exportarCsv() {
    const inicio = exportInicio.value;
    const fim = exportFim.value;
    if (!inicio || !fim) {
      toast("Informe o intervalo de exportação.", "erro");
      return;
    }
    if (inicio > fim) {
      toast("A data inicial deve ser anterior à final.", "erro");
      return;
    }
    const botao = document.getElementById("btn-exportar");
    botao.disabled = true;
    exportStatus.textContent = "Gerando arquivo…";
    try {
      const resposta = await fetch(
        `/api/v1/admin/posicoes.csv?inicio=${encodeURIComponent(inicio)}&fim=${encodeURIComponent(fim)}`,
        { headers: { "X-Admin-Key": chave || "" } },
      );
      if (resposta.status === 401) {
        sair(true);
        return;
      }
      if (!resposta.ok) {
        const texto = await resposta.text();
        throw new Error(texto || `Erro ${resposta.status}`);
      }
      const blob = await resposta.blob();
      const disposicao = resposta.headers.get("content-disposition") || "";
      const nome = /filename="?([^";]+)"?/.exec(disposicao)?.[1] || `posicoes_${inicio}_${fim}.csv`;
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = nome;
      document.body.append(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 4000);
      exportStatus.textContent = `Arquivo ${nome} gerado (${Math.max(1, Math.round(blob.size / 1024))} KB).`;
      toast("Exportação concluída.");
    } catch (erro) {
      exportStatus.textContent = `Falha na exportação: ${erro.message}`;
      toast("Não foi possível exportar a telemetria.", "erro");
    } finally {
      botao.disabled = false;
    }
  }

  function restaurar() {
    if (!chave) return false;
    mostrarApp();
    carregarTudo();
    return true;
  }

  formAdmin.addEventListener("submit", entrar);

  dataAdmin.addEventListener("change", () => {
    dataAtual = dataAdmin.value || hojeLocal();
    carregarTudo();
  });

  document.getElementById("btn-atualizar").addEventListener("click", carregarTudo);
  document.getElementById("btn-sair").addEventListener("click", () => sair(false));
  document.getElementById("btn-exportar").addEventListener("click", exportarCsv);

  validadorInput.addEventListener("change", () => {
    const valor = validadorInput.value.trim();
    if (valor) SVS.armazenar(CHAVE_VALIDADOR, valor);
  });

  if (!restaurar()) chaveInput.focus();
})();
