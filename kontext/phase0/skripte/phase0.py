"""Phase 0 Kontextdaten: Umrechnung auf die 51 Ortsteile (Prüfung, kein Produktionscode)."""
import csv, io, json, statistics, sys, zipfile
from collections import Counter, defaultdict
from pathlib import Path

import shapefile
from pyproj import Transformer
from shapely import STRtree
from shapely.geometry import Point, shape
from shapely.ops import transform

D = Path(__file__).parent / "dl"
OUT = Path(__file__).parent / "ergebnis"
OUT.mkdir(exist_ok=True)
ROOT = Path("/home/user/allris-test")

gj = json.loads((ROOT / "data/geo/ortsteile_bonn.geojson").read_text())
ots = [(f["properties"]["ortsteil_bez"], f["properties"]["bezirk_bez"], shape(f["geometry"])) for f in gj["features"]]
t3035 = Transformer.from_crs(4326, 3035, always_xy=True).transform
t25832 = Transformer.from_crs(4326, 25832, always_xy=True).transform
ot3035 = [(n, b, transform(t3035, g)) for n, b, g in ots]
ot25832 = [(n, b, transform(t25832, g)) for n, b, g in ots]
bezirk = {n: b for n, b, _ in ots}


def assigner(polys):
    tree = STRtree([g for _, _, g in polys])
    def find(x, y):
        p = Point(x, y)
        for i in tree.query(p):
            if polys[i][2].contains(p):
                return polys[i][0]
        return None
    return find


find3035, find25832 = assigner(ot3035), assigner(ot25832)
minx, miny, maxx, maxy = (min(g.bounds[i] for *_, g in ot3035) if i < 2 else max(g.bounds[i] for *_, g in ot3035) for i in range(4))
res = defaultdict(dict)


def num(s):
    s = (s or "").strip().replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def zcsv(z, name):
    with zipfile.ZipFile(D / z) as zf:
        with zf.open(name) as f:
            for row in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig"), delimiter=";"):
                x, y = float(row["x_mp_100m"]), float(row["y_mp_100m"])
                if minx <= x <= maxx and miny <= y <= maxy:
                    ot = find3035(x, y)
                    if ot:
                        yield ot, row


# 1. Einwohner
ew, zellen = Counter(), Counter()
for ot, r in zcsv("bev.zip", "Zensus2022_Bevoelkerungszahl_100m-Gitter.csv"):
    ew[ot] += int(r["Einwohner"]); zellen[ot] += 1
# 2. Alter (infrastrukturelle Gruppen): 0–18 und ab 67; „–“ = geheim gehalten
jung, alt, insg_alter, geheim = Counter(), Counter(), Counter(), Counter()
J, A = ["Unter3", "a3bis5", "a6bis9", "a10bis15", "a16bis18"], ["a67bis74", "a75undaelter"]
for ot, r in zcsv("alter.zip", "Alter_in_infrastrukturellen_Altersgruppen/Zensus2022_Alter_INFR_100m-Gitter.csv"):
    vals = {k: num(r[k]) for k in J + A}
    tot = num(r["Insgesamt_Bevoelkerung"]) or 0
    insg_alter[ot] += tot
    if any(v is None for v in vals.values()):
        geheim[ot] += tot
        continue
    jung[ot] += sum(vals[k] for k in J); alt[ot] += sum(vals[k] for k in A)
# 3. Miete, gewichtet nach Wohnungen
msum, mwhg, mgeheim = Counter(), Counter(), Counter()
for ot, r in zcsv("miete.zip", "Durchschnittliche_Nettokaltmiete_und_Anzahl_der_Wohnungen/Zensus2022_Durchschn_Nettokaltmiete_Anzahl_der_Wohnungen_100m-Gitter.csv"):
    m, w = num(r["durchschnMieteQM"]), num(r["AnzahlWohnungen"])
    if m is None or not w:
        mgeheim[ot] += 1
        continue
    msum[ot] += m * w; mwhg[ot] += w
for n, *_ in ots:
    a_ok = insg_alter[n] - geheim[n]
    res[n].update(einwohner=ew[n], zellen=zellen[n],
                  anteil_0_18=round(100 * jung[n] / a_ok, 1) if a_ok else None,
                  anteil_ab_67=round(100 * alt[n] / a_ok, 1) if a_ok else None,
                  alter_geheim_prozent=round(100 * geheim[n] / insg_alter[n], 1) if insg_alter[n] else None,
                  miete_qm=round(msum[n] / mwhg[n], 2) if mwhg[n] else None, miete_wohnungen=int(mwhg[n]),
                  miete_zellen_ohne_wert=mgeheim[n])
