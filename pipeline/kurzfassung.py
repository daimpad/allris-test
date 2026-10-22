"""Kurzfassungen der Vorlagen in einfacher Sprache (Sprachmodell Mistral, gekennzeichnet).

Rahmen laut Antwort der Stadt Bonn vom 19.10.2026: Verarbeitung der Texte zulässig, keine Zitate und keine Auszüge;
selbst formulierte, gekennzeichnete Kurzfassungen zulässig. Deshalb:
- Eingabe: Titel und bereinigter Hauptteil des Hauptdokuments (volltext.clean), gekürzt auf MAX_ZEICHEN.
- Prüfung jeder Kurzfassung: verworfen wird sie, wenn sie eine Folge von mehr als UEBERNAHME_WOERTER Wörtern wörtlich
  aus dem Text enthält (Auszug) oder eine Hausnummer nennt (Datenschutz).
- Ablage: kurzfassungen.jsonl im Branch `kurzfassungen` (Verzeichnis KURZFASSUNGEN), je Datei-Hash (`textSha256`)
  einmal erzeugt; der Workflow schreibt den Branch zurück. Auf der Seite erscheinen die Kurzfassungen erst, wenn
  FREIGEGEBEN gesetzt ist (nach Prüfung einer Stichprobe von Hand).
Schlüssel: Umgebungsvariable MISTRAL_API_KEY (Secret im Workflow); ohne Schlüssel wird nichts erzeugt.
"""
import csv
import json
import os
import random
import re
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from . import config, sprachmodell, volltext

API = "https://api.mistral.ai/v1/chat/completions"
# Fassung 2 (21.10.2026): großes Modell und genauere Anweisung nach der KI-Vorprüfung der ersten Stichprobe
# (18 plausibel, 8 teilweise, 2 falsch, 2 unklar; Fehler: falscher Akteur, Vermutungen, falsche Orte, vertauschter
# Kostenträger; data/export/kurzfassungen/vorpruefung_kurzfassungen_v1.tsv)
MODELL = os.environ.get("KURZFASSUNG_MODELL", "mistral-large-latest")
FASSUNG = 5   # 3: ohne Überschrift, Absender im ersten Satz, Kosten nur laut Text (Vorprüfung v2); 4: Fragen von
#               Anfragen nur wie gestellt, Gremium und Fraktion nur laut Text (Vorprüfung v4: 20/10/0); 5: Rolle im
#               Verfahren (Kenntnisnahme), keine erschlossenen Fragen oder Ursachen, Ebene einer Zahl (Vorprüfung v5: 23/7/0)
MAX_JE_LAUF = int(os.environ.get("KURZFASSUNG_MAX", "50"))   # zuerst klein, um Kosten und Güte zu messen
MAX_ZEICHEN = 12000
UEBERNAHME_WOERTER = 6
FREIGEGEBEN = False   # erst nach Prüfung der Stichprobe von Hand auf True setzen
VERZEICHNIS = Path(os.environ.get("KURZFASSUNGEN", config.ROOT / "_kurzfassungen"))
# Absender und Gremien, die in einer Kurzfassung nur stehen dürfen, wenn Titel oder Text sie nennen (KI-Vorprüfung v4:
# „Die Grünen beantragen“ und „dem Rat vorgelegt“ ohne Beleg)
PARTEIEN = {"CDU": r"\bCDU\b", "SPD": r"\bSPD\b", "Grüne": r"\bGrüne|\bGRÜNE|Bündnis 90", "FDP": r"\bFDP\b",
            "Linke": r"\bLinke|\bLINKE", "Volt": r"\bVolt\b", "BBB": r"\bBBB\b|Bürger Bund", "AfD": r"\bAfD\b"}
GREMIEN = {"Rat": r"\b(Rat|Rates|Rats\w*|Stadtrat\w*)\b", "Bezirksvertretung": r"Bezirksvertretung",
           "Ausschuss": r"[Aa]usschuss"}
HAUSNUMMER = re.compile(r"(?:straße|str\.|weg|platz|allee|gasse|ring|ufer)\s+\d{1,4}\b", re.I)

