import unittest

from pipeline.objekte import Objekte, norm

DATA = {
    "way/1": {"name": "Adelheidisschule", "art": "Schule", "ortsteil": "Vilich", "bezirk": "Beuel", "lon": 7.1, "lat": 50.7},
    "way/2": {"name": "Alter Friedhof", "art": "Friedhof", "ortsteil": "Nordstadt", "bezirk": "Bonn", "lon": 7.09, "lat": 50.73},
    "way/3": {"name": "Alter Friedhof", "art": "Friedhof", "ortsteil": "Kessenich", "bezirk": "Bonn", "lon": 7.1, "lat": 50.71},
    "way/4": {"name": "Post Tower", "art": "Bauwerk", "ortsteil": "Gronau", "bezirk": "Bonn", "lon": 7.12, "lat": 50.72},
    "way/5": {"name": "Freizeitpark Rheinaue", "art": "Park", "ortsteil": "Hochkreuz", "bezirk": "Bad Godesberg",
              "lon": 7.14, "lat": 50.71},
    "way/6": {"name": "LVR-Landesmuseum Bonn", "art": "Museum", "ortsteil": "Weststadt", "bezirk": "Bonn", "lon": 7.09,
              "lat": 50.73},
    "way/7": {"name": "LVR-LandesMuseum Bonn, Bibliothek", "art": "Bibliothek", "ortsteil": "Weststadt", "bezirk": "Bonn",
              "lon": 7.09, "lat": 50.73},
    "way/8": {"name": "Spielplatz", "art": "Spielplatz", "ortsteil": "Endenich", "bezirk": "Bonn", "lon": 7.07, "lat": 50.72},
}


class ObjekteTest(unittest.TestCase):
    def setUp(self):
        self.obj = Objekte(DATA)

    def test_norm(self):
        self.assertEqual(norm("GGS Adelheidisschule"), "adelheidisschule")
        self.assertEqual(norm("Freizeitpark Bonner Rheinaue"), "freizeitpark rheinaue")
        self.assertEqual(norm("LVR-Landesmuseum"), "lvr landesmuseum")

    def test_eindeutiger_name_vorsatz_und_schreibweise(self):
        self.assertEqual(self.obj.finden("GGS Adelheidisschule")[0]["ortsteil"], "Vilich")
        self.assertEqual(self.obj.finden("Posttower")[0]["name"], "Post Tower")
        self.assertEqual(self.obj.finden("Freizeitpark Bonner Rheinaue")[0]["ortsteil"], "Hochkreuz")

    def test_teil_des_namens_kuerzester(self):
        o, befund = self.obj.finden("LVR-Landesmuseum")
        self.assertEqual((o["name"], befund), ("LVR-Landesmuseum Bonn", "Name"))
        o, befund = self.obj.finden("Rheinaue")
        self.assertEqual((o["name"], befund), ("Freizeitpark Rheinaue", "Teil des Namens"))

    def test_mehrdeutig_nur_mit_ortsteil_aus_dem_text(self):
        self.assertEqual(self.obj.finden("Alter Friedhof"), (None, "mehrdeutig (2 Ortsteile)"))
        self.assertEqual(self.obj.finden("Alter Friedhof", "Kessenich")[0]["ortsteil"], "Kessenich")

    def test_gattungsname_und_unbekanntes(self):
        self.assertEqual(self.obj.finden("Spielplatz"), (None, "Gattungsname"))
        self.assertEqual(self.obj.finden("Gottfried-Kinkel-Schule"), (None, "nicht im Verzeichnis"))


if __name__ == "__main__":
    unittest.main()
