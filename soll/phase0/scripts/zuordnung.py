"""Phase 0 Soll-Modell: Zuordnung unserer Vorlagen zu den 13 Verfahren aus „Bonn entscheidet“.

Regeln übertragen aus anster2025/bonn-entscheidet, einordnung.py, Funktion assign() (Commit 26641f7, MIT).
Vorgang = alle Vorlagen einer Stammnummer (Drucksachennummer ohne Zusatz „-NN XX“). Die Beratungsfolge vom
Deckblatt (plan_arts) fehlt bei uns und bleibt leer. Aufruf: python soll/phase0/scripts/zuordnung.py <bonn-entscheidet>
"""
import collections
import csv
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "soll" / "phase0" / "out"
SIDE_AA = "Änderungsantrag"
SIDE = ("Stellungnahme der Verwaltung", "Änderungsantrag")
BAULEIT_RE = re.compile(r"Bebauungsplan|Satzungsbeschluss|Aufstellungsbeschluss|Offenlage|"
                        r"Flächennutzungsplan|frühzeitige[nr]? (Öffentlichkeits)?[Bb]eteiligung", re.I)
BAULEIT_SICHER = re.compile(r"Bebauungsplan|Flächennutzungsplan(änderung)?\b.*(Aufstellung|"
                            r"Offenlage|Satzung|Beteiligung|Änderung)", re.I)
BAHN = {"Bezirksvertretungen": "bv", "Ratsgremien": "aus", "Rat": "rat"}


def assign(typ, titel, arts, entsch):
    """Wie assign() in bonn-entscheidet; Rückgabe (verfahren, sicherheit, grund)."""
    typ, titel = typ or "", titel or ""
    if typ in ("Anregungen und Beschwerden",) or typ.startswith("Bürgerantrag"):
        return "buergerantrag", "hoch", "Dokumenttyp Bürgerantrag"
    if typ == "Einwohnerfrage":
        return "einwohnerfrage", "hoch", "Dokumenttyp"
    if typ == "Große Anfrage":
        return "grosse-anfrage", "hoch", "Dokumenttyp"
    if typ == "Kleine Anfrage":
        return "kleine-anfrage", "hoch", "Dokumenttyp"
    if typ.startswith("Dringlichkeitsentscheidung") or typ.startswith("Eilentscheidung"):
        return "dringlichkeitsentscheidung", "hoch", "Dokumenttyp"
    if typ in ("Mitteilungsvorlage", "Informationsbrief"):
        return "mitteilung", "hoch", "Dokumenttyp"
    if typ.startswith("Tagesordnungspunkte in nichtöffentlicher"):
        return "nichtoeffentlich", "hoch", "Dokumenttyp"
    if typ == "Dringlichkeitsantrag":
        return "dringlichkeitsantrag", "hoch", "Dokumenttyp"
    if typ in ("Antrag", SIDE_AA):
        sure = "hoch" if typ == "Antrag" else "mittel"
        if arts and arts <= {"Bezirksvertretungen"}:
            return "antrag-bv", sure, "nur Bezirksvertretungen"
        if arts & {"Rat", "Ratsgremien"}:
            return "antrag-rat", sure, "Rat oder Ausschuss"
        if re.search(r"Bezirks(fraktion|verordnete|vertretung)|\bBV\b", titel):
            return "antrag-bv", "mittel", "Titel nennt Bezirksebene"
        return "antrag-rat", "mittel", "ohne Gremium, angenommen Rat"
    if typ.startswith("Beschlussvorlage"):
        if BAULEIT_RE.search(titel):
            return "bauleitplanung", "hoch" if BAULEIT_SICHER.search(titel) else "mittel", "Titel Bauleitplanung"
        if entsch and entsch <= {"Ratsgremien"}:
            return "ausschuss-entscheidung", "hoch", "Ausschuss entscheidet"
        if "Rat" in entsch:
            return "beschlussvorlage", "hoch", "Rat entscheidet"
        if entsch and entsch <= {"Bezirksvertretungen"}:
            return "beschlussvorlage", "mittel", "BV entscheidet"
        return "beschlussvorlage", "mittel", "Entscheidungsgremium unbekannt"
    return "beschlussvorlage", "mittel", f"kein eigenes Verfahren für „{typ}“"


def main(be):
    verf = json.loads((Path(be) / "data" / "verfahren.json").read_text(encoding="utf-8"))
    soll_bahnen = {v["id"]: {s.get("bahn") for s in v.get("schritte", [])} for v in verf["verfahren"]}
    # Mitteilung und nichtöffentliche Punkte: Schritte ohne Bahn, also in jedem Gremium möglich
    for v in verf["einordnung_extra"]["verfahren"]:
        soll_bahnen[v["id"]] = set(BAHN.values())
    db = sqlite3.connect(ROOT / "data" / "build" / "allris.sqlite")
    papers = db.execute("SELECT id, reference, name, paper_type, date FROM paper").fetchall()
    cons = collections.defaultdict(list)
    for pid, cls, role in db.execute("SELECT c.paper_id, o.classification, c.role FROM consultation c "
                                     "JOIN organization o ON o.id = c.organization_id"):
        cons[pid].append((cls, role))
    groups = collections.defaultdict(list)
    for p in papers:
        groups[(p[1] or "").split("-")[0].strip()].append(p)
    rows = []
    for st, ps in groups.items():
        main_p = next((p for p in ps if p[1].strip() == st), None) or next((p for p in ps if p[3] not in SIDE), ps[0])
        arts = {c for p in ps for c, _ in cons[p[0]] if c}
        entsch = {c for p in ps for c, r in cons[p[0]] if c and r == "Entscheidung"}
        vid, sure, why = assign(main_p[3], main_p[2], arts, entsch)
        ist = {BAHN[a] for a in arts if a in BAHN}
        soll = soll_bahnen.get(vid, set())
        fit = "ohne Beratung" if not ist else ("passt" if ist <= soll else "weicht ab")
        rows.append({"stammnummer": st, "jahr": (main_p[4] or "")[:4], "typ": main_p[3], "verfahren": vid,
                     "sicherheit": sure, "grund": why, "dokumente": len(ps), "ist_bahnen": ",".join(sorted(ist)),
                     "soll_bahnen": ",".join(sorted(b for b in soll if b)), "passung": fit})
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "zuordnung.tsv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t")
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: r["stammnummer"]))
    c = collections.Counter
    summary = {
        "vorgaenge": len(rows), "vorlagen": len(papers),
        "verfahren": c(r["verfahren"] for r in rows).most_common(),
        "sicherheit": c(r["sicherheit"] for r in rows).most_common(),
        "ohne_eigenes_verfahren": c(r["typ"] for r in rows if r["grund"].startswith("kein eigenes")).most_common(),
        "passung": c(r["passung"] for r in rows).most_common(),
        "passung_je_verfahren": {v: c(r["passung"] for r in rows if r["verfahren"] == v).most_common()
                                 for v in sorted({r["verfahren"] for r in rows})},
        "abweichung_bahnen": c((r["verfahren"], r["ist_bahnen"]) for r in rows if r["passung"] == "weicht ab").most_common(12),
    }
    (OUT / "zuordnung_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
