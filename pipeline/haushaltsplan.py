"""Beträge je Produktbereich aus den Haushaltsplänen der Stadt Bonn (PDF), für die Themenseiten.

Phase 0 (haushalt/phase0/BERICHT.md): Offene Tabellen gibt es nur bis zum Entwurf 2021/22; die Haushaltspläne
2023/24 und 2025/26 liegen auf bonn.de als PDF je Produktbereich mit Textebene. Entscheidung 27.10.2026: Beträge aus
den PDFs, je Themenseite ein Produktbereich, Ist und Plan getrennt, ohne Finanzplanung ab 2027.

Einmaliger Schritt `haushalt-ausschnitt` (lokal, braucht pdftotext aus poppler-utils): lädt je Ausgabe die 17
Teilergebnispläne der Produktbereiche und den Gesamtergebnisplan, liest die Zeilen 10 (ordentliche Erträge),
17 (ordentliche Aufwendungen) und 18 (ordentliches Ergebnis) mit den Spalten des Tabellenkopfs und prüft je Spalte,
dass die Summe der Produktbereiche den Gesamtergebnisplan trifft. Ergebnis: data/haushalt/produktbereiche.tsv mit
Fundstelle (Datei, Seite) und data/haushalt/STAND.json. Die PDFs selbst kommen nicht ins Repository.

Lizenz: Die Seiten der Stadt nennen keine Lizenz. Der Haushaltsplan ist Teil der Haushaltssatzung; als amtliches Werk
(§ 5 UrhG) dürfte er frei sein – eine Einschätzung, keine gesicherte Auskunft. Quelle und Stand werden genannt."""
import csv
import hashlib
import json
import re
import subprocess
import tempfile
import urllib.request
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


def reihe(pb, rows=None, zeile_nr=17):
    """Ist und Plan eines Produktbereichs für die Themenseite: Ist aus der jüngsten Ausgabe, Plan (Ansatz des
    Haushaltsjahres) aus der Ausgabe des jeweiligen Doppelhaushalts. Gibt [(Jahr, Ist, Plan)] zurück (Euro)."""
    rows = lesen() if rows is None else rows
    sel = [r for r in rows if r["produktbereich"] == pb and int(r["zeile"]) == zeile_nr]
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
