"""Point-in-Polygon gegen die 51 Bonner Ortsteile (shapely)."""
import json

from shapely import STRtree
from shapely.geometry import Point, shape

from . import config


class Ortsteile:
    def __init__(self, path=config.ORTSTEILE):
        features = json.loads(path.read_text())["features"]
        self.props = [f["properties"] for f in features]
        self.tree = STRtree([shape(f["geometry"]) for f in features])

    def locate(self, lon, lat):
        """Liefert die Eigenschaften des Ortsteils, der den Punkt enthält, oder None."""
        hits = self.tree.query(Point(lon, lat), predicate="intersects")
        return self.props[int(hits[0])] if len(hits) else None
