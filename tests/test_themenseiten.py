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


class Verkehr(unittest.TestCase):
    """Regeln der Themenseite Verkehr und Mobilität (themenseiten/verkehr.py) und die Erweiterungen dafür:
    Regel nach Thema, Ausschluss, ganzes Verfahren nur über die Stammvorlage, Punkte nur aus bestimmten Gremien,
    Gliederung nach Stadtbezirk."""

    def setUp(self):
        from pipeline.themenseiten import verkehr

        def v(ref, name, gremien=("Ausschuss für Mobilität und Verkehr",), bezirk=None, thema=True, art="Antrag"):
            p = vorlage(ref, name, amt="61 Stadtplanungsamt", gremien=gremien)
            p["paper_type"] = art
            p["themes"] = [{"theme": "verkehr", "method": "amt", "evidence": "61-3 Stadtverkehr"}] if thema else []
            p["locations"] = [{"stadtbezirk": bezirk}] if bezirk else []
            return p
        self.t = verkehr.THEMA
        cache = {
            "a": v("261900", "Neuer Radweg an der Hauptstraße", bezirk="Beuel"),
            "b": v("261901", "Gehwegparken in der Lindenstraße", gremien=("Bezirksvertretung Beuel",), bezirk="Beuel"),
            "c": v("261902", "Fahrradparkhaus am Bahnhof"),
            "d": v("261903", "Pflegearbeiten im Verkehrsgrün"),
            "e": v("261904", "Fortschreibung des Nahverkehrsplans", art="Beschlussvorlage"),
            "f": v("261904-01 AA", "Ergänzungsantrag: Ersatzverkehr während der Sperrung der Nordbrücke"),
            "g": v("261905", "Sperrung der Nordbrücke: Maßnahmen", thema=False, art="Beschlussvorlage"),
            "h": v("261905-01 ST", "Stellungnahme der Verwaltung", thema=False, art="Stellungnahme der Verwaltung"),
            "i": v("261906", "Beleuchtung am Wasserland", gremien=("Bezirksvertretung Bonn",), bezirk="Bonn"),
        }
        self.d = dossier.daten(self.t, cache, {}, [], "2026-10-26", {})
        self.by = {r["reference"]: (s["key"], r["grund"]) for s in self.d["straenge"] for r in s["vorlagen"]}

    def test_straenge(self):
        self.assertEqual(self.by["261900"], ("rad_fuss", "Thema „Verkehr und Mobilität“ (61-3 Stadtverkehr); "
                                             "Titel: „Radweg“"))
        self.assertEqual(self.by["261901"][0], "parken")  # Gehwegparken: Parken vor Rad und Fuß
        self.assertEqual(self.by["261902"][0], "bus_bahn")  # „Bahnhof“; Fahrradparkhaus zählt nicht als Parken
        self.assertNotIn("261903", self.by)  # Verkehrsgrün ausgeschlossen
        self.assertEqual(self.by["261904"][0], "bus_bahn")  # Änderungsantrag zieht das Verfahren nicht mit
        self.assertEqual(self.by["261904-01 AA"], ("nordbruecke", "Titel: „Nordbrücke“"))
        self.assertEqual(self.by["261905-01 ST"], ("nordbruecke", "Verfahren 261905; Titel: „Nordbrücke“"))
        self.assertEqual(self.by["261906"][0], "weitere")

    def test_punkte_nur_aus_rat_und_mobilitaetsausschuss(self):
        refs = {p["reference"] for p in self.d["punkte"]}
        self.assertIn("261900", refs)
        self.assertNotIn("261901", refs)  # nur in der Bezirksvertretung beraten
        self.assertEqual({p["bahn"] for p in self.d["punkte"] if p["reference"] == "261900"}, {"mobil"})

    def test_weitere_nach_stadtbezirk(self):
        weitere = next(s for s in self.d["straenge"] if s["key"] == "weitere")
        self.assertEqual([r["bezirk"] for r in weitere["vorlagen"]], ["Bonn"])
        self.assertNotIn("bezirk", next(s for s in self.d["straenge"] if s["key"] == "rad_fuss")["vorlagen"][0])
        html = dossier.body(self.t, self.d, "../../")
        self.assertIn("<summary>Bonn (1)</summary>", html)
        self.assertIn("Terminplan 261064", html)  # Haushaltsbahn wie bei Kultur

    def test_regeln_nach_pruefung(self):
        """Prüfung im Gespräch 26.10.2026 (verkehr/PRUEFUNG.md): Änderungen A bis E."""
        from pipeline.themenseiten import verkehr
        t = verkehr.THEMA

        def zu(name, thema=True):
            p = vorlage("262000", name)
            p["themes"] = [{"theme": "verkehr", "evidence": "61-3 Stadtverkehr"}] if thema else []
            return (dossier.zuordnen(t, p) or (None,))[0]
        self.assertEqual(zu("Übernahme der Parkplätze am Bahnhof"), "parken")  # A
        self.assertEqual(zu("Fahrrad- und Lastenradstellplätze an der Kita"), "rad_fuss")  # B
        self.assertEqual(zu("Stellplätze für Pkw"), "parken")
        self.assertEqual(zu("Prüfung der Park- und Verkehrssituation"), "parken")  # C
        self.assertIsNone(zu("Leerung der Altglascontainer an der Bushaltestelle"))  # D
        self.assertIsNone(zu("Abwasserbeseitigungskonzept 2024-2029"))
        self.assertEqual(zu("Überholverbot für einspurige Fahrzeuge", thema=False), "rad_fuss")  # E
        self.assertEqual(zu("Lärmschutzmaßnahmen Autobahn", thema=False), "weitere")
        self.assertIsNone(zu("Kita-Neubau in der Riemannstraße", thema=False))

    def test_veroeffentlicht_mit_uebersicht(self):
        self.assertIn(self.t.key, [t.key for t in ALLE])
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            src = site / "data" / "export" / "bonn" / "dossiers" / "verkehr.json"
            src.parent.mkdir(parents=True)
            src.write_text(json.dumps(self.d))
            self.assertEqual(dossier.uebersicht(ALLE, site, "https://example.org/", gebietsseiten._page), [])
            dossier.write(self.t, site, "https://example.org/", gebietsseiten._page)
            self.assertEqual(dossier.uebersicht(ALLE, site, "https://example.org/", gebietsseiten._page), ["thema/"])
            html = (site / "thema" / "index.html").read_text()
        self.assertIn('<a href="../thema/verkehr-und-mobilitaet/"><strong>Verkehr und Mobilität</strong></a> (8 Vorlagen)',
                      html)
        self.assertNotIn("kultur-und-haushalt", html)  # ohne Daten keine Zeile


