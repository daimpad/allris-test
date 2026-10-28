"""Seite haushalt/: Treemap der ordentlichen Aufwendungen je Produktbereich (Schritt 1, Entscheidung 28.10.2026).

Vorbild ist die Treemap der Berliner Haushaltsdaten (ODIS, github.com/berlin/haushaltsdaten). Hier gibt es eine Ebene:
die 17 Produktbereiche aus den geprüften Teilergebnisplänen (data/haushalt/produktbereiche.tsv, Zeile 17,
pipeline/haushaltsplan.py). Je Ansicht (Plan der beiden Haushaltsjahre, jüngstes Ist) eine Treemap als SVG, für breite
und schmale Bildschirme getrennt gelegt; der Wechsel braucht kein Skript (Auswahlknöpfe und CSS). Eine Tabelle unter der
Treemap nennt alle Werte mit Fundstelle. Nominal, ohne Wertung, ohne Finanzplanung ab 2027.
"""
import json
from html import escape

from . import haushaltsplan
from .dossier import _date, _mio
from .themenseiten import ALLE as THEMEN

PFAD = "haushalt/"
ZEILE = 17
NEUTRAL = ("#ece8f6", "#2e2a3d")   # Fläche und Schrift der Produktbereiche ohne Themenseite
FORMATE = {"breit": (1000, 560), "hoch": (340, 640)}   # hoch: etwa in Bildschirmgröße eines Telefons


def _prozent(x):
    return f"{x:.1f}".replace(".", ",") + " %"


def squarify(werte, x, y, w, h):
    """Squarified Treemap (Bruls, Huizing, van Wijk 2000): [(x, y, w, h)] in der Reihenfolge der Werte, die absteigend
    sortiert sein müssen. Die Flächen sind proportional zu den Werten und füllen das Rechteck."""
    gesamt = sum(werte)
    if not werte or gesamt <= 0:
        return []
    flaechen = [v * w * h / gesamt for v in werte]
    out = []

    def schlechteste(reihe, seite):
        s = sum(reihe)
        return max(max(seite * seite * r / (s * s), s * s / (seite * seite * r)) for r in reihe)

    i = 0
    while i < len(flaechen):
        seite = min(w, h)
        reihe = [flaechen[i]]
        j = i + 1
        while j < len(flaechen) and schlechteste(reihe + [flaechen[j]], seite) <= schlechteste(reihe, seite):
            reihe.append(flaechen[j])
            j += 1
        s = sum(reihe)
        if w >= h:   # Spalte am linken Rand
            breite, yy = s / h, y
            for r in reihe:
                out.append((x, yy, breite, r / breite))
                yy += r / breite
            x, w = x + breite, w - breite
        else:        # Zeile am oberen Rand
            hoehe, xx = s / w, x
            for r in reihe:
                out.append((xx, y, r / hoehe, hoehe))
                xx += r / hoehe
            y, h = y + hoehe, h - hoehe
        i = j
    return out


def daten(rows=None):
    """Produktbereiche mit Ist und Plan (Zeile 17) und die Ansichten: Plan der beiden jüngsten Haushaltsjahre und das
    jüngste Ist. None ohne Freigabe oder ohne Daten."""
    if not haushaltsplan.FREIGEGEBEN:
        return None
    rows = haushaltsplan.lesen() if rows is None else rows
    if not rows:
        return None
    themen = {t.produktbereich: t for t in THEMEN if t.produktbereich}
    pbs = []
    for pb, name in sorted({(r["produktbereich"], r["name"]) for r in rows}):
        reihe = haushaltsplan.reihe(pb, rows, ZEILE)
        wert = lambda x: x and {"betrag": x[0], "ausgabe": x[1]["ausgabe"], "datei": x[1]["datei"], "seite": int(x[1]["seite"])}
        t = themen.get(pb)
        pbs.append({"pb": pb, "name": name, "ist": {j: wert(i) for j, i, _ in reihe if i},
                    "plan": {j: wert(p) for j, _, p in reihe if p},
                    **({"thema": {"titel": t.titel, "pfad": t.pfad, "farben": t.farben}} if t else {})})
    plan_jahre = sorted({j for p in pbs for j in p["plan"]})[-2:]
    ist_jahr = max(j for p in pbs for j in p["ist"])
    ansichten = [{"key": f"plan{j}", "art": "plan", "jahr": j, "titel": f"Plan {j}"} for j in reversed(plan_jahre)] \
        + [{"key": f"ist{ist_jahr}", "art": "ist", "jahr": ist_jahr, "titel": f"Ist {ist_jahr}"}]
    for a in ansichten:
        a["summe"] = sum(p[a["art"]][a["jahr"]]["betrag"] for p in pbs if a["jahr"] in p[a["art"]])
    stand = json.loads(haushaltsplan.STAND.read_text(encoding="utf-8"))
    return {"produktbereiche": pbs, "ansichten": ansichten, "abruf": stand["abruf"], "lizenz": stand["lizenz"],
            "ausgaben": {a: {"seite": v["seite"], "dateien": {k: d["url"] for k, d in v["dateien"].items()}}
                         for a, v in stand["ausgaben"].items()}}


