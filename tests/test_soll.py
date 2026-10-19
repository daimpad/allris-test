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

    def test_anrede_der_regeln(self):
        self.assertEqual(len(self.m.regeln), 14)
        for r in self.m.regeln:
            self.assertNotRegex(r["was"], r"\b(du|dein|deine|dir|dich)\b", r["id"])
        self.assertTrue(next(r for r in self.m.regeln if r["id"] == "einwohnerfrage")["umformuliert"])
        raw = json.loads((soll.SOLL / "verfahren.json").read_text(encoding="utf-8"))
        self.assertTrue(next(r for r in raw["einfluss_regeln"] if r["id"] == "einwohnerfrage")["was"].startswith("Stell selbst"))
        d = soll.site_data(self.m)
        self.assertEqual([r["id"] for r in d["mitwirken"]], [r["id"] for r in raw["einfluss_regeln"]])
        self.assertTrue(next(r for r in d["mitwirken"] if r["id"] == "sitzung-besuchen")["links"])
        # ergänzte Bedingung: Offenlage-Hinweis nur bei offenen Verfahren (Quelle ohne Status-Bedingung)
        self.assertEqual(next(r for r in d["mitwirken"] if r["id"] == "offenlage")["wenn"]["status"], ["offen", "vertagt"])
        self.assertNotIn("status", next(r for r in raw["einfluss_regeln"] if r["id"] == "offenlage")["wenn"])
        # erweiterter Ausschluss: kein Hinweis auf einen eigenen Bürgerantrag bei Bürgeranträgen
        w = next(r for r in d["mitwirken"] if r["id"] == "eigener-buergerantrag")["wenn"]["nicht_verfahren"]
        self.assertEqual(w, ["nichtoeffentlich", "dringlichkeitsentscheidung", "buergerantrag"])

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
            extra["korrekturen"][0]["alt"] = False
            extra["anrede"]["regeln"][0]["alt"] = "anderer Wortlaut"
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

    def _db(self):
        db = sqlite3.connect(":memory:")
        db.executescript("""
            CREATE TABLE paper (id, reference, name, paper_type, date);
            CREATE TABLE organization (id, classification);
            CREATE TABLE consultation (paper_id, organization_id, role);
            INSERT INTO organization VALUES ('rat', 'Rat'), ('bv', 'Bezirksvertretungen'), ('aus', 'Ratsgremien'),
                                            ('beirat', 'Beiräte und Kommissionen');
            INSERT INTO paper VALUES ('p1', '261000', 'Antrag A', 'Antrag', '2026-01-01'),
                                     ('p2', '261000-01 ST', 'Stellungnahme', 'Stellungnahme der Verwaltung', '2026-02-01'),
                                     ('p3', '261001', 'Frage', 'Einwohnerfrage', '2026-01-02'),
                                     ('p4', '261002', 'Brief', 'Bürgerbrief', '2026-01-03'),
                                     ('p5', '261003', 'Info', 'Mitteilungsvorlage', '2026-01-04'),
                                     ('p6', '261004', 'Info', 'Mitteilungsvorlage', '2026-01-05'),
                                     ('p7', '261005', 'Frage', 'Einwohnerfrage', '2026-01-06'),
                                     ('p8', '261005-01', 'Anfrage', 'Große Anfrage', '2026-02-01'),
                                     ('p9', '261005-02 ST', 'Antwort', 'Stellungnahme der Verwaltung', '2026-02-10'),
                                     ('p10', '261006', 'Vorlage', 'Beschlussvorlage', '2026-03-01'),
                                     ('p11', '261006-01', 'Eil', 'Dringlichkeitsentscheidung OB', '2026-03-10');
            INSERT INTO consultation VALUES ('p1', 'aus', 'Empfehlung'), ('p2', 'rat', 'Entscheidung'), ('p3', 'rat', 'Kenntnisnahme'),
                                            ('p5', 'beirat', 'Kenntnisnahme'), ('p7', 'bv', 'Kenntnisnahme'),
                                            ('p8', 'rat', 'Kenntnisnahme'), ('p9', 'rat', 'Kenntnisnahme'),
                                            ('p10', 'beirat', 'Entscheidung'), ('p11', 'rat', 'Genehmigung');
        """)
        return db

    def test_abgleich(self):
        db = self._db()
        rows = {r["stammnummer"]: r for r in soll.abgleich(db, soll.Modell())}
        self.assertEqual((rows["261000"]["verfahren"], rows["261000"]["dokumente"], rows["261000"]["passung"]), ("antrag-rat", 2, "passt"))
        self.assertEqual((rows["261001"]["passung"], rows["261001"]["abweichung"]), ("weicht ab", "rat"))
        self.assertEqual(rows["261002"]["passung"], "ohne Soll")
        self.assertEqual((rows["261003"]["passung"], rows["261004"]["passung"]), ("nur Beirat", "ohne Beratung"))
        # spätere Große Anfrage samt Stellungnahme zählt nicht; eine Dringlichkeitsentscheidung setzt den Weg fort
        self.assertEqual((rows["261005"]["passung"], rows["261005"]["ist_bahnen"], rows["261005"]["dokumente"]), ("passt", "bv", 3))
        self.assertEqual((rows["261006"]["passung"], rows["261006"]["ist_bahnen"]), ("passt", "rat"))

    def test_lookup_je_vorlage(self):
        db = self._db()
        s = soll.lookup(db, "261000-01 ST")
        self.assertEqual((s["verfahren"], s["passung"], s["ist"]), ("antrag-rat", "passt", ["aus", "rat"]))
        self.assertEqual(soll.lookup(db, "261001")["abweichung"], ["rat"])
        self.assertIsNone(soll.lookup(db, "999999"))


