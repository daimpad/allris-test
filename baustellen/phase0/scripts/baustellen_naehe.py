"""Phase 0 (Machbarkeit, keine Produktionslogik): räumliche Nähe Baustellen (geplant-Feed, enthält die
tagesaktuellen) zu verorteten Vorlagen. Kandidat = Vorlagenort ≤ R m vom Baustellenpunkt; zusätzlich
Straßenname gleich, federführend Tiefbauamt (66) oder Verkehrs-Stelle, Vorlagendatum ≥ 2019.
Aufruf: .venv/bin/python -I baustellen_naehe.py <repo> <baustellen.geojson> <outdir>"""
import collections
import csv
import json
import math
import re
import sqlite3
import sys

repo, bpath, out = sys.argv[1:4]
db = sqlite3.connect(f"file:{repo}/data/build/allris.sqlite?mode=ro", uri=True)
bst = json.load(open(bpath))["features"]
KX, KY = 111320 * math.cos(math.radians(50.72)), 110540


def d(a, b):
    return math.hypot((a[0] - b[0]) * KX, (a[1] - b[1]) * KY)


def norm(s):
    s = (s or "").lower()
    s = re.sub(r"\(.*?\)", "", s)
    s = s.replace("str.", "straße").replace("strasse", "straße")
    return re.sub(r"[^a-zäöüß]", "", s)


locs = list(db.execute("""
    SELECT p.reference, p.name, p.date, o.classification, o.name, pl.method, pl.confidence, l.street,
           l.description, l.lon, l.lat, l.level
    FROM paper_location pl JOIN paper p ON p.id = pl.paper_id JOIN location l ON l.id = pl.location_id
    LEFT JOIN organization o ON o.id = p.under_direction_of
    WHERE l.level IN ('strasse', 'bebauungsplan') AND l.lon IS NOT NULL"""))
BAU = re.compile(r"(?i)ausbau|erneuerung|umgestaltung|baureife|vorentwurf|ausbauplanung|kanal|sanierung|baubeginn|bauarbeiten|straßenbau|deckenerneuerung|bau straße|objektplanung")
VERKEHR = re.compile(r"(?i)verkehr|mobilit|straßen")
R = 150
rows, stat = [], collections.Counter()
for f in bst:
    p = f["properties"]
    pt = f["geometry"]["coordinates"]
    street_b = norm(p["bezeichnung"].split("(")[0]) or norm(re.sub(r"\s*\d+\w*$", "", p["adresse"]))
    street_a = norm(re.sub(r"\s*\d+\w*$", "", p["adresse"]))
    near = [x for x in locs if d(pt, (x[9], x[10])) <= R]
    same = [x for x in near if norm(x[7] or x[8]) in (street_b, street_a)]
    amt = [x for x in same if (x[3] or "").startswith("66") or VERKEHR.search(x[4] or "")]
    thema = [x for x in amt if BAU.search(x[1] or "")]
    refs = lambda xs: sorted({x[0] for x in xs})
    stat["baustellen"] += 1
    stat["mit Vorlage ≤150 m"] += bool(near)
    stat["mit Vorlage ≤150 m + gleiche Straße"] += bool(same)
    stat["… + Amt 66/Verkehr federführend"] += bool(amt)
    stat["… + Bau-Stichwort im Titel"] += bool(thema)
    rows.append([p["baustelle_id"], p["bezeichnung"], p["adresse"], p["traeger"], p["massnahme"], p["von"], p["bis"],
                 len(refs(near)), len(refs(same)), len(refs(amt)), len(refs(thema)),
                 "; ".join(f"{x[0]} ({x[2]}) {x[1][:70]}" for x in sorted({x[0]: x for x in (thema or amt)}.values(),
                                                                         key=lambda x: x[2] or "", reverse=True)[:3])])
with open(f"{out}/baustellen_naehe.tsv", "w", newline="") as fh:
    w = csv.writer(fh, delimiter="\t")
    w.writerow(["baustelle_id", "bezeichnung", "adresse", "traeger", "massnahme", "von", "bis", "vorlagen_150m",
                "vorlagen_150m_gleiche_strasse", "davon_amt66_verkehr", "davon_bau_stichwort", "beispiele (bau-stichwort, sonst amt66)"])
    w.writerows(rows)
print(dict(stat))
for r in rows:
    print(r[:5], r[7:11], r[11][:200]) if r[10] else None
