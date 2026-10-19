"""Phase 0 Soll-Modell: alle Belege (Rechtsgrundlagen) aus verfahren.json sammeln und eine Stichprobe ziehen.
Aufruf: python soll/phase0/scripts/belege.py <bonn-entscheidet>"""
import collections
import csv
import json
import random
import re
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "out"
LAWS = ["GO NRW", "BauGB", "GeschO", "BezS", "HS", "ZustO", "Satzung", "Leitlinien"]


def walk(node, path=""):
    if isinstance(node, dict):
        if isinstance(node.get("beleg"), str):
            text = " · ".join(str(v) for k, v in node.items() if isinstance(v, str) and k not in ("beleg", "id", "url", "note", "farbe"))
            yield path, node["beleg"], text
        for k, v in node.items():
            yield from walk(v, f"{path}/{node.get('id', k) if k != 'beleg' else k}" if isinstance(v, (dict, list)) else path)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, f"{path}[{i}]")


def main(be):
    data = json.loads((Path(be) / "data" / "verfahren.json").read_text(encoding="utf-8"))
    rows = [{"ort": p, "beleg": b, "aussage": t} for p, b, t in walk(data)]
    law = lambda b: [l for l in LAWS if re.search(rf"(?<![A-Za-z]){re.escape(l)}\b", b)] or ["sonstiges"]
    counts = collections.Counter(l for r in rows for l in law(r["beleg"]))
    distinct = sorted({r["beleg"] for r in rows})
    random.seed(20261019)
    # Stichprobe 20: je Gesetz anteilig, mindestens eine je vorkommendem Gesetz
    by = collections.defaultdict(list)
    for r in rows:
        by[law(r["beleg"])[0]].append(r)
    sample = [random.choice(v) for v in by.values()]
    rest = [r for r in rows if r not in sample]
    sample += random.sample(rest, 20 - len(sample))
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "belege_stichprobe.tsv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["nr", "ort", "beleg", "aussage", "pruefung", "begruendung"])
        for i, r in enumerate(sample, 1):
            w.writerow([i, r["ort"], r["beleg"], r["aussage"].replace("\n", " ")[:200], "", ""])
    print(json.dumps({"belege": len(rows), "verschieden": len(distinct), "je_gesetz": counts.most_common()}, ensure_ascii=False))
    for i, r in enumerate(sample, 1):
        print(i, "|", r["beleg"], "|", r["aussage"][:150])


if __name__ == "__main__":
    main(sys.argv[1])
