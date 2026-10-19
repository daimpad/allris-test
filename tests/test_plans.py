import json
import tempfile
import unittest
from pathlib import Path

from shapely.geometry import box

from pipeline import plans
from pipeline.geocode import plan_numbers


class FakeOrtsteile:
    """Zwei Ortsteile nebeneinander: A (x 0–1) und B (x 1–2)."""
    def overlaps(self, geom):
        out = []
        for name, nr, poly in (("A", 1, box(0, 0, 1, 1)), ("B", 2, box(1, 0, 2, 1))):
            part = poly.intersection(geom)
            if not part.is_empty:
                out.append(({"ortsteil_bez": name, "ortsteil": nr, "bezirk_bez": "Bonn"}, part, part.area / geom.area))
        return sorted(out, key=lambda x: -x[2])


def FakePlans(features):
    """Plans aus einer temporären GeoJSON-Datei wie der Datensatz der Stadt."""
    tmp = Path(tempfile.mkdtemp()) / "plaene.geojson"
    tmp.write_text(json.dumps({"type": "FeatureCollection", "features": features}))
    return plans.Plans(tmp)


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
        self.assertTrue(all(r[2:5] == ("B", "bebauungsplan", "hoch") for r in rows))  # eindeutig → hoch

    def test_kleiner_anteil_bleibt_unberuecksichtigt(self):
        locs, _ = plans.plan_locations([("p1", "1-1", "x")], FakeOrtsteile(), FakePlans([feature("1-1", 0.0, 1.02)]))
        self.assertEqual([l[7] for l in locs.values()], ["A"])

    def test_teilplaene_und_fehlender_plan(self):
        p = FakePlans([feature("6322-2 Teil A", 0, 0.5), feature("6322-2 Teil B", 0.5, 1)])
        locs, rows = plans.plan_locations([("p1", "6322-2", "x"), ("p2", "9999-1", "y")], FakeOrtsteile(), p)
        self.assertEqual(len(locs), 2)
        self.assertEqual({r[0] for r in rows}, {"p1"})
        self.assertEqual({r[4] for r in rows}, {"niedrig"})  # zwei Teilpläne passen → mehrdeutig

    def test_einstufung(self):
        p = FakePlans([feature("6322-2 Teil A", 0, 0.5), feature("7925-18", 0, 1), feature("7219-15", 0, 0.5),
                       feature("7219-15", 0.5, 1), feature("7722-44A", 0, 1), feature("7722-44B", 1, 2), feature("6622-2-A", 0, 1)])
        cls = lambda nr: p.classify(nr)[0]
        self.assertEqual(cls("6322-2"), "eindeutig")           # einziger Teilplan
        self.assertEqual(cls("6322-2 Teil A"), "eindeutig")
        self.assertEqual(cls("7925-18 II"), "grundnummer")     # Zusatz nicht im Datensatz
        self.assertEqual(cls("7219-15"), "eindeutig")          # zwei Flächen, ein Plan
        self.assertEqual(cls("7722-44"), "mehrdeutig")
        self.assertEqual(cls("6622-2 A"), "eindeutig")
        self.assertEqual(cls("9999-1"), "nicht_im_datensatz")
        locs, rows = plans.plan_locations([("p", "7219-15", "x")], FakeOrtsteile(), p)
        self.assertEqual(len(locs), 1)  # Flächen zusammengeführt

    def test_nummern_im_titel(self):
        nrs = lambda t: [n for n, _ in plan_numbers(t)]
        self.assertEqual(nrs("Satzungsbeschluss der Bebauungspläne Nrn. 7721-56, 7721-24 und 7621-3"), ["7721-56", "7721-24", "7621-3"])
        self.assertEqual(nrs("Stellungnahmen zum Bebaungsplanes 6322-2 Teil A"), ["6322-2 Teil A"])
        self.assertEqual(nrs("Bebauungsplan 7925-18 II"), ["7925-18 II"])
        self.assertEqual(nrs("Grundstück Flur 9, Flurstück 7618-12-345, Bebauungsplan"), [])
        self.assertEqual(nrs("Drucksache 6421-1 ohne Stichwort"), [])

    def test_verfahrensschritte_und_register(self):
        self.assertEqual(plans.title_steps("Vorentwurf im Geltungsbereich des in Aufstellung befindlichen Bebauungsplanes"), ([], []))
        self.assertEqual(plans.title_steps("Aufstellungsbeschluss sowie Beschluss zur Veröffentlichung des Bebauungsplans "
                                           "Nr. 7522-77 zum Zwecke seiner Aufhebung"), (["aufstellung", "veroeffentlichung"], ["aufhebung"]))
        p = FakePlans([feature("6322-3", 0, 1)])
        paper = lambda ref, date, name: {"reference": ref, "date": date, "name": name, "paper_type": "Beschlussvorlage",
                                         "stand": "entschieden", "plans": [{"nr": "6322-3", "evidence": "x"}],
                                         "locations": [{"method": "bebauungsplan", "ortsteil": "Endenich", "name": "Bebauungsplan 6322-3"}]}
        reg = plans.register([paper("2", "2023-01-01", "Satzungsbeschluss Bebauungsplan Nr. 6322-3"),
                              paper("1", "2022-01-01", "Einleitung des Planverfahrens Bebauungsplan Nr. 6322-3")], p)
        e = reg["plaene"][0]
        self.assertEqual((e["treffer"], e["ortsteile"], [v["drucksache"] for v in e["vorlagen"]]), ("eindeutig", ["Endenich"], ["1", "2"]))
        self.assertEqual([v["schritte"] for v in e["vorlagen"]], [["aufstellung"], ["satzung"]])


if __name__ == "__main__":
    unittest.main()
