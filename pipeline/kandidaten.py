"""Kandidaten „Beschluss ↔ Baustelle“ (Phase 3): Welche entschiedenen Vorlagen könnten mit einer Baustelle der
Stadt zusammenhängen? Ergebnis ist ein Kandidat mit Konfidenz und einzeln ausgewiesenen Kriterien, nie die Aussage
„umgesetzt“. Termine der Baustellen sind laut Quelle unverbindlich.

Kriterien:
- räumlich: Abstand zwischen Baustelle und Ortsbezug der Vorlage (Straßenpunkt, Bebauungsplan, Koordinate der
  Stadt) höchstens 150 m – Straßenpunkte sind repräsentative Punkte ganzer Straßen, daher großzügig;
- Straße: Straßenname der Baustelle (Bezeichnung oder Adresse) gleich einem Straßennamen der Vorlage;
- zeitlich: die Vorlage ist entschieden, und die Baustelle beginnt am oder nach dem Tag der Entscheidung;
- thematisch: federführend oder fachlich Tiefbauamt (66) bzw. Stadtverkehr (61-3) oder Thema Verkehr;
- Stichwort: Bau-Stichwort im Titel, passend zur Maßnahme der Baustelle (Kanalbau: Kanal, Entwässerung, Abwasser;
  sonst Ausbau, Umgestaltung, Erneuerung, Sanierung …).
Baustellen fremder Träger (Versorger, Straßen NRW, Bahn) setzen in der Regel keinen Ratsbeschluss um und werden
getrennt ausgewiesen."""
import json
import math
import re
from datetime import date
from pathlib import Path

from . import baustellen, config

MAX_DIST = 150
OWN = re.compile(r"Bundesstadt Bonn|^Amt \d|Stadt Bonn", re.I)
BUILD = re.compile(r"(?i)ausbau|umbau|umgestaltung|neugestaltung|erneuerung|sanierung|neubau|baureife planung|"
                   r"ausführungsplanung|herstellung|verbreiterung|instandsetzung|radweg(?!benutzung)|gehweg|fahrbahn|"
                   r"baumaßnahme|baubeginn")
SEWER = re.compile(r"(?i)kanal|entwässerung|abwasser|regenwasser|starkregen")
TSV = ["konfidenz", "baustelle_id", "bezeichnung", "massnahme", "traeger", "von", "bis", "drucksache", "titel",
       "entschieden_am", "abstand_m", "kriterium_strasse", "kriterium_thema", "kriterium_stichwort", "begruendung",
       "pruefvermerk"]


def street(name):
    """„Hermann-Wandersleb-Ring (B56)“, „Siemensstraße 50“, „Siemensstr.“ → „siemensstraße“ bzw. ohne Zusatz."""
    n = re.sub(r"\s*\(.*?\)", "", name or "").strip()
    n = re.sub(r"\s+\d+\s*[a-zA-Z]?(?:\s*[-–]\s*\d+\s*[a-zA-Z]?)?$", "", n)
    n = re.sub(r"(?i)str\.?$", "straße", n).replace("Strasse", "Straße").replace("strasse", "straße")
    return n.lower()


