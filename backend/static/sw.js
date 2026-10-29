/* Service worker do PWA: casca em cache, API sempre em rede primeiro. */
"use strict";

const VERSAO = "svs-rastreio-v1";
const CASCA = [
  "/",
  "/index.html",
  "/paciente.html",
  "/motorista.html",
  "/admin.html",
  "/sobre.html",
  "/manifest.webmanifest",
  "/css/app.css",
  "/js/comum.js",
  "/js/rastreio.js",
  "/js/paciente.js",
  "/js/motorista.js",
  "/js/admin.js",
  "/icons/icon.svg",
  "/icons/maskable.svg",
  "/icons/icon-192.png",
  "/icons/icon-512.png",
  "/icons/maskable-512.png",
];

const OFFLINE_HTML = `<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sem conexão — SVS Rastreio</title>
<style>body{font-family:system-ui,sans-serif;margin:0;display:grid;place-items:center;min-height:100vh;background:#f1f5f9;color:#1e293b}
main{max-width:32rem;padding:2rem;text-align:center}h1{color:#0f766e}button{font:inherit;padding:.7rem 1rem;border:0;border-radius:10px;background:#0f766e;color:#fff;cursor:pointer}</style>
</head><body><main><h1>Sem conexão</h1>
<p>Não foi possível alcançar o servidor. Verifique sua rede e tente novamente.</p>
<p>As páginas já visitadas continuam disponíveis, mas a posição dos veículos exige conexão.</p>
<button onclick="location.reload()">Tentar novamente</button></main></body></html>`;

self.addEventListener("install", (evento) => {
  evento.waitUntil(
    (async () => {
      const cache = await caches.open(VERSAO);
      await Promise.allSettled(CASCA.map((url) => cache.add(new Request(url, { cache: "reload" }))));
      await self.skipWaiting();
    })(),
  );
});

self.addEventListener("activate", (evento) => {
  evento.waitUntil(
    (async () => {
      const chaves = await caches.keys();
      await Promise.all(chaves.filter((chave) => chave !== VERSAO).map((chave) => caches.delete(chave)));
      await self.clients.claim();
    })(),
  );
});

function respostaOffline() {
  return new Response(OFFLINE_HTML, {
    status: 503,
    headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" },
  });
}

function respostaApiOffline() {
  return new Response(
    JSON.stringify({ detail: "Sem conexão com o servidor. Tente novamente quando a rede voltar." }),
    { status: 503, headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" } },
  );
}

async function redePrimeiro(evento) {
  const { request } = evento;
  try {
    const resposta = await fetch(request);
    if (resposta && resposta.ok) {
      const cache = await caches.open(VERSAO);
      cache.put(request, resposta.clone()).catch(() => {});
    }
    return resposta;
  } catch {
    const cache = await caches.match(request);
    if (cache) return cache;
    if (request.mode === "navigate") {
      return (await caches.match("/")) || respostaOffline();
    }
    return request.url.includes("/api/") ? respostaApiOffline() : respostaOffline();
  }
}

async function cachePrimeiro(evento) {
  const { request } = evento;
  const emCache = await caches.match(request);
  if (emCache) return emCache;
  try {
    const resposta = await fetch(request);
    if (resposta && resposta.ok) {
      const cache = await caches.open(VERSAO);
      cache.put(request, resposta.clone()).catch(() => {});
    }
    return resposta;
  } catch {
    return request.mode === "navigate" ? respostaOffline() : respostaOffline();
  }
}

self.addEventListener("fetch", (evento) => {
  const { request } = evento;
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  if (url.pathname.startsWith("/api/")) {
    evento.respondWith(redePrimeiro(evento));
    return;
  }

  if (url.pathname === "/sw.js" || url.pathname.startsWith("/docs") || url.pathname.startsWith("/openapi")) {
    return;
  }

  if (request.mode === "navigate") {
    evento.respondWith(redePrimeiro(evento));
    return;
  }

  evento.respondWith(cachePrimeiro(evento));
});
