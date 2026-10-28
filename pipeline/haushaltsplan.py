"""Beträge je Produktbereich aus den Haushaltsplänen der Stadt Bonn (PDF), für die Themenseiten.

Phase 0 (haushalt/phase0/BERICHT.md): Offene Tabellen gibt es nur bis zum Entwurf 2021/22; die Haushaltspläne
2023/24 und 2025/26 liegen auf bonn.de als PDF je Produktbereich mit Textebene. Entscheidung 27.10.2026: Beträge aus
den PDFs, je Themenseite ein Produktbereich, Ist und Plan getrennt, ohne Finanzplanung ab 2027.

Einmaliger Schritt `haushalt-ausschnitt` (lokal, braucht pdftotext aus poppler-utils): lädt je Ausgabe die 17
Teilergebnispläne der Produktbereiche und den Gesamtergebnisplan, liest die Zeilen 10 (ordentliche Erträge),
17 (ordentliche Aufwendungen) und 18 (ordentliches Ergebnis) mit den Spalten des Tabellenkopfs und prüft je Spalte,
dass die Summe der Produktbereiche den Gesamtergebnisplan trifft. Ergebnis: data/haushalt/produktbereiche.tsv mit
Fundstelle (Datei, Seite) und data/haushalt/STAND.json. Die PDFs selbst kommen nicht ins Repository.

Ebenen 2 und 3 (haushalt/phase0/EBENE2.md, Entscheidung 28.10.2026): einmaliger Schritt `haushalt-ebenen` liest aus
denselben PDF die Aufwandsarten (Zeilen 11–16) der 17 Produktbereiche und die Teilergebnispläne der Produktgruppen
(Zeilen 11–17) über die Wortkoordinaten (pdftotext -bbox), weil teilweise gefüllte Zeilen das Lesen der Reihe nach
brechen. Leere Zellen zählen als 0. Prüfsummen je Spalte: Aufwandsarten = Zeile 17 (Produktbereich und Produktgruppe),
Summe der Produktgruppen = Zeile 17 des Produktbereichs aus produktbereiche.tsv. Ergebnis: data/haushalt/aufwandsarten.tsv
und produktgruppen.tsv, Vermerk in STAND.json. Aus dem Kopf der Produktgruppe werden nur Nummer, Name und
Organisationseinheit übernommen, nicht die verantwortliche Person.

Lizenz: Die Seiten der Stadt nennen keine Lizenz. Der Haushaltsplan ist Teil der Haushaltssatzung; als amtliches Werk
(§ 5 UrhG) dürfte er frei sein – eine Einschätzung, keine gesicherte Auskunft. Quelle und Stand werden genannt."""
import csv
import hashlib
import html
import json
import re
import subprocess
import tempfile
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from . import config

BASIS = "https://www.bonn.de/medien-global/amt-20-und-21/haushaltsdaten/"
AUSGABEN = {
    "2023/2024": {"seite": "https://www.bonn.de/service-bieten/aktuelles-zahlen-fakten/haushaltsplan-2023-2024.php",
                  "gesamt": BASIS + "haushaltsplan-2023-24/gepp.pdf",
                  "pb": BASIS + "haushaltsplan-2023-24/produktbereiche/pb{:02d}.pdf"},
    "2025/2026": {"seite": "https://www.bonn.de/service-bieten/aktuelles-zahlen-fakten/haushaltsplan-2025-2026.php",
                  "gesamt": BASIS + "haushaltsplan-2025-2026/gepp.pdf",
                  "pb": BASIS + "haushaltsplan-2025-2026/produktbereiche/PB{:02d}.pdf"},
}
ZEILEN = {10: "Ordentliche Erträge", 17: "Ordentliche Aufwendungen", 18: "Ordentliches Ergebnis"}
ORDNER = config.ROOT / "data" / "haushalt"
TSV = ORDNER / "produktbereiche.tsv"
STAND = ORDNER / "STAND.json"
KOPF = ["ausgabe", "produktbereich", "name", "zeile", "zeile_name", "jahr", "art", "betrag", "datei", "seite"]
TOLERANZ = 1_500   # Euro je Spalte (Rundung in den Teilplänen)
AB_JAHR = 2022     # Themenseiten: Ist ab 2022 und Plan 2023–2026 (Entscheidung 27.10.2026; die Datei enthält mehr)
FREIGEGEBEN = True    # Prüfbogen im Gespräch vorgelegt und freigegeben am 27.10.2026 (haushalt/PHASE1.md)
PRUEFBOGEN = config.EXPORT / "haushalt" / "pruefbogen_haushalt.tsv"
# Ebenen 2 und 3: Aufwandsarten und Produktgruppen, Namen wie in den Teilergebnisplänen
AUFWANDSARTEN = {11: "Personalaufwendungen", 12: "Versorgungsaufwendungen",
                 13: "Aufwendungen für Sach- und Dienstleistungen", 14: "Bilanzielle Abschreibungen",
                 15: "Transferaufwendungen", 16: "Sonstige ordentliche Aufwendungen"}
