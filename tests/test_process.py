import unittest

from pipeline import process


def cons(gremium, role="Empfehlung", authoritative=False, start=None, result=None, status="beraten"):
    return {"gremium": gremium, "role": role, "authoritative": authoritative, "start_date": start,
            "result": result, "status": status, "number": None}


def paper(ptype="Beschlussvorlage", process_=(), subordinated=(), originators=(), date="2024-03-01"):
    return {"paper_type": ptype, "date": date, "source_object": "oparl/papers/1",
            "process": list(process_), "subordinated": list(subordinated),
            "originators": [{"actor": a} for a in originators]}


def typen(p):
    return [s["typ"] for s in process.steps(p)]


class Steps(unittest.TestCase):
    def test_verwaltungsvorlage_hat_nichtoeffentliche_vorbereitung(self):
        steps = process.steps(paper())
        self.assertEqual(typen(paper()), ["initiierung", "vorbereitung", "veroeffentlichung"])
        self.assertEqual(steps[1]["status"], "nicht_öffentlich")

    def test_antrag_ohne_vorbereitung(self):
        self.assertNotIn("vorbereitung", typen(paper("Antrag", originators=["CDU"])))

    def test_beratung_mit_lite_datum_ist_abgeleitet_und_sortiert(self):
        p = paper(process_=[cons("Rat", "Entscheidung", True, "2024-05-02T17:00:00", "ungeändert beschlossen"),
                            cons("Hauptausschuss", start="2024-04-10T17:00:00", result="vertagt")])
        steps = process.steps(p)
        mid = [s for s in steps if s["typ"] in ("beratung", "entscheidung")]
        self.assertEqual([s["label"] for s in mid], ["Hauptausschuss", "Rat"])
        self.assertTrue(all(s["date_status"] == "abgeleitet" for s in mid))
        self.assertTrue(mid[0].get("schleife"))
        self.assertEqual(steps[-1]["typ"], "vollzug")
        self.assertEqual(steps[-1]["status"], "unklar")

    def test_beratung_ohne_sitzung_bleibt_als_luecke(self):
        s = [x for x in process.steps(paper(process_=[cons("Rat", status="")])) if x["typ"] == "beratung"][0]
        self.assertEqual((s["date"], s["date_status"], s["note"]), (None, "unklar", "ohne_sitzung"))

    def test_kein_vollzug_ohne_beschluss(self):
        p = paper(process_=[cons("Rat", "Entscheidung", True, "2024-05-02", "zur Kenntnis genommen")])
        self.assertNotIn("vollzug", typen(p))

    def test_sonderweg_und_nichtoeffentlich(self):
        self.assertEqual(process.steps(paper("Dringlichkeitsentscheidung OB"))[0]["note"], "sonderweg")
        t = typen(paper(process.NICHTOEFFENTLICH_TYPE))
        self.assertIn("beratung", t)

    def test_folgevorlage_undatiert_ans_ende_der_mitte(self):
        p = paper(subordinated=[{"paper_type": "Stellungnahme der Verwaltung", "reference": "1-01",
                                 "name": "x", "date": None}])
        self.assertEqual(typen(p)[-1], "folgevorlage")


class StandUndWeg(unittest.TestCase):
    def test_stand(self):
        self.assertEqual(process.stand(paper()), "ohne Beratungsfolge")
        self.assertEqual(process.stand(paper(process_=[cons("Rat", status="")])), "offen")
        self.assertEqual(process.stand(paper(process_=[cons("BV"), cons("Rat", status="")])), "in Beratung")
        self.assertEqual(process.stand(paper(process_=[cons("Rat", "Entscheidung", True)])), "entschieden")

    def test_path_key(self):
        p = paper(process_=[cons("BV Bonn", "Anhörung"),
                            cons("Rat", "Entscheidung", True, result="geändert beschlossen")])
        self.assertEqual(process.path_key(p),
                         (("BV Bonn (Anhörung)", "Rat (Entscheidung)"), "geändert beschlossen"))


if __name__ == "__main__":
    unittest.main()
