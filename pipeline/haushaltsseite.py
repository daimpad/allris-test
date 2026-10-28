"""Seite haushalt/: Treemap der ordentlichen Aufwendungen je Produktbereich (Schritt 1, Entscheidung 28.10.2026).

Vorbild ist die Treemap der Berliner Haushaltsdaten (ODIS, github.com/berlin/haushaltsdaten). Ebene 1: die 17
Produktbereiche aus den geprüften Teilergebnisplänen (data/haushalt/produktbereiche.tsv, Zeile 17,
pipeline/haushaltsplan.py). Je Ansicht (Plan der beiden Haushaltsjahre, jüngstes Ist) eine Treemap als SVG, für breite
und schmale Bildschirme getrennt gelegt; der Wechsel braucht kein Skript (Auswahlknöpfe und CSS). Eine Tabelle unter der
Treemap nennt alle Werte mit Fundstelle. Nominal, ohne Wertung, ohne Finanzplanung ab 2027.

Ebenen 2 und 3 (haushalt/PHASE3.md, nur mit haushaltsplan.EBENEN_FREIGEGEBEN): Ein Klick auf einen Produktbereich führt
auf das Sprungziel #zoom-XX mit der Treemap seiner Produktgruppen, den Aufwandsarten des Produktbereichs als Balken und
einer Tabelle der Produktgruppen (data/haushalt/aufwandsarten.tsv, produktgruppen.tsv). Ein Klick auf eine
Produktgruppe führt auf #pg-1-XX-YY mit ihren Aufwandsarten als Balken und Tabelle. Auch das geht ohne Skript (:target);
alle Abschnitte liegen in .hh-karten, damit die Auswahlknöpfe überall wirken. Für die Browser-Prüfung vor der Freigabe
zeigt die Umgebungsvariable HAUSHALT_EBENEN=vorschau die Ebenen beim Erzeugen der Seite.

Mit Skript (site/haushalt.js, Entscheidung 28.10.2026) wächst die angeklickte Kachel auf die ganze Fläche und zeigt ihre
Unterteilung; Ebene 3 zeichnet es als Kacheln aus den Beträgen der Balken (data-b), damit die Seite klein bleibt.
Erklärungen stehen einmal im Akkordeon „So lesen Sie die Zahlen“, Grenzen und Quellen in zugeklappten Akkordeons.
"""
import json
import os
from collections import defaultdict
from html import escape

from . import haushaltsplan
from .dossier import _date, _mio
from .themenseiten import ALLE as THEMEN

PFAD = "haushalt/"
ZEILE = 17
NEUTRAL = ("#ece8f6", "#2e2a3d")   # Fläche und Schrift der Produktbereiche ohne Themenseite
FORMATE = {"breit": (1000, 560), "hoch": (340, 640)}   # hoch: etwa in Bildschirmgröße eines Telefons
# Aufwandsarten: feste, nominale Farben als Klassen hh-f11 … hh-f16 (Balken) und hh-z11 … hh-z16 (Tabelle) in page.css
HINWEIS = ("Aufwandsarten sind Kontenarten, keine Aufgaben: Sie zeigen, wofür das Geld der Art nach verbucht ist, etwa "
           "für Personal oder für Transfers. Bilanzielle Abschreibungen verteilen den Wertverlust von Gebäuden und "
           "Anlagen auf die Jahre; sie fließen nicht als Geld ab.")
BEGRIFFE = "Begriffe oben unter „So lesen Sie die Zahlen“."   # kein Link: ein Sprung verließe die Ebene (:target)


def _prozent(x):
    return f"{x:.1f}".replace(".", ",") + " %"


def _euro(x):
    return f"{x:,}".replace(",", ".").replace("-", "−") + " €"


def _betrag(x):
    """Wie _mio; Beträge unter 0,05 Mio. € in Euro, damit sie nicht als 0,0 Mio. € erscheinen."""
    return _euro(x) if abs(x) < 50_000 else _mio(x)


def ebenen_an():
    return haushaltsplan.EBENEN_FREIGEGEBEN or os.environ.get("HAUSHALT_EBENEN") == "vorschau"


def _anker(pg):
    return "pg-" + pg.replace(".", "-")


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


def _wert(x):
    return x and {"betrag": x[0], "ausgabe": x[1]["ausgabe"], "datei": x[1]["datei"], "seite": int(x[1]["seite"]),
                  "leer": x[1].get("leer") == "ja"}


