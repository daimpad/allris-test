"""Normalisierung der Rohdaten in eine SQLite-Datenbank (data/build/allris.sqlite)."""
import json
import sqlite3

from . import actors, config
from .geo import Ortsteile

SCHEMA = """
CREATE TABLE source (
  name TEXT PRIMARY KEY, url TEXT, license TEXT, retrieved_at TEXT);
CREATE TABLE organization (
  id TEXT PRIMARY KEY, name TEXT, short_name TEXT, org_type TEXT, classification TEXT,
  label TEXT, start_date TEXT, end_date TEXT, web TEXT, source TEXT);
CREATE TABLE paper (
  id TEXT PRIMARY KEY, reference TEXT, name TEXT, paper_type TEXT, date TEXT,
  under_direction_of TEXT REFERENCES organization, web TEXT,
  main_file_url TEXT, main_file_name TEXT, source TEXT);
CREATE TABLE paper_relation (
  parent_id TEXT, child_id TEXT, source TEXT, PRIMARY KEY (parent_id, child_id));
CREATE TABLE meeting (
  id TEXT PRIMARY KEY, name TEXT, start_date TEXT, cancelled INTEGER, source TEXT);
CREATE TABLE agenda_item (
  id TEXT PRIMARY KEY, meeting_id TEXT REFERENCES meeting, number TEXT, name TEXT,
  result TEXT, public INTEGER, source TEXT);
CREATE TABLE consultation (
  id TEXT PRIMARY KEY, paper_id TEXT REFERENCES paper, position INTEGER,
  organization_id TEXT REFERENCES organization, role TEXT, authoritative INTEGER,
  meeting_id TEXT REFERENCES meeting, agenda_item_id TEXT REFERENCES agenda_item,
  source TEXT, link_source TEXT);
CREATE TABLE location (
  id TEXT PRIMARY KEY, street TEXT, postal_code TEXT, sub_locality TEXT, description TEXT,
  lon REAL, lat REAL, ortsteil TEXT, ortsteil_nr INTEGER, stadtbezirk TEXT, source TEXT);
CREATE TABLE paper_location (
  paper_id TEXT REFERENCES paper, location_id TEXT REFERENCES location, stage TEXT,
  method TEXT, confidence TEXT, evidence TEXT, source_object TEXT,
  PRIMARY KEY (paper_id, location_id, method));
CREATE TABLE paper_originator (
  paper_id TEXT REFERENCES paper, actor TEXT, actor_type TEXT,
  organization_id TEXT REFERENCES organization, method TEXT, evidence TEXT, derived INTEGER);
CREATE TABLE paper_responsibility (
  paper_id TEXT REFERENCES paper, organization_id TEXT REFERENCES organization, kind TEXT,
  method TEXT, evidence TEXT, derived INTEGER);
CREATE INDEX consultation_paper ON consultation(paper_id);
CREATE INDEX paper_location_loc ON paper_location(location_id);
CREATE INDEX location_ortsteil ON location(ortsteil);
CREATE INDEX originator_paper ON paper_originator(paper_id);
CREATE INDEX responsibility_paper ON paper_responsibility(paper_id);
"""


