// Reiter „Prozesse“: Verfahrensarten (Soll-Modell, soll.json) und Gremien (prozessarten.json) als Schaubild oder Liste.
// Verfahren und Zuständigkeitsordnung stammen aus „Bonn entscheidet“ (anster2025, MIT) mit Ergänzungen der RIS-Karte;
// Zahlen je Verfahren beruhen auf der abgeleiteten Zuordnung (pipeline/soll.py), Gremien und Sitzungen auf der
// OParl-API der Stadt Bonn (CC0). Wird von app.js erst beim Öffnen des Reiters geladen.
import { deDate } from "./mitwirken.js";

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const num = (n) => Number(n || 0).toLocaleString("de-DE");
const LANES = ["ew", "rm", "bvm", "vw", "bv", "aus", "rat"];
const ART_PL = { rat: "Rat", hauptausschuss: "Hauptausschuss", ausschuss: "Fachausschüsse", bezirksvertretung: "Bezirksvertretungen",
  beirat: "Beiräte und Kommissionen", unterausschuss: "Unterausschüsse", wahlausschuss: "Wahlausschüsse" };
const ART = { rat: "Rat", hauptausschuss: "Hauptausschuss", ausschuss: "Fachausschuss", bezirksvertretung: "Bezirksvertretung",
  beirat: "Beirat oder Kommission", unterausschuss: "Unterausschuss", wahlausschuss: "Wahlausschuss" };
const RECHT = [["Entscheidung", "entscheidet selbst"], ["Empfehlung", "empfiehlt dem Rat"], ["Anhörung", "wird angehört"], ["Mitteilung", "erhält Mitteilungen"]];
// Wege, sich einzubringen (Regeln des Soll-Modells); kurze Bezeichnungen der RIS-Karte, Frist und Beleg aus der Quelle
const WEGE = { "sitzung-besuchen": "Sitzung besuchen", livestream: "Ratssitzung im Livestream verfolgen",
  "buergerantrag-erlaeutern": "Eigenen Bürgerantrag im Ausschuss erläutern", einwohnerfrage: "Frage in der Einwohnerfragestunde stellen",
  "ansprechen-bv": "Bezirksverordnete ansprechen", "ansprechen-rat": "Fraktionen oder Gruppen ansprechen",
  "eigener-buergerantrag": "Eigenen Bürgerantrag einbringen", offenlage: "Stellungnahme in der Offenlage abgeben" };

let ctx, soll, data, root, state = { tab: "verfahren", view: "schaubild", verfahren: null, gremium: null, frueher: false, q: "" };

const links = (ls) => (ls || []).map((l) => `<a href="${esc(l.url)}" target="_blank" rel="noopener">${esc(l.label)}<span class="visually-hidden"> (neuer Tab)</span></a>`).join(" · ");
const beleg = (x) => (x.links && x.links.length ? links(x.links) : x.beleg ? esc(x.beleg) : "");

