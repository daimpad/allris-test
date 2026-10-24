"""Hausnummern in Titeln aus der Einwohnerschaft (pipeline/maske.py; Entscheidung 24.10.2026: überall ausblenden)."""
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from pipeline import check, maske

STRASSEN = ["Reichsstraße", "Endenicher Straße", "An der Nesselburg"]


class Maske(unittest.TestCase):
    def setUp(self):
        self.m = maske.Maske({"261847", "231681-12 ST"}, STRASSEN)

    def test_nur_vorlagen_aus_der_einwohnerschaft(self):
        t = "Bürgerantrag: im Bereich Reichsstraße 12 in Bonn-Röttgen"
        self.assertEqual(self.m(t, "261847"), "Bürgerantrag: im Bereich Reichsstraße [Hausnummer ausgelassen] in Bonn-Röttgen")
        self.assertEqual(self.m("Sanierung Reichsstraße 12", "250001"), "Sanierung Reichsstraße 12")

    def test_bereiche_buchstaben_und_endungen(self):
        m = self.m
        self.assertEqual(m("Endenicher Straße 308 und 328", "261847"), "Endenicher Straße [Hausnummer ausgelassen]")
        self.assertEqual(m("Vor der Hausnr. An der Nesselburg 18a", "261847"), "Vor der Hausnr. An der Nesselburg [Hausnummer ausgelassen]")
        # unbekannte Straße, erkannt an der Endung; Postleitzahl bleibt
        self.assertEqual(m("Kapitelshof 3, 53229 Bonn", "231681-12 ST"), "Kapitelshof [Hausnummer ausgelassen], 53229 Bonn")
        self.assertEqual(m("Tempo 30 in der Reichsstraße", "261847"), "Tempo 30 in der Reichsstraße")
        self.assertIsNone(m(None, "261847"))

    def test_kette_ueber_folgevorlagen(self):
        db = sqlite3.connect(":memory:")
        db.executescript("""CREATE TABLE paper (id TEXT, reference TEXT, paper_type TEXT, name TEXT);
            CREATE TABLE paper_relation (parent_id TEXT, child_id TEXT);
            INSERT INTO paper VALUES ('a', '231681', 'Bürgerantrag § 24 GO - Öffentlich', 'Bürgerantrag Reichsstraße 5'),
              ('b', '231681-12 ST', 'Stellungnahme der Verwaltung', 'Stellungnahme Reichsstraße 5'),
              ('c', '250001', 'Beschlussvorlage', 'Sanierung Reichsstraße 5');
            INSERT INTO paper_relation VALUES ('a', 'b');""")
        m = maske.aus_db(db, STRASSEN)
        self.assertEqual(m("Stellungnahme Reichsstraße 5", "231681-12 ST"), "Stellungnahme Reichsstraße [Hausnummer ausgelassen]")
        self.assertEqual(m("Sanierung Reichsstraße 5", "250001"), "Sanierung Reichsstraße 5")

    def test_pruefung_findet_offene_titel(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            (base / "suche.json").write_text(json.dumps({"rows": [["261847", "Reichsstraße 12"], ["250001", "Reichsstraße 12"]]}))
            (base / "vorlagen.geojson").write_text(json.dumps({"features": [
                {"properties": {"reference": "261847", "name": "Reichsstraße [Hausnummer ausgelassen]"}}]}))
            self.assertEqual(check.titel_mit_hausnummer(self.m, base), ["261847"])


if __name__ == "__main__":
    unittest.main()
