import unittest

from pipeline import topics


def paper(name, labels=(), gremien=(), originators=()):
    return {"name": name, "responsibility": [{"label": l} for l in labels],
            "process": [{"gremium": g} for g in gremien],
            "originators": [{"actor": a, "actor_type": t} for a, t in originators]}


def ids(p):
    return [(t["theme"], t["method"]) for t in topics.themes(p)]


class Themen(unittest.TestCase):
    def test_amt_vor_stichwort(self):
        p = paper("Radweg an der Endenicher Straße", labels=["66 Tiefbauamt"])
        self.assertEqual(ids(p), [("verkehr", "amt")])

    def test_gremium_und_stichwort(self):
        p = paper("Neue Bäume am Kaiserplatz", gremien=["Rat", "Ausschuss für Umwelt, Klima und Lokale Agenda"])
        self.assertEqual(ids(p), [("umwelt", "gremium")])

    def test_sonderfaelle(self):
        self.assertEqual(ids(paper("x", gremien=["Betriebsausschuss SGB"])), [("bauen", "gremium")])
        self.assertEqual(ids(paper("x", gremien=["Ausschuss für Soziales, Migration, Gesundheit und Wohnen"])),
                         [("soziales", "gremium")])
        self.assertEqual(ids(paper("x", gremien=["Ausschuss für Finanzen, Beteiligungen und Vergabe"])),
                         [("wirtschaft", "gremium")])
        self.assertEqual(ids(paper("x", gremien=["Bezirksvertretung Bonn", "Hauptausschuss"])), [])

    def test_keine_falschen_treffer(self):
        self.assertEqual(ids(paper("Baumaßnahme in Bad Godesberg")), [])
        self.assertEqual(ids(paper("Verkehrssicherheit an der Schule")), [("verkehr", "stichwort"), ("bildung", "stichwort")])


    def test_abteilung_stadtverkehr_und_umweltspur(self):
        # Stichprobe 19.10.2026: 61-3 Stadtverkehr gehört zum Stadtplanungsamt, bearbeitet aber Verkehr
        p = {"name": "Umweltspur auf dem Hermann-Wandersleb-Ring", "process": [],
             "responsibility": [{"label": "61 Stadtplanungsamt", "name": "61-3 Stadtverkehr"}]}
        self.assertEqual(topics.themes(p), [{"theme": "verkehr", "method": "amt", "evidence": "61-3 Stadtverkehr", "confidence": "mittel"}])
        p = {"name": "Bebauungsplan", "process": [], "responsibility": [{"label": "61 Stadtplanungsamt", "name": "61-4 Planungsrecht"}]}
        self.assertEqual(ids(p), [("bauen", "amt")])
        self.assertEqual(ids(paper("Umweltspur Endenicher Straße")), [("verkehr", "stichwort")])
        self.assertEqual(ids(paper("Umweltbericht")), [("umwelt", "stichwort")])


class Parteien(unittest.TestCase):
    def test_bezirksfraktion_und_kategorien(self):
        p = paper("x", originators=[("Grüne-Bezirksfraktion Beuel", "Bezirksfraktion"), ("CDU", "Fraktion/Gruppe"),
                                    ("weitere (u.w., nicht aufgelöst)", "unaufgelöst"), ("Koalition", "Koalition")])
        self.assertEqual(topics.parties(p), ["CDU", "Grüne", "Koalition"])


if __name__ == "__main__":
    unittest.main()
