// Cliente web del sistema experto como servicio. No guarda estado en el servidor:
// cada turno envia la categoria y todas las respuestas dadas.
const API = (new URLSearchParams(location.search).get("api") || window.SE_API || "").replace(/\/$/, "");
const NOMBRES = { se: "Nuestro sistema experto", gemini: "Gemini (IA generativa)" };
const URGENCIA = { Critica: "crítica", Alta: "alta", Media: "media", Baja: "baja" };
let modo = "se";

const $ = (s, r = document) => r.querySelector(s);
const el = (tag, attrs = {}, ...hijos) => {
  const n = document.createElement(tag);
  Object.entries(attrs).forEach(([k, v]) => (k === "class" ? (n.className = v) : n.setAttribute(k, v)));
  hijos.flat().forEach((h) => n.append(h instanceof Node ? h : document.createTextNode(h ?? "")));
  return n;
};

async function llamar(ruta, cuerpo) {
  const r = await fetch(API + ruta, cuerpo ? {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(cuerpo),
  } : {});
  const datos = await r.json().catch(() => ({ error: `HTTP ${r.status}` }));
  if (!r.ok) throw new Error(datos.error || `HTTP ${r.status}`);
  return datos;
}

// ---------------------------------------------------------------- inicio

async function iniciar() {
  document.querySelectorAll(".modo").forEach((b) => b.addEventListener("click", () => {
    modo = b.dataset.modo;
    document.querySelectorAll(".modo").forEach((x) => x.setAttribute("aria-checked", String(x === b)));
  }));
  try {
    const salud = await llamar("/api/salud");
    $("#estado").textContent = `Conectado · base ${salud.huella_base} · IA: ${salud.modelo_ia || "no configurada"}`;
    $("#estado").classList.add("ok");
    const { categorias } = await llamar("/api/categorias");
    $("#categorias").replaceChildren(...categorias.map((c) =>
      el("button", { class: "categoria", type: "button" }, el("strong", {}, c.nombre), el("span", {}, c.descripcion || ""))));
    [...$("#categorias").children].forEach((b, i) => b.addEventListener("click", () => abrir(categorias[i])));
  } catch (e) {
    $("#estado").textContent = `Sin conexión con el servicio (${API || location.origin}): ${e.message}`;
    $("#estado").classList.add("error");
  }
}

function abrir(categoria) {
  const motores = modo === "ambos" ? ["se", "gemini"] : [modo];
  const cont = $("#sesiones");
  cont.classList.toggle("doble", motores.length === 2);
  cont.replaceChildren(...motores.map((m) => crearSesion(m, categoria)));
  cont.scrollIntoView({ behavior: "smooth" });
}

// ---------------------------------------------------------------- una sesion de diagnostico

function crearSesion(motor, categoria) {
  const nodo = $("#t-sesion").content.firstElementChild.cloneNode(true);
  $(".sesion-titulo", nodo).textContent = NOMBRES[motor];
  $(".sesion-sub", nodo).textContent = categoria.nombre;
  nodo.classList.add(`motor-${motor}`);
  const s = { motor, categoria: categoria.codigo, respuestas: [], textos: [], ms: 0, nodo };
  turno(s);
  return nodo;
}

async function turno(s) {
  const zona = $(".zona", s.nodo);
  zona.replaceChildren(el("p", { class: "cargando" }, "Pensando…"));
  try {
    const r = await llamar(`/api/${s.motor}/diagnostico`, { categoria: s.categoria, respuestas: s.respuestas });
    s.ms += r.tiempo_ms || 0;
    $(".metricas", s.nodo).textContent =
      `${s.respuestas.length} pregunta(s) · ${(s.ms / 1000).toFixed(2)} s en el servidor` +
      (r.detalle?.tokens_entrada ? ` · ${r.detalle.tokens_entrada + (r.detalle.tokens_salida || 0)} tokens en el último turno` : "");
    if (r.estado === "pregunta") return mostrarPregunta(s, r);
    mostrarResultado(s, r);
  } catch (e) {
    zona.replaceChildren(el("p", { class: "aviso error", role: "alert" }, `Error del servicio: ${e.message}`),
      el("button", { class: "secundario", type: "button" }, "Reintentar"));
    $("button", zona).addEventListener("click", () => turno(s));
  }
}

