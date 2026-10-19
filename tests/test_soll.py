import json
import re
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from pipeline import soll


class Modell(unittest.TestCase):
    def setUp(self):
        self.m = soll.Modell()

    def test_korrekturen_angewandt(self):
        vii = next(a for a in self.m.zusto["ausschuesse"] if a["nr"] == "VII")
        r = next(x for x in vii["rechte"] if x["nr"] == "2.16")
        self.assertTrue(r["an_bezirksvertretung"])
        self.assertIn("Stand 9.7.2026", r["korrigiert"])
        bv = self.m.verfahren["beschlussvorlage"]
        self.assertIn("Unterausschuss", next(a for a in bv["ausgaenge"] if a["wenn"] == "Kosten ohne Haushaltsmittel")["dann"])

    def test_quelle_bleibt_unveraendert(self):
        raw = json.loads((soll.SOLL / "zustaendigkeitsordnung.json").read_text(encoding="utf-8"))
        vii = next(a for a in raw["ausschuesse"] if a["nr"] == "VII")
        self.assertFalse(next(x for x in vii["rechte"] if x["nr"] == "2.16")["an_bezirksvertretung"])

    def test_ergaenzungen_gekennzeichnet_und_belegt(self):
        eigen = [s for v in self.m.verfahren.values() for s in v["schritte"] if s.get("eigen")]
        self.assertGreaterEqual(len(eigen), 9)
        for s in eigen:
            self.assertRegex(s["beleg"], r"(GeschO|BezS|HS|GO NRW|BauGB) ")
        self.assertEqual(self.m.bahnen("grosse-anfrage"), {"rat", "aus", "bv"})
        self.assertEqual(self.m.bahnen("mitteilung"), {"rat", "aus", "bv"})
        self.assertEqual(self.m.bahnen("unbekannt"), set())

    def test_korrektur_passt_nicht_zur_quelle(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for f in soll.SOLL.glob("*.json"):
                shutil.copy(f, base / f.name)
            extra = json.loads((base / "ergaenzungen.json").read_text(encoding="utf-8"))
            extra["korrekturen"][0]["alt"] = True
            (base / "ergaenzungen.json").write_text(json.dumps(extra), encoding="utf-8")
            with self.assertRaises(ValueError):
                soll.Modell(base)


class Zuordnung(unittest.TestCase):
    def test_regeln(self):
        a = soll.assign
        self.assertEqual(a("Bürgerantrag § 24 GO - Öffentlich", "x", set(), set())[:2], ("buergerantrag", "hoch"))
        self.assertEqual(a("Antrag", "x", {"Bezirksvertretungen"}, set())[0], "antrag-bv")
        self.assertEqual(a("Antrag", "x", {"Ratsgremien"}, set())[0], "antrag-rat")
        self.assertEqual(a("Antrag", "Antrag der Bezirksfraktion", set(), set())[:2], ("antrag-bv", "mittel"))
        self.assertEqual(a("Beschlussvorlage", "Aufstellung des Bebauungsplans 6122-1", set(), set())[:2], ("bauleitplanung", "hoch"))
        self.assertEqual(a("Beschlussvorlage", "x", {"Ratsgremien"}, {"Ratsgremien"})[0], "ausschuss-entscheidung")
        self.assertEqual(a("Beschlussvorlage", "x", {"Rat"}, {"Rat"})[:2], ("beschlussvorlage", "hoch"))
        self.assertEqual(a("Dringlichkeitsentscheidung OB", "x", set(), set())[0], "dringlichkeitsentscheidung")
        self.assertEqual(a("Bürgerbrief", "x", set(), set(), {"Bürgerbrief": "…"})[0], None)

    def test_abgleich(self):
        db = sqlite3.connect(":memory:")
        db.executescript("""
            CREATE TABLE paper (id, reference, name, paper_type, date);
            CREATE TABLE organization (id, classification);
            CREATE TABLE consultation (paper_id, organization_id, role);
            INSERT INTO organization VALUES ('rat', 'Rat'), ('bv', 'Bezirksvertretungen'), ('aus', 'Ratsgremien');
            INSERT INTO paper VALUES ('p1', '261000', 'Antrag A', 'Antrag', '2026-01-01'),
                                     ('p2', '261000-01 ST', 'Stellungnahme', 'Stellungnahme der Verwaltung', '2026-02-01'),
                                     ('p3', '261001', 'Frage', 'Einwohnerfrage', '2026-01-02'),
                                     ('p4', '261002', 'Brief', 'Bürgerbrief', '2026-01-03');
            INSERT INTO consultation VALUES ('p1', 'aus', 'Empfehlung'), ('p2', 'rat', 'Entscheidung'), ('p3', 'rat', 'Kenntnisnahme');
        """)
        rows = {r["stammnummer"]: r for r in soll.abgleich(db, soll.Modell())}
        self.assertEqual((rows["261000"]["verfahren"], rows["261000"]["dokumente"], rows["261000"]["passung"]), ("antrag-rat", 2, "passt"))
        self.assertEqual((rows["261001"]["passung"], rows["261001"]["abweichung"]), ("weicht ab", "rat"))
        self.assertEqual(rows["261002"]["passung"], "ohne Soll")


if __name__ == "__main__":
    unittest.main()
