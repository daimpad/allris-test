import unittest

from pipeline import actors

ORGS = [
    {"id": "cdu", "name": "CDU-Fraktion im Rat der Stadt Bonn", "classification": "Fraktion"},
    {"id": "spd", "name": "SPD-Fraktion im Rat der Stadt Bonn", "classification": "Fraktion"},
    {"id": "gruene", "name": "Fraktion Bündnis 90 / DIE GRÜNEN", "classification": "Fraktion"},
    {"id": "fdp-f", "name": "FDP-Fraktion im Rat der Stadt Bonn", "classification": "Fraktion",
     "endDate": "2025-10-31"},
    {"id": "fdp-g", "name": "FDP-Gruppe im Rat der Stadt Bonn", "classification": "Gruppen"},
    {"id": "spd-bf-bo", "name": "SPD Bezirksfraktion Bonn",
     "classification": "Bezirksfraktionen (intern)"},
    {"id": "vb", "name": "01-2 Ratsbüro", "classification": "Co-Dezernat"},
    {"id": "amt61", "name": "61-1 Stadtentwicklung", "classification": "61 Stadtplanungsamt"},
]


def paper(name, ptype="Antrag", date="2024-05-01", **kw):
    return {"name": name, "paperType": ptype, "date": date, **kw}


def actor_names(p, bezirke=()):
    return [r["actor"] for r in actors.originators(p, ORGS, bezirke)]


class Originators(unittest.TestCase):
    def test_prefix_single_party(self):
        rows = actors.originators(paper("CDU-Antrag: Mehr Bäume"), ORGS)
        self.assertEqual([(r["actor"], r["organization_id"]) for r in rows], [("CDU", "cdu")])
        self.assertEqual(rows[0]["evidence"], "CDU-Antrag")

    def test_prefix_several_parties_with_unresolved_rest(self):
        self.assertEqual(actor_names(paper("Grüne/SPD/u.w.-Antrag: Radweg")),
                         ["Grüne", "SPD", "weitere (u.w., nicht aufgelöst)"])

    def test_party_after_keyword_without_colon(self):
        self.assertEqual(actor_names(paper("Fahrradabstellanlagen BBB-Änderungsantrag zur Vorlage 212008",
                                           "Änderungsantrag")), ["BBB"])

    def test_no_party_gives_no_originator(self):
        self.assertEqual(actor_names(paper("Instandsetzung Vitrinen")), [])

    def test_group_status_depends_on_date(self):
        org = lambda d: actors.originators(paper("FDP-Antrag: X", date=d), ORGS)[0]["organization_id"]
        self.assertEqual(org("2024-01-01"), "fdp-f")
        self.assertEqual(org("2026-01-01"), "fdp-g")

    def test_bezirksfraktion_mapped_via_bezirk(self):
        rows = actors.originators(paper("SPD-Bezirksfraktion: Verkehrsberuhigung"), ORGS, {"Bonn"})
        self.assertEqual((rows[0]["actor"], rows[0]["organization_id"]),
                         ("SPD-Bezirksfraktion Bonn", "spd-bf-bo"))

    def test_koalition(self):
        self.assertEqual(actor_names(paper("Koalitionsantrag: Klimaplan")), ["Koalition"])

    def test_rhein_gruen_is_not_gruene(self):
        self.assertNotIn("Grüne", actor_names(paper("Rhein.Grün-Antrag: Ufer")))

    def test_verwaltung_and_einwohner_from_paper_type(self):
        self.assertEqual(actor_names(paper("Bebauungsplan", "Beschlussvorlage", underDirectionOf=["amt61"])),
                         ["Verwaltung"])
        self.assertEqual(actor_names(paper("Bürgerantrag: Ampel", "Bürgerantrag § 24 GO - Öffentlich")),
                         ["Einwohner:innen"])


class Responsibilities(unittest.TestCase):
    def test_co_dezernat_resolved_via_stellungnahme(self):
        orgs = {o["id"]: o for o in ORGS}
        sub = {"id": "s", "reference": "241-01 ST", "paperType": "Stellungnahme der Verwaltung",
               "underDirectionOf": ["amt61"]}
        p = {"underDirectionOf": ["vb"], "subordinatedPaper": ["s"]}
        rows = actors.responsibilities(p, orgs, {"s": sub})
        self.assertEqual([(r["kind"], r["organization_id"], r["evidence"]) for r in rows],
                         [("federfuehrend", "vb", None), ("fachlich", "amt61", "241-01 ST")])

    def test_amt_label(self):
        self.assertEqual(actors.amt_label(ORGS[-2]), "01-2 Ratsbüro")
        self.assertEqual(actors.amt_label(ORGS[-1]), "61 Stadtplanungsamt")


if __name__ == "__main__":
    unittest.main()
