"""Verifikation: Stichprobe exportierter Vorlagen gegen die OParl-API der Stadt abgleichen, und
Datenpaket (Zip) mit Exporten, Audit-Protokollen und Lizenzen erzeugen."""
import json
import random
import sqlite3
import zipfile

from . import config
from .export import _write_tsv
from .net import get_json

# Feld im Export → Feld im OParl-Objekt
FIELDS = {"reference": "reference", "name": "name", "date": "date", "paper_type": "paperType"}


def verify(n=50, seed=2026):
    """Lädt n zufällig gewählte Vorlagen (die Hälfte aus dem Pilot-Ortsteil) erneut aus der
    OParl-API und vergleicht Stammdaten, Federführung, Zahl der Beratungen und Ortsangaben."""
    db = sqlite3.connect(config.DB)
    db.row_factory = sqlite3.Row
    rnd = random.Random(seed)
    pilot = [r[0] for r in db.execute(
        "SELECT DISTINCT pl.paper_id FROM paper_location pl JOIN location l ON l.id = pl.location_id "
        "WHERE l.ortsteil = ? ORDER BY 1", (config.PILOT_ORTSTEIL,))]
    rest = [r[0] for r in db.execute("SELECT id FROM paper ORDER BY id")]
    ids = rnd.sample(pilot, min(n // 2, len(pilot)))
    ids += rnd.sample([i for i in rest if i not in set(ids)], n - len(ids))
    rows, ok_papers = [], 0
    for pid in ids:
        p = db.execute("SELECT * FROM paper WHERE id = ?", (pid,)).fetchone()
        try:
            src = get_json(pid, tries=3)
        except Exception as exc:
            rows.append([p["reference"], "abruf", "", str(exc), "fehler"])
            continue
        checks = [(f, p[f], src.get(o)) for f, o in FIELDS.items()]
        checks.append(("under_direction_of", p["under_direction_of"], (src.get("underDirectionOf") or [None])[0]))
        n_cons = db.execute("SELECT COUNT(*) FROM consultation WHERE paper_id = ?", (pid,)).fetchone()[0]
        checks.append(("beratungen", n_cons, len(src.get("consultation") or [])))
        a_locs = sorted(r[0] for r in db.execute(
            "SELECT location_id FROM paper_location WHERE paper_id = ? AND stage = 'A' AND method <> 'vererbt'",
            (pid,)))
        checks.append(("orte_stufe_a", ";".join(a_locs), ";".join(sorted(l["id"] for l in src.get("location") or []))))
        all_ok = True
        for field, mine, theirs in checks:
            same = str(mine or "") == str(theirs or "")
            all_ok &= same
            rows.append([p["reference"], field, mine, theirs, "ok" if same else "abweichend"])
        ok_papers += all_ok
    db.close()
    _write_tsv(config.EXPORT / "verifikation_oparl.tsv",
               ["drucksache", "feld", "export", "oparl_api", "ergebnis"], rows)
    print(f"Verifikation: {ok_papers} von {len(ids)} Vorlagen stimmen in allen Feldern mit der "
          f"OParl-API überein → {config.EXPORT / 'verifikation_oparl.tsv'}")


PACKAGE_README = """allris-bonn – Datenpaket

Inhalt
- endenich/: Pilot-Ortsteil Endenich – vorlagen.json, vorlagen.geojson, audit_geokodierung.tsv,
  stichprobe_pruefung.tsv (Prüfung von Hand)
- bonn/: ganz Bonn – index.json, ortsteile/<ortsteil>.json, bezirke/<bezirk>.json,
  ohne-ortsbezug/<jahr>.json
- audit_geokodierung_bonn.tsv: Audit aller Ortsbezüge (Stufe, Methode, Treffer, Konfidenz,
  Fundstelle, Prüfstatus)
- verifikation_oparl.tsv: Abgleich einer Stichprobe mit der OParl-API der Stadt Bonn
- strassen_bonn.json: Straßenverzeichnis (OSM) mit Ortsteilen je Straße
- LICENSE-DATA.md: Quellen und Lizenzen je Datei

Abgeleitete Angaben (Einreichende, fachliche Zuständigkeit, Ortsbezüge der Stufe B und
„vererbt“) sind in den Feldern method, confidence und evidence gekennzeichnet.
Quellcode und Dokumentation: https://github.com/daimpad/allris-test
"""


def package():
    """Zip-Paket der Ergebnisse unter data/export/allris-bonn-export.zip."""
    target = config.EXPORT / "allris-bonn-export.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("allris-bonn/LIESMICH.txt", PACKAGE_README)
        z.write(config.ROOT / "data" / "LICENSE-DATA.md", "allris-bonn/LICENSE-DATA.md")
        z.write(config.STRASSEN, "allris-bonn/strassen_bonn.json")
        for path in sorted(config.EXPORT.rglob("*")):
            if path.is_file() and path != target:
                z.write(path, "allris-bonn/" + str(path.relative_to(config.EXPORT)))
    print(f"Datenpaket → {target} ({target.stat().st_size // 1024} KB)")
