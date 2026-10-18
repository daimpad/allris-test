# allris-bonn – Ratskarte Bonn

Ratsinformationen der Stadt Bonn räumlich, zeitlich und nach Akteuren erschließen: Wo liegt eine Vorlage, wo steht das Verfahren, wer ist beteiligt? Jede Angabe ist auf ihr Quellobjekt rückführbar; abgeleitete Angaben sind gekennzeichnet. Pilot und erste Auslieferung: Ortsteil Endenich.

**Seite:** https://daimpad.github.io/allris-test/ (vorläufige Fassung) · **Datenpaket:** https://daimpad.github.io/allris-test/data/export/allris-bonn-export.zip

## Was die Seite zeigt

- **Wo?** Karte und gleichwertige Liste je Ortsteil, je Stadtbezirk (Vorlagen ohne genaueren Ort) und für Vorlagen ohne Ortsbezug (je Jahr). Jeder Ortsbezug nennt Stufe, Methode, Konfidenz und Fundstelle.
- **Wann?** Prozesslinie je Vorlage: Beratungen mit Gremium, Datum, Tagesordnungspunkt und Ergebnis (wörtlich aus der Quelle, mit allgemeiner Erläuterung); Folgevorlagen und übergeordnete Vorlagen.
- **Wer?** Federführendes Amt; bei der Sammelklasse „Co-Dezernat“ zusätzlich das fachlich zuständige Amt; befasste Gremien; Einreichende.
- Filter: Gebiet, Stichwort, Vorlagenart, Zeitraum, Amt, Gremium, Stand des Verfahrens, Konfidenz der Verortung. Direktlinks: `?gebiet=ortsteil:endenich#191010`.
- „Verortung falsch?“ öffnet ein vorausgefülltes Issue.

## Datenquellen und Lizenzen

| Quelle | Inhalt | Lizenz |
|---|---|---|
| [OParl-API der Stadt Bonn](https://www.bonn.sitzung-online.de/oparl/bodies/1) (ALLRIS) | Vorlagen, Beratungsfolge, Gremien, Ämter (`underDirectionOf`), Orte (`location`) – Primärquelle | CC0 1.0; PDFs sind vom Datensatz ausgenommen |
| [OParl-Lite Bonn](https://oparl.bonn.machdenstaat.de/) (machdenstaat), GraphQL | Sitzung, Tagesordnungspunkt und Ergebnis je Beratung | CC BY 4.0 |
| Ortsteil- und Bezirksflächen der Stadt Bonn ([Open-Data-Portal](https://opendata.bonn.de/dataset/flächen-der-ortsteile)) | 51 Ortsteile, 4 Stadtbezirke | CC0 1.0 |
| OpenStreetMap (Overpass API) | Straßennamen und -verläufe für das Straßenverzeichnis | ODbL 1.0, © OpenStreetMap-Mitwirkende |

Code: MIT (`LICENSE`). Daten: `data/LICENSE-DATA.md` (je Datei).

## Datenstand

Die Seite wird täglich neu erzeugt (Workflow `pages.yml`, 04:17 UTC) und bei jedem Push auf `main`. Die Abrufzeitpunkte je Quelle stehen im Footer der Seite und in `meta.sources` jedes Exports.

## Geokodierung

| Stufe | Methode | Konfidenz |
|---|---|---|
| A | `location` aus der OParl-API (ein Punkt je Straße; Ortsteil per Point-in-Polygon) | hoch |
| B | Straßen-, Ortsteil- und Stadtbezirksnamen im Titel; Straßenverzeichnis aus OSM mit Ortsteilen je Straße; Eingrenzung mehrdeutiger Straßen über genannten Ortsteil oder befasste Bezirksvertretung; Folgevorlagen erben den Ortsbezug der übergeordneten Vorlage | mittel, bei Mehrdeutigkeit oder Widerspruch niedrig |
| C | Volltext mit Sprachmodell | zurückgestellt, bis die Lizenz der PDFs geklärt ist |

Prüfung: `python -m pipeline check` gleicht Stufe B mit Stufe A ab (je Vorlage, unabhängig, da OSM-Geometrie). `python -m pipeline verify` lädt eine Stichprobe von 50 Vorlagen erneut aus der OParl-API und vergleicht die Felder (`data/export/verifikation_oparl.tsv`). Audit aller Ortsbezüge: `data/export/audit_geokodierung_bonn.tsv`.

## Grenzen

- Rund 57 % der Vorlagen haben keinen erkennbaren Ortsbezug im Titel; sie stehen unter „ohne Ortsbezug“.
- Stufe B wertet nur Titel aus; Orte, die nur im Dokument stehen, fehlen. Gleichnamige Straßen ohne eingrenzenden Hinweis bleiben mehrdeutig.
- Die Punkte der Stufe A stehen für die ganze Straße, nicht für das Objekt; bei langen Straßen kann der Ortsteil abweichen.
- Einreichende stehen in der Quelle nicht strukturiert; sie werden aus Vorlagenart und Titel abgeleitet (bei rund 60 % der Anträge und Anfragen erkennbar). Namen von Privatpersonen werden nicht ausgewiesen.
- Die Stichprobe von 50 Endenicher Vorlagen (`data/export/endenich/stichprobe_pruefung.tsv`) ist noch nicht von Hand geprüft.

## Pipeline

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pipeline all      # fetch → build → export → check → verify → package
```

| Schritt | Ergebnis |
|---|---|
| `fetch` (`fetch-papers`, `fetch-organizations`, `fetch-lite`, `fetch-streets`) | Rohdaten in `data/raw/` (nicht im Repository, außer Gremien und Ämtern); Abrufzeitpunkte in `STAND.json` |
| `gazetteer` | `data/geo/strassen_bonn.json`: Straßenverzeichnis aus den OSM-Rohdaten (im Repository, damit die Aktualisierung ohne Overpass auskommt) |
| `build` | `data/build/allris.sqlite`: Vorlage, Beratung, Sitzung, Tagesordnungspunkt, Organisation, Vorlagenbeziehung, Ort, Ortsbezug (Stufe, Methode, Konfidenz, Fundstelle), Einreichende, Zuständigkeit |
| `export` | `data/export/endenich/` (Pilot, im Repository) und `data/export/bonn/` (je Ortsteil, Bezirk, Jahr; wird bei der Veröffentlichung erzeugt); Audit-TSV |
| `check`, `verify` | Kennzahlen, Abgleich B/A, Datenschutzprüfung; Abgleich mit der OParl-API |
| `package` | `data/export/allris-bonn-export.zip` |

Lokale Vorschau der Seite:

```bash
mkdir -p _site/data/geo && cp -r site/. _site/ && cp -r data/export _site/data/ \
  && cp data/LICENSE-DATA.md _site/data/ && cp data/geo/*.geojson _site/data/geo/
python3 -m http.server -d _site 8000
```

Tests: `.venv/bin/python -m unittest discover tests`

## Aufbau des Repositorys

- `pipeline/` – Abruf, Aufbereitung, Geokodierung (`geocode.py`), Akteure (`actors.py`), Export, Prüfung
- `site/` – statische Seite (Leaflet, OSM-Kacheln), WCAG 2.1 AA geprüft mit axe-core
- `data/` – Gremien, Ämter, Flächen, Straßenverzeichnis, Pilot-Export, Lizenzen
- `phase0/` – Explorationsbericht und Audit der Phase 0
- `CLAUDE.md`, `docs/` – Projektprompt und frühere Fassungen
- `.github/` – Workflows (Veröffentlichung, Tests) und Issue-Vorlagen

Mitmachen: siehe `CONTRIBUTING.md`.
