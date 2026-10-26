"""Themenseiten (thema/<name>/): Vorlagen und Verfahren eines Themas in Strängen, mit Prozessbild, Sitzungen und
Wegen zum Mitwirken. Die Beschreibung je Thema (Regeln, Bahnen, Texte) steht in pipeline/themenseiten/.

Die Zuordnung der Vorlagen zu den Strängen ist abgeleitet: feste Regeln aus Amt, Gremium, Titel und
Drucksachennummer, je Vorlage mit Grund. Keine Bewertung, keine Beträge, keine Zitate aus den Dokumenten.
Ausgabe: export/bonn/dossiers/<key>.json (export_all) und die statische Seite (seo-Schritt)."""
import csv
import json
import random
import re
import sqlite3
from dataclasses import dataclass, field
from datetime import date, timedelta
from html import escape
from urllib.parse import quote

from . import config, maske, process as proc

FRIST_TAGE = 21  # Anträge, Bürgeranträge und Einwohnerfragen spätestens 21 Tage vor der Sitzung (GeschO §§ 26, 27)
PUNKT_ARTEN = ("Beschlussvorlage", "Antrag", "Dringlichkeitsantrag")  # Punkte: Beschlüsse und Anträge


@dataclass(frozen=True)
class Zustaendig:
    """Zuständigkeit für eine Regel: federführendes Amt (Anfang der Bezeichnung), Stellen nur mit Wort im Titel,
    beratende Gremien."""
    aemter: tuple = ()
    stellen_mit_titel: dict = field(default_factory=dict)
    gremien: tuple = ()


@dataclass(frozen=True)
class Regel:
    """Eine Regel der Zuordnung. Reihenfolge der Prüfung: zuerst Stammnummern (unabhängig vom Zeitraum), dann
    nur Vorlagen ab Beginn des Zeitraums: Verfahren, deren Titel passt (ganzes Verfahren), danach die übrigen
    Regeln in ihrer Reihenfolge; die erste passende gilt.
    - stammnummer: Drucksache und ihre Folgevorlagen
    - verfahren_titel: ein Titel im Verfahren passt, das ganze Verfahren (Stammnummer) gehört zum Strang;
      mit nur_stammvorlage zählt nur der Titel der Stammvorlage (nicht z. B. ein einzelner Änderungsantrag)
    - titel: Wort im Titel; mit zustaendig oder thema zusätzlich dazu, sonst allein
    - zustaendig: Amt, Stelle oder Gremium; ohne Treffer im Titel gilt der Strang sonst
    - thema: Schlüssel der Themenzuordnung (topics.py, abgeleitet); wie zustaendig
    - bedingung: ein zweites Merkmal, das der Titel zusätzlich nennen muss (z. B. ein Wort für Schule)"""
    strang: str
    stammnummer: str = None
    verfahren_titel: re.Pattern = None
    nur_stammvorlage: bool = False
    titel: re.Pattern = None
    zustaendig: Zustaendig = None
    thema: str = None
    sonst: str = None
    bedingung: re.Pattern = None


