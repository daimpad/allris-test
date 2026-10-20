import json
import tempfile
import unittest
from pathlib import Path

from pipeline import flaechen


class Flaechen(unittest.TestCase):
    def test_vereinfacht_und_gerundet(self):
        # Quadrat mit vielen Zwischenpunkten auf den Kanten: werden entfernt, Ecken bleiben
        edge = [[7.0 + i * 0.00001, 50.7] for i in range(101)]
        ring = edge + [[7.001, 50.701], [7.0, 50.701], [7.0, 50.7]]
        fc = {"features": [{"properties": {"ortsteil_bez": "A"}, "geometry": {"type": "Polygon", "coordinates": [ring]}},
                           {"properties": {"name": "ohne"}, "geometry": None}]}
        out = flaechen.simplify(fc)
        g = out["features"][0]["geometry"]["coordinates"][0]
        self.assertLessEqual(len(g), 6)
        self.assertEqual(out["features"][0]["properties"], {"ortsteil_bez": "A"})
        self.assertIsNone(out["features"][1]["geometry"])
        self.assertTrue(all(len(str(c).split(".")[-1]) <= 5 for p in g for c in p))

    def test_schreibt_json(self):
        with tempfile.TemporaryDirectory() as d:
            sizes = flaechen.write(Path(d))
            self.assertIn("ortsteile", sizes)
            data = json.loads((Path(d) / "flaechen" / "ortsteile.json").read_text())
            self.assertEqual(len(data["features"]), 51)


if __name__ == "__main__":
    unittest.main()
