# allris-bonn

Ratsinformationen der Stadt Bonn räumlich, zeitlich und nach Akteuren erschließen. Pilot: Ortsteil Endenich.

## Inhalt

- `CLAUDE.md` – Projektprompt v0.3 (Rolle, Datenquellen, Anforderungen, Phasen). Wird von Claude Code automatisch gelesen.
- `docs/` – Prompt-Versionen v0.1 und v0.3 zum Nachvollziehen.
- `phase0/` – Explorationsbericht (`BERICHT_phase0.md`), Audit-TSV der 522 Endenich-Kandidaten, Hilfstabellen, Abrufskript `fetch_papers.py`.
- `data/raw/` – Gremien und Verwaltungsbereiche aus der OParl-API (Abruf 17.10.2026). Die 24.912 Vorlagen (`papers.jsonl`, ca. 44 MB) liegen nicht im Repository und werden lokal geladen (siehe unten).
- `data/geo/` – Ortsteil- und Stadtbezirkspolygone (GeoJSON, WGS84).
- `pipeline/` – Datenpipeline (Phase 1): Abruf, Normalisierung in SQLite, Exporte, Prüfung.
- `data/export/endenich/` – Pilot-Export Endenich: Vorlagen (JSON, GeoJSON), Audit der Geokodierung, Stichprobe zur Prüfung von Hand (TSV); `data/export/audit_geokodierung_bonn.tsv` für ganz Bonn.
- `site/` – Webseite „Ratskarte Endenich“ (statisch, Leaflet); wird über GitHub Pages veröffentlicht.
- `data/LICENSE-DATA.md` – Lizenzen der Datendateien (CC0, CC BY 4.0 bzw. ODbL), getrennt vom MIT-Code.

## Start in Claude Code

```bash
cd allris-bonn-starter
git init
claude mcp add --transport http oparl-bonn https://oparl.bonn.machdenstaat.de/mcp
claude
```

Erster Prompt in der Sitzung:

> Beginne mit Phase 1 laut CLAUDE.md. Berücksichtige phase0/BERICHT_phase0.md; die Rohdaten liegen bereits in data/raw/ und data/geo/. Lege vor dem Programmieren einen kurzen Plan vor.

## Datenpipeline (Phase 1)

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pipeline all      # fetch → build → export → check
```

Einzelschritte: `fetch` (bzw. `fetch-papers`, `fetch-organizations`, `fetch-lite`, `fetch-streets`), `build`, `export`, `check`.

| Schritt | Ergebnis |
|---|---|
| `fetch` | `data/raw/papers.jsonl`, `organizations.json`, `verwaltungsbereiche.json` (OParl-API Stadt Bonn); `consultations_lite.jsonl` (Sitzung und TOP je Beratung aus OParl-Lite); `osm_streets.json` (benannte Straßen aus OSM, in Kacheln über Overpass; abgerufene Kacheln werden in `osm_tiles/` zwischengespeichert); Abrufzeitpunkte in `STAND.json` |
| `build` | `data/build/allris.sqlite`: Vorlage, Beratung, Sitzung, Tagesordnungspunkt, Organisation, Vorlagenbeziehung, Ort (Stufe A mit Ortsteil), Einreichende, Zuständigkeit; jede Zeile mit Quelle |
| `export` | `data/export/endenich/`: `vorlagen.json`, `vorlagen.geojson`, `audit_geokodierung.tsv`, `stichprobe_pruefung.tsv`; `data/export/audit_geokodierung_bonn.tsv` |
| `check` | Kennzahlen gegen den Phase-0-Bericht, Verknüpfungsquote, Datenschutzprüfung |

Abgeleitet und als solche gekennzeichnet (`method`, `evidence`) sind:
- **Einreichende**: aus der Vorlagenart (Verwaltung, Einwohner:innen) oder aus dem Titel (Fraktionen, Gruppen, Bezirksfraktionen, Koalition); die Quelle setzt `originatorOrganization` nicht.
- **Fachliche Zuständigkeit** bei der Sammelklasse „Co-Dezernat“: Amt der zugehörigen Stellungnahme der Verwaltung.
- **Ortsbezüge Stufe B** (Phase 2, vorläufig): Straßen-, Ortsteil- und Stadtbezirksnamen im Titel. Straßenverzeichnis aus OSM (Ortsteile je Straße per Verschneidung, gleichnamige getrennte Lagen als mehrdeutig) und ergänzend aus den Straßenpunkten der OParl-Locations. Mehrdeutige Straßen werden über den genannten Ortsteil oder die befasste Bezirksvertretung eingegrenzt; Folgevorlagen ohne eigenen Ortsbezug erben den der übergeordneten Vorlage. Stufe C (Volltext) ist zurückgestellt, bis die Lizenz der PDFs geklärt ist.

## Webseite

`site/` liest die Exporte aus `data/export/endenich/` und die Ortsteilflächen. Der Workflow `.github/workflows/static.yml` stellt bei jedem Push auf `main` `site/`, `data/export/` und `data/geo/` zusammen und veröffentlicht sie über GitHub Pages. Lokale Vorschau:

```bash
mkdir -p _site/data/geo && cp -r site/. _site/ && cp -r data/export _site/data/ && cp data/geo/*.geojson _site/data/geo/
python3 -m http.server -d _site 8000
```

Tests: `.venv/bin/python -m unittest discover tests`

## Lizenz

Code: MIT (`LICENSE`). Daten: siehe `data/LICENSE-DATA.md`.
