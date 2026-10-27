import unittest

from pipeline import dossier, haushaltsplan as h

SEITE = """Haushaltsplan 2025/2026                                                Produktbereich
Bundesstadt Bonn                                                  1.04 Kultur und Wissenschaft

                                                   Ergebnis          Ergebnis        Ansatz         Ansatz          Ansatz          Planung         Planung         Planung
          Teilergebnisplan                          Jahres            Jahres        Vorjahres      Haushalts-      Haushalts-      Haushalts-      Haushalts-      Haushalts-
                                                     2022              2023           2024           jahres          jahres          jahres          jahres          jahres
                                                                                                      2025            2026            2027            2028            2029
                                                      1                 2              3               4               5               6               7               8
1        Steuern und ähnliche Abgaben
10   =   Ordentliche Erträge                        15.052.528        13.763.046      11.688.313     13.152.520      13.385.237      13.266.273      13.297.692      13.357.548
17   =   Ordentliche Aufwendungen                   77.134.449        80.227.924      80.209.896     89.240.729      92.787.001      92.707.868      91.725.455      89.929.582
         Ordentliches Ergebnis
18   =                                              -62.081.921       -66.464.878    -68.521.583     -76.088.209     -79.401.764     -79.441.595     -78.427.763     -76.572.034
         (Zeilen 10 und 17)
"""


def row(ausgabe, jahr, art, betrag, zeile=17, pb="04"):
    return {"ausgabe": ausgabe, "produktbereich": pb, "name": "Kultur und Wissenschaft", "zeile": str(zeile), "jahr": str(jahr),
            "art": art, "betrag": str(betrag), "datei": "PB04.pdf", "seite": "1"}


class Auslesen(unittest.TestCase):
    def test_spalten_chronologisch_ohne_ausgabe_im_kopf(self):
        self.assertEqual(h.spalten(SEITE), [("Ergebnis", 2022), ("Ergebnis", 2023), ("Ansatz", 2024), ("Ansatz", 2025),
                                            ("Ansatz", 2026), ("Planung", 2027), ("Planung", 2028), ("Planung", 2029)])

    def test_zeilen_auch_zweizeilig_und_negativ(self):
        self.assertEqual(h.zeile(SEITE, 17, 8)[4], 92787001)
        self.assertEqual(h.zeile(SEITE, 18, 8)[0], -62081921)
        self.assertIsNone(h.zeile(SEITE, 1, 8))   # Zeile ohne Werte

    def test_fehlende_zelle_bricht_ab(self):
        with self.assertRaises(ValueError):
            h.zeile(SEITE.replace("13.385.237      ", ""), 10, 8)


class Reihe(unittest.TestCase):
    def test_ist_aus_juengster_ausgabe_plan_aus_eigenem_doppelhaushalt(self):
        rows = [row("2023/2024", 2021, "Ergebnis", 1), row("2023/2024", 2022, "Ansatz", 2), row("2023/2024", 2023, "Ansatz", 3),
                row("2025/2026", 2023, "Ergebnis", 4), row("2025/2026", 2024, "Ansatz", 5), row("2025/2026", 2025, "Ansatz", 6),
                row("2025/2026", 2025, "Ansatz", 99, zeile=10)]
        r = {j: (i and i[0], p and p[0]) for j, i, p in h.reihe("04", rows)}
        # Ansatz des Vorjahres (2022 in 2023/24, 2024 in 2025/26) zählt nicht als Plan
        self.assertEqual(r, {2021: (1, None), 2023: (4, 3), 2025: (None, 6)})


class Freigabe(unittest.TestCase):
    def test_ohne_freigabe_kein_abschnitt(self):
        alt = h.FREIGEGEBEN
        try:
            h.FREIGEGEBEN = False
            self.assertIsNone(dossier._betraege("04"))
            self.assertEqual(dossier._haushalt({}), "")
        finally:
            h.FREIGEGEBEN = alt

    def test_betrag_in_mio(self):
        self.assertEqual(dossier._mio(92787001), "92,8 Mio. €")
        self.assertEqual(dossier._mio(1797043216), "1.797,0 Mio. €")


if __name__ == "__main__":
    unittest.main()
