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


if __name__ == "__main__":
    unittest.main()
