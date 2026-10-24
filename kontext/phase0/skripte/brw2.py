import json, statistics
from collections import defaultdict
exec(open(__import__("pathlib").Path(__file__).parent / "phase0.py").read().split("# 1. Einwohner")[0])
from pyproj import Transformer
t = Transformer.from_crs(3035, 25832, always_xy=True).transform
r = shapefile.Reader(str(D / "brw/BRW_2026_Polygon")); names = [f[0] for f in r.fields[1:]]
zonen, ortst = [], defaultdict(list)
for sr in r.iterShapeRecords():
    d = dict(zip(names, sr.record))
    if d["GENA"] == "Bonn" and d["NUTA"].startswith("W") and d["ENTW"] == "B" and d["ERGNUTA"] != "ASB":
        v = float(d["BRW"].replace(",", "."))
        zonen.append((shape(sr.shape.__geo_interface__), v)); ortst[d["ORTST"]].append(v)
tree = STRtree([g for g, _ in zonen])
pw = defaultdict(list); ohne = Counter(); alle = Counter()
for ot, row in zcsv("bev.zip", "Zensus2022_Bevoelkerungszahl_100m-Gitter.csv"):
    e = int(row["Einwohner"]); x, y = t(float(row["x_mp_100m"]), float(row["y_mp_100m"])); p = Point(x, y)
    alle[ot] += e
    hit = [zonen[i][1] for i in tree.query(p) if zonen[i][0].contains(p)]
    if hit: pw[ot].append((hit[0], e))
    else: ohne[ot] += e
def wmedian(pairs):
    pairs = sorted(pairs); tot = sum(a for _, a in pairs); acc = 0
    for v, a in pairs:
        acc += a
        if acc >= tot / 2:
            return v
res = json.loads((OUT / "ortsteile.json").read_text())
abw = []
alias = {"Alt-Godesberg": "Alt- Godesberg", "Godesberg-Villenviertel": "Godesberg, Villenviertel", "Lessenich/Meßdorf": "Lessenich/ Meßdorf", "Pützchen/Bechlinghoven": "Pützchen/ Bechlinghoven", "Schwarzrheindorf / Vilich-Rheindorf": "Schwarzrheindorf"}
for n in res:
    m = wmedian(pw[n]) if pw[n] else None
    res[n]["brw_median_ew"] = m
    res[n]["brw_ew_ohne_zone_prozent"] = round(100 * ohne[n] / alle[n], 1) if alle[n] else None
    o = ortst.get(alias.get(n, n))
    om = statistics.median(o) if o else None
    res[n]["brw_median_ortst"] = om
    if m and om:
        d = 100 * (m - om) / om; abw.append(abs(d))
        if abs(d) > 15: print(f"> 15 %: {n}: nach Einwohnern {m} | Zonen mit Ortsteilangabe {om}")
(OUT / "ortsteile.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
print("verglichen:", len(abw), "| mittlere Abweichung", round(statistics.mean(abw), 1), "% | Median", round(statistics.median(abw), 1), "% | ohne Wert:", [n for n in res if not res[n]["brw_median_ew"]])
for n in ["Endenich", "Tannenbusch", "Beuel-Mitte"]: print(n, res[n]["brw_median_ew"], res[n]["brw_median_ortst"], res[n]["brw_ew_ohne_zone_prozent"])
