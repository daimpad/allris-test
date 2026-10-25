"""Prozessbild der Themenseite „Kultur und Haushalt“: Zeitleiste mit Bahnen je Gremium (SVG, ohne Skript),
Stand je Strang als Balken und Aufrufe zum Mitwirken. Grundlage ist dossier.daten(); erzeugt im seo-Schritt.

Beschlüsse und Anträge erscheinen als nummerierte Punkte (entschieden, beraten, offen), die Phasen des Haushalts
2027/2028 als Balken (geplant laut 261064, abgeleitet), kommende öffentliche Sitzungen mit Hand-Symbol und der
Frist 21 Tage vorher (GeschO §§ 26, 27). Die nummerierte Liste unter dem Bild ist die Textfassung."""
from datetime import date
from html import escape
from urllib.parse import quote

from . import dossier

T0, T1 = date(2025, 11, 1), date(2027, 4, 1)
# Zeitachse in zwei Abschnitten: der Rückblick gestaucht, die Monate der Haushaltsberatung breiter
KNICK, ANTEIL_RUECKBLICK = date(2026, 9, 1), 0.42
W, LINKS, RECHTS, OBEN, BAHN = 1100, 170, 16, 62, 52
MONATE = "Jan Feb Mär Apr Mai Jun Jul Aug Sep Okt Nov Dez".split()
ART = {"entschieden": "entschieden", "beraten": "beraten, ohne abschließende Entscheidung", "offen": "offen"}
ICON = {
    "hand": '<path d="M8 13V5.5a1.5 1.5 0 0 1 3 0V12M11 11V4.5a1.5 1.5 0 0 1 3 0V12M14 11.5V6a1.5 1.5 0 0 1 3 0v8a7 7 0 '
            '0 1-7 7h-.6a6 6 0 0 1-4.5-2.1L2.6 16a1.5 1.5 0 0 1 2.2-2L8 16"/>',
    "calendar": '<rect x="3.5" y="5" width="17" height="15.5" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
    "rss": '<path d="M5 11a8 8 0 0 1 8 8M5 4.5A14.5 14.5 0 0 1 19.5 19"/><circle cx="6" cy="18" r="1.4"/>',
    "people": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c.5-3.6 3.2-6 6.5-6s6 2.4 6.5 6"/>'
              '<path d="M16 4.6a3.5 3.5 0 0 1 0 6.8M18.5 14.6c1.8.9 3 2.7 3.2 5.4"/>',
}
TEXT, LILA, LILA_HELL, GRAU, BERNSTEIN = "#0f0f14", "#6d28d9", "#c4b5fd", "#5a5a68", "#f59e0b"


def _d(iso):
    return date.fromisoformat(iso[:10])


def _x(iso):
    d, breite = min(max(_d(iso), T0), T1), W - LINKS - RECHTS
    if d <= KNICK:
        return LINKS + breite * ANTEIL_RUECKBLICK * (d - T0).days / (KNICK - T0).days
    return LINKS + breite * (ANTEIL_RUECKBLICK + (1 - ANTEIL_RUECKBLICK) * (d - KNICK).days / (T1 - KNICK).days)


def _kurz(iso):
    return f"{iso[8:10]}.{iso[5:7]}."


def _datum(iso):
    return f"{iso[8:10]}.{iso[5:7]}.{iso[:4]}" if iso else "–"


def _icon(name, size=18, farbe=LILA):
    return (f'<svg class="icon" viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="{farbe}" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICON[name]}</svg>')


def _zeile(b):
    return OBEN + [k for k, _ in dossier.BAHNEN].index(b) * BAHN


