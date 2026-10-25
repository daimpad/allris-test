"""Themenseite „Kultur und Haushalt“ (pipeline/dossier.py): Regeln der Stränge, Daten und Seite."""
import json
import tempfile
import unittest
from pathlib import Path

from pipeline import dossier, gebietsseiten


def vorlage(ref, name, amt=None, date="2026-06-01", gremien=(), result=None):
    return {"reference": ref, "name": name, "amt": amt, "date": date, "paper_type": "Beschlussvorlage",
            "stand": "offen", "web": f"https://example.org/{ref}",
            "process": [{"gremium": g, "start_date": "2026-06-10T16:00:00Z", "result": result, "cancelled": False}
                        for g in gremien]}


CACHE = {
    "a": vorlage("261677", "Erlass einer haushaltswirtschaftlichen Sperre", amt="20 Stadtkämmerei"),
    "b": vorlage("260127-05", "Zukunft der Bonner Bühnen, Änderungsantrag", amt="01-2 Ratsbüro", date="2024-01-01"),
    "c": vorlage("261033", "Umstellung der institutionellen Förderung auf Festbetragsfinanzierung", amt="41 Kulturamt"),
    "d": vorlage("261285", "Gleichbehandlung der Kulturangebote", amt="01-2 Ratsbüro", gremien=("Kulturausschuss",),
                 result="beschlossen"),
    "e": vorlage("261500", "Ausstellung im Stadtmuseum", amt="41 Kulturamt"),
    "f": vorlage("261501", "Sanierung einer Schule", amt="40 Schulamt"),
    "g": vorlage("250001", "Förderung von Kulturprojekten", amt="41 Kulturamt", date="2025-10-31"),
    "h": vorlage("261064", "Rahmenterminplan für die Einbringung der Haushaltssatzung 2027/2028", amt="20 Stadtkämmerei"),
    "i": vorlage("240986", "Einbringung der Haushaltssatzung 2025/2026", date="2024-09-01"),
    "j": vorlage("240986-01 AA", "Änderungsantrag zur Haushaltssatzung", date="2024-10-01"),
}
MEETINGS = [
    {"date": "2026-10-01", "time": "18:00", "gremium": "Kulturausschuss", "cancelled": False, "web": None, "source_object": "m0"},
    {"date": "2026-12-01", "time": "18:00", "gremium": "Kulturausschuss", "cancelled": False, "web": None, "source_object": "m1"},
    {"date": "2026-12-02", "time": None, "gremium": "Rat", "cancelled": True, "web": None, "source_object": "m2"},
    {"date": "2026-12-03", "time": "17:00", "gremium": "Rat", "cancelled": False, "web": None, "source_object": "m3"},
    {"date": "2026-12-04", "time": "17:00", "gremium": "Schulausschuss", "cancelled": False, "web": None, "source_object": "m4"},
]


class Straenge(unittest.TestCase):
    def setUp(self):
        self.d = dossier.daten(CACHE, {"a": "ohne:2026", "d": "ortsteil:endenich"}, MEETINGS, "2026-10-25", {})
        self.by = {s["key"]: [r["reference"] for r in s["vorlagen"]] for s in self.d["straenge"]}

    def test_zuordnung(self):
        self.assertEqual(self.by["haushalt"], ["261677", "261064"])  # gleiches Datum: Drucksache absteigend
        self.assertEqual(self.by["buehnen"], ["260127-05"])  # Stammnummer gilt auch vor Beginn der Wahlperiode
        self.assertEqual(self.by["kultur_finanzen"], ["261285", "261033"])
        self.assertEqual(self.by["kultur_weitere"], ["261500"])  # ohne Geldbezug im Titel

    def test_ausgeschlossen(self):
        alle = {r for refs in self.by.values() for r in refs}
        self.assertNotIn("261501", alle)  # anderes Amt, kein Kulturgremium
        self.assertNotIn("250001", alle)  # vor Beginn der Wahlperiode
        self.assertNotIn("240986", alle)

    def test_grund_mit_ganzem_wort(self):
        rows = {r["reference"]: r for s in self.d["straenge"] for r in s["vorlagen"]}
        self.assertEqual(rows["261033"]["grund"], "federführend: 41 Kulturamt; Titel: „Förderung“")
        self.assertEqual(rows["261285"]["grund"], "Beratung im Kulturausschuss; Titel: „Gleichbehandlung“")
        self.assertEqual(rows["261677"]["grund"], "Titel: „haushaltswirtschaftlichen“")
        self.assertEqual(rows["261285"]["letzte_beratung"],
                         {"gremium": "Kulturausschuss", "date": "2026-06-10", "result": "beschlossen"})

    def test_sitzungen_und_vergleich(self):
        self.assertEqual([m["source_object"] for m in self.d["sitzungen"]], ["m1", "m3"])
        self.assertEqual(self.d["vergleich"]["vorlagen"], 2)
        self.assertEqual(self.d["terminplan"]["reference"], "261064")


class Seite(unittest.TestCase):
    def test_seite_und_sitemap_pfad(self):
        d = dossier.daten(CACHE, {"d": "ortsteil:endenich"}, MEETINGS, "2026-10-25", {})
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            src = site / "data" / "export" / "bonn" / "dossiers" / "kultur.json"
            src.parent.mkdir(parents=True)
            src.write_text(json.dumps(d))
            self.assertEqual(dossier.write(site, "https://example.org/", gebietsseiten._page), [dossier.PFAD])
            html = (site / dossier.PFAD / "index.html").read_text()
        self.assertIn('<link rel="canonical" href="https://example.org/thema/kultur-und-haushalt/">', html)
        self.assertIn('href="../../?gebiet=ortsteil:endenich#261285"', html)
        self.assertIn("Kulturausschuss 10.06.2026: beschlossen", html)
        self.assertIn("01.12.2026, 18:00 Uhr: Kulturausschuss", html)
        self.assertNotIn("o. Ä..", html)

    def test_ohne_daten_keine_seite(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(dossier.write(Path(tmp), "https://example.org/", gebietsseiten._page), [])


if __name__ == "__main__":
    unittest.main()
