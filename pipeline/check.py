"""Prüfung: Kennzahlen gegen den Phase-0-Bericht, Verknüpfungsquote, Datenschutz."""
import re
import sqlite3

from . import actors, config

# Werte aus phase0/BERICHT_phase0.md (Abruf 17.10.2026)
PHASE0 = {
    "Vorlagen": 24912,
    "Vorlagen mit Koordinate": 1814,
    "Vorlagen mit Koordinate in einem Ortsteil": None,
    f"Vorlagen in {config.PILOT_ORTSTEIL} (Stufe A)": 98,
    "Ortsteile mit mind. einer Vorlage": 50,
}


def check():
    db = sqlite3.connect(config.DB)
    one = lambda sql, *a: db.execute(sql, a).fetchone()[0]
    pct = lambda n, d: f"{n} von {d} ({100 * n / d:.1f} %)" if d else "–"

    found = {
        "Vorlagen": one("SELECT COUNT(*) FROM paper"),
        "Vorlagen mit Koordinate": one(
            "SELECT COUNT(DISTINCT pl.paper_id) FROM paper_location pl "
            "JOIN location l ON l.id = pl.location_id WHERE l.lon IS NOT NULL"),
        "Vorlagen mit Koordinate in einem Ortsteil": one(
            "SELECT COUNT(DISTINCT pl.paper_id) FROM paper_location pl "
            "JOIN location l ON l.id = pl.location_id WHERE l.ortsteil IS NOT NULL"),
        f"Vorlagen in {config.PILOT_ORTSTEIL} (Stufe A)": one(
            "SELECT COUNT(DISTINCT pl.paper_id) FROM paper_location pl "
            "JOIN location l ON l.id = pl.location_id WHERE l.ortsteil = ?", config.PILOT_ORTSTEIL),
        "Ortsteile mit mind. einer Vorlage": one(
            "SELECT COUNT(DISTINCT ortsteil) FROM location WHERE ortsteil IS NOT NULL"),
    }
    print("Kennzahl\tPhase 0\tjetzt")
    for k, v in found.items():
        print(f"{k}\t{PHASE0[k] if PHASE0[k] is not None else '–'}\t{v}")

    cons = one("SELECT COUNT(*) FROM consultation")
    print("\nVerknüpfung Beratung ↔ Sitzung (OParl-Lite)")
    print("mit Sitzung:", pct(one("SELECT COUNT(*) FROM consultation WHERE meeting_id IS NOT NULL"), cons))
    print("mit TOP-Ergebnis:", pct(one(
        "SELECT COUNT(*) FROM consultation c JOIN agenda_item a ON a.id = c.agenda_item_id "
        "WHERE a.result IS NOT NULL AND a.result <> ''"), cons))

    politik = tuple(actors.POLITIK_TYPES)
    marks = ",".join("?" * len(politik))
    n_pol = one(f"SELECT COUNT(*) FROM paper WHERE paper_type IN ({marks})", *politik)
    n_pol_orig = one(
        f"SELECT COUNT(DISTINCT p.id) FROM paper p JOIN paper_originator o ON o.paper_id = p.id "
        f"WHERE p.paper_type IN ({marks})", *politik)
    print("\nEinreichende")
    print("Anträge/Anfragen mit abgeleiteten Einreichenden:", pct(n_pol_orig, n_pol))
    print("Vorlagen mit Einreichenden insgesamt:",
          pct(one("SELECT COUNT(DISTINCT paper_id) FROM paper_originator"), found["Vorlagen"]))
    print("davon einer Ratsfraktion/-gruppe zugeordnet:",
          one("SELECT COUNT(*) FROM paper_originator WHERE actor_type IN ('Fraktion/Gruppe', 'Bezirksfraktion') "
              "AND organization_id IS NOT NULL"), "von",
          one("SELECT COUNT(*) FROM paper_originator WHERE actor_type IN ('Fraktion/Gruppe', 'Bezirksfraktion')"),
          "Nennungen")

    n_co = one("SELECT COUNT(*) FROM paper p JOIN organization o ON o.id = p.under_direction_of "
               "WHERE o.classification = ?", actors.CO_DEZERNAT)
    n_co_res = one("SELECT COUNT(DISTINCT paper_id) FROM paper_responsibility WHERE kind = 'fachlich'")
    print("\nCo-Dezernat")
    print("fachliche Zuständigkeit über Stellungnahme abgeleitet:", pct(n_co_res, n_co))

    streets = [r[0] for r in db.execute("SELECT street FROM location WHERE street IS NOT NULL")]
    with_number = [s for s in streets if re.search(r"\d", s)]
    print("\nDatenschutz")
    print("Orte mit Hausnummer im Straßenfeld:", len(with_number))
    db.close()
    if with_number:
        raise SystemExit("Prüfung fehlgeschlagen: Hausnummern in Ortsangaben (CLAUDE.md 5.2).")
