import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from pipeline import publish

PAPER = {
    "reference": "261856", "name": "Radweg <Endenicher> Straße & Co.", "paper_type": "Antrag",
    "date": "2026-05-04", "amt": "66 Tiefbauamt", "stand": "in Beratung", "web": "https://example.org/vo?x=1&y=2",
    "source_object": "https://www.bonn.sitzung-online.de/oparl/papers/1", "locations": [],
    "steps": [
        {"typ": "initiierung", "label": "Antrag", "status": "belegt"},
        {"typ": "beratung", "label": "Bezirksvertretung Bonn", "role": "Empfehlung", "date": "2026-06-10",
         "result": "vertagt", "status": "belegt"},
        {"typ": "entscheidung", "label": "Rat", "role": "Entscheidung", "status": "belegt"},
        {"typ": "folgevorlage", "label": "Stellungnahme der Verwaltung", "reference": "261856-01 ST",
         "title": "Stellungnahme", "date": "2026-06-01", "status": "belegt"},
    ],
}
ATOM = "{http://www.w3.org/2005/Atom}"


class Feeds(unittest.TestCase):
    def test_ereignisse(self):
        ev = publish.events(PAPER)
        self.assertEqual([e["id"].split("#")[1] for e in ev], ["vorlage", "beratung-2026-06-10-Bezirksvertretung%20Bonn"])
        # ID bleibt, wenn davor ein Schritt hinzukommt (bisher Position in der Liste)
        mehr = {**PAPER, "steps": [{"typ": "folgevorlage", "label": "Mitteilung", "reference": "261856-02",
                                    "title": "Mitteilung", "date": "2026-05-01", "status": "belegt"}] + PAPER["steps"]}
        self.assertEqual([e["id"] for e in publish.events(mehr)], [e["id"] for e in ev])
        self.assertEqual(len(publish.events(PAPER, with_followups=True)), 3)
        self.assertNotIn("KI-Kurzfassung", ev[0]["summary"])
        kurz = {**PAPER, "kurzfassung": {"text": "Es geht um Bäume.", "modell": "m", "erzeugt": "2026-10-21"}}
        self.assertTrue(publish.events(kurz)[0]["summary"].endswith(
            "KI-Kurzfassung (abgeleitet, Einzelheiten können ungenau sein): Es geht um Bäume."))

    def test_atom_ist_wohlgeformt_und_stabil(self):
        entries = [{**e, "link": "https://site/?gebiet=ortsteil:endenich#261856", "original": PAPER["web"]}
                   for e in publish.events(PAPER)]
        xml = publish._atom("tag:x,2026:feed/a", "T & <a>", "S", "https://site/f.xml", "https://site/", entries)
        root = ET.fromstring(xml.encode())
        self.assertEqual(root.find(ATOM + "updated").text, "2026-06-10T00:00:00Z")  # jüngstes Ereignis, keine Uhrzeit
        self.assertEqual(len(root.findall(ATOM + "entry")), 2)
        self.assertEqual(xml, publish._atom("tag:x,2026:feed/a", "T & <a>", "S", "https://site/f.xml",
                                            "https://site/", list(reversed(entries))))

    def test_feed_je_vorlage_nur_wo_sich_etwas_aendern_kann(self):
        self.assertTrue(publish.has_paper_feed(PAPER, "2025-01-01"))
        alt = {**PAPER, "date": "2020-01-01", "stand": "entschieden"}
        self.assertFalse(publish.has_paper_feed(alt, "2025-01-01"))
        self.assertTrue(publish.has_paper_feed({**alt, "stand": "offen"}, "2025-01-01"))


class Kalender(unittest.TestCase):
    def test_faltung_grenzfall(self):
        for n in range(70, 160):
            folded = publish._ics_fold("X" * n).encode()
            self.assertTrue(all(len(x) <= 75 for x in folded.split(b"\r\n")), n)
            self.assertEqual(folded.replace(b"\r\n ", b""), b"X" * n)

    def test_ics(self):
        meetings = [{"date": "2026-11-04", "start": "2026-11-04T17:00:00+01:00", "end": "2026-11-04T23:59:59+01:00",
                     "gremium": "Bezirksvertretung Bad Godesberg", "name": "Sitzung der Bezirksvertretung, "
                     "Bad Godesberg; mit sehr langem Namen, der gefaltet werden muss ÄÖÜ ÄÖÜ ÄÖÜ ÄÖÜ",
                     "cancelled": False, "web": None, "invitation": None,
                     "source_object": "https://www.bonn.sitzung-online.de/oparl/meetings/1"}]
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "t.ics"
            publish.write_calendar(path, meetings, today=publish.date(2026, 10, 18))
            raw = path.read_bytes()
        self.assertIn(b"DTSTART:20261104T160000Z", raw)
        self.assertNotIn(b"DTEND", raw)  # 23:59:59 ist kein echtes Ende
        self.assertTrue(all(len(line) <= 75 for line in raw.split(b"\r\n")))
        self.assertIn("Bezirksvertretung\\, Bad Godesberg\;".encode(), raw.replace(b"\r\n ", b""))
        raw.decode("utf-8")  # Faltung trennt keine Umlaute



class Dcat(unittest.TestCase):
    def test_kurzfassungen_nur_nach_freigabe(self):
        import json
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "dcat.jsonld"
            publish.write_dcat(path, "2019-10-01", "2026-10-21")
            files = [x["@id"] for x in json.loads(path.read_text())["dcat:distribution"]]
            self.assertFalse(any(f.endswith("kurzfassungen.tsv") for f in files))
            publish.write_dcat(path, "2019-10-01", "2026-10-21", kurzfassungen=True)
            dist = json.loads(path.read_text())["dcat:distribution"][-1]
            self.assertTrue(dist["@id"].endswith("bonn/kurzfassungen.tsv"))
            self.assertIn("Sprachmodell", dist["dct:description"]["@value"])


if __name__ == "__main__":
    unittest.main()