function mostrarPregunta(s, r) {
  const si = el("button", { class: "primario", type: "button" }, "Sí");
  const no = el("button", { class: "secundario", type: "button" }, "No");
  const responder = (valor) => {
    s.respuestas.push({ pregunta: r.pregunta.codigo, valor });
    s.textos.push([r.pregunta.texto, valor]);
    $(".dadas", s.nodo).replaceChildren(...s.textos.map(([t, v]) =>
      el("li", {}, el("span", {}, t), el("b", { class: v ? "si" : "no" }, v ? "Sí" : "No"))));
    turno(s);
  };
  si.addEventListener("click", () => responder(1));
  no.addEventListener("click", () => responder(0));
  $(".zona", s.nodo).replaceChildren(
    el("p", { class: "numero" }, `Pregunta ${s.respuestas.length + 1}`),
    el("p", { class: "pregunta" }, r.pregunta.texto),
    el("div", { class: "botones" }, si, no));
  si.focus();
}

function mostrarResultado(s, r) {
  const zona = $(".zona", s.nodo);
  const partes = [];
  if (r.estado === "diagnostico") {
    const d = r.diagnostico;
    const criticas = r.detalle?.acciones_inmediatas || [];
    if (criticas.length) {
      partes.push(el("div", { class: "alerta", role: "alert" }, el("strong", {}, "Riesgo crítico: actúe de inmediato"),
        el("ul", {}, criticas.map((a) => el("li", {}, a)))));
    }
    partes.push(el("div", { class: `resultado urg-${d.urgencia}` },
      el("span", { class: "chip" }, `Urgencia ${URGENCIA[d.urgencia]}`),
      el("h3", {}, `${d.codigo} · ${d.nombre}`),
      el("p", {}, `Factor de certeza del experto: ${d.certeza} %` +
        (d.probabilidad != null ? ` · Probabilidad calculada: ${(d.probabilidad * 100).toFixed(1)} %` : "")),
      el("p", {}, el("b", {}, "Especialista: "), d.especialista),
      el("p", {}, el("b", {}, "Qué hacer: "), d.accion)));
  } else if (r.estado === "sin_diagnostico") {
    partes.push(el("div", { class: "resultado neutro" }, el("h3", {}, "Sin diagnóstico concluyente"),
      el("p", {}, "Las respuestas no coinciden con ninguna regla de esta categoría. Revise las respuestas o pruebe otra categoría.")));
  } else {
    partes.push(el("div", { class: "aviso error", role: "alert" }, el("strong", {}, "Respuesta no válida del servicio. "),
      r.detalle?.validacion || ""));
  }
  partes.push(explicacion(s, r));
  const otra = el("button", { class: "secundario", type: "button" }, "Nuevo diagnóstico");
  otra.addEventListener("click", () => { s.respuestas = []; s.textos = []; s.ms = 0; $(".dadas", s.nodo).replaceChildren(); turno(s); });
  partes.push(otra);
  zona.replaceChildren(...partes);
}

function explicacion(s, r) {
  const det = r.detalle || {};
  const caja = el("details", { class: "porque" }, el("summary", {}, "¿Por qué?"));
  if (s.motor === "se") {
    caja.append(el("p", {}, "Cada respuesta actualiza la probabilidad de la hipótesis con el teorema de Bayes:"));
    caja.append(el("table", {}, el("thead", {}, el("tr", {}, el("th", {}, "Respuesta"), el("th", {}, "Efecto"), el("th", {}, "Antes"), el("th", {}, "Después"))),
      el("tbody", {}, (det.explicacion || []).map((f) => el("tr", {}, el("td", {}, f.texto), el("td", {}, f.efecto),
        el("td", {}, `${(f.antes * 100).toFixed(1)} %`), el("td", {}, `${(f.despues * 100).toFixed(1)} %`))))));
    caja.append(el("p", { class: "nota" }, "Hipótesis más probables: " +
      (det.ranking || []).slice(0, 4).map((h) => `${h.codigo} ${(h.probabilidad * 100).toFixed(1)} %`).join(" · ")));
  } else {
    caja.append(el("p", {}, el("b", {}, "Justificación del modelo: "), det.justificacion || "—"));
    caja.append(el("p", { class: "nota" }, `Confianza declarada por el modelo: ${det.confianza ?? "—"} · modelo ${det.modelo} · ` +
      `${det.tokens_entrada ?? "?"} tokens de entrada. Es una explicación generada en texto: no hay un cálculo verificable detrás.`));
  }
  return caja;
}

iniciar();
