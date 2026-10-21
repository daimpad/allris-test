"""Stufe C: Orte aus dem Volltext mit einem Sprachmodell, gegengeprüft mit den Regeln der Stufe B (CLAUDE.md 5.2).

Für Vorlagen ohne eigenen Ortsbezug aus Titel, Ort der Stadt oder Bebauungsplan (dieselben wie bei volltext.py).
1. Erzeugen (`erzeugen`, nur mit Schlüssel, höchstens MAX_JE_LAUF je Lauf, je Datei-Hash einmal): Das Modell nennt
   aus dem bereinigten Hauptteil je Ort Name, Art und Rolle („gegenstand“ oder „erwähnt“). Gespeichert werden nur
   diese Angaben, nie Text (Rahmen laut Antwort der Stadt Bonn vom 19.10.2026: keine Zitate, keine Auszüge).
   Ablage: orte_stufe_c.jsonl im Branch `kurzfassungen` (Verzeichnis KURZFASSUNGEN).
2. Gegenprüfen (`pruefen`): Ein Ort zählt nur, wenn sein Name im Hauptteil steht und das Verzeichnis der Stufe B ihn
   einer Straße, einem Ortsteil oder einem Stadtbezirk zuordnet; Gattungsnamen („Markt“) und Listen mit mehr als
   volltext.MAX_ORTSTEILE Ortsteilen zählen nicht.
   - Ort aus Stufe B, vom Modell als Gegenstand bestätigt: Konfidenz „mittel“, wenn die Regel „mittel“ erlaubt.
   - Ort aus Stufe B, vom Modell als nur erwähnt eingestuft: Konfidenz „niedrig“ (nichts wird gelöscht).
   - Neuer Ort, nur vom Modell als Gegenstand genannt: Methode `llm_…`, Konfidenz „niedrig“.
3. Anwenden (`anwenden`, nach `build`, vor `export`): erst wenn FREIGEGEBEN gesetzt ist (nach Prüfung der Stichprobe
   von Hand); bis dahin nur Audit (audit_stufe_c.tsv) und einmalig eine Stichprobe von 30 im Branch.
"""
import csv
import json
import os
import random
import re
import sqlite3
import traceback
from datetime import datetime, timezone
from pathlib import Path

from . import config, sprachmodell, volltext
from .geocode import Gazetteer
from .objekte import Objekte

MODELL = os.environ.get("STUFE_C_MODELL",
                        {"anthropic": "claude-sonnet-5-5"}.get(sprachmodell.ANBIETER, "mistral-large-latest"))
MAX_JE_LAUF = int(os.environ.get("STUFE_C_MAX", "50"))   # zuerst klein, um Kosten und Güte zu messen
MAX_ZEICHEN = 16000
MAX_TOKENS = 1200     # erster Lauf (21.10.2026, 600): zwei Antworten ohne lesbares JSON, vermutlich abgeschnitten
MAX_VERSUCHE = 3      # gescheiterte Anfragen werden in späteren Läufen wiederholt
FREIGEGEBEN = False   # erst nach Prüfung der Stichprobe von Hand auf True setzen
VERZEICHNIS = Path(os.environ.get("KURZFASSUNGEN", config.ROOT / "_kurzfassungen"))
DATEI = "orte_stufe_c.jsonl"
ARTEN = {"strasse", "ortsteil", "stadtbezirk", "objekt", "kreuzung"}
ROLLEN = {"gegenstand", "erwähnt"}
ZIFFERN = re.compile(r"\s*\d+\s*[a-zA-Z]?\b")

