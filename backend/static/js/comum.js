/* Utilidades compartilhadas pelas páginas do PWA (sem framework, sem build). */
"use strict";

const SVS = (() => {
  const API = "/api/v1";
  const FUSO = "America/Sao_Paulo";

  async function api(caminho, opcoes = {}) {
    const cabecalhos = { "Content-Type": "application/json", ...(opcoes.headers || {}) };
    const resposta = await fetch(API + caminho, { ...opcoes, headers: cabecalhos });
    const texto = await resposta.text();
    let dados = null;
    if (texto) {
      try {
        dados = JSON.parse(texto);
      } catch {
        dados = null;
      }
    }
    if (!resposta.ok) {
      const detalhe = dados && dados.detail;
      const mensagem = Array.isArray(detalhe)
        ? detalhe.map((d) => d.msg).join("; ")
        : typeof detalhe === "string"
          ? detalhe
          : `Erro ${resposta.status}`;
      const erro = new Error(mensagem);
      erro.status = resposta.status;
      throw erro;
    }
    return dados;
  }

  function el(tag, props = {}, ...filhos) {
    const node = document.createElement(tag);
    for (const [chave, valor] of Object.entries(props)) {
      if (valor === null || valor === undefined) continue;
      if (chave === "class") node.className = valor;
      else if (chave === "text") node.textContent = valor;
      else if (chave === "html") node.innerHTML = valor;
      else if (chave.startsWith("on") && typeof valor === "function") {
        node.addEventListener(chave.slice(2).toLowerCase(), valor);
      } else if (valor === true) node.setAttribute(chave, "");
      else if (valor !== false) node.setAttribute(chave, valor);
    }
    for (const filho of filhos.flat()) {
      if (filho === null || filho === undefined || filho === false) continue;
      node.append(filho.nodeType ? filho : document.createTextNode(String(filho)));
    }
    return node;
  }

  const fmtDataHora = (iso) =>
    iso
      ? new Date(iso).toLocaleString("pt-BR", {
          timeZone: FUSO,
          dateStyle: "short",
          timeStyle: "short",
        })
      : "—";

  const fmtHora = (iso) =>
    iso ? new Date(iso).toLocaleTimeString("pt-BR", { timeZone: FUSO, timeStyle: "short" }) : "—";

  const fmtData = (iso) => {
    if (!iso) return "—";
    const [ano, mes, dia] = String(iso).slice(0, 10).split("-");
    return `${dia}/${mes}/${ano}`;
  };

  const fmtIdade = (segundos) => {
    if (segundos === null || segundos === undefined) return "sem registro";
    if (segundos < 90) return `${segundos} s atrás`;
    if (segundos < 5400) return `${Math.round(segundos / 60)} min atrás`;
    if (segundos < 172800) return `${Math.round(segundos / 3600)} h atrás`;
    return `${Math.round(segundos / 86400)} dias atrás`;
  };

  const fmtKm = (km) =>
    km === null || km === undefined
      ? "—"
      : km < 1
        ? `${Math.round(km * 1000)} m`
        : `${km.toLocaleString("pt-BR", { maximumFractionDigits: 1 })} km`;

  const fmtNumero = (valor, casas = 0) =>
    valor === null || valor === undefined
      ? "—"
      : Number(valor).toLocaleString("pt-BR", { maximumFractionDigits: casas });

  const normalizarPlaca = (valor) =>
    String(valor || "")
      .toUpperCase()
      .replace(/[^A-Z0-9]/g, "")
      .slice(0, 7);

  function pill(online) {
    return el("span", {
      class: `pill ${online ? "pill-on" : "pill-off"}`,
      text: online ? "Online" : "Offline",
    });
  }

  function avatar(nome) {
    const inicial = (nome || "?").trim().charAt(0).toUpperCase();
    return el("span", { class: "avatar", "aria-hidden": "true", text: inicial });
  }

  let temporizadorToast = null;
  function toast(mensagem, tipo = "ok") {
    document.querySelectorAll(".toast").forEach((t) => t.remove());
    const node = el("div", { class: `toast ${tipo === "erro" ? "erro" : ""}`, role: "status" }, mensagem);
    document.body.append(node);
    clearTimeout(temporizadorToast);
    temporizadorToast = setTimeout(() => node.remove(), 4200);
  }

  /** Cria um mapa Leaflet ou retorna null com aviso textual (modo offline). */
  function criarMapa(id) {
    const alvo = document.getElementById(id);
    if (!alvo) return null;
    if (!window.L) {
      alvo.replaceWith(
        el(
          "div",
          { class: "mapa-indisponivel", id },
          el("p", {}, "Mapa indisponível sem conexão com o CDN do Leaflet."),
          el("p", { class: "miudo" }, "As coordenadas continuam disponíveis nos cartões ao lado."),
        ),
      );
      return null;
    }
    const mapa = L.map(alvo, { zoomControl: true, scrollWheelZoom: false }).setView(
      [-23.85, -46.5],
      9,
    );
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(mapa);
    return mapa;
  }

  function camadaVeiculo(mapa) {
    if (!mapa) return null;
    return {
      marcador: L.circleMarker([0, 0], {
        radius: 9,
        color: "#0f766e",
        weight: 3,
        fillColor: "#14b8a6",
        fillOpacity: 0.9,
      }).addTo(mapa),
      trilha: L.polyline([], { color: "#0f766e", weight: 3, opacity: 0.55 }).addTo(mapa),
      usuario: L.circleMarker([0, 0], {
        radius: 6,
        color: "#2563eb",
        weight: 2,
        fillColor: "#60a5fa",
        fillOpacity: 0.85,
      }),
    };
  }

  function lerParametro(nome) {
    return new URLSearchParams(window.location.search).get(nome);
  }

  function armazenar(chave, valor) {
    try {
      sessionStorage.setItem(chave, valor);
    } catch {
      /* modo privado: ignora */
    }
  }

  function recuperar(chave) {
    try {
      return sessionStorage.getItem(chave);
    } catch {
      return null;
    }
  }

  function apagar(chave) {
    try {
      sessionStorage.removeItem(chave);
    } catch {
      /* ignora */
    }
  }

  function registrarServiceWorker() {
    if ("serviceWorker" in navigator && window.isSecureContext) {
      navigator.serviceWorker.register("/sw.js").catch(() => {});
    }
  }

  registrarServiceWorker();

  return {
    api,
    el,
    fmtDataHora,
    fmtHora,
    fmtData,
    fmtIdade,
    fmtKm,
    fmtNumero,
    normalizarPlaca,
    pill,
    avatar,
    toast,
    criarMapa,
    camadaVeiculo,
    lerParametro,
    armazenar,
    recuperar,
    apagar,
  };
})();
