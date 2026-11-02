"""Allgemeine Themenseiten (pipeline/themenseiten/, dossier.py, prozessbild.py): Die Kulturseite bleibt nach dem
Umbau Zeichen für Zeichen gleich (Referenz in tests/referenz/, erzeugt vor dem Umbau am 26.10.2026; am 27.10.2026 um
die Abschnitte „Haushalt im Produktbereich“ und „Wer berät mit“ sowie die Sprungleiste und den Link auf haushalt/ ergänzt,
am 28.10.2026 um target="_blank" an externen Links, die Feed-Erkennung im Kopf und den Link auf rss/, am 02.11.2026 um den
Link in die Kachel des Produktbereichs auf haushalt/ und das Akkordeon „Begriffe auf dieser Seite“, im Fuß der Link
auf einfach/); dazu die
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


# Besetzung des Fachausschusses fest vorgegeben (die Datei data/raw/besetzung.json ändert sich mit jedem Abruf)
AUSSCHUSS = {"name": "Kulturausschuss", "id": "17", "mitglieder": 21, "ohne_fraktion": 9, "sachkundig": 9, "stichtag": "2026-10-27",
             "vorsitz": [{"name": "Anna Beispiel", "rolle": "Vorsitz", "fraktion": "Beispiel-Fraktion"}],
             "sitze": [{"fraktion": "Beispiel-Fraktion", "n": 7}, {"fraktion": "Andere Fraktion", "n": 5}]}


def _kultur_daten():
    alt, dossier.fachausschuss = dossier.fachausschuss, lambda t, **kw: AUSSCHUSS
    try:
        return _kultur_daten_ohne()
    finally:
        dossier.fachausschuss = alt


def _kultur_daten_ohne():
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
        self.assertIn('<h2><a href="../thema/verkehr-und-mobilitaet/">Verkehr und Mobilität</a></h2>', html)
        self.assertIn('<p class="kachel-zahl"><strong>8</strong> Vorlagen in 5 Strängen</p>', html)
        self.assertIn('class="kachel-symbol"', html)
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
            "k": v("261910", "Aufhebung des Fluchtlinienplans B 1"),
            "l": v("261911", "Straßenbenennung in Dransdorf", amt="63 Bauordnungsamt"),
            "m": v("261912", "Fortführung des Quartiersmanagements in Auerberg", amt="50 Amt für Soziales und Wohnen"),
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

    def test_regeln_nach_pruefung(self):
        self.assertEqual(self.by["261910"][0], "bebauungsplan")  # A: Fluchtlinienplan
        self.assertNotIn("261911", self.by)  # B: Straßenbenennung
        self.assertEqual(self.by["261912"], ("weitere", "Titel: „Quartiersmanagements“"))  # C: Stadtentwicklung

    def test_veroeffentlicht(self):
        from pipeline.themenseiten import ENTWUERFE
        self.assertIn(self.t.key, [t.key for t in ALLE])
        self.assertNotIn(self.t, ENTWUERFE)


class Klima(unittest.TestCase):
    """Regelentwurf der Themenseite Klima und Umwelt (themenseiten/klima.py, Entwurf): Titelregeln ohne Verkehr,
    Umweltamt und Umweltausschuss, Sondervermögen kein Klimaschutz."""

    def setUp(self):
        from pipeline.themenseiten import klima

        def v(ref, name, amt="01-2 Ratsbüro", gremien=("Bezirksvertretung Bonn",), themen=()):
            p = vorlage(ref, name, amt=amt, gremien=gremien)
            p["themes"] = [{"theme": t, "method": "stichwort", "evidence": t} for t in themen]
            p["locations"] = []
            return p
        self.t = klima.THEMA
        cache = {
            "a": v("261900", "Fortschreibung Klimaplan"),
            "b": v("261901", "Hitzeschutz in Seniorenheimen"),
            "c": v("261902", "Neufassung der Baumschutzsatzung"),
            "d": v("261903", "Mehrweg statt Einweg: Verpackungssteuer"),
            "e": v("261904", "Gebührenkalkulation des Friedhofswesens", amt="67 Amt für Umwelt und Stadtgrün"),
            "f": v("261905", "Regionales Fahrradmietsystem nach Maßgabe des Klimasteckbriefes", themen=("verkehr",)),
            "g": v("261906", "Sondervermögen „Infrastruktur und Klimaneutralität“"),
            "h": v("261907", "Baumaßnahme an der Schule"),
            "i": v("261908", "Rasenmähroboter", gremien=("Ausschuss für Umwelt, Klima und Lokale Agenda",)),
            "j": v("261909", "Toilettensituation am Eingang der Rheinaue"),
            "k": v("261910", "Bonner Leitlinien zum „Bau-Turbo“", gremien=("Ausschuss für Umwelt, Klima und Lokale Agenda",)),
            "l": v("261911", "Heimische Fauna vor Neozoen schützen", amt="67 Amt für Umwelt und Stadtgrün"),
            "m": v("261912", "Lärmbelastung durch den Schienengüterverkehr"),
            "n": v("261913", "Klimagerechtes Hof- und Fassadenprogramm"),
        }
        self.d = dossier.daten(self.t, cache, {}, [], "2026-10-26", {})
        self.by = {r["reference"]: (s["key"], r["grund"]) for s in self.d["straenge"] for r in s["vorlagen"]}

    def test_straenge(self):
        self.assertEqual(self.by["261900"][0], "klimaschutz")
        self.assertEqual(self.by["261901"][0], "anpassung")
        self.assertEqual(self.by["261902"][0], "gruen")
        self.assertEqual(self.by["261903"][0], "abfall")
        self.assertEqual(self.by["261904"], ("weitere", "federführend: 67 Amt für Umwelt und Stadtgrün"))
        self.assertEqual(self.by["261908"], ("weitere", "Beratung im Ausschuss für Umwelt, Klima und Lokale Agenda"))

    def test_ohne_verkehr_und_fehltreffer(self):
        for ref in ("261905", "261906", "261907"):
            self.assertNotIn(ref, self.by, ref)

    def test_regeln_nach_pruefung(self):
        self.assertEqual(self.by["261909"][0], "weitere")  # A: Toiletten in Parks
        self.assertNotIn("261910", self.by)  # B: Bau-Turbo auf der Seite Wohnen und Bauen
        self.assertEqual(self.by["261911"][0], "gruen")  # C: Artenschutz
        self.assertEqual(self.by["261912"], ("weitere", "Titel: „Lärmbelastung“"))  # D: Lärm
        self.assertEqual(self.by["261913"][0], "klimaschutz")  # E: klimagerecht

    def test_veroeffentlicht(self):
        from pipeline.themenseiten import ENTWUERFE
        self.assertIn(self.t.key, [t.key for t in ALLE])
        self.assertNotIn(self.t, ENTWUERFE)


class Kinder(unittest.TestCase):
    """Themenseite Kinder, Jugend und Familie (themenseiten/kinder.py): Titelregeln, Kitas als Ortsangabe beim Verkehr,
    Beirat nur mit Kindern oder Jugend im Titel, Ganztag auf der Schulseite; Regeln A und B nach der Prüfung."""

    def setUp(self):
        from pipeline.themenseiten import kinder

        def v(ref, name, amt="01-2 Ratsbüro", gremien=("Bezirksvertretung Bonn",), themen=()):
            p = vorlage(ref, name, amt=amt, gremien=gremien)
            p["themes"] = [{"theme": t, "method": "stichwort", "evidence": t} for t in themen]
            p["locations"] = []
            return p
        self.t = kinder.THEMA
        cache = {
            "a": v("261900", "Kita-Neubau an der Riemannstraße"),
            "b": v("261901", "Halteverbot vor der Kita am Markt", themen=("verkehr",)),
            "c": v("261902", "Umbau des Kinderspielplatzes Königsberger Weg"),
            "d": v("261903", "Fortschreibung des Kinder- und Jugendförderplans: Jugendarbeit"),
            "e": v("261904", "Arbeit der Frühen Hilfen Bonn"),
            "f": v("261905", "Kinder- und Jugendrechtewoche und Weltkindertag"),
            "g": v("261906", "Sachstand Personal", amt="51 Amt für Kinder, Jugend und Familie"),
            "h": v("261907", "Bericht aus dem Beirat", gremien=("Beirat Kinder- und Jugendbeteiligung",)),
            "i": v("261908", "Wünsche von Kindern an die Stadt", gremien=("Beirat Kinder- und Jugendbeteiligung",)),
            "j": v("261909", "Ausbau des Offenen Ganztags", amt="51 Amt für Kinder, Jugend und Familie"),
            "k": v("261910", "Neubau eines Einfamilienhauses"),
            "l": v("261911", "Tagesordnungspunkte in nichtöffentlicher Sitzung",
                   gremien=("Ausschuss für Kinder, Jugend und Familie",)),
            # vor dem Ziehen des Prüfbogens korrigiert (02.11.2026)
            "m": v("261912", "Antrag: Parksituation Zuwegung Kita In der Raste"),
            "n": v("261913", "Marktverzeichnis 2026 - Hier: Jubiläums-, Freundes- und Familienfest"),
            "o": v("261914", "Elternbefragung zum Bedarf an Gesamtschulplätzen"),
            "p": v("261915", "Deutsche Meisterschaft im Vert Skateboarding 2026"),
            "q": v("261916", "Organisationsuntersuchung im Amt für Kinder, Jugend und Familie",
                   amt="51 Amt für Kinder, Jugend und Familie"),
            "r": v("261917", "Zuschuss an den Verband binationaler Familien"),
            # nach der Prüfung (02.11.2026): A Bauen nicht allein über die Beratung im Ausschuss, B junge Menschen
            "s": v("261918", "Evaluation Baulandmodell", amt="61 Stadtplanungsamt",
                   gremien=("Ausschuss für Kinder, Jugend und Familie",), themen=("bauen",)),
            "t": v("261919", "Überplanmäßige Ausgaben im Dezernat 5", gremien=("Ausschuss für Kinder, Jugend und Familie",)),
            "u": v("261920", "Evaluation des freien Eintritts für Kinder und Jugendliche während der Sommerferien"),
            "w": v("261921", "Sichere Mobilität von Kindern und Jugendlichen - Tempo 30", themen=("verkehr",)),
            "x": v("261922", "Vertretung von Kindern und Jugendlichen im Klimabeirat",
                   gremien=("Beirat Kinder- und Jugendbeteiligung",)),
        }
        self.d = dossier.daten(self.t, cache, {}, [], "2026-11-02", {})
        self.by = {r["reference"]: (s["key"], r["grund"]) for s in self.d["straenge"] for r in s["vorlagen"]}

    def test_straenge(self):
        self.assertEqual(self.by["261900"], ("kita", "Titel: „Kita-Neubau“"))
        self.assertEqual(self.by["261902"][0], "spiel")
        self.assertEqual(self.by["261903"][0], "jugend")
        self.assertEqual(self.by["261904"][0], "familie")
        self.assertEqual(self.by["261905"][0], "beteiligung")
        self.assertEqual(self.by["261906"], ("weitere", "federführend: 51 Amt für Kinder, Jugend und Familie"))
        self.assertEqual(self.by["261908"], ("beteiligung", "Beratung im Beirat Kinder- und Jugendbeteiligung; Titel: „Kindern“"))

    def test_abgrenzung(self):
        # Kita als Ortsangabe beim Verkehr, Beirat ohne Kinder/Jugend im Titel, Ganztag (Schulseite), Haustyp, Formalien
        for ref in ("261901", "261907", "261909", "261910", "261911", "261912", "261913", "261914", "261915"):
            self.assertNotIn(ref, self.by, ref)
        self.assertEqual(self.by["261916"], ("weitere", "federführend: 51 Amt für Kinder, Jugend und Familie"))
        self.assertEqual(self.by["261917"][0], "familie")

    def test_regeln_nach_pruefung(self):
        self.assertNotIn("261918", self.by)  # A
        self.assertEqual(self.by["261919"], ("weitere", "Beratung im Ausschuss für Kinder, Jugend und Familie"))
        self.assertEqual(self.by["261920"], ("weitere", "Titel: „für Kinder und Jugendliche“"))  # B
        self.assertNotIn("261921", self.by)  # B ohne Verkehr
        self.assertEqual(self.by["261922"][0], "beteiligung")  # Beirat vor Regel B

    def test_veroeffentlicht(self):
        from pipeline.themenseiten import ENTWUERFE
        self.assertIn(self.t.key, [t.key for t in ALLE])
        self.assertNotIn(self.t, ENTWUERFE)
        self.assertEqual([k for k, *_ in self.t.straenge], ["kita", "spiel", "jugend", "familie", "beteiligung", "weitere"])


class Soziales(unittest.TestCase):
    """Entwurf der Themenseite Soziales, Gesundheit und Integration (themenseiten/soziales.py): Abgrenzung zu Wohnen
    (Regel-Feld ohne_seite, Wohnungslosigkeit und Unterkünfte auf beiden Seiten), Fehltreffer vor dem Ziehen des
    Prüfbogens, Zuschüsse unter „weitere“."""

    def setUp(self):
        from pipeline.themenseiten import soziales, wohnen

        def v(ref, name, amt="01-2 Ratsbüro", gremien=("Rat",), themen=()):
            p = vorlage(ref, name, amt=amt, gremien=gremien)
            p["themes"] = [{"theme": t, "method": "stichwort", "evidence": t} for t in themen]
            p["locations"] = []
            return p
        self.t, self.wohnen = soziales.THEMA, wohnen.THEMA
        a50, a05 = "50 Amt für Soziales und Wohnen", "05 Amt für Integration und Vielfalt"
        self.cache = {
            # Wohnen bleibt auf der Seite Wohnen und Bauen
            "a": v("261900", "Fortschreibung des Bonner Mietspiegels 2026", amt=a50),
            "b": v("261901", "Wohnen in Bonn hier: Handlungskonzept Wohnen Bonn", amt=a50),
            "c": v("261902", "Programm zur Förderung von gemeinwohlorientierten Wohnprojekten", amt=a50),
            "d": v("261903", "Bebauungsplan Nr. 1234-5 Pflegeheim am Beispielweg", amt="61 Stadtplanungsamt"),
            # Wohnungslosigkeit und Unterkünfte auf beiden Seiten
            "e": v("261904", "Grüne-Antrag: Housing First", amt=a50),
            "f": v("261905", "Wohnungen für Wohnungslose", amt=a50),
            "g": v("261906", "Satzung über Unterkünfte für obdachlose und geflüchtete Menschen", amt=a50),
            "h": v("261907", "Wohnprojekt für Wohnungslose", amt=a50),
            # übrige Vorlagen der Ämter und Ausschüsse
            "i": v("261908", "Sachstand Personal", amt=a50),
            "j": v("261909", "Bericht über das Bürgerschaftliche Engagement",
                   gremien=("Ausschuss für Chancengerechtigkeit und Integration",)),
            # Fehltreffer vor dem Ziehen des Prüfbogens (02.11.2026)
            "k": v("261910", "Aufstellung eines Gedenksteins/-tafel"),
            "l": v("261911", "Pflege und Erneuerung der städtischen Grünflächen"),
            "m": v("261912", "Arbeitspaket „Migrationsunterstützung UDP“"),
            "n": v("261913", "Pilotprojekt: Integration von Bordsteinladesäulen in das Stadtgebiet"),
            "o": v("261914", "Barrierefreier Umbau der Haltestelle Markt"),
            "p": v("261915", "Barrierefreiheit im Stadthaus", amt=a50),
            "q": v("261916", "Wahl des/der Vorsitzenden des Ausschusses für Chancengerechtigkeit und Integration",
                   amt=a05),
            "r": v("261917", "Bestellung von Mitgliedern des Rates für den Ausschuss für Chancengerechtigkeit und "
                             "Integration", amt=a05),
            "s": v("261918", "Künftige Unterbringung des Stadtmuseums"),
            "t": v("261919", "Dialogforum Biodiversität"),
            "u": v("261920", "Zuschuss an den Verein Beispiel e.V.", amt=a05),
            "w": v("261921", "Bezuschussung MobilPass-Tickets aus Bonn-Ausweis-Mitteln", amt=a50),
            "x": v("261922", "Grüne Anfrage: Zukunft Bonner Tafel"),
            "y": v("261923", "Seniorenzentren Wirtschaftsplan 2026", amt="Seniorenzentren der Bundesstadt Bonn"),
            "z": v("261924", "Maßnahmen zur Bewältigung des Drogenkonsums"),
            "aa": v("261925", "Sicherheit auf dem Radweg vor dem Ärztehaus", themen=("verkehr",)),
        }
        self.d = dossier.daten(self.t, self.cache, {}, [], "2026-11-02", {})
        self.by = {r["reference"]: (s["key"], r["grund"]) for s in self.d["straenge"] for r in s["vorlagen"]}

    def test_wohnen_bleibt_auf_der_wohnseite(self):
        for ref in ("261900", "261901", "261902", "261903"):
            self.assertNotIn(ref, self.by, ref)
        self.assertEqual(dossier.zuordnen(self.wohnen, self.cache["a"])[0], "wohnraum")

    def test_wohnungslosigkeit_auf_beiden_seiten(self):
        self.assertEqual(self.by["261904"], ("armut", "Titel: „Housing First“"))
        self.assertEqual(self.by["261905"][0], "armut")
        self.assertEqual(self.by["261906"][0], "gefluechtete")
        self.assertEqual(self.by["261907"][0], "armut")
        for k in ("e", "f"):
            self.assertEqual(dossier.zuordnen(self.wohnen, self.cache[k])[0], "wohnraum")

    def test_weitere_und_zuschuesse(self):
        self.assertEqual(self.by["261908"], ("weitere", "federführend: 50 Amt für Soziales und Wohnen"))
        self.assertEqual(self.by["261909"], ("weitere", "Beratung im Ausschuss für Chancengerechtigkeit und Integration"))
        self.assertEqual(self.by["261920"], ("weitere", "federführend: 05 Amt für Integration und Vielfalt; "
                                                        "Titel: „Zuschuss an“"))
        self.assertEqual(self.by["261921"][0], "armut")  # Bezuschussung von Tickets ist kein Zuschuss an Träger
        self.assertEqual(self.by["261922"][0], "armut")
        self.assertEqual(self.by["261923"][0], "senioren")
        self.assertEqual(self.by["261924"][0], "gesundheit")
        self.assertEqual(self.by["261915"], ("senioren", "federführend: 50 Amt für Soziales und Wohnen; "
                                                         "Titel: „Barrierefreiheit“"))

    def test_fehltreffer(self):
        for ref in ("261910", "261911", "261912", "261913", "261914", "261916", "261917", "261918", "261919",
                    "261925"):
            self.assertNotIn(ref, self.by, ref)

    def test_regeln_nach_pruefung(self):
        from pipeline import dossier
        # A: Friedhöfe und Bestattungswesen nicht, auch bei Mitberatung im ACI; muslimische Bestattungsflächen bleiben
        p = vorlage("261990", "Gebührenkalkulation des Friedhofs- und Bestattungswesens für das Jahr 2026",
                    amt="13 Amt für Umwelt", gremien=("Ausschuss für Chancengerechtigkeit und Integration",))
        self.assertIsNone(dossier.zuordnen(self.t, p))
        p = vorlage("261991", "Sicherung einer muslimischen Bestattungsfläche am Nordfriedhof")
        self.assertEqual(dossier.zuordnen(self.t, p)[0], "integration")
        # B: soziales Miteinander
        p = vorlage("261992", "Grüne/Linke-Antrag: Soziales Miteinander in der GGS Medinghoven")
        self.assertEqual(dossier.zuordnen(self.t, p)[0], "integration")

    def test_veroeffentlicht(self):
        from pipeline.themenseiten import ENTWUERFE
        self.assertNotIn(self.t, ENTWUERFE)
        self.assertIn(self.t.key, [t.key for t in ALLE])
        self.assertEqual(self.t.fachausschuss, ("Ausschuss für Soziales, Migration, Gesundheit, Wohnen und Senioren",
                                                "Ausschuss für Chancengerechtigkeit und Integration"))
        strang = {k for k, _, _ in self.t.straenge}
        self.assertLessEqual({r.strang for r in self.t.regeln}, strang)
        self.assertLessEqual(set(self.t.punkt_straenge), strang)
        self.assertLessEqual(set(self.t.bahn_gremien), {k for k, _ in self.t.bahnen})
        self.assertEqual(sum(self.t.stichprobe_je_strang.values()), 25)


class OhneSeite(unittest.TestCase):
    """Regel-Feld ohne_seite: Vorlagen, die auf einer anderen Themenseite stehen, überspringen die Regel."""

    def test_ohne_seite(self):
        andere = dossier.Thema(**{**SCHULE.__dict__, "key": "andere", "regeln": SCHULE.regeln[:1]})  # nur Neubau
        thema = dossier.Thema(**{**SCHULE.__dict__, "regeln": [
            dossier.Regel("bau", titel=re.compile(r"Wohnungslos")),
            dossier.Regel("weitere", zustaendig=dossier.Zustaendig(aemter=("40 ",)), ohne_seite=andere)]})
        neubau = vorlage("261900", "Neubau der Grundschule", amt="40 Schulamt")
        personal = vorlage("261901", "Sachstand Personal", amt="40 Schulamt")
        beides = vorlage("261902", "Neubau einer Unterkunft für Wohnungslose", amt="40 Schulamt")
        self.assertEqual(dossier.zuordnen(andere, neubau)[0], "bau")
        self.assertIsNone(dossier.zuordnen(thema, neubau))           # steht auf der anderen Seite
        self.assertEqual(dossier.zuordnen(thema, personal)[0], "weitere")
        self.assertEqual(dossier.zuordnen(thema, beides)[0], "bau")   # Regel ohne ohne_seite gilt vorher


class MehrereFachausschuesse(unittest.TestCase):
    """Kasten „Wer berät mit“ mit zwei Ausschüssen (Thema.fachausschuss als Tupel); ein Name bleibt wie bisher."""

    def setUp(self):
        self.besetzung = {
            "Sozialausschuss": dict(AUSSCHUSS, name="Sozialausschuss", id="374", ohne_fraktion=8, sachkundig=8),
            "ACI": dict(AUSSCHUSS, name="ACI", id="368", mitglieder=28, ohne_fraktion=18, sachkundig=0,
                        vorsitz=[{"name": "Anna Beispiel", "rolle": "Vorsitz IntegrationsA", "fraktion": None}],
                        ohne_fraktion_rollen=[{"rolle": "Mitglied ACI", "n": 15}, {"rolle": "Vorsitz", "n": 3}]),
        }
        self.alt = dossier._besetzung
        dossier._besetzung = lambda name, seit, orgs, path: self.besetzung.get(name)

    def tearDown(self):
        dossier._besetzung = self.alt

    def test_str_und_tupel(self):
        ein = dossier.Thema(**{**SCHULE.__dict__, "fachausschuss": "Sozialausschuss"})
        zwei = dossier.Thema(**{**SCHULE.__dict__, "fachausschuss": ("Sozialausschuss", "ACI", "fehlt")})
        self.assertEqual(dossier.fachausschuss(ein, orgs={"x": {}})["id"], "374")
        self.assertEqual([a["id"] for a in dossier.fachausschuss(zwei, orgs={"x": {}})], ["374", "368"])
        d = dossier.daten(zwei, {}, {}, [], "2026-11-02", {})
        self.assertNotIn("fachausschuss", d)
        html = dossier.body(zwei, d, "../../")
        self.assertIn('<h2 id="fachausschuss">Wer berät mit</h2>\n    <p>Zu diesem Thema beraten zwei Fachausschüsse:</p>',
                      html)
        self.assertIn('<h3 id="fachausschuss-374">Sozialausschuss</h3>', html)
        self.assertIn('<h3 id="fachausschuss-368">ACI</h3>', html)
        self.assertIn("<li>ohne Angabe einer Fraktion: 18 (darunter 15 mit der Rolle „Mitglied ACI“, 3 im Vorsitz "
                      "oder in der Stellvertretung)</li>", html)
        self.assertIn("<li>ohne Angabe einer Fraktion: 8 (darunter 8 sachkundige Bürger:innen und Einwohner:innen)</li>",
                      html)
        self.assertIn("Vorsitz IntegrationsA: Anna Beispiel.", html)
        self.assertIn('<a href="#fachausschuss">Wer berät mit</a>', html)
        self.assertEqual(html.count('?prozesse=gremien&amp;gremium='), 2)
