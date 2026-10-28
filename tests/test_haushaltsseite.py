"""Seite haushalt/ (pipeline/haushaltsseite.py): Treemap der Produktbereiche, Ebenen 2 (Produktgruppen) und 3
(Aufwandsarten einer Produktgruppe)."""
import os
import re
import unittest
from unittest import mock

from pipeline import config, haushaltsseite as hs


def daten(ebenen):
    """Daten der Seite mit oder ohne Ebenen 2 und 3, unabhängig von Freigabe und Umgebung."""
    with mock.patch.object(hs.haushaltsplan, "EBENEN_FREIGEGEBEN", ebenen), \
            mock.patch.dict(os.environ, {"HAUSHALT_EBENEN": ""}):
        return hs.daten()


def abschnitt(html, ziel):
    return html.split(f'<section id="{ziel}"')[1].split("</section>")[0]


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

    def test_zeilen_und_betraege(self):
        self.assertEqual(hs._zeilen("Kinder-, Jugend- und Familienhilfe", 20), ["Kinder-, Jugend- und", "Familienhilfe"])
        self.assertIsNone(hs._zeilen("Natur- und Landschaftspflege", 12))
        self.assertEqual(hs._euro(-84508), "−84.508 €")
        self.assertEqual(hs._betrag(5000), "5.000 €")   # sonst 0,0 Mio. €
        self.assertEqual(hs._betrag(140000), "0,1 Mio. €")
        self.assertEqual(hs._anker("1.04.07"), "pg-1-04-07")


class Seite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = daten(False)
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

    def test_freigegeben(self):
        self.assertTrue(hs.haushaltsplan.EBENEN_FREIGEGEBEN)   # Prüfbogen im Gespräch freigegeben 28.10.2026

    def test_ohne_freigabe_nur_ebene_1(self):
        self.assertFalse(self.d["zoom"])
        self.assertNotIn("hh-ebene", self.html)
        self.assertNotIn("#zoom-", self.html)
        self.assertNotIn("#pg-", self.html)
        self.assertIn("Die Seite zeigt eine Ebene", self.html)
        self.assertEqual(hs.stil(self.d), "")

    def test_vorschau_ueber_umgebungsvariable(self):
        with mock.patch.object(hs.haushaltsplan, "EBENEN_FREIGEGEBEN", False):
            with mock.patch.dict(os.environ, {"HAUSHALT_EBENEN": "vorschau"}):
                self.assertTrue(hs.ebenen_an())
            with mock.patch.dict(os.environ, {"HAUSHALT_EBENEN": "ja"}):
                self.assertFalse(hs.ebenen_an())

    def test_themenseiten_verlinkt(self):
        for pfad in ("thema/kultur-und-haushalt/", "thema/schule-und-bildung/", "thema/klima-und-umwelt/"):
            self.assertIn(f'href="../{pfad}"', self.html)