AUFWANDSARTEN_TSV = ORDNER / "aufwandsarten.tsv"
AUFWANDSARTEN_KOPF = KOPF + ["leer"]
PRODUKTGRUPPEN_TSV = ORDNER / "produktgruppen.tsv"
PRODUKTGRUPPEN_KOPF = ["ausgabe", "produktbereich", "produktgruppe", "name", "einheit", "zeile", "zeile_name", "jahr",
                       "art", "betrag", "datei", "seite", "leer"]
EBENEN_FREIGEGEBEN = False   # Ebenen 2 und 3 erst nach Prüfung des Prüfbogens im Gespräch (haushalt/PHASE3.md)
EBENEN_PRUEFBOGEN = config.EXPORT / "haushalt" / "pruefbogen_haushalt_ebenen.tsv"
SPALTE_PT = 4   # pt: größter Abstand des rechten Rands einer Zahl von der Lage, die ihre Spalte erwarten lässt
WORT = re.compile(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>')


def _laden(url):
    req = urllib.request.Request(url, headers={"User-Agent": config.USER_AGENT})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def _text(pdf, seiten=3):
    """Seiten 1–n als Text mit Layout (pdftotext); gibt Liste der Seitentexte zurück."""
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "x.pdf"
        p.write_bytes(pdf)
        out = subprocess.run(["pdftotext", "-layout", "-f", "1", "-l", str(seiten), str(p), "-"],
                             capture_output=True, check=True, text=True).stdout
    return out.split("\f")


ZAHL = re.compile(r"-?\d{1,3}(?:\.\d{3})*")


def spalten(seite):
    """Spalten des Tabellenkopfs: [(Art, Jahr)], z. B. („Ergebnis“, 2022), („Ansatz“, 2025), („Planung“, 2027)."""
    # ohne die erste Zeile („Haushaltsplan 2025/2026“) und ohne die Tabellenzeilen ab Zeile 1
    kopf = re.split(r"^\s*1\s+\S", seite.split("\n", 1)[-1], maxsplit=1, flags=re.M)[0]
    arten = re.findall(r"\b(Ergebnis|Ansatz|Planung)\b", kopf)
    # Spalten sind chronologisch; die Jahreszahlen stehen im Kopf teils in verschobenen Zeilen (Gesamtplan)
    jahre = sorted({int(j) for j in re.findall(r"\b(20[1-3]\d)\b", kopf)})
    if len(arten) != len(jahre) or len(arten) < 5:
        raise ValueError(f"Tabellenkopf nicht erkannt: {arten} {jahre}")
    return list(zip(arten, jahre))


def zeile(seite, nr, n):
    """Beträge einer Zeile (n Spalten) aus der Zeile mit ihrer Nummer; bei zweizeiliger Bezeichnung stehen die Werte
    in der Zeile mit der Nummer. Bricht ab, wenn die Zahl der Werte nicht passt (leere Zellen)."""
    m = re.search(rf"^\s*{nr}\s+[=+\-/]+\s*(.*)$", seite, re.M)
    if not m:
        return None
    werte = [int(x.replace(".", "")) for x in ZAHL.findall(m.group(1))]
    if not werte:
        return None
    if len(werte) != n:
        raise ValueError(f"Zeile {nr}: {len(werte)} statt {n} Werte")
    return werte


def auslesen(pdf):
    """(Name des Produktbereichs, Spalten, {Zeile: Werte}, Seite) aus einem Teilergebnisplan."""
    for i, seite in enumerate(_text(pdf), 1):
        if "ergebnisplan" not in seite.lower():
            continue
        cols = spalten(seite)
        m = re.search(r"(?:Produktbereich|Gesamtergebnisplan)\s*\n.*?(\d\.\d{2})\s+([^\n]+)", seite)
        name = m.group(2).strip() if m else ""
        werte = {nr: zeile(seite, nr, len(cols)) for nr in ZEILEN}
        if werte[17] is not None:
            return name, cols, werte, i
    raise ValueError("keine Seite mit Zeile 17 gefunden")


def ausschnitt():
    """Pipeline-Schritt `haushalt-ausschnitt` (einmalig): data/haushalt/produktbereiche.tsv und STAND.json."""
    ORDNER.mkdir(parents=True, exist_ok=True)
    rows, stand = [], {"abruf": datetime.now(timezone.utc).date().isoformat(), "ausgaben": {}}
    for ausgabe, q in AUSGABEN.items():
        gesamt_pdf = _laden(q["gesamt"])
        _, gcols, gwerte, _ = auslesen(gesamt_pdf)
        summe = {nr: [0] * len(gcols) for nr in ZEILEN}
        dateien = {"gesamt": {"url": q["gesamt"], "sha256": hashlib.sha256(gesamt_pdf).hexdigest()}}
        for pb in range(1, 18):
            url = q["pb"].format(pb)
            pdf = _laden(url)
            name, cols, werte, seite = auslesen(pdf)
            if cols != gcols:
                raise ValueError(f"{ausgabe} PB {pb:02d}: Spalten {cols} weichen vom Gesamtplan ab")
            dateien[f"{pb:02d}"] = {"url": url, "sha256": hashlib.sha256(pdf).hexdigest(), "name": name}
            for nr, ws in werte.items():
                for k, w in enumerate(ws or [0] * len(cols)):
                    summe[nr][k] += w
                    if ws is None:
                        continue
                    art, jahr = cols[k]
                    if art == "Planung":   # Finanzplanung ab dem dritten Jahr: nicht übernommen (Entscheidung 27.10.2026)
                        continue
                    rows.append([ausgabe, f"{pb:02d}", name, nr, ZEILEN[nr], jahr, art, w, Path(url).name, seite])
        abweichung = {nr: [s - (g or 0) for s, g in zip(summe[nr], gwerte[nr] or [0] * len(gcols))] for nr in ZEILEN}
        schlecht = {nr: a for nr, a in abweichung.items() if any(abs(x) > TOLERANZ for x in a)}
        if schlecht:
            raise ValueError(f"{ausgabe}: Summe der Produktbereiche trifft den Gesamtplan nicht: {schlecht}")
        stand["ausgaben"][ausgabe] = {"seite": q["seite"], "spalten": [f"{a} {j}" for a, j in gcols],
                                      "pruefsumme_abweichung_euro": {str(k): v for k, v in abweichung.items()},
                                      "dateien": dateien}
    with open(TSV, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f, delimiter="\t", lineterminator="\n")
        wr.writerow(KOPF)
        wr.writerows(rows)
    stand["lizenz"] = ("Keine Lizenzangabe der Stadt Bonn; Haushaltsplan als Teil der Haushaltssatzung, amtliches Werk "
                       "nach § 5 UrhG (Einschätzung)")
    STAND.write_text(json.dumps(stand, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Haushalt: {len(rows)} Werte aus {len(AUSGABEN)} Ausgaben, Prüfsumme je Spalte innerhalb {TOLERANZ} € → {TSV}")


def lesen(path=TSV):
    if not Path(path).exists():
        return []
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def reihe(pb, rows=None, zeile_nr=17, feld="produktbereich"):
    """Ist und Plan eines Produktbereichs (oder mit feld="produktgruppe" einer Produktgruppe): Ist aus der jüngsten
    Ausgabe, Plan (Ansatz des Haushaltsjahres) aus der Ausgabe des jeweiligen Doppelhaushalts. Gibt [(Jahr, Ist, Plan)]
    zurück (Euro)."""
    rows = lesen() if rows is None else rows
    sel = [r for r in rows if r[feld] == pb and int(r["zeile"]) == zeile_nr]
    ist, plan = {}, {}
    for r in sorted(sel, key=lambda r: r["ausgabe"]):   # spätere Ausgabe überschreibt Ist-Werte
        j, b = int(r["jahr"]), int(r["betrag"])
        if r["art"] == "Ergebnis":
            ist[j] = (b, r)
        elif r["art"] == "Ansatz" and j in {int(x) for x in r["ausgabe"].split("/")}:   # Ansatz des Haushaltsjahres
            plan[j] = (b, r)
    return [(j, ist.get(j), plan.get(j)) for j in sorted(set(ist) | set(plan))]


def pruefbogen(themen=None):
    """Pipeline-Schritt `haushalt-pruefbogen` (einmalig): je Themenseite die gezeigten Werte mit Fundstelle zur
    Prüfung von Hand gegen das PDF. Wird nicht überschrieben."""
    from .themenseiten import ALLE
    if PRUEFBOGEN.exists():
        print(f"Prüfbogen besteht bereits: {PRUEFBOGEN}")
        return
    rows, stand = lesen(), json.loads(STAND.read_text(encoding="utf-8"))
    out = []
    for t in themen or ALLE:
        if not t.produktbereich:
            continue
        for j, ist, plan in reihe(t.produktbereich, rows):
            if j < AB_JAHR:
                continue
            for art, x in (("Ergebnis (Ist)", ist), ("Ansatz (Plan)", plan)):
                if not x:
                    continue
                b, r = x
                url = stand["ausgaben"][r["ausgabe"]]["dateien"][t.produktbereich]["url"]
                out.append([t.titel, f"{t.produktbereich} {r['name']}", j, art, b, f"{b / 1e6:.1f}".replace(".", ","),
                            r["ausgabe"], f"{url}#page={r['seite']}", "", ""])
    PRUEFBOGEN.parent.mkdir(parents=True, exist_ok=True)
    with open(PRUEFBOGEN, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f, delimiter="\t", lineterminator="\n")
        wr.writerow(["thema", "produktbereich", "jahr", "art", "betrag_euro", "mio_euro", "ausgabe", "fundstelle",
                     "urteil", "bemerkung"])
        wr.writerows(out)
    print(f"Prüfbogen Haushalt: {len(out)} Werte → {PRUEFBOGEN}")


# --- Ebenen 2 und 3: Aufwandsarten und Produktgruppen über die Wortkoordinaten ---

def woerter(bbox):
    """Wörter je Seite aus der HTML-Ausgabe von pdftotext -bbox: [[(x0, y0, x1, y1, Text)]] in Punkt."""
    return [[(float(a), float(b), float(c), float(d), html.unescape(t)) for a, b, c, d, t in WORT.findall(seite)]
            for seite in bbox.split("<page ")[1:]]


def _seiten(pdf):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "x.pdf"
        p.write_bytes(pdf)
        out = subprocess.run(["pdftotext", "-bbox", str(p), "-"], capture_output=True, check=True, text=True).stdout
    return woerter(out)


def _textzeilen(ws, tol=2.5):
    """Wörter nach ihrer Mitte in y zu Zeilen: [(y, [Wörter nach x])]."""
    zl = []
    for w in sorted(ws, key=lambda w: (w[1] + w[3]) / 2):
        y = (w[1] + w[3]) / 2
        if zl and abs(zl[-1][0] - y) <= tol:
            zl[-1][1].append(w)
        else:
            zl.append([y, [w]])
    return [(y, sorted(z, key=lambda w: w[0])) for y, z in zl]


def _gruppen(z, luecke=15):
    """Wörter einer Zeile in Gruppen, getrennt an Lücken über luecke pt (Spalten des Seitenkopfs)."""
    out = []
    for w in z:
        if out and w[0] - out[-1][-1][2] <= luecke:
            out[-1].append(w)
        else:
            out.append([w])
    return [[w[4] for w in g] for g in out]


def kopf(ws):
    """(Produktbereich, Produktgruppe, Name, Organisationseinheit) aus dem Seitenkopf; Produktgruppe None auf Seiten des
    Produktbereichs. Die Gruppe „verantwortlich: …“ links im Kopf nennt eine Person und wird nicht gelesen."""
    pb = pg = name = einheit = None
    for _, z in _textzeilen(ws)[:4]:
        gruppen = _gruppen(z)
        for i, g in enumerate(gruppen):
            if re.fullmatch(r"1\.\d{2}", g[0]):
                pb = g[0][2:]
                if i + 1 < len(gruppen):
                    einheit = " ".join(gruppen[i + 1])
            elif re.fullmatch(r"1\.\d{2}\.\d{2}", g[0]):   # Name bis vor „Nr. Profitcenter“
                pg, name = g[0], " ".join(g[1:g.index("Nr.")] if "Nr." in g else g[1:])
    return pb, pg, name, einheit


def koordinaten(ws, nummern=None):
    """Spalten [(Art, Jahr)] und {Zeile: [Betrag oder None je Spalte]} einer Seite des Teilergebnisplans.

    Die Spalten stehen in der Zeile mit den Spaltennummern 1 … n, Art und Jahr darüber. Die Beträge sind rechtsbündig,
    ihr rechter Rand liegt in festem Abstand rechts der Mitte der Spaltennummer (meist 31–32 pt); der häufigste Abstand
    der Seite bestimmt die Spalte jedes Betrags. So bleibt die Spalte auch bei teilweise gefüllten Zeilen eindeutig. Die
    Bezeichnung jeder gelesenen Zeile (auch zweizeilig) muss dem erwarteten Namen entsprechen. Bricht ab, wenn etwas
    nicht passt."""
    nummern = AUFWANDSARTEN if nummern is None else nummern
    zl = _textzeilen(ws)
    kopf_ = next((z for _, z in zl if len(z) >= 5 and [w[4] for w in z] == [str(i) for i in range(1, len(z) + 1)]), None)
    if not kopf_:
        raise ValueError("Zeile mit den Spaltennummern nicht gefunden")
    y_kopf, mitten = (kopf_[0][1] + kopf_[0][3]) / 2, [(w[0] + w[2]) / 2 for w in kopf_]
    abstand = (mitten[-1] - mitten[0]) / (len(mitten) - 1)
    arten, jahre = [None] * len(mitten), [None] * len(mitten)
    oben = min((y for y, z in zl if any(w[4] in ("Ergebnis", "Ansatz", "Planung") for w in z)), default=y_kopf)
    for y, z in zl:
        if not oben <= y < y_kopf - 1:   # nur der Tabellenkopf über den Spaltennummern
            continue
        for w in z:
            k = min(range(len(mitten)), key=lambda i: abs(mitten[i] - (w[0] + w[2]) / 2))
            if abs(mitten[k] - (w[0] + w[2]) / 2) > abstand / 2:
                continue
            if w[4] in ("Ergebnis", "Ansatz", "Planung"):
                arten[k] = arten[k] or w[4]
            elif re.fullmatch(r"20[1-3]\d", w[4]):
                jahre[k] = int(w[4])
    if None in arten or None in jahre:
        raise ValueError(f"Tabellenkopf nicht erkannt: {arten} {jahre}")
    # Tabellenzeilen beginnen links mit ihrer Nummer; Zeilen ohne Nummer (zweizeilige Bezeichnung) gehören zur
    # nächstgelegenen nummerierten Zeile
    tabelle = [(y, z) for y, z in zl if y > y_kopf + 1]
    nummeriert = {}
    for y, z in tabelle:
        if re.fullmatch(r"\d{1,2}", z[0][4]) and z[0][0] <= 100:
            if int(z[0][4]) in nummeriert:
                raise ValueError(f"Zeile {z[0][4]} doppelt")
            nummeriert[int(z[0][4])] = (y, z)
    if not nummeriert:
        raise ValueError("keine Tabellenzeilen gefunden")
    ist_betrag = lambda w: ZAHL.fullmatch(w[4]) and w[2] > mitten[0]   # rechter Rand rechts der ersten Spaltenmitte
    bezeichnung = defaultdict(list)   # Zeile → [(y, x, Wort)] ohne Beträge, Nummer und Rechenzeichen
    for y, z in tabelle:
        nr = min(nummeriert, key=lambda n: abs(nummeriert[n][0] - y))
        eigene = z is nummeriert[nr][1]
        for w in z[1:] if eigene else z:
            if not ist_betrag(w) and not (eigene and re.fullmatch(r"[=+\-/]+", w[4])):
                bezeichnung[nr].append((y, w[0], w[4]))
    # je Betrag genau eine Spaltenmitte im Fenster einer Spaltenbreite; der häufigste Abstand gilt für die ganze Seite
    abstaende = Counter(round(w[2] - c) for _, z in nummeriert.values() for w in z if ist_betrag(w)
                        for c in mitten if -10 <= w[2] - c < abstand - 10)
    anker = [c + (abstaende.most_common(1)[0][0] if abstaende else 0) for c in mitten]
    werte = {}
    for nr, name in nummern.items():
        if nr not in nummeriert:
            raise ValueError(f"Zeile {nr} nicht gefunden")
        gelesen = " ".join(t for *_, t in sorted(bezeichnung[nr]))
        if gelesen != name:
            raise ValueError(f"Zeile {nr}: Bezeichnung „{gelesen}“ statt „{name}“")
        werte[nr] = [None] * len(anker)
        for w in nummeriert[nr][1]:
            if not ist_betrag(w):
                continue
            k = min(range(len(anker)), key=lambda i: abs(anker[i] - w[2]))
            if abs(anker[k] - w[2]) > SPALTE_PT:
                raise ValueError(f"Zeile {nr}: Wert {w[4]} keiner Spalte zuzuordnen")
            if werte[nr][k] is not None:
                raise ValueError(f"Zeile {nr}: zwei Werte in Spalte {k + 1}")
            werte[nr][k] = int(w[4].replace(".", ""))
    return list(zip(arten, jahre)), werte


def pruefsumme(teile, ganze, was, toleranz=TOLERANZ):
    """Summe der Teile [(Schlüssel, Betrag)] gegen das Ganze {Schlüssel: Betrag} je Schlüssel (Ausgabe, Einheit, Jahr,
    Art). Gibt (Zahl der Spalten, größte Abweichung in Euro) zurück; bricht ab, wenn eine Spalte fehlt oder mehr als die
    Toleranz abweicht."""
    summe = defaultdict(int)
    for k, b in teile:
        summe[k] += b
    if set(summe) != set(ganze):
        raise ValueError(f"{was}: Spalten passen nicht zu Zeile 17: {sorted(set(summe) ^ set(ganze))[:5]}")
    abweichung = {k: summe[k] - ganze[k] for k in ganze}
    schlecht = {k: a for k, a in abweichung.items() if abs(a) > toleranz}
    if schlecht:
        raise ValueError(f"{was}: Summe trifft Zeile 17 nicht: {schlecht}")
    return len(abweichung), max((abs(a) for a in abweichung.values()), default=0)


def pruefsummen(aufwand, gruppen, produktbereiche):
    """Die drei Prüfsummen der Ebenen 2 und 3 je Spalte; bricht bei Abweichung ab. Gibt {Prüfung: (Spalten, größte
    Abweichung)} zurück."""
    ausgaben = {r["ausgabe"] for r in aufwand + gruppen}
    pb = lambda r: (r["ausgabe"], r["produktbereich"], int(r["jahr"]), r["art"])
    pg = lambda r: (r["ausgabe"], r["produktgruppe"], int(r["jahr"]), r["art"])
    z17 = {pb(r): int(r["betrag"]) for r in produktbereiche if int(r["zeile"]) == 17 and r["ausgabe"] in ausgaben}
    teile = [r for r in gruppen if int(r["zeile"]) != 17]
    summen = [r for r in gruppen if int(r["zeile"]) == 17]
    return {
        "aufwandsarten_produktbereich": pruefsumme([(pb(r), int(r["betrag"])) for r in aufwand], z17,
                                                   "Aufwandsarten der Produktbereiche"),
        "aufwandsarten_produktgruppe": pruefsumme([(pg(r), int(r["betrag"])) for r in teile],
                                                  {pg(r): int(r["betrag"]) for r in summen}, "Aufwandsarten der Produktgruppen"),
        "produktgruppen_produktbereich": pruefsumme([(pb(r), int(r["betrag"])) for r in summen], z17,
                                                    "Summe der Produktgruppen"),
    }


def _zellen(kopf_, cols, werte, ausgabe, datei, seite):
    """TSV-Zeilen je Zeile und Spalte ohne Finanzplanung; leere Zellen als 0 mit Vermerk."""
    namen = {**AUFWANDSARTEN, 17: ZEILEN[17]}
    for nr, ws in werte.items():
        for (art, jahr), w in zip(cols, ws):
            if art == "Planung":   # Finanzplanung ab dem dritten Jahr: nicht übernommen (wie Zeile 17)
                continue
            yield {"ausgabe": ausgabe, **kopf_, "zeile": nr, "zeile_name": namen[nr], "jahr": jahr, "art": art,
                   "betrag": w or 0, "datei": Path(datei["url"]).name, "seite": seite, "leer": "ja" if w is None else ""}


def ebenen():
    """Pipeline-Schritt `haushalt-ebenen` (einmalig, lokal): data/haushalt/aufwandsarten.tsv (Zeilen 11–16 je
    Produktbereich, S. 1) und produktgruppen.tsv (Zeilen 11–17 je Produktgruppe), Vermerk in STAND.json. Liest dieselben
    PDF wie `haushalt-ausschnitt` (SHA-256 laut STAND.json)."""
    stand = json.loads(STAND.read_text(encoding="utf-8"))
    aufwand, gruppen, zahl = [], [], {}
    for ausgabe in AUSGABEN:
        st, gesehen = stand["ausgaben"][ausgabe], set()
        for pb in (f"{i:02d}" for i in range(1, 18)):
            datei = st["dateien"][pb]
            pdf = _laden(datei["url"])
            if hashlib.sha256(pdf).hexdigest() != datei["sha256"]:
                raise ValueError(f"{ausgabe} PB {pb}: PDF weicht von STAND.json ab ({datei['url']})")
            seiten = _seiten(pdf)
            if kopf(seiten[0])[:2] != (pb, None) or "Teilergebnisplan" not in {w[4] for w in seiten[0]}:
                raise ValueError(f"{ausgabe} PB {pb}: Seite 1 ist nicht der Teilergebnisplan des Produktbereichs")
            for s, ws in enumerate(seiten, 1):
                texte = {w[4] for w in ws}
                if not {"Teilergebnisplan", "Personalaufwendungen"} <= texte:   # erste Seite eines Teilergebnisplans
                    continue
                _, pg, name, einheit = kopf(ws)
                if s > 1 and not pg:
                    raise ValueError(f"{ausgabe} PB {pb} S. {s}: Teilergebnisplan ohne Produktgruppe")
                if pg and (not pg.startswith(f"1.{pb}.") or pg in gesehen):
                    raise ValueError(f"{ausgabe} PB {pb} S. {s}: Produktgruppe {pg} unerwartet oder doppelt")
                gesehen.add(pg)
                cols, werte = koordinaten(ws, AUFWANDSARTEN if s == 1 else {**AUFWANDSARTEN, 17: ZEILEN[17]})
                if [f"{a} {j}" for a, j in cols] != st["spalten"]:
                    raise ValueError(f"{ausgabe} PB {pb} S. {s}: Spalten {cols} weichen von STAND.json ab")
                if s == 1:
                    aufwand += _zellen({"produktbereich": pb, "name": datei["name"]}, cols, werte, ausgabe, datei, s)
                else:
                    gruppen += _zellen({"produktbereich": pb, "produktgruppe": pg, "name": name, "einheit": einheit or ""},
                                       cols, werte, ausgabe, datei, s)
        zahl[ausgabe] = len(gesehen - {None})
    pruefung = pruefsummen(aufwand, gruppen, lesen())
    for path, kopf_, rows in ((AUFWANDSARTEN_TSV, AUFWANDSARTEN_KOPF, aufwand),
                              (PRODUKTGRUPPEN_TSV, PRODUKTGRUPPEN_KOPF, gruppen)):
        with open(path, "w", newline="", encoding="utf-8") as f:
            wr = csv.DictWriter(f, kopf_, delimiter="\t", lineterminator="\n")
            wr.writeheader()
            wr.writerows(rows)
    stand.pop("aufwandsarten", None)
    stand["ebenen"] = {"abruf": datetime.now(timezone.utc).date().isoformat(),
                       "zeilen": {str(k): v for k, v in AUFWANDSARTEN.items()}, "produktgruppen": zahl,
                       "pruefsummen": {k: {"spalten": n, "groesste_abweichung_euro": a} for k, (n, a) in pruefung.items()},
                       "toleranz_euro": TOLERANZ,
                       "leere_zellen": {"produktbereiche": sum(r["leer"] == "ja" for r in aufwand),
                                        "produktgruppen": sum(r["leer"] == "ja" for r in gruppen)}}
    STAND.write_text(json.dumps(stand, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Ebenen: {len(aufwand)} Werte der Produktbereiche, {len(gruppen)} der Produktgruppen ({zahl}); Prüfsummen "
          + ", ".join(f"{k} {n} Spalten bis {a} €" for k, (n, a) in pruefung.items()))


def pruefbogen_ebenen():
    """Pipeline-Schritt `haushalt-pruefbogen-ebenen` (einmalig): etwa 30 Zellen der Ebenen 2 und 3 zur Prüfung von Hand
    gegen das PDF. Darunter die Sonderfälle (negative Werte, teilweise gefüllte Zeilen, umbenannte Produktgruppen,
    0 € im Plan, größte Produktgruppe) und eine Stichprobe der Werte der Seite haushalt/. Wird nicht überschrieben."""
    if EBENEN_PRUEFBOGEN.exists():
        print(f"Prüfbogen besteht bereits: {EBENEN_PRUEFBOGEN}")
        return
    stand = json.loads(STAND.read_text(encoding="utf-8"))
    zellen = {}
    for ebene, path, feld in (("Produktbereich", AUFWANDSARTEN_TSV, "produktbereich"),
                              ("Produktgruppe", PRODUKTGRUPPEN_TSV, "produktgruppe")):
        for r in lesen(path):
            zellen[(ebene, r["ausgabe"], r[feld], int(r["zeile"]), int(r["jahr"]), r["art"])] = r
    neu, alt = max(AUSGABEN), min(AUSGABEN)
    ist = max(k[4] for k in zellen if k[1] == neu and k[5] == "Ergebnis")
    ansichten = [(int(j), "Ansatz") for j in reversed(neu.split("/"))] + [(ist, "Ergebnis")]   # wie haushalt/
    gezeigt = lambda k: k[1] == neu and k[4:] in ansichten
    erst_gezeigt = lambda k: (not gezeigt(k), k)
    auswahl = defaultdict(list)
    # negative Werte der Seite (Ebenen 2 und 3); Zeile 17 einer Produktgruppe auch außerhalb der Ansichten
    for k, r in sorted(zellen.items()):
        if int(r["betrag"]) < 0 and k[1] == neu and (gezeigt(k) or k[0] == "Produktbereich" or k[3] == 17):
            auswahl[k].append("negativer Wert")
    # teilweise gefüllte Zeilen: alle der Produktbereiche, zwei der Produktgruppen; je eine gefüllte und eine leere Zelle
    zeilen = defaultdict(list)
    for k in sorted(zellen):
        zeilen[k[:4]].append(k)
    teilweise = [ks for ks in zeilen.values() if {zellen[k]["leer"] for k in ks} == {"", "ja"}]
    for ks in [ks for ks in teilweise if ks[0][0] == "Produktbereich"] + \
              [ks for ks in teilweise if ks[0][0] == "Produktgruppe" and ks[0][1] == neu][:2]:
        for k in (min((k for k in ks if zellen[k]["leer"] == ""), key=erst_gezeigt),
                  min((k for k in ks if zellen[k]["leer"] == "ja"), key=erst_gezeigt)):
            auswahl[k].append("teilweise gefüllte Zeile")
    # umbenannte Produktgruppen: Zeile 17 im Ansatz des ersten Haushaltsjahres beider Ausgaben
    namen = defaultdict(dict)
    for k, r in zellen.items():
        if k[0] == "Produktgruppe":
            namen[k[2]][k[1]] = r["name"]
    for pg, n in sorted(namen.items()):
        if len(set(n.values())) > 1:
            for a in (alt, neu):
                auswahl[("Produktgruppe", a, pg, 17, int(a.split("/")[0]), "Ansatz")].append("Name geändert")
    # Produktgruppen mit 0 € im Plan eines Haushaltsjahres (nur in der Tabelle), die erste davon
    null = sorted(k for k, r in zellen.items() if k[0] == "Produktgruppe" and k[3] == 17 and gezeigt(k)
                  and k[5] == "Ansatz" and int(r["betrag"]) == 0)
    if null:
        auswahl[null[0]].append("0 € im Plan")
    # größte Produktgruppe im ersten Plan der Seite
    gross = max((k for k in zellen if k[0] == "Produktgruppe" and k[3] == 17 and k[1] == neu and k[4:] == ansichten[0]),
                key=lambda k: int(zellen[k]["betrag"]))
    auswahl[gross].append("größte Produktgruppe")
    # Stichprobe in jedem zweiten Produktbereich, abwechselnd eine Produktgruppe (Zeile 17, Ebene 2) und eine
    # Aufwandsart einer Produktgruppe (Ebene 3); Produktgruppe, Ansicht und Zeile wechseln
    gruppen = sorted({k[2] for k in zellen if k[0] == "Produktgruppe" and k[1] == neu})
    for i, pb in enumerate(f"{n:02d}" for n in range(1, 18, 2)):
        pgs = [g for g in gruppen if g.startswith(f"1.{pb}.")]
        nr, grund = (17, "Stichprobe Ebene 2") if i % 2 == 0 else (11 + (i // 2) % 6, "Stichprobe Ebene 3")
        auswahl[("Produktgruppe", neu, pgs[i % len(pgs)], nr, *ansichten[i % 3])].append(grund)
    out = []
    for k, gruende in sorted(auswahl.items()):
        r = zellen[k]
        url = stand["ausgaben"][r["ausgabe"]]["dateien"][r["produktbereich"]]["url"]
        einheit = f"{k[2]} {r['name']}" if k[0] == "Produktgruppe" else f"{r['produktbereich']} {r['name']}"
        out.append([k[0], einheit, f"{r['zeile']} {r['zeile_name']}", r["jahr"], r["art"], r["betrag"], r["leer"],
                    r["ausgabe"], f"{url}#page={r['seite']}", r["seite"], ", ".join(gruende), ""])
    EBENEN_PRUEFBOGEN.parent.mkdir(parents=True, exist_ok=True)
    with open(EBENEN_PRUEFBOGEN, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f, delimiter="\t", lineterminator="\n")
        wr.writerow(["ebene", "einheit", "zeile", "jahr", "art", "betrag_euro", "leer", "ausgabe", "datei", "seite",
                     "auswahl", "pruefung"])
        wr.writerows(out)
    print(f"Prüfbogen Ebenen: {len(out)} Zellen → {EBENEN_PRUEFBOGEN}")