// --- Verfahren ---------------------------------------------------------------------------------------
function lanesOf(v) {
  const used = new Set(v.schritte.map((s) => s.bahn).filter(Boolean));
  return LANES.filter((b) => used.has(b));
}
function wrap(text, max = 19) {
  const out = [];
  let line = "";
  for (const w of String(text).split(/\s+/)) {
    if (line && (line + " " + w).length > max) { out.push(line); line = w; } else line = line ? `${line} ${w}` : w;
  }
  if (line) out.push(line);
  return out.length > 3 ? [...out.slice(0, 2), out.slice(2).join(" ").slice(0, max - 1) + "…"] : out;
}
function swimlane(vid, v) {
  const lanes = lanesOf(v), LW = 150, CW = 150, LH = 58, NW = 132, NH = 44, top = 8;
  const W = LW + v.schritte.length * CW + 10, H = top + lanes.length * LH + 8;
  const pos = v.schritte.map((s, i) => ({ x: LW + i * CW + (CW - NW) / 2, y: top + Math.max(0, lanes.indexOf(s.bahn)) * LH + (LH - NH) / 2 }));
  const lanesSvg = lanes.map((b, i) => `<rect class="pz-lane${i % 2 ? " odd" : ""}" x="0" y="${top + i * LH}" width="${W}" height="${LH}"/>
    <text class="pz-lane-label" x="10" y="${top + i * LH + LH / 2}">${wrap(soll.bahnen[b] || b, 20).map((t, k, a) => `<tspan x="10" dy="${k ? 13 : -(a.length - 1) * 6.5 + 4}">${esc(t)}</tspan>`).join("")}</text>`).join("");
  const arrows = pos.slice(1).map((p, i) => {
    const a = pos[i], x1 = a.x + NW, y1 = a.y + NH / 2, x2 = p.x, y2 = p.y + NH / 2, mx = (x1 + x2) / 2;
    return `<path class="pz-arrow" d="M${x1},${y1} H${mx} V${y2} H${x2 - 2}" marker-end="url(#pz-head-${vid})"/>`;
  }).join("");
  const nodes = v.schritte.map((s, i) => {
    const p = pos[i], lines = wrap(s.label);
    return `<g class="pz-node${s.eigen ? " eigen" : ""}"><rect x="${p.x}" y="${p.y}" width="${NW}" height="${NH}" rx="10"/>
      <circle cx="${p.x}" cy="${p.y}" r="9"/><text class="pz-no" x="${p.x}" y="${p.y + 3.5}">${i + 1}</text>
      <text class="pz-label" x="${p.x + NW / 2}" y="${p.y + NH / 2}">${lines.map((t, k) => `<tspan x="${p.x + NW / 2}" dy="${k ? 12.5 : -(lines.length - 1) * 6.25 + 4}">${esc(t)}</tspan>`).join("")}</text></g>`;
  }).join("");
  const summary = `${v.titel}: ${v.schritte.map((s, i) => `${i + 1}. ${s.label} (${soll.bahnen[s.bahn] || "ohne Ebene"})`).join("; ")}`;
  return `<div class="pz-scroll" tabindex="0" role="region" aria-label="Schaubild ${esc(v.titel)}, seitlich verschiebbar"><svg class="pz-svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="${esc(summary)}">
    <defs><marker id="pz-head-${vid}" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L8,4 L0,8 z" class="pz-head"/></marker></defs>
    ${lanesSvg}${arrows}${nodes}</svg></div>
    <p class="hint">Jede Zeile ist eine Ebene, die Kästen sind die Schritte in ihrer Reihenfolge.${v.schritte.some((s) => s.eigen) ? " Gestrichelt: von der RIS-Karte ergänzte Schritte." : ""} Dieselben Schritte stehen unten als Liste.</p>`;
}
function wegeFor(vid, v) {
  const lanes = new Set(lanesOf(v));
  return (soll.mitwirken || []).filter((r) => {
    const w = r.wenn || {};
    if (!WEGE[r.id] || !(w.status || []).includes("offen")) return false;
    if (w.verfahren && !w.verfahren.includes(vid)) return false;
    if (w.nicht_verfahren && w.nicht_verfahren.includes(vid)) return false;
    if (r.id === "livestream" && !lanes.has("rat")) return false;
    if ((r.id === "einwohnerfrage" || r.id === "ansprechen-bv") && !lanes.has("bv")) return false;
    if (r.id === "ansprechen-rat" && !lanes.has("aus") && !lanes.has("rat")) return false;
    return true;
  });
}
function verfahrenBody(vid, v) {
  const z = (data.verfahren || {})[vid];
  const steps = `<ol class="pz-steps">${v.schritte.map((s) => `<li><strong>${esc(s.label)}</strong> <span class="pz-bahn">${esc(soll.bahnen[s.bahn] || "")}</span>
      ${s.was && s.was !== s.label ? `<br>${esc(s.was)}` : ""}${s.eigen ? ' <span class="derived">ergänzt von der RIS-Karte</span>' : ""}
      ${beleg(s) ? `<br><span class="hint">Rechtsgrundlage: ${beleg(s)}</span>` : ""}</li>`).join("")}</ol>`;
  const zahl = z ? `<p><strong>In Bonn:</strong> ${num(z.vorgaenge)} Vorgänge seit Oktober 2019 <span class="derived">abgeleitet</span>
      <span class="hint">(davon ${num(z.sicher)} mit hoher Sicherheit zugeordnet)</span></p>
      ${z.beispiele.length ? `<p class="pz-examples"><span class="hint">Jüngste Beispiele:</span> ${z.beispiele.map((b) => `<button type="button" class="btn btn-soft pz-open" data-ref="${esc(b.drucksache)}">${esc(b.drucksache)} · ${esc(b.titel.length > 70 ? b.titel.slice(0, 68) + "…" : b.titel)}</button>`).join(" ")}</p>` : ""}`
    : `<p class="hint">In den Daten ist kein Vorgang diesem Verfahren zugeordnet.</p>`;
  const wege = wegeFor(vid, v);
  return `<p>${esc(v.kurz || "")}</p>${zahl}
    <h4>Schritte</h4>${steps}
    ${wege.length ? `<h4>Wege, sich einzubringen</h4><ul class="pz-wege">${wege.map((r) => `<li><strong>${esc(WEGE[r.id])}</strong> <span class="hint">Frist: ${esc(r.frist)}</span>${beleg(r) ? `<br><span class="hint">Rechtsgrundlage: ${beleg(r)}</span>` : ""}</li>`).join("")}</ul>
      <p class="hint">Welche Wege bei einem bestimmten Vorgang offen sind, zeigt dort der Abschnitt „Selbst mitwirken“.</p>` : ""}`;
}
function fristen() {
  return `<details class="pz-more"><summary>Fristen vor einer Sitzung</summary><ul class="pz-wege">${(soll.fristen || []).map((f) => `<li><strong>${esc(f.label)}</strong>: ${esc(f.was)}${beleg(f) ? ` <span class="hint">(${beleg(f)})</span>` : ""}</li>`).join("")}</ul></details>`;
}
function renderVerfahren() {
  const ids = Object.keys(soll.verfahren);
  const count = (id) => (data.verfahren[id] || {}).vorgaenge || 0;
  if (state.view === "liste") {
    return `<p class="hint">${ids.length} Verfahrensarten nach dem Regelwerk der Stadt Bonn (vereinfachtes Modell, keine Rechtsauskunft).</p>
      ${ids.map((id) => `<details class="pz-item" data-verfahren="${esc(id)}"${state.verfahren === id ? " open" : ""}><summary><span class="pz-title">${esc(soll.verfahren[id].titel)}</span>
        <span class="pz-meta">${num(count(id))} Vorgänge</span></summary>${verfahrenBody(id, soll.verfahren[id])}</details>`).join("")}${fristen()}`;
  }
  const vid = soll.verfahren[state.verfahren] ? state.verfahren : "buergerantrag";
  const v = soll.verfahren[vid];
  return `<label class="pz-pick">Verfahren <select id="pz-verfahren">${ids.map((id) => `<option value="${esc(id)}"${id === vid ? " selected" : ""}>${esc(soll.verfahren[id].titel)} (${num(count(id))})</option>`).join("")}</select></label>
    <h3 class="pz-h">${esc(v.titel)}</h3>${swimlane(vid, v)}${verfahrenBody(vid, v)}${fristen()}`;
}

