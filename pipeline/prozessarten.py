"""Reiter „Prozesse“: Verfahrensarten mit Zahlen aus Bonn und Gremien mit Zuständigkeit (data/export/bonn/prozessarten.json).

Die Verfahren selbst (Schritte, Bahnen, Fristen, Rechtsgrundlagen) und die Zuständigkeitsordnung stehen in soll.json;
diese Datei ergänzt je Verfahren die Zahl der Vorgänge in Bonn mit Beispielen (Zuordnung abgeleitet, pipeline/soll.py)
und je Gremium Art, Beratungen, letzte und nächste Sitzung (OParl-API der Stadt Bonn, CC0)."""
import collections
import datetime
import json

from . import config, soll

# Gremienarten der OParl-API, die Entscheidungen treffen oder beraten (ohne Fraktionen, Gruppen und interne Gremien)
ARTEN = {"Rat": "rat", "Ratsgremien": "ausschuss", "Bezirksvertretungen": "bezirksvertretung",
         "Beiräte und Kommissionen": "beirat"}
# Abschnitt der Zuständigkeitsordnung, dessen Titel vom Namen des Gremiums in der OParl-API abweicht
ZUSTO_ALIAS = {"Ausschuss für Soziales, Migration, Gesundheit, Wohnen und Senioren":
               "Ausschuss für Soziales, Migration, Gesundheit und Senioren"}
BEISPIELE = 3


def art(name, classification):
    """Feinere Art eines Gremiums: rat, hauptausschuss, ausschuss, unterausschuss, wahlausschuss, bezirksvertretung, beirat."""
    a = ARTEN.get(classification)
    if a != "ausschuss":
        return a
    if name == "Hauptausschuss":
        return "hauptausschuss"
    if "Unterausschuss" in name:
        return "unterausschuss"
    if "wahl" in name.lower():
        return "wahlausschuss"
    return "ausschuss"


def _term_start(terms, today):
    """Beginn der laufenden Wahlperiode (OParl legislativeTerms)."""
    starts = [t["startDate"] for t in terms if t.get("startDate") and t["startDate"] <= today
              and (not t.get("endDate") or t["endDate"] >= today)]
    return max(starts) if starts else None


def verfahren(rows, titles):
    """Je Verfahren: Zahl der Vorgänge und die jüngsten Beispiele (Stammnummer, Titel, Datum)."""
    out = {}
    by = collections.defaultdict(list)
    for r in rows:
        if r["verfahren"]:
            by[r["verfahren"]].append(r)
    for vid, rs in by.items():
        known = [r for r in rs if r["stammnummer"] in titles]
        known.sort(key=lambda r: (titles[r["stammnummer"]][1] or "", r["stammnummer"]), reverse=True)
        out[vid] = {"vorgaenge": len(rs), "sicher": sum(r["sicherheit"] == "hoch" for r in rs),
                    "beispiele": [{"drucksache": r["stammnummer"], "titel": titles[r["stammnummer"]][0],
                                   "datum": titles[r["stammnummer"]][1]} for r in known[:BEISPIELE]]}
    return out


def gremien(db, meetings, zusto, today, term_start):
    """Gremien mit Art, Zahl der Beratungen und Vorlagen, letzter und nächster Sitzung, Abschnitt der Zuständigkeitsordnung."""
    stats = {oid: (n, k, last) for oid, n, k, last in db.execute(
        "SELECT c.organization_id, COUNT(*), COUNT(DISTINCT c.paper_id), MAX(substr(m.start_date, 1, 10)) "
        "FROM consultation c LEFT JOIN meeting m ON m.id = c.meeting_id GROUP BY c.organization_id")}
    upcoming = {}
    for m in sorted(meetings, key=lambda m: m.get("start") or ""):
        day = (m.get("start") or "")[:10]
        if day < today or m.get("cancelled"):
            continue
        for oid in m.get("organization") or []:
            upcoming.setdefault(oid, {"datum": day, "web": m.get("web")})
    out = []
    for oid, name, cls, end, web in db.execute(
            "SELECT id, name, classification, end_date, web FROM organization WHERE org_type = 'Gremium'"):
        a = art(name, cls)
        if not a:
            continue
        n, k, last = stats.get(oid, (0, 0, None))
        nxt = upcoming.get(oid)
        ended = bool(end) and end < today
        # aktuell: nicht aufgelöst und in der laufenden Wahlperiode zusammengetreten oder mit angesetzter Sitzung
        aktuell = not ended and (bool(nxt) or bool(last and term_start and last >= term_start))
        key = name if name in zusto else ZUSTO_ALIAS.get(name)
        g = {"id": oid.rsplit("/", 1)[-1], "name": name, "art": a, "aktuell": aktuell, "beratungen": n, "vorlagen": k,
             "letzte": last, "naechste": nxt, "aufgeloest": end if ended else None, "web": web}
        if key in zusto:
            g["zusto"] = key
            if key != name:
                g["zusto_hinweis"] = f"In der Zuständigkeitsordnung als „{key}“ geführt (Zuordnung abgeleitet)."
        out.append(g)
    order = ["rat", "hauptausschuss", "ausschuss", "bezirksvertretung", "beirat", "unterausschuss", "wahlausschuss"]
    out.sort(key=lambda g: (not g["aktuell"], order.index(g["art"]), -g["beratungen"], g["name"]))
    return out


def site_data(db, today=None):
    today = today or datetime.date.today().isoformat()
    rows = soll.vorgaenge(db)
    titles = {ref: (name, date) for ref, name, date in db.execute("SELECT reference, name, date FROM paper")}
    meetings = json.loads(config.MEETINGS.read_text()) if config.MEETINGS.exists() else []
    meetings = meetings.get("data", []) if isinstance(meetings, dict) else meetings
    terms = json.loads(config.LEGISLATIVE_TERMS.read_text()) if config.LEGISLATIVE_TERMS.exists() else []
    term_start = _term_start(terms, today)
    zusto = soll.site_data()["zusto"]
    return {
        "meta": {"quellen": "OParl-API der Stadt Bonn (CC0): Gremien, Beratungen, Sitzungen; Zuordnung der Vorgänge "
                            "zu Verfahren abgeleitet (Soll-Modell nach „Bonn entscheidet“, MIT)",
                 "wahlperiode_seit": term_start,
                 "hinweis": "Zahlen je Verfahren beruhen auf der abgeleiteten Zuordnung; Sicherheit „hoch“ separat ausgewiesen."},
        "verfahren": verfahren(rows, titles),
        "gremien": gremien(db, meetings, zusto, today, term_start),
    }
