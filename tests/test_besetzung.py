import json
import tempfile
import unittest
from pathlib import Path

from pipeline import besetzung

O = "https://www.bonn.sitzung-online.de/oparl/organizations/"
ORGS = {O + "gr/1": {"id": O + "gr/1", "name": "Rat", "classification": "Rat"},
        O + "gr/17": {"id": O + "gr/17", "name": "Kulturausschuss", "classification": "Ratsgremien"},
        O + "gr/4": {"id": O + "gr/4", "name": "Bezirksvertretung Beuel", "classification": "Bezirksvertretungen"},
        O + "gr/99": {"id": O + "gr/99", "name": "Beirat Kinder- und Jugendbeteiligung", "classification": "Beiräte und Kommissionen"},
        O + "gr/45": {"id": O + "gr/45", "name": "CDU-Fraktion im Rat der Stadt Bonn", "classification": "Fraktion"},
        O + "gr/296": {"id": O + "gr/296", "name": "CDU Bezirksfraktion Beuel", "classification": "Bezirksfraktionen (intern)"},
        O + "gr/50": {"id": O + "gr/50", "name": "Alte Fraktion", "classification": "Fraktion", "endDate": "2020-10-31"},
        # gleiche Nummer, andere Art (Verwaltungsbereich): darf nicht mit dem Rat verwechselt werden
        O + "at/1": {"id": O + "at/1", "name": "01 Amt", "classification": "Verwaltungsbereich"}}


def mitglied(org, rolle, start="2025-11-01", ende=None):
    return {"id": f"m{org}{rolle}", "organization": O + org, "role": rolle, "startDate": start, "endDate": ende, "votingRight": False}


def person(pid, name, *ms, status=("Politik",)):
    return {"id": f"https://www.bonn.sitzung-online.de/oparl/persons/{pid}", "name": name, "title": [], "status": list(status),
            "web": f"https://www.bonn.sitzung-online.de/public/KP020?KPLFDNR={pid}", "email": ["a@b.de"], "phone": ["0228 1"],
            "locationObject": {"streetAddress": "Weg 1"}, "gender": "female", "membership": list(ms)}


PERSONEN = [
    person(1, "Anna Rat", mitglied("gr/1", "Stadtverordnete/r"), mitglied("gr/45", "Fraktionsmitglied"),
           mitglied("gr/50", "Fraktionsmitglied", "2015-01-01"), mitglied("gr/17", "Mitglied (Stv.)"),
           mitglied("gr/4", "Stadtverordnete/r in Bezirksvertretung"), mitglied("gr/296", "Stadtverordnete/r in Bezirksfraktion")),
    person(2, "Berta Sachkundig", mitglied("gr/17", "Sachkundige/r Bürger/in")),
    person(3, "Carl Vertretung", mitglied("gr/17", "Stellv. Mitglied")),
    person(4, "Dora Verwaltung", mitglied("gr/17", "Beratendes Mitglied"), mitglied("gr/1", "Schriftführung"), status=("Verwaltung",)),
    person(5, "Emil Jugend", mitglied("gr/99", "Beiratsmitglied Jugend")),
    person(6, "Frida Beirat", mitglied("gr/99", "Beiratsmitglied")),
    person(7, "Gerd Alt", mitglied("gr/17", "Mitglied (Stv.)", "2019-01-01")),               # vor der Wahlperiode
    person(8, "Hanna Ehemals", mitglied("gr/1", "Stadtverordnete/r", "2020-11-01", "2025-10-31")),
    person(9, "Ida Geschäftsstelle", mitglied("gr/1", "Stadtverordnete/r"), mitglied("gr/45", "Fraktionsmitglied"),
           status=("Fraktionsgeschäftsstellen",)),
    person(10, "Jan Bezirk", mitglied("gr/4", "Bezirksverordnete/r"), mitglied("gr/296", "Fraktionsmitglied")),
]


class Auszug(unittest.TestCase):
    def setUp(self):
        self.doc = besetzung.auszug(PERSONEN, ORGS, "2026-10-27")

    def test_ohne_kontaktdaten_und_ohne_namen_wo_ausgeschlossen(self):
        text = json.dumps(self.doc, ensure_ascii=False)
        for verboten in ("a@b.de", "0228", "Weg 1", "female", "Carl Vertretung", "Dora Verwaltung", "Emil Jugend",
                         "Frida Beirat", "Hanna Ehemals", "Schriftführung"):
            self.assertNotIn(verboten, text)
        self.assertEqual(besetzung.pruefen_auszug(self.doc), [])
        self.assertIn("Ida Geschäftsstelle", text)   # gewählt: Name trotz Status der Quelle
        self.assertEqual(self.doc["personen"]["1"]["fraktionen"], ["gr/45", "gr/296"])   # beendete Fraktion fehlt

    def test_pruefung_findet_kontaktdaten(self):
        doc = json.loads(json.dumps(self.doc))
        doc["personen"]["1"]["email"] = ["a@b.de"]
        self.assertTrue(besetzung.pruefen_auszug(doc))


class Gremien(unittest.TestCase):
    def test_sitze_fraktion_beratend_und_audit(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "besetzung.json"
            path.write_text(json.dumps(besetzung.auszug(PERSONEN, ORGS, "2026-10-27"), ensure_ascii=False))
            out, audit = besetzung.gremien("2025-11-01", "2026-10-27", path, ORGS)
        rat, kultur, bv, beirat = out["gr/1"], out["gr/17"], out["gr/4"], out["gr/99"]
        self.assertEqual(rat["sitze"], [{"fraktion": "CDU-Fraktion", "n": 2}])
        self.assertEqual(kultur["sitze_gesamt"], 2)
        self.assertEqual((kultur["sachkundig"], kultur["ohne_fraktion"], kultur["stellvertretend"]), (1, 1, 1))
        self.assertEqual([e["name"] for e in kultur["ordentlich"]], ["Anna Rat", "Berta Sachkundig"])
        self.assertEqual((kultur["ohne_namen"], kultur["beratend"]), (1, []))   # Verwaltung ohne Namen
        # Bezirksvertretung: Bezirksfraktion; Ratsmitglied beratend
        self.assertEqual(bv["sitze"], [{"fraktion": "CDU", "n": 1}])
        self.assertEqual([(e["name"], e["fraktion"]) for e in bv["beratend"]], [("Anna Rat", "CDU")])
        self.assertEqual((beirat["sitze_gesamt"], beirat["ordentlich"], beirat["ohne_namen_grund"]),
                         (2, [], ["Beirat mit Jugendmitgliedern"]))
        self.assertEqual(audit, [["Kulturausschuss", "Mitglied (Stv.)", "2019-01-01", "Beginn vor der Wahlperiode"]])
        self.assertNotIn("at/1", out)

    def test_kurze_id_mit_art(self):
        self.assertEqual(besetzung._kurz(O + "gr/45"), "gr/45")
        self.assertEqual(besetzung._kurz(O + "at/1"), "at/1")
        self.assertEqual(besetzung._kurz("https://www.bonn.sitzung-online.de/oparl/persons/12"), "12")


if __name__ == "__main__":
    unittest.main()
