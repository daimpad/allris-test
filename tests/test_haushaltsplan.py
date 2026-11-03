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


# --- Erweiterung: Jahresabschluss 2024 (Teilergebnisrechnung) und Teilfinanzplan A ---

JA_MITTEN = [292, 381, 471, 552, 650, 752]          # Mitten der Kopfwörter der sechs Spalten
JA_RECHTS = [333, 422, 512, 602, 691, 781]          # rechter Rand der Beträge (Spalte 4 teils 601)
JA_WERTE = {10: ["142.588,06", "211.940,41", "0,00", "455.494,02", "243.553,61", "0,00"],
            11: ["1.103.258,08", "1.052.853,94", None, "1.059.221,14", "6.367,20", None],
            12: ["108.077,12", "76.568,12", None, "96.796,38", "20.228,26", None],
            13: ["109.999,29", "108.147,76", "7.000,00", "95.076,00", "-13.071,76", "-49.185,09"],
            14: ["1.734,26", "2.254,44", None, "1.660,69", "-593,75", None],
            15: ["55.451,72", "372.535,49", "26.940,94", "273.088,29", "-99.447,20", None],
            16: [None, "224.879,16", None, "357.584,99", "132.705,83", None],   # teilweise gefüllt
            17: ["1.559.975,97", "1.837.238,91", "33.940,94", "1.883.427,49", "46.188,58", "-49.185,09"],
            18: ["-1.417.387,91", "-1.625.298,50", "-33.940,94", "-1.427.933,47", "197.365,03", "49.185,09"]}
JA_NAMEN = {10: ["Ordentliche Erträge"], 11: ["Personalaufwendungen"], 12: ["Versorgungsaufwendungen"],
            13: ["", "Aufwendungen für Sach- und", "Dienstleistungen"], 14: ["Bilanzielle Abschreibungen"],
            15: ["Transferaufwendungen"], 16: ["", "Sonstige ordentliche", "Aufwendungen"],
            17: ["Ordentliche Aufwendungen"],
            18: ["Verwaltungstätigkeit", "Ergebnis der laufenden", "(Zeilen 10 und 17)"]}


def _woerter(x, y, text, breite=6):
    out = []
    for t in text.split():
        out.append(wort(x, y, x + breite * len(t), t))
        x += breite * len(t) + 2.5
    return out


def probe_ja(werte=JA_WERTE, namen=JA_NAMEN, versatz=None, gesamt=False):
    """Kleine, selbst gebaute erste Seite einer Teilergebnisrechnung des Jahresabschlusses (ohne Spaltennummern)."""
    w = _woerter(60, 66, "Jahresabschluss 2024") + _woerter(329, 66, "Produktgruppe")
    w += _woerter(303, 83, "1.01 Innere Verwaltung", 5) + _woerter(549, 83, "Amt 02", 5)
    w += _woerter(60, 100, "verantwortlich: Erika Muster", 5) + _woerter(300, 100, "1.01.02 Internationales Nr. Profitcenter: 1.01.00.01.02", 5)
    w += _woerter(89, 132, "Gesamtergebnisrechnung" if gesamt else "Teilergebnisrechnung")
    for m, kopf in zip(JA_MITTEN, ("Vorjahres", "fortgeschriebener", "davon", "Ist-Ergebnis", "Vergleich", "Folgejahr")):
        w.append(wort(m - 3 * len(kopf), 132, m + 3 * len(kopf), kopf))
    w += [wort(283, 141, 301, "2023"), wort(372, 151, 390, "2024"), wort(551, 141, 569, "2024"),
          wort(439, 151, 502, "Vorjahr")]
    w += [wort(63, 163, 67, "1")] + _woerter(94, 163, "Steuern und ähnliche Abgaben")
    for i, (nr, zeile) in enumerate(sorted(werte.items())):
        y = 322 + 14.5 * i
        w += [wort(61, y, 70, str(nr)), wort(79, y, 84, "=" if nr in (10, 17, 18) else "-")]
        for dy, text in zip((0, -4.6, 4.6), namen[nr]):
            w += _woerter(94, y + dy, text)
        for k, v in enumerate(zeile):
            if v is not None:
                rechts = JA_RECHTS[k] + (versatz or {}).get((nr, k), 0)
                w.append(wort(rechts - 4.5 * len(v), y, rechts, v))
    w += _woerter(347, 553, "Bundesstadt Bonn Jahresabschluss 2024") + _woerter(389, 562, "Seite 195 von 858")
    return '<page width="841.92" height="595.32">' + "".join(reversed(w)) + "</page>"


