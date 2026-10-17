"""Exporte für den Pilot-Ortsteil: Vorlagen mit Prozesslinie, Akteuren und Orten (JSON, GeoJSON)."""
import json
import sqlite3
from datetime import datetime, timezone

from . import config

DERIVED_NOTE = (
    "Einreichende (originators) und fachliche Zuständigkeit (responsibility.kind = 'fachlich') "
    "sind abgeleitet (method, evidence); alle übrigen Felder stammen unverändert aus den Quellen."
)


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
    locs = db.execute(
        "SELECT l.street, l.postal_code, l.ortsteil, l.stadtbezirk, l.lon, l.lat, pl.stage, "
        "pl.method, pl.confidence, pl.evidence, pl.source_object FROM paper_location pl "
        "JOIN location l ON l.id = pl.location_id WHERE pl.paper_id = ?", (pid,)).fetchall()
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
        "locations": [dict(r) for r in locs],
        "source_object": pid,
    }


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
                        "street": loc["street"], "ortsteil": loc["ortsteil"],
                        "stage": loc["stage"], "confidence": loc["confidence"], "web": p["web"]}}
        for p in papers for loc in p["locations"]
        if loc["lon"] is not None and loc["ortsteil"] == ortsteil
    ]
    (out / "vorlagen.geojson").write_text(json.dumps(
        {"type": "FeatureCollection", "meta": meta, "features": features},
        ensure_ascii=False, indent=1) + "\n")
    db.close()
    print(f"{len(papers)} Vorlagen, {len(features)} Punkte → {out}")
