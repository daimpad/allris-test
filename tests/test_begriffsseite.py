"""Begriffe (pipeline/glossar.py, pipeline/begriffsseite.py; Entscheidungen 02.11.2026): alle Vorlagenarten der Daten
erklärt, Sprungmarken eindeutig, Seite begriffe/ und Akkordeon „Begriffe auf dieser Seite“, einfachere Wörter."""
import tempfile
import unittest
from pathlib import Path

from pipeline import begriffsseite, gebietsseiten, glossar

# Vorlagenarten in den Daten der Stadt (Abruf 02.11.2026)
ARTEN_DER_DATEN = [
    "Stellungnahme der Verwaltung", "Beschlussvorlage", "Mitteilungsvorlage", "Änderungsantrag", "Antrag", "Große Anfrage",
    "Bürgerantrag § 24 GO - Öffentlich", "Tagesordnungspunkte in nichtöffentlicher Sitzung", "Beschlussvorlage: Einleitung",
    "Anregungen und Beschwerden", "Dringlichkeitsantrag", "Informationsbrief", "Bürgerbrief", "Kleine Anfrage",
    "Dringlichkeitsentscheidung OB", "Einwohnerfrage", "Dringlichkeitsentscheidung BV", "Eilentscheidung HA",
    "Beschlussvorlage: Auftrag"]


class Glossar(unittest.TestCase):
    def setUp(self):
        self.g = glossar.glossar()
        self.anker = {b["anker"] for b in self.g["begriffe"]}

    def test_alle_vorlagenarten_erklaert(self):
        for art in ARTEN_DER_DATEN:
            self.assertIn(self.g["arten"].get(art), self.anker, art)

    def test_kuerzel_und_fundstelle(self):
        self.assertEqual(self.g["kuerzel"], {"ST": "st", "AA": "aa", "DA": "da"})
        for b in self.g["begriffe"]:
            self.assertTrue(b["erklaerung"] and b["fundstelle"], b["begriff"])
            self.assertIn(b["gruppe"], self.g["gruppen"])
        # aus den Daten erschlossene Erklärungen sind gekennzeichnet
        info = next(b for b in self.g["begriffe"] if b["begriff"] == "Informationsbrief")
        self.assertIn("erschlossen", info["fundstelle"])

    def test_einfachere_woerter(self):
        self.assertEqual(self.g["schritte"]["initiierung"], "Anstoß")
        self.assertEqual(self.g["schritte"]["vollzug"], "Umsetzung")
        self.assertEqual(set(glossar.SCHRITTE_TEXT), set(glossar.SCHRITTE))


class Seite(unittest.TestCase):
    def test_seite_mit_sprungmarken(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            self.assertEqual(begriffsseite.write(site, "https://example.org/", gebietsseiten._page), ["begriffe/"])
            html = (site / "begriffe" / "index.html").read_text()
        self.assertIn("<h1>Begriffe</h1>", html)
        for anker in ("stellungnahme-der-verwaltung", "st", "zur-kenntnis-genommen", "rolle-kenntnisnahme",
                      "stand-entschieden", "schritt-vollzug", "ansatz", "haushalt", "ergebnisse"):
            self.assertIn(f'id="{anker}"', html, anker)
        ids = [x.split('"')[0] for x in html.split(' id="')[1:]]
        self.assertEqual(len(ids), len(set(ids)), "Sprungmarken doppelt")
        self.assertIn("Fundstelle: § 60 Abs. 1 GO NRW", html)

    def test_akkordeon(self):
        html = begriffsseite.akkordeon(["Bürgerbrief", "zur Kenntnis genommen - mit Maßgabe", "offen", "Kenntnisnahme",
                                        None, "unbekannt"], "../../")
        self.assertIn('<a href="../../begriffe/#buergerbrief">Bürgerbrief</a>', html)
        self.assertIn('href="../../begriffe/#zur-kenntnis-genommen"', html)
        self.assertIn('href="../../begriffe/#mit-massgabe"', html)
        self.assertIn('href="../../begriffe/#stand-offen"', html)
        self.assertNotIn("rolle-kenntnisnahme", html)   # Rollen stehen nicht in den Listen der Seiten
        self.assertEqual(begriffsseite.akkordeon(["unbekannt"], "../"), "")

    def test_gebietsseite(self):
        p = {"reference": "261088", "name": "Bäume", "paper_type": "Informationsbrief", "stand": "beraten, ohne Entscheidung",
             "date": "2026-06-02", "themes": [], "web": None}
        html = gebietsseiten._area_body("Ortsteil", "Endenich", "Bonn", "ortsteil:endenich", [p], "../../")
        self.assertIn("Begriffe auf dieser Seite", html)
        self.assertIn("begriffe/#informationsbrief", html)
        self.assertIn("begriffe/#stand-beraten-ohne-entscheidung", html)


if __name__ == "__main__":
    unittest.main()
