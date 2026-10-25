import unittest

from pipeline import volltext
from pipeline.geocode import Gazetteer


def way(name, lon, lat, d=0.002):
    return {"name": name, "highway": "residential", "coords": [[lon - d, lat], [lon + d, lat]]}


KOPF = """Beschlussvorlage
Drucksachen-Nr.
251234
Beratungsfolge
Bezirksvertretung Beuel 01.02.2025 Entscheidung
Sachverhalt
"""


class VolltextTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        probe = Gazetteer(ways=[], housenumbers={})
        e, m = probe.ot_point["Endenich"], probe.ot_point["Mehlem"]
        cls.gaz = Gazetteer(ways=[way("Endenicher Straße", e.x, e.y), way("Markt", m.x, m.y)], housenumbers={})

    def test_clean_blendet_kopf_gremien_und_wiederholungen_aus(self):
        text = KOPF + "Die Bezirksvertretung Beuel hat beraten.\nSeite 1 von 3 Dokumentenklasse B\n" * 3 + "Anlage/n\nListe\n"
        main, annex = volltext.clean(text)
        self.assertNotIn("Beratungsfolge", main)
        self.assertNotIn("Bezirksvertretung Beuel", main)
        self.assertNotIn("Dokumentenklasse", main)
        self.assertTrue(annex.startswith("Anlage/n"))

    def test_hauptteil_zweimal_genannt_ist_mittel(self):
        rows, info = volltext.locate(self.gaz, KOPF + "Ausbau der Endenicher Straße. Die Endenicher Straße wird saniert.")
        self.assertEqual(info["befund"], "verortet")
        self.assertEqual([(r["name"], r["method"], r["confidence"], r["nennungen"]) for r in rows],
                         [("Endenicher Straße", "volltext_strasse", "mittel", 2)])
        self.assertNotIn("saniert", rows[0]["evidence"])  # Fundstelle ohne Textauszug

    def test_einmal_genannt_ist_niedrig_und_anlage_zaehlt_nicht(self):
        rows, _ = volltext.locate(self.gaz, KOPF + "Ausbau der Endenicher Straße.")
        self.assertEqual(rows[0]["confidence"], "niedrig")
        rows, info = volltext.locate(self.gaz, KOPF + "Kein Ort.\nAnlage/n\nEndenicher Straße, Endenicher Straße")
        self.assertEqual((rows, info["befund"]), ([], "nur in Anlagen genannt, nicht verortet"))

    def test_gattungsname_und_einzelner_bezirk_zaehlen_nicht(self):
        self.assertEqual(volltext.locate(self.gaz, KOPF + "Wochenmarkt auf dem Markt.")[0], [])
        rows, info = volltext.locate(self.gaz, KOPF + "Ein Angebot im Stadtbezirk Beuel.")
        self.assertEqual((rows, info["befund"]), ([], "nur einzelne Erwähnung eines Stadtbezirks"))
        rows, _ = volltext.locate(self.gaz, KOPF + "Ein Angebot in Beuel.", bv_bezirke={"Beuel"})
        self.assertEqual([r["level"] for r in rows], ["stadtbezirk"])

    def test_drei_stadtbezirke_sind_stadtweit(self):
        bv = {"Beuel", "Bad Godesberg", "Hardtberg"}   # in den Bezirksvertretungen beraten
        rows, info = volltext.locate(self.gaz, KOPF + "Zentren in Beuel, Bad Godesberg und Hardtberg.", bv)
        self.assertEqual((rows, info["befund"]), ([], "3 Stadtbezirke, stadtweit, nicht verortet"))
        rows, _ = volltext.locate(self.gaz, KOPF + "Zentren in Beuel und Hardtberg.", bv)
        self.assertEqual(sorted(r["name"] for r in rows), ["Beuel", "Hardtberg"])

    def test_titel_ohne_gemeinsamen_ort(self):
        for t in ["Tagesordnungspunkte in nichtöffentlicher Sitzung", "Tagesordnungspunkte der nicht öffentlichen Sitzung",
                  "Übersicht über die Beratung nichtöffentlicher Tagesordnungspunkte", "Wirtschaftsplan 2027 der bonnorange AöR",
                  "Jahresabschluss 2023 der Beethovenhalle GmbH"]:
            self.assertTrue(volltext.titel_ohne_ort(t), t)
        self.assertFalse(volltext.titel_ohne_ort("Spielplatz an der Endenicher Straße"))
        self.assertTrue(volltext.sammelliste("Punkte der nichtöffentlichen Sitzung"))
        self.assertFalse(volltext.sammelliste("Wirtschaftsplan 2027 der bonnorange AöR"))

    def test_eingaben_von_buergerinnen_nicht_aus_dem_volltext(self):
        self.assertFalse(volltext.allowed("Bürgerantrag § 24 GO - Öffentlich"))
        self.assertFalse(volltext.allowed("Anregungen und Beschwerden"))
        self.assertTrue(volltext.allowed("Stellungnahme der Verwaltung"))

    def test_folgevorlagen_von_buergerantraegen_nicht_aus_dem_volltext(self):
        # Code-Prüfung 24.10.2026: Stellungnahmen zu einem Bürgerantrag nennen oft dieselbe Anschrift
        U = "https://www.bonn.sitzung-online.de/oparl/papers/"
        papers = [{"id": U + "1", "reference": "231681", "paperType": "Bürgerantrag § 24 GO - Öffentlich", "name": "x",
                   "subordinatedPaper": [U + "2"]},
                  {"id": U + "2", "reference": "231681-12 ST", "paperType": "Stellungnahme der Verwaltung", "name": "y",
                   "superordinatedPaper": [U + "1"]},
                  {"id": U + "3", "reference": "250001", "paperType": "Beschlussvorlage", "name": "z"}]
        self.assertEqual(volltext.einwohner_kette(papers), {U + "1", U + "2"})

    def test_liste_vieler_ortsteile_wird_nicht_verortet(self):
        text = KOPF + ", ".join(["Endenich", "Duisdorf", "Lengsdorf", "Tannenbusch", "Beuel-Mitte", "Mehlem"])
        rows, info = volltext.locate(self.gaz, text)
        self.assertEqual(rows, [])
        self.assertTrue(info["befund"].startswith("Liste"))


if __name__ == "__main__":
    unittest.main()