// --- Gremien -----------------------------------------------------------------------------------------
const meta = (g) => [g.naechste ? `nächste Sitzung ${deDate(g.naechste.datum)}` : g.letzte ? `zuletzt ${deDate(g.letzte)}` : "", g.aufgeloest ? `aufgelöst ${deDate(g.aufgeloest)}` : ""].filter(Boolean).join(" · ");
function zustaendig(g) {
  if (g.zusto && soll.zusto[g.zusto]) {
    const z = soll.zusto[g.zusto];
    const groups = RECHT.map(([art, label]) => [label, z.rechte.filter((r) => r.art === art)]).filter(([, rs]) => rs.length);
    return `<h4>Zuständigkeit laut Zuständigkeitsordnung (Abschnitt ${esc(z.nr)})</h4>
      ${g.zusto_hinweis ? `<p class="hint">${esc(g.zusto_hinweis)}</p>` : ""}
      ${groups.map(([label, rs]) => `<details class="pz-more"><summary>${esc(g.name)} ${esc(label)} (${rs.length})</summary><ul class="pz-recht">${rs.map((r) => `<li><span class="pz-nr">${esc(r.nr)}</span> ${esc(r.inhalt)}${r.an_bezirksvertretung ? ' <span class="hint">(Bezirksvertretung wird beteiligt)</span>' : ""}</li>`).join("")}</ul></details>`).join("")}
      <p class="hint">Quelle: <a href="${esc(soll.meta.zusto_url)}" target="_blank" rel="noopener">Zuständigkeitsordnung der Stadt Bonn<span class="visually-hidden"> (neuer Tab)</span></a>, Stand ${esc(soll.meta.zusto_stand || "")}.</p>`;
  }
  const rule = (re) => (soll.zustaendigkeit || []).filter((z) => re.test(`${z.frage} ${z.antwort}`));
  const rules = g.art === "bezirksvertretung" ? rule(/Bezirk|BV/) : g.art === "rat" || g.art === "hauptausschuss" ? rule(/Rat|Hauptausschuss/) : [];
  if (rules.length) return `<h4>Zuständigkeit nach Regelwerk</h4><dl class="pz-zust">${rules.map((z) => `<dt>${esc(z.frage)}</dt><dd>${esc(z.antwort)}${beleg(z) ? ` <span class="hint">(${beleg(z)})</span>` : ""}</dd>`).join("")}</dl>`;
  return `<p class="hint">Für dieses Gremium enthält das Regelwerk der RIS-Karte keinen eigenen Abschnitt.</p>`;
}
function gremiumBody(g) {
  return `<p><span class="pz-art">${esc(ART[g.art] || g.art)}</span>${g.aktuell ? "" : ' <span class="derived">nicht in der laufenden Wahlperiode</span>'}</p>
    <ul class="pz-facts">
      <li>${num(g.beratungen)} Beratungen zu ${num(g.vorlagen)} Vorlagen seit Oktober 2019</li>
      ${g.letzte ? `<li>Letzte Sitzung: ${deDate(g.letzte)}</li>` : ""}
      ${g.naechste ? `<li>Nächste Sitzung: ${g.naechste.web ? `<a href="${esc(g.naechste.web)}" target="_blank" rel="noopener">${deDate(g.naechste.datum)}<span class="visually-hidden"> (Tagesordnung, neuer Tab)</span></a>` : deDate(g.naechste.datum)}</li>` : ""}
      ${g.aufgeloest ? `<li>Aufgelöst: ${deDate(g.aufgeloest)}</li>` : ""}
    </ul>
    ${zustaendig(g)}
    <p class="pz-actions">${g.vorlagen ? `<button type="button" class="btn btn-soft pz-filter" data-name="${esc(g.name)}">Vorlagen dieses Gremiums in der Liste</button>` : ""}
      ${g.web ? `<a class="btn btn-ghost" href="${esc(g.web)}" target="_blank" rel="noopener">Im Ratsinformationssystem<span class="visually-hidden"> (neuer Tab)</span></a>` : ""}</p>
    <p class="pz-msg hint" aria-live="polite"></p>`;
}
const nodeBtn = (g) => `<button type="button" class="org-node org-${esc(g.art)}" data-gremium="${esc(g.id)}" aria-pressed="${state.gremium === g.id}">
  <span class="org-name">${esc(g.name)}</span><span class="org-meta">${esc(meta(g))}</span></button>`;