ANWEISUNG = """Du liest Vorlagen des Rates der Stadt Bonn und bestimmst die Orte in Bonn, die darin vorkommen.
Antworte nur mit JSON der Form {"orte": [{"name": "...", "art": "...", "rolle": "...", "ortsteil": "..."}]}.
- name: der Ort, wie er im Text steht (Straße, Platz, Ortsteil, Stadtbezirk, Gebäude oder Anlage), ohne Hausnummer.
- art: "strasse", "ortsteil", "stadtbezirk", "objekt" (Gebäude, Schule, Park, Anlage) oder "kreuzung".
- rolle: "gegenstand", wenn die Vorlage diesen Ort betrifft (dort wird gebaut, geplant, geändert, gefragt);
  "erwähnt", wenn er nur nebenbei vorkommt (Anschrift einer Stelle, Vergleich, Aufzählung, Sitzungsort).
- ortsteil: Ortsteil, wenn der Text ihn für diesen Ort nennt, sonst "".
Nenne nicht die Stadt Bonn als Ganzes („Bonn“, „Bundesstadt Bonn“, „Stadtgebiet“) und keine Orte außerhalb
Bonns. Nenne keine Personen und keine Hausnummern. Nenne nur Orte, die wörtlich im Text stehen. Gibt es keinen Ort,
antworte {"orte": []}."""


def _anfrage(titel, text, schluessel):
    return sprachmodell.frage(ANWEISUNG, f"Titel: {titel}\n\nText der Vorlage:\n{text}", MODELL, schluessel,
                              max_tokens=MAX_TOKENS, json_antwort=True)


def bereinigen(antwort):
    """Gültige Orte aus der Antwort des Modells: bekannte Art und Rolle, ohne Ziffern (Hausnummern)."""
    d = sprachmodell.json_aus(antwort) or {}
    out = []
    for o in d.get("orte") or []:
        if not isinstance(o, dict):
            continue
        name = ZIFFERN.sub(" ", str(o.get("name") or "")).strip(" ,;")
        art, rolle = str(o.get("art") or "").lower(), str(o.get("rolle") or "").lower()
        if len(name) >= 3 and art in ARTEN and rolle in ROLLEN:
            out.append({"name": name[:80], "art": art, "rolle": rolle,
                        "ortsteil": ZIFFERN.sub(" ", str(o.get("ortsteil") or "")).strip()[:40]})
    return out


def laden(verzeichnis=None):
    path = Path(verzeichnis or VERZEICHNIS) / DATEI
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return {r["sha"]: r for r in map(json.loads, f)}


def kandidaten(db):
    """Drucksache → Vorlage (id, reference, name, paper_type, main_file) ohne eigenen Ortsbezug: alle Ortsbezüge
    stammen aus dem Volltext oder sind vererbt (oder es gibt keinen)."""
    own = {r[0] for r in db.execute("SELECT DISTINCT paper_id FROM paper_location "
                                    "WHERE method NOT LIKE 'volltext_%' AND method <> 'vererbt'")}
    out = {}
    with open(config.PAPERS, encoding="utf-8") as f:
        papers = [json.loads(line) for line in f]
    for p in papers:
        main = (p.get("mainFile") or {}).get("id")
        if p["id"] not in own and main and volltext.allowed(p.get("paperType")):
            out.setdefault(p["reference"], {"id": p["id"], "reference": p["reference"], "name": p.get("name"),
                                            "paperType": p.get("paperType"), "main_file": main, "web": p.get("web")})
    return out


def _texte():
    if not config.TEXTE.exists():
        return {}
    with open(config.TEXTE, encoding="utf-8") as f:
        return {r["uri"]: r for r in map(json.loads, f)}


