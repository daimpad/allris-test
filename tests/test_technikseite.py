"""Seite technik/ (pipeline/technikseite.py): aus dem Repository erzeugt, jede Angabe mit Erklärung."""
import re
import unittest

from pipeline import config, technikseite as tk


class AusDemRepository(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.wfs = tk.workflows()
        cls.d = tk.daten("../")
        cls.html = tk.body(cls.d, "../")

    def test_jeder_workflow_und_schritt_erklaert(self):
        # kommt ein Workflow oder ein Schritt im Hauptlauf hinzu, braucht er eine Erklärung in technikseite.py
        for w in self.wfs:
            self.assertIn(w["datei"], tk.WORKFLOW_TEXT, w["datei"])
        pages = next(w for w in self.wfs if w["datei"] == "pages.yml")
        for s in pages["schritte"]:
            self.assertIn(s, tk.SCHRITTE, s)
        self.assertEqual(pages["schritte"][:2], ["fetch-papers", "fetch-organizations"])
        for k in config.SOURCES:
            self.assertIn(k, tk.QUELLEN, k)

    def test_zeiten_aus_den_workflows(self):
        pages = next(w for w in self.wfs if w["datei"] == "pages.yml")
        self.assertEqual(pages["crons"], ["17 4 * * *"])
        self.assertEqual(tk.cron_text("17 4 * * *"), "täglich 04:17 UTC")
        self.assertEqual(tk.cron_text("41 6 * * 1"), "montags 06:41 UTC")
        self.assertEqual(tk.cron_text("23 3 7 1,4,7,10 *"), "am 7. Januar, April, Juli, Oktober um 03:23 UTC")
        self.assertEqual(tk.bonn("17 4 * * *"), "in Bonn 05:17 Uhr, im Sommer 06:17 Uhr")
        self.assertIn("nach jedem Hauptlauf", tk.ausloeser_text(next(w for w in self.wfs if w["datei"] == "live.yml")))
        self.assertIn("Ohne festen Zeitpunkt", self.html)

    def test_jeder_kasten_hat_einen_eintrag(self):
        ziele = set(re.findall(r'<a href="#(tk-[^"]+)" class="tk-box', self.html))
        ziele |= set(re.findall(r'<a class="tk-box" href="#(tk-[^"]+)"', self.html))
        eintraege = re.findall(r'<li id="(tk-[^"]+)"', self.html)
        self.assertEqual(len(eintraege), len(set(eintraege)), "Einträge eindeutig")
        self.assertTrue(ziele)
        self.assertEqual(ziele - set(eintraege), set())

    def test_vier_grafiken_breit_und_hoch(self):
        for anker in ("ueberblick", "datenfluss", "zeitplan", "technik"):
            teil = self.html.split(f'<h2 id="{anker}">')[1].split("<h2")[0]
            self.assertEqual(teil.count('<svg class="tk-svg hh-breit"'), 1, anker)
            self.assertEqual(teil.count('<svg class="tk-svg hh-hoch"'), 1, anker)
        ids = re.findall(r'<marker id="([^"]+)"', self.html)
        self.assertEqual(len(ids), len(set(ids)))

    def test_versionen(self):
        v = tk.versionen()
        self.assertTrue(re.fullmatch(r"\d+\.\d+\.\d+", v["leaflet"]))
        self.assertIn("shapely", v["pakete"])
        for p in v["pakete"]:
            self.assertIn(p, tk.PAKET_TEXT, p)
        self.assertIn("Playwright " + v["browser"]["playwright"], self.html)


if __name__ == "__main__":
    unittest.main()