def svg(d):
    """Zeitleiste mit Bahnen als SVG-Zeichenkette."""
    heute = d["heute"]
    h_bahnen = len(dossier.BAHNEN) * BAHN
    hoehe = OBEN + h_bahnen + 66
    out = [f'<svg class="pb-svg" viewBox="0 0 {W} {hoehe}" role="img" aria-labelledby="pb-titel pb-text" '
           f'xmlns="http://www.w3.org/2000/svg" font-family="Inter, system-ui, sans-serif">',
           '<title id="pb-titel">Zeitleiste: Haushalt und Kultur in Rat, Ausschüssen und Bezirksvertretungen</title>',
           f'<desc id="pb-text">{escape(_beschreibung(d))}</desc>',
           '<defs><pattern id="pb-schraffur" width="6" height="6" patternUnits="userSpaceOnUse" '
           'patternTransform="rotate(45)"><rect width="6" height="6" fill="#f1f1f4"/>'
           '<line x1="0" y1="0" x2="0" y2="6" stroke="#c9c9d3" stroke-width="2"/></pattern>'
           f'<symbol id="pb-hand" viewBox="0 0 24 24">{ICON["hand"]}</symbol></defs>']
    # Bahnen
    for i, (key, label) in enumerate(dossier.BAHNEN):
        y = _zeile(key)
        out.append(f'<rect x="0" y="{y}" width="{W}" height="{BAHN}" fill="{"#f7f5ff" if i % 2 == 0 else "#ffffff"}"/>')
        out.append(f'<text x="10" y="{y + BAHN / 2 + 4.5}" font-size="13" font-weight="600" fill="{TEXT}">'
                   f'{escape(label)}</text>')
    # Monate
    m = date(T0.year, T0.month, 1)
    while m < T1:
        x = _x(m.isoformat())
        out.append(f'<line x1="{x:.1f}" y1="{OBEN - 6}" x2="{x:.1f}" y2="{OBEN + h_bahnen}" stroke="#e4e2ee"/>')
        out.append(f'<text x="{x + 3:.1f}" y="{OBEN - 10}" font-size="11" fill="{GRAU}">{MONATE[m.month - 1]}</text>')
        if m.month == 1 or m == date(T0.year, T0.month, 1):
            out.append(f'<text x="{x + 3:.1f}" y="{OBEN - 26}" font-size="12" font-weight="600" fill="{TEXT}">'
                       f'{m.year}</text>')
        m = date(m.year + (m.month == 12), m.month % 12 + 1, 1)
    # Zeitraum der Haushaltsberatung: Mitwirkung möglich (ab heute bis zum geplanten Ratsbeschluss)
    fenster = [p for p in d["phasen"] if p["bahn"] not in ("plan",) and not p["intern"]]
    if fenster:
        von, bis = max(heute, min(p["von"] for p in fenster)), max(p["bis"] for p in fenster)
        if von < bis:
            y0, y1 = _zeile("bv"), _zeile("rat") + BAHN
            out.append(f'<rect x="{_x(von):.1f}" y="{y0}" width="{_x(bis) - _x(von):.1f}" height="{y1 - y0}" '
                       f'fill="{BERNSTEIN}" fill-opacity="0.16" stroke="{BERNSTEIN}" stroke-opacity="0.7"/>')
    # Phasen (geplant laut Terminplan)
    for p in d["phasen"]:
        x0, x1, y = _x(p["von"]), _x(p["bis"]), _zeile(p["bahn"])
        intern, plan = p["intern"], p["bahn"] == "plan"
        out.append(f'<rect x="{x0:.1f}" y="{y + 9}" width="{x1 - x0:.1f}" height="{BAHN - 18}" rx="6" '
                   + ('fill="url(#pb-schraffur)" stroke="#a9a9b8"' if intern else
                      f'fill="#ede9fe" stroke="{LILA}"' if plan else
                      f'fill="#ede9fe" fill-opacity="0.6" stroke="{LILA}" stroke-opacity="0.6" stroke-dasharray="4 3"')
                   + f'><title>{escape(p["text"])} ({_datum(p["von"])}–{_datum(p["bis"])}, geplant laut 261064)</title></rect>')
        if plan and x1 - x0 > 7 * len(p["text"]) - 10:
            out.append(f'<text x="{(x0 + x1) / 2:.1f}" y="{y + BAHN / 2 + 4}" font-size="11" text-anchor="middle" '
                       f'font-weight="600" fill="{GRAU if intern else LILA}">{escape(p["text"])}</text>')
    # Sitzungen mit Frist
    zuletzt = {}
    for s in sorted(d["sitzungen"], key=lambda s: s["date"]):
        x = _x(s["date"])
        # dicht folgende Sitzungen derselben Bahn abwechselnd oben und unten
        vorher = zuletzt.get(s["bahn"])
        oben = bool(vorher) and x - vorher[0] < 26 and not vorher[1]
        zuletzt[s["bahn"]] = (x, oben)
        yc = _zeile(s["bahn"]) + BAHN / 2 + (-11 if oben else 0)
        if s["frist"] >= heute:
            xf, yf = _x(s["frist"]), yc + 14
            out.append(f'<line x1="{xf:.1f}" y1="{yf:.1f}" x2="{x:.1f}" y2="{yf:.1f}" stroke="{BERNSTEIN}" '
                       f'stroke-width="2" stroke-dasharray="2 3"/>')
            out.append(f'<line x1="{xf:.1f}" y1="{yf - 6:.1f}" x2="{xf:.1f}" y2="{yf + 5:.1f}" stroke="{BERNSTEIN}" '
                       f'stroke-width="2.5"><title>Frist für Anträge und Fragen zur Sitzung {escape(s["gremium"])}: '
                       f'{_datum(s["frist"])}</title></line>')
        out.append(f'<g><title>{escape(s["gremium"])}, {_datum(s["date"])}: öffentliche Sitzung</title>'
                   f'<circle cx="{x:.1f}" cy="{yc:.1f}" r="10.5" fill="#fff" stroke="{BERNSTEIN}" stroke-width="2"/>'
                   f'<use href="#pb-hand" x="{x - 7:.1f}" y="{yc - 7:.1f}" width="14" height="14" fill="none" '
                   f'stroke="{TEXT}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></g>')
    # Beschlüsse und Anträge
    belegt = {}
    for p in d["punkte"]:
        if not p["date"]:
            continue
        x, y = _x(p["date"]), _zeile(p["bahn"]) + BAHN / 2
        for dy in (0, -11, 11, -5, 5):
            if all(abs(x - bx) > 18 or abs(y + dy - by) > 17 for bx, by in belegt.get(p["bahn"], [])):
                break
        else:
            dy = 0
            while any(abs(x - bx) <= 18 and abs(y - by) <= 17 for bx, by in belegt.get(p["bahn"], [])):
                x += 6
        belegt.setdefault(p["bahn"], []).append((x, y + dy))
        fill, stroke, farbe = {"entschieden": (LILA, LILA, "#fff"), "beraten": (LILA_HELL, LILA, TEXT),
                               "offen": ("#fff", LILA, TEXT)}[p["art"]]
        out.append(f'<g><title>{p["nr"]}: {escape(p["reference"])} {escape(p["name"])} – {escape(p["stand"])}'
                   f' ({escape(p["gremium"] or "")}, {_datum(p["date"])})</title>'
                   f'<circle cx="{x:.1f}" cy="{y + dy:.1f}" r="9" fill="{fill}" stroke="{stroke}" stroke-width="1.8"/>'
                   f'<text x="{x:.1f}" y="{y + dy + 3.6:.1f}" font-size="10" font-weight="700" text-anchor="middle" '
                   f'fill="{farbe}">{p["nr"]}</text></g>')
    # heute
    xh = _x(heute)
    out.append(f'<line x1="{xh:.1f}" y1="{OBEN - 44}" x2="{xh:.1f}" y2="{OBEN + h_bahnen}" stroke="{TEXT}" '
               f'stroke-width="2"/>')
    out.append(f'<text x="{xh + 5:.1f}" y="{OBEN - 40}" font-size="12" font-weight="700" fill="{TEXT}">'
               f'Stand {_kurz(heute)}</text>')
    # Legende
    y = OBEN + h_bahnen + 24
    eintraege = [("punkt", "entschieden", LILA, LILA), ("punkt", "beraten, ohne Entscheidung", LILA_HELL, LILA),
                 ("punkt", "offen", "#fff", LILA), ("hand", "öffentliche Sitzung: hier einbringen", "", ""),
                 ("frist", "Frist 21 Tage vorher", "", ""), ("phase", "geplant laut Terminplan", "", ""),
                 ("intern", "nicht öffentlich", "", ""), ("fenster", "Zeitraum der Haushaltsberatung", "", "")]
    x = 10
    for art, text, f, s in eintraege:
        if art == "punkt":
            out.append(f'<circle cx="{x + 8}" cy="{y}" r="7" fill="{f}" stroke="{s}" stroke-width="1.8"/>')
        elif art == "hand":
            out.append(f'<circle cx="{x + 8}" cy="{y}" r="9" fill="#fff" stroke="{BERNSTEIN}" stroke-width="2"/>'
                       f'<use href="#pb-hand" x="{x + 2}" y="{y - 6}" width="12" height="12" fill="none" stroke="{TEXT}" '
                       f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
        elif art == "frist":
            out.append(f'<line x1="{x + 2}" y1="{y - 7}" x2="{x + 2}" y2="{y + 7}" stroke="{BERNSTEIN}" stroke-width="2.5"/>'
                       f'<line x1="{x + 2}" y1="{y}" x2="{x + 16}" y2="{y}" stroke="{BERNSTEIN}" stroke-width="2" '
                       f'stroke-dasharray="2 3"/>')
        elif art == "phase":
            out.append(f'<rect x="{x}" y="{y - 7}" width="16" height="14" rx="3" fill="#ede9fe" stroke="{LILA}" '
                       f'stroke-dasharray="4 3"/>')
        elif art == "intern":
            out.append(f'<rect x="{x}" y="{y - 7}" width="16" height="14" rx="3" fill="url(#pb-schraffur)" '
                       f'stroke="#a9a9b8"/>')
        else:
            out.append(f'<rect x="{x}" y="{y - 7}" width="16" height="14" fill="{BERNSTEIN}" fill-opacity="0.16" '
                       f'stroke="{BERNSTEIN}" stroke-opacity="0.7"/>')
        out.append(f'<text x="{x + 22}" y="{y + 4}" font-size="12" fill="{TEXT}">{escape(text)}</text>')
        x += 34 + 6.4 * len(text)
        if art == "hand":  # zweite Zeile: Mitwirkung und Phasen
            x, y = 10, y + 24
    out.append("</svg>")
    return "".join(out)


def _beschreibung(d):
    n = {k: sum(1 for p in d["punkte"] if p["art"] == k) for k in ART}
    naechste = ", ".join(f"{s['gremium']} am {_datum(s['date'])}" for s in d["sitzungen"][:4])
    return (f"Zeitleiste von November 2025 bis März 2027, Datenstand {_datum(d['heute'])}. "
            f"{len(d['punkte'])} Beschlüsse und Anträge: {n['entschieden']} entschieden, {n['beraten']} beraten ohne "
            f"abschließende Entscheidung, {n['offen']} offen. Der Haushalt 2027/2028 wird laut Terminplan von Oktober "
            f"bis Dezember 2026 beraten und im Dezember im Rat beschlossen. Nächste öffentliche Sitzungen: {naechste}.")


def stand_balken(d):
    """Stand je Strang als gestapelte Balken in HTML (skaliert mit der Seite; Zahlen sichtbar, Wörter für Screenreader)."""
    teile = [("entschieden", "entschieden", "pb-s1"), ("in Beratung", "in Beratung", "pb-s2"),
             ("beraten, ohne Entscheidung", "zur Kenntnis genommen oder ohne Votum", "pb-s3"),
             ("offen", "offen", "pb-s4")]
    groesste = max((len(s["vorlagen"]) for s in d["straenge"]), default=1) or 1
    zeilen = []
    for s in d["straenge"]:
        segmente = []
        for k, text, cls in teile:
            n = sum(1 for r in s["vorlagen"] if r["stand"] == k)
            if n:
                segmente.append(f'<span class="pb-seg {cls}" style="flex-grow:{n}" title="{n} {escape(text)}">{n}'
                                f'<span class="pb-sr"> {escape(text)}</span></span>')
        breite = 100 * len(s["vorlagen"]) / groesste
        zeilen.append(f'      <li><span class="pb-name">{escape(s["titel"])}</span><span class="pb-bar" '
                      f'style="width:{breite:.1f}%">{"".join(segmente)}</span></li>')
    legende = "".join(f'<span><i class="pb-seg {cls}"></i>{escape(text)}</span>' for _, text, cls in teile)
    return ('    <ul class="pb-balken">\n' + "\n".join(zeilen) + f'\n    </ul>\n    <p class="pb-legende">{legende}</p>')


def _karte(icon, titel, text, aktionen):
    return (f'      <div class="pb-karte">{_icon(icon, 22)}<h3>{escape(titel)}</h3><p>{text}</p>'
            f'<p class="pb-aktionen">{aktionen}</p></div>')


def aufrufe(d, root):
    heute = d["heute"]
    offen = sorted((s for s in d["sitzungen"] if s["frist"] >= heute), key=lambda s: s["frist"])
    naechste = d["sitzungen"][0] if d["sitzungen"] else None
    frist = (f"Nächste offene Frist: {_datum(offen[0]['frist'])} für {escape(offen[0]['gremium'])} "
             f"am {_datum(offen[0]['date'])} (berechnet, abgeleitet)." if offen else
             "Für die eingetragenen Sitzungen sind die Fristen abgelaufen.")
    bv = next((s for s in offen if s["bahn"] == "bv"), None)
    karten = [
        _karte("calendar", "Termine in den Kalender",
               "Die Sitzungen dieser Seite als Kalenderdatei, mit Link zur Tagesordnung, sobald sie erscheint.",
               f'<a class="pb-knopf" href="{root}data/export/bonn/dossiers/kultur.ics" download>Kalender (.ics)</a>'),
        _karte("rss", "Auf dem Laufenden bleiben",
               "Neue Vorlagen und Beratungsergebnisse zu Haushalt und Kultur im Feed-Reader.",
               f'<a class="pb-knopf" href="{root}data/export/bonn/dossiers/kultur.xml">Feed abonnieren</a>'),
        _karte("people", "Sitzung besuchen",
               "Rat, Ausschüsse und Bezirksvertretungen tagen in der Regel öffentlich; Ratssitzungen werden live "
               "übertragen." + (f" Nächste Sitzung: {escape(naechste['gremium'])} am {_datum(naechste['date'])}."
                                if naechste else ""),
               '<a class="pb-knopf" href="#sitzungen">Alle Termine</a>'),
        _karte("hand", "Frage oder Anregung einreichen",
               "Einwohnerfrage in einer Bezirksvertretung (GeschO § 26) oder Bürgerantrag an Rat oder "
               "Bezirksvertretung (§ 24 GO NRW), spätestens 21 Tage vor der Sitzung. " + frist
               + (f" Für Fragen: {escape(bv['gremium'])} bis {_datum(bv['frist'])}." if bv and bv is not offen[0] else ""),
               '<a class="pb-knopf" href="https://www.bonn.de/vv/produkte/buergerantrag-anregungen-und-beschwerden-'
               'gemaess-24-gemeindeordnung-nrw.php">Bürgerantrag bei der Stadt</a> '
               f'<a class="pb-knopf pb-knopf-leise" href="{root}?mitmachen=1">Alle Wege und Fristen</a>'),
    ]
    return '    <div class="pb-karten">\n' + "\n".join(karten) + "\n    </div>"


def liste(d, root):
    zeilen = []
    for p in d["punkte"]:
        ref = escape(p["reference"])
        link = (f'<a href="{root}?gebiet={quote(p["gebiet"], safe=":")}#{quote(p["reference"])}">{ref}</a>'
                if p.get("gebiet") else ref)
        zeilen.append(f'        <li value="{p["nr"]}"><span class="pb-nr pb-{p["art"]}">{p["nr"]}</span> {link} '
                      f'{escape(p["name"] or "")} <small>– {escape(p["stand"])}; {escape(p["gremium"] or "")} '
                      f'{_datum(p["date"])}</small></li>')
    return (f'    <details class="pb-liste">\n      <summary>Die {len(d["punkte"])} Beschlüsse und Anträge im Bild'
            f'</summary>\n      <ol>\n' + "\n".join(zeilen) + "\n      </ol>\n    </details>")


def abschnitt(d, root):
    """HTML-Abschnitt für die Themenseite: Bild, Stand je Strang, Liste und Aufrufe."""
    return f"""    <h2>Auf einen Blick</h2>
    <p class="meta">Wo steht das Verfahren, was ist entschieden, wo kann man sich einbringen? Lage der Punkte nach der letzten Beratung mit Ergebnis, sonst nach der nächsten (abgeleitet); Phasen geplant laut Terminplan 261064. Die Monate ab September 2026 sind breiter gezeichnet.</p>
    <div class="pb-rahmen pb-breit" tabindex="0" role="region" aria-label="Zeitleiste, waagerecht verschiebbar" data-start="{_x(d["heute"]) / W:.3f}">
      {svg(d)}
    </div>
{liste(d, root)}
{aufrufe(d, root)}
    <h3>Stand der Vorlagen je Strang</h3>
{stand_balken(d)}
    <script src="{root}thema.js" defer></script>"""
