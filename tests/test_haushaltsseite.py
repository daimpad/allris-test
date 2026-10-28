"""Seite haushalt/ (pipeline/haushaltsseite.py): Treemap der Produktbereiche."""
import re
import unittest

from pipeline import haushaltsseite as hs


class Treemap(unittest.TestCase):
    def test_flaechen_proportional_und_im_rechteck(self):
        werte = [372, 304, 304, 167, 137, 135, 124, 93, 85, 38, 35, 33, 18, 18, 10, 9, 1]
        rects = hs.squarify(werte, 0, 0, 1000, 560)
        self.assertEqual(len(rects), len(werte))
        for v, (x, y, w, h) in zip(werte, rects):
            self.assertAlmostEqual(w * h, v * 1000 * 560 / sum(werte), places=6)
            self.assertTrue(-1e-6 <= x and x + w <= 1000 + 1e-6 and -1e-6 <= y and y + h <= 560 + 1e-6)
        self.assertAlmostEqual(sum(w * h for *_, w, h in rects), 1000 * 560, places=3)

    def test_beispiel_aus_der_literatur(self):
        # Bruls, Huizing, van Wijk (2000), Abb. 4: 6, 6, 4, 3, 2, 2, 1 in einem Rechteck 6 × 4
        rects = hs.squarify([6, 6, 4, 3, 2, 2, 1], 0, 0, 6, 4)
        self.assertEqual([tuple(round(v, 3) for v in r) for r in rects[:2]], [(0, 0, 3, 2), (0, 2, 3, 2)])

    def test_zeilen(self):
        self.assertEqual(hs._zeilen("Kinder-, Jugend- und Familienhilfe", 20), ["Kinder-, Jugend- und", "Familienhilfe"])
        self.assertIsNone(hs._zeilen("Natur- und Landschaftspflege", 12))


class Seite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = hs.daten()
        cls.html = hs.body(cls.d, "../")

    def test_ansichten_und_summen(self):
        self.assertEqual([a["titel"] for a in self.d["ansichten"]], ["Plan 2026", "Plan 2025", "Ist 2023"])
        # Plan 2025: Summe der Produktbereiche = Gesamtergebnisplan (haushalt/phase0/BERICHT.md: 1.797,0 Mio. €)
        self.assertAlmostEqual(self.d["ansichten"][1]["summe"] / 1e6, 1797.0, delta=0.1)
        self.assertEqual(len(self.d["produktbereiche"]), 17)

    def test_je_ansicht_und_format_alle_produktbereiche(self):
        self.assertEqual(self.html.count('<svg class="hh-svg'), 6)
        self.assertEqual(len(re.findall(r'<a href="#pb-\d\d" aria-label=', self.html)), 6 * 17)
        self.assertEqual(len(set(re.findall(r'<tr id="(pb-\d\d)"', self.html))), 17)
        self.assertNotIn("2027", self.html.split("Was diese Seite nicht zeigt")[0])   # keine Finanzplanung

    def test_themenseiten_verlinkt(self):
        for pfad in ("thema/kultur-und-haushalt/", "thema/schule-und-bildung/", "thema/klima-und-umwelt/"):
            self.assertIn(f'href="../{pfad}"', self.html)


if __name__ == "__main__":
    unittest.main()
