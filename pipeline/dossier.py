"""Themenseite „Kultur und Haushalt“ (thema/kultur-und-haushalt/): Vorlagen und Verfahren, die mit dem Haushalt
und der Kulturförderung zusammenhängen. Anlass und Prüfung: kultur/phase0/BERICHT.md.

Die Zuordnung der Vorlagen zu den Strängen ist abgeleitet: feste Regeln aus Amt, Gremium, Titel und
Drucksachennummer (STRAENGE), je Vorlage mit Grund. Keine Bewertung, keine Beträge, keine Zitate aus den
Dokumenten; der Weg des Haushalts ist aus Mitteilungsvorlage 261064 zusammengefasst.
Ausgabe: export/bonn/dossiers/kultur.json (export_all) und die statische Seite (seo-Schritt)."""
import json
import re
from html import escape
from urllib.parse import quote

from . import process as proc

SEIT = "2025-11-01"  # Beginn der 12. Wahlperiode (legislative_terms)
PFAD = "thema/kultur-und-haushalt/"
KULTUR_AEMTER = ("41 ", "42 ", "45 ", "46 ", "48 ")  # Kulturamt, Stadtbibliothek, Kunstmuseum, Theater, Beethovenorchester
KULTUR_GREMIEN = ("Kulturausschuss", "Kulturkommission")
HAUSHALT = re.compile(r"Haushaltssatzung|Haushaltssperre|haushaltswirtschaftlich|Haushaltskonsolidierung|Konsolidierung|"
                      r"Haushaltssicherung|Eckwert|Haushaltsplan|Doppelhaushalt|Nachtragshaushalt", re.I)
FINANZEN = re.compile(r"Förder|Zuschuss|Zuschüsse|Einspar|Kürzung|Gebühr|Entgelt|Wirtschaftsplan|Festbetrag|"
                      r"Gleichbehandlung|Haushalt|Finanz|Drittmittel|Budget|Kosten", re.I)
BUEHNEN = "260127"     # Stammnummer „Zukunft der Bonner Bühnen“
VERGLEICH = "240986"   # Haushaltssatzung 2025/2026 (Vergleich: Zahl der Vorlagen im Verfahren)
TERMINPLAN = "261064"  # Rahmenterminplan Haushalt 2027/2028 (Grundlage der Schritte)
SITZUNGEN = ("Kulturausschuss", "Kulturkommission", "Ausschuss für Finanzen, Beteiligungen und Vergabe",
             "Hauptausschuss", "Rat")
SITZUNGEN_JE_GREMIUM = 2

STRAENGE = [
    ("haushalt", "Haushalt und Konsolidierung",
     "Titel nennt Haushaltssatzung, Haushaltssperre, haushaltswirtschaftliche Lage, Konsolidierung, Eckwerte o. Ä."),
    ("buehnen", "Zukunft der Bonner Bühnen", f"Drucksache {BUEHNEN} und ihre Folgevorlagen"),
    ("kultur_finanzen", "Kulturförderung, Zuschüsse, Gebühren",
     "Kulturamt, Stadtbibliothek, Kunstmuseum, Theater oder Beethovenorchester federführend oder Beratung im "
     "Kulturausschuss bzw. in der Kulturkommission, und der Titel nennt Förderung, Zuschüsse, Einsparung, Gebühren, "
     "Entgelte, Wirtschaftsplan, Finanzierung o. Ä."),
    ("kultur_weitere", "Weitere Vorlagen aus Kulturamt und Kulturausschuss",
     "wie zuvor, ohne Bezug zu Geld im Titel"),
]

# Weg des Haushalts 2027/2028: zusammengefasst aus Mitteilungsvorlage 261064 und ihrer Anlage (Terminplan),
# selbst formuliert, ohne Zitate (Rahmen der Stadt Bonn vom 19.10.2026)
SCHRITTE = [
    ("Aufstellung in der Verwaltung", "Frühjahr und Sommer 2026",
     "Die Ämter melden ihren Bedarf im Rahmen von Eckwerten je Amt und Dezernat; Mehrbedarf ist innerhalb des "
     "Dezernats auszugleichen. Der Verwaltungsvorstand bespricht Härtefälle. Dieser Teil ist nicht öffentlich."),
    ("Einbringung des Entwurfs", "Herbst 2026",
     "Die Verwaltung legt dem Rat den Entwurf des Haushaltsplans vor; die Mitglieder der Ausschüsse erhalten die Unterlagen."),
    ("Beratung in den Fachausschüssen und Bezirksvertretungen", "Oktober und November 2026",
     "Jedes Fachgremium berät den Entwurf einmal, für die Kultur der Kulturausschuss. Fraktionen können "
     "Änderungsanträge stellen."),
    ("Ausschuss für Finanzen, Beteiligungen und Vergabe", "November 2026",
     "Er tagt nach den Fachgremien und bereitet den Beschluss des Rates vor."),
    ("Beschluss im Rat", "Dezember 2026",
     "Etwa zwei Wochen nach dem Finanzausschuss beschließt der Rat die Haushaltssatzung."),
    ("Kommunalaufsicht", "Anfang 2027",
     "Die Satzung geht an die Bezirksregierung Köln; die Genehmigung erwartet die Verwaltung im ersten Quartal 2027."),
]