def _read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def build():
    for path in (config.PAPERS, config.ORGANIZATIONS):
        if not path.exists():
            raise SystemExit(f"Fehlt: {path} – zuerst `python -m pipeline fetch` ausführen.")
    if not config.CONSULTATIONS_LITE.exists():
        print(f"Hinweis: {config.CONSULTATIONS_LITE} fehlt – Beratungen ohne Sitzung/TOP.")
    papers = [p for p in _read_jsonl(config.PAPERS) if not p.get("deleted")]
    orgs = json.loads(config.ORGANIZATIONS.read_text())
    lite = ({c["uri"]: c for c in _read_jsonl(config.CONSULTATIONS_LITE)}
            if config.CONSULTATIONS_LITE.exists() else {})
    stand = json.loads(config.STAND.read_text()) if config.STAND.exists() else {}

    config.BUILD.mkdir(parents=True, exist_ok=True)
    config.DB.unlink(missing_ok=True)
    db = sqlite3.connect(config.DB)
    db.executescript(SCHEMA)

    retrieved = {
        "oparl-bonn": stand.get("papers"),
        "oparl-lite": stand.get("consultations_lite"),
        "geo-bonn": stand.get("geo", "2026-10-17"),
    }
    db.executemany("INSERT INTO source VALUES (?,?,?,?)",
                   [(k, v["url"], v["license"], retrieved[k]) for k, v in config.SOURCES.items()])

    orgs_by_id = {o["id"]: o for o in orgs}
    db.executemany(
        "INSERT INTO organization VALUES (?,?,?,?,?,?,?,?,?,'oparl-bonn')",
        [(o["id"], o["name"], o.get("shortName"), o.get("organizationType"),
          o.get("classification"),
          actors.amt_label(o) if o.get("organizationType") == "Verwaltungsbereich" else o["name"],
          o.get("startDate"), o.get("endDate"), o.get("web")) for o in orgs])

    papers_by_id = {p["id"]: p for p in papers}
    ortsteile = Ortsteile()
    meetings, agenda, locations = {}, {}, {}
    rows = {k: [] for k in ("paper", "rel", "cons", "ploc", "orig", "resp")}

    for p in papers:
        mf = p.get("mainFile") or {}
        rows["paper"].append((p["id"], p.get("reference"), p.get("name"), p.get("paperType"),
                              p.get("date"), (p.get("underDirectionOf") or [None])[0],
                              p.get("web"), mf.get("accessUrl"), mf.get("fileName")))
        for child in p.get("subordinatedPaper") or []:
            rows["rel"].append((p["id"], child))
        for parent in p.get("superordinatedPaper") or []:
            rows["rel"].append((parent, p["id"]))

        bezirke = set()
        for pos, c in enumerate(p.get("consultation") or []):
            org = (c.get("organization") or [None])[0]
            name = (orgs_by_id.get(org) or {}).get("name", "")
            if name.startswith("Bezirksvertretung "):
                bezirke.add(name.removeprefix("Bezirksvertretung "))
            lc = lite.get(c["id"]) or {}
            m, a = lc.get("meeting"), lc.get("agendaItem")
            if m:
                meetings[m["uri"]] = (m["uri"], m.get("name"), m.get("startDate"),
                                      int(bool(m.get("cancelled"))))
            if a:
                agenda[a["uri"]] = (a["uri"], m["uri"] if m else None, a.get("number"),
                                    a.get("name"), a.get("result"),
                                    None if a.get("public") is None else int(a["public"]))
            rows["cons"].append((c["id"], p["id"], pos, org, c.get("role"),
                                 int(bool(c.get("authoritative"))),
                                 m["uri"] if m else None, a["uri"] if a else None,
                                 "oparl-lite" if (m or a) else None))

        for loc in p.get("location") or []:
            geom = (loc.get("geojson") or {}).get("geometry") or {}
            lon = lat = ot = None
            if geom.get("type") == "Point":
                lon, lat = geom["coordinates"][:2]
                ot = ortsteile.locate(lon, lat)
            locations[loc["id"]] = (
                loc["id"], (loc.get("streetAddress") or "").strip() or None, loc.get("postalCode"),
                loc.get("subLocality"), loc.get("description"), lon, lat,
                ot["ortsteil_bez"] if ot else None, ot["ortsteil"] if ot else None,
                ot["bezirk_bez"] if ot else None)
            rows["ploc"].append((p["id"], loc["id"], "A", "oparl_location",
                                 "hoch" if lon is not None else "niedrig",
                                 loc.get("description"), loc["id"]))

        for r in actors.originators(p, orgs, bezirke):
            rows["orig"].append((p["id"], r["actor"], r["actor_type"], r["organization_id"],
                                 r["method"], r["evidence"], 1))
        for r in actors.responsibilities(p, orgs_by_id, papers_by_id):
            rows["resp"].append((p["id"], r["organization_id"], r["kind"], r["method"],
                                 r["evidence"], r["derived"]))

    db.executemany("INSERT INTO paper VALUES (?,?,?,?,?,?,?,?,?,'oparl-bonn')", rows["paper"])
    db.executemany("INSERT OR IGNORE INTO paper_relation VALUES (?,?,'oparl-bonn')", rows["rel"])
    db.executemany("INSERT INTO meeting VALUES (?,?,?,?,'oparl-lite')", meetings.values())
    db.executemany("INSERT INTO agenda_item VALUES (?,?,?,?,?,?,'oparl-lite')", agenda.values())
    db.executemany("INSERT INTO consultation VALUES (?,?,?,?,?,?,?,?,'oparl-bonn',?)", rows["cons"])
    db.executemany("INSERT INTO location VALUES (?,?,?,?,?,?,?,?,?,?,'oparl-bonn')",
                   locations.values())
    db.executemany("INSERT OR IGNORE INTO paper_location VALUES (?,?,?,?,?,?,?)", rows["ploc"])
    db.executemany("INSERT INTO paper_originator VALUES (?,?,?,?,?,?,?)", rows["orig"])
    db.executemany("INSERT INTO paper_responsibility VALUES (?,?,?,?,?,?)", rows["resp"])
    db.commit()
    db.close()
    print(f"{len(papers)} Vorlagen, {len(rows['cons'])} Beratungen, {len(meetings)} Sitzungen, "
          f"{len(agenda)} TOPs, {len(locations)} Orte → {config.DB}")
