"""Phase 0: (a) Verfahrensschritte nach BauGB in Titeln der Plan-Vorlagen, Vorlagen vor/nach Inkrafttreten;
(b) Vergleich Plan-Geltungsbereich vs. Straßentreffer (Stufe B) derselben Vorlage.
Aufruf: .venv/bin/python -I plan_chronik_vergleich.py <repo> <bplan_raw.geojson> <outdir>"""
import collections
import csv
import json
import random
import re
import sqlite3
import sys

import math
from shapely.ops import transform
from shapely.geometry import Point, shape

repo, bplan_path, out = sys.argv[1:4]
db = sqlite3.connect(f"file:{repo}/data/build/allris.sqlite?mode=ro", uri=True)
feats = json.load(open(bplan_path))["features"]
plan_geom, plan_ink = {}, {}
for f in feats:
    n = f["properties"]["bplan_name"]
    base = re.match(r"(\d{4}-\d{1,3})", n)
    key = base.group(1) if base and " Teil" in n else n
    plan_geom.setdefault(key, []).append(shape(f["geometry"]).buffer(0))
    plan_ink[key] = f["properties"]["inkraft_seit"]

rows = list(csv.DictReader(open(f"{out}/plannummern_titel.tsv"), delimiter="\t"))
STEPS = [
    ("Aufstellungsbeschluss / Einleitung", r"(?i)aufstellungsbeschlu|einleitung des (?:plan|bebauungsplan)|beschluss zur aufstellung|aufstellung (?:des|von)"),
    ("Frühzeitige Beteiligung (§ 3 Abs. 1 / § 4 Abs. 1 BauGB)", r"(?i)frühzeitige"),
    ("Offenlage / Veröffentlichung (§ 3 Abs. 2 BauGB)", r"(?i)offenlage|öffentliche auslegung|veröffentlichung|auslegungsbeschlu"),
    ("Satzungsbeschluss (§ 10 BauGB)", r"(?i)satzungsbeschlu"),
    ("Änderung", r"(?i)änderung"),
    ("Aufhebung", r"(?i)aufhebung"),
    ("Anfrage/Antrag/Stellungnahme (Folgevorlage)", r"(?i)anfrage|antrag|stellungnahme"),
]
step_counts = collections.Counter()
seen = set()
for r in rows:
    if r["drucksache"] in seen:
        continue
    seen.add(r["drucksache"])
    hit = False
    for label, rx in STEPS:
        if re.search(rx, r["titel"]):
            step_counts[label] += 1
            hit = True
    if not hit:
        step_counts["kein Schritt-Stichwort"] += 1

# Vorlagen vor/nach Inkrafttreten je Plan (nur Pläne im Datensatz)
vor_nach = collections.Counter()
plans_with = collections.defaultdict(list)
for r in rows:
    if r["klasse"] != "eindeutig":
        continue
    for t in r["treffer_datensatz"].split("; "):
        k = re.match(r"(\d{4}-\d{1,3})", t).group(1) if " Teil" in t else t
        plans_with[k].append(r["datum"])
for k, dates in plans_with.items():
    ink = plan_ink.get(k)
    before = sum(1 for d in dates if d and d < ink)
    vor_nach["Plan mit Vorlagen vor Inkrafttreten (Verfahren im RIS sichtbar)" if before else
             "Plan nur mit Vorlagen nach Inkrafttreten"] += 1

# (b) Vergleich mit Straßentreffern
# Abstand in Metern: lokale Projektion (äquirektangulär um 50,72° N), für Bonn ausreichend genau
KX, KY = 111320 * math.cos(math.radians(50.72)), 110540
proj = lambda g: transform(lambda x, y, z=None: (x * KX, y * KY), g)


def dist_m(pt, geoms):
    p = proj(pt)
    return min(proj(g).distance(p) for g in geoms) if geoms else 1e12


cmp_rows = []
q = """SELECT p.reference, p.name, pl.method, pl.confidence, l.description, l.street, l.lon, l.lat, l.ortsteil
       FROM paper p JOIN paper_location pl ON pl.paper_id = p.id JOIN location l ON l.id = pl.location_id
       WHERE p.id IN (SELECT paper_id FROM paper_location WHERE method = 'bebauungsplan')"""
by_paper = collections.defaultdict(list)
for rec in db.execute(q):
    by_paper[rec[0]].append(rec)
klassen = collections.Counter()
for ref, recs in by_paper.items():
    plans = {re.sub(r"^Bebauungsplan ", "", r[4]) for r in recs if r[2] == "bebauungsplan"}
    plan_ot = {r[8] for r in recs if r[2] == "bebauungsplan"}
    streets = [r for r in recs if r[2].startswith("strasse")]
    if not streets:
        klassen["nur Plan, kein Straßentreffer"] += 1
        continue
    geoms = []
    for pn in plans:
        k = re.match(r"(\d{4}-\d{1,3})", pn).group(1) if " Teil" in pn else pn
        geoms += plan_geom.get(k, [])
    ds = [(dist_m(Point(s[6], s[7]), geoms), s) for s in streets]
    dmin = min(d for d, _ in ds)
    k = ("Straßenpunkt im Geltungsbereich" if dmin == 0 else
         "Straßenpunkt ≤ 250 m vom Geltungsbereich" if dmin <= 250 else
         "Straßenpunkt 250–1000 m" if dmin <= 1000 else "Straßenpunkt > 1000 m")
    klassen[k] += 1
    same_ot = any(s[8] in plan_ot for _, s in ds)
    cmp_rows.append([ref, "; ".join(sorted(plans)), "; ".join(sorted(plan_ot)),
                     "; ".join(sorted({s[4] or s[5] or "" for _, s in ds})), round(dmin), k,
                     "ja" if same_ot else "nein", recs[0][1]])
with open(f"{out}/vergleich_plan_strasse.tsv", "w", newline="") as fh:
    w = csv.writer(fh, delimiter="\t")
    w.writerow(["drucksache", "plaene", "ortsteile_plan", "strassen", "min_abstand_m", "klasse", "ortsteil_gleich", "titel"])
    w.writerows(sorted(cmp_rows))
random.seed(19102026)
sample = random.sample(sorted(cmp_rows), min(15, len(cmp_rows)))
res = dict(schritte_in_titeln=dict(step_counts), plaene_vor_nach=dict(vor_nach),
           vorlagen_mit_plan_geltungsbereich=len(by_paper), vergleich=dict(klassen),
           ortsteil_gleich=sum(1 for r in cmp_rows if r[6] == "ja"), vergleich_n=len(cmp_rows),
           stichprobe=[r[:7] + [r[7][:110]] for r in sample])
json.dump(res, open(f"{out}/plan_chronik_vergleich.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