print("Zensus fertig", sum(ew.values()), file=sys.stderr)

# 4. Bodenrichtwerte 2026: Zonen der Stadt Bonn, Wohnbauflächen (NUTA W*), baureifes Land; Median nach Fläche
r = shapefile.Reader(str(D / "brw/BRW_2026_Polygon"))
names = [f[0] for f in r.fields[1:]]
brw_zonen, nutas = defaultdict(list), Counter()
for sr in r.iterShapeRecords():
    rec = dict(zip(names, sr.record))
    if rec["GENA"] != "Bonn":
        continue
    nutas[(rec["NUTA"], rec["ENTW"])] += 1
    if not rec["NUTA"].startswith("W") or rec["ENTW"] != "B":
        continue
    g = shape(sr.shape.__geo_interface__)
    val = num(rec["BRW"])
    for n, b, og in ot25832:
        if og.intersects(g):
            a = og.intersection(g).area
            if a > 1:
                brw_zonen[n].append((val, a, rec["ORTST"]))
def wmedian(pairs):
    pairs = sorted(pairs); tot = sum(a for _, a in pairs); acc = 0
    for v, a in pairs:
        acc += a
        if acc >= tot / 2:
            return v
for n, *_ in ots:
    z = brw_zonen[n]
    res[n].update(brw_median=wmedian([(v, a) for v, a, _ in z]) if z else None, brw_zonen=len(z),
                  brw_min=min((v for v, *_ in z), default=None), brw_max=max((v for v, *_ in z), default=None),
                  brw_ortst=sorted({o for *_, o in z}))
print("BRW fertig; Nutzungsarten Bonn:", nutas.most_common(12), file=sys.stderr)

# 5. Haltestellen (GTFS): Haltestellennamen je Ortsteil (Steige zusammengefasst)
with zipfile.ZipFile(D / "gtfs.zip") as zf:
    rows = list(csv.DictReader(io.TextIOWrapper(zf.open("stops.txt"), encoding="utf-8-sig")))
halt = defaultdict(set)
for s in rows:
    if s.get("location_type") not in ("", "0", None):
        continue
    x, y = t3035(float(s["stop_lon"]), float(s["stop_lat"]))
    ot = find3035(x, y)
    if ot:
        halt[ot].add(s["stop_name"])
# 6. Kitas NRW
kita, u3, ue3 = Counter(), Counter(), Counter()
with open(D / "kitas.csv", encoding="utf-8-sig") as f:
    for k in csv.DictReader(f, delimiter=";"):
        try:
            lat, lon = map(float, k["Geokoordinate"].split(","))
        except ValueError:
            continue
        x, y = t3035(lon, lat)
        ot = find3035(x, y)
        if ot:
            kita[ot] += 1; u3[ot] += num(k["U3-Plätze"]) or 0; ue3[ot] += num(k["Ü3-Plätze"]) or 0
for n, *_ in ots:
    res[n].update(haltestellen=len(halt[n]), kitas=kita[n], kita_plaetze_u3=int(u3[n]), kita_plaetze_ue3=int(ue3[n]))

# 7. Überschwemmungsgebiete (festgesetzt und vorläufig gesichert): Flächenanteil
import subprocess
subprocess.run(["unzip", "-o", "-q", str(D / "uesg.zip"), "-d", str(D / "uesg")], check=True)
uesg = []
for name in ("festgesetzte_Ueberschwemmungsgebiete", "vorlaeufig_gesicherte_Ueberschwemmungsgebiete"):
    rr = shapefile.Reader(str(D / "uesg" / name))
    bonn = shape({"type": "MultiPolygon", "coordinates": []}) if False else None
    for sr in rr.iterShapeRecords():
        g = shape(sr.shape.__geo_interface__)
        if any(g.intersects(og) for *_, og in ot25832):
            uesg.append(g.buffer(0))
from shapely import union_all
U = union_all(uesg) if uesg else None
for n, b, og in ot25832:
    res[n]["flaeche_km2"] = round(og.area / 1e6, 2)
    res[n]["anteil_uesg"] = round(100 * og.intersection(U).area / og.area, 1) if U else 0.0

(OUT / "ortsteile.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
with open(OUT / "ortsteile.tsv", "w", newline="") as f:
    keys = [k for k in next(iter(res.values())) if k != "brw_ortst"]
    w = csv.writer(f, delimiter="\t"); w.writerow(["ortsteil", "bezirk", *keys])
    for n in sorted(res):
        w.writerow([n, bezirk[n], *[res[n][k] for k in keys]])
print("fertig", file=sys.stderr)