function renderGremien() {
  const all = data.gremien || [];
  const cur = all.filter((g) => g.aktuell);
  const by = (a) => cur.filter((g) => g.art === a);
  const sel = all.find((g) => g.id === state.gremium);
  const intro = `<details class="pz-more"><summary>Wer entscheidet was? Kurz erklärt</summary><dl class="pz-zust">${(soll.zustaendigkeit || []).map((z) => `<dt>${esc(z.frage)}</dt><dd>${esc(z.antwort)}${beleg(z) ? ` <span class="hint">(${beleg(z)})</span>` : ""}</dd>`).join("")}</dl></details>`;
  if (state.view === "liste") {
    const q = state.q.trim().toLowerCase();
    const shown = (state.frueher ? all : cur).filter((g) => !q || g.name.toLowerCase().includes(q));
    const groups = Object.keys(ART).map((a) => [a, shown.filter((g) => g.art === a)]).filter(([, gs]) => gs.length);
    return `${intro}<div class="pz-filterbar"><label>Gremium suchen <input type="search" id="pz-q" value="${esc(state.q)}" autocomplete="off"></label>
      <label class="check"><input type="checkbox" id="pz-frueher"${state.frueher ? " checked" : ""}> frühere Gremien zeigen</label></div>
      <p class="hint" aria-live="polite">${shown.length} Gremien</p>
      ${groups.map(([a, gs]) => `<h3 class="pz-h">${esc(ART_PL[a])}</h3>${gs.map((g) => `<details class="pz-item" data-gremium="${esc(g.id)}"${state.gremium === g.id ? " open" : ""}><summary><span class="pz-title">${esc(g.name)}</span><span class="pz-meta">${esc(meta(g))}</span></summary>${gremiumBody(g)}</details>`).join("")}`).join("")}`;
  }
  return `${intro}<div class="org" role="group" aria-label="Gremien der Stadt Bonn in der laufenden Wahlperiode">
      <div class="org-top">${by("rat").map(nodeBtn).join("")}</div>
      <div class="org-cols">
        <section class="org-col org-aus" aria-label="Ausschüsse des Rates"><h3 class="org-h">Ausschüsse des Rates</h3>
          <div class="org-haupt">${by("hauptausschuss").map(nodeBtn).join("")}</div>
          <div class="org-grid">${by("ausschuss").map(nodeBtn).join("")}</div></section>
        <section class="org-col org-bv" aria-label="Bezirksvertretungen"><h3 class="org-h">Bezirksvertretungen</h3>
          <div class="org-grid org-grid-1">${by("bezirksvertretung").map(nodeBtn).join("")}</div></section>
      </div>
      <section class="org-beirat" aria-label="Beiräte und Kommissionen"><h3 class="org-h">Beiräte und Kommissionen</h3>
        <div class="org-grid">${by("beirat").map(nodeBtn).join("")}</div></section>
      ${by("unterausschuss").length + by("wahlausschuss").length ? `<section class="org-beirat" aria-label="Weitere Gremien"><h3 class="org-h">Weitere Gremien</h3>
        <div class="org-grid">${[...by("unterausschuss"), ...by("wahlausschuss")].map(nodeBtn).join("")}</div></section>` : ""}
    </div>
    <p class="hint">Gezeigt sind die Gremien der laufenden Wahlperiode (seit ${deDate(data.meta.wahlperiode_seit)}); frühere stehen in der Liste. Der Rat entscheidet grundsätzlich; Ausschüsse und Bezirksvertretungen, soweit ihnen Aufgaben übertragen sind.</p>
    <div id="pz-detail" class="pz-detail" aria-live="polite">${sel ? `<h3 class="pz-h" tabindex="-1">${esc(sel.name)}</h3>${gremiumBody(sel)}` : `<p class="hint">Wählen Sie ein Gremium, um seine Zuständigkeit und Sitzungen zu sehen.</p>`}</div>`;
}

