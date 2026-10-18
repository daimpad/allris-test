// RIS-Karte Bonn – Karte vollflächig, darüber Liste, Zeitleiste, Detail (Prozesslinie mit Evidenzstatus)
// und typische Wege. Liest die Exporte der Pipeline; ohne Gesamtexport Rückfall auf den Pilot Endenich.
(function () {
  "use strict";
  const BONN = "data/export/bonn/";
  const PILOT = "data/export/endenich/vorlagen.json";
  const GEO = { ortsteil: "data/geo/ortsteile_bonn.geojson", bezirk: "data/geo/stadtbezirke_bonn.geojson",
    bplan: "data/geo/bebauungsplaene_bonn.geojson" };
  const DEFAULT_AREA = "ortsteil:endenich";
  const REPO = "https://github.com/daimpad/allris-test";
  const RANK = { hoch: 3, mittel: 2, niedrig: 1 };
  const LIST_STEP = 200;
  const MOBILE = matchMedia("(max-width: 900px)");
  const NARROW = matchMedia("(max-width: 1279px)");
  const REDUCED = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const CONF = { hoch: "Ort gesichert", mittel: "Ort erschlossen", niedrig: "Ort unsicher" };
  const METHOD = {
    oparl_location: "Koordinate der Stadt (OParl)", strasse: "Straßenname im Titel",
    "strasse+ortsteil": "Straßen- und Ortsteilname im Titel", "strasse+bezirk": "Straßenname im Titel, Bezirk eingegrenzt",
    strasse_mehrdeutig: "Straßenname im Titel, mehrere Lagen", ortsteil_name: "Ortsteilname im Titel",
    ortsteil_adjektiv: "Ortsteil im Titel (z. B. „Endenicher …“)", stadtbezirk_name: "Stadtbezirk im Titel",
    stadtbezirk_adjektiv: "Stadtbezirk im Titel (Adjektiv)", vererbt: "von der übergeordneten Vorlage übernommen",
    bebauungsplan: "Bebauungsplan-Nummer im Titel, Geltungsbereich laut Stadt Bonn",
  };
  const STATUS = {
    belegt: "belegt", abgeleitet: "abgeleitet", soll: "soll", "nicht_öffentlich": "nicht öffentlich", unklar: "unklar",
  };
  // Glossar, Erläuterungen und Bezeichnungen der Prozessebene: data/export/glossar.json (pipeline/glossar.py)
  const GLOSSAR_URL = "data/export/glossar.json";
  let GLOSSAR = {}, NOTES = {}, STEP_LABEL = {}, STATUS_TEXT = {};
  const LIMITS = `<details class="acc"><summary>Was diese Darstellung nicht zeigen kann</summary><ul>
    <li>Verwaltungsinterne Abläufe vor dem Datum der Vorlage (Erarbeitung, Mitzeichnung, Freigaben).</li>
    <li>Den Vollzug von Beschlüssen: Die Beschlusskontrolle hat keine öffentliche Schnittstelle.</li>
    <li>Was das Regelwerk vorsieht (Soll): Zuständigkeitsordnung und Bezirkssatzung sind noch nicht formalisiert.</li>
    <li>Inhalte nichtöffentlicher Beratungen und Vorlagen vor Oktober 2019.</li>
    <li>Sitzungen und Ergebnisse, die OParl-Lite (noch) nicht verknüpft.</li></ul>
    <p class="hint">Abweichungen zwischen Regel und Ablauf sind Befunde, keine Bewertung.</p></details>`;
  const INTRO = `<div class="intro"><p><strong>So geht's:</strong> Oben ein Gebiet wählen, dann in der Liste oder auf der Karte eine Vorlage anklicken. Hier erscheint der Vorgang: wer ihn eingebracht hat, welches Amt zuständig ist und welche Gremien wann beraten haben.</p>
    <p>Eine <strong>Vorlage</strong> ist ein Schriftstück, über das Rat, Bezirksvertretung oder Ausschüsse beraten – etwa ein Antrag, eine Beschlussvorlage oder ein Bürgerantrag. Mehr unter „Über“.</p></div>${LIMITS}`;

  const $ = (s) => document.querySelector(s);
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  // nur http(s)-Adressen aus den Daten werden zu Links
  const safeUrl = (u) => (/^https?:\/\//i.test(String(u || "")) ? esc(u) : null);
  const ISO_DAY = /^\d{4}-\d{2}-\d{2}$/;
  const fmtDate = (iso) => iso ? new Date(iso.length === 10 ? iso + "T12:00:00Z" : iso)
    .toLocaleDateString("de-DE", { timeZone: "Europe/Berlin", day: "2-digit", month: "2-digit", year: "numeric" }) : "";
  const debounce = (fn, ms) => { let h; return (...a) => { clearTimeout(h); h = setTimeout(() => fn(...a), ms); }; };

  let index = null, zeit = null, geo = {}, meta = null, papers = [], area = null, selected = null, dataStand = null;
  let map, cluster, outline, markers = new Map(), tl = null, range = null, loadSeq = 0, shown = LIST_STEP, lastList = [];
  // Suche über ganz Bonn (suche.json, erst bei Bedarf geladen)
  let search = null, searchLoading = null;
  const THEMES = {  // wie pipeline/topics.THEMES
    verkehr: "Verkehr und Mobilität", bauen: "Bauen und Stadtentwicklung", umwelt: "Umwelt, Grün und Klima",
    bildung: "Schule und Bildung", kinder: "Kinder, Jugend und Familie", soziales: "Soziales, Wohnen und Gesundheit",
    kultur: "Kultur und Sport", wirtschaft: "Wirtschaft und Finanzen", sicherheit: "Sicherheit und Ordnung",
    beteiligung: "Beteiligung, Integration und Internationales",
  };
  const THEME_METHOD = { amt: "Amt", gremium: "Gremium", stichwort: "Stichwort im Titel" };

  // --- Flächen ein- und ausklappen ---------------------------------------------------------------
  const SHEETS = ["panel-list", "panel-detail", "panel-auswertung", "panel-termine", "timeline-wrap"];
  const OVERLAYS = ["panel-auswertung", "panel-termine"];
  const toggleFor = (id) => document.querySelector(`.toggle[data-panel="${id}"]`);
  function setPanel(id, open) {
    const el = document.getElementById(id);
    el.hidden = !open;
    document.querySelectorAll(`.toggle[data-panel="${id}"]`).forEach((b) => b.setAttribute("aria-pressed", String(open)));
    if (id === "panel-list") { document.body.classList.toggle("list-open", open); document.body.classList.toggle("list-closed", !open); }
    if (id === "panel-detail") { document.body.classList.toggle("detail-open", open); document.body.classList.toggle("detail-closed", !open); }
    if (!open) return;
    closeMega();
    // schmale Bildschirme: nur eine Fläche; mittlere Breiten: Liste oder Vorgang, damit die Zeitleiste Platz hat;
    // Auswertung und Termine liegen mittig übereinander, daher immer nur eines davon
    const others = MOBILE.matches ? SHEETS : OVERLAYS.includes(id) ? OVERLAYS
      : NARROW.matches && (id === "panel-list" || id === "panel-detail") ? ["panel-list", "panel-detail"] : [];
    for (const other of others) if (other !== id && !document.getElementById(other).hidden) setPanel(other, false);
  }
  function focusPanel(id) {
    const el = document.getElementById(id);
    const target = el.querySelector("h2[tabindex], .tl-stage, summary");
    if (target) target.focus();
  }
  function closePanel(id) {
    setPanel(id, false);
    const t = toggleFor(id);
    if (t && t.offsetParent) t.focus();
  }
  document.addEventListener("click", (e) => {
    const t = e.target.closest("[data-panel]");
    if (t) {
      const open = document.getElementById(t.dataset.panel).hidden;
      setPanel(t.dataset.panel, open);
      if (open) focusPanel(t.dataset.panel);
    }
    const c = e.target.closest("[data-close]");
    if (c) closePanel(c.dataset.close);
  });
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape" || $("#about").open) return;
    if (openMegaId) return closeMega(true);
    const overlay = OVERLAYS.find((id) => !document.getElementById(id).hidden);
    if (overlay) return closePanel(overlay);
    const inside = SHEETS.find((id) => document.getElementById(id).contains(document.activeElement));
    if (inside) closePanel(inside);
  });
  function applyLayout() {
    if (MOBILE.matches) {
      const open = SHEETS.filter((id) => !document.getElementById(id).hidden);
      open.slice(1).forEach((id) => setPanel(id, false));
    } else if (NARROW.matches && !$("#panel-list").hidden && !$("#panel-detail").hidden) setPanel("panel-detail", false);
    $("#timeline-wrap").classList.toggle("tl-compact", MOBILE.matches);
    clampWidths();
    if (tl) tl.select(selected);
  }

  // --- Mega-Menüs ------------------------------------------------------------------------------------
  let openMegaId = null;
  function openMega(id, trigger) {
    if (openMegaId && openMegaId !== id) closeMega();
    const el = document.getElementById(id);
    el.hidden = false;
    openMegaId = id;
    el.dataset.trigger = trigger ? trigger.id || "" : "";
    document.querySelectorAll(`[data-mega="${id}"]`).forEach((b) => b.setAttribute("aria-expanded", "true"));
    if (id === "mega-suche") fillChips();
    if (id === "mega-mitmachen") fillMitmachen();
    if (MOBILE.matches) SHEETS.forEach((s) => !document.getElementById(s).hidden && setPanel(s, false));
  }
  function closeMega(returnFocus) {
    if (!openMegaId) return;
    const id = openMegaId;
    document.getElementById(id).hidden = true;
    openMegaId = null;
    document.querySelectorAll(`[data-mega="${id}"]`).forEach((b) => b.setAttribute("aria-expanded", "false"));
    if (returnFocus) (id === "mega-suche" ? $("#q") : document.querySelector(`[data-mega="${id}"]`)).focus();
  }
  document.addEventListener("click", (e) => {
    const m = e.target.closest("[data-mega]");
    if (m) {
      const id = m.dataset.mega;
      if (openMegaId === id) closeMega(); else { openMega(id, m); const f = document.getElementById(id).querySelector("button, a, input"); if (f && e.detail === 0) f.focus(); }
      return;
    }
    // Klick außerhalb schließt das Menü (das Suchfeld gehört zum Suchmenü)
    // (Ziele, die beim Klick neu aufgebaut wurden, z. B. Chips, sind nicht mehr im Dokument)
    if (openMegaId && e.target.isConnected && !e.target.closest(".mega") && !e.target.closest("#nav-search")) closeMega();
  });

  // --- Breite von Liste und Vorgang per Ziehgriff ---------------------------------------------------
  const WIDTH = { list: { v: "--list-w", min: 300, max: () => Math.min(680, innerWidth * 0.45), def: 360 },
    detail: { v: "--detail-w", min: 340, max: () => Math.min(760, innerWidth * 0.5), def: 420 } };
  const widthOf = (k) => parseFloat(getComputedStyle(document.documentElement).getPropertyValue(WIDTH[k].v)) || WIDTH[k].def;
  function setWidth(k, px, save) {
    const w = WIDTH[k], v = Math.round(Math.max(w.min, Math.min(w.max(), px)));
    document.documentElement.style.setProperty(w.v, v + "px");
    const r = document.querySelector(`.resizer[data-resize="${k}"]`);
    r.setAttribute("aria-valuemin", String(w.min)); r.setAttribute("aria-valuemax", String(Math.round(w.max())));
    r.setAttribute("aria-valuenow", String(v)); r.setAttribute("aria-valuetext", `${v} Pixel breit`);
    if (save) { try { localStorage.setItem("ris-breite-" + k, String(v)); } catch (e) { /* ohne Speicher */ } }
  }
  function clampWidths() { for (const k of Object.keys(WIDTH)) setWidth(k, widthOf(k)); }
  for (const k of Object.keys(WIDTH)) {
    try { const v = Number(localStorage.getItem("ris-breite-" + k)); if (v) document.documentElement.style.setProperty(WIDTH[k].v, v + "px"); } catch (e) { /* ohne Speicher */ }
  }
  document.querySelectorAll(".resizer").forEach((r) => {
    const k = r.dataset.resize, sign = k === "list" ? 1 : -1;
    r.addEventListener("pointerdown", (e) => {
      e.preventDefault();
      r.setPointerCapture(e.pointerId);
      const x0 = e.clientX, w0 = widthOf(k);
      r.classList.add("active"); document.body.classList.add("resizing");
      const move = (ev) => setWidth(k, w0 + sign * (ev.clientX - x0));
      const up = () => { r.removeEventListener("pointermove", move); r.classList.remove("active"); document.body.classList.remove("resizing"); setWidth(k, widthOf(k), true); };
      r.addEventListener("pointermove", move);
      r.addEventListener("pointerup", up, { once: true });
      r.addEventListener("pointercancel", up, { once: true });
    });
    r.addEventListener("keydown", (e) => {
      const step = e.shiftKey ? 64 : 16;
      const map = { ArrowRight: sign * step, ArrowLeft: -sign * step };
      if (map[e.key] !== undefined) { e.preventDefault(); setWidth(k, widthOf(k) + map[e.key], true); }
      if (e.key === "Home") { e.preventDefault(); setWidth(k, WIDTH[k].def, true); }
    });
    r.addEventListener("dblclick", () => setWidth(k, WIDTH[k].def, true));
  });

  // --- Über ----------------------------------------------------------------------------------------
  $("#about-open").addEventListener("click", () => { closeMega(); $("#about").showModal(); });
  $("#about-close").addEventListener("click", () => $("#about").close());
  $("#about").addEventListener("click", (e) => { if (e.target === e.currentTarget) e.currentTarget.close(); });
  document.addEventListener("click", (e) => {
    const b = e.target.closest("[data-about]");
    if (!b) return;
    closeMega();
    $("#about").showModal();
    const h = document.getElementById("about-" + b.dataset.about);
    if (h) { h.scrollIntoView({ block: "start" }); h.focus(); }
  });

  // --- Gebiet ----------------------------------------------------------------------------------------
  function parseArea(value) {
    const [kind, key] = (value || "").split(":");
    if (!index) return { kind: "ortsteil", key: "endenich", name: "Endenich", file: PILOT };
    if (kind === "ortsteil") {
      const o = index.ortsteile.find((x) => x.slug === key);
      if (o) return { kind, key, name: o.name, file: `${BONN}ortsteile/${key}.json` };
    }
    if (kind === "bezirk") {
      const b = index.bezirke.find((x) => x.slug === key);
      if (b) return { kind, key, name: b.name, file: `${BONN}bezirke/${key}.json` };
    }
    if (kind === "ohne" && index.ohne_ortsbezug.some((x) => x.jahr === key)) {
      return { kind, key, name: `ohne Ortsbezug ${key}`, file: `${BONN}ohne-ortsbezug/${key}.json` };
    }
    if (value !== DEFAULT_AREA) return parseArea(DEFAULT_AREA);
    const first = index.ortsteile[0];
    return { kind: "ortsteil", key: first.slug, name: first.name, file: `${BONN}ortsteile/${first.slug}.json` };
  }
  function fillAreaSelect() {
    const sel = $("#f-area");
    if (!index) { sel.innerHTML = '<option value="ortsteil:endenich">Endenich (Pilot)</option>'; return; }
    const groups = {};
    index.ortsteile.forEach((o) => (groups[o.stadtbezirk] ||= []).push(o));
    let html = "";
    for (const bz of Object.keys(groups).sort()) {
      html += `<optgroup label="Stadtbezirk ${esc(bz)}">` + groups[bz].sort((a, b) => a.name.localeCompare(b.name, "de"))
        .map((o) => `<option value="ortsteil:${o.slug}">${esc(o.name)} (${o.count})</option>`).join("");
      const b = index.bezirke.find((x) => x.name === bz);
      if (b && b.count) html += `<option value="bezirk:${b.slug}">ganzer Stadtbezirk ${esc(bz)}, ohne genaueren Ort (${b.count})</option>`;
      html += "</optgroup>";
    }
    html += '<optgroup label="Stadtweit / ohne Ortsbezug">' + index.ohne_ortsbezug
      .map((y) => `<option value="ohne:${y.jahr}">${y.jahr} (${y.count})</option>`).join("") + "</optgroup>";
    sel.innerHTML = html;
  }
  function areaLocs(p) {
    if (area.kind === "ortsteil") return p.locations.filter((l) => l.ortsteil === area.name);
    if (area.kind === "bezirk") return p.locations.filter((l) => l.level === "stadtbezirk" && l.stadtbezirk === area.name);
    return [];
  }
  const bestConfidence = (p) => areaLocs(p).reduce((b, l) => (RANK[l.confidence] > RANK[b] ? l.confidence : b), "niedrig");

  function setLoading(on) {
    $("#papers").setAttribute("aria-busy", String(on));
    $("#panel-list").classList.toggle("loading", on);
  }
  async function loadArea(value, keepState) {
    const seq = ++loadSeq;
    const next = parseArea(value);
    $("#f-area").value = `${next.kind}:${next.key}`;
    $("#count").textContent = `Lade Vorlagen für ${next.name} …`;
    setLoading(true);
    let data;
    try {
      const r = await fetch(next.file);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      data = await r.json();
    } catch (err) {
      if (seq !== loadSeq) return;
      setLoading(false);
      $("#count").innerHTML = `Die Vorlagen für ${esc(next.name)} konnten nicht geladen werden (${esc(err.message)}). <button type="button" class="btn btn-secondary" id="retry">Erneut versuchen</button>`;
      $("#retry").addEventListener("click", () => loadArea(value, keepState));
      return;
    }
    // ein späterer Gebietswechsel hat diese Antwort überholt
    if (seq !== loadSeq) return;
    setLoading(false);
    area = next;
    meta = data.meta;
    if (index && index.meta) meta = { ...meta, generated_at: index.meta.generated_at, sources: index.meta.sources };
    const oparl = meta.sources.find((s) => s.name === "oparl-bonn") || {};
    dataStand = (oparl.retrieved_at || meta.generated_at || new Date().toISOString()).slice(0, 10);
    papers = data.papers;
    document.title = `RIS-Karte Bonn – ${area.kind === "ohne" ? "Vorlagen ohne Ortsbezug " + area.key : area.name}`;
    $("#f-conf").hidden = area.kind === "ohne";
    fillFilters();
    drawOutline();
    selected = null;
    shown = LIST_STEP;
    if (!keepState) $("#detail").innerHTML = INTRO;
    if (tl && zeit) {
      const series = zeit.areas[`${area.kind}:${area.key}`] || zeit.areas.gesamt;
      tl.setData({ months: zeit.months, categories: zeit.categories, density: series, meetings: zeit.meetings,
        terms: zeit.terms, dataStart: zeit.data_start, dataStand });
      tl.select(null);
    }
    subscribeArea();
    if (!$("#panel-termine").hidden) showTermine();
    if (!$("#panel-auswertung").hidden && !$("#stats").hidden) showStats();
    render();
    syncUrl();
    const stand = meta.sources.map((s) => `${s.name}: ${String(s.retrieved_at || "–").slice(0, 10)}`).join(" · ");
    $("#stand").textContent = `Datenstand: ${stand}${meta.generated_at ? ` · erzeugt ${meta.generated_at.slice(0, 10)}` : ""}`;
  }

  // --- Karte -----------------------------------------------------------------------------------------
  const MARKER = { radius: 7, weight: 2, color: "#fff", fillOpacity: 0.95 };
  function initMap() {
    map = L.map("map", { zoomControl: false, scrollWheelZoom: true, zoomAnimation: !REDUCED, fadeAnimation: !REDUCED, markerZoomAnimation: !REDUCED });
    L.control.zoom({ position: "bottomright" }).addTo(map);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 19, attribution: "© OpenStreetMap-Mitwirkende" }).addTo(map);
    // Kartenhintergrund standardmäßig grau, damit die Marker hervortreten; die Wahl merkt sich der Browser
    let colored = false;
    try { colored = localStorage.getItem("ris-karte-farbig") === "1"; } catch (e) { /* ohne Speicher: grau */ }
    const MapStyle = L.Control.extend({
      options: { position: "bottomright" },
      onAdd() {
        const b = L.DomUtil.create("button", "map-style");
        b.type = "button";
        b.textContent = "Farbige Karte";
        const apply = () => {
          document.getElementById("map").classList.toggle("map-gray", !colored);
          b.setAttribute("aria-pressed", String(colored));
        };
        b.addEventListener("click", () => {
          colored = !colored;
          try { localStorage.setItem("ris-karte-farbig", colored ? "1" : "0"); } catch (e) { /* nicht speicherbar */ }
          apply();
        });
        L.DomEvent.disableClickPropagation(b);
        apply();
        return b;
      },
    });
    new MapStyle().addTo(map);
    cluster = L.markerClusterGroup({ showCoverageOnHover: false, maxClusterRadius: 40, animate: !REDUCED }).addTo(map);
  }
  function mapPadding() {
    const desktop = !MOBILE.matches;
    const left = desktop && !$("#panel-list").hidden ? widthOf("list") + 32 : 16;
    const right = desktop && !$("#panel-detail").hidden ? widthOf("detail") + 32 : 16;
    const top = desktop && !$("#timeline-wrap").hidden ? 86 + $("#timeline-wrap").offsetHeight + 12 : 90;
    return { paddingTopLeft: [left, top], paddingBottomRight: [right, desktop ? 70 : 150], animate: !REDUCED };
  }
  function drawOutline() {
    if (outline) outline.remove();
    let feature = null;
    if (area.kind === "ortsteil") feature = geo.ortsteil.features.find((f) => f.properties.ortsteil_bez === area.name);
    if (area.kind === "bezirk") feature = geo.bezirk.features.find((f) => f.properties.bezirk_bez === area.name);
    outline = L.geoJSON(feature || geo.bezirk, { style: { color: "#7c3aed", weight: 2, fillColor: "#c4b5fd", fillOpacity: 0.12 }, interactive: false }).addTo(map);
    map.fitBounds(outline.getBounds(), mapPadding());
  }
  const color = (c) => getComputedStyle(document.documentElement).getPropertyValue("--" + c).trim();
  function drawMarkers(list) {
    cluster.clearLayers();
    markers.clear();
    for (const p of list) {
      const ms = areaLocs(p).filter((l) => (l.level === "strasse" || l.level === "bebauungsplan") && l.lon != null).map((l) => {
        const m = L.circleMarker([l.lat, l.lon], { ...MARKER, fillColor: color(l.confidence) })
          .bindTooltip(`${esc(p.reference)} · ${esc(l.name)}`).on("click", () => select(p, true));
        m.baseColor = color(l.confidence);
        return m;
      });
      ms.forEach((m) => cluster.addLayer(m));
      markers.set(p.reference, ms);
    }
    highlight();
  }
  // gewählte Vorlage auf der Karte hervorheben
  function highlight() {
    for (const [ref, ms] of markers) {
      const on = selected && ref === selected.reference;
      ms.forEach((m) => { m.setStyle(on ? { radius: 11, weight: 3, color: "#0f0f14" } : { radius: MARKER.radius, weight: MARKER.weight, color: MARKER.color }); if (on) m.bringToFront(); });
    }
  }

  // --- Liste und Filter ------------------------------------------------------------------------------
  function options(sel, values) {
    const cur = sel.value;
    sel.innerHTML = '<option value="">alle</option>' + values.map((v) => `<option value="${esc(v)}">${esc(v)}</option>`).join("");
    if (values.includes(cur)) sel.value = cur;
  }
  function fillFilters() {
    const uniq = (a) => [...new Set(a.filter(Boolean))].sort((x, y) => x.localeCompare(y, "de"));
    options($("#f-type"), uniq(papers.map((p) => p.paper_type)));
    options($("#f-amt"), uniq(papers.map((p) => p.amt)));
    options($("#f-gremium"), uniq(papers.flatMap((p) => p.process.map((s) => s.gremium))));
    fillParties();
  }
  function fillParties() {
    const sel = $("#f-party"), cur = sel.value;
    const list = scope() === "bonn" && search ? search.parties : [...new Set(papers.flatMap((p) => p.parties || []))];
    // Fraktionen und Gruppen zuerst, dann Koalition, interfraktionell, Einwohner:innen, Verwaltung
    const other = ["Koalition", "interfraktionell", "Einwohner:innen", "Verwaltung"];
    const sorted = [...list.filter((x) => !other.includes(x)).sort((a, b) => a.localeCompare(b, "de")), ...other.filter((x) => list.includes(x))];
    sel.innerHTML = '<option value="">alle</option>' + sorted.map((v) => `<option value="${esc(v)}">${esc(v === "Koalition" ? "Koalition (gemeinsamer Antrag)" : v)}</option>`).join("");
    if (sorted.includes(cur)) sel.value = cur;
  }
  const scope = () => (document.querySelector('input[name="scope"]:checked') || {}).value || "gebiet";
  function loadSearch() {
    if (search || !index) return Promise.resolve(search);
    return (searchLoading ||= fetch(BONN + "suche.json").then((r) => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
      .then((d) => {
        d.related = new Map(d.rows.map((r) => [r[0], new Set(r[8].map((i) => d.parties[i]))]));
        search = d;
        return d;
      }).catch((err) => { searchLoading = null; $("#count").textContent = `Der Suchindex konnte nicht geladen werden (${err.message}).`; return null; }));
  }
  // Parteien der übergeordneten Vorlage (z. B. Stellungnahme der Verwaltung zu einem Antrag)
  const relatedParties = (ref) => (search && search.related.get(ref)) || new Set();
  function inRange(p) {
    if (!range) return true;
    const [a, b] = range, dim = tl ? tl.dimension() : "vorlage";
    if (dim === "vorlage") return p.date >= a && p.date <= b;
    return p.steps.some((s) => (s.typ === "beratung" || s.typ === "entscheidung") && s.date && s.date >= a && s.date <= b);
  }
  function filtered(withRange = true) {
    const text = $("#f-text").value.trim().toLowerCase(), type = $("#f-type").value, amt = $("#f-amt").value;
    const gremium = $("#f-gremium").value, standF = $("#f-stand").value;
    const theme = $("#f-theme").value, party = $("#f-party").value, rel = $("#f-related").checked;
    const confs = new Set([...document.querySelectorAll("#f-conf input:checked")].map((i) => i.value));
    return papers.filter((p) => (!type || p.paper_type === type) && (!amt || p.amt === amt) &&
      (!theme || (p.themes || []).some((t) => t.theme === theme)) &&
      (!party || (p.parties || []).includes(party) || (rel && relatedParties(p.reference).has(party))) &&
      (!gremium || p.process.some((s) => s.gremium === gremium)) && (!standF || p.stand === standF) &&
      (area.kind === "ohne" || confs.has(bestConfidence(p))) && (!withRange || inRange(p)) &&
      (!text || (p.name + " " + p.reference).toLowerCase().includes(text)));
  }
  function resetFilters() {
    const sc = scope();
    $("#filters").reset();
    document.querySelector(`input[name="scope"][value="${sc}"]`).checked = true;
    $("#f-related-wrap").hidden = true;
    range = null;
    if (tl) tl.reset();
    shown = LIST_STEP;
    render();
    syncUrl();
  }
  function itemHtml(p) {
    const c = bestConfidence(p);
    const conf = area.kind === "ohne" ? "" : `<span class="conf conf-${c}">${CONF[c]}</span>`;
    return `<li><button type="button" data-ref="${esc(p.reference)}" aria-current="${selected === p}">
      <span class="title">${esc(p.name)}</span>
      <span class="meta"><span>${esc(p.reference)}</span><span>${fmtDate(p.date)}</span><span>${esc(p.paper_type)}</span>
      <span>${esc(p.stand)}</span>${conf}${themeTags(p.themes)}</span></button></li>`;
  }
  const themeTags = (ts) => (ts || []).slice(0, 2).map((t) => `<span class="theme">${esc(THEMES[t.theme || t])}</span>`).join("");

  // Suche über ganz Bonn: Treffer aus dem Index, Öffnen lädt das Gebiet der Vorlage
  function renderGlobal() {
    const text = $("#f-text").value.trim().toLowerCase(), type = $("#f-type").value, standF = $("#f-stand").value;
    const theme = search.themes.findIndex((t) => t.id === $("#f-theme").value), party = search.parties.indexOf($("#f-party").value);
    const rel = $("#f-related").checked, ti = search.types.indexOf(type), si = search.stands.indexOf(standF);
    const rows = search.rows.filter((r) => (!type || r[3] === ti) && (!standF || r[4] === si) && (theme < 0 || r[6].includes(theme)) &&
      (party < 0 || r[7].includes(party) || (rel && r[8].includes(party))) && (!range || (r[2] && r[2] >= range[0] && r[2] <= range[1])) &&
      (!text || (r[1] + " " + r[0]).toLowerCase().includes(text)));
    const span = range ? ` · ${fmtDate(range[0])}–${fmtDate(range[1])}` : "";
    $("#count").textContent = `${rows.length} Treffer in ganz Bonn${span}`;
    let html = rows.slice(0, shown).map((r) => `<li><button type="button" data-gref="${esc(r[0])}" data-area="${esc(search.areas[r[5]].key)}" aria-current="${selected && selected.reference === r[0]}">
      <span class="title">${esc(r[1])}</span>
      <span class="meta"><span>${esc(r[0])}</span><span>${fmtDate(r[2])}</span><span>${esc(search.types[r[3]] || "")}</span>
      <span>${esc(search.stands[r[4]])}</span><span class="area-tag">${esc(search.areas[r[5]].name)}</span>${themeTags(r[6].slice(0, 2).map((i) => search.themes[i].id))}</span></button></li>`).join("");
    if (rows.length > shown) html += `<li class="more"><button type="button" class="btn btn-secondary" id="more">Weitere ${Math.min(LIST_STEP, rows.length - shown)} von ${rows.length - shown} anzeigen</button></li>`;
    if (!rows.length) html = `<li class="empty-list"><p>Keine Vorlage in ganz Bonn passt zu Filtern und Zeitraum.</p><button type="button" class="btn btn-secondary" id="reset-filters">Filter und Zeitraum zurücksetzen</button></li>`;
    $("#papers").innerHTML = html;
    // auf der Karte: die Treffer, die im gerade geladenen Gebiet liegen
    const refs = new Set(rows.map((r) => r[0]));
    drawMarkers(papers.filter((p) => refs.has(p.reference)));
    if (openMegaId === "mega-suche") $("#mega-count").textContent = $("#count").textContent;
  }
  async function openGlobal(ref, areaKey) {
    if (!area || `${area.kind}:${area.key}` !== areaKey) await loadArea(areaKey, true);
    const p = papers.find((x) => x.reference === ref);
    if (p) select(p);
  }

  function render() {
    $("#f-related-wrap").hidden = !$("#f-party").value;
    $("#more-filters").hidden = scope() === "bonn";
    if (scope() === "bonn") {
      if (!search) { $("#count").textContent = "Lade den Suchindex für ganz Bonn …"; loadSearch().then((d) => d && (fillParties(), render())); return; }
      return renderGlobal();
    }
    if ($("#f-party").value && $("#f-related").checked && !search && index) { loadSearch().then((d) => d && render()); }
    const base = filtered(false);
    const list = range ? base.filter(inRange) : base;
    lastList = list;
    const where = area.kind === "ohne" ? `ohne Ortsbezug, ${area.key}` : area.name;
    const span = range ? ` · ${fmtDate(range[0])}–${fmtDate(range[1])}` : "";
    $("#count").textContent = `${list.length} von ${papers.length} Vorlagen · ${where}${span}`;
    const active = [$("#f-amt").value, $("#f-gremium").value].filter(Boolean).length +
      (area.kind === "ohne" ? 0 : document.querySelectorAll("#f-conf input:not(:checked)").length);
    $("#active-filters").textContent = active ? ` (${active} aktiv)` : "";
    let html = list.slice(0, shown).map(itemHtml).join("");
    if (list.length > shown) html += `<li class="more"><button type="button" class="btn btn-secondary" id="more">Weitere ${Math.min(LIST_STEP, list.length - shown)} von ${list.length - shown} anzeigen</button></li>`;
    if (!list.length) html = `<li class="empty-list"><p>Keine Vorlage passt zu Gebiet, Filtern und Zeitraum.</p><button type="button" class="btn btn-secondary" id="reset-filters">Filter und Zeitraum zurücksetzen</button></li>`;
    $("#papers").innerHTML = html;
    drawMarkers(list);
    if (tl) tl.setPapers(base);
    if (openMegaId === "mega-suche") $("#mega-count").textContent = $("#count").textContent;
  }
  const renderSoon = debounce(() => { shown = LIST_STEP; render(); }, 200);

  // --- Detail: Prozesslinie mit Evidenzstatus -------------------------------------------------------
  const glossKeys = (t) => (t ? t.split(" - ").map((x) => x.trim()).filter((x) => GLOSSAR[x]) : []);
  function stepHtml(s) {
    const status = s.status;
    const mark = status === "unklar" ? "?" : "";
    const dateLine = s.date ? `${fmtDate(s.date)}${s.date_status === "abgeleitet" ? " · Datum abgeleitet (OParl-Lite)" : ""}` : "";
    const body = [];
    if (s.typ === "initiierung" && s.actors && s.actors.length) body.push(`Eingereicht von ${esc(s.actors.join(", "))} <span class="derived">abgeleitet</span>`);
    if (s.role) body.push(`${esc(s.role)}${s.typ === "entscheidung" ? " (entscheidet)" : ""}${s.number ? ` · TOP ${esc(s.number)}` : ""}`);
    if (s.result) body.push(`Ergebnis: <q>${esc(s.result)}</q>${s.schleife ? " · Schleife" : ""}`);
    if (s.typ === "folgevorlage") body.push(`${esc(s.reference)} – ${esc(s.title)}`);
    if (dateLine) body.push(dateLine);
    if (s.date) body.push(`<button type="button" class="jump" data-date="${esc(s.date)}">in der Zeitleiste zeigen</button>`);
    const box = s.note && (status === "nicht_öffentlich" || status === "unklar" || s.note === "ohne_sitzung")
      ? `<div class="blackbox">${esc(NOTES[s.note])}</div>` : (s.note ? `<div class="hint">${esc(NOTES[s.note])}</div>` : "");
    const cls = s.date_status === "abgeleitet" ? " date-derived" : "";
    const label = s.label && s.label !== STEP_LABEL[s.typ] ? ": " + esc(s.label) : "";
    return `<li class="step${cls}" data-status="${esc(status)}">
      <span class="mark mark-${esc(status)}" aria-hidden="true">${mark}</span>
      <div class="step-head">${esc(STEP_LABEL[s.typ] || s.typ)}${label}<span class="step-status">${esc(STATUS[status])}</span></div>
      <div class="step-body">${body.join("<br>")}${box}</div></li>`;
  }
  function legend() {
    return `<details class="acc"><summary>Legende Evidenzstatus</summary><div class="legend">${["belegt", "abgeleitet", "nicht_öffentlich", "unklar"]
      .map((s) => `<span><span class="mark mark-${s}" aria-hidden="true">${s === "unklar" ? "?" : ""}</span><strong>${STATUS[s]}</strong> – ${STATUS_TEXT[s] || ""}</span>`).join("")}
      <span class="hint">Linie: durchgezogen = belegt, gestrichelt = abgeleitet, gepunktet = nicht öffentlich oder unklar.</span></div></details>`;
  }
  function glossary(p) {
    const keys = [...new Set(p.process.flatMap((s) => [...glossKeys(s.result), ...glossKeys(s.role)]))];
    if (!keys.length) return "";
    return `<details class="acc glossary"><summary>Was bedeuten die Begriffe?</summary><div><dl>${keys
      .map((k) => `<dt>${esc(k)}</dt><dd>${esc(GLOSSAR[k])}</dd>`).join("")}</dl>
      <p class="hint">Erläuterung allgemein; maßgeblich ist das Original.</p></div></details>`;
  }
  function reportLink(p) {
    const q = new URLSearchParams({ template: "verortung.yml", title: `Verortung prüfen: ${p.reference}`, drucksache: p.reference, titel: p.name, gebiet: area.name });
    return `${REPO}/issues/new?${q}`;
  }
  const link = (url, text, cls) => { const u = safeUrl(url); return u ? `<a ${cls ? `class="${cls}" ` : ""}href="${u}" target="_blank" rel="noopener">${text}</a>` : ""; };
  // Bebauungspläne: Geltungsbereiche der Stadt (CC0), erst bei Bedarf geladen
  let plansData = null, planLayer = null;
  const loadPlans = () => (plansData ||= fetch(GEO.bplan).then((r) => (r.ok ? r.json() : { features: [] })).catch(() => ({ features: [] })));
  async function showPlans(p, fit) {
    if (planLayer) { planLayer.remove(); planLayer = null; }
    const nrs = (p.plans || []).filter((x) => x.area).map((x) => x.nr);
    if (!nrs.length) return;
    const data = await loadPlans();
    if (selected !== p) return;
    const feats = data.features.filter((f) => nrs.includes(f.properties.name.split(" ")[0]));
    planLayer = L.geoJSON({ type: "FeatureCollection", features: feats }, {
      style: { color: "#0f0f14", weight: 2, dashArray: "6 4", fillColor: "#7c3aed", fillOpacity: 0.12 }, interactive: false,
    }).addTo(map);
    if (fit && feats.length) map.fitBounds(planLayer.getBounds(), { ...mapPadding(), maxZoom: 17 });
    for (const nr of nrs) {
      const li = document.querySelector(`#detail .plans li[data-plan="${CSS.escape(nr)}"] .plan-meta`);
      if (!li) continue;
      li.innerHTML = feats.filter((f) => f.properties.name.split(" ")[0] === nr).map((f) =>
        `– ${f.properties.name !== nr ? esc(f.properties.name) + ", " : ""}rechtskräftig seit ${fmtDate(f.properties.inkraft_seit)} · ${link(f.properties.plan, "Plan (PDF)")}${f.properties.begruendung ? " · " + link(f.properties.begruendung, "Begründung (PDF)") : ""}`).join("<br>");
    }
  }

  function select(p, fromMap) {
    selected = p;
    document.querySelectorAll(".papers button[data-ref]").forEach((b) => b.setAttribute("aria-current", String(b.dataset.ref === p.reference)));
    syncUrl();
    if (tl) tl.select(p);
    highlight();
    const resp = p.responsibility.map((r) => `${esc(r.label)}${r.derived ? ` <span class="derived">abgeleitet, über ${esc(r.evidence)}</span>` : ""}`).join("<br>");
    const locs = p.locations.length ? p.locations.map((l) => `<li><strong>${esc(l.name || l.ortsteil || l.stadtbezirk)}</strong>
      ${l.ortsteil && l.level === "strasse" ? `(${esc(l.ortsteil)})` : ""} – <span class="conf conf-${esc(l.confidence)}">${CONF[l.confidence] || esc(l.confidence)}</span>, Stufe ${esc(l.stage)}<br>
      <span class="meta">${esc(METHOD[l.method] || l.method)}${l.evidence ? ` · Fundstelle: „${esc(l.evidence)}“` : ""}</span></li>`).join("")
      : "<li>stadtweit / ohne Ortsbezug</li>";
    const rel = (arr) => arr.map((r) => `<li>${esc(r.reference)} · ${esc(r.paper_type)} – ${esc(r.name)}</li>`).join("");
    const sources = meta.sources.map((s) => `<li>${esc(s.name)}: ${esc(s.license)}${s.retrieved_at ? ` · Abruf ${esc(String(s.retrieved_at).slice(0, 10))}` : ""}</li>`).join("");
    $("#detail").innerHTML = `
      <h3 tabindex="-1">${esc(p.name)}</h3>
      <dl class="facts">
        <dt>Drucksache</dt><dd>${esc(p.reference)}</dd>
        <dt>Art</dt><dd>${esc(p.paper_type)}</dd>
        <dt>Datum</dt><dd>${fmtDate(p.date)}</dd>
        <dt>Amt</dt><dd>${resp || esc(p.amt)}</dd>
        <dt>Stand</dt><dd>${esc(p.stand)}</dd>
        <dt>Themen</dt><dd>${(p.themes || []).length ? p.themes.map((t) => `${esc(THEMES[t.theme])} <span class="derived">abgeleitet, über ${esc(THEME_METHOD[t.method])} „${esc(t.evidence)}“</span>`).join("<br>") : "–"}</dd>
      </dl>
      <div class="links">${link(p.web, "Original im Ratsinformationssystem", "btn btn-primary")}
        ${link(p.main_file, "Dokument (PDF)", "btn btn-secondary")}</div>
      <h4>Prozesslinie</h4>
      <ol class="steps">${p.steps.map(stepHtml).join("")}</ol>
      ${legend()}${glossary(p)}
      <h4>Ortsbezug</h4><ul class="locs">${locs}</ul>
      ${(p.plans || []).length ? `<h4>Bebauungspläne</h4><ul class="locs plans">${p.plans.map((x) => `<li data-plan="${esc(x.nr)}"><strong>Bebauungsplan ${esc(x.nr)}</strong>
        ${x.area ? '<span class="plan-meta">– Geltungsbereich auf der Karte</span>' : " – nicht im Datensatz der rechtskräftigen Pläne (vermutlich noch im Verfahren); keine Fläche verfügbar"}
        <br><span class="meta">Fundstelle: „${esc(x.evidence)}“</span></li>`).join("")}</ul>` : ""}
      <p class="links">${link(reportLink(p), "Verortung falsch? Hinweis geben", "btn btn-secondary")}
        ${hasPaperFeed(p) ? `<a class="btn btn-soft" href="${BONN}feeds/vorlagen/${slug(p.reference)}.xml" type="application/atom+xml"><svg class="icon" aria-hidden="true"><use href="#i-rss"/></svg>Diesen Vorgang abonnieren</a>` : ""}</p>
      ${p.superordinated.length ? `<details class="acc"><summary>Bezieht sich auf (${p.superordinated.length})</summary><ul class="related">${rel(p.superordinated)}</ul></details>` : ""}
      <details class="acc"><summary>Quellen dieser Vorlage</summary><ul>
        <li>Quellobjekt: ${link(p.source_object, esc(p.source_object)) || esc(p.source_object)}</li>
        <li>Original: ${link(p.web, "Ratsinformationssystem") || "–"}</li>
        ${sources}</ul></details>
      ${LIMITS}`;
    $("#announce").textContent = `Vorgang ${p.reference} geöffnet: ${p.name}`;
    fillMitmachen();
    showPlans(p, !fromMap);
    if (MOBILE.matches || $("#panel-detail").hidden) setPanel("panel-detail", true);
    $("#detail").scrollTop = 0;
    const ms = markers.get(p.reference) || [];
    if (fromMap) {
      const b = document.querySelector(`.papers button[data-ref="${CSS.escape(p.reference)}"]`);
      if (b) b.scrollIntoView({ block: "nearest" });
    } else {
      // mit Bebauungsplan zoomt showPlans auf die Planfläche
      if (ms.length && !(p.plans || []).some((x) => x.area)) cluster.zoomToShowLayer(ms[0], () => { highlight(); map.panTo(ms[0].getLatLng(), { animate: !REDUCED }); });
      if (MOBILE.matches) $("#detail h3").focus();
    }
  }
  $("#detail").addEventListener("click", (e) => {
    const b = e.target.closest(".jump");
    if (b && tl) { if ($("#timeline-wrap").hidden) setPanel("timeline-wrap", true); tl.center(b.dataset.date); }
  });

  // --- Typische Wege (Aggregat) ------------------------------------------------------------------------
  async function showWege() {
    const box = $("#wege");
    if (box.dataset.loaded) return;
    let data;
    try {
      const r = await fetch(BONN + "prozesse.json");
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      data = await r.json();
    } catch (e) {
      box.innerHTML = `<p>${index ? "Die typischen Wege konnten nicht geladen werden." : "Für den Pilot nicht verfügbar."}</p>`;
      return;
    }
    box.dataset.loaded = "1";
    const types = data.types.filter((t) => t.count >= 20).length ? data.types.filter((t) => t.count >= 20) : data.types;
    box.innerHTML = `<label class="filters">Vorlagenart <select id="wege-type">${types.map((t) => `<option>${esc(t.paper_type)}</option>`).join("")}</select></label>
      <p class="hint">Weg = Folge der Beratungen (Gremium und Rolle) laut OParl-API. Am Ende steht das Ergebnis der entscheidenden Beratung, wörtlich aus der Quelle (in Anführungszeichen), oder ersatzweise der Stand des Verfahrens. Ganz Bonn.</p>
      <div id="wege-list"></div>${LIMITS}`;
    const draw = () => {
      const t = types.find((x) => x.paper_type === $("#wege-type").value);
      const total = t.paths.reduce((s, p) => s + p.count, 0);
      const final = (p) => (p.final_kind === "stand" ? `<span class="final final-stand">Stand: ${esc(p.final)}</span>` : `<span class="final">„${esc(p.final)}“</span>`);
      $("#wege-list").innerHTML = `<p class="count">${t.count} Vorlagen, ${t.distinct_paths} verschiedene Wege; gezeigt die ${t.paths.length} häufigsten (${Math.round(100 * total / t.count)} %).</p>` +
        t.paths.map((p) => `<div class="path"><div class="path-row">${p.stations.length ? p.stations.map((s) => `<span class="station">${esc(s)}</span>`).join('<span class="arrow" aria-hidden="true">→</span>') : '<span class="station">keine Beratung</span>'}
          <span class="arrow" aria-hidden="true">⇒</span>${final(p)}</div>
          <div class="meta">${p.count} Vorlagen · ${(100 * p.count / t.count).toFixed(1)} %</div>
          <div class="share-wrap" aria-hidden="true"><div class="share" style="width:${Math.max(2, 100 * p.count / t.paths[0].count)}%"></div></div></div>`).join("");
    };
    $("#wege-type").addEventListener("change", draw);
    draw();
  }

  // --- Abonnieren (Atom-Feeds) ------------------------------------------------------------------------
  // gleiche Regeln wie pipeline/export.slug und publish.has_paper_feed
  const slug = (s) => String(s).toLowerCase().replace(/[äöüß]/g, (c) => ({ ä: "ae", ö: "oe", ü: "ue", ß: "ss" }[c]))
    .replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
  const hasPaperFeed = (p) => Boolean(index && dataStand) &&
    ((p.date || "") >= `${Number(dataStand.slice(0, 4)) - 1}-01-01` || ["in Beratung", "offen"].includes(p.stand));
  function subscribeArea() {
    const box = $("#subscribe");
    document.querySelectorAll('link[rel="alternate"][type="application/atom+xml"]').forEach((l) => l.remove());
    if (!index) { box.hidden = true; return; }
    const href = `${BONN}feeds/${area.kind}-${area.key}.xml`;
    const where = area.kind === "ohne" ? `Vorlagen ohne Ortsbezug ${area.key}` : area.name;
    box.innerHTML = `<a class="btn btn-soft" href="${href}" type="application/atom+xml"><svg class="icon" aria-hidden="true"><use href="#i-rss"/></svg>Neues aus ${esc(where)} abonnieren</a>`;
    box.hidden = false;
    fillMitmachen();
    const l = document.createElement("link");
    Object.assign(l, { rel: "alternate", type: "application/atom+xml", href, title: `RIS-Karte Bonn – ${where}` });
    document.head.appendChild(l);
  }

  // --- Termine: kommende Sitzungen -------------------------------------------------------------------
  const isBV = (g) => /^Bezirksvertretung/.test(g || "");
  function areaBezirk() {
    if (!area || !index) return null;
    if (area.kind === "ortsteil") return (index.ortsteile.find((o) => o.slug === area.key) || {}).stadtbezirk;
    if (area.kind === "bezirk") return area.name;
    return null;
  }
  const fmtDay = (iso) => new Date(iso + "T12:00:00Z").toLocaleDateString("de-DE", { weekday: "short", day: "2-digit", month: "2-digit", year: "numeric", timeZone: "Europe/Berlin" });
  function showTermine() {
    if (!zeit) return;
    const box = $("#termine");
    const bezirk = areaBezirk();
    const scope = box.querySelector("#termine-scope") ? box.querySelector("#termine-scope").value : "gebiet";
    const today = new Date().toISOString().slice(0, 10);
    const relevant = (m) => scope === "alle" || !isBV(m.gremium) || !bezirk || m.gremium === `Bezirksvertretung ${bezirk}`;
    const list = zeit.meetings.filter((m) => m.date >= today && relevant(m));
    const where = area.kind === "ohne" ? "Vorlagen ohne Ortsbezug" : area.name;
    // Vorlagen des Gebiets, deren Beratung (über OParl-Lite verknüpft) auf dieser Sitzung liegt
    const onAgenda = (m) => papers.filter((p) => p.steps.some((s) => (s.typ === "beratung" || s.typ === "entscheidung") && s.date === m.date && s.label === m.gremium));
    let month = "";
    const items = list.map((m) => {
      const head = m.date.slice(0, 7) !== month ? `<h3 class="month">${new Date(m.date + "T12:00:00Z").toLocaleDateString("de-DE", { month: "long", year: "numeric" })}</h3>` : "";
      month = m.date.slice(0, 7);
      const docs = [link(m.web, "Tagesordnung"), link(m.invitation, "Einladung (PDF)")].filter(Boolean).join(" · ");
      const ps = onAgenda(m);
      return `${head}<div class="meeting${m.cancelled ? " cancelled" : ""}">
        <div class="meeting-head"><span class="meeting-date">${fmtDay(m.date)}${m.time ? `, ${esc(m.time)} Uhr` : ""}</span>
          <strong>${esc(m.gremium)}</strong>${m.cancelled ? ' <span class="badge">abgesagt</span>' : ""}</div>
        <div class="meta">${docs || "Tagesordnung noch nicht veröffentlicht"}</div>
        ${ps.length ? `<div class="agenda"><span>Aus ${esc(where)} auf der Tagesordnung:</span><ul>${ps.map((p) => `<li><button type="button" class="linkish" data-ref="${esc(p.reference)}">${esc(p.reference)} – ${esc(p.name)}</button></li>`).join("")}</ul></div>` : ""}
      </div>`;
    }).join("");
    box.innerHTML = `<p class="hint">Sitzungen von Rat, Ausschüssen, Beiräten und Bezirksvertretungen laut OParl-API der Stadt. Sie sind in der Regel öffentlich; Ort und Tagesordnung stehen in der Einladung, die etwa zwei Wochen vorher erscheint.</p>
      <div class="filters termine-filters"><label>Gremien
        <select id="termine-scope"><option value="gebiet"${scope === "gebiet" ? " selected" : ""}>${bezirk ? `Rat, Ausschüsse und Bezirksvertretung ${esc(bezirk)}` : "alle (kein Stadtbezirk gewählt)"}</option>
        <option value="alle"${scope === "alle" ? " selected" : ""}>alle Gremien</option></select></label>
        <a class="btn btn-cta" href="${BONN}termine.ics" download><svg class="icon" aria-hidden="true"><use href="#i-download"/></svg>Alle Termine in den Kalender (.ics)</a></div>
      <p class="count">${list.length} kommende Sitzungen</p>
      ${items || "<p>Keine kommenden Sitzungen im Datenbestand.</p>"}`;
    box.querySelector("#termine-scope").addEventListener("change", showTermine);
  }
  $("#termine").addEventListener("click", (e) => {
    const b = e.target.closest("button[data-ref]");
    if (b) { const p = papers.find((x) => x.reference === b.dataset.ref); if (p) { closePanel("panel-termine"); select(p); } }
  });

  // --- Menü „Mitmachen“: Abonnieren und Hinweise ----------------------------------------------------
  function fillMitmachen() {
    if (!area) return;
    const where = area.kind === "ohne" ? `Vorlagen ohne Ortsbezug ${area.key}` : area.name;
    const acts = [];
    if (index) acts.push(`<a class="btn btn-cta" href="${BONN}feeds/${area.kind}-${area.key}.xml" type="application/atom+xml"><svg class="icon" aria-hidden="true"><use href="#i-rss"/></svg>Neues aus ${esc(where)}</a>`);
    if (selected && hasPaperFeed(selected)) acts.push(`<a class="btn btn-soft" href="${BONN}feeds/vorlagen/${slug(selected.reference)}.xml" type="application/atom+xml"><svg class="icon" aria-hidden="true"><use href="#i-rss"/></svg>Vorgang ${esc(selected.reference)}</a>`);
    $("#cta-feed").innerHTML = acts.join("") || '<span class="hint">Feeds gibt es für die Gebiete in ganz Bonn.</span>';
    $("#cta-feed-text").textContent = `Neue Vorlagen und Beratungsergebnisse aus ${where} im Feed-Reader erhalten${selected ? ", oder nur den gewählten Vorgang" : ""}.`;
    const report = $("#cta-report");
    report.href = selected ? reportLink(selected) : `${REPO}/issues/new/choose`;
    report.lastChild.textContent = selected ? `Hinweis zu ${selected.reference}` : "Hinweis geben";
  }

  // --- Suche in der Leiste mit Schnellfiltern (Mega-Menü „Suche“) ----------------------------------
  function setScope(v) {
    const r = document.querySelector(`input[name="scope"][value="${v}"]`);
    if (r) r.checked = true;
    document.querySelectorAll(".scope-switch [data-scope]").forEach((b) => b.setAttribute("aria-checked", String(b.dataset.scope === v)));
  }
  function chip(label, pressed, data, n) {
    return `<button type="button" class="chip" aria-pressed="${pressed}" ${data}>${esc(label)}${n != null ? ` <span class="n">${n}</span>` : ""}</button>`;
  }
  function fillChips() {
    const theme = $("#f-theme").value, party = $("#f-party").value;
    const counts = {};
    for (const p of papers) for (const t of p.themes || []) counts[t.theme] = (counts[t.theme] || 0) + 1;
    const local = scope() === "gebiet";
    $("#chips-theme").innerHTML = Object.entries(THEMES).map(([k, v]) => chip(v, theme === k, `data-theme="${k}"`, local ? counts[k] || 0 : null)).join("");
    const parties = [...$("#f-party").options].map((o) => o.value).filter(Boolean);
    $("#chips-party").innerHTML = parties.map((v) => chip(v === "Koalition" ? "Koalition (gemeinsam)" : v, party === v, `data-party="${esc(v)}"`)).join("")
      || '<span class="hint">Im gewählten Gebiet gibt es keine zugeordneten Einreichenden.</span>';
    document.querySelectorAll(".scope-switch [data-scope]").forEach((b) => b.setAttribute("aria-checked", String(b.dataset.scope === scope())));
    $("#mega-count").textContent = $("#count").textContent;
  }
  function applyFromBar() {
    shown = LIST_STEP;
    fillParties();
    render();
    syncUrl();
    if (openMegaId === "mega-suche") fillChips();
  }
  function initSearchBar() {
    const q = $("#q");
    q.addEventListener("focus", () => openMega("mega-suche"));
    q.addEventListener("input", debounce(() => {
      $("#f-text").value = q.value;
      if (q.value && index && scope() !== "bonn") setScope("bonn");
      openMega("mega-suche");
      applyFromBar();
    }, 200));
    $("#nav-search").addEventListener("submit", (e) => {
      e.preventDefault();
      setPanel("panel-list", true);
      closeMega();
      $("#papers").focus();
    });
    $("#f-text").addEventListener("input", () => { q.value = $("#f-text").value; });
    $("#mega-suche").addEventListener("click", (e) => {
      const sc = e.target.closest("[data-scope]");
      if (sc) { setScope(sc.dataset.scope); return applyFromBar(); }
      const t = e.target.closest("[data-theme]");
      if (t) { $("#f-theme").value = $("#f-theme").value === t.dataset.theme ? "" : t.dataset.theme; return applyFromBar(); }
      const pa = e.target.closest("[data-party]");
      if (pa) { $("#f-party").value = $("#f-party").value === pa.dataset.party ? "" : pa.dataset.party; return applyFromBar(); }
    });
    $("#mega-show").addEventListener("click", () => { setPanel("panel-list", true); closeMega(); focusPanel("panel-list"); });
    $("#mega-reset").addEventListener("click", () => { q.value = ""; resetFilters(); fillChips(); });
    if (!index) document.querySelector(".scope-switch").hidden = true;
  }

  // --- Auswertung: Kennzahlen zum Gebiet und Verfahrenswege ------------------------------------------
  function openAuswertung(tab, focusTab) {
    closeMega();
    setPanel("panel-auswertung", true);
    const stats = tab === "stats";
    $("#tab-stats").setAttribute("aria-selected", String(stats)); $("#tab-stats").tabIndex = stats ? 0 : -1;
    $("#tab-wege").setAttribute("aria-selected", String(!stats)); $("#tab-wege").tabIndex = stats ? -1 : 0;
    $("#stats").hidden = !stats; $("#wege").hidden = stats;
    if (stats) showStats(); else showWege();
    (focusTab ? document.getElementById(stats ? "tab-stats" : "tab-wege") : $("#auswertung-heading")).focus();
  }
  function bars(title, rows, attr) {
    const max = Math.max(1, ...rows.map((r) => r.n));
    return `<section class="stat-block"><h3>${esc(title)}</h3><ul class="bars">${rows.map((r) => `<li><button type="button" class="bar" ${attr}="${esc(r.key)}" aria-label="${esc(r.label)}: ${r.n} Vorlagen – Liste danach filtern">
      <span>${esc(r.label)}</span><span class="bar-track" aria-hidden="true"><span class="bar-fill" style="width:${(100 * r.n / max).toFixed(1)}%"></span></span><span class="bar-n">${r.n}</span></button></li>`).join("")}</ul></section>`;
  }
  function showStats() {
    const list = papers, where = area.kind === "ohne" ? `Vorlagen ohne Ortsbezug ${area.key}` : area.name;
    const count = (f) => { const c = new Map(); for (const p of list) for (const k of f(p)) c.set(k, (c.get(k) || 0) + 1); return c; };
    const th = count((p) => (p.themes || []).map((t) => t.theme));
    const pa = count((p) => p.parties || []);
    const yr = count((p) => (p.date ? [p.date.slice(0, 4)] : []));
    const st = count((p) => [p.stand]);
    $("#stats").innerHTML = `<p class="hint">${list.length} Vorlagen in ${esc(where)}. Ein Klick auf einen Balken filtert die Liste. Themen und Parteien sind abgeleitet.</p>
      ${bars("Nach Thema", Object.keys(THEMES).filter((k) => th.get(k)).map((k) => ({ key: k, label: THEMES[k], n: th.get(k) })).sort((a, b) => b.n - a.n), "data-stat-theme")}
      ${pa.size ? bars("Nach Einreichenden (Partei, Fraktion, Verwaltung)", [...pa].map(([k, n]) => ({ key: k, label: k, n })).sort((a, b) => b.n - a.n), "data-stat-party") : ""}
      ${bars("Nach Jahr (Datum der Vorlage)", [...yr].map(([k, n]) => ({ key: k, label: k, n })).sort((a, b) => a.key.localeCompare(b.key)), "data-stat-year")}
      ${bars("Nach Stand des Verfahrens", [...st].map(([k, n]) => ({ key: k, label: k, n })).sort((a, b) => b.n - a.n), "data-stat-stand")}`;
  }
  $("#stats").addEventListener("click", (e) => {
    const b = e.target.closest(".bar");
    if (!b) return;
    // die Zahl am Balken gilt für das ganze Gebiet: übrige Filter und Zeitraum zurücksetzen
    $("#filters").reset();
    $("#q").value = "";
    range = null;
    if (tl) tl.reset();
    setScope("gebiet");
    if (b.dataset.statTheme) $("#f-theme").value = b.dataset.statTheme;
    if (b.dataset.statParty) { fillParties(); $("#f-party").value = b.dataset.statParty; }
    if (b.dataset.statStand) $("#f-stand").value = b.dataset.statStand;
    if (b.dataset.statYear && tl) { const y = b.dataset.statYear; tl.setRange(`${y}-01-01`, `${y}-12-31`); range = [`${y}-01-01`, `${y}-12-31`]; }
    shown = LIST_STEP;
    render();
    syncUrl();
    closePanel("panel-auswertung");
    setPanel("panel-list", true);
    focusPanel("panel-list");
  });

  // --- URL-Zustand -----------------------------------------------------------------------------------
  function syncUrl() {
    if (!area) return;
    const url = new URL(location.href);
    url.searchParams.set("gebiet", `${area.kind}:${area.key}`);
    if (tl && range) { const s = tl.getState(); for (const k of ["von", "bis", "zoom", "achse"]) url.searchParams.set(k, s[k]); }
    else for (const k of ["von", "bis", "zoom", "achse"]) url.searchParams.delete(k);
    const state = { thema: $("#f-theme").value, partei: $("#f-party").value, suche: scope() === "bonn" ? "bonn" : "" };
    for (const [k, v] of Object.entries(state)) (v ? url.searchParams.set(k, v) : url.searchParams.delete(k));
    url.hash = selected ? encodeURIComponent(selected.reference) : "";
    history.replaceState(null, "", url);
  }

  // --- Start -----------------------------------------------------------------------------------------
  async function start() {
    try {
      const g = await fetch(GLOSSAR_URL).then((r) => (r.ok ? r.json() : null));
      if (g) ({ ergebnisse: GLOSSAR, hinweise: NOTES, schritte: STEP_LABEL, evidenz: STATUS_TEXT } = g);
    } catch (e) { /* ohne Glossar: Schlüssel statt Erläuterungen */ }
    try { index = await fetch(BONN + "index.json").then((r) => (r.ok ? r.json() : null)); } catch (e) { index = null; }
    if (index) { try { zeit = await fetch(BONN + "zeit.json").then((r) => (r.ok ? r.json() : null)); } catch (e) { zeit = null; } }
    [geo.ortsteil, geo.bezirk] = await Promise.all([fetch(GEO.ortsteil).then((r) => r.json()), fetch(GEO.bezirk).then((r) => r.json())]);
    initMap();
    fillAreaSelect();
    if (zeit) {
      tl = Timeline.create($("#timeline-wrap"), {
        onRange(a, b) { range = [a, b]; shown = LIST_STEP; render(); syncUrl(); },
        onDate(d) { tl.center(d); },
      });
    } else {
      setPanel("timeline-wrap", false);
      toggleFor("timeline-wrap").hidden = true;
    }
    if (MOBILE.matches) { setPanel("panel-detail", false); setPanel("timeline-wrap", false); }
    else if (NARROW.matches) setPanel("panel-detail", false);
    applyLayout();
    MOBILE.addEventListener("change", applyLayout);
    NARROW.addEventListener("change", applyLayout);
    $("#filters").addEventListener("submit", (e) => e.preventDefault());
    $("#filters").addEventListener("input", (e) => {
      if (e.target.id === "f-text") return renderSoon();
      shown = LIST_STEP;
      if (e.target.name === "scope") { fillParties(); setScope(e.target.value); }
      render();
      syncUrl();
    });
    $("#f-area").addEventListener("change", (e) => { range = null; if (tl) tl.reset(); loadArea(e.target.value); });
    $("#papers").addEventListener("click", (e) => {
      if (e.target.closest("#more")) { shown += LIST_STEP; render(); return; }
      if (e.target.closest("#reset-filters")) { resetFilters(); return; }
      const g = e.target.closest("button[data-gref]");
      if (g) { openGlobal(g.dataset.gref, g.dataset.area); return; }
      const b = e.target.closest("button[data-ref]");
      if (b) select(papers.find((p) => p.reference === b.dataset.ref));
    });
    $("#papers").addEventListener("mouseover", (e) => {
      const b = e.target.closest("button[data-ref]");
      if (b && tl) tl.select(papers.find((p) => p.reference === b.dataset.ref), true);
    });
    $("#papers").addEventListener("mouseleave", () => tl && tl.select(selected));
    // Menü „Mitmachen“: Termine; Menü „Auswertung“: Reiter Kennzahlen und Verfahrenswege
    if (zeit) $("#cta-termine").addEventListener("click", () => { setPanel("panel-termine", true); showTermine(); focusPanel("panel-termine"); });
    else $("#cta-termine").hidden = true;
    document.querySelectorAll("[data-open-tab]").forEach((b) => b.addEventListener("click", () => openAuswertung(b.dataset.openTab)));
    $("#tab-stats").addEventListener("click", () => openAuswertung("stats"));
    $("#tab-wege").addEventListener("click", () => openAuswertung("wege"));
    $("#panel-auswertung .tabs").addEventListener("keydown", (e) => {
      if (e.key === "ArrowRight" || e.key === "ArrowLeft") { e.preventDefault(); openAuswertung($("#tab-stats").getAttribute("aria-selected") === "true" ? "wege" : "stats", true); }
    });
    initSearchBar();
    $("#f-theme").innerHTML = '<option value="">alle</option>' + Object.entries(THEMES).map(([k, v]) => `<option value="${k}">${esc(v)}</option>`).join("");
    if (index) $("#scope").hidden = false;
    const params = new URLSearchParams(location.search);
    const ref = decodeURIComponent(location.hash.slice(1));
    if (THEMES[params.get("thema")]) $("#f-theme").value = params.get("thema");
    if (index && params.get("suche") === "bonn") document.querySelector('input[name="scope"][value="bonn"]').checked = true;
    if (params.get("partei")) await loadSearch();
    await loadArea(params.get("gebiet") || DEFAULT_AREA, true);
    if (params.get("partei")) { fillParties(); $("#f-party").value = params.get("partei"); render(); }
    const von = params.get("von"), bis = params.get("bis");
    if (tl && ISO_DAY.test(von || "") && ISO_DAY.test(bis || "")) {
      tl.setState({ von, bis, zoom: params.get("zoom"), achse: params.get("achse") });
      range = [von, bis];
      render();
    }
    const initial = papers.find((p) => p.reference === ref);
    if (initial) select(initial);
    else $("#detail").innerHTML = INTRO;
    syncUrl();
  }
  start().catch((err) => { $("#detail").innerHTML = `<p>Die Daten konnten nicht geladen werden (${esc(err.message)}).</p>`; });
})();