ANWEISUNG = """Du schreibst Kurzfassungen von Vorlagen des Rates der Stadt Bonn für Bürgerinnen und Bürger ohne
Verwaltungswissen. Schreibe zwei bis drei kurze Sätze in einfacher Sprache, höchstens 60 Wörter: worum es geht, was
beantragt, vorgeschlagen, beschlossen oder mitgeteilt wird und, wenn genannt, welcher Ort betroffen ist.
- Nenne den richtigen Absender und die Art der Vorlage: Ein Antrag einer Fraktion ist ein Vorschlag, kein Beschluss;
  eine Beschlussvorlage ist ein Vorschlag der Verwaltung; eine Stellungnahme gibt die Sicht der Verwaltung oder einer
  anderen Stelle wieder; eine Mitteilung informiert nur. Schreibe nicht „die Stadt plant“ oder „der Rat will“, wenn
  das nicht im Text steht.
- Gib Bedingungen wieder („nur wenn der Antrag angenommen wird“) und sage, wer Kosten trägt, nur so, wie es im Text steht.
- Nenne nur Orte, Zahlen und Daten, die im Text stehen; nenne keine Stadtbezirke oder Ortsteile, die der Text nicht nennt.
- Vermute nichts und ergänze nichts („vermutlich“, „oder“-Aufzählungen möglicher Inhalte). Steht wenig im Text, schreibe
  kurz, was dort steht.
- Wer Kosten trägt, schreibst du nur, wenn es im Text ausdrücklich steht.
- Bei einer Anfrage gibst du nur die Fragen wieder, die gestellt werden; füge keine eigenen Fragen hinzu.
- Nenne eine Fraktion oder ein Gremium (Rat, Ausschuss, Bezirksvertretung) nur, wenn Titel oder Text sie nennen.
  Steht dort „Koalition“, schreibe „die Koalition“ und zähle keine Parteien auf.
- Gib die Rolle im Verfahren genau wieder: Soll ein Gremium etwas nur zur Kenntnis nehmen, schreibe das; schreibe dann
  nicht, dass es etwas beschließen oder ablehnen soll. Was ein Antrag fordert, ist eine Forderung, keine Tatsache.
- Gib Fragen so wieder, wie sie gestellt sind; erschließe sie nicht aus der Antwort. Nenne keine Gründe oder
  Ursachen, die der Text nicht nennt.
- Gilt eine Zahl für eine bestimmte Ebene (ganze Stadt, Stadtbezirk, Verwaltung, Beschäftigte), nenne diese Ebene.
Beginne direkt mit dem ersten Satz und nenne den Absender darin („Die Verwaltung schlägt vor …“, „Die CDU-Fraktion
beantragt …“); schreibe keine Überschrift und keine Angaben wie „Absender:“ oder „Art der Vorlage:“.
Formuliere vollständig mit eigenen Worten; übernimm keine Sätze und keine längeren Wortfolgen aus dem Text. Nenne keine
Namen von Privatpersonen und keine Hausnummern. Antworte nur mit der Kurzfassung."""


def _woerter(text):
    return re.findall(r"\w+", (text or "").lower())


def _folgen(woerter, n):
    return {tuple(woerter[i:i + n]) for i in range(len(woerter) - n + 1)}


_NAMEN = None


def namen():
    """Namen von Gremien und Ämtern (OParl, CC0): lange Eigennamen, kein Text der Dokumente."""
    global _NAMEN
    if _NAMEN is None:
        orgs = json.loads(config.ORGANIZATIONS.read_text()) if config.ORGANIZATIONS.exists() else []
        _NAMEN = [o.get("name") or "" for o in orgs]
    return _NAMEN


