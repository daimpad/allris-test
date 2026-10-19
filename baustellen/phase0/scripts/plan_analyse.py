"""Phase 0: Plannummern in Vorlagentiteln (lokale SQLite) gegen den Datensatz „Lage der
Bebauungspläne“ (Rohabruf Thema=20074 vom 19.10.2026). Nur lesend; Ausgabe in den Scratchpad.
Aufruf: .venv/bin/python -I plan_analyse.py <repo> <bplan_raw.geojson> <outdir>"""
import collections
import csv
import json
import re
import sqlite3
import sys

from shapely.geometry import shape, Point
from shapely.ops import unary_union

repo, bplan_path, out = sys.argv[1:4]
db = sqlite3.connect(f"file:{repo}/data/build/allris.sqlite?mode=ro", uri=True)
feats = json.load(open(bplan_path))["features"]

# Plandatensatz: exakter Name, Grundnummer (ohne Zusatz) -> Features
by_name = collections.defaultdict(list)
by_base = collections.defaultdict(list)
for f in feats:
    n = f["properties"]["bplan_name"]
    by_name[n].append(f)
    m = re.match(r"(\d{4}-\d{1,3})", n)
    if m:
        by_base[m.group(1)].append(f)

# 1) Pipeline-Regex (pipeline/geocode.py, Stand 18.10.2026)
PIPE = re.compile(r"(?:Bebauungsplan(?:es|s|entwurf|entwurfs|verfahren|verfahrens|änderung)?|B-Plan(?:es|s)?)"
                  r"\s*(?:Nr\.?\s*)?(\d{4}-\d{1,3})")
# 2) Erweiterte Prüf-Regex: Stichwort (auch Tippfehler, Plural, Bauleitplan, Satzung) und danach
#    eine Liste von Nummern mit optionalem Zusatz (a, A, B, I, II, „Teil A“, „-A“)
NR = r"(?<![\d-])[6-8]\d{3}-\d{1,3}(?:\s?(?:[a-dA-D]|I{1,3}|-[A-D])(?![\w-]))?"
CTX = re.compile(r"(?i)(?:beba?u\w*pl[aä]n\w*|b-pl[aä]n\w*|bauleitplan\w*|satzung|vorhaben- und erschließungsplan\w*)"
                 r"[^;]{0,50}?(" + NR + r"(?:\s*(?:,|und|/|sowie|bzw\.)\s*(?:Nr\.\s*)?" + NR + r")*)")
NR_ONE = re.compile(r"(?<![\d-])(" + NR + r")")
FLUR = re.compile(r"\d{4}-\d{1,3}-\d+")  # Flurstückskennzeichen ausschließen


def ext_numbers(title):
    t = FLUR.sub(" ", title or "")
    found = []
    for m in CTX.finditer(t):
        for n in NR_ONE.findall(m.group(1)):
            n = re.sub(r"\s+", " ", n).strip()
            if n not in found:
                found.append(n)
    return found


def classify(nr):
    if nr in by_name:
        return ("eindeutig" if len(by_name[nr]) == 1 else "mehrdeutig"), by_name[nr]
    base = re.match(r"\d{4}-\d{1,3}", nr).group(0)
    hits = by_base.get(base, [])
    if nr != base and hits:
        return "nur_grundnummer", hits
    if len(hits) == 1:
        return "eindeutig", hits
    if len(hits) > 1:
        return "mehrdeutig", hits  # z. B. 7722-44 -> 7722-44A, 7722-44B
    return "nicht_im_datensatz", []


ortsteile = json.load(open(f"{repo}/data/geo/ortsteile_bonn.geojson"))["features"]
endenich = unary_union([shape(f["geometry"]) for f in ortsteile if f["properties"]["ortsteil_bez"] == "Endenich"])
plans_endenich = {f["properties"]["bplan_name"] for f in feats
                  if shape(f["geometry"]).buffer(0).intersection(endenich).area > 0.05 * shape(f["geometry"]).buffer(0).area}
