// Ratskarte Bonn – Karte vollflächig, darüber Liste, Zeitleiste, Detail (Prozesslinie mit Evidenzstatus)
// und typische Wege. Liest die Exporte der Pipeline; ohne Gesamtexport Rückfall auf den Pilot Endenich.
(function () {
  "use strict";
  const BONN = "data/export/bonn/";
  const PILOT = "data/export/endenich/vorlagen.json";
  const GEO = { ortsteil: "data/geo/ortsteile_bonn.geojson", bezirk: "data/geo/stadtbezirke_bonn.geojson" };
  const DEFAULT_AREA = "ortsteil:endenich";
  const REPO = "https://github.com/daimpad/allris-test";
  const RANK = { hoch: 3, mittel: 2, niedrig: 1 };
  const MOBILE = matchMedia("(max-width: 900px)");
  const METHOD = {
    oparl_location: "Koordinate der Stadt (OParl)", strasse: "Straßenname im Titel",
    "strasse+ortsteil": "Straßen- und Ortsteilname im Titel", "strasse+bezirk": "Straßenname im Titel, Bezirk eingegrenzt",
    strasse_mehrdeutig: "Straßenname im Titel, mehrere Lagen", ortsteil_name: "Ortsteilname im Titel",
    ortsteil_adjektiv: "Ortsteil im Titel (z. B. „Endenicher …“)", stadtbezirk_name: "Stadtbezirk im Titel",
    stadtbezirk_adjektiv: "Stadtbezirk im Titel (Adjektiv)", vererbt: "von der übergeordneten Vorlage übernommen",
  };
  const STATUS = {
    belegt: "belegt", abgeleitet: "abgeleitet", soll: "soll", "nicht_öffentlich": "nicht öffentlich", unklar: "unklar",
  };
  const STATUS_TEXT = {
    belegt: "Als Datenobjekt in der Quelle vorhanden.",
    abgeleitet: "Aus Quelldaten erschlossen (z. B. Verknüpfung mit OParl-Lite, Titelmuster).",
    "nicht_öffentlich": "Findet regelmäßig statt, ist von außen aber nicht einsehbar.",
    unklar: "Ob und wann der Schritt stattfindet, lässt sich aus öffentlichen Quellen nicht bestimmen.",
    soll: "Nach Regelwerk zu erwarten, aber nicht dokumentiert (noch nicht modelliert).",
  };
  const NOTES = {
    sonderweg: "Sonderweg: Entscheidung vor der Beratung, nachträgliche Genehmigung durch das Gremium.",
    vorbereitung: "Erarbeitung, Mitzeichnung und Freigabe der Vorlage in der Verwaltung sind von außen nicht einsehbar.",
    datum: "Datum der Vorlage laut Ratsinformationssystem; ob es Erstellung, Freigabe oder Veröffentlichung bezeichnet, ist nicht dokumentiert.",
    ohne_sitzung: "Beratung ist vorgesehen; Sitzung und Ergebnis sind (noch) nicht verknüpft.",
    vollzug: "Ob und wann der Beschluss umgesetzt ist, steht in der Beschlusskontrolle; dafür gibt es keine öffentliche Schnittstelle.",
    nichtoeffentlich: "Der Tagesordnungspunkt wurde nichtöffentlich beraten; Inhalte sind nicht einsehbar.",
  };
  const STEP_LABEL = {
    initiierung: "Initiierung", vorbereitung: "Vorbereitung", veroeffentlichung: "Datum der Vorlage", beratung: "Beratung",
    entscheidung: "Entscheidung", folgevorlage: "Folgevorlage", vollzug: "Vollzug",
  };
  const GLOSSAR = {
    "ungeändert beschlossen": "Das Gremium hat dem Vorschlag in der vorgelegten Fassung zugestimmt.",
    "geändert beschlossen": "Das Gremium hat zugestimmt, aber mit Änderungen, etwa aus Änderungsanträgen.",
    "zur Kenntnis genommen": "Das Gremium wurde informiert; über einen Beschluss wurde nicht abgestimmt.",
    "abgelehnt": "Die Mehrheit des Gremiums hat dagegen gestimmt.",
    "vertagt": "Die Beratung wurde auf eine spätere Sitzung verschoben.",
    "zurückgezogen": "Die Einreichenden haben die Vorlage zurückgenommen.",
    "verwiesen": "Die Vorlage wurde zur Beratung an ein anderes Gremium weitergegeben.",
    "nicht abgestimmt": "In dieser Sitzung fand keine Abstimmung statt.",
    "ohne Votum": "Das Gremium hat keine Empfehlung abgegeben.",
    "erledigt durch Stellungnahme der Verwaltung": "Der Antrag gilt als erledigt, weil die Verwaltung schriftlich Stellung genommen hat.",
    "bei Anerkennung der Tagesordnung nicht aufgenommen oder vertagt": "Der Punkt wurde zu Beginn der Sitzung von der Tagesordnung genommen oder verschoben.",
    "mit Protokollnotiz": "Zusätzlich wurde eine Anmerkung ins Protokoll aufgenommen.",
    "mit Maßgabe": "Der Beschluss gilt mit einer zusätzlichen Bedingung oder Vorgabe.",
    Entscheidung: "Dieses Gremium entscheidet abschließend.",
    Empfehlung: "Das Gremium berät vor und gibt eine Empfehlung an das entscheidende Gremium.",
    Anhörung: "Das Gremium wird angehört; seine Stellungnahme ist nicht bindend.",
    Kenntnisnahme: "Das Gremium wird informiert.",
  };
  const LIMITS = `<details class="acc"><summary>Was diese Darstellung nicht zeigen kann</summary><ul>
    <li>Verwaltungsinterne Abläufe vor dem Datum der Vorlage (Erarbeitung, Mitzeichnung, Freigaben).</li>
    <li>Den Vollzug von Beschlüssen: Die Beschlusskontrolle hat keine öffentliche Schnittstelle.</li>
    <li>Was das Regelwerk vorsieht (Soll): Zuständigkeitsordnung und Bezirkssatzung sind noch nicht formalisiert.</li>
    <li>Inhalte nichtöffentlicher Beratungen und Vorlagen vor Oktober 2019.</li>
    <li>Sitzungen und Ergebnisse, die OParl-Lite (noch) nicht verknüpft.</li></ul>
    <p class="hint">Abweichungen zwischen Regel und Ablauf sind Befunde, keine Bewertung.</p></details>`;

  const $ = (s) => document.querySelector(s);
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const fmtDate = (iso) => iso ? new Date(iso.length === 10 ? iso + "T12:00:00Z" : iso)
    .toLocaleDateString("de-DE", { timeZone: "Europe/Berlin", day: "2-digit", month: "2-digit", year: "numeric" }) : "";

  let index = null, zeit = null, geo = {}, meta = null, papers = [], area = null, selected = null;
  let map, cluster, outline, markers = new Map(), tl = null, range = null;

  // --- Flächen ein- und ausklappen ---------------------------------------------------------------
  function setPanel(id, open) {
    const el = document.getElementById(id);
    el.hidden = !open;
    document.querySelectorAll(`.toggle[data-panel="${id}"]`).forEach((b) => b.setAttribute("aria-pressed", String(open)));
    if (id === "panel-list") { document.body.classList.toggle("list-open", open); document.body.classList.toggle("list-closed", !open); }
    if (id === "panel-detail") { document.body.classList.toggle("detail-open", open); document.body.classList.toggle("detail-closed", !open); }
    if (open && MOBILE.matches) {
      for (const other of ["panel-list", "panel-detail", "panel-wege", "timeline-wrap"]) if (other !== id && !document.getElementById(other).hidden) setPanel(other, false);
    }
  }
  document.addEventListener("click", (e) => {
    const t = e.target.closest("[data-panel]");
    if (t) setPanel(t.dataset.panel, document.getElementById(t.dataset.panel).hidden);
    const c = e.target.closest("[data-close]");
    if (c) setPanel(c.dataset.close, false);
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
    return parseArea(DEFAULT_AREA);
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

  async function loadArea(value, keepState) {
    area = parseArea(value);
    $("#f-area").value = `${area.kind}:${area.key}`;
    $("#count").textContent = "Lade Vorlagen …";
    const data = await fetch(area.file).then((r) => r.json());
    meta = data.meta;
    papers = data.papers;
    document.title = `Ratskarte Bonn – ${area.kind === "ohne" ? "Vorlagen ohne Ortsbezug " + area.key : area.name}`;
    $("#f-conf").hidden = area.kind === "ohne";
    fillFilters();
    drawOutline();
    selected = null;
    if (!keepState) $("#detail").innerHTML = `<p class="empty">Eine Vorlage in der Liste oder auf der Karte auswählen.</p>${LIMITS}`;
    if (tl && zeit) {
      const key = `${area.kind}:${area.key}`;
      const series = zeit.areas[key] || zeit.areas.gesamt;
      tl.setData({ months: zeit.months, categories: zeit.categories, density: series, meetings: zeit.meetings,
        terms: zeit.terms, dataStart: zeit.data_start, dataStand: (meta.sources.find((s) => s.name === "oparl-bonn") || {}).retrieved_at?.slice(0, 10) || meta.generated_at.slice(0, 10) });
      tl.setPapers(papers);
      tl.select(null);
    }
    render();
    syncUrl();
    const stand = meta.sources.map((s) => `${s.name}: ${String(s.retrieved_at || "–").slice(0, 10)}`).join(" · ");
    $("#stand").textContent = `Datenstand: ${stand} · erzeugt ${meta.generated_at.slice(0, 10)}`;
  }

  // --- Karte -----------------------------------------------------------------------------------------
  function initMap() {
    map = L.map("map", { zoomControl: false, scrollWheelZoom: true });
    L.control.zoom({ position: "bottomright" }).addTo(map);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 19, attribution: "© OpenStreetMap-Mitwirkende" }).addTo(map);
    cluster = L.markerClusterGroup({ showCoverageOnHover: false, maxClusterRadius: 40 }).addTo(map);
  }
  function mapPadding() {
    const desktop = !MOBILE.matches;
    const left = desktop && !$("#panel-list").hidden ? 392 : 16;
    const right = desktop && !$("#panel-detail").hidden ? 452 : 16;
    const top = desktop && !$("#timeline-wrap").hidden ? 76 + $("#timeline-wrap").offsetHeight + 12 : 80;
    return { paddingTopLeft: [left, top], paddingBottomRight: [right, desktop ? 70 : 150] };
  }
  function drawOutline() {
    if (outline) outline.remove();
    let feature = null;
    if (area.kind === "ortsteil") feature = geo.ortsteil.features.find((f) => f.properties.ortsteil_bez === area.name);
    if (area.kind === "bezirk") feature = geo.bezirk.features.find((f) => f.properties.bezirk_bez === area.name);
    outline = L.geoJSON(feature || geo.bezirk, { style: { color: "#7c3aed", weight: 2, fillColor: "#c4b5fd", fillOpacity: 0.12 } }).addTo(map);
    map.fitBounds(outline.getBounds(), mapPadding());
  }
  const color = (c) => getComputedStyle(document.documentElement).getPropertyValue("--" + c).trim();
  function drawMarkers(list) {
    cluster.clearLayers();
    markers.clear();
    for (const p of list) {
      const ms = areaLocs(p).filter((l) => l.level === "strasse" && l.lon != null).map((l) =>
        L.circleMarker([l.lat, l.lon], { radius: 7, weight: 2, color: "#fff", fillColor: color(l.confidence), fillOpacity: 0.95 })
          .bindTooltip(`${esc(p.reference)} · ${esc(l.name)}`).on("click", () => select(p, true)));
      ms.forEach((m) => cluster.addLayer(m));
      markers.set(p.reference, ms);
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
  }
  function inRange(p) {
    if (!range) return true;
    const [a, b] = range, dim = tl ? tl.dimension() : "vorlage";
    if (dim === "vorlage") return p.date >= a && p.date <= b;
    return p.steps.some((s) => (s.typ === "beratung" || s.typ === "entscheidung") && s.date && s.date >= a && s.date <= b);
  }
  function filtered() {
    const text = $("#f-text").value.trim().toLowerCase(), type = $("#f-type").value, amt = $("#f-amt").value;
    const gremium = $("#f-gremium").value, standF = $("#f-stand").value;
    const confs = new Set([...document.querySelectorAll("#f-conf input:checked")].map((i) => i.value));
    return papers.filter((p) => (!type || p.paper_type === type) && (!amt || p.amt === amt) &&
      (!gremium || p.process.some((s) => s.gremium === gremium)) && (!standF || p.stand === standF) &&
      (area.kind === "ohne" || confs.has(bestConfidence(p))) && inRange(p) &&
      (!text || (p.name + " " + p.reference).toLowerCase().includes(text)));
  }
  function render() {
    const list = filtered();
    const where = area.kind === "ohne" ? `ohne Ortsbezug, ${area.key}` : area.name;
    const span = range ? ` · ${fmtDate(range[0])}–${fmtDate(range[1])}` : "";
    $("#count").textContent = `${list.length} von ${papers.length} Vorlagen · ${where}${span}`;
    $("#papers").innerHTML = list.map((p) => {
      const conf = area.kind === "ohne" ? "" : `<span class="conf conf-${bestConfidence(p)}">Verortung ${bestConfidence(p)}</span>`;
      return `<li><button type="button" data-ref="${esc(p.reference)}" aria-current="${selected === p}">
        <span class="title">${esc(p.name)}</span>
        <span class="meta"><span>${esc(p.reference)}</span><span>${fmtDate(p.date)}</span><span>${esc(p.paper_type)}</span>
        <span>${esc(p.stand)}</span>${conf}</span></button></li>`;
    }).join("");
    drawMarkers(list);
  }

  // --- Detail: Prozesslinie mit Evidenzstatus -------------------------------------------------------
  const glossKeys = (t) => (t ? t.split(" - ").map((x) => x.trim()).filter((x) => GLOSSAR[x]) : []);
  function stepHtml(s) {
    const status = s.status;
    const mark = { belegt: "", abgeleitet: "", "nicht_öffentlich": "", unklar: "?", soll: "" }[status];
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
    return `<li class="step${cls}" data-status="${esc(status)}">
      <span class="mark mark-${esc(status)}" aria-hidden="true">${mark}</span>
      <div class="step-head">${esc(STEP_LABEL[s.typ] || s.typ)}${s.label && s.label !== STEP_LABEL[s.typ] ? ": " + esc(s.label) : ""}<span class="step-status">${esc(STATUS[status])}</span></div>
      <div class="step-body">${body.join("<br>")}${box}</div></li>`;
  }
  function legend() {
    return `<details class="acc"><summary>Legende Evidenzstatus</summary><div class="legend">${["belegt", "abgeleitet", "nicht_öffentlich", "unklar"]
      .map((s) => `<span><span class="mark mark-${s}" aria-hidden="true">${s === "unklar" ? "?" : ""}</span><strong>${STATUS[s]}</strong> – ${STATUS_TEXT[s]}</span>`).join("")}
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
  function select(p, fromMap) {
    selected = p;
    document.querySelectorAll(".papers button").forEach((b) => b.setAttribute("aria-current", String(b.dataset.ref === p.reference)));
    syncUrl();
    if (tl) tl.select(p);
    const resp = p.responsibility.map((r) => `${esc(r.label)}${r.derived ? ` <span class="derived">abgeleitet, über ${esc(r.evidence)}</span>` : ""}`).join("<br>");
    const locs = p.locations.length ? p.locations.map((l) => `<li><strong>${esc(l.name || l.ortsteil || l.stadtbezirk)}</strong>
      ${l.ortsteil && l.level === "strasse" ? `(${esc(l.ortsteil)})` : ""} – Stufe ${esc(l.stage)}, <span class="conf conf-${esc(l.confidence)}">${esc(l.confidence)}</span><br>
      <span class="meta">${esc(METHOD[l.method] || l.method)}${l.evidence ? ` · Fundstelle: „${esc(l.evidence)}“` : ""}</span></li>`).join("")
      : "<li>stadtweit / ohne Ortsbezug</li>";
    const rel = (arr) => arr.map((r) => `<li>${esc(r.reference)} · ${esc(r.paper_type)} – ${esc(r.name)}</li>`).join("");
    const sources = meta.sources.map((s) => `<li>${esc(s.name)}: ${esc(s.license)} · Abruf ${esc(String(s.retrieved_at || "–").slice(0, 10))}</li>`).join("");
    $("#detail").innerHTML = `
      <h3>${esc(p.name)}</h3>
      <dl class="facts">
        <dt>Drucksache</dt><dd>${esc(p.reference)}</dd>
        <dt>Art</dt><dd>${esc(p.paper_type)}</dd>
        <dt>Datum</dt><dd>${fmtDate(p.date)}</dd>
        <dt>Amt</dt><dd>${resp || esc(p.amt)}</dd>
        <dt>Stand</dt><dd>${esc(p.stand)}</dd>
      </dl>
      <div class="links"><a class="btn btn-primary" href="${esc(p.web)}" target="_blank" rel="noopener">Original im Ratsinformationssystem</a>
        ${p.main_file ? `<a class="btn btn-secondary" href="${esc(p.main_file)}" target="_blank" rel="noopener">Dokument (PDF)</a>` : ""}</div>
      <h4>Prozesslinie</h4>
      <ol class="steps">${p.steps.map(stepHtml).join("")}</ol>
      ${legend()}${glossary(p)}
      <h4>Ortsbezug</h4><ul class="locs">${locs}</ul>
      <p><a class="btn btn-secondary" href="${reportLink(p)}" target="_blank" rel="noopener">Verortung falsch? Hinweis geben</a></p>
      ${p.superordinated.length ? `<details class="acc"><summary>Bezieht sich auf (${p.superordinated.length})</summary><ul class="related">${rel(p.superordinated)}</ul></details>` : ""}
      <details class="acc"><summary>Quellen dieser Vorlage</summary><ul>
        <li>Quellobjekt: <a href="${esc(p.source_object)}" target="_blank" rel="noopener">${esc(p.source_object)}</a></li>
        <li>Original: <a href="${esc(p.web)}" target="_blank" rel="noopener">Ratsinformationssystem</a></li>
        ${sources}</ul></details>
      ${LIMITS}`;
    if (MOBILE.matches || $("#panel-detail").hidden) setPanel("panel-detail", true);
    const ms = markers.get(p.reference) || [];
    if (!fromMap) {
      if (ms.length) map.setView(ms[0].getLatLng(), Math.max(map.getZoom(), 16));
      if (MOBILE.matches) $("#detail").focus();
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
    try { data = await fetch(BONN + "prozesse.json").then((r) => r.json()); } catch (e) { box.innerHTML = "<p>Für den Pilot nicht verfügbar.</p>"; return; }
    box.dataset.loaded = "1";
    const types = data.types.filter((t) => t.count >= 20);
    box.innerHTML = `<label class="filters">Vorlagenart <select id="wege-type">${types.map((t) => `<option>${esc(t.paper_type)}</option>`).join("")}</select></label>
      <p class="hint">Weg = Folge der Beratungen (Gremium und Rolle) laut OParl-API; Ende = Ergebnis der entscheidenden Beratung (OParl-Lite) oder Stand. Ganz Bonn.</p>
      <div id="wege-list"></div>${LIMITS}`;
    const draw = () => {
      const t = types.find((x) => x.paper_type === $("#wege-type").value);
      const shown = t.paths.reduce((s, p) => s + p.count, 0);
      $("#wege-list").innerHTML = `<p class="count">${t.count} Vorlagen, ${t.distinct_paths} verschiedene Wege; gezeigt die ${t.paths.length} häufigsten (${Math.round(100 * shown / t.count)} %).</p>` +
        t.paths.map((p) => `<div class="path"><div class="path-row">${p.stations.length ? p.stations.map((s) => `<span class="station">${esc(s)}</span>`).join('<span class="arrow" aria-hidden="true">→</span>') : '<span class="station">keine Beratung</span>'}
          <span class="arrow" aria-hidden="true">⇒</span><span class="final">„${esc(p.final)}“</span></div>
          <div class="meta">${p.count} Vorlagen · ${(100 * p.count / t.count).toFixed(1)} %</div>
          <div class="share-wrap" aria-hidden="true"><div class="share" style="width:${Math.max(2, 100 * p.count / t.paths[0].count)}%"></div></div></div>`).join("");
    };
    $("#wege-type").addEventListener("change", draw);
    draw();
  }

  // --- URL-Zustand -----------------------------------------------------------------------------------
  function syncUrl() {
    const url = new URL(location.href);
    url.searchParams.set("gebiet", `${area.kind}:${area.key}`);
    if (tl && range) { const s = tl.getState(); for (const k of ["von", "bis", "zoom", "achse"]) url.searchParams.set(k, s[k]); }
    else for (const k of ["von", "bis", "zoom", "achse"]) url.searchParams.delete(k);
    url.hash = selected ? encodeURIComponent(selected.reference) : "";
    history.replaceState(null, "", url);
  }

  // --- Start -----------------------------------------------------------------------------------------
  async function start() {
    try { index = await fetch(BONN + "index.json").then((r) => (r.ok ? r.json() : null)); } catch (e) { index = null; }
    if (index) { try { zeit = await fetch(BONN + "zeit.json").then((r) => (r.ok ? r.json() : null)); } catch (e) { zeit = null; } }
    [geo.ortsteil, geo.bezirk] = await Promise.all([fetch(GEO.ortsteil).then((r) => r.json()), fetch(GEO.bezirk).then((r) => r.json())]);
    initMap();
    fillAreaSelect();
    if (zeit) {
      tl = Timeline.create($("#timeline-wrap"), {
        onRange(a, b) { range = [a, b]; render(); syncUrl(); },
        onDate(d) { tl.center(d); },
      });
      if (MOBILE.matches) $("#timeline-wrap").classList.add("tl-compact");
    } else {
      setPanel("timeline-wrap", false);
      document.querySelector('.toggle[data-panel="timeline-wrap"]').hidden = true;
    }
    if (MOBILE.matches) { setPanel("panel-detail", false); setPanel("timeline-wrap", false); }
    $("#filters").addEventListener("submit", (e) => e.preventDefault());
    $("#filters").addEventListener("input", render);
    $("#f-area").addEventListener("change", (e) => { range = null; loadArea(e.target.value); });
    $("#papers").addEventListener("click", (e) => {
      const b = e.target.closest("button[data-ref]");
      if (b) select(papers.find((p) => p.reference === b.dataset.ref));
    });
    $("#papers").addEventListener("mouseover", (e) => {
      const b = e.target.closest("button[data-ref]");
      if (b && tl) tl.select(papers.find((p) => p.reference === b.dataset.ref));
    });
    $("#papers").addEventListener("mouseleave", () => tl && tl.select(selected));
    document.querySelector('.toggle[data-panel="panel-wege"]').addEventListener("click", showWege);
    const params = new URLSearchParams(location.search);
    const ref = decodeURIComponent(location.hash.slice(1));
    await loadArea(params.get("gebiet") || DEFAULT_AREA, true);
    if (tl && params.get("von") && params.get("bis")) {
      tl.setState({ von: params.get("von"), bis: params.get("bis"), zoom: params.get("zoom"), achse: params.get("achse") });
      range = [params.get("von"), params.get("bis")];
      render();
    }
    const initial = papers.find((p) => p.reference === ref);
    if (initial) select(initial);
    else $("#detail").innerHTML = `<p class="empty">Eine Vorlage in der Liste oder auf der Karte auswählen.</p>${LIMITS}`;
  }
  start().catch((err) => { $("#detail").innerHTML = `<p>Die Daten konnten nicht geladen werden (${esc(err.message)}).</p>`; });
})();