def erzeugen(db, verzeichnis=None, anfrage=_anfrage):
    """Neue Antworten des Modells für Kandidaten mit Text (höchstens MAX_JE_LAUF); ohne Schlüssel nichts."""
    schluessel = sprachmodell.schluessel()
    if not schluessel:
        print(f"Stufe C: {sprachmodell.SCHLUESSEL[sprachmodell.ANBIETER]} fehlt – nichts angefragt.")
        return
    base = Path(verzeichnis or VERZEICHNIS)
    base.mkdir(parents=True, exist_ok=True)
    have, texte = laden(base), _texte()
    def offen(sha):
        r = have.get(sha)
        return r is None or (r.get("fehler") and r.get("versuche", 1) < MAX_VERSUCHE)
    todo = [(ref, p) for ref, p in sorted(kandidaten(db).items())
            if p["main_file"] in texte and offen(texte[p["main_file"]]["sha"])][:MAX_JE_LAUF]
    tokens = {"ein": 0, "aus": 0}
    for ref, p in todo:
        t = texte[p["main_file"]]
        main = re.sub(r"\s+", " ", volltext.clean(t["text"])[0]).strip()[:MAX_ZEICHEN]
        try:
            antwort, usage = anfrage(p["name"] or "", main, schluessel)
            orte, fehler = bereinigen(antwort), None
            if sprachmodell.json_aus(antwort) is None:
                fehler = ("Antwort abgeschnitten" if usage.get("aus", 0) >= MAX_TOKENS
                          else "Antwort ohne lesbares JSON")
        except Exception as e:  # ein Fehler beim Anbieter hält den Lauf nicht auf
            usage, orte, fehler = {}, [], f"Anfrage gescheitert: {type(e).__name__}"
        for k in tokens:
            tokens[k] += usage.get(k, 0)
        versuche = (have.get(t["sha"]) or {}).get("versuche", 0) + 1
        have[t["sha"]] = {"sha": t["sha"], "datei": p["main_file"], "drucksache": ref, "orte": orte, "fehler": fehler,
                          "versuche": versuche, "anbieter": sprachmodell.ANBIETER, "modell": MODELL,
                          "erzeugt": datetime.now(timezone.utc).date().isoformat()}
    with open(base / DATEI, "w", encoding="utf-8") as f:
        for sha in sorted(have):
            f.write(json.dumps(have[sha], ensure_ascii=False) + "\n")
    sprachmodell.protokoll(base, "stufe-c", MODELL, len(todo), tokens,
                           sum(1 for ref, p in todo if have[texte[p["main_file"]]["sha"]]["fehler"]))
    print(f"Stufe C: {len(todo)} neu ({tokens['ein']} Eingabe-, {tokens['aus']} Ausgabe-Tokens, {MODELL}), "
          f"{len(have)} vorhanden → {base / DATEI}")


