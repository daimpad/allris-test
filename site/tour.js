// Tour durch die Funktionen der RIS-Karte Bonn: hebt nacheinander Bedienelemente hervor (abgedunkelte Umgebung,
// pulsierender Rahmen, pulsierende Punkte an erwähnten Einzelheiten) und erklärt sie in einer Karte.
// Start über Schaltflächen mit data-tour (Fenster „Los geht's“, Dialog „Über“). Bedienung: Weiter/Zurück,
// Pfeiltasten, Esc beendet. Bei reduzierter Bewegung ohne Animation (style.css). Kein Inline-Skript (CSP).
(function () {
  "use strict";
  const MOBILE = matchMedia("(max-width: 900px)");
  const $ = (s) => document.querySelector(s);

  // Schritte: target (Selektor) oder rect (Fläche aus app.js), before (Flächen öffnen), menu (Mega-Menü),
  // beacons (Selektoren für pulsierende Punkte), clip (sichtbarer Ausschnitt), when (Schritt nur, wenn verfügbar)
  const STEPS = [
    { title: "Willkommen zur Tour",
      text: "Die RIS-Karte zeigt, womit sich Rat, Bezirksvertretungen und Ausschüsse der Stadt Bonn befassen: wo (Karte), wann (Zeitleiste) und wer beteiligt ist (Ämter, Gremien, Fraktionen). Die Tour stellt die Funktionen der Reihe nach vor. Weiter mit der Pfeiltaste nach rechts, beenden mit Esc." },
    { menu: "mega-suche", target: "#mega-suche", fallback: "#nav-search", beacons: ["#q"],
      title: "Suche in ganz Bonn",
      text: "Ein Stichwort oder eine Drucksachennummer eingeben, etwa „Radweg“ oder „261856“. Darunter stehen Schnellfilter nach Thema und Partei; die Treffer lassen sich in der Liste anzeigen." },
    { target: "#f-area",
      title: "Gebiet wählen",
      text: "Ein Ortsteil, ein ganzer Stadtbezirk oder Vorlagen ohne Ortsbezug je Jahr. Zu Beginn zeigt die Karte ganz Bonn: erst einen Stadtbezirk anklicken, dann einen Ortsteil. Herangezoomt lassen sich Ortsteile direkt anklicken; „Ganz Bonn ansehen“ führt zurück. Karte, Liste und Zeitleiste zeigen jeweils das gewählte Gebiet." },
    { before: (ui) => { if (MOBILE.matches) ui.panel("panel-detail", false); }, rect: (ui) => ui.areaRect(), fallback: "#map",
      beacons: [".marker-cluster, path.leaflet-interactive", ".map-color", ".map-plans", ".map-bau", ".map-legend"],
      title: "Die Karte",
      text: "Jeder Punkt ist eine Vorlage mit Ortsbezug; Zahlen fassen nahe Punkte zusammen, ein Klick zoomt hinein. Die Farbe zeigt, wie sicher der Ort ist: grün gesichert (Koordinate oder Bebauungsplan der Stadt), braun erschlossen (Name im Titel), violett unsicher. „Farbe nach Thema“ färbt die Punkte stattdessen nach Thema; die Legende erklärt die Farben. „Bebauungspläne“ blendet die Geltungsbereiche der rechtskräftigen Pläne ein; ein Klick auf eine Fläche öffnet die Planchronik. „Baustellen“ zeigt gemeldete Baustellen mit unverbindlichen Terminen. „Farbige Karte“ schaltet den Hintergrund um." },
    { before: (ui) => ui.panel("panel-list", true), target: "#panel-list", beacons: ["#f-text", "#more-filters > summary"],
      title: "Die Liste",
      text: () => "Alle Vorlagen des Gebiets – gleichwertig zur Karte und mit der Tastatur bedienbar. Filter nach Stichwort, Vorlagenart, Stand, Thema und Partei; unter „Weitere Filter“ nach Amt, Gremium und Sicherheit der Ortsangabe."
        + (MOBILE.matches ? "" : " Die Breite lässt sich am Rand ziehen.") },
    { when: () => !document.querySelector('.toggle[data-panel="timeline-wrap"]').hidden,
      before: (ui) => ui.panel("timeline-wrap", true), target: "#timeline-wrap", beacons: [".tl-presets"],
      title: "Die Zeitleiste",
      text: "Die Balken zeigen, wie viele Vorlagen je Monat erschienen sind; dazu Sitzungen und Wahlperioden. Mit den Griffen oder einer Voreinstellung wählen Sie einen Zeitraum – Liste und Karte folgen." },
    { before: async (ui) => { await ui.example(); ui.panel("panel-detail", true); }, target: "#panel-detail", requires: "#detail .steps",
      beacons: ["#detail .links .btn-primary"],
      title: "Der Vorgang",
      text: "Ein Beispiel aus dem Gebiet: Drucksache, Art, Datum, federführendes Amt, Stand und Themen – und der Link zum Original im Ratsinformationssystem. Maßgeblich ist immer das Original." },
    { before: (ui) => ui.panel("panel-prozesse", false), target: "#detail .steps", clip: "#detail", scroll: true,
      title: "Die Prozesslinie",
      text: "Die Stationen des Verfahrens: Einreichung, Beratungen in den Gremien mit Datum und Ergebnis, Folgevorlagen. Ergebnisse stehen wörtlich wie in der Quelle. Jede Station trägt ihren Evidenzstatus: belegt, abgeleitet, nicht öffentlich oder unklar." },
    { before: (ui) => ui.panel("panel-prozesse", true), target: "#panel-prozesse", beacons: ["#tab-pz-gremien", "#tab-pz-aemter", ".pz-view"],
      title: "Prozesse: Wer entscheidet was?",
      text: "Alle Verfahrensarten – vom Bürgerantrag bis zum Bebauungsplan – mit ihren Schritten, Fristen und Rechtsgrundlagen und der Zahl der Vorgänge in Bonn. Unter „Gremien“ stehen Rat, Ausschüsse, Bezirksvertretungen und Beiräte mit ihren Zuständigkeiten und nächsten Sitzungen, unter „Ämter“ die Verwaltung mit ihren Abteilungen und den Vorlagen, für die sie federführend ist. Mit „Schaubild“ und „Liste“ wechseln Sie die Darstellung." },
    { before: (ui) => ui.panel("panel-prozesse", false), menu: "mega-auswertung", target: "#mega-auswertung",
      title: "Auswertung",
      text: "Kennzahlen zum Gebiet nach Thema, Partei, Jahr und Stand; ein Klick auf einen Balken filtert die Liste. Die Verfahrenswege zeigen für ganz Bonn, welche Gremien welche Vorlagenart beraten und wie Verfahren meist enden." },
    { menu: "mega-mitmachen", target: "#mega-mitmachen", beacons: ["#cta-termine", "#cta-feed .btn"],
      title: "Mitmachen",
      text: "Kommende Sitzungen, auch als Kalenderdatei; Feeds, die neue Vorlagen im Gebiet oder Änderungen an einem Vorgang melden; der Weg zum Bürgerantrag nach § 24 GO NRW; und ein Hinweis, wenn etwas falsch zugeordnet ist." },
    { menu: "mega-daten", target: "#mega-daten",
      title: "Offene Daten",
      text: "Alle Daten zum Herunterladen: das Datenpaket mit Prüfprotokollen, die verorteten Vorlagen als GeoJSON und eine Datensatzbeschreibung nach DCAT-AP. Darunter stehen Quellen, Lizenzen und Datenstand." },
    { target: ".toggle-ai",
      title: "Der Ratsassistent",
      text: "Ein KI-System beantwortet Fragen zu Bonner Ratsvorgängen und stützt sich dabei nur auf die Daten dieser Seite. Er braucht einen eigenen API-Schlüssel, nennt seine Quellen und verlinkt die Originale. Antworten können Fehler enthalten." },
    { target: ".nav-group.seg",
      title: "Flächen ein- und ausklappen",
      text: "Liste, Zeitleiste, Vorgang, Prozesse und Assistent lassen sich hier öffnen und schließen; die Karte bleibt darunter sichtbar. Esc schließt die Fläche, in der Sie gerade sind." },
    { target: "#about-open",
      title: "Über die Karte",
      text: "Hier steht, woher die Daten stammen, was Stand und Sicherheit der Angaben bedeuten und was die Karte nicht zeigen kann. Viel Freude beim Erkunden." },
  ];

  let steps = [], i = 0, root = null, card = null, spot = null, raf = 0, prevFocus = null, ui = null;

  const shown = (el) => el && el.getClientRects().length > 0 && getComputedStyle(el).visibility !== "hidden";
  const first = (sel) => sel ? [...document.querySelectorAll(sel)].find((el) => shown(el) && inView(el.getBoundingClientRect())) : null;
  const inView = (r) => r.bottom > 0 && r.right > 0 && r.top < innerHeight && r.left < innerWidth;

  function build() {
    root = document.createElement("div");
    root.className = "tour";
    root.innerHTML = `<div class="tour-block"></div><div class="tour-spot" aria-hidden="true"></div><div class="tour-beacons" aria-hidden="true"></div>
      <div class="tour-card glass" role="dialog" aria-modal="true" aria-labelledby="tour-title" aria-describedby="tour-text">
        <div class="tour-top"><span class="tour-count" id="tour-count"></span>
          <button type="button" class="icon-btn tour-x" data-tour-act="end" aria-label="Tour beenden"><svg class="icon" aria-hidden="true"><use href="#i-close"/></svg></button></div>
        <div class="tour-bar" aria-hidden="true"><span></span></div>
        <h2 class="tour-title" id="tour-title"></h2>
        <p class="tour-text" id="tour-text"></p>
        <div class="tour-nav">
          <button type="button" class="btn btn-ghost" data-tour-act="prev">Zurück</button>
          <button type="button" class="btn btn-cta" data-tour-act="next"></button>
        </div>
        <p class="visually-hidden" id="tour-live" aria-live="polite"></p>
      </div>`;
    document.body.appendChild(root);
    card = root.querySelector(".tour-card");
    spot = root.querySelector(".tour-spot");
    // Klicks bleiben in der Tour (sonst schlösse app.js das gerade geöffnete Menü)
    root.addEventListener("click", (e) => {
      e.stopPropagation();
      const b = e.target.closest("[data-tour-act]");
      if (!b) return;
      if (b.dataset.tourAct === "next") go(i + 1, 1);
      else if (b.dataset.tourAct === "prev") go(i - 1, -1);
      else end();
    });
  }

  function start() {
    ui = window.risKarte && window.risKarte.ui;
    if (!ui || root) return;
    const about = $("#about");
    if (about && about.open) about.close();
    prevFocus = document.activeElement;
    steps = STEPS.filter((s) => !s.when || s.when());
    ui.menu(null);
    build();
    // Rest der Seite für Tastatur und Screenreader sperren, solange die Tour läuft
    document.querySelectorAll("body > header, body > main").forEach((el) => { el.inert = true; });
    document.body.classList.add("touring");
    addEventListener("keydown", onKey, true);
    addEventListener("resize", layout);
    go(0, 1);
  }

  function end() {
    if (!root) return;
    cancelAnimationFrame(raf);
    removeEventListener("keydown", onKey, true);
    removeEventListener("resize", layout);
    document.querySelectorAll("body > header, body > main").forEach((el) => { el.inert = false; });
    document.body.classList.remove("touring");
    ui.menu(null);
    root.remove();
    root = null;
    const back = prevFocus && prevFocus.isConnected && shown(prevFocus) ? prevFocus : $("#detail-heading");
    if (back) back.focus();
  }

  let goSeq = 0;
  async function go(n, dir) {
    if (n >= steps.length) return end();
    if (n < 0) return;
    const s = steps[n], seq = ++goSeq;
    if (s.before) await s.before(ui);
    // während des Wartens (Beispiel wird geladen) weitergeblättert oder beendet
    if (seq !== goSeq || !root) return;
    ui.menu(s.menu || null);
    if (s.scroll) { const el = $(s.target); if (el) el.scrollIntoView({ block: "start" }); }
    // fehlt das Element (etwa ohne Vorlagen im Gebiet), in Laufrichtung überspringen
    if ((s.requires && !$(s.requires)) || (s.target && !s.fallback && !$(s.target))) {
      if (n + dir >= 0 && n + dir < steps.length) return go(n + dir, dir);
    }
    i = n;
    root.querySelector("#tour-count").textContent = `Schritt ${n + 1} von ${steps.length}`;
    root.querySelector(".tour-bar span").style.width = `${((n + 1) / steps.length) * 100}%`;
    root.querySelector("#tour-title").textContent = s.title;
    const text = typeof s.text === "function" ? s.text() : s.text;
    root.querySelector("#tour-text").textContent = text;
    const prev = root.querySelector('[data-tour-act="prev"]'), next = root.querySelector('[data-tour-act="next"]');
    prev.hidden = n === 0;
    next.textContent = n === 0 ? "Los geht's" : n === steps.length - 1 ? "Fertig" : "Weiter";
    root.querySelector("#tour-live").textContent = `Schritt ${n + 1} von ${steps.length}: ${s.title}. ${text}`;
    card.classList.remove("enter");
    void card.offsetWidth;  // Einblendung neu starten
    card.classList.add("enter");
    root.querySelector(".tour-beacons").innerHTML = (s.beacons || []).map(() => '<span class="tour-beacon"></span>').join("");
    next.focus();
    // Flächen gleiten herein: Lage einige Bilder lang nachführen
    cancelAnimationFrame(raf);
    const until = performance.now() + 700;
    const tick = () => { layout(); if (performance.now() < until) raf = requestAnimationFrame(tick); };
    tick();
  }

  function targetRect(s) {
    let r = null;
    if (s.rect) r = s.rect(ui);
    if (!r && (s.target || s.fallback)) {
      const el = first(s.target) || first(s.fallback);
      if (el) r = el.getBoundingClientRect();
    }
    if (!r) return null;
    let { left, top, right, bottom } = r;
    if (s.clip) {
      const c = $(s.clip).getBoundingClientRect();
      left = Math.max(left, c.left); top = Math.max(top, c.top); right = Math.min(right, c.right); bottom = Math.min(bottom, c.bottom);
    }
    const pad = 6;
    left = Math.max(4, left - pad); top = Math.max(4, top - pad);
    right = Math.min(innerWidth - 4, right + pad); bottom = Math.min(innerHeight - 4, bottom + pad);
    if (right - left < 12 || bottom - top < 12) return null;
    return { left, top, right, bottom, width: right - left, height: bottom - top };
  }

  function layout() {
    if (!root) return;
    const s = steps[i], r = targetRect(s);
    spot.classList.toggle("none", !r);
    const box = r || { left: innerWidth / 2, top: innerHeight / 2, width: 0, height: 0 };
    Object.assign(spot.style, { left: box.left + "px", top: box.top + "px", width: box.width + "px", height: box.height + "px" });
    // pulsierende Punkte: Mitte kleiner Elemente, sonst rechte obere Ecke
    const beacons = root.querySelectorAll(".tour-beacon");
    (s.beacons || []).forEach((sel, k) => {
      const el = first(sel), b = beacons[k];
      if (!b) return;
      b.hidden = !el;
      if (!el) return;
      const e = el.getBoundingClientRect(), small = e.width < 40 && e.height < 40;
      b.style.left = (small ? e.left + e.width / 2 : e.right - 8) + "px";
      b.style.top = (small ? e.top + e.height / 2 : e.top + 8) + "px";
    });
    placeCard(r);
  }

  function placeCard(r) {
    const vw = innerWidth, vh = innerHeight, gap = 16, m = 10;
    const cw = card.offsetWidth, ch = card.offsetHeight;
    const clampX = (x) => Math.max(m, Math.min(vw - cw - m, x));
    const clampY = (y) => Math.max(m, Math.min(vh - ch - m, y));
    let x, y;
    if (!r) { x = (vw - cw) / 2; y = (vh - ch) / 2; }
    else if (MOBILE.matches) { x = (vw - cw) / 2; y = (r.top + r.bottom) / 2 > vh / 2 ? m : vh - ch - m; }
    else if (r.bottom + gap + ch <= vh - m && r.height < vh * 0.6) { x = clampX(r.left + r.width / 2 - cw / 2); y = r.bottom + gap; }
    else if (r.right + gap + cw <= vw - m) { x = r.right + gap; y = clampY(r.top); }
    else if (r.left - gap - cw >= m) { x = r.left - gap - cw; y = clampY(r.top); }
    else if (r.top - gap - ch >= m) { x = clampX(r.left + r.width / 2 - cw / 2); y = r.top - gap - ch; }
    else { x = clampX(r.left + r.width / 2 - cw / 2); y = vh - ch - m; }
    card.style.left = Math.round(x) + "px";
    card.style.top = Math.round(y) + "px";
  }

  function onKey(e) {
    if (!root) return;
    const keys = { Escape: end, ArrowRight: () => go(i + 1, 1), ArrowLeft: () => go(i - 1, -1) };
    if (keys[e.key]) { e.preventDefault(); e.stopPropagation(); keys[e.key](); return; }
    if (e.key === "Tab") {  // Fokus bleibt in der Karte
      const f = [...card.querySelectorAll("button")].filter(shown);
      const k = f.indexOf(document.activeElement);
      e.preventDefault();
      f[(k + (e.shiftKey ? -1 : 1) + f.length) % f.length].focus();
    }
  }

  document.addEventListener("click", (e) => { if (e.target.closest("[data-tour]")) start(); });
})();
