"""Seite einfach/ (pipeline/einfachseite.py; Entscheidungen 02.11.2026): acht Abschnitte, kurze Sätze, Fundstellen für
Fachleute, Wörter mit gleichem Sinn wie das Glossar, keine Bewertung."""
import re
import tempfile
import unittest
from pathlib import Path

from pipeline import einfachseite, gebietsseiten


class Einfach(unittest.TestCase):
    def setUp(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            self.assertEqual(einfachseite.write(site, "https://example.org/", gebietsseiten._page), ["einfach/"])
            self.html = (site / "einfach" / "index.html").read_text()

    def test_acht_abschnitte(self):
        ids = re.findall(r'<h2 id="([a-z]+)">', self.html)
        self.assertEqual(ids, ["was", "wer", "ablauf", "woerter", "benutzen", "mitmachen", "grenzen", "kontakt"])
        self.assertIn("<h1>Die RIS-Karte in Einfacher Sprache</h1>", self.html)

    def test_kurze_saetze_und_umfang(self):
        teil = self.html.split('<div class="einfach">')[1].split("</div>")[0]
        text = re.sub(r"<[^>]+>", " ", teil)
        woerter = [w for w in text.split() if re.search(r"\w", w)]
        self.assertTrue(550 <= len(woerter) <= 950, len(woerter))
        saetze = [s for s in re.split(r"(?<=[.!?])\s+", " ".join(woerter)) if s.strip()]
        self.assertLess(sum(len(s.split()) for s in saetze) / len(saetze), 11)

    def test_fundstellen_und_grenzen(self):
        self.assertEqual(self.html.count('class="einfach-fach"'), 5)
        for f in ("§ 24 GO NRW", "§ 48 GO NRW", "§§ 36, 37 GO NRW", "§ 62 GO NRW"):
            self.assertIn(f, self.html)
        self.assertIn("Das heißt nicht „abgelehnt“", self.html)   # Vereinfachung ändert den Sinn nicht
        self.assertIn("nicht in Leichter Sprache", self.html)
        self.assertIn('href="../begriffe/"', self.html)

    def test_fuss_aller_seiten(self):
        self.assertIn('<a href="../einfach/">Einfache Sprache</a>', self.html)


if __name__ == "__main__":
    unittest.main()
