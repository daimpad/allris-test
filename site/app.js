// Ratskarte Bonn – liest die Exporte der Pipeline und zeigt Liste, Karte und Detail je Gebiet.
// Gebiete: Ortsteil, Stadtbezirk (nur Bezüge auf Bezirksebene) oder „ohne Ortsbezug“ je Jahr.
// Ohne den Gesamtexport (data/export/bonn) fällt die Seite auf den Pilot-Export Endenich zurück.
(function () {
  "use strict";
  const BONN = "data/export/bonn/";
  const PILOT = "data/export/endenich/vorlagen.json";
  const GEO = { ortsteil: "data/geo/ortsteile_bonn.geojson", bezirk: "data/geo/stadtbezirke_bonn.geojson" };
  const DEFAULT_AREA = "ortsteil:endenich";
  const REPO = "https://github.com/daimpad/allris-test";
  const RANK = { hoch: 3, mittel: 2, niedrig: 1 };
  const METHOD = {
    oparl_location: "Koordinate der Stadt (OParl)",
    strasse: "Straßenname im Titel",
    "strasse+ortsteil": "Straßen- und Ortsteilname im Titel",
    "strasse+bezirk": "Straßenname im Titel, Bezirk eingegrenzt",
    strasse_mehrdeutig: "Straßenname im Titel, mehrere Lagen",
    ortsteil_name: "Ortsteilname im Titel",
    ortsteil_adjektiv: "Ortsteil im Titel (z. B. „Endenicher …“)",
    stadtbezirk_name: "Stadtbezirk im Titel",
    stadtbezirk_adjektiv: "Stadtbezirk im Titel (Adjektiv)",
    vererbt: "von der übergeordneten Vorlage übernommen",
  };
  const STATUS = { beraten: "beraten", terminiert: "terminiert", offen: "noch offen", abgesagt: "Sitzung abgesagt" };
  // Allgemeine Erläuterungen der Verfahrensbegriffe; die Ergebnistexte selbst stehen wörtlich wie in der Quelle.
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

  const $ = (sel) => document.querySelector(sel);
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const fmtDate = (iso) => iso ? new Date(iso.length === 10 ? iso + "T12:00:00Z" : iso)
    .toLocaleDateString("de-DE", { timeZone: "Europe/Berlin", day: "2-digit", month: "2-digit", year: "numeric" }) : "";

  let index = null, geo = {}, meta = null, papers = [], area = null, selected = null;
  let map, cluster, outline, markers = new Map();

  // --- Gebiet --------------------------------------------------------------------------------

  function parseArea(value) {
    const [kind, key] = (value || "").split(":");
    if (!index) return { kind: "ortsteil", key: "endenich", name: "Endenich", file: PILOT };
    if (kind === "ortsteil") {
      const o = index.ortsteile.find((x) => x.slug === key);
      if (o) return { kind, key, name: o.name, bezirk: o.stadtbezirk, file: `${BONN}ortsteile/${key}.json` };
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
    if (!index) {
      sel.innerHTML = '<option value="ortsteil:endenich">Endenich (Pilot)</option>';
      return;
    }
    const groups = {};
    index.ortsteile.forEach((o) => (groups[o.stadtbezirk] ||= []).push(o));
    let html = "";
    for (const bz of Object.keys(groups).sort()) {
      html += `<optgroup label="Stadtbezirk ${esc(bz)}">`;
      html += groups[bz].sort((a, b) => a.name.localeCompare(b.name, "de"))
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
  function bestConfidence(p) {
    return areaLocs(p).reduce((best, l) => (RANK[l.confidence] > RANK[best] ? l.confidence : best), "niedrig");
  }
  function stand(p) {
    const s = p.process;
    if (!s.length) return "ohne Beratungsfolge";
    if (s.some((x) => x.authoritative && x.status === "beraten")) return "entschieden";
    return s.some((x) => x.status === "beraten") ? "in Beratung" : "offen";
  }

  async function loadArea(value, keepHash) {
    area = parseArea(value);
    $("#f-area").value = `${area.kind}:${area.key}`;
    $("#count").textContent = "Lade Vorlagen …";
    const data = await fetch(area.file).then((r) => r.json());
    meta = data.meta;
    papers = data.papers;
    for (const p of papers) p._stand = stand(p);
    const url = new URL(location.href);
    url.searchParams.set("gebiet", `${area.kind}:${area.key}`);
    if (!keepHash) url.hash = "";
    history.replaceState(null, "", url);
    document.title = `Ratskarte Bonn – ${area.kind === "ohne" ? "Vorlagen ohne Ortsbezug " + area.key : area.name}`;
    $("#f-conf").hidden = area.kind === "ohne";
    fillFilters();
    drawOutline();
    selected = null;
    $("#detail").innerHTML = '<p class="empty">Eine Vorlage in der Liste oder auf der Karte auswählen.</p>';
    render();
    const stand_ = meta.sources.map((s) => `${s.name}: ${String(s.retrieved_at || "–").slice(0, 10)}`).join(" · ");
    $("#stand").textContent = `Datenstand: ${stand_} · erzeugt ${meta.generated_at.slice(0, 10)}`;
  }

  // --- Karte -----------------------------------------------------------------------------------

  function initMap() {
    map = L.map("map", { scrollWheelZoom: true });
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19, attribution: "© OpenStreetMap-Mitwirkende",
    }).addTo(map);
    cluster = L.markerClusterGroup({ showCoverageOnHover: false, maxClusterRadius: 40 }).addTo(map);
  }

  function drawOutline() {
    if (outline) outline.remove();
    let feature = null;
    if (area.kind === "ortsteil") feature = geo.ortsteil.features.find((f) => f.properties.ortsteil_bez === area.name);
    if (area.kind === "bezirk") feature = geo.bezirk.features.find((f) => f.properties.bezirk_bez === area.name);
    outline = L.geoJSON(feature || geo.bezirk, { style: { color: "#0b5cad", weight: 2, fillOpacity: 0.04 } }).addTo(map);
    map.fitBounds(outline.getBounds(), { padding: [12, 12] });
  }

  function color(conf) {
    return getComputedStyle(document.documentElement).getPropertyValue("--" + conf).trim();
  }

  function drawMarkers(list) {
    cluster.clearLayers();
    markers.clear();
    for (const p of list) {
      const ms = areaLocs(p).filter((l) => l.level === "strasse" && l.lon != null).map((l) =>
        L.circleMarker([l.lat, l.lon], { radius: 7, weight: 1, color: "#fff", fillColor: color(l.confidence), fillOpacity: 0.9 })
          .bindTooltip(`${esc(p.reference)} · ${esc(l.name)}`).on("click", () => select(p, true)));
      ms.forEach((m) => cluster.addLayer(m));
      markers.set(p.reference, ms);
    }
  }

  // --- Liste und Filter ----------------------------------------------------------------------

  function options(sel, values, keep) {
    const current = keep ? sel.value : "";
    sel.innerHTML = '<option value="">alle</option>' +
      values.map((v) => `<option value="${esc(v)}">${esc(v)}</option>`).join("");
    if (values.includes(current)) sel.value = current;
  }

  function fillFilters() {
    const uniq = (arr) => [...new Set(arr.filter(Boolean))].sort((a, b) => a.localeCompare(b, "de"));
    options($("#f-type"), uniq(papers.map((p) => p.paper_type)), true);
    options($("#f-amt"), uniq(papers.map((p) => p.amt)), true);
    options($("#f-gremium"), uniq(papers.flatMap((p) => p.process.map((s) => s.gremium))), true);
    const years = [...new Set(papers.map((p) => (p.date || "").slice(0, 4)))].sort().reverse();
    $("#f-year").innerHTML = '<option value="">alle Jahre</option>' + years.map((y) => `<option value="${y}">${y}</option>`).join("");
  }

  function filtered() {
    const text = $("#f-text").value.trim().toLowerCase();
    const type = $("#f-type").value, year = $("#f-year").value, amt = $("#f-amt").value;
    const gremium = $("#f-gremium").value, standF = $("#f-stand").value;
    const confs = new Set([...document.querySelectorAll("#f-conf input:checked")].map((i) => i.value));
    return papers.filter((p) =>
      (!type || p.paper_type === type) &&
      (!year || (p.date || "") >= year) &&
      (!amt || p.amt === amt) &&
      (!gremium || p.process.some((s) => s.gremium === gremium)) &&
      (!standF || p._stand === standF) &&
      (area.kind === "ohne" || confs.has(bestConfidence(p))) &&
      (!text || (p.name + " " + p.reference).toLowerCase().includes(text)));
  }

  function render() {
    const list = filtered();
    const where = area.kind === "ohne" ? `ohne Ortsbezug, ${area.key}` : area.name;
    $("#count").textContent = `${list.length} von ${papers.length} Vorlagen · ${where}`;
    $("#papers").innerHTML = list.map((p) => {
      const conf = area.kind === "ohne" ? "" : `<span class="conf conf-${bestConfidence(p)}">Verortung ${bestConfidence(p)}</span>`;
      return `<li><button type="button" data-ref="${esc(p.reference)}" aria-current="${selected === p}">
        <span class="title">${esc(p.name)}</span>
        <span class="meta"><span>${esc(p.reference)}</span><span>${fmtDate(p.date)}</span><span>${esc(p.paper_type)}</span>
        <span>${esc(p._stand)}</span>${conf}</span></button></li>`;
    }).join("");
    drawMarkers(list);
  }

  // --- Detail ----------------------------------------------------------------------------------

  function glossKeys(text) {
    if (!text) return [];
    return text.split(" - ").map((t) => t.trim()).filter((t) => GLOSSAR[t]);
  }

  function timeline(process) {
    if (!process.length) return "<p>Keine Beratungsfolge erfasst.</p>";
    const current = process.findIndex((s) => s.status !== "beraten" && s.status !== "abgesagt");
    return `<ol class="timeline">${process.map((s, i) => `
      <li class="${s.status}${i === current ? " current" : ""}"${i === current ? ' aria-current="step"' : ""}>
        <span class="gremium">${esc(s.gremium || "Gremium unbekannt")}</span><br>
        ${s.start_date ? fmtDate(s.start_date) : ""}${s.number ? ` · TOP ${esc(s.number)}` : ""}<br>
        <span class="status">${esc(s.role || "")}${s.authoritative ? " (entscheidet)" : ""} · ${STATUS[s.status] || esc(s.status)}</span>
        ${s.result ? `<span class="result">„${esc(s.result)}“</span>` : ""}
      </li>`).join("")}</ol>`;
  }

  function glossary(p) {
    const keys = [...new Set(p.process.flatMap((s) => [...glossKeys(s.result), ...glossKeys(s.role)]))];
    if (!keys.length) return "";
    return `<details class="glossary"><summary>Was bedeuten die Begriffe?</summary><dl>${keys
      .map((k) => `<dt>${esc(k)}</dt><dd>${esc(GLOSSAR[k])}</dd>`).join("")}</dl>
      <p class="meta">Allgemeine Erläuterung; maßgeblich ist das Original.</p></details>`;
  }

  function reportLink(p) {
    // Issue-Formular .github/ISSUE_TEMPLATE/verortung.yml; Felder per URL vorausgefüllt
    const q = new URLSearchParams({ template: "verortung.yml", title: `Verortung prüfen: ${p.reference}`,
      drucksache: p.reference, titel: p.name, gebiet: area.name });
    return `${REPO}/issues/new?${q}`;
  }

  function select(p, fromMap) {
    selected = p;
    document.querySelectorAll(".papers button").forEach((b) => b.setAttribute("aria-current", b.dataset.ref === p.reference));
    const url = new URL(location.href);
    url.hash = encodeURIComponent(p.reference);
    history.replaceState(null, "", url);
    const resp = p.responsibility.map((r) => `${esc(r.label)}${r.derived ? ` <span class="derived" title="${esc(METHOD[r.method] || r.method)}">abgeleitet, über ${esc(r.evidence)}</span>` : ""}`).join("<br>");
    const orig = p.originators.length ? p.originators.map((o) => `${esc(o.actor)} <span class="derived" title="Fundstelle: ${esc(o.evidence)}">abgeleitet</span>`).join(", ") : "nicht erfasst";
    const locs = p.locations.length ? p.locations.map((l) => `<li><strong>${esc(l.name || l.ortsteil || l.stadtbezirk)}</strong>
      ${l.ortsteil && l.level === "strasse" ? `(${esc(l.ortsteil)})` : ""} – Stufe ${esc(l.stage)},
      <span class="conf conf-${esc(l.confidence)}">${esc(l.confidence)}</span><br>
      <span class="meta">${esc(METHOD[l.method] || l.method)}${l.evidence ? ` · Fundstelle: „${esc(l.evidence)}“` : ""}</span></li>`).join("")
      : "<li>stadtweit / ohne Ortsbezug</li>";
    const rel = (arr, label) => arr.length ? `<h3>${label}</h3><ul class="related">${arr.map((r) =>
      `<li>${esc(r.reference)} · ${esc(r.paper_type)} – ${esc(r.name)}</li>`).join("")}</ul>` : "";
    const retrieved = meta.sources.filter((s) => s.retrieved_at).map((s) => `${s.name} ${String(s.retrieved_at).slice(0, 10)}`).join(", ");
    $("#detail").innerHTML = `
      <h2>${esc(p.name)}</h2>
      <dl class="facts">
        <dt>Drucksache</dt><dd>${esc(p.reference)}</dd>
        <dt>Art</dt><dd>${esc(p.paper_type)}</dd>
        <dt>Datum</dt><dd>${fmtDate(p.date)}</dd>
        <dt>Amt</dt><dd>${resp || esc(p.amt)}</dd>
        <dt>Eingereicht von</dt><dd>${orig}</dd>
        <dt>Stand</dt><dd>${esc(p._stand)}</dd>
      </dl>
      <div class="links"><a href="${esc(p.web)}" target="_blank" rel="noopener">Original im Ratsinformationssystem</a>
        ${p.main_file ? `<a href="${esc(p.main_file)}" target="_blank" rel="noopener">Dokument (PDF)</a>` : ""}</div>
      <h3>Verfahren</h3>${timeline(p.process)}${glossary(p)}
      <h3>Ortsbezug</h3><ul class="locs">${locs}</ul>
      <p class="links"><a href="${reportLink(p)}" target="_blank" rel="noopener">Verortung falsch? Hinweis geben</a></p>
      ${rel(p.superordinated, "Bezieht sich auf")}${rel(p.subordinated, "Folgevorlagen")}
      <p class="meta">Quellobjekt: ${esc(p.source_object)} · Abruf: ${esc(retrieved)}</p>`;
    const ms = markers.get(p.reference) || [];
    if (!fromMap) {
      if (ms.length) map.setView(ms[0].getLatLng(), Math.max(map.getZoom(), 16));
      else map.fitBounds(outline.getBounds());
      if (matchMedia("(max-width: 1100px)").matches) $("#detail").focus();
    }
  }

  // --- Start -----------------------------------------------------------------------------------

  async function start() {
    try {
      index = await fetch(BONN + "index.json").then((r) => (r.ok ? r.json() : null));
    } catch (e) { index = null; }
    [geo.ortsteil, geo.bezirk] = await Promise.all([fetch(GEO.ortsteil).then((r) => r.json()), fetch(GEO.bezirk).then((r) => r.json())]);
    initMap();
    fillAreaSelect();
    $("#filters").addEventListener("submit", (e) => e.preventDefault());
    $("#filters").addEventListener("input", (e) => { if (e.target.id !== "f-area") render(); });
    $("#f-area").addEventListener("change", (e) => loadArea(e.target.value));
    $("#papers").addEventListener("click", (e) => {
      const b = e.target.closest("button[data-ref]");
      if (b) select(papers.find((p) => p.reference === b.dataset.ref));
    });
    const params = new URLSearchParams(location.search);
    await loadArea(params.get("gebiet") || DEFAULT_AREA, true);
    const ref = decodeURIComponent(location.hash.slice(1));
    const initial = papers.find((p) => p.reference === ref);
    if (initial) select(initial);
  }

  start().catch((err) => {
    $("#detail").innerHTML = `<p>Die Daten konnten nicht geladen werden (${esc(err.message)}).</p>`;
  });
})();