class Jahresabschluss(unittest.TestCase):
    def test_spalten_aus_dem_kopf_und_cent(self):
        cols, werte = h.koordinaten_ja(h.woerter(probe_ja())[0])
        self.assertEqual(cols, [("Ergebnis", 2023), ("Ansatz fortgeschrieben", 2024),
                                ("davon Ermächtigungsübertragung aus dem Vorjahr", 2024), ("Ergebnis", 2024),
                                ("Vergleich Ansatz/Ist", 2024), ("Ermächtigungsübertragung in das Folgejahr", 2024)])
        self.assertEqual(werte[17], [155997597, 183723891, 3394094, 188342749, 4618858, -4918509])
        self.assertEqual(werte[16], [None, 22487916, None, 35758499, 13270583, None])   # teilweise gefüllt
        self.assertEqual(werte[13][2], 700000)                                           # zweizeilige Bezeichnung
        self.assertEqual(werte[10][2], 0)                                                # „0,00“ ist 0, nicht leer
        self.assertEqual(werte[18][0], -141738791)   # dreizeilige Bezeichnung, Seitenfuß gehört nicht dazu

    def test_spalte_4_mit_einem_punkt_versatz(self):
        """Der rechte Rand der Spalte 4 liegt im PDF teils bei 601, teils bei 602 pt."""
        werte = h.koordinaten_ja(h.woerter(probe_ja(versatz={(11, 3): -1, (14, 3): -1}))[0])[1]
        self.assertEqual(werte[11][3], 105922114)

    def test_wert_zwischen_spalten_bricht_ab(self):
        with self.assertRaisesRegex(ValueError, "Zeile 12: Wert"):
            h.koordinaten_ja(h.woerter(probe_ja(versatz={(12, 1): -30}))[0])

    def test_bezeichnung_muss_passen(self):
        with self.assertRaisesRegex(ValueError, "Zeile 14: Bezeichnung"):
            h.koordinaten_ja(h.woerter(probe_ja(namen={**JA_NAMEN, 14: ["Abschreibungen"]}))[0])
        # Zeile 18 heißt in der Gesamtergebnisrechnung „Ordentliches Ergebnis“, in den Teilrechnungen nicht
        gesamt = h.woerter(probe_ja(namen={**JA_NAMEN, 18: ["", "Ordentliches Ergebnis", "(Zeilen 10 und 17)"]}, gesamt=True))[0]
        with self.assertRaisesRegex(ValueError, "Zeile 18: Bezeichnung"):
            h.koordinaten_ja(gesamt)
        self.assertEqual(h.koordinaten_ja(gesamt, h.JA_ZEILEN_GESAMT)[1][18][4], 19736503)

    def test_betrag_im_seitenfuss_bricht_ab(self):
        seite = probe_ja().replace("</page>", wort(650, 540, 691, "1.000,00") + "</page>")
        with self.assertRaisesRegex(ValueError, "außerhalb der Tabellenzeilen"):
            h.koordinaten_ja(h.woerter(seite)[0])

    def test_kopf_ohne_verantwortliche_person(self):
        ws = h.woerter(probe_ja())[0]
        self.assertEqual(h.kopf(ws), ("01", "1.01.02", "Internationales", "Amt 02"))
        self.assertEqual(h._pb_name(ws), "Innere Verwaltung")

    def test_cent_und_schreibweise(self):
        self.assertEqual([h._cent(t) for t in ("1.234,56", "-0,50", "0", "0,00")], [123456, -50, 0, 0])
        self.assertEqual(h._wie_im_pdf(-123456789, True), "-1.234.567,89")
        self.assertEqual(h._wie_im_pdf(5, True), "0,05")
        self.assertEqual(h._wie_im_pdf(-1500, False), "-1.500")