// --- Steuerung ---------------------------------------------------------------------------------------
function render(focusDetail) {
  root.querySelectorAll("[role=tab]").forEach((t) => {
    const on = t.dataset.tab === state.tab;
    t.setAttribute("aria-selected", String(on));
    t.tabIndex = on ? 0 : -1;
  });
  root.querySelectorAll("[data-view]").forEach((b) => {
    b.setAttribute("aria-checked", String(b.dataset.view === state.view));
    b.tabIndex = b.dataset.view === state.view ? 0 : -1;
  });
  const body = root.querySelector("#pz-body");
  body.setAttribute("aria-labelledby", `tab-pz-${state.tab}`);
  body.innerHTML = !soll || !data ? '<p class="hint">Die Daten zu den Prozessen sind nicht verfügbar.</p>'
    : state.tab === "gremien" ? renderGremien() : renderVerfahren();
  if (focusDetail) body.querySelector("#pz-detail h3")?.focus();
  ctx.onState({ ...state });
}
function set(patch, focusDetail) { Object.assign(state, patch); render(focusDetail); }

export async function init(c) {
  ctx = c;
  root = document.getElementById("panel-prozesse");
  [soll, data] = await Promise.all([ctx.loadSoll(), fetch(ctx.BONN + "prozessarten.json").then((r) => (r.ok ? r.json() : null)).catch(() => null)]);
  root.querySelector("[role=tablist]").addEventListener("click", (e) => { const t = e.target.closest("[role=tab]"); if (t) set({ tab: t.dataset.tab }); });
  root.querySelector("[role=tablist]").addEventListener("keydown", (e) => {
    if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
    e.preventDefault();
    set({ tab: state.tab === "verfahren" ? "gremien" : "verfahren" });
    root.querySelector(`[role=tab][data-tab="${state.tab}"]`).focus();
  });
  root.querySelector(".pz-view").addEventListener("click", (e) => { const b = e.target.closest("[data-view]"); if (b) set({ view: b.dataset.view }); });
  root.querySelector(".pz-view").addEventListener("keydown", (e) => {
    if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
    e.preventDefault();
    set({ view: state.view === "schaubild" ? "liste" : "schaubild" });
    root.querySelector(`[data-view="${state.view}"]`).focus();
  });
  const body = root.querySelector("#pz-body");
  body.addEventListener("change", (e) => {
    if (e.target.id === "pz-verfahren") set({ verfahren: e.target.value });
    if (e.target.id === "pz-frueher") set({ frueher: e.target.checked });
  });
  body.addEventListener("input", (e) => {
    if (e.target.id !== "pz-q") return;
    state.q = e.target.value;
    const pos = e.target.selectionStart;
    render();
    const q = root.querySelector("#pz-q");
    q.focus();
    q.setSelectionRange(pos, pos);
  });
  body.addEventListener("toggle", (e) => {
    const d = e.target;
    if (!d.matches?.("details.pz-item") || !d.open) return;
    if (d.dataset.verfahren) { state.verfahren = d.dataset.verfahren; ctx.onState({ ...state }); }
    if (d.dataset.gremium) { state.gremium = d.dataset.gremium; ctx.onState({ ...state }); }
  }, true);
  body.addEventListener("click", async (e) => {
    const n = e.target.closest(".org-node");
    if (n) return set({ gremium: n.dataset.gremium }, true);
    const o = e.target.closest(".pz-open");
    if (o) return ctx.openRef(o.dataset.ref);
    const f = e.target.closest(".pz-filter");
    if (f) {
      const ok = ctx.filterGremium(f.dataset.name);
      if (!ok) f.closest(".pz-item, .pz-detail").querySelector(".pz-msg").textContent =
        "Im gewählten Gebiet hat dieses Gremium keine Vorlage beraten. Wählen Sie oben ein anderes Gebiet, etwa einen Stadtbezirk.";
    }
  });
}
export function show(s) {
  if (s) Object.assign(state, Object.fromEntries(Object.entries(s).filter(([, v]) => v !== undefined && v !== null)));
  render();
}