class Schule(unittest.TestCase):
    """Regelentwurf der Themenseite Schule und Bildung (themenseiten/schule.py, Entwurf): Bedingung im Titel
    (Schulwort und Merkmal des Strangs), Schulamt und Schulausschuss, Ausschluss von Kitas und Sammellisten."""

    def setUp(self):
        from pipeline.themenseiten import schule

        def v(ref, name, amt="85 Städtisches Gebäudemanagement", gremien=("Bezirksvertretung Bonn",)):
            p = vorlage(ref, name, amt=amt, gremien=gremien)
            p["themes"], p["locations"] = [], []
            return p
        self.t = schule.THEMA
        cache = {
            "a": v("261900", "Querungshilfe vor der Grundschule Endenich"),
            "b": v("261901", "Sanierung der Toiletten am Beethoven-Gymnasium"),
            "c": v("261902", "Erhöhung der Zügigkeit der Gesamtschule Beuel"),
            "d": v("261903", "Schulbuchbeschaffung", amt="40 Schulamt"),
            "e": v("261904", "Anfrage: ABC-Klassen", amt="01 Ratsbüro", gremien=("Schulausschuss",)),
            "f": v("261905", "Sanierung des Rathauses"),
            "g": v("261906", "Neubau der Kita an der Schulstraße"),
            "h": v("261907", "Tagesordnungspunkte in nichtöffentlicher Sitzung", amt="40 Schulamt"),
            "i": v("261908", "Neubau der Musikschule"),
            "j": v("261909", "Abbau von Altschulden"),
            "k": v("261910", "Schulstraße in Lengsdorf - Gehwegergänzung"),
            "l": v("261911", "Kleine Anfrage zu Schulstraßen"),
            "m": v("261912", "Betreuungsangebot für Vorschulkinder"),
            "n": v("261913", "Errichtung einer Schranke am Berufskolleg"),
            "o": v("261914", "Errichtung einer dritten Gesamtschule in Beuel"),
        }
        self.d = dossier.daten(self.t, cache, {}, [], "2026-10-26", {})
        self.by = {r["reference"]: (s["key"], r["grund"]) for s in self.d["straenge"] for r in s["vorlagen"]}

    def test_straenge(self):
        self.assertEqual(self.by["261900"], ("schulweg", "Titel: „Querungshilfe“ und „Grundschule“"))
        self.assertEqual(self.by["261901"][0], "bau")
        self.assertEqual(self.by["261902"][0], "plaetze")
        self.assertEqual(self.by["261903"], ("weitere", "federführend: 40 Schulamt"))
        self.assertEqual(self.by["261904"], ("weitere", "Beratung im Schulausschuss"))

    def test_ohne_schulwort_und_ausschluss(self):
        for ref in ("261905", "261906", "261907", "261908", "261909"):
            self.assertNotIn(ref, self.by, ref)

    def test_regeln_nach_pruefung(self):
        # A: „Schulstraße“ in der Einzahl ist ein Straßenname, „Schulstraßen“ zählen
        self.assertNotIn("261910", self.by)
        self.assertEqual(self.by["261911"], ("schulweg", "Titel: „Schulstraßen“"))
        # B: Errichtung nur einer Schule; C: „Vorschul…“ ist kein Schulwort
        self.assertEqual(self.by["261913"], ("weitere", "Titel: „Berufskolleg“"))
        self.assertEqual(self.by["261914"][0], "plaetze")
        self.assertNotIn("261912", self.by)

    def test_veroeffentlicht(self):
        from pipeline.themenseiten import ENTWUERFE
        self.assertIn(self.t.key, [t.key for t in ALLE])
        self.assertNotIn(self.t, ENTWUERFE)