def _zeilen(text, max_zeichen):
    """Bricht einen Namen an Leerzeichen in Zeilen von höchstens max_zeichen Zeichen; None, wenn ein Wort nicht passt."""
    zeilen = []
    for wort in text.split():
        if len(wort) > max_zeichen:
            return None
        if zeilen and len(zeilen[-1]) + 1 + len(wort) <= max_zeichen:
            zeilen[-1] += " " + wort
        else:
            zeilen.append(wort)
    return zeilen


def treemap(d, ansicht, format_):
    """SVG einer Ansicht; jede Fläche verweist auf die Zeile der Tabelle."""
    w, h = FORMATE[format_]
    a = ansicht
    items = sorted(((p, p[a["art"]][a["jahr"]]["betrag"]) for p in d["produktbereiche"] if a["jahr"] in p[a["art"]]),
                   key=lambda x: (-x[1], x[0]["pb"]))
    rects = squarify([b for _, b in items], 0, 0, w, h)
    teile = []
    for (p, b), (x, y, rw, rh) in zip(items, rects):
        anteil = 100 * b / a["summe"]
        fill, ink = (p["thema"]["farben"][0], "#ffffff") if p.get("thema") else NEUTRAL   # dunkle Themenfarbe: Kontrast
        label = f'{p["pb"]} {p["name"]}: {_mio(b)}, {_prozent(anteil)} ({a["titel"]})'
        text = []
        groesse = 15
        zeichen = int((rw - 12) / (0.62 * groesse))   # mittlere Zeichenbreite von Inter, halbfett
        zeilen = _zeilen(p["name"], zeichen) if rw >= 70 else None
        platz = int((rh - 8) // (groesse * 1.2)) - 1   # eine Zeile bleibt für den Betrag
        if zeilen and len(zeilen) <= platz and len(_mio(b)) <= zeichen + 2:
            for k, z in enumerate(zeilen):
                text.append(f'<text x="{x + 6:.1f}" y="{y + 6 + groesse * (1 + 1.2 * k):.1f}" font-size="{groesse}" '
                            f'font-weight="600" fill="{ink}">{escape(z)}</text>')
            text.append(f'<text x="{x + 6:.1f}" y="{y + 6 + groesse * (1 + 1.2 * len(zeilen)):.1f}" font-size="{groesse - 1}" '
                        f'fill="{ink}">{escape(_mio(b))}</text>')
        elif rw >= 0.6 * 13 * len(_mio(b)) + 12 and rh >= 2.6 * 13:   # Name passt nicht: Nummer und Betrag
            text.append(f'<text x="{x + 5:.1f}" y="{y + 5 + 13:.1f}" font-size="13" font-weight="600" fill="{ink}">{escape(p["pb"])}</text>'
                        f'<text x="{x + 5:.1f}" y="{y + 5 + 13 * 2.2:.1f}" font-size="13" fill="{ink}">{escape(_mio(b))}</text>')
        elif rw >= 30 and rh >= groesse + 6:
            text.append(f'<text x="{x + 4:.1f}" y="{y + 3 + groesse:.1f}" font-size="{groesse - 2}" font-weight="600" '
                        f'fill="{ink}">{escape(p["pb"])}</text>')
        clip = f"hh-{a['key']}-{format_}-{p['pb']}"   # Text bleibt in seiner Fläche
        teile.append(f'<a href="#pb-{p["pb"]}" aria-label="{escape(label)}"><title>{escape(label)}</title>'
                     f'<clipPath id="{clip}"><rect x="{x:.1f}" y="{y:.1f}" width="{rw:.1f}" height="{rh:.1f}"/></clipPath>'
                     f'<rect x="{x:.1f}" y="{y:.1f}" width="{rw:.1f}" height="{rh:.1f}" fill="{fill}" stroke="#ffffff" '
                     f'stroke-width="2" rx="3"/><g clip-path="url(#{clip})">{"".join(text)}</g></a>')
    return (f'<svg class="hh-svg hh-{format_}" viewBox="0 0 {w} {h}" role="group" '
            f'aria-label="{escape(a["titel"])}: ordentliche Aufwendungen je Produktbereich, zusammen {escape(_mio(a["summe"]))}">'
            + "".join(teile) + "</svg>")


def _zelle(x):
    return f'{_mio(x["betrag"])}<br><small>Haushaltsplan {escape(x["ausgabe"])}, S. {x["seite"]}</small>' if x else "–"


def body(d, root):
    ansichten = d["ansichten"]
    wahl = "\n".join(
        f'      <input type="radio" name="hh-ansicht" id="hh-{a["key"]}" class="hh-radio"{" checked" if k == 0 else ""}>'
        f'<label for="hh-{a["key"]}">{escape(a["titel"])} <small>{escape(_mio(a["summe"]))}</small></label>'
        for k, a in enumerate(ansichten))
    karten = "\n".join(f'      <figure class="hh-ansicht hh-v{k}">{treemap(d, a, "breit")}{treemap(d, a, "hoch")}</figure>'
                       for k, a in enumerate(ansichten))
    ref = ansichten[0]
    pbs = sorted(d["produktbereiche"], key=lambda p: (-(p["plan"].get(ref["jahr"]) or {"betrag": 0})["betrag"], p["pb"]))
    spalten = [(a["art"], a["jahr"], a["titel"]) for a in reversed(ansichten)]
    def zeile(p):
        thema = (f'<br><small>Themenseite <a href="{root}{p["thema"]["pfad"]}">{escape(p["thema"]["titel"])}</a></small>'
                 if p.get("thema") else "")
        anteil = p["plan"].get(ref["jahr"])
        quelle = next((v["dateien"][p["pb"]] for a, v in sorted(d["ausgaben"].items(), reverse=True) if p["pb"] in v["dateien"]), None)
        name = f'<a href="{escape(quelle)}">{escape(p["name"])}</a>' if quelle else escape(p["name"])
        return (f'        <tr id="pb-{p["pb"]}"><th scope="row">{escape(p["pb"])} {name}{thema}</th>'
                + "".join(f"<td>{_zelle(p[art].get(j))}</td>" for art, j, _ in spalten)
                + f'<td>{_prozent(100 * anteil["betrag"] / ref["summe"]) if anteil else "–"}</td></tr>')
    kopf = "".join(f'<th scope="col">{escape(t)}</th>' for *_, t in spalten)
    summe = "".join(f"<td>{escape(_mio(a['summe']))}</td>" for a in reversed(ansichten))
    themen = ", ".join(f'<a href="{root}{p["thema"]["pfad"]}">{escape(p["thema"]["titel"])}</a> ({p["pb"]})'
                       for p in d["produktbereiche"] if p.get("thema"))
    dateien = ", ".join(f'<a href="{escape(v["seite"])}">Haushaltsplan {escape(a)}</a>' for a, v in sorted(d["ausgaben"].items()))
    return f"""    <h1>Haushalt auf einen Blick</h1>
    <p class="lead">Wofür plant die Stadt Bonn Geld ein? Jede Fläche ist ein Produktbereich des Haushalts; je größer die Fläche, desto höher die ordentlichen Aufwendungen.</p>
    <p class="meta">Ordentliche Aufwendungen (Zeile 17 der Teilergebnispläne), nominal in Mio. €. Plan heißt Ansatz des Haushaltsjahres, Ist heißt Ergebnis laut Haushaltsplan; beide weichen oft voneinander ab. Die Seite bewertet keine Beträge. Farbig sind die Produktbereiche mit eigener Themenseite: {themen}.</p>
    <div class="hh-wahl">
      <p class="hh-wahl-titel" id="hh-wahl-titel">Ansicht:</p>
{wahl}
      <div class="hh-karten">
{karten}
      </div>
    </div>
    <p class="meta">Ein Klick auf eine Fläche führt zur Zeile in der Tabelle. Die Flächen zeigen nur den Anteil am Haushalt, nicht, ob ein Betrag hoch oder niedrig ist.</p>
    <h2 id="tabelle">Alle Produktbereiche</h2>
    <p>Sortiert nach dem {escape(ref["titel"])}. Der Name führt zum Teilergebnisplan (PDF); die Fundstelle steht unter jedem Betrag.</p>
    <table class="hh-tabelle">
      <thead><tr><th scope="col">Produktbereich</th>{kopf}<th scope="col">Anteil {escape(ref["titel"])}</th></tr></thead>
      <tbody>
{chr(10).join(zeile(p) for p in pbs)}
        <tr class="hh-summe"><th scope="row">Zusammen</th>{summe}<td>100,0 %</td></tr>
      </tbody>
    </table>
    <h2>Was diese Seite nicht zeigt</h2>
    <ul>
      <li><strong>Einzelne Posten:</strong> Die Seite zeigt eine Ebene, die 17 Produktbereiche. Produktgruppen, Produkte und Konten stehen in den Haushaltsplänen.</li>
      <li><strong>Erträge und Investitionen:</strong> Die Flächen zeigen nur Aufwendungen, keine Erträge (Zeile 10). Investitionen stehen getrennt in den Teilfinanzplänen.</li>
      <li><strong>Ausgegliederte Bereiche:</strong> Eigenbetriebe und das Städtische Gebäudemanagement haben eigene Wirtschaftspläne. Interne Leistungen, Umgliederungen und der globale Minderaufwand verschieben Summen zwischen den Bereichen.</li>
      <li><strong>Künftige Jahre:</strong> Die Finanzplanung ab 2027 ist nicht übernommen. Der Entwurf des Haushalts 2027/2028 ist noch nicht eingebracht.</li>
      <li><strong>Vorlagen:</strong> Einzelnen Vorlagen ordnet die Seite keine Beträge zu.</li>
    </ul>
    <p class="meta">Quelle: Stadt Bonn, {dateien} (PDF, Teilergebnispläne je Produktbereich; Abruf {_date(d["abruf"])}); ausgelesen mit pipeline/haushaltsplan.py, die Summe aller Produktbereiche trifft je Spalte den Gesamtergebnisplan. Lizenz: {escape(d["lizenz"])}. Gestaltung nach dem Vorbild der <a href="https://haushaltsdaten.odis-berlin.de/visualisierung/">Berliner Haushaltsdaten</a> (ODIS, Technologiestiftung Berlin).</p>
    <p><a href="{root}thema/">Alle Themenseiten</a> · <a href="{root}">Zur Karte</a></p>"""


def write(site, site_url, page):
    """Schreibt haushalt/index.html; gibt den Pfad für die Sitemap zurück (ohne Daten keinen)."""
    d = daten()
    if not d:
        return []
    out = site / PFAD / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page(site_url, PFAD, "Haushalt auf einen Blick – RIS-Karte Bonn",
                        "Ordentliche Aufwendungen der Stadt Bonn je Produktbereich als Treemap: Plan und Ist aus den "
                        "Haushaltsplänen, mit Fundstelle.", body(d, "../"), "../"), encoding="utf-8")
    return [PFAD]
