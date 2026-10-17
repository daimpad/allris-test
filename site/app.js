// Ratskarte Endenich – liest die Exporte der Pipeline (data/export/endenich) und zeigt Liste, Karte, Detail.
(function () {
  "use strict";
  const DATA = "data/export/endenich/vorlagen.json";
  const ORTSTEILE = "data/geo/ortsteile_bonn.geojson";
  const ORTSTEIL = "Endenich";
  const RANK = { hoch: 3, mittel: 2, niedrig: 1 };
  const METHOD = {
    oparl_location: "Koordinate der Stadt (OParl)",
    strasse: "Straßenname im Titel",
    "strasse+ortsteil": "Straßen- und Ortsteilname im Titel",
    "strasse+bezirk": "Straßenname im Titel, Bezirk eingegrenzt",
    strasse_mehrdeutig: "Straßenname im Titel, mehrere Lagen",
    ortsteil_name: "Ortsteilname im Titel",
    ortsteil_adjektiv: "Ortsteil im Titel („Endenicher …“)",
    stadtbezirk_name: "Stadtbezirk im Titel",
    stadtbezirk_adjektiv: "Stadtbezirk im Titel (Adjektiv)",
    vererbt: "von der übergeordneten Vorlage übernommen",
  };
  const STATUS = { beraten: "beraten", terminiert: "terminiert", offen: "noch offen", abgesagt: "abgesagt" };

  const $ = (sel) => document.querySelector(sel);
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const fmtDate = (iso) => iso ? new Date(iso.length === 10 ? iso + "T12:00:00Z" : iso)
    .toLocaleDateString("de-DE", { timeZone: "Europe/Berlin", day: "2-digit", month: "2-digit", year: "numeric" }) : "";

  let papers = [], markers = new Map(), selected = null, map, outline;

  function localLocs(p) {
    return p.locations.filter((l) => l.ortsteil === ORTSTEIL);
  }
  function bestConfidence(p) {
    return localLocs(p).reduce((best, l) => (RANK[l.confidence] > RANK[best] ? l.confidence : best), "niedrig");
  }

  function initMap(geo) {
    map = L.map("map", { scrollWheelZoom: true });
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19, attribution: "© OpenStreetMap-Mitwirkende",
    }).addTo(map);
    const feature = geo.features.find((f) => f.properties.ortsteil_bez === ORTSTEIL);
    outline = L.geoJSON(feature, { style: { color: "#0b5cad", weight: 2, fillOpacity: 0.05 } }).addTo(map);
    map.fitBounds(outline.getBounds(), { padding: [12, 12] });
  }

  function color(conf) {
    return getComputedStyle(document.documentElement).getPropertyValue("--" + conf).trim();
  }

  function drawMarkers(list) {
    markers.forEach((ms) => ms.forEach((m) => m.remove()));
    markers.clear();
    for (const p of list) {
      const ms = localLocs(p).filter((l) => l.level === "strasse" && l.lon != null).map((l) =>
        L.circleMarker([l.lat, l.lon], {
          radius: 7, weight: 1, color: "#fff", fillColor: color(l.confidence), fillOpacity: 0.9,
        }).bindTooltip(`${esc(p.reference)} · ${esc(l.name)}`).on("click", () => select(p, true)).addTo(map));
      markers.set(p.reference, ms);
    }
  }

  function filtered() {
    const text = $("#f-text").value.trim().toLowerCase();
    const type = $("#f-type").value;
    const year = $("#f-year").value;
    const confs = new Set([...document.querySelectorAll("fieldset input:checked")].map((i) => i.value));
    return papers.filter((p) =>
      (!type || p.paper_type === type) &&
      (!year || (p.date || "") >= year) &&
      confs.has(bestConfidence(p)) &&
      (!text || (p.name + " " + p.reference).toLowerCase().includes(text)));
  }

  function render() {
    const list = filtered();
    $("#count").textContent = `${list.length} von ${papers.length} Vorlagen`;
    $("#papers").innerHTML = list.map((p) => {
      const c = bestConfidence(p);
      return `<li><button type="button" data-ref="${esc(p.reference)}" aria-current="${selected === p}">
        <span class="title">${esc(p.name)}</span>
        <span class="meta"><span>${esc(p.reference)}</span><span>${fmtDate(p.date)}</span><span>${esc(p.paper_type)}</span>
        <span class="conf conf-${c}">Verortung ${c}</span></span></button></li>`;
    }).join("");
    drawMarkers(list);
  }

  function timeline(process) {
    if (!process.length) return "<p>Keine Beratungsfolge erfasst.</p>";
    const current = process.findIndex((s) => s.status !== "beraten" && s.status !== "abgesagt");
    return `<ol class="timeline">${process.map((s, i) => `
      <li class="${s.status}${i === current ? " current" : ""}">
        <span class="gremium">${esc(s.gremium || "Gremium unbekannt")}</span><br>
        ${s.start_date ? fmtDate(s.start_date) : ""}${s.number ? ` · TOP ${esc(s.number)}` : ""}<br>
        <span class="status">${esc(s.role || "")}${s.authoritative ? " (entscheidet)" : ""} · ${STATUS[s.status] || esc(s.status)}</span>
        ${s.result ? `<span class="result">„${esc(s.result)}“</span>` : ""}
      </li>`).join("")}</ol>`;
  }

  function select(p, fromMap) {
    selected = p;
    document.querySelectorAll(".papers button").forEach((b) => b.setAttribute("aria-current", b.dataset.ref === p.reference));
    history.replaceState(null, "", "#" + encodeURIComponent(p.reference));
    const resp = p.responsibility.map((r) => `${esc(r.label)}${r.derived ? ` <span class="derived" title="${esc(METHOD[r.method] || r.method)}: ${esc(r.evidence)}">abgeleitet, über ${esc(r.evidence)}</span>` : ""}`).join("<br>");
    const orig = p.originators.length ? p.originators.map((o) => `${esc(o.actor)} <span class="derived" title="${esc(o.evidence)}">abgeleitet</span>`).join(", ") : "nicht erfasst";
    const locs = p.locations.map((l) => `<li><strong>${esc(l.name || l.ortsteil || l.stadtbezirk)}</strong>
      ${l.ortsteil && l.level === "strasse" ? `(${esc(l.ortsteil)})` : ""} – Stufe ${esc(l.stage)},
      <span class="conf conf-${esc(l.confidence)}">${esc(l.confidence)}</span><br>
      <span class="meta">${esc(METHOD[l.method] || l.method)}${l.evidence ? ` · Fundstelle: „${esc(l.evidence)}“` : ""}</span></li>`).join("");
    const rel = (arr, label) => arr.length ? `<h3>${label}</h3><ul class="related">${arr.map((r) =>
      `<li>${esc(r.reference)} · ${esc(r.paper_type)} – ${esc(r.name)}</li>`).join("")}</ul>` : "";
    $("#detail").innerHTML = `
      <h2>${esc(p.name)}</h2>
      <dl class="facts">
        <dt>Drucksache</dt><dd>${esc(p.reference)}</dd>
        <dt>Art</dt><dd>${esc(p.paper_type)}</dd>
        <dt>Datum</dt><dd>${fmtDate(p.date)}</dd>
        <dt>Amt</dt><dd>${resp || esc(p.amt)}</dd>
        <dt>Eingereicht von</dt><dd>${orig}</dd>
      </dl>
      <div class="links"><a href="${esc(p.web)}" target="_blank" rel="noopener">Original im Ratsinformationssystem</a>
        ${p.main_file ? `<a href="${esc(p.main_file)}" target="_blank" rel="noopener">Dokument (PDF)</a>` : ""}</div>
      <h3>Verfahren</h3>${timeline(p.process)}
      <h3>Ortsbezug</h3><ul class="locs">${locs}</ul>
      ${rel(p.superordinated, "Bezieht sich auf")}${rel(p.subordinated, "Folgevorlagen")}
      <p class="meta">Quellobjekt: ${esc(p.source_object)}</p>`;
    const pts = (markers.get(p.reference) || []).map((m) => m.getLatLng());
    if (!fromMap) {
      if (pts.length) map.setView(pts[0], Math.max(map.getZoom(), 16));
      else map.fitBounds(outline.getBounds());
      if (matchMedia("(max-width: 1100px)").matches) $("#detail").focus();
    }
    (markers.get(p.reference) || []).forEach((m) => m.openTooltip());
  }

  function fillSelect(sel, values) {
    sel.insertAdjacentHTML("beforeend", values.map((v) => `<option value="${esc(v)}">${esc(v)}</option>`).join(""));
  }

  Promise.all([fetch(DATA).then((r) => r.json()), fetch(ORTSTEILE).then((r) => r.json())]).then(([data, geo]) => {
    papers = data.papers;
    initMap(geo);
    fillSelect($("#f-type"), [...new Set(papers.map((p) => p.paper_type))].sort());
    $("#f-year").innerHTML = '<option value="">alle Jahre</option>' +
      [...new Set(papers.map((p) => (p.date || "").slice(0, 4)))].sort().reverse()
        .map((y) => `<option value="${y}">${y}</option>`).join("");
    const stand = data.meta.sources.map((s) => `${s.name}: ${String(s.retrieved_at || "–").slice(0, 10)}`).join(" · ");
    $("#stand").textContent = `Datenstand: ${stand} · erzeugt ${data.meta.generated_at.slice(0, 10)}`;
    $("#filters").addEventListener("input", render);
    $("#filters").addEventListener("submit", (e) => e.preventDefault());
    $("#papers").addEventListener("click", (e) => {
      const b = e.target.closest("button[data-ref]");
      if (b) select(papers.find((p) => p.reference === b.dataset.ref));
    });
    render();
    const ref = decodeURIComponent(location.hash.slice(1));
    const initial = papers.find((p) => p.reference === ref);
    if (initial) select(initial);
  }).catch((err) => {
    $("#detail").innerHTML = `<p>Die Daten konnten nicht geladen werden (${esc(err.message)}).</p>`;
  });
})();
