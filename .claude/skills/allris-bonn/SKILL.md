---
name: allris-bonn
description: Arbeitsweise im Repository allris-bonn (RIS-Karte Bonn) – Pipeline ausführen, Daten und Seite prüfen, Konventionen zu Quellen, Lizenzen und Datenschutz, Veröffentlichung über GitHub Pages und den Branch deploy. Verwenden bei jeder Änderung an pipeline/, site/, data/ oder den Workflows.
---

# allris-bonn – Arbeitsweise

Projektauftrag, Entscheidungen und offene Punkte stehen in `CLAUDE.md` (Abschnitte 2, 8, 9). Diese Datei beschreibt, **wie** im Repository gearbeitet wird.

## Grundsätze

- **Quellentreu:** Jede angezeigte Angabe ist auf ihr Quellobjekt (OParl-ID) rückführbar. Abgeleitetes wird gekennzeichnet (`method`, `confidence`, `evidence`; Prozessschritte mit Evidenzstatus belegt / abgeleitet / nicht_öffentlich / unklar). Lücken bleiben sichtbar, nichts wird erfunden.
- **Datenschutz:** keine Wohnadressen natürlicher Personen; Bürgeranträge nur auf Straßen- oder Ortsteilebene. `python -m pipeline check` bricht ab, wenn Hausnummern in Ortsangaben auftauchen.
- **Lizenzen:** OParl-API Stadt Bonn und Geodaten der Stadt CC0; OParl-Lite (Sitzungen, TOPs, Ergebnisse) CC BY 4.0; OSM ODbL. Neue Quelle → `config.SOURCES`, `data/LICENSE-DATA.md`, README, Quellen-Akkordeon der Seite.
- **Stabile Ausgaben:** Gebietsdateien, Feeds und Kalender tragen keine Erzeugungszeitpunkte, damit sich der Branch `deploy` nur bei Inhaltsänderungen ändert. Die Stichprobe zur Prüfung von Hand (`stichprobe_pruefung.tsv`) wird nie überschrieben.
- **Sprache:** Oberfläche, Kommentare und Commit-Nachrichten auf Deutsch, sachlich und ohne Superlative; Texte für Laien verständlich.

## Pipeline

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pipeline all            # fetch → build → export → check → verify → package
.venv/bin/python -m pipeline <schritt>      # fetch-papers | fetch-organizations | fetch-meetings | fetch-plans | fetch-lite | fetch-streets | gazetteer | build | export | check | verify | package
```

| Modul | Aufgabe |
|---|---|
| `fetch.py`, `net.py` | Abruf mit Wiederholung; Rohdaten in `data/raw/` (Abrufzeitpunkte in `STAND.json`) |
| `build.py` | SQLite `data/build/allris.sqlite`: Vorlagen, Beratungen, Sitzungen, TOPs, Orte, Ortsbezüge, Akteure |
| `geocode.py`, `geo.py`, `plans.py` | Stufe B (Straßen, Ortsteile, Bezirke, Bebauungspläne), Point-in-Polygon, Überschneidungen |
| `actors.py`, `process.py` | Einreichende und Zuständigkeit; Prozessschritte, Stand, Wege |
| `export.py`, `publish.py` | JSON je Gebiet, Zeit- und Wegeaggregate, Audits (TSV); Feeds, Kalender, GeoJSON, DCAT |
| `check.py`, `verify.py` | Kennzahlen, Datenschutz; Abgleich von Stichproben mit der OParl-API; Zip-Paket |

Im Repository liegen: Gremien, Ämter, Sitzungen, Wahlperioden (`data/raw/*.json`), Flächen und Straßenverzeichnis (`data/geo/`), Pilot Endenich und Audits (`data/export/`). Erzeugt und nicht eingecheckt: `data/export/bonn/`, Zip, Datenbank.

## Prüfen vor jedem Push

1. `.venv/bin/python -m unittest discover tests` und `node --check site/app.js site/timeline.js`
2. Bei Datenänderungen: `build`, `export`, `check`; Kennzahlen mit dem vorigen Stand vergleichen
3. Bei Oberflächenänderungen: Vorschau bauen und im Browser prüfen

```bash
mkdir -p _site/data/geo && cp -r site/. _site/ && cp -r data/export _site/data/ \
  && cp data/LICENSE-DATA.md _site/data/ && cp data/geo/*.geojson _site/data/geo/
python3 -m http.server -d _site 8765
```

   Mit Playwright (Chromium vorinstalliert) Desktop 1440 px, mittlere Breite 1024 px und Mobil 390 px prüfen; axe-core (`wcag2a`, `wcag2aa`) darf keine Verstöße melden. Typische Fälle: Gebietswechsel (auch schnell hintereinander), URL-Zustand (`?gebiet=…&von=…&bis=…#Drucksache`), Esc und Fokus, Zeitleiste per Tastatur.

## Veröffentlichung

- Arbeitsbranch `claude/new-session-r8w4my`; nach jedem Merge von `main` neu ansetzen; jede Änderung als Pull Request.
- `.github/workflows/pages.yml`: Abruf (mit Rückfall auf den letzten Stand) → Build → Export → Prüfung → Paket → GitHub Pages und Branch `deploy` (fertige Seite plus `.htaccess`, ohne Zip).
- `SITE_URL` (Umgebungsvariable) bestimmt absolute Links in Feeds, Kalender und DCAT.
- Nach dem Merge die veröffentlichte Seite im Browser prüfen.