def ja_zellen(einheit, werte, ebene="Produktgruppe", pb="01"):
    """Zeilen wie in jahresabschluss.tsv: werte {Zeile: [Cent je Spalte]}."""
    return [{"ebene": ebene, "produktbereich": "" if ebene == "Gesamt" else pb,
             "produktgruppe": einheit if ebene == "Produktgruppe" else "", "zeile": str(nr), "spalte": str(k),
             "jahr": "2023" if k == 1 else "2024", "betrag_cent": str(b)}
            for nr, ws in werte.items() for k, b in enumerate(ws, 1)]


def ja_einheit(e10, aufwand):
    """Zeilen 10–18 mit zwei Spalten aus Erträgen und sechs Aufwandsarten."""
    w = {10: e10, **{11 + i: a for i, a in enumerate(aufwand)}}
    w[17] = [sum(a[k] for a in aufwand) for k in range(2)]
    w[18] = [w[10][k] - w[17][k] for k in range(2)]
    return w


class PruefsummenErweiterung(unittest.TestCase):
    def daten(self):
        a = ja_einheit([100, 200], [[10, 20], [0, 0], [5, 5], [1, 1], [-3, 4], [0, 0]])
        b = ja_einheit([50, 0], [[7, 8], [1, 1], [0, 0], [0, 0], [2, 2], [0, 9]])
        pb = {nr: [a[nr][k] + b[nr][k] for k in range(2)] for nr in a}
        rows = ja_zellen("1.01.02", a) + ja_zellen("1.01.03", b) + ja_zellen("01", pb, "Produktbereich")
        plan_pb = [{"ausgabe": "2025/2026", "produktbereich": "01", "zeile": str(nr), "jahr": "2023", "art": "Ergebnis",
                    "betrag": str(round(pb[nr][0] / 100))} for nr in (10, 17, 18)]
        return rows, ja_zellen("", pb, "Gesamt"), plan_pb

    def test_alle_pruefungen(self):
        rows, gesamt, plan_pb = self.daten()
        p = h.pruefsummen_ja(rows, gesamt, plan_pb, [], [], bekannt={})
        self.assertEqual(p["aufwandsarten_17"], (8, 0, "Cent"))   # 4 Einheiten (PG, PG, PB, Gesamt) × 2 Spalten
        self.assertEqual(p["produktgruppen_produktbereich"], (18, 0, "Cent"))
        self.assertEqual(p["vorjahr_haushaltsplan"], (3, 0, "Euro"))

    def test_abweichung_bricht_ab(self):
        rows, gesamt, plan_pb = self.daten()
        zelle = lambda nr: next(r for r in rows if r["produktgruppe"] == "1.01.03" and r["zeile"] == str(nr) and r["spalte"] == "1")
        zelle(10)["betrag_cent"] = str(int(zelle(10)["betrag_cent"]) + h.TOLERANZ_CENT + 1)
        with self.assertRaisesRegex(ValueError, "Zeile 10 − 17"):   # 10 − 17 = 18 der Produktgruppe
            h.pruefsummen_ja(rows, gesamt, plan_pb, [], [], bekannt={})
        zelle(18)["betrag_cent"] = str(int(zelle(18)["betrag_cent"]) + h.TOLERANZ_CENT + 1)   # in sich wieder stimmig
        with self.assertRaisesRegex(ValueError, "Summe der Produktgruppen"):
            h.pruefsummen_ja(rows, gesamt, plan_pb, [], [], bekannt={})

    def test_bekannte_abweichung_nur_in_genau_der_hoehe(self):
        teile, ganze = [(("a", 1), 100)], {("a", 1): 130}
        self.assertEqual(h.pruefsumme(teile, ganze, "Probe", 0, bekannt={("a", 1): -30}), (1, 0))
        with self.assertRaisesRegex(ValueError, "Summe trifft"):
            h.pruefsumme(teile, ganze, "Probe", 0, bekannt={("a", 1): -20})
        with self.assertRaisesRegex(ValueError, "tritt nicht mehr auf"):
            h.pruefsumme(teile, {("a", 1): 100}, "Probe", 0, bekannt={("a", 1): -30})

    def test_investitionen(self):
        def einheit(pg, ein, aus, ebene="Produktgruppe"):
            w = {**{1 + i: e for i, e in enumerate(ein)}, 6: sum(ein), **{7 + i: a for i, a in enumerate(aus)},
                 13: sum(aus)}
            w[14] = w[6] - w[13]
            return [{"ausgabe": "2025/2026", "ebene": ebene, "produktbereich": "03", "produktgruppe": pg if ebene == "Produktgruppe" else "",
                     "zeile": str(nr), "spalte": "6", "art": "Ansatz", "jahr": "2026", "betrag": str(b)} for nr, b in w.items()]
        rows = einheit("1.03.01", [1, 0, 0, 0, 0], [0, 5, 2, 0, 0, 0]) + einheit("1.03.02", [0, 2, 0, 0, 0], [0, 0, 0, 3, 0, 0])
        rows += einheit("", [1, 2, 0, 0, 0], [0, 5, 2, 3, 0, 0], "Produktbereich")
        gesamt = {"2025/2026": ([("Ansatz", 2026), ("Planung", 2027)],
                                {nr + 17: [int(r["betrag"]), 99] for r in rows if r["ebene"] == "Produktbereich"
                                 for nr in [int(r["zeile"])]})}
        p = h.pruefsummen_investitionen(rows, gesamt)
        self.assertEqual(p["zeilen_7_12_gleich_13"], (3, 0, "Euro"))
        self.assertEqual(p["produktgruppen_produktbereich"], (14, 0, "Euro"))
        self.assertEqual(p["produktbereiche_gesamtfinanzplan"], (14, 0, "Euro"))   # Planung zählt nicht
        rows[8]["betrag"] = str(int(rows[8]["betrag"]) + h.TOLERANZ_EURO + 1)          # Zeile 9 der ersten PG
        with self.assertRaisesRegex(ValueError, "Zeilen 7–12"):
            h.pruefsummen_investitionen(rows, gesamt)


