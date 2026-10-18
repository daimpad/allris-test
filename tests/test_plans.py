import unittest

from shapely.geometry import box

from pipeline import plans


class FakeOrtsteile:
    """Zwei Ortsteile nebeneinander: A (x 0–1) und B (x 1–2)."""
    def overlaps(self, geom):
        out = []
        for name, nr, poly in (("A", 1, box(0, 0, 1, 1)), ("B", 2, box(1, 0, 2, 1))):
            part = poly.intersection(geom)
            if not part.is_empty:
                out.append(({"ortsteil_bez": name, "ortsteil": nr, "bezirk_bez": "Bonn"}, part, part.area / geom.area))
        return sorted(out, key=lambda x: -x[2])


class FakePlans:
    def __init__(self, features):
        self.by_nr = {}
        for f in features:
            self.by_nr.setdefault(plans.plan_key(f["properties"]["name"]), []).append(f)

    def match(self, nr):
        return self.by_nr.get(nr, [])


def feature(name, x0, x1):
    return {"properties": {"name": name}, "geometry": box(x0, 0, x1, 1).__geo_interface__}


class Bebauungsplaene(unittest.TestCase):
    def test_plan_key(self):
        self.assertEqual(plans.plan_key("6322-2 Teil A"), "6322-2")
        self.assertEqual(plans.plan_key("8118-52"), "8118-52")

    def test_flaeche_ueber_zwei_ortsteile(self):
        locs, rows = plans.plan_locations([("p1", "6421-1", "Bebauungsplan Nr. 6421-1")], FakeOrtsteile(),
                                          FakePlans([feature("6421-1", 0.5, 1.5)]))
        self.assertEqual(sorted(l[7] for l in locs.values()), ["A", "B"])
        self.assertTrue(all(r[2:5] == ("B", "bebauungsplan", "mittel") for r in rows))

    def test_kleiner_anteil_bleibt_unberuecksichtigt(self):
        locs, _ = plans.plan_locations([("p1", "1-1", "x")], FakeOrtsteile(), FakePlans([feature("1-1", 0.0, 1.02)]))
        self.assertEqual([l[7] for l in locs.values()], ["A"])

    def test_teilplaene_und_fehlender_plan(self):
        p = FakePlans([feature("6322-2 Teil A", 0, 0.5), feature("6322-2 Teil B", 0.5, 1)])
        locs, rows = plans.plan_locations([("p1", "6322-2", "x"), ("p2", "9999-1", "y")], FakeOrtsteile(), p)
        self.assertEqual(len(locs), 2)
        self.assertEqual({r[0] for r in rows}, {"p1"})


if __name__ == "__main__":
    unittest.main()