def _stamm(ref):
    return re.split(r"[- ]", ref or "")[0]


def _wort(m):
    """Ganzes Wort um einen Treffer, z. B. „Förderung“ statt „Förder“."""
    text, a, b = m.string, m.start(), m.end()
    while a and (text[a - 1].isalnum() or text[a - 1] == "-"):
        a -= 1
    while b < len(text) and (text[b].isalnum() or text[b] == "-"):
        b += 1
    return text[a:b].strip("-")


def _strang(p):
    """(Strang, Grund) einer Vorlage oder None; jede Vorlage gehört zu höchstens einem Strang."""
    name, amt = p.get("name") or "", p.get("amt") or ""
    if _stamm(p["reference"]) == BUEHNEN:
        return "buehnen", f"Folgevorlage zu {BUEHNEN}" if p["reference"] != BUEHNEN else "Stammvorlage"
    if (p.get("date") or "") < SEIT:
        return None
    m = HAUSHALT.search(name)
    if m:
        return "haushalt", f"Titel: „{_wort(m)}“"
    gremien = sorted({s["gremium"] for s in p["process"] if s.get("gremium") in KULTUR_GREMIEN})
    if amt.startswith(KULTUR_AEMTER):
        grund = f"federführend: {amt}"
    elif gremien:
        grund = "Beratung im " + " und in der ".join(gremien)
    else:
        return None
    m = FINANZEN.search(name)
    return ("kultur_finanzen", f"{grund}; Titel: „{_wort(m)}“") if m else ("kultur_weitere", grund)


def _eintrag(p, home, today):
    beraten = [s for s in p["process"] if s.get("result")]
    naechste = next((s for s in p["process"] if not s.get("result") and not s.get("cancelled") and s.get("start_date")
                     and proc.local_day(s["start_date"]) >= today), None)
    last = beraten[-1] if beraten else None
    return {
        "reference": p["reference"], "date": p.get("date"), "paper_type": p.get("paper_type"), "name": p.get("name"),
        "amt": p.get("amt"), "stand": p.get("stand"), "web": p.get("web"), "gebiet": home,
        "letzte_beratung": last and {"gremium": last["gremium"], "date": proc.local_day(last["start_date"]),
                                     "result": last["result"]},
        "naechste_beratung": naechste and {"gremium": naechste["gremium"],
                                           "date": proc.local_day(naechste["start_date"])},
    }


def daten(cache, home, meetings, today, meta):
    """Inhalt der Themenseite aus den Vorlagen des Exports (cache: id → Vorgang, home: id → Gebiet)."""
    straenge = {k: [] for k, _, _ in STRAENGE}
    for pid, p in cache.items():
        hit = _strang(p)
        if hit:
            straenge[hit[0]].append({**_eintrag(p, home.get(pid), today), "grund": hit[1]})
    for rows in straenge.values():
        rows.sort(key=lambda r: (r["date"] or "", r["reference"]), reverse=True)
    termine, je = [], {}
    for m in meetings:
        if m["date"] >= today and not m["cancelled"] and m["gremium"] in SITZUNGEN:
            if je.get(m["gremium"], 0) < SITZUNGEN_JE_GREMIUM:
                je[m["gremium"]] = je.get(m["gremium"], 0) + 1
                termine.append({k: m[k] for k in ("date", "time", "gremium", "web", "source_object")})
    by_ref = {p["reference"]: (pid, p) for pid, p in cache.items()}
    plan = by_ref.get(TERMINPLAN)
    vergleich = by_ref.get(VERGLEICH)
    return {
        "meta": {**meta, "seit": SEIT, "hinweis": "Zuordnung zu den Strängen abgeleitet (feste Regeln, je Vorlage "
                 "mit Grund); Schritte des Haushalts aus Drucksache 261064 zusammengefasst, keine Zitate"},
        "straenge": [{"key": k, "titel": t, "regel": r, "vorlagen": straenge[k]} for k, t, r in STRAENGE],
        "sitzungen": termine,
        "haushalt_schritte": [{"titel": t, "zeit": z, "text": x} for t, z, x in SCHRITTE],
        "terminplan": plan and {"reference": TERMINPLAN, "web": plan[1].get("web"), "gebiet": home.get(plan[0])},
        "vergleich": vergleich and {
            "reference": VERGLEICH, "name": vergleich[1].get("name"), "web": vergleich[1].get("web"),
            "gebiet": home.get(vergleich[0]),
            "vorlagen": sum(1 for r in by_ref if _stamm(r) == VERGLEICH)},
    }