FIN_MITTEN = [266 + 54.5 * k for k in range(7)]
FIN_KOPF = [("Ergebnis", 2022), ("Ergebnis", 2023), ("Ansatz", 2024), ("Ansatz", 2025), ("VE", 2025), ("Ansatz", 2026),
            ("VE", 2026)]
FIN_NAMEN = {1: ["", "Einzahlungen aus Zuwendungen für", "Investitionsmaßnahmen"],
             6: ["", "Summe der investiven", "Einzahlungen"], 13: ["", "Summe der investiven", "Auszahlungen"],
             14: ["", "Saldo der Investitionstätigkeit", "(= Zeilen 6 und 13)"]}


def probe_finanz(werte):
    """Kleine Seite eines Teilfinanzplans A mit Zwischenüberschriften und VE-Spalten; werte {Zeile: [Text je Spalte]}."""
    w = _woerter(108, 136, "Teilfinanzplan") + _woerter(99, 148, "Teil A: Zahlungsübersicht")
    for k, (art, jahr) in enumerate(FIN_KOPF):
        m = FIN_MITTEN[k]
        w += [wort(m - 12, 121, m + 12, art), wort(m - 8, 145 if k < 3 else 153, m + 8, str(jahr)),
              wort(m - 2, 172.6, m + 2, str(k + 1))]
    w += _woerter(61, 186, "Investitionstätigkeit") + _woerter(76, 197, "Einzahlungen")
    y = {1: 213, 6: 307, 13: 437, 14: 457}
    w += _woerter(76, 323, "Auszahlungen")
    for nr, zeile in werte.items():
        w += [wort(61, y[nr], 69, str(nr))]
        for dy, text in zip((0, -4, 4), FIN_NAMEN[nr]):
            w += _woerter(87, y[nr] + dy, text)
        for k, v in enumerate(zeile):
            if v is not None:
                w.append(wort(FIN_MITTEN[k] + 24 - 4.5 * len(v), y[nr], FIN_MITTEN[k] + 24, v))
    return '<page width="841.92" height="595.32">' + "".join(reversed(w)) + "</page>"