def uebernahme(kurz, text, n=UEBERNAHME_WOERTER + 1, erlaubt=()):
    """Erste Wortfolge aus n Wörtern, die wörtlich auch im Text steht (sonst None). Stellen, an denen die Kurzfassung
    eine Angabe aus `erlaubt` wiederholt (Titel der Vorlage, Namen von Gremien; ab drei Wörtern), zählen nicht: Sie
    sind öffentliche Angaben aus der OParl-API, kein Auszug aus dem Dokument."""
    folgen = _folgen(_woerter(text), n)
    k = _woerter(kurz)
    frei = set()
    for e in erlaubt:
        w = _woerter(e)
        if len(w) >= 3:
            frei |= {j for i in range(len(k) - len(w) + 1) if k[i:i + len(w)] == w for j in range(i, i + len(w))}
    for i in range(len(k) - n + 1):
        f = tuple(k[i:i + n])
        if f in folgen and not frei & set(range(i, i + n)):
            return " ".join(f)
    return None


KOPFZEILE = re.compile(r"^(Absender|Art der Vorlage)\s*:|:\s*$|^[^.!?]{0,80}$")


def glaetten(kurz):
    """Markdown-Auszeichnungen (*kursiv*, **fett**, `Code`) und vorangestellte Überschriften („Stellungnahme der
    Verwaltung“, „Absender: …“) entfernen; Zeilen werden zu einem Absatz: die Seite zeigt reinen Text."""
    zeilen = [z.strip() for z in re.sub(r"(\*{1,2}|_{2}|`)(.+?)\1", r"\2", kurz or "").split("\n")]
    while len(zeilen) > 1 and (not zeilen[0] or KOPFZEILE.search(zeilen[0])):
        zeilen = zeilen[1:]
    return " ".join(z for z in zeilen if z).strip()


# Prüfungen nach der KI-Vorprüfung von Fassung 3 (21.10.2026): Sätze zum Kostenträger, die der Text nicht stützt,
# werden entfernt; Zahlen, die nicht im Text stehen (falsch errechnete Summen), führen zum Verwerfen
KOSTEN_SATZ = re.compile(r"\bKosten\b.*\b(trägt|tragen|übernimmt|übernehmen|zahlt|zahlen)\b|"
                         r"\b(trägt|tragen|übernimmt|übernehmen|zahlt|zahlen)\b.*\bKosten\b")
KOSTEN_IM_TEXT = re.compile(r"Kostenträger|Kostenübernahme|Übernahme der[^.]{0,60}Kosten|"
                            r"(trägt|tragen|übernimmt|übernehmen)[^.]{0,40}Kosten|Kosten[^.]{0,40}(trägt|tragen|übernimmt|übernehmen)")
ZAHL = re.compile(r"\d+(?:[.,]\d+)*")


def ohne_kostensatz(kurz, text):
    """Sätze zum Kostenträger entfernen, wenn der Text keinen Kostenträger nennt."""
    if KOSTEN_IM_TEXT.search(text or ""):
        return kurz
    saetze = re.split(r"(?<=[.!?])\s+", kurz or "")
    return " ".join(s for s in saetze if not KOSTEN_SATZ.search(s)).strip()


def fremde_zahl(kurz, text):
    """Erste Zahl (ab zwei Ziffern) der Kurzfassung, die so nicht im Text steht, sonst None."""
    tausender = lambda t: re.sub(r"(?<=\d)\.(?=\d{3}\b)", "", t)
    quelle = set()
    for z in ZAHL.findall(text or ""):   # auch Teile von Datumsangaben („31.12.2024“ → „2024“)
        quelle |= {tausender(z), *re.split(r"[.,]", z)}
    for z in ZAHL.findall(kurz or ""):
        if len(re.sub(r"\D", "", z)) >= 2 and tausender(z) not in quelle:
            return z
    return None


def fremder_akteur(kurz, quelle):
    """Fraktion oder Gremium, das die Kurzfassung nennt, Titel und Text aber nicht (sonst None)."""
    for name, rx in {**PARTEIEN, **GREMIEN}.items():
        if re.search(rx, kurz or "") and not re.search(rx, quelle or ""):
            return name
    return None


