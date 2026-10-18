"""Phase 0 Prozessebene und Zeitleiste: Schrittfolgen, Sonderwege und Datumsabdeckung auswerten.

Aufruf (nach `python -m pipeline build`): python prozess/analyse_phase0.py
Schreibt prozess/stichprobe_endenich.tsv und gibt Kennzahlen für den Bericht aus.
"""
import csv
import json
import random
import sqlite3
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline import config, process  # noqa: E402
from pipeline.export import _paper_detail  # noqa: E402

db = sqlite3.connect(config.DB)
db.row_factory = sqlite3.Row
one = lambda sql, *a: db.execute(sql, a).fetchone()[0]
pct = lambda n, d: f"{n} von {d} ({100 * n / d:.1f} %)" if d else "–"

# --- Sonderwege und Lücken, ganz Bonn ---------------------------------------------------------
n = one("SELECT COUNT(*) FROM paper")
print("Vorlagen:", n)
print("Vorlagenarten:", dict(db.execute("SELECT paper_type, COUNT(*) FROM paper GROUP BY 1 ORDER BY 2 DESC")))
print("ohne Beratungsfolge:", pct(one("SELECT COUNT(*) FROM paper WHERE id NOT IN (SELECT paper_id FROM consultation)"), n))
print("mit entscheidender Beratung:", pct(one("SELECT COUNT(DISTINCT paper_id) FROM consultation WHERE authoritative = 1"), n))
rat_only = one("""SELECT COUNT(*) FROM (SELECT c.paper_id FROM consultation c JOIN organization o ON o.id = c.organization_id
    GROUP BY c.paper_id HAVING COUNT(*) = 1 AND MAX(o.name) = 'Rat' AND MAX(c.authoritative) = 1)""")
print("Rat entscheidet ohne Vorberatung (einzige Beratung):", rat_only)
res = Counter(r[0] for r in db.execute("SELECT a.result FROM consultation c JOIN agenda_item a ON a.id = c.agenda_item_id"))
print("Ergebnisse (Top 12):", res.most_common(12))
print("Schleifen: vertagt", sum(v for k, v in res.items() if k and "vertagt" in k),
      "| verwiesen", sum(v for k, v in res.items() if k and "verwiesen" in k))
print("Änderungsanträge:", one("SELECT COUNT(*) FROM paper WHERE paper_type = 'Änderungsantrag'"),
      "| Stellungnahmen:", one("SELECT COUNT(*) FROM paper WHERE paper_type = 'Stellungnahme der Verwaltung'"))
print("Dringlichkeits-/Eilentscheidungen:", dict(db.execute(
    "SELECT paper_type, COUNT(*) FROM paper WHERE paper_type LIKE 'Dringlichkeitsentscheidung%' "
    "OR paper_type LIKE 'Eilentscheidung%' GROUP BY 1")))
print("davon mit Beratungsfolge:", one(
    "SELECT COUNT(DISTINCT p.id) FROM paper p JOIN consultation c ON c.paper_id = p.id WHERE "
    "p.paper_type LIKE 'Dringlichkeitsentscheidung%' OR p.paper_type LIKE 'Eilentscheidung%'"))
print("nichtöffentliche TOP (Vorlagenart):", one("SELECT COUNT(*) FROM paper WHERE paper_type = ?", process.NICHTOEFFENTLICH_TYPE))
print("TOP nicht öffentlich (agenda_item.public = 0):", one("SELECT COUNT(*) FROM agenda_item WHERE public = 0"))

# --- Datumsabdeckung je Zeitdimension ---------------------------------------------------------
print("\nDatum der Vorlage gesetzt:", pct(one("SELECT COUNT(*) FROM paper WHERE date IS NOT NULL AND date <> ''"), n))
print("Zeitraum:", one("SELECT MIN(date) FROM paper"), "bis", one("SELECT MAX(date) FROM paper"))
cons = one("SELECT COUNT(*) FROM consultation")
print("Beratungen mit Sitzungsdatum (OParl-Lite):", pct(one(
    "SELECT COUNT(*) FROM consultation c JOIN meeting m ON m.id = c.meeting_id WHERE m.start_date IS NOT NULL"), cons))
print("Sitzungsdatum vor Datum der Vorlage (Plausibilität):", one(
    "SELECT COUNT(*) FROM consultation c JOIN meeting m ON m.id = c.meeting_id JOIN paper p ON p.id = c.paper_id "
    "WHERE substr(m.start_date, 1, 10) < p.date"))
gap = [r[0] for r in db.execute(
    "SELECT julianday(substr(m.start_date,1,10)) - julianday(p.date) FROM consultation c JOIN meeting m "
    "ON m.id = c.meeting_id JOIN paper p ON p.id = c.paper_id WHERE m.start_date IS NOT NULL ORDER BY 1")]
if gap:
    print("Tage zwischen Vorlage und Beratung: Median", gap[len(gap) // 2], "| 90 %-Quantil", gap[int(len(gap) * .9)],
          "| Maximum", gap[-1])
if config.MEETINGS.exists():
    ms = json.loads(config.MEETINGS.read_text())
    print("Sitzungen (OParl-API):", len(ms), "| künftig:", sum(1 for m in ms if (m.get("start") or "") > "2026-10-18"),
          "| abgesagt:", sum(1 for m in ms if m.get("cancelled")))
print("modified/created ohne Aussagekraft (2000-01-01):", "ja" if one(
    "SELECT COUNT(*) FROM paper") else "–")

# --- Stichprobe Endenich, geschichtet nach Initiierungsart ------------------------------------
ids = [r[0] for r in db.execute(
    "SELECT DISTINCT pl.paper_id FROM paper_location pl JOIN location l ON l.id = pl.location_id "
    "WHERE l.ortsteil = 'Endenich' ORDER BY 1")]
rnd = random.Random(2026)
groups = {}
for pid in ids:
    t = db.execute("SELECT paper_type FROM paper WHERE id = ?", (pid,)).fetchone()[0]
    groups.setdefault(process.initiation_kind(t), []).append(pid)
quota = {"verwaltung": 8, "antrag": 7, "einwohner": 6, "anfrage": 4, "sonderweg": 3, "sonstige": 2}
sample = [pid for k, q in quota.items() for pid in rnd.sample(groups.get(k, []), min(q, len(groups.get(k, []))))]
rows, observed = [], Counter()
for pid in sample:
    d = _paper_detail(db, pid)
    seq = " → ".join(f"{s['typ']}[{s['status']}]" for s in d["steps"])
    for s in d["steps"]:
        observed[(s["typ"], s["status"])] += 1
    rows.append([d["reference"], d["paper_type"], process.initiation_kind(d["paper_type"]), d["stand"],
                 len(d["process"]), sum(1 for s in d["steps"] if s.get("date_status") == "abgeleitet"), seq])
with open(ROOT / "prozess" / "stichprobe_endenich.tsv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(["drucksache", "vorlagenart", "initiierung", "stand", "beratungen", "datiert_ueber_lite", "schrittfolge"])
    w.writerows(rows)
print("\nStichprobe Endenich:", len(sample), "Vorlagen; Gruppen:", {k: len(v) for k, v in groups.items()})
print("Schritte nach Typ und Status:", sorted(observed.items()))