class Teilfinanzplan(unittest.TestCase):
    WERTE = {1: ["134.713", "836.770", "2.500.450", "2.729.040", None, "2.503.250", None],
             6: ["134.713", "836.770", "2.500.450", "2.729.040", "0", "2.503.250", "0"],
             13: [None, None, "1.500", "1.500", "1.750.000", "1.500", "600.000"],
             14: ["134.713", "836.770", "2.498.950", "2.727.540", "-1.750.000", "2.501.750", "-600.000"]}

    def test_ve_spalten_und_zwischenueberschriften(self):
        nummern = {nr: h.INVESTITIONEN[nr] for nr in (1, 6, 13, 14)}
        cols, werte = h.koordinaten(h.woerter(probe_finanz(self.WERTE))[0], nummern, h.ARTEN_FINANZ, h.NAEHE_PT)
        self.assertEqual(cols, FIN_KOPF)
        self.assertEqual(werte[13], [None, None, 1500, 1500, 1750000, 1500, 600000])
        self.assertEqual(werte[6][4], 0)

    def test_ohne_abstand_gehoert_die_ueberschrift_zur_zeile(self):
        with self.assertRaisesRegex(ValueError, "Zeile 1: Bezeichnung"):   # „Einzahlungen“ hinge an Zeile 1
            h.koordinaten(h.woerter(probe_finanz(self.WERTE))[0], {1: h.INVESTITIONEN[1]}, h.ARTEN_FINANZ)

    def test_zellen_ohne_ve_und_planung(self):
        cols = FIN_KOPF + [("Planung", 2027)]
        datei = {"url": "https://example.org/PB03.pdf", "name": "Schulträgeraufgaben"}
        zellen = list(h._finanz_zellen({"ebene": "Produktbereich", "produktbereich": "03", "produktgruppe": "",
                                        "name": "Schulträgeraufgaben", "einheit": ""},
                                       cols, {13: [None, None, 1500, 1500, 1750000, 1500, 600000, 9]}, "2025/2026", datei, 3))
        self.assertEqual([(z["art"], z["jahr"], z["betrag"], z["leer"], z["spalte"]) for z in zellen],
                         [("Ergebnis", 2022, 0, "ja", 1), ("Ergebnis", 2023, 0, "ja", 2), ("Ansatz", 2024, 1500, "", 3),
                          ("Ansatz", 2025, 1500, "", 4), ("Ansatz", 2026, 1500, "", 6)])