class Wohnen(unittest.TestCase):
    """Regelentwurf der Themenseite Wohnen und Bauen (themenseiten/wohnen.py, Entwurf): Reihenfolge der Titelregeln,
    Zuständigkeit ohne Verkehr (ohne_thema), Ausschluss von Bühnen und „Miet…“ ohne Wohnbezug."""

    def setUp(self):
        from pipeline.themenseiten import wohnen

        def v(ref, name, amt="01-2 Ratsbüro", gremien=("Bezirksvertretung Bonn",), themen=()):
            p = vorlage(ref, name, amt=amt, gremien=gremien)
            p["themes"] = [{"theme": t, "method": "stichwort", "evidence": t} for t in themen]
            p["locations"] = []
            return p
        self.t = wohnen.THEMA
        cache = {
            "a": v("261900", "Verfahrensbeschleunigung in der Bauleitplanung"),
            "b": v("261901", "Bebauungsplan Nr. 1234-5 „Am Bach“ mit gefördertem Wohnraum"),
            "c": v("261902", "Antrag: Housing First"),
            "d": v("261903", "Eintragung in die Denkmalliste"),
            "e": v("261904", "Tempo 30 vor einem denkmalgeschützten Haus", themen=("verkehr",)),
            "f": v("261905", "Nutzungsänderung eines Ladens", amt="63 Bauordnungsamt"),
            "g": v("261906", "Neue Ampel an der Kreuzung", amt="61 Stadtplanungsamt", themen=("verkehr",)),
            "h": v("261907", "Fahrradmietsystem: neue Stationen"),
            "i": v("261908", "Zukunft Bonner Bühnen: Denkmalschutz"),
            "j": v("261909", "Sachstand", gremien=("Ausschuss für Planen, Bauen und Denkmalschutz",)),
        }
        self.d = dossier.daten(self.t, cache, {}, [], "2026-10-26", {})
        self.by = {r["reference"]: (s["key"], r["grund"]) for s in self.d["straenge"] for r in s["vorlagen"]}

    def test_straenge(self):
        self.assertEqual(self.by["261900"][0], "turbo")  # vor Bebauungsplänen
        self.assertEqual(self.by["261901"][0], "bebauungsplan")  # vor Wohnraum
        self.assertEqual(self.by["261902"], ("wohnraum", "Titel: „Housing First“"))
        self.assertEqual(self.by["261903"][0], "denkmal")
        self.assertEqual(self.by["261905"], ("weitere", "federführend: 63 Bauordnungsamt"))
        self.assertEqual(self.by["261909"][0], "weitere")

    def test_ohne_verkehr_und_ausschluss(self):
        for ref in ("261904", "261906", "261907", "261908"):
            self.assertNotIn(ref, self.by, ref)

    def test_entwurf_ohne_seite(self):
        from pipeline.themenseiten import ENTWUERFE
        self.assertIn(self.t, ENTWUERFE)
        self.assertNotIn(self.t.key, [t.key for t in ALLE])
