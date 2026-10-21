"""Verzeichnis der Gebäude und Anlagen (OSM, ODbL; `fetch-objects` → data/geo/objekte_bonn.json) für Stufe C.

Abgleich über den angeglichenen Namen: Groß- und Kleinschreibung, Satzzeichen, Bindestriche und typische Vorsätze
(„GGS“, „Kita“, „Städt.“, „ehem.“) zählen nicht. Ein Name zählt nur, wenn er in genau einem Ortsteil vorkommt; liegt
er in mehreren Ortsteilen („Alter Friedhof“), entscheidet der Ortsteil, den der Text nennt, sonst wird nicht
verortet. Ein kürzerer Name passt auf einen längeren, wenn er darin als ganze Wortfolge steht („Rheinaue“ →
„Freizeitpark Rheinaue“), mindestens acht Zeichen hat und dabei nur ein Ortsteil herauskommt. Gattungsnamen
(„Spielplatz“, „Friedhof“) zählen nie.
"""
import json
import re
from collections import defaultdict

from . import config

VORSAETZE = {"ggs", "kgs", "ogs", "ggs/ogs", "städt", "städtische", "städtischer", "städtisches", "kita", "kindertagesstätte",
             "ehem", "ehemalige", "ehemaliger", "ehemaliges", "die", "der", "das", "bonner"}
GATTUNG = {"spielplatz", "friedhof", "sportplatz", "turnhalle", "sporthalle", "schule", "grundschule", "kita",
           "kindergarten", "bibliothek", "stadtbibliothek", "park", "garten", "bolzplatz", "schulhof", "kirche",
           "rathaus", "schwimmbad", "hallenbad", "freibad", "feuerwache", "museum", "theater", "jugendzentrum",
           "bürgerhaus", "stadtteilbibliothek", "waldfriedhof", "parkfriedhof", "gesamtschule", "gymnasium",
           "realschule", "hauptschule", "förderschule", "mehrzweckhalle", "stadthalle", "altenheim"}
MIN_TEIL = 8


def norm(name):
    """Angeglichener Name; „Bonn“ und „Bonner“ zählen nirgends („Freizeitpark Bonner Rheinaue“)."""
    words = re.sub(r"[^\w/]+", " ", (name or "").lower().replace("-", " ")).split()
    while words and words[0].strip(".") in VORSAETZE:
        words = words[1:]
    return " ".join(w for w in words if w not in ("bonn", "bonner"))


class Objekte:
    def __init__(self, data=None):
        if data is None:
            data = json.loads(config.OBJEKTE.read_text())["objekte"] if config.OBJEKTE.exists() else {}
        self.by_norm = defaultdict(dict)   # angeglichener Name → Ortsteil → Objekt (eines je Ortsteil)
        self.ohne_leer = {}                 # Name ohne Leerzeichen → angeglichener Name („Posttower“ → „post tower“)
        for osm, o in sorted(data.items()):
            n = norm(o["name"])
            if len(n) >= 4 and n not in GATTUNG:
                self.by_norm[n].setdefault(o["ortsteil"], dict(o, osm=osm))
                self.ohne_leer.setdefault(n.replace(" ", ""), n)

    def __len__(self):
        return len(self.by_norm)

    def finden(self, name, ortsteil_im_text=""):
        """(Objekt, Befund) für einen Namen; Objekt None, wenn kein eindeutiger Treffer."""
        n = norm(name)
        if len(n) < 4 or n in GATTUNG:
            return None, "Gattungsname"
        cands = self.by_norm.get(n) or self.by_norm.get(self.ohne_leer.get(n.replace(" ", ""), ""))
        art = "Name"
        if not cands and len(n) >= MIN_TEIL:
            # kürzester passender Name je Ortsteil („LVR-Landesmuseum Bonn“ vor „…, Bibliothek“)
            pat = re.compile(rf"(^| ){re.escape(n)}( |$)")
            cands = {}
            for key in sorted((k for k in self.by_norm if pat.search(k)), key=len, reverse=True):
                for ot, o in self.by_norm[key].items():
                    cands[ot] = o
            art = "Teil des Namens"
        if not cands:
            return None, "nicht im Verzeichnis"
        if len(cands) == 1:
            return next(iter(cands.values())), art
        if ortsteil_im_text in cands:
            return cands[ortsteil_im_text], f"{art}, Ortsteil laut Text"
        return None, f"mehrdeutig ({len(cands)} Ortsteile)"
