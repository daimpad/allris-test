import json
import tempfile
import unittest
from pathlib import Path

from pipeline import kandidaten


def site(bez="Siemensstraße", von="03.08.2026", traeger="Bundesstadt Bonn - Amt 66-2", massnahme="Straßenbau",
         lon=7.0712, lat=50.7299):
    return {"bezeichnung": bez, "adresse": f"{bez} 50", "von": von, "bis": "31.12.2026", "traeger": traeger,
            "massnahme": massnahme, "lon": lon, "lat": lat}


def paper(ref="240553", name="Umgestaltung der Siemensstraße – Vorplanung", amt="66 Tiefbauamt", stand="entschieden",
          decided="2024-05-28", street="Siemensstraße", lon=7.0713, lat=50.7299, method="strasse", typ="Beschlussvorlage"):
    return {"reference": ref, "name": name, "paper_type": typ, "amt": amt, "stand": stand, "responsibility": [], "themes": [],
            "steps": [{"typ": "beratung", "date": "2024-05-01"}, {"typ": "entscheidung", "date": decided}],
            "locations": [{"level": "strasse", "name": street, "lon": lon, "lat": lat, "method": method}]}


class Hilfen(unittest.TestCase):
    def test_strassennamen(self):
        self.assertEqual(kandidaten.street("Siemensstraße 50"), "siemensstraße")
        self.assertEqual(kandidaten.street("Siemensstr."), "siemensstraße")
        self.assertEqual(kandidaten.street("Hermann-Wandersleb-Ring (B56)"), "hermann-wandersleb-ring")
        self.assertEqual(kandidaten.street("Kölnstraße 464-480"), "kölnstraße")

    def test_stichwort_passend_zur_massnahme(self):
        self.assertTrue(kandidaten.build_word("Ausbau Siemensstraße", "Straßenbau"))
        self.assertFalse(kandidaten.build_word("Ausbau Siemensstraße", "Kanalbau"))
        self.assertTrue(kandidaten.build_word("Kanalsanierung Siemensstraße", "Kanalbau"))
        self.assertFalse(kandidaten.build_word("Aufhebung der Radwegbenutzungspflicht", "Straßenbau"))

    def test_abstand(self):
        self.assertAlmostEqual(kandidaten.distance_m(7.0, 50.0, 7.0, 50.001), 111, delta=1)


