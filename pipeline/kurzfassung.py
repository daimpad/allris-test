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

from . import config, volltext

API = "https://api.mistral.ai/v1/chat/completions"
MODELL = os.environ.get("KURZFASSUNG_MODELL", "mistral-small-latest")
MAX_JE_LAUF = int(os.environ.get("KURZFASSUNG_MAX", "50"))   # zuerst klein, um Kosten und Güte zu messen
MAX_ZEICHEN = 12000
UEBERNAHME_WOERTER = 6
FREIGEGEBEN = False   # erst nach Prüfung der Stichprobe von Hand auf True setzen
VERZEICHNIS = Path(os.environ.get("KURZFASSUNGEN", config.ROOT / "_kurzfassungen"))
HAUSNUMMER = re.compile(r"(?:straße|str\.|weg|platz|allee|gasse|ring|ufer)\s+\d{1,4}\b", re.I)

ANWEISUNG = """Du schreibst Kurzfassungen von Vorlagen des Rates der Stadt Bonn für Bürgerinnen und Bürger ohne
Verwaltungswissen. Schreibe zwei bis drei kurze Sätze in einfacher Sprache, höchstens 60 Wörter: worum es geht, was
entschieden, beantragt oder mitgeteilt wird und, wenn genannt, welcher Ort betroffen ist. Formuliere vollständig mit
eigenen Worten; übernimm keine Sätze und keine längeren Wortfolgen aus dem Text. Nenne keine Namen von Privatpersonen
und keine Hausnummern. Erfinde nichts; was im Text nicht steht, lässt du weg. Antworte nur mit der Kurzfassung."""


def _woerter(text):
    return re.findall(r"\w+", (text or "").lower())


def uebernahme(kurz, text, n=UEBERNAHME_WOERTER + 1):
    """Erste Wortfolge aus n Wörtern, die wörtlich auch im Text steht (sonst None)."""
    quelle = _woerter(text)
    folgen = {tuple(quelle[i:i + n]) for i in range(len(quelle) - n + 1)}
    k = _woerter(kurz)
    for i in range(len(k) - n + 1):
        if tuple(k[i:i + n]) in folgen:
            return " ".join(k[i:i + n])
    return None


def pruefe(kurz, text):
    """Grund, aus dem eine Kurzfassung verworfen wird, oder None."""
    if not kurz or len(_woerter(kurz)) < 8:
        return "zu kurz"
    if uebernahme(kurz, text):
        return f"wörtliche Übernahme von mehr als {UEBERNAHME_WOERTER} Wörtern"
    if HAUSNUMMER.search(kurz):
        return "Hausnummer genannt"
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


def laden(verzeichnis=None):
    path = Path(verzeichnis or VERZEICHNIS) / "kurzfassungen.jsonl"
    if not path.exists():
        return {}
    return {r["sha"]: r for r in map(json.loads, open(path, encoding="utf-8"))}


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
        if uri in texts and volltext.allowed(p.get("paperType")):
            papers.setdefault(uri, p)
    todo = [(uri, p) for uri, p in sorted(papers.items()) if texts[uri]["sha"] not in have][:MAX_JE_LAUF]
    tokens = [0, 0]
    for uri, p in todo:
        main, _ = volltext.clean(texts[uri]["text"])
        main = re.sub(r"\s+", " ", main).strip()[:MAX_ZEICHEN]
        kurz, usage = anfrage(p.get("name") or "", main, schluessel)
        tokens[0] += usage.get("prompt_tokens", 0)
        tokens[1] += usage.get("completion_tokens", 0)
        grund = pruefe(kurz, main)
        have[texts[uri]["sha"]] = {"sha": texts[uri]["sha"], "datei": uri, "drucksache": p["reference"],
                                   "kurzfassung": None if grund else kurz, "verworfen": grund, "modell": MODELL,
                                   "erzeugt": datetime.now(timezone.utc).date().isoformat()}
        time.sleep(0.5)
    with open(base / "kurzfassungen.jsonl", "w", encoding="utf-8") as f:
        for sha in sorted(have):
            f.write(json.dumps(have[sha], ensure_ascii=False) + "\n")
    ok = [r for r in have.values() if r["kurzfassung"]]
    print(f"Kurzfassungen: {len(todo)} neu ({tokens[0]} Eingabe-, {tokens[1]} Ausgabe-Tokens), "
          f"{len(ok)} vorhanden, {sum(1 for r in have.values() if r['verworfen'])} verworfen → {base}")
    sample = base / "stichprobe_kurzfassungen.tsv"
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
    return {r["drucksache"]: {"text": r["kurzfassung"], "modell": r["modell"], "erzeugt": r["erzeugt"]}
            for r in laden(verzeichnis).values() if r["kurzfassung"]}
