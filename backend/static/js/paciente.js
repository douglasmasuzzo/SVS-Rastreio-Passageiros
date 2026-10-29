/* Consulta do passageiro: CPF + data de nascimento, com respostas genéricas. */
(() => {
  "use strict";

  const { api, el, fmtData, fmtDataHora, fmtHora, toast } = SVS;

  const form = document.getElementById("form-consulta");
  const cpfInput = document.getElementById("cpf");
  const nascimentoInput = document.getElementById("nascimento");
  const dataInput = document.getElementById("data-viagem");
  const resultado = document.getElementById("resultado");
  const conteudo = document.getElementById("resultado-conteudo");
  const atalhos = document.getElementById("atalhos-demo");

  const ROTULOS_VIAGEM = {
    PLANEJADA: "Planejada",
    AUTORIZADA: "Autorizada",
    EM_ANDAMENTO: "Em andamento",
    CONCLUIDA: "Concluída",
    CANCELADA: "Cancelada",
  };

  const ROTULOS_AUTORIZACAO = {
    PENDENTE: "Autorização pendente",
    APROVADA: "Autorização aprovada",
    NEGADA: "Autorização negada",
    CANCELADA: "Autorização cancelada",
  };

  const apenasDigitos = (valor) => String(valor || "").replace(/\D/g, "").slice(0, 11);

  function formatarCpf(valor) {
    const digitos = apenasDigitos(valor);
    if (digitos.length <= 3) return digitos;
    if (digitos.length <= 6) return `${digitos.slice(0, 3)}.${digitos.slice(3)}`;
    if (digitos.length <= 9) {
      return `${digitos.slice(0, 3)}.${digitos.slice(3, 6)}.${digitos.slice(6)}`;
    }
    return `${digitos.slice(0, 3)}.${digitos.slice(3, 6)}.${digitos.slice(6, 9)}-${digitos.slice(9)}`;
  }

  function hojeLocal() {
    return new Date().toLocaleDateString("sv-SE", { timeZone: "America/Sao_Paulo" });
  }

  function pillStatusViagem(status) {
    const classe =
      status === "EM_ANDAMENTO"
        ? "pill-on"
        : status === "CANCELADA"
          ? "pill-erro"
          : status === "PLANEJADA"
            ? "pill-alerta"
            : "pill-off";
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

  function exibirResultado(...filhos) {
    resultado.hidden = false;
    resultado.setAttribute("aria-busy", "false");
    conteudo.replaceChildren(...filhos);
    resultado.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function exibirCarregando() {
    resultado.hidden = false;
    resultado.setAttribute("aria-busy", "true");
    conteudo.replaceChildren(
      el("h2", { text: "Consultando…" }),
      el("div", { class: "esqueleto", style: "margin-bottom:.6rem" }),
      el("div", { class: "esqueleto", style: "width:70%" }),
    );
  }

  function exibirErro(mensagem) {
    exibirResultado(
      el("h2", { tabindex: "-1", text: "Não foi possível consultar" }),
      el(
        "div",
        { class: "aviso erro" },
        el("strong", {}, "Dados não conferem. "),
        mensagem || "Verifique o CPF e a data de nascimento e tente novamente.",
      ),
      el(
        "p",
        { class: "miudo", style: "margin-top:.8rem" },
        "Por segurança, esta mensagem é a mesma para CPF inexistente, data errada ou cadastro inativo.",
      ),
      el(
        "button",
        { class: "botao secundario", type: "button", onclick: () => cpfInput.focus() },
        "Tentar novamente",
      ),
    );
    const titulo = conteudo.querySelector("h2");
    if (titulo) titulo.focus({ preventScroll: true });
  }

  function cabecalhoPaciente(paciente) {
    return el(
      "div",
      { class: "card-cabecalho" },
      el(
        "div",
        { class: "cresce" },
        el("span", { class: "etiqueta", text: "Cadastro localizado" }),
        el("h2", { tabindex: "-1", text: paciente.nome }),
        el(
          "p",
          { class: "miudo", style: "margin:0" },
          `CPF ${paciente.cpf_mascarado} · ${paciente.municipio}`,
        ),
      ),
    );
  }

  function blocoViagem(viagem) {
    const acompanhar = viagem.acompanhamento_em_tempo_real;
    const link = `/?placa=${encodeURIComponent(viagem.veiculo.placa)}`;
    return el(
      "div",
      { class: "viagem-destaque" },
      el(
        "div",
        { class: "card-cabecalho" },
        el(
          "div",
          { class: "cresce" },
          el("span", { class: "etiqueta", text: "Viagem do dia" }),
          el("h3", { style: "margin:.2rem 0 0", text: viagem.destino }),
          el("p", { class: "miudo", style: "margin:.2rem 0 0", text: `Autorização ${viagem.numero_autorizacao}` }),
        ),
        el(
          "div",
          { style: "text-align:right" },
          pillStatusViagem(viagem.status),
          el(
            "div",
            { class: "miudo", style: "margin-top:.35rem" },
            viagem.embarcado ? "Embarque confirmado" : "Embarque não registrado",
          ),
        ),
      ),
      el(
        "dl",
        { class: "dados" },
        dado("Partida prevista", fmtHora(viagem.partida_prevista), fmtData(viagem.partida_prevista)),
        dado(
          "Retorno previsto",
          viagem.retorno_previsto ? fmtHora(viagem.retorno_previsto) : "—",
          viagem.retorno_previsto ? fmtData(viagem.retorno_previsto) : null,
        ),
        dado("Veículo", viagem.veiculo.placa, `${viagem.veiculo.modelo}${viagem.veiculo.acessivel ? " · acessível" : ""}`),
        dado("Motorista", viagem.motorista, viagem.veiculo.operadora),
      ),
      el(
        "p",
        { class: "miudo" },
        acompanhar
          ? "O veículo está em operação. A posição exibida no mapa é aproximada (~11 m) e a trilha cobre as últimas 12 horas."
          : "O mapa em tempo real é liberado quando a viagem é iniciada pelo motorista. Você já pode acompanhar a placa pela tela pública.",
      ),
      el(
        "div",
        { class: "acoes" },
        el("a", { class: "botao", href: link }, acompanhar ? "Acompanhar veículo agora" : "Ver veículo no mapa"),
        el(
          "button",
          { class: "botao secundario", type: "button", onclick: () => window.print() },
          "Imprimir comprovante",
        ),
      ),
    );
  }

  function semAgendamento(dados) {
    return el(
      "div",
      {},
      el("span", { class: "etiqueta", text: "Sem viagem aprovada" }),
      el("h2", { tabindex: "-1", text: `Nenhuma viagem em ${fmtData(dados.data_consulta)}` }),
      el(
        "div",
        { class: "aviso", style: "margin-top:.6rem" },
        el("strong", {}, "O que isso significa? "),
        "Não há autorização municipal aprovada para esta data. Se a viagem foi solicitada há pouco, aguarde a validação da central de regulação. Autorizações pendentes ou negadas não aparecem como viagem do dia.",
      ),
      el(
        "p",
        { class: "miudo", style: "margin-top:.8rem" },
        "Em caso de dúvida, procure a unidade de saúde que solicitou o transporte.",
      ),
    );
  }

  function tabelaHistorico(historico) {
    if (!historico.length) {
      return el(
        "p",
        { class: "miudo", style: "margin-top:1rem" },
        "Nenhum atendimento anterior nos últimos 180 dias.",
      );
    }
    const linhas = historico.map((item) =>
      el(
        "tr",
        {},
        el("td", { class: "num", text: fmtData(item.data) }),
        el("td", { text: item.destino }),
        el("td", { class: "num", text: item.placa }),
        el("td", {}, el("span", { class: "pill pill-off", text: ROTULOS_VIAGEM[item.status] || item.status })),
        el("td", { text: ROTULOS_AUTORIZACAO[item.status_autorizacao] || item.status_autorizacao }),
      ),
    );
    return el(
      "div",
      { style: "margin-top:1.2rem" },
      el("h3", { text: "Histórico recente" }),
      el(
        "p",
        { class: "miudo" },
        "Últimos 30 registros nos 180 dias anteriores à data consultada.",
      ),
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
              el("th", { scope: "col", text: "Data" }),
              el("th", { scope: "col", text: "Destino" }),
              el("th", { scope: "col", text: "Placa" }),
              el("th", { scope: "col", text: "Viagem" }),
              el("th", { scope: "col", text: "Autorização" }),
            ),
          ),
          el("tbody", {}, ...linhas),
        ),
      ),
    );
  }

  function renderizar(dados) {
    const partes = [cabecalhoPaciente(dados.paciente)];
    partes.push(
      dados.viagem_hoje
        ? blocoViagem(dados.viagem_hoje)
        : semAgendamento(dados),
    );
    partes.push(tabelaHistorico(dados.historico));
    partes.push(
      el(
        "p",
        { class: "selo-lgpd", style: "margin-top:1.2rem" },
        el("span", { "aria-hidden": "true", text: "🔒" }),
        "Consulta registrada em auditoria. Nenhum CPF completo é exibido ou armazenado no navegador.",
      ),
    );
    exibirResultado(...partes);
    const titulo = conteudo.querySelector("h2");
    if (titulo) titulo.focus({ preventScroll: true });
  }

  async function consultar(evento) {
    evento.preventDefault();
    const cpf = apenasDigitos(cpfInput.value);
    if (cpf.length !== 11) {
      toast("Informe um CPF com 11 dígitos.", "erro");
      cpfInput.focus();
      return;
    }
    if (!nascimentoInput.value) {
      toast("Informe a data de nascimento.", "erro");
      nascimentoInput.focus();
      return;
    }

    exibirCarregando();
    try {
      const dados = await api("/passageiro/consulta", {
        method: "POST",
        body: JSON.stringify({
          cpf,
          data_nascimento: nascimentoInput.value,
          data: dataInput.value || null,
        }),
      });
      renderizar(dados);
    } catch (erro) {
      if (erro.status === 429) {
        exibirErro("Muitas tentativas em pouco tempo. Aguarde um minuto antes de tentar novamente.");
      } else if (erro.status === 404) {
        exibirErro("Confira o CPF e a data de nascimento. A mensagem é intencionalmente genérica.");
      } else if (erro.status === 422) {
        exibirErro("Verifique o formato dos campos informados.");
      } else {
        exibirErro(erro.message || "Falha de comunicação com o servidor. Tente novamente.");
      }
    }
  }

  cpfInput.addEventListener("input", () => {
    const posicao = cpfInput.selectionStart;
    const antes = cpfInput.value.length;
    cpfInput.value = formatarCpf(cpfInput.value);
    const depois = cpfInput.value.length;
    cpfInput.setSelectionRange(posicao + (depois - antes), posicao + (depois - antes));
  });

  form.addEventListener("submit", consultar);

  form.addEventListener("reset", () => {
    resultado.hidden = true;
    conteudo.replaceChildren();
    resultado.setAttribute("aria-busy", "false");
  });

  atalhos.addEventListener("click", (evento) => {
    const botao = evento.target.closest("button[data-cpf]");
    if (!botao) return;
    cpfInput.value = formatarCpf(botao.dataset.cpf);
    nascimentoInput.value = botao.dataset.nascimento;
    dataInput.value = "";
    toast("Credenciais de demonstração preenchidas. Clique em consultar.");
    form.requestSubmit();
  });

  if (!dataInput.value) dataInput.max = hojeLocal();
  cpfInput.focus();
})();