# --- Seite --------------------------------------------------------------------------------------------

def _date(iso):
    return f"{iso[8:10]}.{iso[5:7]}.{iso[:4]}" if iso and len(iso) >= 10 else "–"


def _map(root, gebiet, ref):
    return f"{root}?gebiet={quote(gebiet, safe=':')}#{quote(ref)}" if gebiet else None


def _ref(root, r):
    url = _map(root, r.get("gebiet"), r["reference"])
    return f'<a href="{escape(url)}">{escape(r["reference"])}</a>' if url else escape(r["reference"])


def _row(root, r):
    lb, nb = r.get("letzte_beratung"), r.get("naechste_beratung")
    verlauf = []
    if lb:
        verlauf.append(f'{escape(lb["gremium"] or "")} {_date(lb["date"])}: {escape(lb["result"])}')
    if nb:
        verlauf.append(f'als Nächstes: {escape(nb["gremium"] or "")} am {_date(nb["date"])}')
    return (f'      <tr><td>{_date(r["date"])}</td><td>{_ref(root, r)}</td>'
            f'<td>{escape(r["name"] or "")}<br><small>{escape(r["paper_type"] or "")}'
            + (f' · <a href="{escape(r["web"])}">Original</a>' if r.get("web") else "")
            + f' · Grund: {escape(r["grund"])}</small></td>'
            f'<td>{escape(r["stand"] or "")}' + (f'<br><small>{"<br>".join(verlauf)}</small>' if verlauf else "")
            + "</td></tr>")