def parse_de(d):
    m = re.match(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", d or "")
    return date(int(m.group(3)), int(m.group(2)), int(m.group(1))) if m else None


def distance_m(lon1, lat1, lon2, lat2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 6371000 * 2 * math.asin(math.sqrt(a))


def decided_on(p):
    """Tag der (letzten) Entscheidung einer entschiedenen Vorlage, sonst None."""
    if p.get("stand") != "entschieden":
        return None
    days = [s["date"] for s in p.get("steps", []) if s.get("typ") == "entscheidung" and s.get("date")]
    return date.fromisoformat(max(days)) if days else None


def build_word(title, massnahme):
    """Bau-Stichwort im Titel, das zur Maßnahme passt (Kanalbau verlangt einen Bezug zur Entwässerung)."""
    return bool((SEWER if "kanal" in (massnahme or "").lower() else BUILD).search(title or ""))


def thematic(p):
    names = [p.get("amt") or ""] + [r.get("name") or "" for r in p.get("responsibility", [])]
    return any(n.startswith(("66", "61-3")) for n in names) or any(t.get("theme") == "verkehr" for t in p.get("themes", []))


def load_papers(base=None):
    """Alle Vorlagen mit Ortsbezug aus den Gebietsdateien (ohne Doppelte)."""
    base = Path(base or config.EXPORT / "bonn")
    papers = {}
    for f in sorted([*(base / "ortsteile").glob("*.json"), *(base / "bezirke").glob("*.json")]):
        for p in json.loads(f.read_text(encoding="utf-8"))["papers"]:
            papers.setdefault(p["reference"], p)
    return list(papers.values())


def load_sites(archive=None, fetcher=None):
    """Aktive Baustellen aus dem Archiv (Branch archiv) oder, falls nicht vorhanden, direkt aus dem Feed „1 Jahr“."""
    state_file = Path(archive or config.BAUSTELLEN_ARCHIV) / "baustellen.json"
    if state_file.exists():
        state = json.loads(state_file.read_text(encoding="utf-8"))
        return {k: v["angaben"] for k, v in state.items() if v.get("aktiv")}, "Archiv"
    feats, _ = (fetcher or baustellen.fetch)(14698)
    return baustellen.normalize(feats), "Feed 14698 (direkt)"


def candidates(sites, papers):
    """Kandidaten je Baustelle und Vorlage mit Kriterien und Konfidenz; fremde Träger mit Konfidenz „fremd“."""
    points = []
    for p in papers:
        when = decided_on(p)
        if not when:
            continue
        locs = [l for l in p.get("locations", []) if l.get("lon") is not None and l.get("method") != "vererbt"
                and l.get("level") in ("strasse", "bebauungsplan")]
        if locs:
            points.append((p, when, locs, {street(l.get("name")) for l in locs if l.get("level") == "strasse"}))
    out = []
    for bid, s in sites.items():
        if s.get("lon") is None:
            continue
        begin = parse_de(s.get("von"))
        names = {street(s.get("bezeichnung")), street(s.get("adresse"))} - {""}
        own = bool(OWN.search(s.get("traeger") or ""))
        for p, when, locs, pstreets in points:
            dist = min(distance_m(s["lon"], s["lat"], l["lon"], l["lat"]) for l in locs)
            if dist > MAX_DIST or not begin or begin < when:
                continue
            same, theme, word = bool(names & pstreets), thematic(p), build_word(p["name"], s.get("massnahme"))
            if not own:
                conf = "fremd"
            elif same and theme and word:
                conf = "hoch"
            elif same and (theme or word):
                conf = "mittel"
            else:
                conf = "niedrig"
            why = [f"{round(dist)} m entfernt", "gleiche Straße" if same else "andere Straße",
                   f"Baubeginn {s.get('von')} nach Entscheidung {when.strftime('%d.%m.%Y')}",
                   "Tiefbau/Verkehr" if theme else "anderes Amt/Thema", "Bau-Stichwort passend zur Maßnahme" if word else "kein passendes Bau-Stichwort",
                   "städtischer Träger" if own else f"fremder Träger ({s.get('traeger')})"]
            out.append({"konfidenz": conf, "baustelle_id": bid, "bezeichnung": s.get("bezeichnung"), "massnahme": s.get("massnahme"),
                        "traeger": s.get("traeger"), "von": s.get("von"), "bis": s.get("bis"), "drucksache": p["reference"],
                        "titel": p["name"], "entschieden_am": when.isoformat(), "abstand_m": round(dist),
                        "kriterium_strasse": "ja" if same else "nein", "kriterium_thema": "ja" if theme else "nein",
                        "kriterium_stichwort": "ja" if word else "nein", "begruendung": "; ".join(why), "pruefvermerk": "ungeprüft"})
    rank = {"hoch": 0, "mittel": 1, "niedrig": 2, "fremd": 3}
    return sorted(out, key=lambda c: (rank[c["konfidenz"]], c["baustelle_id"], c["abstand_m"], c["drucksache"]))


def sample(cands, n=30, per_site=2):
    """Stichprobe zur Prüfung: zuerst hoch, dann mittel, dann niedrig; höchstens per_site je Baustelle und je
    Baustelle nur eine Vorlage desselben Vorgangs (Änderungsanträge und Stellungnahmen zählen zur Hauptvorlage)."""
    picked, count, seen = [], {}, set()
    for c in cands:
        key = (c["baustelle_id"], c["drucksache"].split("-")[0])
        if c["konfidenz"] == "fremd" or count.get(c["baustelle_id"], 0) >= per_site or key in seen:
            continue
        seen.add(key)
        picked.append(c)
        count[c["baustelle_id"]] = count.get(c["baustelle_id"], 0) + 1
        if len(picked) == n:
            break
    return picked


def _tsv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    clean = lambda v: str(v if v is not None else "").replace("\t", " ").replace("\n", " ")
    path.write_text("\t".join(TSV) + "\n" + "".join("\t".join(clean(r[k]) for k in TSV) + "\n" for r in rows), encoding="utf-8")


def write():
    """Audit aller Kandidaten und Stichprobe (die Stichprobe wird nie überschrieben)."""
    sites, origin = load_sites()
    cands = candidates(sites, load_papers())
    _tsv(config.EXPORT / "baustellen_kandidaten.tsv", cands)
    sample_file = config.EXPORT / "baustellen" / "stichprobe_kandidaten.tsv"
    if not sample_file.exists():
        _tsv(sample_file, sample(cands))
    by = {k: sum(1 for c in cands if c["konfidenz"] == k) for k in ("hoch", "mittel", "niedrig", "fremd")}
    print(f"Baustellen ({origin}): {len(sites)} aktiv; Kandidaten {by}; "
          f"Baustellen mit Kandidat (hoch/mittel): {len({c['baustelle_id'] for c in cands if c['konfidenz'] in ('hoch', 'mittel')})}")
    return cands
