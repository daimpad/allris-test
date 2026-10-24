import json, sys
sys.argv = ["x"]
exec(open(Path := __import__("pathlib").Path(__file__).parent / "phase0.py").read().split("# 1. Einwohner")[0])
pop = {}
for ot, r in zcsv("bev.zip", "Zensus2022_Bevoelkerungszahl_100m-Gitter.csv"):
    pop[r["GITTER_ID_100m"]] = (ot, int(r["Einwohner"]))
from collections import Counter
out = {}
for key, z, name, col in [("u18", "u18.zip", "Zensus2022_Anteil_unter_18_100m-Gitter.csv", "AnteilUnter18"),
                          ("a65", "a65.zip", None, None)]:
    import zipfile
    if name is None:
        name = [n for n in zipfile.ZipFile(D / z).namelist() if "100m" in n][0]
        col = None
    s, w, geh = Counter(), Counter(), Counter()
    for ot, r in zcsv(z, name):
        c = col or [k for k in r if k.startswith("Anteil")][0]
        _, e = pop.get(r[[k for k in r if k.upper().startswith("GITTER_ID")][0]], (ot, 0))
        v = num(r[c])
        if v is None:
            geh[ot] += e
        else:
            s[ot] += v * e; w[ot] += e
    out[key] = {n: (round(s[n] / w[n], 1) if w[n] else None, round(100 * geh[n] / (geh[n] + w[n]), 1) if geh[n] + w[n] else None) for n, *_ in ots}
res = json.loads((OUT / "ortsteile.json").read_text())
for n in res:
    res[n]["anteil_unter_18"], res[n]["u18_geheim_prozent"] = out["u18"][n]
    res[n]["anteil_ab_65"], res[n]["a65_geheim_prozent"] = out["a65"][n]
(OUT / "ortsteile.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
for n in ["Endenich", "Tannenbusch", "Beuel-Mitte"]:
    print(n, res[n]["anteil_unter_18"], res[n]["u18_geheim_prozent"], res[n]["anteil_ab_65"], res[n]["a65_geheim_prozent"], "| alt:", res[n]["anteil_0_18"], res[n]["anteil_ab_67"], res[n]["alter_geheim_prozent"])