def _ist_plan(reihe):
    return {"ist": {j: _wert(i) for j, i, _ in reihe if i}, "plan": {j: _wert(x) for j, _, x in reihe if x}}


def _arten(schluessel, rows, feld):
    return [{"zeile": nr, "name": name, **_ist_plan(haushaltsplan.reihe(schluessel, rows, nr, feld))}
            for nr, name in haushaltsplan.AUFWANDSARTEN.items()]


def daten(rows=None, aufwand=None, gruppen=None):
    """Produktbereiche mit Ist und Plan (Zeile 17), mit den Ebenen 2 und 3 auch Aufwandsarten und Produktgruppen, und
    die Ansichten: Plan der beiden jüngsten Haushaltsjahre und das jüngste Ist. None ohne Freigabe oder ohne Daten."""
    if not haushaltsplan.FREIGEGEBEN:
        return None
    rows = haushaltsplan.lesen() if rows is None else rows
    if not rows:
        return None
    an = ebenen_an()
    aufwand = (haushaltsplan.lesen(haushaltsplan.AUFWANDSARTEN_TSV) if an else []) if aufwand is None else aufwand
    gruppen = (haushaltsplan.lesen(haushaltsplan.PRODUKTGRUPPEN_TSV) if an else []) if gruppen is None else gruppen
    je_pg, namen = defaultdict(list), defaultdict(dict)
    for r in gruppen:
        je_pg[r["produktgruppe"]].append(r)
        namen[r["produktgruppe"]][r["ausgabe"]] = (r["name"], r["einheit"])
    neu = max((r["ausgabe"] for r in gruppen), default=None)
    themen = {t.produktbereich: t for t in THEMEN if t.produktbereich}
    pbs = []
    for pb, name in sorted({(r["produktbereich"], r["name"]) for r in rows}):
        t = themen.get(pb)
        p = {"pb": pb, "name": name, **_ist_plan(haushaltsplan.reihe(pb, rows, ZEILE)),
             **({"thema": {"titel": t.titel, "pfad": t.pfad, "farben": t.farben}} if t else {})}
        if aufwand and gruppen:
            p["aufwandsarten"] = _arten(pb, aufwand, "produktbereich")
            p["produktgruppen"] = []
            for pg in sorted(g for g in je_pg if g.startswith(f"1.{pb}.") and neu in namen[g]):
                n, einheit = namen[pg][neu]
                alt = sorted((a, v[0]) for a, v in namen[pg].items() if v[0] != n)   # andere Namen älterer Ausgaben
                p["produktgruppen"].append({"nr": pg, "name": n, "einheit": einheit, "alt": alt,
                                            **_ist_plan(haushaltsplan.reihe(pg, je_pg[pg], ZEILE, "produktgruppe")),
                                            "aufwandsarten": _arten(pg, je_pg[pg], "produktgruppe")})
        pbs.append(p)
    plan_jahre = sorted({j for p in pbs for j in p["plan"]})[-2:]
    ist_jahr = max(j for p in pbs for j in p["ist"])
    ansichten = [{"key": f"plan{j}", "art": "plan", "jahr": j, "titel": f"Plan {j}"} for j in reversed(plan_jahre)] \
        + [{"key": f"ist{ist_jahr}", "art": "ist", "jahr": ist_jahr, "titel": f"Ist {ist_jahr}"}]
    for a in ansichten:
        a["summe"] = sum(p[a["art"]][a["jahr"]]["betrag"] for p in pbs if a["jahr"] in p[a["art"]])
    stand = json.loads(haushaltsplan.STAND.read_text(encoding="utf-8"))
    return {"produktbereiche": pbs, "ansichten": ansichten, "abruf": stand["abruf"], "lizenz": stand["lizenz"],
            "zoom": bool(aufwand and gruppen),
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


def _text(x, y, rw, rh, name, marke, betrag):
    """Beschriftung einer Fläche (Klassen hh-n, hh-b, hh-m, hh-k in page.css): Name umbrochen mit Betrag; passt er
    nicht, Marke (Nummer) und Betrag oder nur die Marke; bei sehr kleinen Flächen nichts."""
    groesse = 15
    zeichen = int((rw - 12) / (0.62 * groesse))   # mittlere Zeichenbreite von Inter, halbfett
    platz = int((rh - 8) // (groesse * 1.2)) - 1   # eine Zeile bleibt für den Betrag
    zeilen = _zeilen(name, zeichen) if rw >= 70 else None
    if zeilen and len(zeilen) <= platz and len(betrag) <= zeichen + 2:
        return "".join(f'<text x="{x + 6:.0f}" y="{y + 6 + groesse * (1 + 1.2 * k):.0f}" class="hh-n">{escape(z)}</text>'
                       for k, z in enumerate(zeilen)) \
            + f'<text x="{x + 6:.0f}" y="{y + 6 + groesse * (1 + 1.2 * len(zeilen)):.0f}" class="hh-b">{escape(betrag)}</text>'
    if rw >= 0.6 * 13 * max(len(marke), len(betrag)) + 12 and rh >= 2.6 * 13:   # Name passt nicht
        return (f'<text x="{x + 5:.0f}" y="{y + 18:.0f}" class="hh-m">{escape(marke)}</text>'
                f'<text x="{x + 5:.0f}" y="{y + 5 + 13 * 2.2:.0f}" class="hh-k">{escape(betrag)}</text>')
    if rw >= max(30, 0.62 * 13 * len(marke) + 8) and rh >= groesse + 6:
        return f'<text x="{x + 4:.0f}" y="{y + 3 + groesse:.0f}" class="hh-m">{escape(marke)}</text>'
    return ""


def _svg_gruppen(flaechen, format_, label, fill, ink):
    """Treemap der Produktgruppen als SVG, knapp gehalten (viele Flächen): flaechen absteigend nach Betrag als
    (Betrag, Ziel, Beschreibung, Name, Marke, Betragstext). Alle Flächen tragen die Farbe des Produktbereichs (am SVG),
    die Schrift ihre Klasse (page.css); Koordinaten ganzzahlig, der weiße Rand deckt die Rundung. Jede Fläche ist ein
    Link mit Titel (Hinweis beim Überfahren, zugleich Name des Links); _text setzt nur Beschriftungen, die passen."""
    w, h = FORMATE[format_]
    teile = []
    for (b, ziel, beschreibung, name, marke, text), (x, y, rw, rh) in zip(flaechen, squarify([f[0] for f in flaechen], 0, 0, w, h)):
        teile.append(f'<a href="#{ziel}"><title>{escape(beschreibung)}</title>'
                     f'<rect x="{x:.0f}" y="{y:.0f}" width="{rw:.0f}" height="{rh:.0f}" rx="3"/>{_text(x, y, rw, rh, name, marke, text)}</a>')
    return (f'<svg class="hh-svg hh-{format_} hh-pgs{" hh-hell" if ink == "#ffffff" else ""}" viewBox="0 0 {w} {h}" '
            f'fill="{fill}" role="group" aria-label="{escape(label)}">' + "".join(teile) + "</svg>")


def _farben_pb(p):
    return (p["thema"]["farben"][0], "#ffffff") if p.get("thema") else NEUTRAL   # dunkle Themenfarbe: Kontrast


def treemap(d, ansicht, format_):
    """SVG einer Ansicht der Produktbereiche; jede Fläche verweist auf Ebene 2 oder (ohne Ebenen) auf die Zeile der
    Tabelle. Die Flächen der Themenseiten tragen deren Farbe."""
    a = ansicht
    items = sorted(((p, p[a["art"]][a["jahr"]]["betrag"]) for p in d["produktbereiche"] if a["jahr"] in p[a["art"]]),
                   key=lambda x: (-x[1], x[0]["pb"]))
    w, h = FORMATE[format_]
    teile = []
    for (p, b), (x, y, rw, rh) in zip(items, squarify([b for _, b in items], 0, 0, w, h)):
        fill, ink = _farben_pb(p)
        ziel = f'{"zoom" if d.get("zoom") else "pb"}-{p["pb"]}'
        label = f'{p["pb"]} {p["name"]}: {_mio(b)}, {_prozent(100 * b / a["summe"])} ({a["titel"]})'
        r = f'x="{x:.1f}" y="{y:.1f}" width="{rw:.1f}" height="{rh:.1f}"'
        clip = f"hh-{a['key']}-{format_}-{p['pb']}"
        teile.append(f'<a href="#{ziel}" aria-label="{escape(label)}"><title>{escape(label)}</title>'
                     f'<clipPath id="{clip}"><rect {r}/></clipPath><rect {r} fill="{fill}" rx="3"/>'
                     f'<g clip-path="url(#{clip})" fill="{ink}">{_text(x, y, rw, rh, p["name"], p["pb"], _mio(b))}</g></a>')
    return (f'<svg class="hh-svg hh-{format_}" viewBox="0 0 {w} {h}" role="group" '
            f'aria-label="{escape(a["titel"])}: ordentliche Aufwendungen je Produktbereich, zusammen {escape(_mio(a["summe"]))}">'
            + "".join(teile) + "</svg>")


def treemap_gruppen(p, ansicht, format_):
    """SVG der Produktgruppen eines Produktbereichs in einer Ansicht; Produktgruppen mit 0 € oder negativem Wert haben
    keine Fläche (nur in der Tabelle). Anteile an Zeile 17 des Produktbereichs."""
    a = ansicht
    gesamt = p[a["art"]].get(a["jahr"])
    if not gesamt:
        return ""
    items = sorted(((g, g[a["art"]][a["jahr"]]["betrag"]) for g in p["produktgruppen"]
                    if a["jahr"] in g[a["art"]] and g[a["art"]][a["jahr"]]["betrag"] > 0), key=lambda x: (-x[1], x[0]["nr"]))
    flaechen = [(b, _anker(g["nr"]), f'{g["nr"]} {g["name"]}: {_betrag(b)}, {_prozent(100 * b / gesamt["betrag"])} ({a["titel"]})',
                 g["name"], g["nr"], _betrag(b)) for g, b in items]
    return _svg_gruppen(flaechen, format_, f'{a["titel"]}: Produktgruppen im Produktbereich {p["pb"]} {p["name"]}, '
                                           f'zusammen {_mio(gesamt["betrag"])}', *_farben_pb(p))


def _balken(arten, ansichten, betraege=False):
    """Gestapelter Balken der Aufwandsarten je Ansicht (HTML, Breite anteilig an der Summe der positiven Werte). Die
    Tabelle darunter nennt dieselben Werte; der Balken ist für Vorleseprogramme ausgeblendet. Mit betraege trägt jedes
    Stück seinen Betrag (data-b), aus dem site/haushalt.js die Kacheln der Ebene 3 zeichnet."""
    out = []
    for k, a in enumerate(ansichten):
        werte = [(t["zeile"], t[a["art"]][a["jahr"]]["betrag"]) for t in arten if a["jahr"] in t[a["art"]]]
        positiv = sum(b for _, b in werte if b > 0)
        teile = "".join(f'<i class="hh-f{nr}" style="width:{100 * b / positiv:.1f}%"{f' data-b="{b}"' if betraege else ""}></i>'
                        for nr, b in werte
                        if positiv and 100 * b / positiv >= 0.05)   # unter 0,05 % unsichtbar
        out.append(f'<div class="hh-ansicht hh-v{k} hh-balken" aria-hidden="true">{teile}</div>')
    return "".join(out)


def _zelle(x):
    return f'{_mio(x["betrag"])}<br><small>Haushaltsplan {escape(x["ausgabe"])}, S. {x["seite"]}</small>' if x else "–"


def _zelle_art(x):
    if not x:
        return "–"
    if x["leer"]:
        return "leer"
    if x["betrag"] < 0:
        return f'{_euro(x["betrag"])}<br><small>negativ, ohne Fläche</small>'
    return _betrag(x["betrag"])


def _fundstelle(d, pb, werte, datei=False, ausgabe=None):
    """Links auf die Seiten im PDF; aus der Ausgabe `ausgabe` (im Spaltenkopf genannt) nur die Seite."""
    orte = sorted({(x["ausgabe"], x["datei"], x["seite"]) for x in werte if x})
    return "; ".join(f'<a href="{escape(d["ausgaben"][a]["dateien"][pb])}#page={s}">'
                     + (f"S. {s}" if a == ausgabe else f'Haushaltsplan {escape(a)}{", " + escape(f) if datei else ""}, S. {s}')
                     + "</a>" for a, f, s in orte)


def _negativ(name, spalten, werte):
    return [f'{escape(name)} im {titel} ({_euro(x["betrag"])})' for (_, _, titel), x in zip(spalten, werte) if x and x["betrag"] < 0]


def _mit_werten(g, ansichten):
    """Produktgruppe mit einem Betrag ungleich 0 in einer Ansicht (sonst ohne Ebene 3, nur in der Tabelle)."""
    return any(x.get(a["jahr"]) and x[a["jahr"]]["betrag"] for t in [g, *g["aufwandsarten"]] for a in ansichten
               for x in [t[a["art"]]])


def _pfad(*teile):
    """Brotkrumen: Links auf die übergeordneten Ebenen, die aktuelle Ebene als Text."""
    *links, aktuell = teile
    return ('<nav class="hh-pfad" aria-label="Ebenen des Haushalts">'
            + "".join(f'<a href="#{ziel}">{escape(text)}</a> › ' for ziel, text in links)
            + f'<span aria-current="location">{escape(aktuell)}</span></nav>')


def zoom(d, p):
    """Ebene 2, Abschnitt #zoom-XX: Treemap der Produktgruppen je Ansicht, Aufwandsarten des Produktbereichs als Balken
    und Tabelle, Tabelle der Produktgruppen mit Fundstelle."""
    pb, ansichten, neu = p["pb"], d["ansichten"], max(d["ausgaben"])
    ref = ansichten[0]
    spalten = [(a["art"], a["jahr"], a["titel"]) for a in reversed(ansichten)]
    kopf = "".join(f'<th scope="col">{escape(t)}</th>' for *_, t in spalten)
    karten = "".join(f'<figure class="hh-ansicht hh-v{k}">{treemap_gruppen(p, a, "breit")}{treemap_gruppen(p, a, "hoch")}</figure>'
                     for k, a in enumerate(ansichten))
    summe_ref = p["plan"].get(ref["jahr"])
    anteil = lambda x: _prozent(100 * x["betrag"] / summe_ref["betrag"]) if x and x["betrag"] > 0 and summe_ref else "–"
    zelle = lambda inhalt: f'<td>{inhalt}</td>'   # Spaltennamen auf dem Telefon über stil()
    summe = [p[art].get(j) for art, j, _ in spalten]
    summenzeile = ('<tr class="hh-summe"><th scope="row">Ordentliche Aufwendungen (Zeile 17)</th>'
                   + "".join(zelle(_mio(x["betrag"]) if x else "–") for x in summe)
                   + zelle("100,0 %"))
    # Aufwandsarten des Produktbereichs
    arten, negativ = [], []
    for t in p["aufwandsarten"]:
        werte = [t[art].get(j) for art, j, _ in spalten]
        negativ += _negativ(t["name"], spalten, werte)
        arten.append(f'<tr class="hh-z{t["zeile"]}"><th scope="row">{escape(t["name"])}</th>'
                     + "".join(zelle(_zelle_art(x)) for x in werte)
                     + zelle(anteil(t["plan"].get(ref["jahr"]))) + "</tr>")
    # Produktgruppen
    gruppen = []
    for g in p["produktgruppen"]:
        werte = [g[art].get(j) for art, j, _ in spalten]
        negativ += _negativ(f'{g["nr"]} {g["name"]}', spalten, werte)
        name = f'<a href="#{_anker(g["nr"])}">{escape(g["name"])}</a>' if _mit_werten(g, ansichten) else escape(g["name"])
        zusatz = "".join(f'<br><small>Name in Haushaltsplan {escape(a)}: {escape(n)}</small>' for a, n in g["alt"])
        gruppen.append(f'<tr><th scope="row">{escape(g["nr"])} {name}'
                       + (f'<br><small>{escape(g["einheit"])}</small>' if g["einheit"] else "") + zusatz + "</th>"
                       + "".join(zelle(_zelle_art(x)) for x in werte)
                       + zelle(anteil(g["plan"].get(ref["jahr"])))
                       + zelle(_fundstelle(d, pb, werte, ausgabe=neu)) + "</tr>")
    hinweise = [f'Negativ sind: {"; ".join(negativ)}.'] if negativ else []
    hinweise.append(BEGRIFFE)
    t_ = f"zoom-{pb}-t"
    return f"""        <section id="zoom-{pb}" class="hh-ebene" aria-labelledby="{t_}">
          {_pfad(("produktbereiche", "Alle Produktbereiche"), f'{pb} {p["name"]}')}
          <h2 id="{t_}">Produktbereich {escape(pb)} {escape(p["name"])}</h2>
          <p class="meta">Jede Fläche ist eine Produktgruppe; ein Klick zeigt ihre Aufwandsarten.</p>
          {karten}
          <h3>Aufwandsarten des Produktbereichs</h3>
          {_balken(p["aufwandsarten"], ansichten)}
          <table class="hh-tabelle hh-zoom-tabelle">
            <thead><tr><th scope="col">Aufwandsart</th>{kopf}<th scope="col">Anteil {escape(ref["titel"])}</th></tr></thead>
            <tbody>{"".join(arten)}{summenzeile}</tr></tbody>
          </table>
          <h3>Produktgruppen</h3>
          <table class="hh-tabelle hh-zoom-tabelle">
            <thead><tr><th scope="col">Produktgruppe</th>{kopf}<th scope="col">Anteil {escape(ref["titel"])}</th><th scope="col">Seite im Haushaltsplan {escape(neu)}</th></tr></thead>
            <tbody>{"".join(gruppen)}{summenzeile}{zelle(_fundstelle(d, pb, summe, ausgabe=neu))}</tr></tbody>
          </table>
          <p class="meta">{" ".join(hinweise)}</p>
        </section>"""


def gruppe(d, p, g):
    """Ebene 3, Abschnitt #pg-1-XX-YY: Aufwandsarten einer Produktgruppe als Balken je Ansicht und Tabelle; mit Skript
    zeichnet site/haushalt.js aus den Balken Kacheln (keine Treemap im HTML, damit die Seite klein bleibt)."""
    ansichten = d["ansichten"]
    spalten = [(a["art"], a["jahr"], a["titel"]) for a in reversed(ansichten)]
    zeilen, negativ, alle = [], [], []
    for t in g["aufwandsarten"]:
        werte = [t[art].get(j) for art, j, _ in spalten]
        negativ += _negativ(t["name"], spalten, werte)
        alle += werte
        zeilen.append(f'<tr class="hh-z{t["zeile"]}"><th scope="row">{escape(t["name"])}</th>'
                      + "".join(f"<td>{_zelle_art(x)}</td>" for x in werte) + "</tr>")
    summe = [g[art].get(j) for art, j, _ in spalten]
    zeilen.append('<tr class="hh-summe"><th scope="row">Ordentliche Aufwendungen (Zeile 17)</th>'
                  + "".join(f"<td>{_zelle_art(x)}</td>" for x in summe) + "</tr>")
    kopf = "".join(f'<th scope="col">{escape(t)}</th>' for *_, t in spalten)
    angaben = [escape(g["einheit"])] if g["einheit"] else []
    angaben += [f"Name in Haushaltsplan {escape(a)}: {escape(n)}" for a, n in g["alt"]]
    hinweis = f' Negativ sind: {"; ".join(negativ)}.' if negativ else ""
    t_ = f"{_anker(g['nr'])}-t"
    return f"""        <section id="{_anker(g["nr"])}" class="hh-ebene hh-pg" aria-labelledby="{t_}">
          {_pfad(("produktbereiche", "Alle Produktbereiche"), (f"zoom-{p['pb']}", f'{p["pb"]} {p["name"]}'), f'{g["nr"]} {g["name"]}')}
          <h2 id="{t_}">Produktgruppe {escape(g["nr"])} {escape(g["name"])}</h2>
          {f'<p class="meta">{" · ".join(angaben)}</p>' if angaben else ""}
          {_balken(g["aufwandsarten"], ansichten, betraege=True)}
          <table class="hh-tabelle hh-pg-tabelle"><thead><tr><th scope="col">Aufwandsart</th>{kopf}</tr></thead><tbody>{"".join(zeilen)}</tbody></table>
          <p class="meta">Fundstelle: {_fundstelle(d, p["pb"], alle + summe, datei=True)}.{hinweis}</p>
        </section>"""


def body(d, root):
    ansichten = d["ansichten"]
    wahl = "\n".join(
        f'      <input type="radio" name="hh-ansicht" id="hh-{a["key"]}" class="hh-radio"{" checked" if k == 0 else ""}>'
        f'<label for="hh-{a["key"]}">{escape(a["titel"])} <small>{escape(_mio(a["summe"]))}</small></label>'
        for k, a in enumerate(ansichten))
    karten = "\n".join(f'          <figure class="hh-ansicht hh-v{k}">{treemap(d, a, "breit")}{treemap(d, a, "hoch")}</figure>'
                       for k, a in enumerate(ansichten))
    ebenen = []
    if d.get("zoom"):
        for p in d["produktbereiche"]:
            ebenen.append(zoom(d, p))
            ebenen += [gruppe(d, p, g) for g in p["produktgruppen"] if _mit_werten(g, ansichten)]
    ref = ansichten[0]
    pbs = sorted(d["produktbereiche"], key=lambda p: (-(p["plan"].get(ref["jahr"]) or {"betrag": 0})["betrag"], p["pb"]))
    spalten = [(a["art"], a["jahr"], a["titel"]) for a in reversed(ansichten)]
    def zeile(p):
        thema = (f'<br><small>Themenseite <a href="{root}{p["thema"]["pfad"]}">{escape(p["thema"]["titel"])}</a></small>'
                 if p.get("thema") else "")
        tiefer = f'<br><small><a href="#zoom-{p["pb"]}">Produktgruppen und Aufwandsarten</a></small>' if d.get("zoom") else ""
        anteil = p["plan"].get(ref["jahr"])
        quelle = next((v["dateien"][p["pb"]] for a, v in sorted(d["ausgaben"].items(), reverse=True) if p["pb"] in v["dateien"]), None)
        name = f'<a href="{escape(quelle)}">{escape(p["name"])}</a>' if quelle else escape(p["name"])
        return (f'        <tr id="pb-{p["pb"]}"><th scope="row">{escape(p["pb"])} {name}{thema}{tiefer}</th>'
                + "".join(f"<td>{_zelle(p[art].get(j))}</td>" for art, j, _ in spalten)
                + f'<td>{_prozent(100 * anteil["betrag"] / ref["summe"]) if anteil else "–"}</td></tr>')
    kopf = "".join(f'<th scope="col">{escape(t)}</th>' for *_, t in spalten)
    summe = "".join(f"<td>{escape(_mio(a['summe']))}</td>" for a in reversed(ansichten))
    themen = ", ".join(f'<a href="{root}{p["thema"]["pfad"]}">{escape(p["thema"]["titel"])}</a> ({p["pb"]})'
                       for p in d["produktbereiche"] if p.get("thema"))
    dateien = ", ".join(f'<a href="{escape(v["seite"])}">Haushaltsplan {escape(a)}</a>' for a, v in sorted(d["ausgaben"].items()))
    if d.get("zoom"):
        klick = ("Ein Klick auf eine Fläche zeigt ihre Unterteilung: erst die Produktgruppen, dann die Aufwandsarten. "
                 "Die Flächen zeigen Anteile, keine Bewertung.")
        umfang = ("Die Seite zeigt drei Ebenen: Produktbereiche, Produktgruppen und je Bereich und Gruppe die sechs "
                  "Aufwandsarten. Produkte und Konten enthalten die Haushaltspläne nicht.")
        pruefung = (" Je Produktbereich und Spalte ergeben die Produktgruppen und die Aufwandsarten (Zeilen 11–16) die "
                    "ordentlichen Aufwendungen, ebenso je Produktgruppe; leere Zellen zählen als 0. Ein Prüfbogen mit 33 "
                    "Zellen wurde mit einem zweiten Leseweg gegengeprüft (KI-gestützt, 33 von 33 gleich) und vor der "
                    "Veröffentlichung freigegeben.")
        begriffe = f"""
        <dt>Ebenen</dt><dd>Produktbereich, Produktgruppe, Aufwandsart. Die Produktgruppen eines Bereichs ergeben zusammen seine ordentlichen Aufwendungen, ebenso seine sechs Aufwandsarten.</dd>
        <dt>Aufwandsarten</dt><dd>{HINWEIS}</dd>
        <dt>„leer“ und 0 €</dt><dd>Eine leere Zelle im Haushaltsplan zählt als 0 €. Produktgruppen mit 0 € in einer Ansicht haben keine Fläche und stehen nur in der Tabelle.</dd>
        <dt>Negative Werte</dt><dd>Sie kommen nur im Ist vor und haben keine Fläche; die übrigen Flächen zeigen dann zusammen etwas mehr als die Summe.</dd>"""
    else:
        klick = "Ein Klick auf eine Fläche führt zur Zeile in der Tabelle. Die Flächen zeigen Anteile, keine Bewertung."
        umfang = "Die Seite zeigt eine Ebene, die 17 Produktbereiche. Produktgruppen, Produkte und Konten stehen in den Haushaltsplänen."
        pruefung = begriffe = ""
    return f"""    <h1>Haushalt auf einen Blick</h1>
    <p class="lead">Wofür plant die Stadt Bonn Geld ein? Jede Fläche ist ein Produktbereich des Haushalts; je größer die Fläche, desto höher die ordentlichen Aufwendungen.</p>
    <details class="hh-mehr" id="lesen">
      <summary>So lesen Sie die Zahlen</summary>
      <dl>
        <dt>Betrag</dt><dd>Ordentliche Aufwendungen (Zeile 17 der Teilergebnispläne), nominal in Mio. €, ohne Investitionen.</dd>
        <dt>Plan und Ist</dt><dd>Plan ist der Ansatz des Haushaltsjahres, Ist das Ergebnis laut Haushaltsplan; beide weichen oft voneinander ab.</dd>{begriffe}
        <dt>Farben</dt><dd>Farbig sind die Produktbereiche mit eigener Themenseite: {themen}.</dd>
      </dl>
    </details>
    <div class="hh-wahl" id="produktbereiche">
      <p class="hh-wahl-titel" id="hh-wahl-titel">Ansicht:</p>
{wahl}
      <div class="hh-karten">
        <div class="hh-haupt">
{karten}
          <p class="meta">{klick}</p>
        </div>
{chr(10).join(ebenen)}
      </div>
    </div>
    <h2 id="tabelle">Alle Produktbereiche</h2>
    <p>Sortiert nach dem {escape(ref["titel"])}; der Name führt zum Teilergebnisplan (PDF).</p>
    <table class="hh-tabelle">
      <thead><tr><th scope="col">Produktbereich</th>{kopf}<th scope="col">Anteil {escape(ref["titel"])}</th></tr></thead>
      <tbody>
{chr(10).join(zeile(p) for p in pbs)}
        <tr class="hh-summe"><th scope="row">Zusammen</th>{summe}<td>100,0 %</td></tr>
      </tbody>
    </table>
    <details class="hh-mehr">
      <summary>Was diese Seite nicht zeigt</summary>
      <ul>
        <li><strong>Einzelne Posten:</strong> {umfang}</li>
        <li><strong>Erträge und Investitionen:</strong> Die Flächen zeigen nur Aufwendungen, keine Erträge (Zeile 10). Investitionen stehen getrennt in den Teilfinanzplänen.</li>
        <li><strong>Ausgegliederte Bereiche:</strong> Eigenbetriebe und das Städtische Gebäudemanagement haben eigene Wirtschaftspläne. Interne Leistungen, Umgliederungen und der globale Minderaufwand verschieben Summen zwischen den Bereichen.</li>
        <li><strong>Künftige Jahre:</strong> Die Finanzplanung ab 2027 ist nicht übernommen. Der Entwurf des Haushalts 2027/2028 ist noch nicht eingebracht.</li>
        <li><strong>Vorlagen:</strong> Einzelnen Vorlagen ordnet die Seite keine Beträge zu.</li>
      </ul>
    </details>
    <details class="hh-mehr">
      <summary>Quellen, Prüfung und Lizenz</summary>
      <p>Stadt Bonn, {dateien} (PDF, Teilergebnispläne je Produktbereich; Abruf {_date(d["abruf"])}).</p>
      <p>Ausgelesen mit pipeline/haushaltsplan.py; die Summe aller Produktbereiche trifft je Spalte den Gesamtergebnisplan.{pruefung}</p>
      <p>Lizenz: {escape(d["lizenz"])}.</p>
      <p>Gestaltung nach dem Vorbild der <a href="https://haushaltsdaten.odis-berlin.de/visualisierung/">Berliner Haushaltsdaten</a> (ODIS, Technologiestiftung Berlin).</p>
    </details>
    <p><a href="{root}thema/">Alle Themenseiten</a> · <a href="{root}">Zur Karte</a></p>"""


def stil(d):
    """Spaltennamen der Tabellen der Ebenen 2 und 3 auf dem Telefon, wo die Tabellen zu Listen werden; die Jahre kommen aus den
    Daten, daher als Stilblock der Seite statt als Attribut an jeder Zelle. Dazu das Skript für Zoom und Kacheln."""
    if not d.get("zoom"):
        return ""
    titel = [a["titel"] for a in reversed(d["ansichten"])] + [f'Anteil {d["ansichten"][0]["titel"]}', "Fundstelle"]
    regeln = " ".join(f'.page table:is(.hh-zoom-tabelle, .hh-pg-tabelle) td:nth-of-type({k})::before {{ content: "{t}: "; }}'
                      for k, t in enumerate(titel, 1))
    return (f"\n  <style>@media (max-width: 600px) {{ {regeln} }}</style>"
            f'\n  <script src="../haushalt.js" defer></script>')


def write(site, site_url, page):
    """Schreibt haushalt/index.html; gibt den Pfad für die Sitemap zurück (ohne Daten keinen)."""
    d = daten()
    if not d:
        return []
    out = site / PFAD / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page(site_url, PFAD, "Haushalt auf einen Blick – RIS-Karte Bonn",
                        "Ordentliche Aufwendungen der Stadt Bonn je Produktbereich als Treemap: Plan und Ist aus den "
                        "Haushaltsplänen, mit Fundstelle.", body(d, "../"), "../", stil(d)), encoding="utf-8")
    return [PFAD]