@dataclass(frozen=True)
class Thema:
    """Beschreibung einer Themenseite (siehe pipeline/themenseiten/kultur.py)."""
    key: str
    pfad: str
    titel: str
    lead: str                 # mit {seit}
    seo_text: str             # mit {n}
    seit: str
    straenge: list            # (Schlüssel, Titel, Regel in Worten)
    regeln: list
    punkt_straenge: tuple
    bahnen: list              # (Schlüssel, Beschriftung) von oben nach unten; "plan" für die Phasen im Ganzen
    bahn_gremien: dict        # Bahn → Gremien (eigene Bahnen; sonst Bezirksvertretungen, Finanzausschuss, Rat, andere)
    sitzungen: tuple          # Gremien der nächsten Sitzungen (dazu je eine Sitzung jeder Bezirksvertretung)
    achse: tuple              # Zeitachse: Anfang, Ende, Knick, Anteil des Rückblicks
    bild_titel: str
    feed_text: str            # „zu …“
    hinweis: str
    pruefung_text: str
    nicht_gezeigt: list       # HTML
    eingeklappt: set = frozenset()
    sitzungen_je_gremium: int = 2
    terminplan: str = None    # Drucksache, aus der die Phasen stammen
    phasen: list = ()         # (Bahn, von, bis, Beschriftung, nicht öffentlich), geplant laut Terminplan
    phasen_text: str = ""
    fenster_text: str = ""
    schritte_titel: str = ""
    schritte: list = ()       # (Titel, Zeit, Text), selbst formuliert aus dem Terminplan
    vergleich: str = None
    vergleich_text: str = ""  # mit {ref} und {n}
    stichprobe_je_strang: dict = field(default_factory=dict)
    stichprobe_ohne: int = 0
    kandidat: re.Pattern = None  # Gegenprobe: Wörter im Titel nicht zugeordneter Vorlagen
    ausschluss: re.Pattern = None  # Titel, die zu keinem Strang gehören (vor allen Regeln)
    punkt_gremien: tuple = ()  # Punkte im Bild nur mit Beratung in diesen Gremien (leer: alle)
    nach_bezirk: frozenset = frozenset()  # Stränge, deren Vorlagen nach Stadtbezirk gegliedert erscheinen

    @property
    def stichprobe_pfad(self):
        return config.EXPORT / self.key / f"stichprobe_{self.key}.tsv"


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


def _verfahren(t, cache):
    """Stammnummer → (Strang, Grund) für Verfahren, die ein Titel seit Beginn des Zeitraums einem Strang zuweist."""
    regeln = [r for r in t.regeln if r.verfahren_titel]
    out = {}
    for p in sorted(cache.values(), key=lambda p: p["reference"]):
        if (p.get("date") or "") < t.seit:
            continue
        for r in regeln:
            if r.nur_stammvorlage and p["reference"] != _stamm(p["reference"]):
                continue
            m = r.verfahren_titel.search(p.get("name") or "")
            if m and _stamm(p["reference"]) not in out:
                out[_stamm(p["reference"])] = (r.strang, f"Verfahren {_stamm(p['reference'])}; Titel: „{_wort(m)}“")
    return out


def _zustaendig(z, p):
    name, amt = p.get("name") or "", p.get("amt") or ""
    gremien = sorted({s["gremium"] for s in p["process"] if s.get("gremium") in z.gremien})
    if amt.startswith(z.aemter) or (amt in z.stellen_mit_titel and z.stellen_mit_titel[amt].search(name)):
        return f"federführend: {amt}"
    if gremien:
        return "Beratung im " + " und in der ".join(gremien)
    return None


def _thema(key, p):
    from . import topics
    hit = next((x for x in p.get("themes") or [] if x.get("theme") == key), None)
    if not hit:
        return None
    label = dict(topics.THEMES).get(key, key)
    return f"Thema „{label}“ ({hit.get('evidence')})" if hit.get("evidence") else f"Thema „{label}“"


def zuordnen(t, p, verfahren=None):
    """(Strang, Grund) einer Vorlage oder None; jede Vorlage gehört zu höchstens einem Strang."""
    name = p.get("name") or ""
    if t.ausschluss and t.ausschluss.search(name):
        return None
    for r in t.regeln:
        if r.stammnummer and _stamm(p["reference"]) == r.stammnummer:
            return r.strang, f"Folgevorlage zu {r.stammnummer}" if p["reference"] != r.stammnummer else "Stammvorlage"
    if (p.get("date") or "") < t.seit:
        return None
    if _stamm(p["reference"]) in (verfahren or {}):
        return verfahren[_stamm(p["reference"])]
    for r in t.regeln:
        if r.stammnummer or r.verfahren_titel:
            continue
        mb = r.bedingung and r.bedingung.search(name)
        if r.bedingung and not mb:
            continue
        if r.zustaendig or r.thema:
            grund = _zustaendig(r.zustaendig, p) if r.zustaendig else _thema(r.thema, p)
            if not grund:
                continue
            m = r.titel and r.titel.search(name)
            if m:
                return r.strang, f"{grund}; Titel: „{_wort(m)}“"
            if r.titel is None:
                return r.strang, grund
            if r.sonst:
                return r.sonst, grund
            continue
        m = r.titel and r.titel.search(name)
        if m:
            woerter = [_wort(m)] + ([_wort(mb)] if mb and _wort(mb) != _wort(m) else [])
            return r.strang, "Titel: " + " und ".join(f"„{w}“" for w in woerter)
    return None


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


