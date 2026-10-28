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


def wort(x0, y, x1, text):
    """Ein Wort wie in der Ausgabe von pdftotext -bbox; y ist die Mitte der Zeile, Höhe 9 pt."""
    return (f'<word xMin="{x0:.6f}" yMin="{y - 4.5:.6f}" xMax="{x1:.6f}" yMax="{y + 4.5:.6f}">'
            f'{text.replace("&", "&amp;")}</word>')


MITTEN = [268 + 68.6 * k for k in range(5)]   # Mitten der Spaltennummern 1–5
WERTE = {11: ["12.299.038", "12.643.261", "12.896.237", "13.422.480", "13.852.338"],
         12: ["1.304.548", "1.492.873", "1.223.917", "1.429.228", "1.500.097"],
         13: ["1.605.284", "2.452.437", "1.743.641", "2.593.414", "2.397.457"],
         14: ["78.209", "72.827", "104.134", "81.698", "328.377"],
         15: ["-1.667.775", "-84.508", "11.500", "140.000", None],   # teilweise gefüllt, negativ
         16: [None, "153.989", None, None, "241.248"],                # teilweise gefüllt, Lücken in der Mitte
         17: ["13.620.304", "16.730.879", "17.979.429", "17.666.820", "18.319.517"]}
NAMEN = {11: ["Personalaufwendungen"], 12: ["Versorgungsaufwendungen"],
         13: ["", "Aufwendungen für Sach- und", "Dienstleistungen"],   # zweizeilig, Werte in der Zeile mit der Nummer
         14: ["Bilanzielle Abschreibungen"], 15: ["Transferaufwendungen"], 16: ["Sonstige ordentliche Aufwendungen"],
         17: ["Ordentliche Aufwendungen"]}
KOPF_PG = [(59.5, 66, "Haushaltsplan 2025/2026"), (328.6, 66, "Produktgruppe"), (59.5, 82, "Bundesstadt Bonn"),
           (303.5, 82, "1.04 Kultur und Wissenschaft"), (690, 82, "Amt 41-2"), (59.5, 96, "verantwortlich: Erika Muster"),
           (300, 96, "1.04.08 Stadtm., Gedenkstätte, Zentrale Projekte Nr. Profitcenter: 141500408")]


def probe(werte=WERTE, namen=NAMEN, versatz=None, kopf=KOPF_PG):
    """Kleine, selbst gebaute Seite eines Teilergebnisplans (fünf Spalten) als bbox-HTML, Wörter ungeordnet wie im PDF."""
    w = [wort(97.7, 142, 193.2, "Teilergebnisplan")]
    for x, y, text in kopf:
        for t in text.split():
            w.append(wort(x, y, x + 5 * len(t), t))
            x += 5 * len(t) + 3   # „Nr. Profitcenter“ ohne große Lücke nach dem Namen, wie teils im PDF
    for k, (art, jahr) in enumerate([("Ergebnis", 2022), ("Ergebnis", 2023), ("Ansatz", 2024), ("Ansatz", 2025), ("Ansatz", 2026)]):
        m = MITTEN[k]
        w += [wort(m - 17, 121, m + 17, art), wort(m - 9, 149 if k < 3 else 158, m + 9, str(jahr)), wort(m - 2.2, 175.5, m + 2.2, str(k + 1))]
    for i, (nr, zeile) in enumerate(sorted(werte.items())):
        y = 337 + 14 * i + (5 if nr > 13 else 0)
        w += [wort(60.8, y, 69.8, str(nr)), wort(80.5, y, 83.2, "=" if nr == 17 else "-")]
        for dy, text in zip((0, -4.6, 4.6), namen[nr]):
            x = 93.7
            for t in text.split():
                w.append(wort(x, y + dy, x + 6 * len(t), t))
                x += 6 * len(t) + 2.5
        for k, v in enumerate(zeile):
            if v is not None:
                rechts = MITTEN[k] + 31.2 + (versatz or {}).get((nr, k), 0)
                w.append(wort(rechts - 4.5 * len(v), y, rechts, v))
    return '<page width="841.92" height="595.32">' + "".join(reversed(w)) + "</page>"


MIT_17 = {**h.AUFWANDSARTEN, 17: "Ordentliche Aufwendungen"}


class Koordinaten(unittest.TestCase):
    def test_teilweise_gefuellte_zeilen_spalte_eindeutig(self):
        cols, werte = h.koordinaten(h.woerter(probe())[0], MIT_17)
        self.assertEqual(cols, [("Ergebnis", 2022), ("Ergebnis", 2023), ("Ansatz", 2024), ("Ansatz", 2025), ("Ansatz", 2026)])
        self.assertEqual(werte[15], [-1667775, -84508, 11500, 140000, None])
        self.assertEqual(werte[16], [None, 153989, None, None, 241248])
        self.assertEqual(werte[13][1], 2452437)   # zweizeilige Bezeichnung
        self.assertEqual(werte[17][4], 18319517)
        self.assertEqual(sorted(h.koordinaten(h.woerter(probe())[0])[1]), [11, 12, 13, 14, 15, 16])

    def test_zeile_17_darf_luecken_haben(self):
        """Die Spalte folgt aus dem Abstand zur Spaltennummer, nicht aus einer vollständigen Zeile."""
        werte = {**WERTE, 17: [None, None, "17.979.429", None, "18.319.517"]}
        self.assertEqual(h.koordinaten(h.woerter(probe(werte=werte))[0], MIT_17)[1][17], [None, None, 17979429, None, 18319517])

    def test_bezeichnung_muss_passen(self):
        with self.assertRaisesRegex(ValueError, "Zeile 14: Bezeichnung"):
            h.koordinaten(h.woerter(probe(namen={**NAMEN, 14: ["Abschreibungen"]}))[0])

    def test_wert_zwischen_spalten_bricht_ab(self):
        with self.assertRaisesRegex(ValueError, "Zeile 12: Wert"):
            h.koordinaten(h.woerter(probe(versatz={(12, 2): -20}))[0])

    def test_fehlende_zeile_bricht_ab(self):
        werte = {k: v for k, v in WERTE.items() if k != 14}
        with self.assertRaisesRegex(ValueError, "Zeile 14 nicht gefunden"):
            h.koordinaten(h.woerter(probe(werte=werte))[0])

    def test_kopf_ohne_verantwortliche_person(self):
        pb, pg, name, einheit = h.kopf(h.woerter(probe())[0])
        self.assertEqual((pb, pg, name, einheit), ("04", "1.04.08", "Stadtm., Gedenkstätte, Zentrale Projekte", "Amt 41-2"))
        kopf_pb = [(59.5, 66, "Haushaltsplan 2025/2026"), (328.6, 66, "Produktbereich"), (303.5, 82, "1.04 Kultur und Wissenschaft")]
        self.assertEqual(h.kopf(h.woerter(probe(kopf=kopf_pb))[0]), ("04", None, None, None))


