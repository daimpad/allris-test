"""Geokodierung Stufe B (regelbasiert, Titel): Straßen, Ortsteile, Stadtbezirke, Bebauungspläne.

Straßenverzeichnis: benannte OSM-Ways (ODbL), je Name zu Ortsteilen zugeordnet. Mehrere räumlich
getrennte Lagen desselben Namens gelten als mehrdeutig (z. B. „Kapellenstraße“). Ergänzend dienen
die Straßenpunkte der OParl-Locations (Stufe A, CC0) für Namen, die in OSM (noch) fehlen.
"""
import json
import math
import re
from collections import defaultdict

import shapely
from shapely import STRtree
from shapely.geometry import LineString, Point, shape
from shapely.ops import unary_union

from . import config

# Lokale Projektion in Metern (gleichabständig, ausreichend für Bonn)
KY = 111_320.0
KX = KY * math.cos(math.radians(50.7))
to_m = lambda geom: shapely.transform(geom, lambda c: c * (KX, KY))
to_deg = lambda geom: shapely.transform(geom, lambda c: c / (KX, KY))

# Ways ohne Straßencharakter (Haltestellen, Planungen) bleiben außen vor.
SKIP_HIGHWAY = {"platform", "bus_stop", "proposed", "construction", "elevator", "corridor", "razed",
                "abandoned", "disused"}
COMPONENT_GAP_M = 150   # Abstand, ab dem gleichnamige Abschnitte als getrennte Lagen gelten
MIN_SHARE, MIN_LENGTH_M = 0.15, 150  # Ortsteil zählt ab diesem Längenanteil bzw. dieser Länge

# Schreibvarianten der Ortsteilnamen in Titeln
ORTSTEIL_ALIASES = {
    "Lessenich/Meßdorf": ["Lessenich", "Meßdorf", "Messdorf"],
    "Pützchen/Bechlinghoven": ["Pützchen", "Bechlinghoven"],
    "Schwarzrheindorf / Vilich-Rheindorf": ["Schwarzrheindorf", "Vilich-Rheindorf"],
    "Vilich- Müldorf": ["Vilich-Müldorf", "Müldorf"],
    "Bonn-Castell": ["Bonn-Castell", "Castell"],
    "Godesberg-Villenviertel": ["Godesberg-Villenviertel", "Villenviertel"],
}
BEZIRKE = {"Bad Godesberg": ["Bad Godesberg", "Godesberg"], "Beuel": ["Beuel"], "Hardtberg": ["Hardtberg"]}
# Namen, die im Titel oft nicht die Straße meinen (oder mehrere Lagen haben): Konfidenz niedrig
GENERIC_NAMES = {"Rheinufer", "Markt", "Kirchberg", "Wasserland"}
PLAN = re.compile(r"(?:Bebauungsplan(?:es|s|entwurf|entwurfs|verfahren|verfahrens|änderung)?|B-Plan(?:es|s)?)"
                  r"\s*(?:Nr\.?\s*)?(\d{4}-\d{1,3})")
STRASSE = re.compile(r"[Ss]traße$")


def _boundary(pattern, hyphen_before=False):
    """Wortgrenzen; bei Ortsnamen darf ein Bindestrich vorangehen („Bonn-Endenich“)."""
    before = r"(?<!\w)" if hyphen_before else r"(?<![\w-])"
    return rf"{before}(?:{pattern})(?![\w])"


def _street_pattern(name):
    """Regex für einen Straßennamen; „Straße“ auch als „Strasse“ oder „Str.“."""
    m = STRASSE.search(name)
    if not m:
        return re.escape(name)
    return re.escape(name[: m.start()]) + r"(?:[Ss]traße|[Ss]trasse|[Ss]tr\.)"


def _norm_street(text):
    """„Str.“ und „Strasse“ am Ende eines Treffers → „Straße“ (für die Rückzuordnung zum Namen)."""
    return re.sub(r"([Ss])(?:trasse|tr\.)$", r"\1traße", text)


def _alternation(names, pattern=re.escape, hyphen_before=False):
    """Eine Regex für alle Namen, längste zuerst (so gewinnt „Marienforster Steinweg“ vor
    „Steinweg“)."""
    names = sorted(set(names), key=len, reverse=True)
    return re.compile("|".join(_boundary(pattern(n), hyphen_before) for n in names))


