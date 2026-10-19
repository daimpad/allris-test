"""Soll-Modell der Prozessebene: Verfahren nach Regelwerk und Abgleich mit den Beratungen (Ist).

Übernommen aus „Bonn entscheidet“ (anster2025/bonn-entscheidet, Commit 26641f7, MIT): Verfahrensmodell
(data/soll/verfahren.json), Zuständigkeitsordnung (data/soll/zustaendigkeitsordnung.json) und die Zuordnungsregeln
aus einordnung.py (assign). Eigene Ergänzungen und Korrekturen mit Belegen: data/soll/ergaenzungen.json.
Ein Vorgang umfasst alle Vorlagen einer Stammnummer (Drucksache ohne Zusatz „-NN XX“). Abweichungen zwischen
Soll und Ist sind Befunde, keine Bewertung."""
import collections
import copy
import csv
import json
import re
import sqlite3

from . import config

SOLL = config.ROOT / "data" / "soll"
SIDE = ("Stellungnahme der Verwaltung", "Änderungsantrag")
BAHN = {"Bezirksvertretungen": "bv", "Ratsgremien": "aus", "Rat": "rat"}  # Gremienart (OParl classification) → Bahn
BAULEIT_RE = re.compile(r"Bebauungsplan|Satzungsbeschluss|Aufstellungsbeschluss|Offenlage|"
                        r"Flächennutzungsplan|frühzeitige[nr]? (Öffentlichkeits)?[Bb]eteiligung", re.I)
BAULEIT_SICHER = re.compile(r"Bebauungsplan|Flächennutzungsplan(änderung)?\b.*(Aufstellung|"
                            r"Offenlage|Satzung|Beteiligung|Änderung)", re.I)
AUDIT = ["stammnummer", "jahr", "typ", "verfahren", "sicherheit", "grund", "dokumente", "ist_bahnen",
         "soll_bahnen", "passung", "abweichung"]


class Modell:
    """Verfahren mit Schritten (übernommene und eigene, `eigen: true`), Zuständigkeitsordnung, Korrekturen."""

    def __init__(self, base=SOLL):
        load = lambda n: json.loads((base / n).read_text(encoding="utf-8"))
        self.quelle, self.zusto, self.extra = load("verfahren.json"), load("zustaendigkeitsordnung.json"), load("ergaenzungen.json")
        self.quelle, self.zusto = copy.deepcopy(self.quelle), copy.deepcopy(self.zusto)
        self.korrigiert = [self._korrigiere(k) for k in self.extra["korrekturen"]]
        self.verfahren = {v["id"]: v for v in self.quelle["verfahren"]}
        for v in self.quelle["einordnung_extra"]["verfahren"]:  # Mitteilung, nichtöffentlich: in jedem Gremium möglich
            self.verfahren[v["id"]] = dict(v, jedes_gremium=True)
        for vid, steps in self.extra["zusaetzliche_schritte"].items():
            self.verfahren[vid]["schritte"] = self.verfahren[vid]["schritte"] + [dict(s, eigen=True) for s in steps]
        self.ohne_soll = self.extra["ohne_soll"]

    def _korrigiere(self, k):
        if k["datei"] == "zustaendigkeitsordnung.json":
            a = next(x for x in self.zusto["ausschuesse"] if x["nr"] == k["ausschuss"])
            r = next(x for x in a["rechte"] if x["nr"] == k["nr"])
        else:
            v = next(x for x in self.quelle["verfahren"] if x["id"] == k["verfahren"])
            r = next(x for x in v["ausgaenge"] if x["wenn"] == k["ausgang"])
        if r[k["feld"]] != k["alt"]:
            raise ValueError(f"Korrektur passt nicht zur Quelle: {k}")
        r[k["feld"]] = k["neu"]
        r["korrigiert"] = k["beleg"]
        return k

    def bahnen(self, vid):
        v = self.verfahren.get(vid)
        if not v:
            return set()
        if v.get("jedes_gremium"):
            return set(BAHN.values())
        return {s.get("bahn") for s in v["schritte"]} & set(BAHN.values())


