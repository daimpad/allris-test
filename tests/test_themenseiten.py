"""Allgemeine Themenseiten (pipeline/themenseiten/, dossier.py, prozessbild.py): Die Kulturseite bleibt nach dem
Umbau Zeichen für Zeichen gleich (Referenz in tests/referenz/, erzeugt vor dem Umbau am 26.10.2026); dazu die
Regeln der Zuordnung und ein Thema ohne Phasen."""
import json
import re
import tempfile
import unittest
from datetime import date
from pathlib import Path

from pipeline import dossier, gebietsseiten, prozessbild
from pipeline.themenseiten import ALLE, kultur
from tests.test_dossier import vorlage
from tests.test_prozessbild import CACHE, MEETINGS

REFERENZ = Path(__file__).parent / "referenz"


def _kultur_daten():
    cache = dict(CACHE, h=vorlage("261064", "Rahmenterminplan Haushalt 2027/2028", amt="20 Stadtkämmerei"),
                 v=vorlage("240986", "Einbringung der Haushaltssatzung 2025/2026", date="2024-09-01"))
    meetings = MEETINGS + [dict(MEETINGS[0], date="2026-12-10", gremium="Rat", source_object="m9",
                                web="https://example.org/to/m9")]
    return dossier.daten(kultur.THEMA, cache, {"a": "ortsteil:endenich", "h": "ohne:2026"}, meetings, "2026-10-18",
                         {"stand": "2026-10-18"})


class KulturUnveraendert(unittest.TestCase):
    def setUp(self):
        self.d = _kultur_daten()

    def test_daten(self):
        self.assertEqual(json.loads(json.dumps(self.d)), json.loads((REFERENZ / "kultur.json").read_text()))

    def test_bild_zum_teilen(self):
        self.assertEqual(prozessbild.bild(kultur.THEMA, self.d, "https://example.org/thema/kultur-und-haushalt/"),
                         (REFERENZ / "kultur-zeitleiste.svg").read_text())

    def test_seite(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            src = site / "data" / "export" / "bonn" / "dossiers" / "kultur.json"
            src.parent.mkdir(parents=True)
            src.write_text(json.dumps(self.d))
            self.assertEqual(dossier.write(kultur.THEMA, site, "https://example.org/", gebietsseiten._page),
                             [kultur.THEMA.pfad])
            html = (site / kultur.THEMA.pfad / "index.html").read_text()
        self.assertEqual(html, (REFERENZ / "kultur-seite.html").read_text())


class Beschreibungen(unittest.TestCase):
    def test_alle_themen_vollstaendig(self):
        keys = [t.key for t in ALLE]
        self.assertEqual(len(keys), len(set(keys)))
        for t in ALLE:
            strang = {k for k, _, _ in t.straenge}
            bahnen = [k for k, _ in t.bahnen]
            self.assertTrue(t.pfad.startswith("thema/") and t.pfad.endswith("/"), t.key)
            self.assertLessEqual(set(t.punkt_straenge), strang, t.key)
            self.assertLessEqual({r.strang for r in t.regeln} | {r.sonst for r in t.regeln if r.sonst}, strang, t.key)
            self.assertLessEqual(set(t.bahn_gremien), set(bahnen), t.key)
            self.assertLessEqual({b for b, *_ in t.phasen}, set(bahnen), t.key)
            self.assertTrue({"bv", "fach", "finanz", "rat"} <= set(bahnen), t.key)  # Bahnen ohne eigene Gremien
            if t.phasen:
                self.assertTrue(t.terminplan, t.key)


# ein kleines Thema ohne Phasen, Terminplan und Vergleich (Form einer neuen Themenseite)
SCHULE = dossier.Thema(
    key="schule", pfad="thema/schule/", titel="Schule", lead="Vorlagen zu Schulen seit {seit}.",
    seo_text="{n} Vorlagen zu Schulen.", seit="2025-11-01",
    straenge=[("bau", "Schulbau", "Titel nennt Neubau oder Sanierung"),
              ("weitere", "Weitere Vorlagen aus dem Schulamt", "Schulamt federführend oder Schulausschuss")],
    regeln=[dossier.Regel("bau", titel=re.compile(r"Neubau|Sanierung")),
            dossier.Regel("weitere", zustaendig=dossier.Zustaendig(aemter=("40 ",), gremien=("Schulausschuss",)))],
    punkt_straenge=("bau", "weitere"),
    bahnen=[("bv", "Bezirksvertretungen"), ("schule", "Schulausschuss"), ("fach", "andere Ausschüsse"),
            ("finanz", "Finanzausschuss"), ("rat", "Hauptausschuss, Rat")],
    bahn_gremien={"schule": ("Schulausschuss",)}, sitzungen=("Schulausschuss", "Rat"),
    achse=(date(2025, 11, 1), date(2027, 1, 1), date(2026, 7, 1), 0.5),
    bild_titel="Zeitleiste: Schule in Rat, Ausschüssen und Bezirksvertretungen", feed_text="zu Schulen",
    hinweis="Zuordnung abgeleitet", pruefung_text="Noch nicht von Hand geprüft.", nicht_gezeigt=["Beträge"])


class ThemaOhnePhasen(unittest.TestCase):
    def setUp(self):
        cache = {
            "a": vorlage("261900", "Neubau der Grundschule", amt="40 Schulamt", gremien=("Schulausschuss",),
                         result="beschlossen"),
            "b": vorlage("261901", "Schulentwicklungsplan", amt="01-2 Ratsbüro", gremien=("Schulausschuss",)),
            "c": vorlage("261902", "Ausstellung im Stadtmuseum", amt="41 Kulturamt"),
        }
        meetings = [{"date": "2026-12-01", "time": "17:00", "gremium": "Schulausschuss", "cancelled": False,
                     "web": None, "source_object": "m1"}]
        self.d = dossier.daten(SCHULE, cache, {}, meetings, "2026-10-26", {})

    def test_straenge_und_bahnen(self):
        by = {s["key"]: [(r["reference"], r["grund"]) for s2 in [s] for r in s2["vorlagen"]] for s in self.d["straenge"]}
        self.assertEqual(by["bau"], [("261900", "Titel: „Neubau“")])
        self.assertEqual(by["weitere"], [("261901", "Beratung im Schulausschuss")])
        self.assertEqual({p["bahn"] for p in self.d["punkte"]}, {"schule"})
        self.assertEqual([s["bahn"] for s in self.d["sitzungen"]], ["schule"])

    def test_seite_ohne_phasen(self):
        html = dossier.body(SCHULE, self.d, "../../")
        self.assertNotIn("Terminplan", html)
        self.assertNotIn("So entsteht", html)
        self.assertIn("Die Monate ab Juli 2026 sind breiter gezeichnet. Punkte und Sitzungen lassen sich", html)
        self.assertIn('href="../../data/export/bonn/dossiers/schule.ics"', html)
        self.assertIn("Neue Vorlagen und Beratungsergebnisse zu Schulen im Feed-Reader.", html)
        svg = prozessbild.svg(SCHULE, self.d)
        self.assertIn("Zeitleiste von November 2025 bis Dezember 2026", svg)
        self.assertNotIn("geplant laut Terminplan", svg)
        self.assertIn("Zuordnung abgeleitet</text>", prozessbild.bild(SCHULE, self.d, "https://example.org/"))


if __name__ == "__main__":
    unittest.main()