def body(d, root):
    schritte = "\n".join(f'      <li><strong>{escape(s["titel"])}</strong> ({escape(s["zeit"])}): {escape(s["text"])}</li>'
                         for s in d["haushalt_schritte"])
    tp = d.get("terminplan")
    tp_link = (f'Mitteilungsvorlage {_ref(root, tp)}' + (f' (<a href="{escape(tp["web"])}">Original</a>)' if tp.get("web") else "")
               if tp else f"Mitteilungsvorlage {TERMINPLAN}")
    vg = d.get("vergleich")
    vergleich = (f'    <p>Zum Vergleich: Zum Doppelhaushalt 2025/2026 ({_ref(root, vg)}) gehören im Ratsinformationssystem '
                 f'{vg["vorlagen"]} Vorlagen, vor allem Änderungsanträge und Stellungnahmen der Verwaltung.</p>\n') if vg else ""
    sitzungen = "\n".join(
        f'      <li>{_date(m["date"])}{(", " + m["time"] + " Uhr") if m.get("time") else ""}: {escape(m["gremium"])}'
        + (f' (<a href="{escape(m["web"])}">Tagesordnung</a>)' if m.get("web") else "") + "</li>"
        for m in d["sitzungen"]) or "      <li>Keine Sitzungen eingetragen.</li>"
    straenge = []
    for s in d["straenge"]:
        rows = "\n".join(_row(root, r) for r in s["vorlagen"])
        straenge.append(f"""    <h3 id="{s['key']}">{escape(s['titel'])} ({len(s['vorlagen'])})</h3>
    <p class="meta">Regel (abgeleitet): {escape(s['regel'].rstrip('.'))}.</p>
""" + (f"""    <table>
      <thead><tr><th scope="col">Datum</th><th scope="col">Drucksache</th><th scope="col">Titel</th><th scope="col">Stand</th></tr></thead>
      <tbody>
{rows}
      </tbody>
    </table>""" if rows else "    <p>Keine Vorlagen.</p>"))
    inhalt = " · ".join(f'<a href="#{s["key"]}">{escape(s["titel"])}</a>' for s in d["straenge"])
    return f"""    <h1>Kultur und Haushalt</h1>
    <p class="lead">Welche Vorlagen und Verfahren hängen mit dem Haushalt der Stadt Bonn und der Kulturförderung zusammen? Diese Seite ordnet Vorlagen aus dem Ratsinformationssystem seit Beginn der Wahlperiode ({_date(d["meta"]["seit"])}) und zeigt, wann und wo darüber beraten wird.</p>
    <p class="meta">Die Seite beschreibt Verfahren; sie bewertet keine Entscheidungen. Maßgeblich sind die Originale im Ratsinformationssystem.</p>
    <h2>So entsteht der Haushalt 2027/2028</h2>
    <p>Zusammengefasst aus der {tp_link} (abgeleitet, keine Zitate). Die Zeitangaben sind geplant; Abweichungen sind möglich.</p>
    <ol>
{schritte}
    </ol>
{vergleich}    <h2>Nächste Sitzungen</h2>
    <p>Sitzungen sind in der Regel öffentlich. Die Tagesordnung erscheint etwa zwei Wochen vorher.</p>
    <ul>
{sitzungen}
    </ul>
    <h2>Mitwirken</h2>
    <ul>
      <li><strong>Sitzungen besuchen:</strong> Rat und Ausschüsse tagen in der Regel öffentlich (§ 48 GO NRW).</li>
      <li><strong>Einwohnerfragestunde:</strong> In Sitzungen können Einwohnerinnen und Einwohner Fragen stellen; Einzelheiten regelt die Geschäftsordnung des Rates.</li>
      <li><strong>Anregungen und Beschwerden (§ 24 GO NRW):</strong> Jede Person kann sich schriftlich an den Rat oder eine Bezirksvertretung wenden. <a href="https://www.bonn.de/vv/produkte/buergerantrag-anregungen-und-beschwerden-gemaess-24-gemeindeordnung-nrw.php">Bürgerantrag bei der Stadt Bonn</a></li>
      <li><a href="{root}?mitmachen=1">Alle Wege, Fristen und Sitzungen je Stadtbezirk auf der Karte</a></li>
    </ul>
    <h2>Vorlagen nach Strang</h2>
    <p>{inhalt}</p>
    <p class="meta">Jede Vorlage steht in höchstens einem Strang. Die Zuordnung folgt festen Regeln (Amt, Gremium, Wörter im Titel, Drucksachennummer) und ist nicht von Hand geprüft; der Grund steht je Vorlage dabei. Der Stand ist aus der Beratungsfolge abgeleitet, Ergebnisse stehen wörtlich wie in der Quelle.</p>
{chr(10).join(straenge)}
    <h2>Was diese Seite nicht zeigt</h2>
    <ul>
      <li><strong>Beträge:</strong> Zahlen je Einrichtung stehen in den Dokumenten der Vorlagen und im Haushaltsplan der Stadt (Produktbereich 1.04 Kultur und Wissenschaft, auf bonn.de), nicht in den Daten des Ratsinformationssystems. Die Seite übernimmt keine Beträge.</li>
      <li><strong>Vorbereitung in der Verwaltung:</strong> Eckwerte, Aufgabenkritik und Beratungen des Verwaltungsvorstands sind nicht öffentlich.</li>
      <li><strong>Nichtöffentliche Beratungen</strong> und Vorlagen, deren Titel keines der Merkmale nennt, fehlen.</li>
    </ul>
    <p class="meta">Quelle: OParl-API der Stadt Bonn (CC0), Sitzungen und Ergebnisse aus OParl-Lite (CC BY 4.0). Die Daten als JSON: <a href="{root}data/export/bonn/dossiers/kultur.json">kultur.json</a>.</p>"""


def write(site, site_url, page):
    """Schreibt die Themenseite nach site; gibt die Pfade relativ zu site_url zurück (für die Sitemap)."""
    src = site / "data" / "export" / "bonn" / "dossiers" / "kultur.json"
    if not src.exists():
        return []
    d = json.loads(src.read_text(encoding="utf-8"))
    n = sum(len(s["vorlagen"]) for s in d["straenge"])
    out = site / PFAD / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page(site_url, PFAD, "Kultur und Haushalt – RIS-Karte Bonn",
                        f"Haushalt 2027/2028 und Kulturförderung in Bonn: {n} Vorlagen aus dem Ratsinformationssystem "
                        "in vier Strängen, der Weg des Haushalts und die nächsten Sitzungen.",
                        body(d, "../../"), "../../"), encoding="utf-8")
    print(f"Themenseite Kultur und Haushalt: {n} Vorlagen")
    return [PFAD]
