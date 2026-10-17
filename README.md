# allris-bonn – Starterpaket (Stand 17.10.2026)

Ratsinformationen der Stadt Bonn räumlich, zeitlich und nach Akteuren erschließen. Pilot: Ortsteil Endenich.

## Inhalt

- `CLAUDE.md` – Projektprompt v0.3 (Rolle, Datenquellen, Anforderungen, Phasen). Wird von Claude Code automatisch gelesen.
- `docs/` – Prompt-Versionen v0.1 und v0.3 zum Nachvollziehen.
- `phase0/` – Explorationsbericht (`BERICHT_phase0.md`), Audit-TSV der 522 Endenich-Kandidaten, Hilfstabellen, Abrufskript `fetch_papers.py`.
- `data/raw/` – Gremien und Verwaltungsbereiche aus der OParl-API (Abruf 17.10.2026). Die 24.912 Vorlagen (`papers.jsonl`, ca. 44 MB) liegen nicht im Repository und werden lokal geladen (siehe unten).
- `data/geo/` – Ortsteil- und Stadtbezirkspolygone (GeoJSON, WGS84).
- `data/LICENSE-DATA.md` – Lizenzen der Datendateien (CC0 bzw. ODbL), getrennt vom MIT-Code.

## Start in Claude Code

```bash
cd allris-bonn-starter
git init
claude mcp add --transport http oparl-bonn https://oparl.bonn.machdenstaat.de/mcp
claude
```

Erster Prompt in der Sitzung:

> Beginne mit Phase 1 laut CLAUDE.md. Berücksichtige phase0/BERICHT_phase0.md; die Rohdaten liegen bereits in data/raw/ und data/geo/. Lege vor dem Programmieren einen kurzen Plan vor.

## Rohdaten laden bzw. aktualisieren

```bash
python3 phase0/fetch_papers.py data/raw/papers.jsonl
```

## Lizenz

Code: MIT (`LICENSE`). Daten: siehe `data/LICENSE-DATA.md`.