def bahn(t, gremium):
    g = gremium or ""
    for key, gremien in t.bahn_gremien.items():
        if g in gremien:
            return key
    if g.startswith("Bezirksvertretung"):
        return "bv"
    if g == "Ausschuss für Finanzen, Beteiligungen und Vergabe":
        return "finanz"
    if g in ("Hauptausschuss", "Rat"):
        return "rat"
    return "fach"


def _punkt(t, p, e, strang):
    """Lage eines Beschlusses oder Antrags im Prozessbild: letzte Beratung mit Ergebnis, sonst die nächste,
    sonst das erste Gremium der Beratungsfolge am Tag der Vorlage. Dazu die Angaben des Detailfelds
    (Strang mit Grund, Art, Amt, Beratungsfolge mit Ergebnis wörtlich aus der Quelle)."""
    lb, nb = e["letzte_beratung"], e["naechste_beratung"]
    if lb:
        gremium, datum = lb["gremium"], lb["date"] or e["date"]
    elif nb:
        gremium, datum = nb["gremium"], nb["date"]
    else:
        gremium, datum = next((s["gremium"] for s in p["process"] if s.get("gremium")), "Rat"), e["date"]
    art = "entschieden" if e["stand"] == "entschieden" else "offen" if e["stand"] in ("offen", "ohne Beratungsfolge") \
        else "beraten"
    beratungen = [{"gremium": s["gremium"], "date": s.get("start_date") and proc.local_day(s["start_date"]),
                   "result": s.get("result"), "cancelled": bool(s.get("cancelled"))}
                  for s in p["process"] if s.get("gremium")]
    return {"reference": e["reference"], "name": e["name"], "date": datum, "bahn": bahn(t, gremium), "gremium": gremium,
            "art": art, "stand": e["stand"], "gebiet": e["gebiet"], "web": e["web"], "strang": strang,
            "grund": e["grund"], "paper_type": e["paper_type"], "amt": e["amt"], "beratungen": beratungen}


def _frist(datum):
    return (date.fromisoformat(datum) - timedelta(days=FRIST_TAGE)).isoformat()


def bezirk(p):
    """Stadtbezirk einer Vorlage für die Gliederung (aus den Ortsbezügen, abgeleitet)."""
    bezirke = {x.get("stadtbezirk") for x in p.get("locations") or [] if x.get("stadtbezirk")}
    if len(bezirke) == 1:
        return bezirke.pop()
    return "mehrere Stadtbezirke" if bezirke else "ohne Ortsbezug"


def sitzung_im_thema(t, gremium):
    """Sitzungen der Themenseite: die Gremien des Themas und alle Bezirksvertretungen (Kalender, Liste)."""
    return gremium in t.sitzungen or gremium.startswith("Bezirksvertretung")


