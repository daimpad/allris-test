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
          decided="2024-05-28", street="Siemensstraße", lon=7.0713, lat=50.7299, method="strasse"):
    return {"reference": ref, "name": name, "amt": amt, "stand": stand, "responsibility": [], "themes": [],
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


if __name__ == "__main__":
    unittest.main()