def pruefen(gaz, text, orte, b_rows, bv_bezirke=(), objekte=None, objekt_befunde=None):
    """Gegenprüfung eines Ergebnisses. b_rows: Ortsbezüge aus volltext.locate; objekte: Verzeichnis der Gebäude und
    Anlagen (objekte.Objekte). Liefert (Änderungen, Befund): Änderungen als Zeilen mit aktion („bestätigt“,
    „herabgestuft“, „neu“) und den Feldern von Gazetteer.locate. objekt_befunde sammelt (Name, Befund) je Objekt."""
    main = volltext.clean(text)[0]
    low = re.sub(r"\s+", " ", main).lower()
    found = []
    for o in orte:
        if o["name"].lower() not in low:
            continue   # nicht wörtlich im Hauptteil: nicht übernommen
        hint = o["ortsteil"] if o["ortsteil"] in gaz.ot_by_name else ""
        if o["art"] == "objekt" and objekte is not None:
            # Ortsteil des Modells nur, wenn er im Text steht
            obj, befund = objekte.finden(o["name"], hint if hint.lower() in low else "")
            if objekt_befunde is not None:
                objekt_befunde.append((o["name"], befund if obj is None else f"{obj['name']} ({obj['ortsteil']}), {befund}"))
            if obj:
                found.append((o, dict(level="objekt", name=obj["name"], ortsteil=obj["ortsteil"], bezirk=obj["bezirk"],
                                      lon=obj["lon"], lat=obj["lat"], confidence="niedrig", method="objekt",
                                      objektart=obj["art"], osm=obj["osm"])))
                continue
        rows = gaz.locate(f"{o['name']}, {hint}" if hint else o["name"], bv_bezirke)
        rows = [r for r in rows if r["name"] not in volltext.GATTUNG and (not hint or r["level"] != "ortsteil"
                                                                          or r["name"] == hint)]
        found += [(o, r) for r in rows]
    neu_ot = {r["ortsteil"] for o, r in found if o["rolle"] == "gegenstand" and r["ortsteil"]}
    if len(neu_ot) > volltext.MAX_ORTSTEILE:
        return [], f"Liste ({len(neu_ot)} Ortsteile), nicht verortet"
    # Abgleich über Ebene und Namen: ohne den Zusammenhang des Textes ordnet das Verzeichnis eine Straße womöglich
    # einem anderen Ortsteil zu als Stufe B; es gilt dann der Ortsteil aus Stufe B
    b_by_name = {}
    for b in b_rows:
        b_by_name.setdefault((b["level"], b["name"]), []).append(b)
    out, done = [], set()
    for o, r in found:
        for b in b_by_name.get((r["level"], r["name"]), []):
            key = (b["level"], b["name"], b["ortsteil"])
            if key in done:
                continue
            done.add(key)
            if o["rolle"] == "erwähnt" and b["confidence"] != "niedrig":
                out.append(dict(b, aktion="herabgestuft", confidence="niedrig", art=o["art"]))
            elif o["rolle"] == "gegenstand":
                conf = "mittel" if r["confidence"] == "mittel" else b["confidence"]
                out.append(dict(b, aktion="bestätigt", confidence=conf, art=o["art"]))
        key = (r["level"], r["name"], r["ortsteil"])
        if (r["level"], r["name"]) in b_by_name or key in done:
            continue
        done.add(key)
        # ein Ortsteil, in dem schon ein Ort aus Stufe B liegt, kommt nicht als eigene Fläche hinzu
        if o["rolle"] == "gegenstand" and r["level"] != "stadtbezirk" and not (
                r["level"] == "ortsteil" and r["ortsteil"] in {b["ortsteil"] for b in b_rows}):
            lage = f"; Lage laut OpenStreetMap ({r['objektart']}, {r['osm']})" if r["level"] == "objekt" else ""
            out.append(dict(r, aktion="neu", method=f"llm_{r['level']}", confidence="niedrig", art=o["art"],
                            evidence=f"mit Sprachmodell im Hauptteil des Hauptdokuments erkannt: {r['name']}{lage}"))
    return out, "geändert" if out else "keine Änderung"


def _ortsbezuege(db, verzeichnis=None):
    """(Kandidaten, Ergebnisse je Drucksache, Texte, Gazetteer) für Prüfung und Anwendung."""
    kand, texte, have = kandidaten(db), _texte(), laden(verzeichnis)
    by_ref = {r["drucksache"]: r for r in have.values()
              if r["drucksache"] in kand and texte.get(kand[r["drucksache"]]["main_file"], {}).get("sha") == r["sha"]}
    return kand, by_ref, texte