def assign(typ, titel, arts, entsch, ohne_soll=()):
    """Verfahren eines Vorgangs nach Vorlagenart der Hauptvorlage, Gremienarten und Titel: (id, sicherheit, grund).
    Regeln wie assign() in bonn-entscheidet/einordnung.py; ohne Soll (z. B. Bürgerbrief) → (None, None, grund)."""
    typ, titel = typ or "", titel or ""
    if typ in ohne_soll:
        return None, None, f"kein Verfahren im Regelwerk für „{typ}“"
    if typ == "Anregungen und Beschwerden" or typ.startswith("Bürgerantrag"):
        return "buergerantrag", "hoch", f"Vorlagenart „{typ}“ (§ 24 GO NRW)"
    fixed = {"Einwohnerfrage": "einwohnerfrage", "Große Anfrage": "grosse-anfrage", "Kleine Anfrage": "kleine-anfrage",
             "Mitteilungsvorlage": "mitteilung", "Informationsbrief": "mitteilung", "Dringlichkeitsantrag": "dringlichkeitsantrag"}
    if typ in fixed:
        return fixed[typ], "hoch", f"Vorlagenart „{typ}“"
    if typ.startswith(("Dringlichkeitsentscheidung", "Eilentscheidung")):
        return "dringlichkeitsentscheidung", "hoch", f"Vorlagenart „{typ}“"
    if typ.startswith("Tagesordnungspunkte in nichtöffentlicher"):
        return "nichtoeffentlich", "hoch", "nichtöffentliche Tagesordnungspunkte"
    if typ in ("Antrag", "Änderungsantrag"):
        sure = "hoch" if typ == "Antrag" else "mittel"
        if arts and arts <= {"Bezirksvertretungen"}:
            return "antrag-bv", sure, "Antrag, beraten nur in Bezirksvertretungen"
        if arts & {"Rat", "Ratsgremien"}:
            return "antrag-rat", sure, "Antrag mit Beratung in Rat oder Ausschuss"
        if re.search(r"Bezirks(fraktion|verordnete|vertretung)|\bBV\b", titel):
            return "antrag-bv", "mittel", "Antrag ohne bekanntes Gremium; der Titel nennt die Bezirksebene"
        return "antrag-rat", "mittel", "Antrag ohne bekanntes Gremium; angenommen: Rat oder Ausschuss"
    if typ.startswith("Beschlussvorlage"):
        if BAULEIT_RE.search(titel):
            return "bauleitplanung", "hoch" if BAULEIT_SICHER.search(titel) else "mittel", "Bauleitplanung (Titel)"
        if entsch and entsch <= {"Ratsgremien"}:
            return "ausschuss-entscheidung", "hoch", "verbindlich entscheidet ein Ausschuss"
        if "Rat" in entsch:
            return "beschlussvorlage", "hoch", "verbindlich entscheidet der Rat"
        if entsch and entsch <= {"Bezirksvertretungen"}:
            return "beschlussvorlage", "mittel", "die Bezirksvertretung entscheidet selbst"
        return "beschlussvorlage", "mittel", "entscheidendes Gremium noch nicht bekannt"
    return "beschlussvorlage", "mittel", f"kein eigenes Verfahren für „{typ}“"


def stammnummer(reference):
    return (reference or "").split("-")[0].strip()


def abgleich(db, modell):
    """Je Vorgang: Verfahren, Sicherheit, Gremien (Ist/Soll) und Passung."""
    cons = collections.defaultdict(list)
    for pid, cls, role in db.execute("SELECT c.paper_id, o.classification, c.role FROM consultation c "
                                     "JOIN organization o ON o.id = c.organization_id"):
        cons[pid].append((cls, role))
    groups = collections.defaultdict(list)
    for p in db.execute("SELECT id, reference, name, paper_type, date FROM paper"):
        groups[stammnummer(p[1])].append(p)
    rows = []
    for st, ps in sorted(groups.items()):
        head = next((p for p in ps if p[1].strip() == st), None) or next((p for p in ps if p[3] not in SIDE), ps[0])
        arts = {c for p in ps for c, _ in cons[p[0]] if c}
        entsch = {c for p in ps for c, r in cons[p[0]] if c and r == "Entscheidung"}
        vid, sure, why = assign(head[3], head[2], arts, entsch, modell.ohne_soll)
        ist, soll = {BAHN[a] for a in arts if a in BAHN}, modell.bahnen(vid)
        passung = "ohne Soll" if vid is None else "ohne Beratung" if not ist else "passt" if ist <= soll else "weicht ab"
        rows.append({"stammnummer": st, "jahr": (head[4] or "")[:4], "typ": head[3], "verfahren": vid or "",
                     "sicherheit": sure or "", "grund": why, "dokumente": len(ps), "ist_bahnen": ",".join(sorted(ist)),
                     "soll_bahnen": ",".join(sorted(soll)), "passung": passung,
                     "abweichung": ",".join(sorted(ist - soll)) if passung == "weicht ab" else ""})
    return rows


def write():
    """Audit des Soll-Ist-Abgleichs: data/export/audit_soll.tsv (ohne Titel; Datenschutz)."""
    modell = Modell()
    db = sqlite3.connect(config.DB)
    rows = abgleich(db, modell)
    db.close()
    path = config.EXPORT / "audit_soll.tsv"
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=AUDIT, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    c = collections.Counter
    print(f"Soll-Modell: {len(rows)} Vorgänge; Sicherheit {dict(c(r['sicherheit'] or 'ohne' for r in rows))}; "
          f"Passung {dict(c(r['passung'] for r in rows))}; {len(modell.korrigiert)} Korrekturen → {path}")
    return rows
