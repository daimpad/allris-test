"""Prozessbild der Themenseite (pipeline/prozessbild.py): Zeitachse, Punkte, Sitzungen mit Frist, Aufrufe."""
import unittest

from pipeline import dossier, prozessbild
from tests.test_dossier import vorlage

CACHE = {
    "a": vorlage("261285", "Gleichbehandlung der Kulturangebote", amt="01-2 Ratsbüro", gremien=("Kulturausschuss",),
                 result="geändert beschlossen"),
    "b": vorlage("261724", "Neufassung der Gebührenordnung der Stadtbibliothek", amt="42 Stadtbibliothek",
                 date="2026-09-22"),
    "c": vorlage("261677", "Erlass einer haushaltswirtschaftlichen Sperre", amt="20 Stadtkämmerei"),
}
for p in CACHE.values():
    p["stand"] = "entschieden" if p["reference"] == "261285" else "offen"
MEETINGS = [
    {"date": "2026-11-26", "time": "18:00", "gremium": "Ausschuss für Finanzen, Beteiligungen und Vergabe",
     "cancelled": False, "web": None, "source_object": "m1"},
    {"date": "2026-11-04", "time": "18:00", "gremium": "Bezirksvertretung Bad Godesberg", "cancelled": False,
     "web": None, "source_object": "m2"},
]


class Prozessbild(unittest.TestCase):
    def setUp(self):
        self.d = dossier.daten(CACHE, {"a": "ortsteil:endenich"}, MEETINGS, "2026-10-18", {})

    def test_daten(self):
        self.assertEqual([(p["nr"], p["reference"], p["art"], p["bahn"]) for p in self.d["punkte"]],
                         [(1, "261677", "offen", "rat"), (2, "261285", "entschieden", "kultur"),
                          (3, "261724", "offen", "rat")])  # ohne Beratungsfolge: Bahn des Rates am Tag der Vorlage
        frist = {s["source_object"]: (s["bahn"], s["frist"]) for s in self.d["sitzungen"]}
        self.assertEqual(frist, {"m1": ("finanz", "2026-11-05"), "m2": ("bv", "2026-10-14")})

    def test_zeitachse_zweigeteilt(self):
        self.assertEqual(prozessbild._x("2025-11-01"), prozessbild.LINKS)
        self.assertAlmostEqual(prozessbild._x("2027-04-01"), prozessbild.W - prozessbild.RECHTS)
        rueckblick = prozessbild._x("2026-02-01") - prozessbild._x("2026-01-01")
        demnaechst = prozessbild._x("2026-12-01") - prozessbild._x("2026-11-01")
        self.assertGreater(demnaechst, 1.8 * rueckblick)  # kommende Monate breiter

    def test_bild(self):
        svg = prozessbild.svg(self.d)
        self.assertIn("Stand 18.10.", svg)
        self.assertEqual(svg.count('href="#pb-hand"'), 2 + 1)  # zwei Sitzungen und die Legende
        self.assertIn("Frist für Anträge und Fragen zur Sitzung Ausschuss für Finanzen", svg)
        self.assertNotIn("zur Sitzung Bezirksvertretung Bad Godesberg", svg)  # Frist 14.10. schon vorbei
        self.assertIn("3 Beschlüsse und Anträge: 1 entschieden, 0 beraten", svg)

    def test_aufrufe_und_balken(self):
        html = prozessbild.abschnitt(self.d, "../../")
        self.assertIn("Nächste offene Frist: 05.11.2026 für Ausschuss für Finanzen", html)
        self.assertIn('href="../../data/export/bonn/dossiers/kultur.ics"', html)
        self.assertIn('href="../../?gebiet=ortsteil:endenich#261285"', html)
        self.assertIn('title="1 entschieden"', html)
        self.assertIn('data-start="0.', html)


if __name__ == "__main__":
    unittest.main()