class Kandidaten(unittest.TestCase):
    def test_konfidenz_stufen(self):
        sites = {"1": site()}
        papers = [paper(),
                  paper("2", "Tempo 30 in der Siemensstraße", amt="61-3 Stadtverkehr"),
                  paper("3", "Bänke Ecke Wenzelgasse", amt="67 Grün", street="Wenzelgasse")]
        got = {c["drucksache"]: c for c in kandidaten.candidates(sites, papers)}
        self.assertEqual({k: v["konfidenz"] for k, v in got.items()}, {"240553": "hoch", "2": "mittel", "3": "niedrig"})
        c = got["240553"]
        self.assertEqual((c["kriterium_strasse"], c["kriterium_thema"], c["kriterium_stichwort"], c["pruefvermerk"]),
                         ("ja", "ja", "ja", "ungeprüft"))
        self.assertIn("Baubeginn 03.08.2026 nach Entscheidung 28.05.2024", c["begruendung"])

    def test_nur_baubeschluesse_hoch(self):
        sites = {"1": site()}
        papers = [paper(), paper("212110", "Bürgerantrag: Ausbauplanung Siemensstraße", typ="Bürgerantrag § 24 GO - Öffentlich"),
                  paper("240553-01 AA", "Änderungsantrag: Umgestaltung der Siemensstraße", typ="Änderungsantrag")]
        got = {c["drucksache"]: c for c in kandidaten.candidates(sites, papers)}
        self.assertEqual({k: v["konfidenz"] for k, v in got.items()}, {"240553": "hoch", "212110": "mittel", "240553-01 AA": "mittel"})
        self.assertIn("kein Baubeschluss (Bürgerantrag § 24 GO - Öffentlich)", got["212110"]["begruendung"])

    def test_ausschluesse(self):
        sites = {"1": site()}
        papers = [paper("früh", decided="2026-09-01"),            # Baustelle beginnt vor der Entscheidung
                  paper("offen", stand="in Beratung"),            # nicht entschieden
                  paper("fern", lon=7.0800),                      # mehr als 150 m
                  paper("geerbt", method="vererbt")]              # nur von übergeordneter Vorlage geerbt
        self.assertEqual(kandidaten.candidates(sites, papers), [])

    def test_fremder_traeger_getrennt(self):
        got = kandidaten.candidates({"1": site(traeger="SWB Bonn-Netz")}, [paper()])
        self.assertEqual([c["konfidenz"] for c in got], ["fremd"])
        self.assertIn("fremder Träger (SWB Bonn-Netz)", got[0]["begruendung"])
        self.assertEqual(kandidaten.sample(got), [])

    def test_stichprobe_ein_vorgang_je_baustelle(self):
        sites = {"1": site(), "2": site("Gerichtsweg", lon=7.0900, lat=50.7400)}
        papers = [paper(), paper("240553-01 ST", "Stellungnahme: Umgestaltung der Siemensstraße"),
                  paper("210801", "Ausbau Siemensstraße"),
                  paper("230332", "Ausbau der Straße Gerichtsweg", street="Gerichtsweg", lon=7.0900, lat=50.7400)]
        refs = [(c["baustelle_id"], c["drucksache"]) for c in kandidaten.sample(kandidaten.candidates(sites, papers))]
        self.assertEqual(refs, [("1", "210801"), ("1", "240553"), ("2", "230332")])

    def test_baustellen_aus_archiv(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = {"1": {"aktiv": True, "angaben": site()}, "2": {"aktiv": False, "angaben": site()}}
            (Path(tmp) / "baustellen.json").write_text(json.dumps(state), encoding="utf-8")
            sites, origin = kandidaten.load_sites(tmp)
            self.assertEqual((list(sites), origin), (["1"], "Archiv"))
            sites, origin = kandidaten.load_sites(Path(tmp) / "fehlt", fetcher=lambda thema: ([], 1))
            self.assertEqual((sites, origin), ({}, "Feed 14698 (direkt)"))


class Seite(unittest.TestCase):
    def test_ohne_hausnummer(self):
        self.assertEqual(kandidaten.without_number("Kölnstraße 464-480"), "Kölnstraße")
        self.assertEqual(kandidaten.without_number("Siemensstraße 50 a"), "Siemensstraße")
        self.assertEqual(kandidaten.without_number("Am Burgweiher"), "Am Burgweiher")

    def test_seitendaten_nur_hoch(self):
        state = {"1": {"angaben": site(), "aktiv": True, "first_seen": "2026-10-19", "aenderungen": [
                       {"datum": "2026-10-20", "feld": "bis", "alt": "31.12.2026", "neu": "31.03.2027"},
                       {"datum": "2026-10-20", "feld": "sperrung", "alt": "a", "neu": "b"}]},
                 "2": {"angaben": site("Gerichtsweg", lon=7.09, lat=50.74), "aktiv": False, "first_seen": "2026-10-19", "entfallen": "2026-10-21"}}
        papers = [paper(), paper("2", "Tempo 30 in der Siemensstraße", amt="61-3 Stadtverkehr")]
        d = kandidaten.site_data(state, papers, "Archiv", "2026-10-21T05:23:00+00:00")
        b = {x["id"]: x for x in d["baustellen"]}
        self.assertEqual([c["drucksache"] for c in b["1"]["kandidaten"]], ["240553"])  # „mittel“ entfällt
        self.assertEqual((b["1"]["strasse"], b["1"]["von"], b["1"]["fremd"], b["2"]["aktiv"]), ("Siemensstraße", "2026-08-03", False, False))
        self.assertEqual([a["feld"] for a in b["1"]["aenderungen"]], ["bis"])
        self.assertEqual(d["meta"]["archiv_beginn"], "2026-10-19")

    def test_rueckfall_auf_feeds_und_leere_liste(self):
        feature = {"type": "Feature", "geometry": {"type": "Point", "coordinates": [7.0712, 50.7299]},
                   "properties": {"baustelle_id": 9746, **{k: v for k, v in site().items() if k not in ("lon", "lat")},
                                  "stadtbezirk_bez": "Bonn"}}
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "bonn"
            (out / "ortsteile").mkdir(parents=True)
            (out / "ortsteile" / "x.json").write_text(json.dumps({"papers": [paper()]}), encoding="utf-8")
            d = kandidaten.write_site(out, Path(tmp) / "fehlt", fetcher=lambda thema: ([feature], 1))
            self.assertEqual((d["meta"]["herkunft"], len(d["baustellen"]), len(d["baustellen"][0]["kandidaten"])), ("Feeds (ohne Archiv)", 1, 1))

            def broken(thema):
                raise RuntimeError("HTTP 400")
            d = kandidaten.write_site(out, Path(tmp) / "fehlt", fetcher=broken)
            self.assertEqual((d["baustellen"], d["meta"]["fehler"]), ([], "Baustellen derzeit nicht abrufbar"))
            self.assertTrue((out / "baustellen.json").exists())


if __name__ == "__main__":
    unittest.main()