class DateienErweiterung(unittest.TestCase):
    """jahresabschluss.tsv und investitionen.tsv im Repository: Prüfsummen, Spalten, ohne Personen."""

    def test_jahresabschluss(self):
        rows = h.lesen(h.JAHRESABSCHLUSS_TSV)
        self.assertEqual(len({r["produktbereich"] for r in rows}), 17)
        self.assertEqual(len({r["produktgruppe"] for r in rows if r["ebene"] == "Produktgruppe"}), 141)
        self.assertEqual({(r["spalte"], r["art"], r["jahr"]) for r in rows},
                         {(str(k), a, str(j)) for k, (a, j) in enumerate(
                             [("Ergebnis", 2023), ("Ansatz fortgeschrieben", 2024),
                              ("davon Ermächtigungsübertragung aus dem Vorjahr", 2024), ("Ergebnis", 2024),
                              ("Vergleich Ansatz/Ist", 2024), ("Ermächtigungsübertragung in das Folgejahr", 2024)], 1)})
        self.assertEqual({r["zeile"] for r in rows}, {str(n) for n in range(10, 19)})
        self.assertTrue(all(r["betrag_cent"] == "0" for r in rows if r["leer"] == "ja"))
        z = {(r["ebene"], r["produktgruppe"] or r["produktbereich"], int(r["zeile"]), int(r["spalte"])): int(r["betrag_cent"])
             for r in rows}
        for (e, u, nr, sp), b in z.items():
            if nr == 17:
                self.assertEqual(sum(z[(e, u, n, sp)] for n in range(11, 17)), b)
            if nr == 18:
                self.assertEqual(z[(e, u, 10, sp)] - z[(e, u, 17, sp)], b)
            if sp == 5:   # Vergleich = Ist minus fortgeschriebener Ansatz
                self.assertEqual(z[(e, u, nr, 4)] - z[(e, u, nr, 2)], b)
        p = h.pruefsumme([((r["produktbereich"], r["zeile"], r["spalte"]), int(r["betrag_cent"])) for r in rows
                          if r["ebene"] == "Produktgruppe"],
                         {(r["produktbereich"], r["zeile"], r["spalte"]): int(r["betrag_cent"]) for r in rows
                          if r["ebene"] == "Produktbereich"}, "Probe", h.TOLERANZ_CENT)
        self.assertEqual(p, (918, 0))
        self.assertFalse([r for r in rows if "verantwortlich" in r["name"] + r["einheit"] or "Profitcenter" in r["name"]])

    def test_vorjahr_gleich_haushaltsplan(self):
        """Ergebnis 2023 der Produktgruppen (Spalte 1) gegen das Ist 2023 im Haushaltsplan 2025/2026, Zeilen 11–17."""
        rows = h.lesen(h.JAHRESABSCHLUSS_TSV)
        plan = {(r["produktgruppe"], r["zeile"]): int(r["betrag"]) for r in h.lesen(h.PRODUKTGRUPPEN_TSV)
                if r["ausgabe"] == "2025/2026" and r["art"] == "Ergebnis" and r["jahr"] == "2023"}
        ja = {(r["produktgruppe"], r["zeile"]): int(r["betrag_cent"]) for r in rows
              if r["ebene"] == "Produktgruppe" and r["spalte"] == "1" and 11 <= int(r["zeile"]) <= 17}
        self.assertEqual(len(ja), 141 * 7)
        self.assertLessEqual(max(abs(round(b / 100) - plan[k]) for k, b in ja.items()), h.TOLERANZ_EURO)

    def test_investitionen(self):
        rows = h.lesen(h.INVESTITIONEN_TSV)
        self.assertEqual({r["art"] for r in rows}, {"Ergebnis", "Ansatz"})   # ohne VE und Planung
        self.assertEqual({a: len({r["produktbereich"] for r in rows if r["ausgabe"] == a}) for a in h.AUSGABEN},
                         {"2023/2024": 17, "2025/2026": 17})
        self.assertEqual({r["zeile_name"] for r in rows}, set(h.INVESTITIONEN.values()))
        self.assertTrue(all(r["betrag"] == "0" for r in rows if r["leer"] == "ja"))
        e = lambda r: (r["ausgabe"], r["ebene"], r["produktgruppe"] or r["produktbereich"], r["spalte"])
        z = {(e(r), int(r["zeile"])): int(r["betrag"]) for r in rows}
        for (k, nr), b in z.items():
            if nr == 14:
                self.assertLessEqual(abs(sum(z[(k, n)] for n in range(1, 6)) - z[(k, 6)]), h.TOLERANZ_EURO)
                self.assertLessEqual(abs(sum(z[(k, n)] for n in range(7, 13)) - z[(k, 13)]), h.TOLERANZ_EURO)
                self.assertLessEqual(abs(z[(k, 6)] - z[(k, 13)] - b), h.TOLERANZ_EURO)
        finanzanlagen = {(r["ausgabe"], r["produktgruppe"], r["jahr"]): int(r["betrag"]) for r in rows if r["zeile"] == "10"}
        self.assertEqual(finanzanlagen[("2025/2026", "1.01.29", "2026")], 99558600)
        self.assertEqual(finanzanlagen[("2025/2026", "1.16.04", "2026")], 70000000)

    def test_freigegeben(self):
        self.assertTrue(h.ERWEITERUNG_FREIGEGEBEN)   # Prüfbögen im Gespräch bestätigt 03.11.2026
        self.assertEqual(h.ist_2024("Produktbereich", "03")["betrag"], 77_769_135)   # 77.769.134,95 € (Prüfbogen)