def zellen(betraege, ausgabe="2025/2026", pb="09", jahr=2025, art="Ansatz", pg=None):
    return [{"ausgabe": ausgabe, "produktbereich": pb, "produktgruppe": pg, "zeile": str(nr), "jahr": str(jahr), "art": art,
             "betrag": str(b)} for nr, b in zip((*range(11, 17), 17), betraege)]


class Pruefsumme(unittest.TestCase):
    def test_summe_trifft_ganzes(self):
        teile = [(("a", 1), 100), (("a", 1), -10), (("a", 2), 7)]
        self.assertEqual(h.pruefsumme(teile, {("a", 1): 91, ("a", 2): 7}, "Probe"), (2, 1))

    def test_abweichung_ueber_toleranz_bricht_ab(self):
        with self.assertRaisesRegex(ValueError, "Probe: Summe trifft Zeile 17 nicht"):
            h.pruefsumme([(("a", 1), 100 + h.TOLERANZ + 1)], {("a", 1): 100}, "Probe")

    def test_fehlende_spalte_bricht_ab(self):
        with self.assertRaisesRegex(ValueError, "Spalten passen nicht"):
            h.pruefsumme([(("a", 1), 1)], {("a", 1): 1, ("a", 2): 1}, "Probe")

    def test_drei_pruefungen(self):
        aufwand = zellen([100, 20, 30, 0, -10, 5])[:6]
        gruppen = zellen([60, 10, 0, 0, 0, 0, 70], pg="1.09.01") + zellen([40, 10, 30, 0, -10, 5, 75], pg="1.09.02")
        z17 = [row("2025/2026", 2025, "Ansatz", 145, pb="09"), row("2023/2024", 2023, "Ansatz", 999, pb="09")]
        self.assertEqual(h.pruefsummen(aufwand, gruppen, z17), {"aufwandsarten_produktbereich": (1, 0),
                                                               "aufwandsarten_produktgruppe": (2, 0),
                                                               "produktgruppen_produktbereich": (1, 0)})
        gruppen[-1]["betrag"] = str(75 + h.TOLERANZ + 1)   # Zeile 17 der Produktgruppe passt nicht mehr
        with self.assertRaisesRegex(ValueError, "Aufwandsarten der Produktgruppen"):
            h.pruefsummen(aufwand, gruppen, z17)

    def test_dateien_im_repository(self):
        """aufwandsarten.tsv und produktgruppen.tsv: alle drei Prüfsummen je Spalte, leere Zellen als 0."""
        aufwand, gruppen = h.lesen(h.AUFWANDSARTEN_TSV), h.lesen(h.PRODUKTGRUPPEN_TSV)
        p = h.pruefsummen(aufwand, gruppen, h.lesen())
        self.assertEqual(p["aufwandsarten_produktbereich"], (170, 0))
        self.assertEqual(p["aufwandsarten_produktgruppe"], (1500, 0))
        self.assertEqual(p["produktgruppen_produktbereich"][0], 170)
        self.assertLessEqual(p["produktgruppen_produktbereich"][1], 9)
        for rows in (aufwand, gruppen):
            self.assertTrue(all(r["betrag"] == "0" for r in rows if r["leer"] == "ja"))
            self.assertFalse([r for r in rows if r["art"] == "Planung"])   # ohne Finanzplanung
            self.assertTrue(all(r["art"] == "Ergebnis" for r in rows if int(r["betrag"]) < 0))   # negativ nur im Ist
        self.assertIn(("09", "15", "2023", "-84508"), [(r["produktbereich"], r["zeile"], r["jahr"], r["betrag"]) for r in aufwand])
        self.assertEqual({r["zeile_name"] for r in aufwand}, set(h.AUFWANDSARTEN.values()))
        self.assertEqual({a: len({r["produktgruppe"] for r in gruppen if r["ausgabe"] == a}) for a in h.AUSGABEN},
                         {"2023/2024": 150, "2025/2026": 150})
        namen = {(r["ausgabe"], r["produktgruppe"]): r["name"] for r in gruppen}
        self.assertEqual(namen[("2025/2026", "1.04.07")], "Stadtarchiv")
        self.assertEqual(namen[("2023/2024", "1.04.07")], "Z. f. Stadtgesch. u. Erinnerungskulturen")
        self.assertFalse([n for n in namen.values() if "verantwortlich" in n or "Profitcenter" in n])
        self.assertNotIn("verantwortlich", "".join(r["einheit"] for r in gruppen))


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
