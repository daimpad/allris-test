"""Exporte für den Pilot-Ortsteil: Vorlagen mit Prozesslinie, Akteuren und Orten (JSON, GeoJSON)."""
import csv
import json
import random
import sqlite3
from datetime import datetime, timezone

from . import config

DERIVED_NOTE = (
    "Einreichende (originators), fachliche Zuständigkeit (responsibility.kind = 'fachlich') und "
    "Ortsbezüge der Stufe B bzw. 'vererbt' (locations.stage, method, confidence, evidence) sind "
    "abgeleitet; alle übrigen Felder stammen unverändert aus den Quellen. VORLÄUFIGE FASSUNG: "
    "Stichprobenprüfung von Hand ausstehend."
)
AUDIT_COLUMNS = ["drucksache", "datum", "vorlagenart", "titel", "stufe", "methode", "ebene", "treffer",
                 "ortsteil", "stadtbezirk", "konfidenz", "fundstelle", "quellobjekt", "pruefstatus"]


def _status(row):
    if row["cancelled"]:
        return "abgesagt"
    if row["result"]:
        return "beraten"
    return "terminiert" if row["meeting_id"] else "offen"


def _paper_detail(db, pid):
    p = db.execute(
        "SELECT p.*, o.label AS amt, o.name AS vb_name FROM paper p "
        "LEFT JOIN organization o ON o.id = p.under_direction_of WHERE p.id = ?", (pid,)).fetchone()
    process = db.execute(
        "SELECT c.position, c.role, c.authoritative, c.meeting_id, g.name AS gremium, "
        "m.name AS meeting, m.start_date, m.cancelled, a.number, a.result, a.public "
        "FROM consultation c LEFT JOIN organization g ON g.id = c.organization_id "
        "LEFT JOIN meeting m ON m.id = c.meeting_id LEFT JOIN agenda_item a ON a.id = c.agenda_item_id "
        "WHERE c.paper_id = ? ORDER BY m.start_date IS NULL, m.start_date, c.position", (pid,)).fetchall()
    resp = db.execute(
        "SELECT r.kind, r.method, r.evidence, r.derived, o.label, o.name FROM paper_responsibility r "
        "LEFT JOIN organization o ON o.id = r.organization_id WHERE r.paper_id = ?", (pid,)).fetchall()
    orig = db.execute(
        "SELECT actor, actor_type, organization_id, method, evidence, derived "
        "FROM paper_originator WHERE paper_id = ?", (pid,)).fetchall()
    locs = _locations(db, pid)
    rel = lambda sql: [dict(r) for r in db.execute(sql, (pid,))]
    return {
        "reference": p["reference"],
        "name": p["name"],
        "paper_type": p["paper_type"],
        "date": p["date"],
        "amt": p["amt"],
        "web": p["web"],
        "main_file": p["main_file_url"],
        "responsibility": [dict(r) for r in resp],
        "originators": [dict(r) for r in orig],
        "process": [{**dict(r), "status": _status(r)} for r in process],
        "superordinated": rel("SELECT p.reference, p.paper_type, p.name FROM paper_relation r "
                              "JOIN paper p ON p.id = r.parent_id WHERE r.child_id = ?"),
        "subordinated": rel("SELECT p.reference, p.paper_type, p.name FROM paper_relation r "
                            "JOIN paper p ON p.id = r.child_id WHERE r.parent_id = ? "
                            "ORDER BY p.date"),
        "locations": locs,
        "source_object": pid,
    }


def _locations(db, pid):
    """Ortsbezüge einer Vorlage; Stufe-B-Bezüge entfallen, wo Stufe A denselben Ortsteil belegt."""
    rows = [dict(r) for r in db.execute(
        "SELECT l.level, COALESCE(l.street, l.description) AS name, l.ortsteil, l.stadtbezirk, "
        "l.lon, l.lat, pl.stage, pl.method, pl.confidence, pl.evidence, pl.source_object, "
        "l.source FROM paper_location pl JOIN location l ON l.id = pl.location_id "
        "WHERE pl.paper_id = ? ORDER BY pl.stage, l.level", (pid,))]
    a_ortsteile = {r["ortsteil"] for r in rows if r["stage"] == "A"}
    return [r for r in rows if r["stage"] == "A" or r["ortsteil"] not in a_ortsteile
            or r["ortsteil"] is None]


