import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from pipeline import config, kurzfassung

TEXT = ("Die Verwaltung schlägt vor, den Spielplatz an der Endenicher Straße neu zu gestalten. "
        "Dazu sollen neue Geräte aufgestellt und die Wege erneuert werden. Die Kosten trägt der städtische Haushalt.")


class KurzfassungTest(unittest.TestCase):
    def test_wortliche_uebernahme_wird_erkannt(self):
        self.assertIsNotNone(kurzfassung.uebernahme("Dazu sollen neue Geräte aufgestellt und die Wege erneuert werden.", TEXT))
        self.assertIsNone(kurzfassung.uebernahme("Der Spielplatz bekommt neue Geräte und bessere Wege.", TEXT))

    def test_fraktion_und_gremium_nur_mit_beleg(self):
        text = "Die Verwaltung wird gebeten, den Spielplatz an der Endenicher Straße zu erneuern."
        kurz = "Die Grünen möchten einen neuen Spielplatz in Endenich. Darüber entscheidet bald der Rat."
        self.assertEqual(kurzfassung.fremder_akteur(kurz, text), "Grüne")
        self.assertEqual(kurzfassung.fremder_akteur(kurz, "Antrag der Fraktion BÜNDNIS 90/DIE GRÜNEN " + text), "Rat")
        self.assertIsNone(kurzfassung.fremder_akteur(kurz, "Antrag von Bündnis 90/Die Grünen an den Rat " + text))
        self.assertIsNone(kurzfassung.fremder_akteur("Der Beirat empfiehlt den Spielplatz.", text))
        self.assertEqual(kurzfassung.pruefe(kurz, text, "Antrag der Grünen"), "nicht in Titel oder Text: Rat")

    def test_pruefe(self):
        gut = "Der Spielplatz in Endenich soll neue Geräte und bessere Wege bekommen. Bezahlt wird das aus dem Haushalt der Stadt."
        self.assertIsNone(kurzfassung.pruefe(gut, TEXT))
        self.assertEqual(kurzfassung.pruefe("Zu kurz.", TEXT), "zu kurz")
        self.assertEqual(kurzfassung.pruefe("Ein Anwohner der Endenicher Straße 12 möchte einen neuen Spielplatz.", TEXT),
                         "Hausnummer genannt")
        self.assertTrue(kurzfassung.pruefe("Die Verwaltung schlägt vor, den Spielplatz an der Endenicher Straße neu zu gestalten.", TEXT)
                        .startswith("wörtliche Übernahme"))

    def test_markdown_wird_entfernt(self):
        self.assertEqual(kurzfassung.glaetten("Baum in der Straße *Am Herrengarten*, **gefällt**."),
                         "Baum in der Straße Am Herrengarten, gefällt.")
        self.assertEqual(kurzfassung.glaetten("3 * 4 Bäume"), "3 * 4 Bäume")

    def test_kostensatz_und_fremde_zahlen(self):
        text = "Die Verwaltung gewährt einen Zuschuss von 20.000 EUR für 2023 und 1.661.000 EUR für 2024."
        kurz = "Die Verwaltung schlägt einen Zuschuss von 20.000 Euro vor. Die Kosten trägt die Stadt."
        self.assertEqual(kurzfassung.ohne_kostensatz(kurz, text), "Die Verwaltung schlägt einen Zuschuss von 20.000 Euro vor.")
        self.assertEqual(kurzfassung.ohne_kostensatz(kurz, text + " Die Kosten trägt der Antragsteller."), kurz)
        self.assertIsNone(kurzfassung.fremde_zahl("Zuschuss von 1.661.000 Euro für 2024, Teil 2.", text))
        self.assertEqual(kurzfassung.fremde_zahl("insgesamt rund 4,1 Millionen Euro", text), "4,1")
        self.assertIsNone(kurzfassung.fremde_zahl("Der Vertrag endet 2024.", "Er läuft zum 31.12.2024 aus."))

    def test_ueberschrift_wird_entfernt(self):
        for kopf in ("Stellungnahme der Verwaltung", "Stadt Bonn – Mitteilung", "Beschlussvorlage der Verwaltung:",
                     "Absender: Mehrere Fraktionen (interfraktioneller Antrag)\nArt der Vorlage: Vorschlag"):
            self.assertEqual(kurzfassung.glaetten(f"{kopf}\n\nDie Verwaltung schlägt vor, den Baum zu fällen. Ersatz folgt."),
                             "Die Verwaltung schlägt vor, den Baum zu fällen. Ersatz folgt.")
        self.assertEqual(kurzfassung.glaetten("Kurz und ohne Punkt"), "Kurz und ohne Punkt")   # nur eine Zeile: bleibt

    def test_ohne_schluessel_nichts(self):
        with mock.patch.dict(os.environ, {}, clear=True), tempfile.TemporaryDirectory() as d:
            kurzfassung.erzeugen(d, anfrage=lambda *a: self.fail("keine Anfrage ohne Schlüssel"))
            self.assertFalse((Path(d) / "kurzfassungen.jsonl").exists())

    def test_erzeugen_nur_neue_und_verwirft_auszuege(self):
        with tempfile.TemporaryDirectory() as d:
            texte, papers = Path(d) / "texte.jsonl", Path(d) / "papers.jsonl"
            texte.write_text("\n".join(json.dumps({"uri": f"f{i}", "sha": f"s{i}", "papers": [], "text": TEXT}) for i in range(3)))
            papers.write_text("\n".join(json.dumps({"reference": f"26000{i}", "name": "Spielplatz", "paperType": t,
                                                    "mainFile": {"id": f"f{i}"}})
                                        for i, t in enumerate(["Beschlussvorlage", "Antrag", "Bürgerantrag § 24 GO"])))
            antworten = iter(["Der Spielplatz in Endenich soll neue Geräte und bessere Wege bekommen, bezahlt von der Stadt.",
                              "Dazu sollen neue Geräte aufgestellt und die Wege erneuert werden, sagt der Antrag."])
            calls = []
            def anfrage(titel, text, key):
                calls.append(titel)
                return next(antworten), {"prompt_tokens": 100, "completion_tokens": 30}
            out = Path(d) / "kurz"
            with mock.patch.dict(os.environ, {"MISTRAL_API_KEY": "test"}), \
                    mock.patch.object(config, "TEXTE", texte), mock.patch.object(config, "PAPERS", papers):
                kurzfassung.erzeugen(out, anfrage=anfrage)
                kurzfassung.erzeugen(out, anfrage=anfrage)  # zweiter Lauf: nichts Neues
            rows = kurzfassung.laden(out)
            self.assertEqual(len(calls), 2)  # Bürgerantrag ausgenommen, zweiter Lauf ohne Anfragen
            self.assertEqual(sorted(r["verworfen"] or "ok" for r in rows.values()),
                             ["ok", f"wörtliche Übernahme von mehr als {kurzfassung.UEBERNAHME_WOERTER} Wörtern"])
            self.assertEqual(kurzfassung.fuer_seite(out), {})  # vor der Freigabe nichts auf der Seite
            self.assertEqual(len((out / "laeufe.tsv").read_text().splitlines()), 2)  # Kopf und ein Lauf mit Anfragen
            # ältere Fassung wird neu erzeugt
            rows = kurzfassung.laden(out)
            for r in rows.values():
                r.pop("fassung")
            (out / "kurzfassungen.jsonl").write_text("\n".join(json.dumps(r) for r in rows.values()) + "\n")
            antworten = iter(["Die Verwaltung schlägt vor, den Spielplatz mit neuen Geräten und Wegen auszustatten."] * 2)
            with mock.patch.dict(os.environ, {"MISTRAL_API_KEY": "test"}), \
                    mock.patch.object(config, "TEXTE", texte), mock.patch.object(config, "PAPERS", papers):
                kurzfassung.erzeugen(out, anfrage=anfrage)
            self.assertEqual(len(calls), 4)
            self.assertTrue(all(r["fassung"] == kurzfassung.FASSUNG for r in kurzfassung.laden(out).values()))


if __name__ == "__main__":
    unittest.main()