class Ebenen(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = daten(True)
        cls.html = hs.body(cls.d, "../")
        cls.pb = {p["pb"]: p for p in cls.d["produktbereiche"]}

    def test_ebene_1_fuehrt_zu_ebene_2_tabelle_bleibt(self):
        self.assertEqual(len(re.findall(r'<a href="#zoom-\d\d" aria-label=', self.html)), 6 * 17)
        self.assertNotIn('<a href="#pb-', self.html)
        self.assertEqual(len(set(re.findall(r'<tr id="(pb-\d\d)"', self.html))), 17)   # Sprungziele der Themenseiten
        self.assertEqual(self.html.count('<a href="#zoom-01">Produktgruppen und Aufwandsarten</a>'), 1)

    def test_abschnitte_in_den_karten_und_ziele_vorhanden(self):
        karten = self.html.split('<div class="hh-karten">')[1].split('<h2 id="tabelle">')[0]
        self.assertEqual(re.findall(r'<section id="zoom-(\d\d)" class="hh-ebene"', karten), [f"{i:02d}" for i in range(1, 18)])
        ids = re.findall(r'id="([^"]+)"', self.html)
        self.assertEqual(len(set(ids)), len(ids))
        ziele = set(re.findall(r'href="#([^"]+)"', self.html))
        self.assertFalse(ziele - set(ids), "jeder Sprung hat ein Ziel")
        gruppen = re.findall(r'<section id="(pg-1-\d\d-\d\d)" class="hh-ebene hh-pg"', karten)
        self.assertEqual(len(gruppen), sum(hs._mit_werten(g, self.d["ansichten"]) for p in self.pb.values()
                                           for g in p["produktgruppen"]))
        self.assertGreater(len(gruppen), 130)

    def test_ebene_2_produktgruppen(self):
        z = abschnitt(self.html, "zoom-04")
        self.assertIn('<a href="#produktbereiche">Alle Produktbereiche</a> › <span aria-current="location">04 Kultur und Wissenschaft</span>', z)
        self.assertIn(">Produktbereich 04 Kultur und Wissenschaft</h2>", z)
        self.assertEqual(re.findall(r'<figure class="hh-ansicht (hh-v\d)">', z), ["hh-v0", "hh-v1", "hh-v2"])
        self.assertEqual(z.count("<svg "), 6)
        self.assertEqual(z.count('hh-balken" aria-hidden="true"'), 3)   # Aufwandsarten des Produktbereichs
        plan26 = re.search(r'<figure class="hh-ansicht hh-v0">(.*?)</figure>', z).group(1)
        self.assertIn("<title>1.04.07 Stadtarchiv: 3,2 Mio. €, 3,4 % (Plan 2026)</title>", plan26)
        self.assertEqual(plan26.count('<a href="#pg-'), 2 * 12)   # 14 Produktgruppen, zwei mit 0 €
        self.assertNotIn("#pg-1-04-13", z)   # 0 € in allen Ansichten: nur in der Tabelle, ohne Ebene 3
        self.assertIn("1.04.13 Internationale Wissenschaft", z)
        self.assertIn("Name in Haushaltsplan 2023/2024: Z. f. Stadtgesch. u. Erinnerungskulturen", z)
        self.assertIn("Name in Haushaltsplan 2023/2024: Stadtmuseum", z)
        self.assertIn("Begriffe oben unter „So lesen Sie die Zahlen“.", z)
        self.assertNotIn("Kontenarten", z)   # Erklärung einmal im Akkordeon, nicht in jedem Abschnitt
        self.assertNotIn("2027", z)   # keine Finanzplanung

    def test_ebene_3_aufwandsarten_der_produktgruppe(self):
        g = abschnitt(self.html, "pg-1-04-07")
        self.assertIn('<a href="#produktbereiche">Alle Produktbereiche</a> › <a href="#zoom-04">04 Kultur und Wissenschaft</a> › '
                      '<span aria-current="location">1.04.07 Stadtarchiv</span>', g)
        self.assertIn(">Produktgruppe 1.04.07 Stadtarchiv</h2>", g)
        self.assertIn("Amt 41-2 · Name in Haushaltsplan 2023/2024: Z. f. Stadtgesch. u. Erinnerungskulturen", g)
        self.assertNotIn("<svg", g)   # keine Treemap im HTML; die Kacheln zeichnet site/haushalt.js aus den Balken
        self.assertEqual(g.count('hh-balken" aria-hidden="true"'), 3)
        self.assertIn('<i class="hh-f11" style="width:', g)
        self.assertEqual(len(re.findall(r'<i class="hh-f\d\d" style="width:[\d.]+%" data-b="\d+"></i>', g)), 15)
        self.assertNotIn("Kontenarten", g)
        self.assertEqual(re.findall(r'<tr class="hh-z(\d\d)">', g), ["11", "12", "13", "14", "15", "16"])
        self.assertIn('PB04.pdf#page=29">Haushaltsplan 2025/2026, PB04.pdf, S. 29</a>', g)
        self.assertNotIn("verantwortlich", g)
        # 1.01.29: dass dort Gebäude der Schulen und Bühnen bewirtschaftet werden, belegt das PDF nicht – kein Zusatz
        self.assertNotRegex(abschnitt(self.html, "pg-1-01-29"), r"Schul|Bühne")

    def test_negative_werte_ohne_flaeche_und_balkenstueck(self):
        z = abschnitt(self.html, "zoom-09")
        self.assertIn("<td>−84.508 €<br><small>negativ, ohne Fläche</small></td>", z)
        ist = re.search(r'<div class="hh-ansicht hh-v2 hh-balken"[^>]*>(.*?)</div>', z).group(1)
        self.assertNotIn("hh-f15", ist)   # Transferaufwendungen im Ist 2023 negativ
        self.assertIn("Negativ sind: Transferaufwendungen im Ist 2023 (−84.508 €)", z)
        g = abschnitt(self.html, "pg-1-09-04")
        self.assertIn("<td>−86.000 €<br><small>negativ, ohne Fläche</small></td>", g)
        self.assertNotIn("hh-f15", re.search(r'<div class="hh-ansicht hh-v2 hh-balken"[^>]*>(.*?)</div>', g).group(1))
        self.assertIn("Negativ sind: Transferaufwendungen im Ist 2023 (−86.000 €)", g)

    def test_erklaerungen_einmal_im_akkordeon(self):
        oben = self.html.split('<div class="hh-wahl"')[0]
        self.assertIn('<details class="hh-mehr" id="lesen">', oben)
        self.assertNotIn("<details open", self.html)   # alle Akkordeons zugeklappt
        self.assertEqual(self.html.count("Kontenarten, keine Aufgaben"), 1)
        self.assertIn("<summary>Was diese Seite nicht zeigt</summary>", self.html)
        self.assertIn("<summary>Quellen, Prüfung und Lizenz</summary>", self.html)
        self.assertIn('<script src="../haushalt.js" defer></script>', hs.stil(self.d))

    def test_leere_zeilen(self):
        z = abschnitt(self.html, "zoom-16")
        zeile = re.search(r'<tr class="hh-z11">.*?</tr>', z).group(0)
        self.assertEqual(zeile.count("<td>leer</td>"), 3)
        self.assertNotIn("hh-f11", z)   # kein Balkenstück für Personalaufwendungen

    def test_summen_je_ansicht(self):
        for p in self.pb.values():
            for a in self.d["ansichten"]:
                z17 = p[a["art"]][a["jahr"]]["betrag"]
                self.assertEqual(sum(t[a["art"]][a["jahr"]]["betrag"] for t in p["aufwandsarten"]), z17)
                pgs = sum(g[a["art"]][a["jahr"]]["betrag"] for g in p["produktgruppen"] if a["jahr"] in g[a["art"]])
                self.assertLessEqual(abs(pgs - z17), hs.haushaltsplan.TOLERANZ, (p["pb"], a["titel"]))
                for g in p["produktgruppen"]:
                    self.assertEqual(sum(t[a["art"]][a["jahr"]]["betrag"] for t in g["aufwandsarten"]),
                                     g[a["art"]][a["jahr"]]["betrag"])

    def test_groesse_und_spaltennamen(self):
        self.assertLess(len(self.html.encode()), 800_000)   # Vorgabe: Seite höchstens etwa 800 KB, ohne Skript
        self.assertIn('td:nth-of-type(1)::before { content: "Ist 2023: "; }', hs.stil(self.d))

    def test_farben_fest(self):
        css = (config.ROOT / "site" / "page.css").read_text(encoding="utf-8")
        farben = dict(re.findall(r"\.hh-f(1[1-6]), \.hh-z1[1-6] > th::before \{ background: (#[0-9a-f]{6}); \}", css))
        self.assertEqual(sorted(farben), ["11", "12", "13", "14", "15", "16"])
        self.assertEqual(len(set(farben.values())), 6)


if __name__ == "__main__":
    unittest.main()
