import json
exec(open(__import__("pathlib").Path(__file__).parent / "phase0.py").read().split("# 1. Einwohner")[0])
from pyproj import Transformer
from shapely import union_all, prepare
t = Transformer.from_crs(3035, 25832, always_xy=True).transform
bonn = union_all([g for *_, g in ot25832]).buffer(100)
parts = []
for name in ("festgesetzte_Ueberschwemmungsgebiete", "vorlaeufig_gesicherte_Ueberschwemmungsgebiete"):
    for sr in shapefile.Reader(str(D / "uesg" / name)).iterShapes():
        g = shape(sr.__geo_interface__)
        if g.intersects(bonn): parts.append(g.buffer(0).intersection(bonn))
U = union_all(parts); prepare(U)
ein, drin = Counter(), Counter()
for ot, row in zcsv("bev.zip", "Zensus2022_Bevoelkerungszahl_100m-Gitter.csv"):
    e = int(row["Einwohner"]); ein[ot] += e
    if U.contains(Point(*t(float(row["x_mp_100m"]), float(row["y_mp_100m"])))): drin[ot] += e
res = json.loads((OUT / "ortsteile.json").read_text())
for n in res: res[n]["uesg_ew_prozent"] = round(100 * drin[n] / ein[n], 1) if ein[n] else 0.0
(OUT / "ortsteile.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
print("Bonn: Einwohner im ÜSG", sum(drin.values()))
for n in sorted(res, key=lambda n: -res[n]["uesg_ew_prozent"])[:8]: print(n, res[n]["uesg_ew_prozent"], "% EW |", res[n]["anteil_uesg"], "% Fläche")
