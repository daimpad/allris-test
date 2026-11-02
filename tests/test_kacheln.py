"""Graue Kartenkacheln: Kachelbereich gleich in Skript und Seite, Grauwerte wie die bisherige graue Ansicht."""
import importlib.util
import json
import pathlib
import re
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
KACHELN = ROOT / "pipeline" / "kacheln"
sys.path.insert(0, str(KACHELN))
import rahmen  # noqa: E402

HAS_PIL = importlib.util.find_spec("PIL") is not None


class TestRahmen(unittest.TestCase):
    def test_seite_gleich_skript(self):
        js = (ROOT / "site" / "app.js").read_text(encoding="utf-8")
        m = re.search(r"const KACHEL_RAHMEN = (\{[^;]+\});", js)
        self.assertIsNotNone(m)
        seite = {int(k): v for k, v in json.loads(re.sub(r"(\d+):", r'"\1":', m.group(1))).items()}
        skript = {z: list(rahmen.kachelbereich(z)) for z in range(rahmen.ZMIN, rahmen.ZMAX + 1)}
        self.assertEqual(seite, skript)

    def test_bonn_im_rahmen(self):
        for z in range(rahmen.ZMIN, rahmen.ZMAX + 1):
            x1, y1, x2, y2 = rahmen.kachelbereich(z)
            for lon, lat in ((7.0225, 50.6327), (7.2107, 50.7744), (7.0982, 50.7374)):
                x, y = rahmen.kachel(lon, lat, z)
                self.assertTrue(x1 <= x <= x2 and y1 <= y <= y2, (z, lon, lat))

    def test_rand_waechst_nach_aussen(self):
        self.assertGreater(rahmen.rand(12)[0], rahmen.rand(14)[0])
        self.assertGreater(rahmen.rand(14)[0], rahmen.rand(16)[0])


@unittest.skipUnless(HAS_PIL, "Pillow fehlt")
class TestZerlegen(unittest.TestCase):
    def setUp(self):
        import zerlegen
        self.z = zerlegen

    def test_grauwert_wie_css_filter(self):
        # Land der Gestaltung „light“ (#e2dfda, Leuchtdichte 223) → Stufe 14 (#eee, Hintergrund der Karte in style.css)
        self.assertEqual(self.z.TABELLE[223], 14)
        self.assertEqual(self.z.TABELLE[255], 15)
        self.assertEqual(self.z.TABELLE[0], 1)  # contrast(.9) hebt Schwarz an
        self.assertEqual(self.z.TABELLE, sorted(self.z.TABELLE))

    def test_zerlegen_block(self):
        from PIL import Image, ImageDraw
        with tempfile.TemporaryDirectory() as d:
            d = pathlib.Path(d)
            (d / "bloecke").mkdir()
            im = Image.new("RGB", (10 * 256, 10 * 256), (226, 223, 218))
            ImageDraw.Draw(im).line((0, 0, 10 * 256, 10 * 256), fill=(120, 120, 120), width=40)
            im.save(d / "bloecke" / "16_100_200.png")
            (d / "bloecke" / "bloecke.tsv").write_text("16\t100\t200\t101\t201\n")
            (d / "stand.json").write_text(json.dumps({"build": "20261102.pmtiles", "osm_stand": "2026-11-02T04:00:00Z"}))
            self.z.main(str(d / "bloecke"), str(d / "kacheln"), str(d / "stand.json"))
            kacheln = sorted(p.relative_to(d / "kacheln").as_posix() for p in (d / "kacheln").rglob("*.png"))
            self.assertEqual(kacheln, ["16/100/200.png", "16/100/201.png", "16/101/200.png", "16/101/201.png"])
            k = Image.open(d / "kacheln" / "16" / "100" / "200.png")
            self.assertEqual(k.mode, "P")
            self.assertLessEqual(len(k.getcolors()), 16)
            stand = json.loads((d / "kacheln" / "stand.json").read_text())
            self.assertEqual(stand["rasterkacheln"], {"16": 4})
            self.assertIn("ODbL", (d / "kacheln" / "LIZENZ.md").read_text())


if __name__ == "__main__":
    unittest.main()
