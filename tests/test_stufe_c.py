import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from pipeline import config, stufe_c, volltext
from pipeline.build import SCHEMA
from pipeline.geocode import Gazetteer


def way(name, lon, lat, d=0.002):
    return {"name": name, "highway": "residential", "coords": [[lon - d, lat], [lon + d, lat]]}


KOPF = "Beschlussvorlage\nBeratungsfolge\nBezirksvertretung Bonn 01.02.2025 Entscheidung\nSachverhalt\n"


class StufeCTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        probe = Gazetteer(ways=[], housenumbers={})
        e, m = probe.ot_point["Endenich"], probe.ot_point["Mehlem"]
        cls.gaz = Gazetteer(ways=[way("Endenicher Straße", e.x, e.y), way("Mainzer Straße", m.x, m.y),
                                  way("Markt", m.x, m.y)], housenumbers={})

    def test_bereinigen_entfernt_hausnummern_und_unbekanntes(self):
        antwort = '```json\n{"orte": [{"name": "Endenicher Straße 12", "art": "strasse", "rolle": "gegenstand"},' \
                  '{"name": "Max Mustermann", "art": "person", "rolle": "gegenstand"},' \
                  '{"name": "Mehlem", "art": "ortsteil", "rolle": "vielleicht"}]}\n```'
        self.assertEqual(stufe_c.bereinigen(antwort),
                         [{"name": "Endenicher Straße", "art": "strasse", "rolle": "gegenstand", "ortsteil": ""}])
        self.assertEqual(stufe_c.bereinigen("keine Antwort"), [])

    def test_bestaetigt_herabgestuft_und_neu(self):
        text = KOPF + "Die Endenicher Straße wird saniert. Wie an der Mainzer Straße; die Mainzer Straße dient als Vergleich."
        b_rows, _ = volltext.locate(self.gaz, text)
        orte = [{"name": "Endenicher Straße", "art": "strasse", "rolle": "gegenstand", "ortsteil": ""},
                {"name": "Mainzer Straße", "art": "strasse", "rolle": "erwähnt", "ortsteil": "Mehlem"}]
        rows, befund = stufe_c.pruefen(self.gaz, text, orte, b_rows)
        got = {(r["name"], r["aktion"], r["confidence"]) for r in rows}
        self.assertIn(("Endenicher Straße", "bestätigt", "mittel"), got)
        self.assertEqual(befund, "geändert")
        self.assertIn(("Mainzer Straße", "herabgestuft", "niedrig"), got)

    def test_neuer_ort_nur_wenn_im_text_und_im_verzeichnis(self):
        text = KOPF + "Neue Bänke für den Platz."
        orte = [{"name": "Endenicher Straße", "art": "strasse", "rolle": "gegenstand", "ortsteil": ""},  # nicht im Text
                {"name": "Platz", "art": "objekt", "rolle": "gegenstand", "ortsteil": ""}]                # nicht im Verzeichnis
        self.assertEqual(stufe_c.pruefen(self.gaz, text, orte, [])[0], [])
        text = KOPF + "Neue Bänke für den Spielplatz in Endenich."
        orte = [{"name": "Spielplatz in Endenich", "art": "objekt", "rolle": "gegenstand", "ortsteil": "Endenich"}]
        rows, _ = stufe_c.pruefen(self.gaz, text, orte, [])
        self.assertEqual([(r["name"], r["aktion"], r["method"], r["confidence"]) for r in rows],
                         [("Endenich", "neu", "llm_ortsteil", "niedrig")])
        self.assertNotIn("Bänke", rows[0]["evidence"])  # Fundstelle ohne Textauszug

    def test_gattungsname_und_bezirk_allein_zaehlen_nicht(self):
        text = KOPF + "Wochenmarkt auf dem Markt im Stadtbezirk Bad Godesberg."
        orte = [{"name": "Markt", "art": "objekt", "rolle": "gegenstand", "ortsteil": ""},
                {"name": "Bad Godesberg", "art": "stadtbezirk", "rolle": "gegenstand", "ortsteil": ""}]
        self.assertEqual(stufe_c.pruefen(self.gaz, text, orte, [])[0], [])

    def test_ohne_schluessel_nichts_und_nur_neue(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            db = sqlite3.connect(":memory:")
            db.executescript(SCHEMA)
            papers, texte = d / "papers.jsonl", d / "texte.jsonl"
            papers.write_text("\n".join(json.dumps({"id": f"p{i}", "reference": f"26000{i}", "name": "Spielplatz",
                                                    "paperType": t, "mainFile": {"id": f"f{i}"}})
                                        for i, t in enumerate(["Beschlussvorlage", "Bürgerantrag § 24 GO", "Antrag"])))
            texte.write_text("\n".join(json.dumps({"uri": f"f{i}", "sha": f"s{i}", "text": KOPF + "Endenich"})
                                       for i in range(3)))
            # p2 hat einen eigenen Ortsbezug aus dem Titel und ist kein Kandidat
            db.execute("INSERT INTO paper_location VALUES ('p2','ortsteil:Endenich','B','ortsteil_name','mittel','','p2')")
            calls = []
            def anfrage(titel, text, key):
                calls.append(titel)
                return '{"orte": [{"name": "Endenich", "art": "ortsteil", "rolle": "gegenstand"}]}', {"ein": 10, "aus": 5}
            with mock.patch.object(config, "PAPERS", papers), mock.patch.object(config, "TEXTE", texte):
                with mock.patch.dict(os.environ, {}, clear=True):
                    stufe_c.erzeugen(db, d / "out", anfrage=anfrage)
                self.assertEqual(calls, [])
                with mock.patch.dict(os.environ, {"MISTRAL_API_KEY": "test"}):
                    stufe_c.erzeugen(db, d / "out", anfrage=anfrage)
                    stufe_c.erzeugen(db, d / "out", anfrage=anfrage)  # zweiter Lauf: nichts Neues
            self.assertEqual(len(calls), 1)  # Bürgerantrag ausgenommen, p2 mit eigenem Ortsbezug
            rows = list(stufe_c.laden(d / "out").values())
            self.assertEqual([(r["drucksache"], r["orte"][0]["name"]) for r in rows], [("260000", "Endenich")])


if __name__ == "__main__":
    unittest.main()