def daten(t, cache, home, meetings, today, meta):
    """Inhalt der Themenseite aus den Vorlagen des Exports (cache: id → Vorgang, home: id → Gebiet)."""
    straenge = {k: [] for k, _, _ in t.straenge}
    verfahren = _verfahren(t, cache)
    for pid, p in cache.items():
        hit = zuordnen(t, p, verfahren)
        if hit:
            eintrag = {**_eintrag(p, home.get(pid), today), "grund": hit[1], "_pid": pid}
            if hit[0] in t.nach_bezirk:
                eintrag["bezirk"] = bezirk(p)
            straenge[hit[0]].append(eintrag)
    im_bild = lambda p: not t.punkt_gremien or any(s.get("gremium") in t.punkt_gremien for s in p["process"])
    punkte = sorted((_punkt(t, cache[r["_pid"]], r, k) for k in t.punkt_straenge for r in straenge[k]
                     if r["paper_type"] in PUNKT_ARTEN and im_bild(cache[r["_pid"]])),
                    key=lambda x: (x["date"] or "", x["reference"]))
    for i, x in enumerate(punkte, 1):
        x["nr"] = i
    for rows in straenge.values():
        for r in rows:
            del r["_pid"]
    for rows in straenge.values():
        rows.sort(key=lambda r: (r["date"] or "", r["reference"]), reverse=True)
    termine, je = [], {}
    for m in meetings:
        bv = m["gremium"].startswith("Bezirksvertretung")
        if m["date"] >= today and not m["cancelled"] and sitzung_im_thema(t, m["gremium"]):
            if je.get(m["gremium"], 0) < (1 if bv else t.sitzungen_je_gremium):
                je[m["gremium"]] = je.get(m["gremium"], 0) + 1
                termine.append({**{k: m[k] for k in ("date", "time", "gremium", "web", "source_object")},
                                "bahn": bahn(t, m["gremium"]), "frist": _frist(m["date"])})
    by_ref = {p["reference"]: (pid, p) for pid, p in cache.items()}
    plan = t.terminplan and by_ref.get(t.terminplan)
    vergleich = t.vergleich and by_ref.get(t.vergleich)
    return {
        "meta": {**meta, "seit": t.seit, "hinweis": t.hinweis},
        "straenge": [{"key": k, "titel": ti, "regel": r, "eingeklappt": k in t.eingeklappt, "vorlagen": straenge[k]}
                     for k, ti, r in t.straenge],
        "heute": today,
        "sitzungen": termine,
        "punkte": punkte,
        "phasen": [{"bahn": b, "von": v, "bis": bis, "text": x, "intern": i} for b, v, bis, x, i in t.phasen],
        "haushalt_schritte": [{"titel": ti, "zeit": z, "text": x} for ti, z, x in t.schritte],
        "terminplan": plan and {"reference": t.terminplan, "web": plan[1].get("web"), "gebiet": home.get(plan[0])},
        "vergleich": vergleich and {
            "reference": t.vergleich, "name": vergleich[1].get("name"), "web": vergleich[1].get("web"),
            "gebiet": home.get(vergleich[0]),
            "vorlagen": sum(1 for r in by_ref if _stamm(r) == t.vergleich)},
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


def _tabelle(rows):
    return f"""    <table>
      <thead><tr><th scope="col">Datum</th><th scope="col">Drucksache</th><th scope="col">Titel</th><th scope="col">Stand</th></tr></thead>
      <tbody>
{rows}
      </tbody>
    </table>"""


def _nach_bezirk(root, vorlagen):
    """Vorlagen je Stadtbezirk, jeder Abschnitt eingeklappt; zuletzt mehrere Stadtbezirke und ohne Ortsbezug."""
    gruppen = {}
    for r in vorlagen:
        gruppen.setdefault(r["bezirk"], []).append(r)
    folge = sorted(gruppen, key=lambda b: (b in ("mehrere Stadtbezirke", "ohne Ortsbezug"), b == "ohne Ortsbezug", b))
    teile = [f"    <details>\n      <summary>{escape(b)} ({len(gruppen[b])})</summary>\n"
             + _tabelle("\n".join(_row(root, r) for r in gruppen[b])) + "\n    </details>" for b in folge]
    return "    <p class=\"meta\">Nach Stadtbezirk (aus den Ortsbezügen, abgeleitet).</p>\n" + "\n".join(teile)


def _schritte(t, d, root):
    """Abschnitt zum Weg eines Verfahrens laut Terminplan (nur mit Schritten)."""
    if not d["haushalt_schritte"]:
        return ""
    schritte = "\n".join(f'      <li><strong>{escape(s["titel"])}</strong> ({escape(s["zeit"])}): {escape(s["text"])}</li>'
                         for s in d["haushalt_schritte"])
    tp = d.get("terminplan")
    tp_link = (f'Mitteilungsvorlage {_ref(root, tp)}' + (f' (<a href="{escape(tp["web"])}">Original</a>)' if tp.get("web") else "")
               if tp else f"Mitteilungsvorlage {t.terminplan}")
    return f"""    <h2>{escape(t.schritte_titel)}</h2>
    <p>Zusammengefasst aus der {tp_link} (abgeleitet, keine Zitate). Die Zeitangaben sind geplant; Abweichungen sind möglich.</p>
    <ol>
{schritte}
    </ol>
"""


def body(t, d, root):
    from . import prozessbild
    vg = d.get("vergleich")
    vergleich = f'    <p>{t.vergleich_text.format(ref=_ref(root, vg), n=vg["vorlagen"])}</p>\n' if vg else ""
    sitzungen = "\n".join(
        f'      <li>{_date(m["date"])}{(", " + m["time"] + " Uhr") if m.get("time") else ""}: {escape(m["gremium"])}'
        + (f' (<a href="{escape(m["web"])}">Tagesordnung</a>)' if m.get("web") else "")
        + (f' <small>– Frist für Anträge und Fragen: {_date(m["frist"])}</small>' if m.get("frist", "") >= d["heute"]
           else "") + "</li>"
        for m in d["sitzungen"]) or "      <li>Keine Sitzungen eingetragen.</li>"
    straenge = []
    for s in d["straenge"]:
        rows = "\n".join(_row(root, r) for r in s["vorlagen"])
        tabelle = _tabelle(rows) if rows else "    <p>Keine Vorlagen.</p>"
        if rows and any("bezirk" in r for r in s["vorlagen"]):
            tabelle = _nach_bezirk(root, s["vorlagen"])
        elif rows and s.get("eingeklappt"):
            tabelle = (f"    <details>\n      <summary>Alle {len(s['vorlagen'])} Vorlagen anzeigen</summary>\n"
                       f"{tabelle}\n    </details>")
        straenge.append(f"""    <h3 id="{s['key']}">{escape(s['titel'])} ({len(s['vorlagen'])})</h3>
    <p class="meta">Regel (abgeleitet): {escape(s['regel'].rstrip('.'))}.</p>
""" + tabelle)
    inhalt = " · ".join(f'<a href="#{s["key"]}">{escape(s["titel"])}</a>' for s in d["straenge"])
    nicht = "\n".join(f"      <li>{x}</li>" for x in t.nicht_gezeigt)
    return f"""    <h1>{escape(t.titel)}</h1>
    <p class="lead">{escape(t.lead.format(seit=_date(d["meta"]["seit"])))}</p>
    <p class="meta">Die Seite beschreibt Verfahren; sie bewertet keine Entscheidungen. Maßgeblich sind die Originale im Ratsinformationssystem.</p>
{prozessbild.abschnitt(t, d, root)}
{_schritte(t, d, root)}{vergleich}    <h2 id="sitzungen">Nächste Sitzungen</h2>
    <p>Sitzungen sind in der Regel öffentlich. Die Tagesordnung erscheint etwa zwei Wochen vorher. Die Frist (21 Tage vorher, GeschO §§ 26, 27) ist berechnet.</p>
    <ul>
{sitzungen}
    </ul>
    <h2>Mitwirken</h2>
    <ul>
      <li><strong>Sitzungen besuchen:</strong> Rat und Ausschüsse tagen in der Regel öffentlich (§ 48 GO NRW).</li>
      <li><strong>Einwohnerfragestunde:</strong> In den Bezirksvertretungen können Einwohnerinnen und Einwohner bis zu zwei Fragen stellen, eingereicht spätestens 21 Tage vor der Sitzung (GeschO § 26).</li>
      <li><strong>Anregungen und Beschwerden (§ 24 GO NRW):</strong> Jede Person kann sich schriftlich an den Rat oder eine Bezirksvertretung wenden. <a href="https://www.bonn.de/vv/produkte/buergerantrag-anregungen-und-beschwerden-gemaess-24-gemeindeordnung-nrw.php">Bürgerantrag bei der Stadt Bonn</a></li>
      <li><a href="{root}?mitmachen=1">Alle Wege, Fristen und Sitzungen je Stadtbezirk auf der Karte</a></li>
    </ul>
    <h2>Vorlagen nach Strang</h2>
    <p>{inhalt}</p>
    <p class="meta">Jede Vorlage steht in höchstens einem Strang. Die Zuordnung folgt festen Regeln (Amt, Gremium, Wörter im Titel, Drucksachennummer); der Grund steht je Vorlage dabei. {t.pruefung_text} Der Stand ist aus der Beratungsfolge abgeleitet, Ergebnisse stehen wörtlich wie in der Quelle.</p>
{chr(10).join(straenge)}
    <h2>Was diese Seite nicht zeigt</h2>
    <ul>
{nicht}
    </ul>
    <p class="meta">Quelle: OParl-API der Stadt Bonn (CC0), Sitzungen und Ergebnisse aus OParl-Lite (CC BY 4.0). Die Daten als JSON: <a href="{root}data/export/bonn/dossiers/{t.key}.json">{t.key}.json</a>.</p>"""


def write(t, site, site_url, page):
    """Schreibt die Themenseite nach site; gibt die Pfade relativ zu site_url zurück (für die Sitemap)."""
    src = site / "data" / "export" / "bonn" / "dossiers" / f"{t.key}.json"
    if not src.exists():
        return []
    d = json.loads(src.read_text(encoding="utf-8"))
    n = sum(len(s["vorlagen"]) for s in d["straenge"])
    out = site / t.pfad / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    titel = f"{t.titel} – RIS-Karte Bonn"
    text = t.seo_text.format(n=n)
    head = ""
    png = site / "data" / "export" / "bonn" / "dossiers" / f"{t.key}-zeitleiste.png"
    if png.exists():  # Vorschaubild beim Teilen: die Zeitleiste
        bild = f"{site_url}data/export/bonn/dossiers/{t.key}-zeitleiste.png"
        head = "".join(f'\n  <meta property="{k}" content="{escape(v)}">' for k, v in (
            ("og:type", "article"), ("og:site_name", "RIS-Karte Bonn"), ("og:locale", "de_DE"), ("og:title", titel),
            ("og:description", text), ("og:url", site_url + t.pfad), ("og:image", bild),
            ("og:image:alt", t.bild_titel)))
        head += '\n  <meta name="twitter:card" content="summary_large_image">'
    root = "../" * t.pfad.rstrip("/").count("/") + "../"
    out.write_text(page(site_url, t.pfad, titel, text, body(t, d, root), root, head), encoding="utf-8")
    print(f"Themenseite {t.titel}: {n} Vorlagen")
    return [t.pfad]


UEBERSICHT = "thema/"


def uebersicht(themen, site, site_url, page):
    """Übersicht thema/ über die geschriebenen Themenseiten (Titel, Zahl der Vorlagen, Beschreibung); gibt den Pfad
    für die Sitemap zurück, ohne Themenseiten keinen."""
    eintraege = []
    for t in themen:
        src = site / "data" / "export" / "bonn" / "dossiers" / f"{t.key}.json"
        if not (site / t.pfad / "index.html").exists() or not src.exists():
            continue
        d = json.loads(src.read_text(encoding="utf-8"))
        n = sum(len(s["vorlagen"]) for s in d["straenge"])
        straenge = ", ".join(s["titel"] for s in d["straenge"])
        eintraege.append(f'      <li><a href="../{t.pfad}"><strong>{escape(t.titel)}</strong></a> ({n} Vorlagen)<br>'
                         f'<small>Stränge: {escape(straenge)}</small></li>')
    if not eintraege:
        return []
    body = f"""    <h1>Themen</h1>
    <p class="lead">Themenseiten ordnen Vorlagen aus dem Ratsinformationssystem der Stadt Bonn nach Strängen und zeigen, wo ein Verfahren steht, was entschieden ist und wo man sich einbringen kann.</p>
    <p class="meta">Die Zuordnung folgt festen Regeln je Thema (abgeleitet, je Vorlage mit Grund) und wurde an einer Stichprobe von Hand geprüft. Maßgeblich sind die Originale im Ratsinformationssystem.</p>
    <ul>
{chr(10).join(eintraege)}
    </ul>
    <p><a href="../">Zur Karte</a></p>"""
    out = site / UEBERSICHT / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page(site_url, UEBERSICHT, "Themen – RIS-Karte Bonn",
                        "Themenseiten der RIS-Karte Bonn: Vorlagen und Verfahren je Thema mit Prozessbild, Sitzungen und "
                        "Wegen zum Mitwirken.", body, "../"), encoding="utf-8")
    return [UEBERSICHT]