def pruefe(kurz, text, titel=""):
    """Grund, aus dem eine Kurzfassung verworfen wird, oder None."""
    if not kurz or len(_woerter(kurz)) < 8:
        return "zu kurz"
    if uebernahme(kurz, text, erlaubt=[titel, *namen()]):
        return f"wörtliche Übernahme von mehr als {UEBERNAHME_WOERTER} Wörtern"
    if HAUSNUMMER.search(kurz):
        return "Hausnummer genannt"
    z = fremde_zahl(kurz, f"{titel} {text}")   # Zahlen im Titel („Controllingbericht 2023“) zählen mit
    if z:
        return f"Zahl nicht im Text: {z}"
    a = fremder_akteur(kurz, f"{titel} {text}")
    if a:
        return f"nicht in Titel oder Text: {a}"
    return None


def _anfrage(titel, text, schluessel, tries=4):
    body = json.dumps({"model": MODELL, "temperature": 0.2, "max_tokens": 220, "messages": [
        {"role": "system", "content": ANWEISUNG},
        {"role": "user", "content": f"Titel: {titel}\n\nText der Vorlage:\n{text}"}]}).encode()
    req = urllib.request.Request(API, data=body, headers={"Content-Type": "application/json",
                                                         "Authorization": f"Bearer {schluessel}"})
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.load(r)
            return d["choices"][0]["message"]["content"].strip(), d.get("usage") or {}
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(2 ** (i + 2))


def _ergebnis(kurz, grund):
    """Felder eines Ergebnisses. Ein verworfener Entwurf wird aufbewahrt, außer er enthält Text der Quelle oder eine
    Hausnummer (dann wird nichts gespeichert); er erscheint nirgends und dient nur der erneuten Prüfung."""
    if not grund:
        return {"kurzfassung": kurz, "verworfen": None, "entwurf": None}
    aufbewahren = not (grund.startswith("wörtliche Übernahme") or grund.startswith("Hausnummer"))
    return {"kurzfassung": None, "verworfen": grund, "entwurf": kurz if aufbewahren else None}


def laden(verzeichnis=None):
    path = Path(verzeichnis or VERZEICHNIS) / "kurzfassungen.jsonl"
    if not path.exists():
        return {}
    return {r["sha"]: r for r in map(json.loads, open(path, encoding="utf-8"))}


def _schreiben(base, have):
    tmp = base / "kurzfassungen.jsonl.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for sha in sorted(have):
            f.write(json.dumps(have[sha], ensure_ascii=False) + "\n")
    tmp.replace(base / "kurzfassungen.jsonl")


