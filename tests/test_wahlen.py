"""Wahl 2025 als Übergang (pipeline/wahlen.py): Lesen der Datei von IT.NRW und Zuordnung über das Straßenverzeichnis."""
import unittest

from pipeline import wahlen

ITNRW = """Endgültige Ergebnisse ...;;;;;;;;;;;;;
Verwaltungsbezirk;;;Stimmbezirk;Briefwahl;...
KRS;GKZ_Gemeinde;Gemeindenname;Nr;Briefwahl;A1;A2;A3;A;B;B1;C;D;D01;D02
111;111000;Krfr. Stadt Düsseldorf;101;Urne;1110;138;0;1248;283;0;1;282;57;42
314;314000;Krfr. Stadt Bonn;11;Urne;1053;549;0;1602;479;0;3;476;102;43
314;314000;Krfr. Stadt Bonn;010 A;Brief;0;0;0;0;996;996;4;992;300;200
"""

# Straße;PLZ;Ort;von;vonAlpha;bis;bisAlpha;gerade/ungerade;Stimmbezirk;…;Wahlvorstand (wird nicht gelesen)
STRASSEN = """strasse_strassenname;plz;ort;von;va;bis;ba;gu;sb;sb_bez;art;ot;wb;wb_bez;x;x;x;x;x;Name;Telefon
Abenteuerweg;53125;Bonn;;;;;;412;412 X;W;Hardtberg;41;41 Y;;;;;;Muster;0228 1
Langer Weg;53111;Bonn;1;;9;;ung.;11;;W;;1;;;;;;;Muster;0228 1
Langer Weg;53111;Bonn;2;;10;;ger.;12;;W;;1;;;;;;;Muster;0228 1
Endenicher Str.;53115;Bonn;1;;99;;;13;;W;;1;;;;;;;Muster;0228 1
"""


class Lesen(unittest.TestCase):
    def test_nur_bonn_ohne_parteien(self):
        rows = wahlen.stimmbezirke(ITNRW)
        self.assertEqual([(r["stimmbezirk"], r["art"], r["wahlbezirk"]) for r in rows], [("11", "Urne", 1), ("010 A", "Brief", 1)])
        self.assertEqual((rows[0]["wahlberechtigte"], rows[0]["sperrvermerk_w"], rows[0]["waehler"]), (1602, 549, 479))
        self.assertEqual(set(rows[0]), {"stimmbezirk", "art", "wahlbezirk", "wahlberechtigte", "sperrvermerk_w", "waehler"})

    def test_zuordnung_nach_adressen(self):
        hn = {"Abenteuerweg": {"Brüser Berg": ["1", "3"]}, "Langer Weg": {"Endenich": ["3", "4", "5a"]},
              "Endenicher Straße": {"Endenich": ["7"]}, "Fehlweg": {"Endenich": ["1"]}}
        zu, (treffer, ohne_str, ohne_nr) = wahlen.zuordnung(STRASSEN, hn)
        self.assertEqual({k: dict(v) for k, v in zu.items()},
                         {"412": {"Brüser Berg": 2}, "11": {"Endenich": 2}, "12": {"Endenich": 1}, "13": {"Endenich": 1}})
        self.assertEqual((treffer, ohne_str, ohne_nr), (6, 1, 0))


if __name__ == "__main__":
    unittest.main()
