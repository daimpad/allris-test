import unittest

from pipeline import gebietszahlen as gz


def paper(date, *themes):
    return {"date": date, "themes": [{"theme": t} for t in themes]}


class Gebietszahlen(unittest.TestCase):
    def test_zeitraum(self):
        self.assertEqual(gz.window_start("2026-10-20T04:17:00+00:00"), "2025-10-20")
        papers = {1: paper("2026-01-01"), 2: paper("2025-10-20"), 3: paper(None)}
        self.assertEqual(gz.recent([1, 2, 3], papers, "2025-10-20"), 1)

    def test_auffaellig(self):
        papers = {i: paper("2026-01-01", "verkehr") for i in range(80)}
        papers.update({100 + i: paper("2026-01-01", "soziales") for i in range(20)})
        base = gz.shares(list(papers), papers)            # Soziales 20 % in ganz Bonn
        area = [100 + i for i in range(8)] + list(range(8))  # Soziales 50 % im Gebiet
        a = gz.auffaellig(area, papers, base)
        self.assertEqual((a["thema"], a["anteil"], a["anteil_bonn"]), ("soziales", 50, 20))
        # zu wenige Vorlagen des Themas: kein Befund
        self.assertIsNone(gz.auffaellig([100, 101, 1, 2], papers, base))
        # Anteil wie in ganz Bonn: kein Befund
        self.assertIsNone(gz.auffaellig(list(range(40)) + [100 + i for i in range(10)], papers, base))

    def test_themenanteile(self):
        papers = {i: paper("2020-01-01", "verkehr", "bauen") if i < 5 else paper("2020-01-01", "bauen") for i in range(20)}
        s = gz.theme_shares(list(papers), papers)
        self.assertEqual((s["verkehr"], s["bauen"]), ([5, 25.0], [20, 100.0]))
        self.assertIsNone(gz.theme_shares(list(range(19)), papers))  # unter der Mindestzahl

    def test_bezirk_ohne_doppelte(self):
        papers = {i: paper("2026-01-01") for i in range(5)}
        index = {"ortsteile": [{"name": "A", "slug": "a", "stadtbezirk": "B"}, {"name": "C", "slug": "c", "stadtbezirk": "B"}],
                 "bezirke": [{"name": "B", "slug": "b"}]}
        areas = {"ortsteil:a": [0, 1, 2], "ortsteil:c": [2, 3], "bezirk:b": [4]}
        gz.annotate(index, areas, papers, "2026-10-20")
        self.assertEqual((index["bezirke"][0]["alle"], index["bezirke"][0]["jahr"], index["ortsteile"][0]["jahr"]), (5, 5, 3))
        self.assertEqual(index["zahlen"]["seit"], "2025-10-20")


if __name__ == "__main__":
    unittest.main()
