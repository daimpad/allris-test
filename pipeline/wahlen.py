"""Kommunalwahl 2025 in Bonn: Abruf der Quelldateien (Phase 1, Schritt 1).

Phase 0 (wahlen/phase0/BERICHT.md): Die Ergebnisse der Stadt nach Stimmbezirk (votemanager, wahlen.bonn.de) und die
Flächen der Wahl- und Stimmbezirke 2025 (stadtplan.bonn.de) waren aus der Arbeitsumgebung nicht erreichbar, aus dem
täglichen Workflow dagegen ist stadtplan.bonn.de erreichbar. Der Schritt `wahlen-rohdaten` läuft deshalb im Workflow
`quellen.yml` (auf Knopfdruck) und legt die Dateien unverändert mit Abrufstand im Branch `quellen` ab
(Ordner wahlen2025/). Daraus entsteht nach Prüfung ein fester Ausschnitt in data/kontext/ (Entscheidung 27.10.2026:
Wahlbeteiligung je Ortsteil als Kennzahl der Kontextdaten, ohne Ergebnisse der Parteien je Gebiet).

Lizenz laut opendata.bonn.de: CC0 (Datensätze „Kommunalwahl und Integrationsratswahl 2025 Wahlergebnisse“ und
„Wahl- und Stimmbezirke“); die Stadtseite nennt dl-de/zero-2.0."""
import hashlib
import html
import json
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from . import config

VOTEMANAGER = "https://wahlen.bonn.de/wahlen/KW2025/05314000/praesentation/opendata.html"
FLAECHEN = {"wahlbezirke": "https://stadtplan.bonn.de/geojson?OD=4873",
            "stimmbezirke": "https://stadtplan.bonn.de/geojson?OD=4874"}
DATENSAETZE = ["https://opendata.bonn.de/dataset/c6a47ff2-f49c-455e-a7a0-455247539956",   # Wahlergebnisse
               "https://opendata.bonn.de/dataset/3af508a5-4016-4c8d-9828-c84f0630efa1"]   # Wahl- und Stimmbezirke
ENDUNGEN = (".csv", ".json", ".geojson", ".zip", ".xlsx")


def _laden(url, tries=4, pause=5):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": config.USER_AGENT})
            with urllib.request.urlopen(req, timeout=180) as r:
                return r.read(), r.geturl(), r.headers.get("Content-Type", "")
        except Exception as err:   # Verbindungsabbrüche kommen vor
            last = err
            time.sleep(pause * (i + 1))
    raise RuntimeError(f"{url}: {last}")


def _links(seite, basis):
    """Links auf Dateien (CSV, JSON, GeoJSON, ZIP, XLSX) in einer HTML-Seite, absolut."""
    out = []
    for href in re.findall(r'href="([^"]+)"', seite):
        u = urllib.parse.urljoin(basis, html.unescape(href))
        if urllib.parse.urlparse(u).path.lower().endswith(ENDUNGEN) or "geojson" in u.lower() or "download" in u.lower():
            out.append(u)
    return list(dict.fromkeys(out))


def _dateiname(url, typ):
    teil = urllib.parse.urlparse(url)
    name = Path(teil.path).name or "datei"
    if teil.query:
        name += "_" + re.sub(r"[^\w]+", "_", teil.query)
    if "." not in name:
        name += ".json" if "json" in typ else ".html" if "html" in typ else ".bin"
    return re.sub(r"[^\w.\-]+", "_", name)[:120]


def rohdaten(ziel=None):
    """Pipeline-Schritt `wahlen-rohdaten`: Quelldateien in ziel (Standard _quellen/wahlen2025) mit STAND.json."""
    ziel = Path(ziel or config.ROOT / "_quellen" / "wahlen2025")
    ziel.mkdir(parents=True, exist_ok=True)
    stand = {"abruf": datetime.now(timezone.utc).isoformat(timespec="seconds"), "dateien": [], "fehler": []}

    def ablegen(url, inhalt, typ, rolle):
        name = _dateiname(url, typ)
        (ziel / name).write_bytes(inhalt)
        stand["dateien"].append({"rolle": rolle, "url": url, "datei": name, "bytes": len(inhalt), "typ": typ,
                                 "sha256": hashlib.sha256(inhalt).hexdigest()})

    for rolle, url in FLAECHEN.items():
        try:
            inhalt, echt, typ = _laden(url)
            ok = json.loads(inhalt).get("features")
            if not ok:
                raise RuntimeError("keine Flächen in der Antwort")
            ablegen(echt, inhalt, typ, rolle)
        except Exception as err:
            stand["fehler"].append({"url": url, "fehler": str(err)})
    # Seiten mit Links: votemanager (offene Daten) und die Datensätze auf opendata.bonn.de (Ressourcen)
    seiten = [(u, 0) for u in [VOTEMANAGER] + DATENSAETZE]
    gesehen = set()
    while seiten:
        url, tiefe = seiten.pop(0)
        if url in gesehen or len(gesehen) >= 60:
            continue
        gesehen.add(url)
        try:
            inhalt, echt, typ = _laden(url)
        except Exception as err:
            stand["fehler"].append({"url": url, "fehler": str(err)})
            continue
        if "html" in typ:
            ablegen(echt, inhalt, typ, "seite")
            if tiefe < 2:   # Startseiten und Ressourcen-Seiten des Katalogs; nicht weiter
                text = inhalt.decode("utf-8", "replace")
                ziele = _links(text, echt) + [urllib.parse.urljoin(echt, h)
                                               for h in re.findall(r'href="(/dataset/[^"]+/resource/[^"/]+)"', text)]
                seiten += [(u, tiefe + 1) for u in ziele if "wahl" in u.lower() or "/resource/" in u or "stadtplan" in u]
        else:
            ablegen(echt, inhalt, typ, "datei")
        time.sleep(1)
    (ziel / "STAND.json").write_text(json.dumps(stand, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    n = sum(1 for d in stand["dateien"] if d["rolle"] != "seite")
    print(f"Wahlen 2025: {n} Dateien, {len(stand['fehler'])} Fehler → {ziel}")
    for f in stand["fehler"]:
        print("  Fehler:", f["url"], f["fehler"][:200])
    if not n:
        raise SystemExit("Wahlen 2025: keine Datei abrufbar")