class Seite(unittest.TestCase):
    def test_rechtsgrundlagen(self):
        r = soll.rechtsgrundlagen("§ 24 GO NRW, GeschO §§ 7 Abs. 4, 9; BezS § 9")
        self.assertEqual([x["label"] for x in r], ["Gemeindeordnung NRW § 24", "Geschäftsordnung des Rates §§ 7 Abs. 4, 9",
                                                   "Bezirkssatzung § 9"])
        self.assertTrue(all(x["url"].startswith("https://") for x in r))
        self.assertEqual(soll.rechtsgrundlagen("ZustO")[0]["url"], soll.Modell().zusto["quelle"])
        self.assertEqual(soll.rechtsgrundlagen(None), [])
        # mehrere Paragrafen eines Gesetzes bleiben zusammen (eigene Ergänzungen, z. B. d+aus)
        self.assertEqual([x["label"] for x in soll.rechtsgrundlagen("GeschO § 22 Abs. 1, § 7 Abs. 6; ZustO")],
                         ["Geschäftsordnung des Rates § 22 Abs. 1, § 7 Abs. 6", "Zuständigkeitsordnung"])

    def test_site_data(self):
        d = soll.site_data()
        self.assertIn("keine Rechtsauskunft", d["meta"]["hinweis"])
        self.assertEqual(set(d["bahnen"]), {"ew", "rm", "bvm", "vw", "bv", "aus", "rat"})
        schritte = [s for v in d["verfahren"].values() for s in v["schritte"]]
        self.assertTrue(all(s.get("links") for s in schritte if s.get("beleg") and re.search(r"GeschO|BezS|GO NRW", s["beleg"])))
        self.assertGreaterEqual(sum(1 for s in schritte if s.get("eigen")), 9)
        self.assertTrue(d["verfahren"]["mitteilung"]["jedes_gremium"])
        self.assertEqual(d["zusto"]["Ausschuss für Planen, Bauen und Denkmalschutz"]["nr"], "VII")
        self.assertNotIn("Alle Ausschüsse und Unterausschüsse", d["zusto"])  # ohne Einzelrechte
        self.assertTrue(all(f["links"] for f in d["fristen"] if f.get("beleg")))
        self.assertIn("Bürgerbrief", d["ohne_soll"])


if __name__ == "__main__":
    unittest.main()
