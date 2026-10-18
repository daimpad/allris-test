// RIS-Karte Bonn – Karte vollflächig, darüber Liste, Zeitleiste, Detail (Prozesslinie mit Evidenzstatus)
// und typische Wege. Liest die Exporte der Pipeline; ohne Gesamtexport Rückfall auf den Pilot Endenich.
(function () {
  "use strict";
  const BONN = "data/export/bonn/";
  const PILOT = "data/export/endenich/vorlagen.json";
  const GEO = { ortsteil: "data/geo/ortsteile_bonn.geojson", bezirk: "data/geo/stadtbezirke_bonn.geojson" };
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
    datum_vor_vorlage: "Dieser Schritt liegt vor dem angegebenen Datum der Vorlage; die Quelle erklärt die Abweichung nicht.",
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

  let index = null, zeit = null, geo = {}, meta = null, papers = [], area = null, selected = null;
  let map, cluster, outline, markers = new Map(), tl = null, range = null, loadSeq = 0, shown = LIST_STEP, lastList = [];

  // --- Flächen ein- und ausklappen ---------------------------------------------------------------
  const SHEETS = ["panel-list", "panel-detail", "panel-wege", "timeline-wrap", "sources"];
  const toggleFor = (id) => document.querySelector(`.toggle[data-panel="${id}"]`);
  function setPanel(id, open) {
    const el = document.getElementById(id);
    el.hidden = !open;
    document.querySelectorAll(`.toggle[data-panel="${id}"]`).forEach((b) => b.setAttribute("aria-pressed", String(open)));
    if (id === "panel-list") { document.body.classList.toggle("list-open", open); document.body.classList.toggle("list-closed", !open); }
    if (id === "panel-detail") { document.body.classList.toggle("detail-open", open); document.body.classList.toggle("detail-closed", !open); }
    if (!open) return;
    // schmale Bildschirme: nur eine Fläche; mittlere Breiten: Liste oder Detail, damit die Zeitleiste Platz hat
    const others = MOBILE.matches ? SHEETS : NARROW.matches && (id === "panel-list" || id === "panel-detail")
      ? ["panel-list", "panel-detail"] : [];
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
      if (open && t.dataset.panel === "sources") $("#sources details").open = true;
    }
    const c = e.target.closest("[data-close]");
    if (c) closePanel(c.dataset.close);
  });
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape" || $("#about").open) return;
    if (!$("#panel-wege").hidden) return closePanel("panel-wege");
    const inside = SHEETS.find((id) => document.getElementById(id).contains(document.activeElement));
    if (inside && (MOBILE.matches || inside !== "sources")) closePanel(inside);
  });
  function applyLayout() {
    if (MOBILE.matches) {
      setPanel("sources", false);
      const open = SHEETS.filter((id) => !document.getElementById(id).hidden);
      open.slice(1).forEach((id) => setPanel(id, false));
    } else {
      $("#sources").hidden = false;
      if (NARROW.matches && !$("#panel-list").hidden && !$("#panel-detail").hidden) setPanel("panel-detail", false);
    }
    $("#timeline-wrap").classList.toggle("tl-compact", MOBILE.matches);
    if (tl) tl.select(selected);
  }

  // --- Über ----------------------------------------------------------------------------------------
  $("#about-open").addEventListener("click", () => $("#about").showModal());
  $("#about-close").addEventListener("click", () => $("#about").close());
  $("#about").addEventListener("click", (e) => { if (e.target === e.currentTarget) e.currentTarget.close(); });

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
      const oparl = meta.sources.find((s) => s.name === "oparl-bonn") || {};
      tl.setData({ months: zeit.months, categories: zeit.categories, density: series, meetings: zeit.meetings,
        terms: zeit.terms, dataStart: zeit.data_start,
        dataStand: (oparl.retrieved_at || meta.generated_at || new Date().toISOString()).slice(0, 10) });
      tl.select(null);
    }
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
    cluster = L.markerClusterGroup({ showCoverageOnHover: false, maxClusterRadius: 40, animate: !REDUCED }).addTo(map);
  }
  function mapPadding() {
    const desktop = !MOBILE.matches;
    const left = desktop && !$("#panel-list").hidden ? 392 : 16;
    const right = desktop && !$("#panel-detail").hidden ? 452 : 16;
    const top = desktop && !$("#timeline-wrap").hidden ? 76 + $("#timeline-wrap").offsetHeight + 12 : 80;
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
      const ms = areaLocs(p).filter((l) => l.level === "strasse" && l.lon != null).map((l) => {
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
  }
  function inRange(p) {
    if (!range) return true;
    const [a, b] = range, dim = tl ? tl.dimension() : "vorlage";
    if (dim === "vorlage") return p.date >= a && p.date <= b;
    return p.steps.some((s) => (s.typ === "beratung" || s.typ === "entscheidung") && s.date && s.date >= a && s.date <= b);
  }
  function filtered(withRange = true) {
    const text = $("#f-text").value.trim().toLowerCase(), type = $("#f-type").value, amt = $("#f-amt").value;
    const gremium = $("#f-gremium").value, standF = $("#f-stand").value;
    const confs = new Set([...document.querySelectorAll("#f-conf input:checked")].map((i) => i.value));
    return papers.filter((p) => (!type || p.paper_type === type) && (!amt || p.amt === amt) &&
      (!gremium || p.process.some((s) => s.gremium === gremium)) && (!standF || p.stand === standF) &&
      (area.kind === "ohne" || confs.has(bestConfidence(p))) && (!withRange || inRange(p)) &&
      (!text || (p.name + " " + p.reference).toLowerCase().includes(text)));
  }
  function resetFilters() {
    $("#filters").reset();
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
      <span>${esc(p.stand)}</span>${conf}</span></button></li>`;
  }
  function render() {
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
  const link = (url, text, cls) => { const u = safeUrl(url); return u ? `<a ${cls ? `class="${cls}" ` : ""}href="${u}" target="_blank" rel="noopener">${text}</a>` : ""; };
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
      </dl>
      <div class="links">${link(p.web, "Original im Ratsinformationssystem", "btn btn-primary")}
        ${link(p.main_file, "Dokument (PDF)", "btn btn-secondary")}</div>
      <h4>Prozesslinie</h4>
      <ol class="steps">${p.steps.map(stepHtml).join("")}</ol>
      ${legend()}${glossary(p)}
      <h4>Ortsbezug</h4><ul class="locs">${locs}</ul>
      <p>${link(reportLink(p), "Verortung falsch? Hinweis geben", "btn btn-secondary")}</p>
      ${p.superordinated.length ? `<details class="acc"><summary>Bezieht sich auf (${p.superordinated.length})</summary><ul class="related">${rel(p.superordinated)}</ul></details>` : ""}
      <details class="acc"><summary>Quellen dieser Vorlage</summary><ul>
        <li>Quellobjekt: ${link(p.source_object, esc(p.source_object)) || esc(p.source_object)}</li>
        <li>Original: ${link(p.web, "Ratsinformationssystem") || "–"}</li>
        ${sources}</ul></details>
      ${LIMITS}`;
    $("#announce").textContent = `Vorgang ${p.reference} geöffnet: ${p.name}`;
    if (MOBILE.matches || $("#panel-detail").hidden) setPanel("panel-detail", true);
    $("#detail").scrollTop = 0;
    const ms = markers.get(p.reference) || [];
    if (fromMap) {
      const b = document.querySelector(`.papers button[data-ref="${CSS.escape(p.reference)}"]`);
      if (b) b.scrollIntoView({ block: "nearest" });
    } else {
      if (ms.length) cluster.zoomToShowLayer(ms[0], () => { highlight(); map.panTo(ms[0].getLatLng(), { animate: !REDUCED }); });
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

  // --- URL-Zustand -----------------------------------------------------------------------------------
  function syncUrl() {
    if (!area) return;
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
    $("#filters").addEventListener("input", (e) => (e.target.id === "f-text" ? renderSoon() : (shown = LIST_STEP, render())));
    $("#f-area").addEventListener("change", (e) => { range = null; if (tl) tl.reset(); loadArea(e.target.value); });
    $("#papers").addEventListener("click", (e) => {
      if (e.target.closest("#more")) { shown += LIST_STEP; render(); return; }
      if (e.target.closest("#reset-filters")) { resetFilters(); return; }
      const b = e.target.closest("button[data-ref]");
      if (b) select(papers.find((p) => p.reference === b.dataset.ref));
    });
    $("#papers").addEventListener("mouseover", (e) => {
      const b = e.target.closest("button[data-ref]");
      if (b && tl) tl.select(papers.find((p) => p.reference === b.dataset.ref), true);
    });
    $("#papers").addEventListener("mouseleave", () => tl && tl.select(selected));
    toggleFor("panel-wege").addEventListener("click", showWege);
    const params = new URLSearchParams(location.search);
    const ref = decodeURIComponent(location.hash.slice(1));
    await loadArea(params.get("gebiet") || DEFAULT_AREA, true);
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
