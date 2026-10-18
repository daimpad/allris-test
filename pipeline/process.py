"""Prozessebene: Schritte je Vorlage mit Evidenzstatus (PROMPT_prozessebene_v0.1, Abschnitt 3–4).

Evidenzstatus
- belegt            Schritt ist als Datenobjekt in einer Quelle vorhanden (OParl-API der Stadt)
- abgeleitet        aus Quelldaten erschlossen (Join mit OParl-Lite, Textmuster, Vererbung)
- soll              nach Regelwerk zu erwarten, nicht dokumentiert (Soll-Modell noch nicht formalisiert)
- nicht_öffentlich  findet regelmäßig statt, ist extern nicht einsehbar
- unklar            aus öffentlichen Quellen nicht bestimmbar

Lücken werden als eigene Schritte ausgegeben, nicht weggelassen.
"""
from .actors import EINWOHNER_TYPES, POLITIK_TYPES, VERWALTUNG_TYPES

SONDER_TYPES = {
    "Dringlichkeitsentscheidung OB": "Dringlichkeitsentscheidung der Oberbürgermeisterin bzw. des Oberbürgermeisters",
    "Dringlichkeitsentscheidung BV": "Dringlichkeitsentscheidung in der Bezirksvertretung",
    "Eilentscheidung HA": "Eilentscheidung im Hauptausschuss",
}
NICHTOEFFENTLICH_TYPE = "Tagesordnungspunkte in nichtöffentlicher Sitzung"
SCHLEIFE = ("vertagt", "verwiesen", "nicht aufgenommen")
VOLLZUG = ("beschlossen",)

# Erläuterungen; in den Exporten steht nur der Schlüssel (`note`), die Texte stehen in der Seite.
NOTES = {
    "sonderweg": "Sonderweg: Entscheidung vor der Beratung, nachträgliche Genehmigung durch das Gremium.",
    "vorbereitung": "Erarbeitung, Mitzeichnung und Freigabe der Vorlage in der Verwaltung sind von "
                    "außen nicht einsehbar.",
    "datum": "Datum der Vorlage laut Ratsinformationssystem; ob es Erstellung, Freigabe oder "
             "Veröffentlichung bezeichnet, ist nicht dokumentiert.",
    "ohne_sitzung": "Beratung ist vorgesehen; Sitzung und Ergebnis sind (noch) nicht verknüpft.",
    "vollzug": "Ob und wann der Beschluss umgesetzt ist, steht in der Beschlusskontrolle; dafür gibt "
               "es keine öffentliche Schnittstelle.",
    "nichtoeffentlich": "Der Tagesordnungspunkt wurde nichtöffentlich beraten; Inhalte sind nicht einsehbar.",
}


def initiation_kind(paper_type):
    if paper_type in SONDER_TYPES:
        return "sonderweg"
    if paper_type == NICHTOEFFENTLICH_TYPE:
        return "nichtoeffentlich"
    if paper_type in EINWOHNER_TYPES:
        return "einwohner"
    if paper_type in POLITIK_TYPES:
        return "anfrage" if "Anfrage" in paper_type else "antrag"
    if paper_type in VERWALTUNG_TYPES:
        return "verwaltung"
    return "sonstige"


def steps(p):
    """Schrittfolge einer exportierten Vorlage (dict aus export._paper_detail)."""
    kind = initiation_kind(p["paper_type"])
    out = [{
        "typ": "initiierung", "label": p["paper_type"], "status": "belegt",
        "date": None, "source": "oparl-bonn", "source_object": p["source_object"],
        "note": "sonderweg" if p["paper_type"] in SONDER_TYPES else None,
        "actors": [o["actor"] for o in p["originators"]],
        "actors_status": "abgeleitet" if p["originators"] else None,
    }]
    if kind in ("verwaltung", "sonderweg"):
        out.append({"typ": "vorbereitung", "label": "Verwaltungsinterne Vorbereitung",
                    "status": "nicht_öffentlich", "date": None, "note": "vorbereitung"})
    out.append({"typ": "veroeffentlichung", "label": "Datum der Vorlage", "status": "belegt",
                "date": p["date"], "source": "oparl-bonn", "source_object": p["source_object"],
                "note": "datum"})
    if kind == "nichtoeffentlich":
        out.append({"typ": "beratung", "label": "Nichtöffentliche Beratung", "status": "nicht_öffentlich",
                    "date": None, "note": "nichtoeffentlich"})

    decided = False
    for s in p["process"]:
        linked = bool(s["start_date"] or s["result"])
        step = {
            "typ": "entscheidung" if s["authoritative"] else "beratung",
            "label": s["gremium"] or "Gremium unbekannt", "role": s["role"],
            "status": "belegt", "source": "oparl-bonn",
            "date": (s["start_date"] or "")[:10] or None,
            "date_status": "abgeleitet" if linked else "unklar",
            "date_source": "oparl-lite" if linked else None,
            "number": s["number"], "result": s["result"], "stand": s["status"],
            "note": None if linked else "ohne_sitzung",
        }
        if s["result"] and any(k in s["result"] for k in SCHLEIFE):
            step["schleife"] = True
        if s["authoritative"] and s["result"] and any(k in s["result"] for k in VOLLZUG):
            decided = True
        out.append(step)

    for sub in p["subordinated"]:
        out.append({"typ": "folgevorlage", "label": sub["paper_type"], "status": "belegt",
                    "date": sub.get("date"), "source": "oparl-bonn", "reference": sub["reference"],
                    "title": sub["name"]})
    if decided:
        out.append({"typ": "vollzug", "label": "Vollzug durch die Verwaltung", "status": "unklar",
                    "date": None, "note": "vollzug"})

    # Datierte Schritte nach Datum, undatierte an ihrer logischen Stelle
    head = [s for s in out if s["typ"] in ("initiierung", "vorbereitung")]
    tail = [s for s in out if s["typ"] == "vollzug"]
    mid = [s for s in out if s not in head and s not in tail]
    mid.sort(key=lambda s: (s["date"] is None, s["date"] or ""))
    return head + mid + tail


def stand(p):
    """Stand des Verfahrens: entschieden / in Beratung / offen / ohne Beratungsfolge."""
    s = p["process"]
    if not s:
        return "ohne Beratungsfolge"
    if any(x["authoritative"] and x["status"] == "beraten" for x in s):
        return "entschieden"
    return "in Beratung" if any(x["status"] == "beraten" for x in s) else "offen"


def path_key(p):
    """Weg einer Vorlage für die Aggregatdarstellung: Gremien mit Rolle, dann Ergebnis."""
    stations = [f"{s['gremium'] or '?'} ({s['role'] or '?'})" for s in p["process"]]
    final = next((s["result"] for s in reversed(p["process"]) if s["authoritative"] and s["result"]), None)
    return tuple(stations), final or stand(p)
