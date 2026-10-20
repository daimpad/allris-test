import sqlite3
import unittest

from pipeline import prozessarten


def db_with(orgs, consultations=(), meetings=()):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE organization (id, name, short_name, org_type, classification, label, start_date, end_date, web, source)")
    db.execute("CREATE TABLE consultation (id, paper_id, position, organization_id, role, authoritative, meeting_id, "
               "agenda_item_id, source, link_source)")
    db.execute("CREATE TABLE meeting (id, name, start_date, cancelled, source)")
    for oid, name, cls, end in orgs:
        db.execute("INSERT INTO organization VALUES (?,?,?,?,?,?,?,?,?,?)", (oid, name, None, "Gremium", cls, None, None, end, None, None))
    for i, (pid, oid, mid) in enumerate(consultations):
        db.execute("INSERT INTO consultation VALUES (?,?,?,?,?,?,?,?,?,?)", (i, pid, 0, oid, None, 0, mid, None, None, None))
    for mid, start in meetings:
        db.execute("INSERT INTO meeting VALUES (?,?,?,?,?)", (mid, "Sitzung", start, 0, None))
    return db


class Arten(unittest.TestCase):
    def test_art(self):
        self.assertEqual(prozessarten.art("Rat", "Rat"), "rat")
        self.assertEqual(prozessarten.art("Hauptausschuss", "Ratsgremien"), "hauptausschuss")
        self.assertEqual(prozessarten.art("Unterausschuss Denkmalschutz", "Ratsgremien"), "unterausschuss")
        self.assertEqual(prozessarten.art("Wahlprüfungsausschuss (Kommunalwahl 2025)", "Ratsgremien"), "wahlausschuss")
        self.assertEqual(prozessarten.art("Schulausschuss", "Ratsgremien"), "ausschuss")
        self.assertEqual(prozessarten.art("Bezirksvertretung Beuel", "Bezirksvertretungen"), "bezirksvertretung")
        self.assertIsNone(prozessarten.art("CDU-Fraktion", "Fraktion"))

    def test_wahlperiode(self):
        terms = [{"startDate": "2020-11-01", "endDate": "2025-10-31"}, {"startDate": "2025-11-01"}]
        self.assertEqual(prozessarten._term_start(terms, "2026-10-20"), "2025-11-01")


class Gremien(unittest.TestCase):
    def test_aktuell_naechste_sitzung_und_zustaendigkeit(self):
        db = db_with(
            [("gr/1", "Rat", "Rat", None), ("gr/10", "Schulausschuss", "Ratsgremien", None),
             ("gr/24", "Ausschuss für Umwelt und Verbraucherschutz", "Ratsgremien", "2020-10-31"),
             ("gr/374", "Ausschuss für Soziales, Migration, Gesundheit, Wohnen und Senioren", "Ratsgremien", None),
             ("gr/99", "CDU-Fraktion", "Fraktion", None)],
            [("p1", "gr/1", "m1"), ("p2", "gr/1", "m1"), ("p1", "gr/10", "m2"), ("p3", "gr/24", "m0")],
            [("m0", "2020-05-01T16:00:00Z"), ("m1", "2026-09-28T17:00:00Z"), ("m2", "2025-06-01T16:00:00Z")])
        meetings = [{"start": "2026-11-12T17:00:00+01:00", "organization": ["gr/1"], "web": "w1"},
                    {"start": "2026-11-04T16:00:00+01:00", "organization": ["gr/10"], "cancelled": True},
                    {"start": "2026-10-01T16:00:00+01:00", "organization": ["gr/10"]}]  # vergangen
        zusto = {"Schulausschuss": {}, "Ausschuss für Soziales, Migration, Gesundheit und Senioren": {}}
        g = {x["name"]: x for x in prozessarten.gremien(db, meetings, zusto, "2026-10-20", "2025-11-01")}
        self.assertNotIn("CDU-Fraktion", g)
        self.assertEqual((g["Rat"]["aktuell"], g["Rat"]["beratungen"], g["Rat"]["vorlagen"], g["Rat"]["naechste"]),
                         (True, 2, 2, {"datum": "2026-11-12", "web": "w1"}))
        # letzte Sitzung vor der Wahlperiode, keine angesetzte (abgesagt zählt nicht): nicht aktuell
        self.assertEqual((g["Schulausschuss"]["aktuell"], g["Schulausschuss"]["naechste"], g["Schulausschuss"]["zusto"]),
                         (False, None, "Schulausschuss"))
        self.assertEqual(g["Ausschuss für Umwelt und Verbraucherschutz"]["aufgeloest"], "2020-10-31")
        soz = g["Ausschuss für Soziales, Migration, Gesundheit, Wohnen und Senioren"]
        self.assertEqual(soz["zusto"], "Ausschuss für Soziales, Migration, Gesundheit und Senioren")
        self.assertIn("abgeleitet", soz["zusto_hinweis"])


