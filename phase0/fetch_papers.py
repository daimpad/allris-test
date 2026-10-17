"""Phase 0: alle Vorlagen (Papers) aus der OParl-API der Stadt Bonn laden."""
import json, sys, time, urllib.request, concurrent.futures as cf

BASE = "https://www.bonn.sitzung-online.de/oparl/bodies/1/papers"
OUT = sys.argv[1]
SIZE = 100

def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.load(r)
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))

first = get(f"{BASE}?page=1&size={SIZE}")
pages = first["pagination"]["totalPages"]
total = first["pagination"]["totalElements"]
print("totalElements", total, "pages", pages, flush=True)

def fetch(p):
    return p, get(f"{BASE}?page={p}&size={SIZE}")["data"]

results = {1: first["data"]}
with cf.ThreadPoolExecutor(max_workers=6) as ex:
    for p, data in ex.map(fetch, range(2, pages + 1)):
        results[p] = data
        if p % 25 == 0:
            print("page", p, flush=True)

n = 0
with open(OUT, "w", encoding="utf-8") as f:
    for p in sorted(results):
        for paper in results[p]:
            f.write(json.dumps(paper, ensure_ascii=False) + "\n")
            n += 1
print("written", n, flush=True)