def probe_tfr(jahr_kopf=True):
    """Kleine Teilfinanzrechnung (Teil A) des Jahresabschlusses: Zeilen 1, 6, 9, 13, 14; Zeile 1 und 9 mit der Nummer
    mittig neben zweizeiliger Bezeichnung und den Beträgen in der zweiten Zeile; leere Zeilen fehlen."""
    w = _woerter(60, 66, "Jahresabschluss 2024") + _woerter(329, 66, "Produktbereich") + _woerter(303, 83, "1.01 Innere Verwaltung", 5)
    w += _woerter(97, 127, "Teilfinanzrechnung") + _woerter(103, 138.5, "Teil A: Zahlungsnachweis")
    for m, kopf in zip(JA_MITTEN, ("Vorjahres", "fortgeschriebener", "davon", "Ist-Ergebnis", "Vergleich", "Folgejahr")):
        w.append(wort(m - 3 * len(kopf), 130 if kopf != "Folgejahr" else 138.5, m + 3 * len(kopf), kopf))
    if jahr_kopf:
        w += [wort(283, 138.5, 301, "2023"), wort(552, 138.5, 569, "2024")]
    else:
        w += [wort(288, 138.5, 295, "-1")]   # wie Jahresabschluss S. 608
    w += _woerter(61, 163.6, "Investitionstätigkeit")
    zeilen = [(1, "", 182.1, [("aus Zuwendungen für", -4.6), ("Investitionsmaßnahmen", 4.6)], 4.6,
               ["836.769,95", "2.520.450,00", None, "135.385,96", "-2.385.064,04", None]),
              (6, "=", 228.6, [("Summe:", -4.6), ("(invest. Einzahlungen)", 4.5)], 0,
               ["836.769,95", "2.520.450,00", "0", "135.385,96", "-2.385.064,04", "0"]),
              (9, "-", 251.8, [("für den Erwerb von beweglichem", -4.6), ("Anlagevermögen", 4.6)], 4.6,
               ["3.479.781,38", "9.431.251,42", "4.222.387,93", "6.370.023,41", "-3.061.228,01", "-3.307.190,89"]),
              (13, "=", 270.2, [("Summe:", -4.6), ("(invest. Auszahlungen)", 4.6)], 0,
               ["3.479.781,38", "9.431.251,42", "4.222.387,93", "6.370.023,41", "-3.061.228,01", "-3.307.190,89"]),
              (14, "=", 290, [("Saldo:", -9.2), ("der Investitionstätigkeit", 0), ("(Einzahlungen ./. Auszahlungen)", 9.2)], 0,
               ["-2.643.011,43", "-6.910.801,42", "-4.222.387,93", "-6.234.637,45", "676.163,97", "3.307.190,89"])]
    for nr, zeichen, y, namen, dy_werte, werte in zeilen:
        w += [wort(61, y, 70, str(nr))] + ([wort(78, y, 81, zeichen)] if zeichen else [])
        for text, dy in namen:
            w += _woerter(89, y + dy, text)
        for k, v in enumerate(werte):
            if v is not None:
                w.append(wort(JA_RECHTS[k] - 4.5 * len(v), y + dy_werte, JA_RECHTS[k], v))
    w += _woerter(347, 553, "Bundesstadt Bonn Jahresabschluss 2024")
    return '<page width="841.92" height="595.32">' + "".join(reversed(w)) + "</page>"