class Gazetteer:
    def __init__(self, ways=None, street_points=()):
        """`street_points`: (Name, lon, lat) aus den OParl-Locations der Stadt."""
        ortsteile = json.loads(config.ORTSTEILE.read_text())["features"]
        bezirke = json.loads(config.STADTBEZIRKE.read_text())["features"]
        self.ortsteile = [f["properties"] for f in ortsteile]
        self.ot_geoms = [to_m(shape(f["geometry"])) for f in ortsteile]
        self.ot_tree = STRtree(self.ot_geoms)
        self.ot_point = {p["ortsteil_bez"]: to_deg(g.representative_point())
                         for p, g in zip(self.ortsteile, self.ot_geoms)}
        self.bezirk_point = {f["properties"]["bezirk_bez"]: shape(f["geometry"]).representative_point()
                             for f in bezirke}
        self.ot_by_name = {p["ortsteil_bez"]: p for p in self.ortsteile}
        if ways is None and config.STRASSEN.exists():
            self.streets = json.loads(config.STRASSEN.read_text())["streets"]
        else:
            self.streets = self._streets(ways if ways is not None else self._load_ways())
        self._add_points(street_points)

        # Ortsteilnamen, Varianten und Adjektive („Endenicher“) → Ortsteil
        self.ot_alias = {}
        for name in self.ot_by_name:
            for alias in ORTSTEIL_ALIASES.get(name, [name]):
                self.ot_alias[alias] = (name, "ortsteil_name")
                if re.fullmatch(r"[A-ZÄÖÜ][a-zäöüß]+", alias):
                    self.ot_alias[alias + "er"] = (name, "ortsteil_adjektiv")
        self.bz_alias = {}
        for bezirk, aliases in BEZIRKE.items():
            for alias in aliases:
                self.bz_alias[alias] = (bezirk, "stadtbezirk_name")
                self.bz_alias[alias + "er"] = (bezirk, "stadtbezirk_adjektiv")

        reserved = set(self.ot_alias) | set(self.bz_alias)
        street_names = [n for n in self.streets if n not in reserved and len(n) >= 4]
        self.street_re = _alternation(street_names, _street_pattern)
        self.ot_re = _alternation(self.ot_alias, hyphen_before=True)
        self.bz_re = _alternation(self.bz_alias, hyphen_before=True)

    @staticmethod
    def _load_ways():
        """Ways aus osm_streets.json, sonst aus den bisher zwischengespeicherten Kacheln."""
        if config.OSM_STREETS.exists():
            return json.loads(config.OSM_STREETS.read_text())["ways"]
        ways = {}
        for tile in sorted(config.OSM_TILES.glob("*.json")) if config.OSM_TILES.exists() else []:
            for el in json.loads(tile.read_text()):
                if el.get("geometry"):
                    ways[el["id"]] = {"name": el["tags"]["name"], "highway": el["tags"].get("highway"),
                                      "coords": [[q["lon"], q["lat"]] for q in el["geometry"]]}
        return list(ways.values())

    def _streets(self, ways):
        """Name → Liste von Lagen je Ortsteil: ortsteil, bezirk, lon, lat, length_m, component."""
        lines = defaultdict(list)
        for w in ways:
            if w.get("highway") in SKIP_HIGHWAY or len(w["coords"]) < 2:
                continue
            lines[w["name"].strip()].append(to_m(LineString(w["coords"])))
        streets = {}
        for name, parts in lines.items():
            merged = unary_union(parts)
            blobs = unary_union([p.buffer(COMPONENT_GAP_M / 2) for p in parts])
            comps = list(getattr(blobs, "geoms", [blobs]))
            entries = []
            for ci, comp in enumerate(comps):
                geom = merged.intersection(comp)
                total = geom.length or 1
                for idx in self.ot_tree.query(geom, predicate="intersects"):
                    part = geom.intersection(self.ot_geoms[idx])
                    if part.length < MIN_LENGTH_M and part.length / total < MIN_SHARE:
                        continue
                    longest = max(getattr(part, "geoms", [part]), key=lambda g: g.length)
                    pt = to_deg(longest.interpolate(0.5, normalized=True))
                    props = self.ortsteile[int(idx)]
                    entries.append({"ortsteil": props["ortsteil_bez"], "ortsteil_nr": props["ortsteil"],
                                    "bezirk": props["bezirk_bez"], "lon": round(pt.x, 6),
                                    "lat": round(pt.y, 6), "length_m": round(part.length),
                                    "component": ci, "source": "osm"})
            if entries:
                streets[name] = entries
        return streets

    def _add_points(self, street_points):
        for name, lon, lat in street_points:
            name = (name or "").strip()
            if not name or name in self.streets or lon is None:
                continue
            hits = self.ot_tree.query(to_m(Point(lon, lat)), predicate="intersects")
            if len(hits):
                props = self.ortsteile[int(hits[0])]
                self.streets[name] = [{"ortsteil": props["ortsteil_bez"], "ortsteil_nr": props["ortsteil"],
                                       "bezirk": props["bezirk_bez"], "lon": lon, "lat": lat,
                                       "length_m": None, "component": 0, "source": "oparl-bonn"}]

    # --- Erkennung im Titel ------------------------------------------------------------------

    @staticmethod
    def _find(regex, text, normalize=lambda t: t):
        return [(m.start(), m.end(), normalize(m.group(0)), m.group(0)) for m in regex.finditer(text)]

    @staticmethod
    def _mask(text, hits):
        for s, e, *_ in hits:
            text = text[:s] + " " * (e - s) + text[e:]
        return text

    def locate(self, title, bv_bezirke=()):
        """Ortsbezüge eines Titels als Zeilen mit level, name, ortsteil, bezirk, lon, lat,
        method, confidence, evidence. `bv_bezirke`: Stadtbezirke befasster Bezirksvertretungen."""
        title = title or ""
        streets = self._find(self.street_re, title, _norm_street)
        rest = self._mask(title, streets)
        ots = self._find(self.ot_re, rest)
        rest = self._mask(rest, ots)
        bzs = self._find(self.bz_re, rest)

        named_ot = {self.ot_alias[n][0] for *_, n, _ in ots}
        named_bz = {self.bz_alias[n][0] for *_, n, _ in bzs} | {self.ot_by_name[o]["bezirk_bez"] for o in named_ot}
        rows = []
        for _, _, name, ev in streets:
            if name in self.streets:
                rows += self._resolve_street(name, ev, named_ot, named_bz, set(bv_bezirke))
        covered = {r["ortsteil"] for r in rows}
        for _, _, alias, ev in ots:
            ot, method = self.ot_alias[alias]
            if ot in covered:
                continue
            covered.add(ot)
            pt = self.ot_point[ot]
            conf = "mittel"
            if bv_bezirke and self.ot_by_name[ot]["bezirk_bez"] not in bv_bezirke:
                conf = "niedrig"
            rows.append(dict(level="ortsteil", name=ot, ortsteil=ot, bezirk=self.ot_by_name[ot]["bezirk_bez"],
                             lon=round(pt.x, 6), lat=round(pt.y, 6), method=method,
                             confidence=conf, evidence=ev))
        covered_bz = {r["bezirk"] for r in rows}
        for _, _, alias, ev in bzs:
            bz, method = self.bz_alias[alias]
            if bz in covered_bz:
                continue
            covered_bz.add(bz)
            pt = self.bezirk_point[bz]
            rows.append(dict(level="stadtbezirk", name=bz, ortsteil=None, bezirk=bz,
                             lon=round(pt.x, 6), lat=round(pt.y, 6), method=method,
                             confidence="mittel" if method == "stadtbezirk_name" else "niedrig",
                             evidence=ev))
        return rows

    def _resolve_street(self, name, evidence, named_ot, named_bz, bv_bezirke):
        entries = self.streets[name]
        n_comp = len({e["component"] for e in entries})
        method, conf = "strasse", "niedrig" if name in GENERIC_NAMES else "mittel"
        if named_ot & {e["ortsteil"] for e in entries}:
            entries = [e for e in entries if e["ortsteil"] in named_ot]
            method = "strasse+ortsteil"
        elif n_comp > 1:
            narrow = named_bz or bv_bezirke
            keep = [e for e in entries if e["bezirk"] in narrow] if narrow else []
            if keep and len({e["component"] for e in keep}) == 1:
                entries, method = keep, "strasse+bezirk"
            else:
                entries, method, conf = keep or entries, "strasse_mehrdeutig", "niedrig"
        elif bv_bezirke and not ({e["bezirk"] for e in entries} & bv_bezirke):
            conf = "niedrig"  # Straße liegt nicht im Bezirk der befassten Bezirksvertretung
        elif named_bz and not ({e["bezirk"] for e in entries} & named_bz):
            conf = "niedrig"  # Titel nennt einen anderen Bezirk („Beueler Rheinufer“)
        return [dict(level="strasse", name=name, ortsteil=e["ortsteil"], bezirk=e["bezirk"],
                     lon=e["lon"], lat=e["lat"], method=method, confidence=conf, evidence=evidence,
                     source=e["source"])
                for e in entries]


def plan_numbers(title):
    return [(m.group(1), m.group(0)) for m in PLAN.finditer(title or "")]


def write_gazetteer():
    """Straßenverzeichnis aus den OSM-Rohdaten neu berechnen und in data/geo ablegen."""
    gaz = Gazetteer(ways=Gazetteer._load_ways())
    stand = json.loads(config.STAND.read_text()) if config.STAND.exists() else {}
    config.STRASSEN.write_text(json.dumps({
        "meta": {"source": "OpenStreetMap (Overpass API), benannte Ways mit highway-Tag",
                 "license": config.SOURCES["osm"]["license"],
                 "retrieved_at": stand.get("osm_streets"),
                 "note": "Ortsteile je Straße per Verschneidung mit den Ortsteilflächen der Stadt Bonn; "
                         "component = räumlich getrennte Lage desselben Namens"},
        "streets": dict(sorted(gaz.streets.items()))}, ensure_ascii=False, separators=(",", ":")))
    print(f"{len(gaz.streets)} Straßennamen → {config.STRASSEN}")