papers_in_endenich = {r[0] for r in db.execute(
    "SELECT DISTINCT pl.paper_id FROM paper_location pl JOIN location l ON l.id=pl.location_id "
    "WHERE l.ortsteil='Endenich' AND pl.method!='bebauungsplan'")}

rows, stats = [], collections.Counter()
per_paper_pipe, per_paper_ext = {}, {}
for pid, ref, name, date, udo in db.execute("SELECT id, reference, name, date, under_direction_of FROM paper"):
    pipe = [m.group(1) for m in PIPE.finditer(name or "")]
    ext = ext_numbers(name)
    if pipe:
        per_paper_pipe[pid] = pipe
    if ext:
        per_paper_ext[pid] = ext
    for nr in ext:
        cls, hits = classify(nr)
        hit_names = sorted({h["properties"]["bplan_name"] for h in hits})
        in_end = bool(set(hit_names) & plans_endenich) or pid in papers_in_endenich or "Endenich" in (name or "")
        aend = bool(re.search(r"(?i)änderung", name or ""))
        rows.append([ref, date, nr, cls, "; ".join(hit_names), "ja" if nr in pipe else "nein",
                     "ja" if aend else "nein", "ja" if in_end else "nein", name])

with open(f"{out}/plannummern_titel.tsv", "w", newline="") as fh:
    w = csv.writer(fh, delimiter="\t")
    w.writerow(["drucksache", "datum", "plannummer", "klasse", "treffer_datensatz", "pipeline_regex_erkannt",
                "aenderung_im_titel", "endenich", "titel"])
    w.writerows(rows)


def summarize(sel):
    papers = {r[0] for r in sel}
    pairs = {(r[0], r[2]) for r in sel}
    nrs = collections.Counter()
    distinct = collections.defaultdict(set)
    for r in sel:
        nrs[r[3]] += 1
        distinct[r[3]].add(r[2])
    # je Vorlage beste Klasse
    best = {}
    order = ["eindeutig", "nur_grundnummer", "mehrdeutig", "nicht_im_datensatz"]
    for r in sel:
        cur = best.get(r[0])
        if cur is None or order.index(r[3]) < order.index(cur):
            best[r[0]] = r[3]
    return dict(vorlagen=len(papers), paare=len(pairs), paare_je_klasse=dict(nrs),
                nummern_je_klasse={k: len(v) for k, v in distinct.items()},
                vorlagen_je_bester_klasse=dict(collections.Counter(best.values())),
                distinct_nummern=len({r[2] for r in sel}))


res = {
    "stand_db": [r for r in db.execute("SELECT name, retrieved_at FROM source")],
    "vorlagen_gesamt": db.execute("SELECT count(*) FROM paper").fetchone()[0],
    "pipeline_regex_vorlagen": len(per_paper_pipe),
    "pipeline_regex_paare": sum(len(v) for v in per_paper_pipe.values()),
    "erweitert_vorlagen": len(per_paper_ext),
    "nur_erweitert_vorlagen": len(set(per_paper_ext) - set(per_paper_pipe)),
    "nur_pipeline_vorlagen": len(set(per_paper_pipe) - set(per_paper_ext)),
    "stadtweit": summarize(rows),
    "endenich": summarize([r for r in rows if r[7] == "ja"]),
    "plaene_im_datensatz_endenich": sorted(plans_endenich),
    "vorlagen_mit_aenderung_im_titel": len({r[0] for r in rows if r[6] == "ja"}),
    "plaene_im_datensatz_von_vorlagen_referenziert": len({h for r in rows for h in r[4].split("; ") if h}),
}
# Datum der Vorlagen zu Nummern nicht im Datensatz vs. Datensatz-Inkrafttreten: neueste Planänderungen
recent = sorted(((f["properties"]["inkraft_seit"], f["properties"]["bplan_name"]) for f in feats), reverse=True)[:15]
res["neueste_plaene_mit_vorlagen"] = [(d, n, sum(1 for r in rows if n in r[4].split("; "))) for d, n in recent]
json.dump(res, open(f"{out}/plan_analyse.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