# --- Stichprobe zur Prüfung von Hand --------------------------------------------------------------------

def entwurf(t, db_path=None):
    """Daten eines Themas direkt aus der Datenbank (für den Prüfbogen eines Themas, das noch nicht in ALLE steht
    und deshalb nicht exportiert wird; ohne Gebiete und Sitzungen)."""
    from .export import _paper_detail
    db = sqlite3.connect(db_path or config.DB)
    db.row_factory = sqlite3.Row
    cache = {pid: _paper_detail(db, pid) for (pid,) in db.execute("SELECT id FROM paper WHERE date >= ?", (t.seit,))}
    for r in t.regeln:  # Stammnummern gelten auch vor Beginn des Zeitraums
        if r.stammnummer:
            for (pid,) in db.execute("SELECT id FROM paper WHERE reference = ? OR reference LIKE ? OR reference LIKE ?",
                                     (r.stammnummer, f"{r.stammnummer}-%", f"{r.stammnummer} %")):
                cache.setdefault(pid, _paper_detail(db, pid))
    db.close()
    return daten(t, cache, {}, [], date.today().isoformat(), {})


def stichprobe(t, src=None, out=None, seed=2026, db_path=None):
    """Prüfbogen: je Strang einige zugeordnete Vorlagen (passt die Zuordnung?) und nicht zugeordnete Vorlagen mit
    passenden Wörtern im Titel (fehlen sie?). Wird nur einmal gezogen; eine vorhandene Datei bleibt unverändert."""
    out = out or t.stichprobe_pfad
    if out.exists():
        print(f"Stichprobe vorhanden, unverändert: {out}")
        return
    src = src or config.EXPORT / "bonn" / "dossiers" / f"{t.key}.json"
    d = json.loads(src.read_text(encoding="utf-8")) if src.exists() else entwurf(t, db_path)
    rnd = random.Random(seed)
    rows = []
    for s in d["straenge"]:
        for r in rnd.sample(s["vorlagen"], min(t.stichprobe_je_strang.get(s["key"], 0), len(s["vorlagen"]))):
            rows.append([r["reference"], r["date"], r["paper_type"], r["name"], r["web"] or "", s["titel"], r["grund"]])
    drin = {r["reference"] for s in d["straenge"] for r in s["vorlagen"]}
    db = sqlite3.connect(db_path or config.DB)
    m = maske.aus_db(db)
    ohne = [list(r) for r in db.execute("SELECT reference, date, paper_type, name, web FROM paper WHERE date >= ? "
                                        "ORDER BY reference", (t.seit,))
            if t.kandidat and r[0] not in drin and t.kandidat.search(r[3] or "")
            and not (t.ausschluss and t.ausschluss.search(r[3] or ""))]  # Ausgeschlossenes ist entschieden
    je_verfahren = {}  # eine Vorlage je Verfahren (Stammnummer), damit die Gegenprobe breiter streut
    for r in ohne:
        je_verfahren.setdefault(_stamm(r[0]), r)
    for r in rnd.sample(sorted(je_verfahren.values()), min(t.stichprobe_ohne, len(je_verfahren))):
        r[3] = m(r[3], r[0])
        rows.append([*r[:4], r[4] or "", "nicht zugeordnet", f"Titel: „{_wort(t.kandidat.search(r[3]))}“ (Gegenprobe)"])
    db.close()
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["nr", "drucksache", "datum", "vorlagenart", "titel", "link", "strang (laut Regel)", "grund",
                    "urteil (passend/teilweise/unpassend; bei „nicht zugeordnet“: fehlt/richtig ausgelassen)",
                    "richtiger strang (falls abweichend)", "anmerkung"])
        for i, r in enumerate(rows, 1):
            w.writerow([i, *r, "", "", ""])
    print(f"Stichprobe {t.titel}: {len(rows)} Vorlagen ({len(je_verfahren)} Verfahren ohne Zuordnung) → {out}")