class Teilfinanzrechnung(unittest.TestCase):
    def test_werte_neben_der_nummer_und_fehlende_zeilen(self):
        cols, werte = h.koordinaten_ja(h.woerter(probe_tfr())[0], h.JA_INVESTITIONEN, nur_vorhandene=True)
        self.assertEqual(cols[3], ("Ergebnis", 2024))   # Spalte 2 ohne Jahr im Kopf: Haushaltsjahr
        self.assertEqual(werte[1], [83676995, 252045000, None, 13538596, -238506404, None])
        self.assertEqual(werte[9][5], -330719089)
        self.assertEqual(werte[2], [None] * 6)          # nicht gedruckt: leer
        self.assertEqual(werte[14][0], -264301143)
        self.assertEqual(sorted(werte), list(range(1, 15)))

    def test_ohne_nur_vorhandene_fehlt_zeile(self):
        with self.assertRaisesRegex(ValueError, "Zeile 2 nicht gefunden"):
            h.koordinaten_ja(h.woerter(probe_tfr())[0], h.JA_INVESTITIONEN)

    def test_unerwartete_zeile_bricht_ab(self):
        with self.assertRaisesRegex(ValueError, "unerwartete Zeilen"):
            h.koordinaten_ja(h.woerter(probe_tfr())[0], {n: x for n, x in h.JA_INVESTITIONEN.items() if n != 9},
                             nur_vorhandene=True)

    def test_kopf_ohne_jahr_nur_mit_vorgabe(self):
        ws = h.woerter(probe_tfr(jahr_kopf=False))[0]
        with self.assertRaisesRegex(ValueError, "Jahr der Spalte 1"):
            h.koordinaten_ja(ws, h.JA_INVESTITIONEN, nur_vorhandene=True)
        vermerke = []
        cols, _ = h.koordinaten_ja(ws, h.JA_INVESTITIONEN, nur_vorhandene=True, jahre=(2023, 2024), vermerke=vermerke)
        self.assertEqual((cols[0], cols[3]), (("Ergebnis", 2023), ("Ergebnis", 2024)))
        self.assertEqual(len(vermerke), 2)

    def test_datei_im_repository(self):
        rows = h.lesen(h.JA_INVESTITIONEN_TSV)
        self.assertEqual({r["spalte"] for r in rows}, {"1", "2", "4", "5"})   # ohne Ermächtigungsübertragungen
        self.assertEqual({r["zeile_name"] for r in rows}, set(h.INVESTITIONEN.values()))
        self.assertEqual(len({r["produktbereich"] for r in rows}), 16)          # PB 17 ohne Teilfinanzrechnung
        self.assertNotIn("17", {r["produktbereich"] for r in rows})
        self.assertTrue(all(r["betrag_cent"] == "0" for r in rows if r["leer"] == "ja"))
        z = {(r["ebene"], r["produktgruppe"] or r["produktbereich"], int(r["zeile"]), int(r["spalte"])): int(r["betrag_cent"])
             for r in rows}
        for (e, u, nr, sp), b in z.items():
            if nr == 14:
                self.assertEqual(sum(z[(e, u, n, sp)] for n in range(1, 6)), z[(e, u, 6, sp)])
                self.assertEqual(sum(z[(e, u, n, sp)] for n in range(7, 13)), z[(e, u, 13, sp)])
                self.assertEqual(z[(e, u, 6, sp)] - z[(e, u, 13, sp)], b)
            if sp == 5:
                self.assertEqual(z[(e, u, nr, 4)] - z[(e, u, nr, 2)], b)
        self.assertEqual(z[("Produktgruppe", "1.01.29", 10, 4)], 8571614659)
        self.assertFalse([r for r in rows if "verantwortlich" in r["name"] + r["einheit"]])


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



class DateienErtragsarten(unittest.TestCase):
    """data/haushalt/ertragsarten.tsv und jahresabschluss_ertragsarten.tsv (haushalt/PHASE6.md)."""
    def test_zeilen_1_bis_9_ergeben_zeile_10(self):
        from collections import defaultdict
        for path, wert, key in ((h.ERTRAGSARTEN_TSV, "betrag", ("ebene", "ausgabe", "produktbereich", "produktgruppe", "jahr", "art")),
                                (h.JA_ERTRAGSARTEN_TSV, "betrag_cent", ("ebene", "produktbereich", "produktgruppe", "spalte"))):
            teile, summe = defaultdict(int), {}
            for r in h.lesen(path):
                k = tuple(r[f] for f in key)
                if r["zeile"] == "10":
                    summe[k] = int(r[wert])
                else:
                    teile[k] += int(r[wert])
            self.assertEqual(set(teile), set(summe))
            self.assertLessEqual(max(abs(teile[k] - summe[k]) for k in summe), 0, path.name)

    def test_freigegeben(self):
        self.assertTrue(h.ERTRAGSARTEN_FREIGEGEBEN)   # Prüfbogen im Gespräch bestätigt 03.11.2026

if __name__ == "__main__":
    unittest.main()
