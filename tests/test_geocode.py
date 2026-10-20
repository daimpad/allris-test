import unittest

from pipeline.geocode import Gazetteer, plan_numbers


def way(name, lon, lat, d=0.002):
    return {"name": name, "highway": "residential", "coords": [[lon - d, lat], [lon + d, lat]]}


class GeocodeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        probe = Gazetteer(ways=[])
        e, m = probe.ot_point["Endenich"], probe.ot_point["Mehlem"]
        cls.gaz = Gazetteer(ways=[
            way("Endenicher Straße", e.x, e.y),
            way("Steinweg", e.x, e.y - 0.001),
            way("Marienforster Steinweg", m.x, m.y),
            way("Kapellenstraße", e.x, e.y + 0.001),
            way("Kapellenstraße", m.x, m.y + 0.001),
            {"name": "Querweg", "highway": "residential",
             "coords": [[e.x, e.y + 0.0005], [e.x, e.y + 0.0015]]},  # kreuzt die Kapellenstraße in Endenich
        ], street_points=[("Am Burggraben", e.x, e.y)],
            housenumbers={"Kapellenstraße": {"Mehlem": ["5", "9"], "Endenich": ["7", "9"], "Beuel-Mitte": ["11"]},
                          "Endenicher Straße": {"Endenich": ["2", "2025"]}})

    def names(self, title, bv=()):
        return [(r["level"], r["name"], r["ortsteil"], r["method"], r["confidence"])
                for r in self.gaz.locate(title, bv)]

    def test_street_with_abbreviation(self):
        self.assertEqual(self.names("Sanierung Endenicher Str. 2. Bauabschnitt"),
                         [("strasse", "Endenicher Straße", "Endenich", "strasse", "mittel")])

    def test_longest_name_wins(self):
        self.assertEqual([n for _, n, *_ in self.names("Marienforster Steinweg: Ampel")],
                         ["Marienforster Steinweg"])

    def test_ambiguous_street_low_unless_narrowed(self):
        self.assertEqual({r[4] for r in self.names("Tempo 30 Kapellenstraße")}, {"niedrig"})
        self.assertEqual(self.names("Tempo 30 Kapellenstraße", bv={"Bad Godesberg"}),
                         [("strasse", "Kapellenstraße", "Mehlem", "strasse+bezirk", "mittel")])
        self.assertEqual(self.names("Tempo 30 Kapellenstraße in Endenich"),
                         [("strasse", "Kapellenstraße", "Endenich", "strasse+ortsteil", "mittel")])

    def test_crossing_decides_ortsteil(self):  # R1
        self.assertEqual(self.gaz.crossings[("Kapellenstraße", "Querweg")], {"Endenich"})
        self.assertIn(("strasse", "Kapellenstraße", "Endenich", "strasse+kreuzung", "mittel"),
                      self.names("Ampel Kapellenstraße / Querweg"))
        self.assertNotIn("Mehlem", {r[2] for r in self.names("Ampel Kapellenstraße / Querweg")})

    def test_housenumber_decides_ortsteil(self):
        self.assertEqual(self.names("Anregung zur Kapellenstraße 5"),
                         [("strasse", "Kapellenstraße", "Mehlem", "strasse+hausnummer", "mittel")])
        self.assertEqual(self.names("Kapellenstraße 7a, Parkplätze")[0][2:4], ("Endenich", "strasse+hausnummer"))
        # Vorrang vor dem genannten Ortsteil derselben Straße (meist die Gemarkung); kein zusätzlicher Ortsbezug
        self.assertEqual([r[:3] for r in self.names("Grundstück in Bonn-Endenich, Kapellenstraße Nr. 5")],
                         [("strasse", "Kapellenstraße", "Mehlem")])
        # ein anderer genannter Ortsteil bleibt erhalten
        self.assertIn(("ortsteil", "Beuel-Mitte", "Beuel-Mitte"),
                      [r[:3] for r in self.names("Kapellenstraße 5 und Beuel-Mitte")])
        row = self.gaz.locate("Kapellenstraße 5")[0]
        self.assertEqual((row["hnr_vorher"], row["evidence"]), (["Endenich", "Mehlem"], "Kapellenstraße"))

    def test_housenumber_without_effect(self):
        # Nummer in zwei Ortsteilen, Jahreszahl, Aufzählung nach Punkt: bisherige Regeln
        self.assertEqual({r[3] for r in self.names("Kapellenstraße 9")}, {"strasse_mehrdeutig"})
        self.assertEqual(self.names("Endenicher Straße 2025 – Sanierung")[0][3], "strasse")
        self.assertEqual(self.names("Endenicher Str. 2. Bauabschnitt")[0][3], "strasse")
        # Ortsteil der Hausnummer ohne Abschnitt im Straßenverzeichnis: ohne Wirkung, im Audit vermerkt
        rows = self.gaz.locate("Kapellenstraße 11")
        self.assertEqual({r["method"] for r in rows}, {"strasse_mehrdeutig"})
        self.assertEqual(rows[0]["hnr_ohne_lage"], "Beuel-Mitte")

    def test_ortsteil_with_city_prefix_and_adjective(self):
        self.assertEqual(self.names("Spielplatz in Bonn-Endenich")[0][:2], ("ortsteil", "Endenich"))
        self.assertEqual(self.names("Endenicher Burg")[0][3], "ortsteil_adjektiv")

    def test_ortsteil_not_repeated_when_street_covers_it(self):
        self.assertEqual([r[0] for r in self.names("Am Burggraben in Bonn-Endenich")], ["strasse"])

    def test_bezirk_level(self):
        self.assertEqual(self.names("Schwimmbad Beuel"),
                         [("stadtbezirk", "Beuel", None, "stadtbezirk_name", "mittel")])

    def test_bv_mismatch_lowers_confidence(self):
        self.assertEqual(self.names("Am Burggraben", bv={"Beuel"})[0][4], "niedrig")

    def test_named_bezirk_elsewhere_lowers_confidence(self):
        self.assertEqual(self.names("Beueler Endenicher Straße")[0][4], "niedrig")

    def test_plan_numbers(self):
        self.assertEqual(plan_numbers("Bebauungsplan Nr. 6522-3 Kaiser-Karl-Ring")[0][0], "6522-3")
        self.assertEqual(plan_numbers("Anhörung zum Bebauungsplanverfahren Nr. 6421-1")[0][0], "6421-1")
        self.assertEqual(plan_numbers("Öffentlichkeitsbeteiligung zum Bebauungsplanverfahrens Nr. 6421-1")[0][0], "6421-1")


if __name__ == "__main__":
    unittest.main()
