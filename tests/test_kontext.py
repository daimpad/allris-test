"""Kontextdaten je Ortsteil (kontext/KONZEPT.md, Phase 1)."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from pipeline import config, kontext


class Median(unittest.TestCase):
    def test_gewichteter_median(self):
        self.assertEqual(kontext._wmedian([(500, 1), (700, 1), (900, 5)]), 900)
        self.assertEqual(kontext._wmedian([(500, 3), (700, 1), (900, 1)]), 500)
        self.assertIsNone(kontext._wmedian([]))

    def test_gleichstand_ergibt_mittel(self):
        self.assertEqual(kontext._wmedian([(460, 0.5), (770, 0.5)]), 615)
        self.assertEqual(kontext._wmedian([(500, 1), (600, 1), (700, 2)]), 650)


class Kennzahlen(unittest.TestCase):
    """Mit den Ausschnitten im Repository (data/kontext/)."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        with mock.patch.object(config, "EXPORT", Path(cls.tmp.name)):
            kontext.write()
        cls.path = Path(cls.tmp.name) / "bonn" / kontext.OUT
        cls.doc = json.loads(cls.path.read_text())

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_einwohner_wie_zensus(self):
        self.assertEqual(self.doc["bonn"]["einwohner"], 321351)
        self.assertEqual(sum(v["einwohner"] for v in self.doc["ortsteile"].values()), 321351)
        self.assertEqual(sum(v["einwohner"] for v in self.doc["bezirke"].values()), 321351)
        self.assertEqual(len(self.doc["ortsteile"]), 51)
        self.assertEqual(set(self.doc["stadtbezirk_je_ortsteil"]), set(self.doc["ortsteile"]))
        self.assertEqual(self.doc["stadtbezirk_je_ortsteil"]["Endenich"], "Bonn")

    def test_reihenfolge_fuer_den_steckbrief(self):
        self.assertEqual(self.doc["meta"]["reihenfolge"], list(kontext.KENNZAHLEN))
        self.assertEqual(self.doc["meta"]["reihenfolge"][0], "einwohner")

    def test_wahlbeteiligung(self):
        # ganz Bonn amtlich (Heft 3: 160.220 von 247.052); Ortsteile geschätzt in ganzen Prozent
        self.assertEqual(self.doc["bonn"]["wahlbeteiligung"], 64.9)
        ohne = sorted(n for n, v in self.doc["ortsteile"].items() if v.get("wahlbeteiligung") is None)
        self.assertEqual(ohne, ["Beuel-Ost", "Hardthöhe", "Hoholz"])   # ohne eigenen Stimmbezirk (wahlen/phase0)
        werte = [v["wahlbeteiligung"] for v in self.doc["ortsteile"].values() if v.get("wahlbeteiligung") is not None]
        self.assertTrue(all(isinstance(w, int) and 35 <= w <= 85 for w in werte))
        self.assertEqual(set(self.doc["bezirke"]), {n for n, v in self.doc["bezirke"].items() if v.get("wahlbeteiligung")})
        self.assertEqual(self.doc["meta"]["kennzahlen"]["wahlbeteiligung"]["ohne_wert"], "ohne eigenen Stimmbezirk")
        self.assertIn("uebergang", self.doc["meta"]["quellen"]["wahl2025"])
        self.assertEqual(kontext.pruefen(self.path), [])

    def test_kleine_ortsteile_ohne_anteile(self):
        hardthoehe = self.doc["ortsteile"]["Hardthöhe"]
        self.assertLess(hardthoehe["einwohner"], kontext.MIN_EINWOHNER)
        self.assertFalse(kontext.ANTEILE & set(hardthoehe))

    def test_werte_im_plausiblen_bereich(self):
        for n, v in self.doc["ortsteile"].items():
            if v["einwohner"] < kontext.MIN_EINWOHNER:
                continue
            with self.subTest(ortsteil=n):
                self.assertTrue(0 <= v["unter_18"] <= 40 and 0 <= v["ab_65"] <= 50)
                self.assertTrue(5 <= v["miete"] <= 20)
                self.assertTrue(100 <= v["bodenrichtwert"] <= 2500)
                self.assertTrue(0 <= v["hitze"] <= 100 and 0 <= v["ueberschwemmung"] <= 100)

    def test_jede_kennzahl_mit_quelle_lizenz_und_stand(self):
        for k, d in self.doc["meta"]["kennzahlen"].items():
            q = self.doc["meta"]["quellen"][d["quelle"]]
            self.assertTrue(q["lizenz"] and q["stand"], k)
        self.assertEqual(kontext.pruefen(self.path), [])

    def test_pruefung_meldet_fehler(self):
        doc = json.loads(self.path.read_text())
        doc["bonn"]["einwohner"] = 250000
        doc["meta"]["quellen"]["kitas"]["lizenz"] = ""
        doc["ortsteile"]["Hardthöhe"]["miete"] = 5.0
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(doc, f)
        befunde = kontext.pruefen(f.name)
        Path(f.name).unlink()
        self.assertEqual(len(befunde), 5)   # Einwohner, Lizenz der Kitas (drei Kennzahlen), Hardthöhe

    def test_zuschaltbare_flaechen_fuer_die_karte(self):
        d = Path(self.tmp.name) / "bonn" / "flaechen"
        uesg = json.loads((d / "ueberschwemmung.json").read_text())
        self.assertEqual({f["properties"]["art"] for f in uesg["features"]}, {"festgesetzt", "vorläufig gesichert"})
        brw = json.loads((d / "bodenrichtwerte.json").read_text())
        self.assertEqual(len(brw["features"]), 317)
        self.assertEqual(set(brw["features"][0]["properties"]), {"zone", "brw", "ergaenzung", "stichtag"})
        self.assertLess((d / "ueberschwemmung.json").stat().st_size + (d / "bodenrichtwerte.json").stat().st_size, 1_000_000)

    def test_ausgabe_ohne_zeitstempel_und_gleich_bei_wiederholung(self):
        before = self.path.read_bytes()
        with mock.patch.object(config, "EXPORT", Path(self.tmp.name)):
            kontext.write()
        self.assertEqual(self.path.read_bytes(), before)
        self.assertNotIn("abgerufen", before.decode())


class OhneAusschnitte(unittest.TestCase):
    def test_schritt_wird_uebersprungen(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.object(kontext, "ZENSUS", Path(d) / "fehlt.tsv"), \
                mock.patch.object(config, "EXPORT", Path(d)):
            kontext.write()
            self.assertFalse((Path(d) / "bonn" / kontext.OUT).exists())


if __name__ == "__main__":
    unittest.main()
