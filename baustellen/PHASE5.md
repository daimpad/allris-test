# Phase 5 – Auslieferung

Stand: 19.10.2026.

## Datenpaket (`python -m pipeline package`, täglich im Workflow)

| Inhalt | Datei im Paket |
|---|---|
| Geltungsbereiche und Änderungsprotokoll der Pläne | `geo/bebauungsplaene_bonn.geojson`, `geo/bebauungsplaene_protokoll.tsv` |
| Planregister mit Verfahrensschritten (abgeleitet) | `bonn/plaene.json` |
| Audit B3 (Vorlage ↔ Plan) | `audit_bebauungsplaene.tsv`, `endenich/audit_bebauungsplaene.tsv` |
| Baustellen für die Seite | `bonn/baustellen.json` |
| Audit Kandidaten mit Kriterien und Prüfvermerk (täglich neu) | `baustellen_kandidaten.tsv` |
| Stichprobe (30) und KI-Vorprüfung | `baustellen/stichprobe_kandidaten.tsv`, `baustellen/vorpruefung_kandidaten.tsv` |
| Ereignisse und Abrufstand des Archivs | `baustellen_archiv/protokoll.tsv`, `baustellen_archiv/STAND.json` |
| Berichte der Phasen 0 bis 5 | `berichte/` |

Lizenzen stehen je Datei in `LICENSE-DATA.md`. `LIESMICH.txt` beschreibt Inhalt und Grenzen. `bonn/dcat.jsonld` nennt Planregister und Baustellen als eigene Distributionen (CC0). Tests: `tests/test_paket.py` prüft Inhalt und Lizenzzeilen.

## Offene Punkte aus dem Auftrag (Abschnitt 8)

| Punkt | Stand |
|---|---|
| Ressourcen-URLs und Felder | geklärt (Phase 0) |
| Nummernschema, Änderungspläne | geklärt (Phase 1: Grundnummer, Änderungen, Mehrdeutigkeit mit Konfidenz niedrig) |
| Bauherr bzw. Träger | erfasst (Feld `traeger`); andere Träger getrennt |
| Historische Baustellendaten | Anfrage an opendata@bonn.de vom Auftraggeber versandt (19.10.2026), Antwort offen |
| Schwelle der Freischaltung | Vorschlag 70 % plausibel je Stufe; „hoch“ sichtbar; Prüfung von Hand abgeschlossen (6/6 plausibel), Hinweis „vorläufig“ entfallen (19.10.2026) |
| Lizenz je Datensatz | Bebauungspläne CC0 (Katalog der Stadt); Baustellen CC0 laut Auftraggeber, Bestätigung der Stadt mit der Anfrage |

## Noch zu tun (Auftraggeber)

- Workflow „Baustellen archivieren“ einmal von Hand starten (Branch `archiv` entsteht).
- Stichprobe `baustellen/stichprobe_kandidaten.tsv` von Hand prüfen (Spalte `pruefvermerk`); danach Regeln kalibrieren und über „hoch“ endgültig entscheiden.