class Verfahren(unittest.TestCase):
    def test_zahlen_und_juengste_beispiele(self):
        rows = [{"stammnummer": s, "verfahren": v, "sicherheit": sure} for s, v, sure in
                [("1", "buergerantrag", "hoch"), ("2", "buergerantrag", "hoch"), ("3", "buergerantrag", "mittel"),
                 ("4", "buergerantrag", "hoch"), ("5", "", "")]]
        titles = {"1": ("A", "2026-01-01"), "2": ("B", "2026-03-01"), "3": ("C", "2026-02-01"), "4": ("D", "2025-01-01")}
        v = prozessarten.verfahren(rows, titles)
        self.assertEqual(list(v), ["buergerantrag"])
        self.assertEqual((v["buergerantrag"]["vorgaenge"], v["buergerantrag"]["sicher"]), (4, 3))
        self.assertEqual([b["drucksache"] for b in v["buergerantrag"]["beispiele"]], ["2", "3", "1"])


class Aemter(unittest.TestCase):
    def test_gruppe(self):
        g = prozessarten.amt_gruppe
        self.assertEqual((g("61 Stadtplanungsamt"), g("03 Amt für Wirtschaftsförderung"), g("85 Städtisches Gebäudemanagement Bonn")),
                         ("6", "0", "8"))
        self.assertEqual((g("01-2 Ratsbüro"), g("Dezernat III"), g("II-2 Referat Vergabedienste")), ("koordination",) * 3)
        self.assertEqual((g("Bezirksverwaltungsstelle Beuel"), g("Seniorenzentren der Bundesstadt Bonn")), ("bezirk", "weitere"))

    def test_abteilungen_gremien_und_hinweis(self):
        db = sqlite3.connect(":memory:")
        db.execute("CREATE TABLE organization (id, name, short_name, org_type, classification, label, start_date, end_date, web, source)")
        db.execute("CREATE TABLE paper (id, reference, name, paper_type, date, under_direction_of, web, main_file_url, main_file_name, source)")
        db.execute("CREATE TABLE consultation (id, paper_id, position, organization_id, role, authoritative, meeting_id, "
                   "agenda_item_id, source, link_source)")
        db.execute("CREATE TABLE paper_responsibility (paper_id, organization_id, kind, method, evidence, derived)")
        orgs = [("at/1", "61 Stadtplanungsamt", "Verwaltungsbereich", "61 Stadtplanungsamt", "61 Stadtplanungsamt", None),
                ("at/2", "61-3 Stadtverkehr", "Verwaltungsbereich", "61 Stadtplanungsamt", "61 Stadtplanungsamt", None),
                ("at/3", "61-1 Stadtentwicklung und Statistik", "Verwaltungsbereich", "61 Stadtplanungsamt", "61 Stadtplanungsamt", "2021-07-08"),
                ("at/4", "68 Amt für Stadtgrün", "Verwaltungsbereich", "68 Amt für Stadtgrün", "68 Amt für Stadtgrün", "2020-10-07"),
                ("at/5", "01-2 Ratsbüro", "Verwaltungsbereich", "Co-Dezernat", "01-2 Ratsbüro", None),
                ("gr/7", "Bezirksvertretung Bonn", "Gremium", "Bezirksvertretungen", "Bezirksvertretung Bonn", None)]
        for oid, name, typ, cls, label, end in orgs:
            db.execute("INSERT INTO organization VALUES (?,?,?,?,?,?,?,?,?,?)", (oid, name, None, typ, cls, label, None, end, None, None))
        papers = [("p1", "1", "A", "Beschlussvorlage", "2026-01-01", "at/2"), ("p2", "2", "B", "Antrag", "2026-02-01", "at/5"),
                  ("p3", "3", "C", "Antrag", "2026-03-01", "at/5"), ("p4", "4", "D", "Beschlussvorlage", "2020-01-01", "at/4")]
        for pid, ref, name, typ, date, org in papers:
            db.execute("INSERT INTO paper VALUES (?,?,?,?,?,?,?,?,?,?)", (pid, ref, name, typ, date, org, None, None, None, None))
        db.execute("INSERT INTO consultation VALUES (1,'p1',0,'gr/7',NULL,0,NULL,NULL,NULL,NULL)")
        db.execute("INSERT INTO paper_responsibility VALUES ('p2','at/2','fachlich','stellungnahme','5',1)")
        a = {x["name"]: x for x in prozessarten.aemter(db, "2026-10-20")}
        spa = a["61 Stadtplanungsamt"]
        self.assertEqual((spa["id"], spa["gruppe"], spa["vorlagen"], spa["aktuell"], spa["fachlich"]),
                         ("61-stadtplanungsamt", "6", 1, True, 1))
        self.assertEqual([(x["name"], x["aufgeloest"]) for x in spa["abteilungen"]],
                         [("61-3 Stadtverkehr", None), ("61-1 Stadtentwicklung und Statistik", "2021-07-08")])
        self.assertEqual(spa["gremien"], [{"id": "7", "name": "Bezirksvertretung Bonn", "vorlagen": 1}])
        self.assertEqual((a["68 Amt für Stadtgrün"]["aktuell"], a["68 Amt für Stadtgrün"]["aufgeloest"]), (False, "2020-10-07"))
        rb = a["01-2 Ratsbüro"]
        self.assertEqual((rb["gruppe"], rb["politik"], rb["hinweis"]), ("koordination", 2, prozessarten.HINWEIS_POLITIK))
        self.assertEqual(rb["fachlich_aemter"], [{"name": "61 Stadtplanungsamt", "vorlagen": 1}])
        self.assertEqual([b["drucksache"] for b in rb["beispiele"]], ["3", "2"])


if __name__ == "__main__":
    unittest.main()
