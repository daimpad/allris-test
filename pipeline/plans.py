"""Bebauungspläne: Plannummern in Vorlagentiteln mit den Geltungsbereichen der rechtskräftigen
Pläne der Stadt Bonn (CC0) abgleichen. Der Datensatz enthält nur rechtskräftige Pläne; Pläne im
Verfahren bleiben ohne Fläche."""
import json

from shapely.geometry import shape

from . import config

MIN_SHARE = 0.05  # Ortsteile mit weniger als 5 % der Planfläche bleiben unberücksichtigt


def plan_key(name):
    """„6322-2 Teil A“ → „6322-2“ (Teilpläne gehören zur Plannummer im Titel)."""
    return (name or "").split(" ")[0]


class Plans:
    def __init__(self, path=config.BPLAN):
        self.by_nr = {}
        if path.exists():
            for f in json.loads(path.read_text())["features"]:
                self.by_nr.setdefault(plan_key(f["properties"]["name"]), []).append(f)

    def match(self, nr):
        return self.by_nr.get(nr, [])


def plan_locations(plan_rows, ortsteile, plans=None):
    """plan_rows: (paper_id, plannummer, fundstelle). Liefert Orte (je Plan und berührtem Ortsteil,
    Punkt = innerer Punkt der Schnittfläche) und Ortsbezüge der Stufe B."""
    plans = plans or Plans()
    locations, rows = {}, []
    for pid, nr, evidence in plan_rows:
        for f in plans.match(nr):
            name = f["properties"]["name"]
            parts = ortsteile.overlaps(shape(f["geometry"]))
            for ot, part, _ in [x for x in parts if x[2] >= MIN_SHARE] or parts[:1]:
                pt = part.representative_point()
                loc_id = f"bplan:{name}|{ot['ortsteil_bez']}"
                locations[loc_id] = (loc_id, None, None, None, f"Bebauungsplan {name}", round(pt.x, 6),
                                     round(pt.y, 6), ot["ortsteil_bez"], ot["ortsteil"], ot["bezirk_bez"],
                                     "bebauungsplan", "bplan-bonn")
                rows.append((pid, loc_id, "B", "bebauungsplan", "mittel", evidence, pid))
    return locations, rows