def _audit_rows(db, where="", params=()):
    """Audit-Zeilen je Ortsbezug; Stufe-B-Treffer bei Vorlagen mit Stufe A gelten als geprüft."""
    a = {}
    for pid, ot in db.execute("SELECT pl.paper_id, l.ortsteil FROM paper_location pl JOIN location l "
                              "ON l.id = pl.location_id WHERE pl.stage = 'A'"):
        a.setdefault(pid, set()).add(ot)
    out = []
    for r in db.execute(
            "SELECT p.id, p.reference, p.date, p.paper_type, p.name, pl.stage, pl.method, l.level, "
            "COALESCE(l.street, l.description), l.ortsteil, l.stadtbezirk, pl.confidence, pl.evidence, "
            "pl.source_object FROM paper_location pl JOIN paper p ON p.id = pl.paper_id "
            f"JOIN location l ON l.id = pl.location_id {where} ORDER BY p.date DESC, p.reference", params):
        pid, *vals = r
        status = "Quelle (Stufe A)" if vals[4] == "A" else "ungeprüft"
        if vals[4] != "A" and pid in a and vals[6] != "stadtbezirk":
            status = "bestätigt durch Stufe A" if vals[8] in a[pid] else "abweichend von Stufe A"
        out.append(vals + [status])
    return out


def _write_tsv(path, header, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def export(ortsteil=config.PILOT_ORTSTEIL):
    db = sqlite3.connect(config.DB)
    db.row_factory = sqlite3.Row
    ids = [r[0] for r in db.execute(
        "SELECT DISTINCT pl.paper_id FROM paper_location pl JOIN location l ON l.id = pl.location_id "
        "JOIN paper p ON p.id = pl.paper_id WHERE l.ortsteil = ? ORDER BY p.date DESC, p.reference",
        (ortsteil,))]
    papers = [_paper_detail(db, pid) for pid in ids]
    meta = {
        "ortsteil": ortsteil,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sources": [dict(r) for r in db.execute("SELECT * FROM source")],
        "note": DERIVED_NOTE,
        "count": len(papers),
    }
    out = config.EXPORT / ortsteil.lower()
    out.mkdir(parents=True, exist_ok=True)
    (out / "vorlagen.json").write_text(
        json.dumps({"meta": meta, "papers": papers}, ensure_ascii=False, indent=1) + "\n")

    features = [
        {"type": "Feature",
         "geometry": {"type": "Point", "coordinates": [loc["lon"], loc["lat"]]},
         "properties": {"reference": p["reference"], "name": p["name"],
                        "paper_type": p["paper_type"], "date": p["date"], "amt": p["amt"],
                        "place": loc["name"], "level": loc["level"], "ortsteil": loc["ortsteil"],
                        "stage": loc["stage"], "method": loc["method"],
                        "confidence": loc["confidence"], "web": p["web"]}}
        for p in papers for loc in p["locations"]
        if loc["lon"] is not None and loc["ortsteil"] == ortsteil
    ]
    (out / "vorlagen.geojson").write_text(json.dumps(
        {"type": "FeatureCollection", "meta": meta, "features": features},
        ensure_ascii=False, indent=1) + "\n")
    _write_tsv(out / "audit_geokodierung.tsv", AUDIT_COLUMNS,
               _audit_rows(db, "WHERE p.id IN (SELECT pl2.paper_id FROM paper_location pl2 JOIN location l2 "
                               "ON l2.id = pl2.location_id WHERE l2.ortsteil = ?)", (ortsteil,)))
    _write_tsv(config.EXPORT / "audit_geokodierung_bonn.tsv", AUDIT_COLUMNS, _audit_rows(db))
    _sample(db, out, ortsteil)
    db.close()
    print(f"{len(papers)} Vorlagen, {len(features)} Punkte → {out}")


def _sample(db, out, ortsteil, n=50, seed=2026):
    """Stichprobe zur Prüfung von Hand: Vorlagen, die nur über Stufe B/vererbt im Ortsteil liegen."""
    ids = [r[0] for r in db.execute(
        "SELECT DISTINCT pl.paper_id FROM paper_location pl JOIN location l ON l.id = pl.location_id "
        "WHERE l.ortsteil = ? AND pl.stage = 'B' AND pl.paper_id NOT IN "
        "(SELECT paper_id FROM paper_location WHERE stage = 'A') ORDER BY pl.paper_id", (ortsteil,))]
    pick = sorted(random.Random(seed).sample(ids, min(n, len(ids))))
    rows = []
    for i, pid in enumerate(pick, 1):
        p = db.execute("SELECT reference, date, paper_type, name, web FROM paper WHERE id = ?", (pid,)).fetchone()
        locs = db.execute(
            "SELECT COALESCE(l.street, l.description), pl.method, pl.confidence, pl.evidence "
            "FROM paper_location pl JOIN location l ON l.id = pl.location_id "
            "WHERE pl.paper_id = ? AND l.ortsteil = ?", (pid, ortsteil)).fetchall()
        rows.append([i, *p, "; ".join(l[0] for l in locs), "; ".join(sorted({l[1] for l in locs})),
                     "; ".join(sorted({l[2] for l in locs})), "; ".join(sorted({l[3] for l in locs})),
                     "", ""])
    _write_tsv(out / "stichprobe_pruefung.tsv",
               ["nr", "drucksache", "datum", "vorlagenart", "titel", "link", "zuordnung", "methode",
                "konfidenz", "fundstelle", "urteil (richtig/falsch/unklar)", "anmerkung"], rows)