def anwenden(verzeichnis=None, db_path=None):
    """Gegenprüfung aller vorhandenen Ergebnisse; Audit; Übernahme in die Datenbank nur nach Freigabe."""
    base = Path(verzeichnis or VERZEICHNIS)
    db = sqlite3.connect(db_path or config.DB)
    kand, by_ref, texte = _ortsbezuege(db, base)
    if not by_ref:
        print("Stufe C: keine Ergebnisse des Sprachmodells – nichts zu prüfen.")
        db.close()
        return
    gaz, objekte = Gazetteer(), Objekte()
    bv = {}
    for pid, bez in db.execute("SELECT c.paper_id, o.name FROM consultation c JOIN organization o "
                               "ON o.id = c.organization_id WHERE o.name LIKE 'Bezirksvertretung %'"):
        bv.setdefault(pid, set()).add(bez.replace("Bezirksvertretung ", ""))
    audit, changes, objekt_audit = [], {}, []
    for ref, res in sorted(by_ref.items()):
        p, text = kand[ref], texte[kand[ref]["main_file"]]["text"]
        b_rows, _ = volltext.locate(gaz, text, bv.get(p["id"], ()))
        obj_befunde = []
        rows, befund = pruefen(gaz, text, res["orte"], b_rows, bv.get(p["id"], ()), objekte, obj_befunde)
        objekt_audit += [(ref, name, b) for name, b in obj_befunde]
        if res.get("fehler"):
            befund = res["fehler"]
        changes[ref] = rows
        if not rows:
            audit.append((ref, befund, "", "", "", "", "", res["modell"]))
        for r in rows:
            audit.append((ref, befund, r["aktion"], r["method"], r["name"], r["ortsteil"] or "", r["confidence"],
                          res["modell"]))
    with open(config.EXPORT / "audit_stufe_c.tsv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["drucksache", "befund", "aktion", "methode", "ort", "ortsteil", "konfidenz", "modell"])
        w.writerows(audit)
    with open(config.EXPORT / "audit_stufe_c_objekte.tsv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["drucksache", "name (Sprachmodell)", "befund (Verzeichnis der Gebäude und Anlagen)"])
        w.writerows(objekt_audit)
    n = {a: sum(1 for rs in changes.values() for r in rs if r["aktion"] == a) for a in ("neu", "bestätigt", "herabgestuft")}
    print(f"Stufe C: {len(by_ref)} Vorlagen geprüft; {n} → audit_stufe_c.tsv"
          f"{'' if FREIGEGEBEN else ' (nicht übernommen: noch nicht freigegeben)'}")
    _stichprobe(base, kand, changes)
    if FREIGEGEBEN:
        _uebernehmen(db, kand, changes, gaz)
    db.close()


def _uebernehmen(db, kand, changes, gaz):
    from .build import _add_location
    locations = {}
    for ref, rows in changes.items():
        pid = kand[ref]["id"]
        for r in rows:
            loc_id = _add_location(r, locations, gaz)
            if r["aktion"] == "neu":
                db.execute("INSERT OR IGNORE INTO paper_location VALUES (?,?,?,?,?,?,?)",
                           (pid, loc_id, "C", r["method"], r["confidence"], r["evidence"], pid))
            else:
                note = "; Sprachmodell: " + ("Gegenstand der Vorlage" if r["aktion"] == "bestätigt" else "nur erwähnt")
                db.execute("UPDATE paper_location SET confidence = ?, evidence = evidence || ? "
                           "WHERE paper_id = ? AND location_id = ? AND method LIKE 'volltext_%'",
                           (r["confidence"], note, pid, loc_id))
    db.executemany("INSERT OR IGNORE INTO location VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", locations.values())
    db.commit()


def _stichprobe(base, kand, changes):
    """30 Vorlagen mit Änderung zur Prüfung von Hand (einmalig, im Branch; wird nie überschrieben)."""
    path = base / "stichprobe_stufe_c.tsv"
    refs = sorted(ref for ref, rows in changes.items() if rows)
    if path.exists() or len(refs) < 30:
        return
    pick = sorted(random.Random(20261021).sample(refs, 30))
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["nr", "drucksache", "titel", "link", "änderungen (Aktion: Ort, Ortsteil, Konfidenz)",
                    "urteil (richtig/teilweise/falsch)", "anmerkung"])
        for i, ref in enumerate(pick, 1):
            w.writerow([i, ref, kand[ref]["name"], kand[ref]["web"] or "",
                        "; ".join(f"{r['aktion']}: {r['name']}" + (f" ({r['ortsteil']})" if r["ortsteil"] and r["level"] == "strasse" else "")
                                  + f", {r['confidence']}" for r in changes[ref]), "", ""])
    print(f"Stichprobe Stufe C: 30 → {path}")


def schritt():
    """Pipeline-Schritt `stufe-c` (nach build, vor export): neue Anfragen, dann Gegenprüfung und Audit."""
    db = sqlite3.connect(config.DB)
    try:
        erzeugen(db)
    except Exception as e:   # Anbieter oder Netz: Seite wird trotzdem gebaut
        print(f"Stufe C: Erzeugen gescheitert ({type(e).__name__}); weiter mit dem Bestand.")
    db.close()
    try:
        anwenden()
    except Exception:   # ein Fehler hier darf die Seite nicht aufhalten; Stufe C fehlt dann in diesem Lauf
        traceback.print_exc()
        print("Stufe C: Gegenprüfung gescheitert – ohne Stufe C weiter.")