def erzeugen(verzeichnis=None, anfrage=_anfrage):
    """Neue Kurzfassungen für Hauptdokumente mit Text (höchstens MAX_JE_LAUF je Lauf); Stichprobe einmalig."""
    schluessel = os.environ.get("MISTRAL_API_KEY")
    if not schluessel:
        print("Kurzfassungen: MISTRAL_API_KEY fehlt – nichts erzeugt.")
        return
    base = Path(verzeichnis or VERZEICHNIS)
    base.mkdir(parents=True, exist_ok=True)
    have = laden(base)
    texts = {}
    if config.TEXTE.exists():
        texts = {r["uri"]: r for r in map(json.loads, open(config.TEXTE, encoding="utf-8"))}
    papers = {}
    for line in open(config.PAPERS, encoding="utf-8"):
        p = json.loads(line)
        uri = (p.get("mainFile") or {}).get("id")
        # Sammellisten nichtöffentlicher Punkte teilen meist nur mit, dass es keine gibt: keine Kurzfassung
        if uri in texts and volltext.allowed(p.get("paperType")) and not volltext.sammelliste(p.get("name")):
            papers.setdefault(uri, p)
    # vorhandene Kurzfassungen der aktuellen Fassung nach den jeweils geltenden Prüfungen neu bewerten, auch
    # aufbewahrte Entwürfe (verworfen ohne Text der Quelle), damit geänderte Regeln sie wieder zulassen können
    for r in have.values():
        kurz = r["kurzfassung"] or r.get("entwurf")
        if r.get("fassung", 1) == FASSUNG and kurz and r.get("datei") in texts:
            main = re.sub(r"\s+", " ", volltext.clean(texts[r["datei"]]["text"])[0]).strip()[:MAX_ZEICHEN]
            kurz = ohne_kostensatz(glaetten(kurz), main)
            grund = pruefe(kurz, main, (papers.get(r["datei"]) or {}).get("name") or "")
            r.update(_ergebnis(kurz, grund))
    # ältere Fassungen zuerst (so entsteht die neue Stichprobe aus denselben Vorlagen), danach neue Texte
    alt = lambda uri: have[texts[uri]["sha"]].get("fassung", 1) < FASSUNG
    todo = ([(uri, p) for uri, p in sorted(papers.items()) if texts[uri]["sha"] in have and alt(uri)]
            + [(uri, p) for uri, p in sorted(papers.items()) if texts[uri]["sha"] not in have])[:MAX_JE_LAUF]
    tokens = [0, 0]
    for i, (uri, p) in enumerate(todo, 1):
        main, _ = volltext.clean(texts[uri]["text"])
        main = re.sub(r"\s+", " ", main).strip()[:MAX_ZEICHEN]
        titel = f"{p.get('name') or ''} (Art der Vorlage: {p.get('paperType') or 'unbekannt'})"
        kurz, usage = anfrage(titel, main, schluessel)
        kurz = ohne_kostensatz(glaetten(kurz), main)
        tokens[0] += usage.get("prompt_tokens", 0)
        tokens[1] += usage.get("completion_tokens", 0)
        grund = pruefe(kurz, main, p.get("name") or "")
        have[texts[uri]["sha"]] = {"sha": texts[uri]["sha"], "datei": uri, "drucksache": p["reference"],
                                   **_ergebnis(kurz, grund), "modell": MODELL, "fassung": FASSUNG,
                                   "erzeugt": datetime.now(timezone.utc).date().isoformat()}
        time.sleep(0.5)
        if i % 25 == 0:   # Zwischenstand sichern: bricht der Lauf ab, bleibt das Erzeugte erhalten
            _schreiben(base, have)
    _schreiben(base, have)
    ok = [r for r in have.values() if r["kurzfassung"] and r.get("fassung", 1) == FASSUNG]
    sprachmodell.protokoll(base, "kurzfassungen", MODELL, len(todo), {"ein": tokens[0], "aus": tokens[1]},
                           sum(1 for uri, p in todo if have[texts[uri]["sha"]]["verworfen"]))
    print(f"Kurzfassungen: {len(todo)} neu ({tokens[0]} Eingabe-, {tokens[1]} Ausgabe-Tokens), "
          f"{len(ok)} vorhanden, {sum(1 for r in have.values() if r['verworfen'])} verworfen → {base}")
    sample = base / f"stichprobe_kurzfassungen_v{FASSUNG}.tsv"   # Fassung 1: stichprobe_kurzfassungen.tsv
    if not sample.exists() and len(ok) >= 30:
        titel = {p["reference"]: (p.get("name"), p.get("web")) for p in papers.values()}
        pick = sorted(random.Random(20261020).sample(ok, 30), key=lambda r: r["drucksache"])
        with open(sample, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, delimiter="\t", lineterminator="\n")
            w.writerow(["nr", "drucksache", "titel", "link", "kurzfassung (KI)", "urteil (zutreffend/teilweise/falsch)",
                        "anmerkung"])
            for i, r in enumerate(pick, 1):
                t, web = titel.get(r["drucksache"], ("", ""))
                w.writerow([i, r["drucksache"], t, web or "", r["kurzfassung"], "", ""])
        print(f"Stichprobe Kurzfassungen: 30 → {sample}")


def fuer_seite(verzeichnis=None):
    """Drucksache → Kurzfassung für den Export, nur wenn freigegeben."""
    if not FREIGEGEBEN:
        return {}
    return {r["drucksache"]: {"text": glaetten(r["kurzfassung"]), "modell": r["modell"], "erzeugt": r["erzeugt"]}
            for r in laden(verzeichnis).values() if r["kurzfassung"] and r.get("fassung", 1) == FASSUNG}
