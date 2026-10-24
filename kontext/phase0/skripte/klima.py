import json, sqlite3, struct, sys
from collections import Counter
from pathlib import Path
from pyproj import Transformer
from shapely import STRtree, from_wkb
from shapely.geometry import shape
from shapely.ops import transform
P = Path(__file__).parent
gj = json.loads(Path("/home/user/allris-test/data/geo/ortsteile_bonn.geojson").read_text())
t = Transformer.from_crs(4326, 25832, always_xy=True).transform
ots = [(f["properties"]["ortsteil_bez"], transform(t, shape(f["geometry"]))) for f in gj["features"]]
tree = STRtree([g for _, g in ots])
def geom(b):
    env = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}[(b[3] >> 1) & 7]
    return from_wkb(bytes(b[8 + env:]))
c = sqlite3.connect(P / "dl/phk/Klimaanalyse-Planungshinweiskarte_2026_EPSG25832.gpkg")
ew, ew12, fl, fl12 = Counter(), Counter(), Counter(), Counter()
for b, hp, e in c.execute("select geom, Handlungspriorität, Einwohnerzahl from PL_KY_PHK_HP where GN='Bonn'"):
    g = geom(b).buffer(0)
    dring = hp in ("Handlungspriorität 1", "Handlungspriorität 2")
    for i in tree.query(g):
        n, og = ots[i]
        a = og.intersection(g).area
        if a <= 0:
            continue
        s = a / g.area
        ew[n] += (e or 0) * s; fl[n] += a
        if dring:
            ew12[n] += (e or 0) * s; fl12[n] += a
res = json.loads((P / "ergebnis/ortsteile.json").read_text())
for n, _ in ots:
    res[n]["klima_ew_dringend_prozent"] = round(100 * ew12[n] / ew[n], 1) if ew[n] else None
    res[n]["klima_flaeche_dringend_prozent"] = round(100 * fl12[n] / fl[n], 1) if fl[n] else None
    res[n]["klima_ew_modell"] = round(ew[n])
(P / "ergebnis/ortsteile.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
print("Bonn gesamt: EW laut Karte", round(sum(ew.values())), "davon dringend", round(sum(ew12.values())))
