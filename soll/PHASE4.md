# Soll-Modell – Phase 4: Prüfung

Stand: 19.10.2026. Grundlage: `soll/PHASE1.md` bis `soll/PHASE3.md`.

## Stichprobe

`data/export/soll/stichprobe_soll.tsv` enthält 30 Vorgänge mit Stichtag 19.10.2026. Die Datei wird nie überschrieben; erzeugt hat sie `soll/phase4/stichprobe.mjs`.

**Auswahl** (geschichtet, fester Startwert):
- beide Befunde;
- ein Vorgang ohne Soll;
- zwei Vorgänge nur im Beirat;
- je Verfahren ein Vorgang;
- vier mit Sicherheit „mittel“;
- der Rest zufällig ab 2025.

**Spalten** je Vorgang:
- Angaben: Titel ohne Hausnummern (in allen Titeln, auch bei Grundstücken in Verwaltungsvorlagen), Stand, Beratungen, Verfahren, Sicherheit, Grund, Gremien Ist und Soll, Passung, Befund, Einordnung und Hinweise zur Mitwirkung, Link ins Ratsinformationssystem;
- leer für die Prüfung von Hand: `pruef_verfahren`, `pruef_befund`, `pruef_mitwirken`, `pruefvermerk`.

## KI-Vorprüfung

`data/export/soll/vorpruefung_soll.tsv`. Die Vorprüfung hat eine KI (Claude) vorgenommen; sie ersetzt nicht die Prüfung von Hand.

| Prüfgegenstand | ja | teilweise | nein | entfällt |
|---|---|---|---|---|
| Verfahren | 27 | 3 | 0 | – |
| Passung und Befund | 26 | – | 1 | 3 |
| Mitwirkung | 29 | 1 | 0 | – |

- **Verfahren, teilweise (3):** alle mit Sicherheit „mittel“. Das entscheidende Gremium ist unklar, oder mehrere Gremien entscheiden; für Verwaltungsvorlagen in der Bezirksvertretung kennt das Modell kein eigenes Verfahren.
- **Befund, nein (1):** 230577. Ausschuss und Rat berieten spätere Große Anfragen von Fraktionen unter derselben Stammnummer, nicht die Einwohnerfrage selbst. Der zweite Befund, 221004, trifft zu: Die Bezirksvertretung hat die Einwohnerfrage an den Schulausschuss verwiesen.
- **Mitwirkung, teilweise (1):** 200556. Der Hinweis auf die Offenlage passt bei einer vereinfachten Änderung (§ 13 BauGB) nur bedingt.

## Korrekturen aus der Vorprüfung (in diesem Schritt umgesetzt)

| Fehler | Beispiel | Korrektur |
|---|---|---|
| Eine Eilentscheidung, die der Rat genehmigt hat, galt als „unklar“ | 200633 | Genehmigung durch den Rat → abgeschlossen, beschlossen |
| Kenntnisnahme oder Erledigung schloss den Vorgang nur beim Stand „beraten, ohne Entscheidung“ | 221004 | gilt bei jedem Stand, sofern keine entscheidende Beratung aussteht (wie im Original) |
| Eine Mitteilung ohne Termin galt als „offen“ | 253869 | Mitteilung ohne Termin → zur Kenntnis (wie im Original) |
| Passung „ohne Beratung“ bei 297 Vorgängen, die nur in Beiräten beraten wurden | 190402 | eigener Wert „nur Beirat“ mit Hinweis, dass das Modell Beiräte nicht abbildet |

Wirkung in Endenich (574 Vorlagen):

| Status | vorher | nachher |
|---|---|---|
| abgeschlossen | 442 | 474 |
| unklar | 90 | 59 |
| offen | 21 | 20 |
| vertagt | 14 | 14 |
| ohne Soll | 7 | 7 |

## Nachtrag: Befund nur aus dem Hauptweg (umgesetzt nach Freigabe, 19.10.2026)

Zuordnung und Abgleich zählen nur den Hauptweg eines Vorgangs (`hauptweg` in `pipeline/soll.py`):
- Spätere Fragen und Berichte anderer Art zählen nicht: Anfragen, Einwohnerfragen, Mitteilungen, Informationsbriefe. So regelt es auch das Original (`is_followup`, `current_main`).
- Stellungnahmen und Änderungsanträge gehören zu der Vorlage, die ihnen vorausgeht.
- Andere Folgevorlagen setzen den Weg fort, etwa eine Dringlichkeitsentscheidung zu einer Beschlussvorlage.

Ein erster, weiter gefasster Entwurf (alle Vorlagen anderer Art ausschließen, alle Stellungnahmen einschließen) hätte zwei Fehler erzeugt:
- Bei 230577 wäre der Scheinbefund geblieben, weil die Stellungnahmen zu den Großen Anfragen weiter gezählt hätten.
- Bei 261798 wäre die Dringlichkeitsentscheidung herausgefallen, die die Beschlussvorlage fortführt.

Wirkung auf alle 14.104 Vorgänge:

| Änderung | Vorgänge |
|---|---|
| Befund entfällt (230577) | 1; es bleibt 221004 |
| Verfahren „Antrag im Rat“ → „Antrag in der Bezirksvertretung“ (spätere Kleine Anfrage oder Mitteilung zum Stand der Umsetzung in Rat oder Ausschuss; geprüft an 190300, 211355) | 11 |
| geänderte Gremien Ist ohne Wirkung auf Verfahren oder Passung | 61 |

Die Stichprobe bleibt unverändert. Ihre Zeile zu 230577 zeigt noch den alten Befund; die Prüfung von Hand bewertet ihn mit dem neuen Stand.

## Prüfung

- Tests:
  - Python: `tests/test_soll.py`, `tests/test_paket.py`;
  - JavaScript: `tests/js/mitwirken.test.mjs` (6), `tests/js/tools.test.mjs`.
- Browser auf Desktop (1440 px) und Mobil (390 px): axe-core ohne Verstöße.
- Datenpaket: Stichprobe, Vorprüfung und Berichte der Phasen 1 bis 4 (`berichte/soll/`); Lizenzzeile in `data/LICENSE-DATA.md`.

## Belege der Ergänzungen (geprüft 19.10.2026)

`soll/pruefung/belege_ergaenzungen.tsv` enthält 13 Belege (10 Schritte, 3 Korrekturen) mit dem Wortlaut der Fundstelle und der KI-Vorprüfung. Der Auftraggeber hat 8 bestätigt und 5 als teilweise eingestuft; diese sind präzisiert:
- a+aus: Beleg um die Zuständigkeitsordnung ergänzt;
- d+aus, d+bv: Beleg um GeschO § 7 Abs. 5 ergänzt;
- a+bv, e+bv: Anhörung nur in Angelegenheiten nach BezS § 9.

## Prüfung der Stichprobe von Hand (begonnen 19.10.2026)

Die Prüfvermerke stehen in `data/export/soll/stichprobe_soll.tsv` (Spalten `pruef_*`, `pruefvermerk`).

| Vorgänge | Ergebnis | Folge |
|---|---|---|
| 1–6 | bestätigt; bei 200556 Mitwirkung teilweise | Der Hinweis auf die Offenlage erscheint nur noch bei offenen oder vertagten Verfahren (`regel_bedingungen` in `data/soll/ergaenzungen.json`) |
| 7–12 | bestätigt | 221004: Befund bleibt (Verweisung an den Schulausschuss); 230577: kein Befund richtig (Stand nach Hauptweg) |
| 13–18 | bestätigt | 241058, 253500: Sicherheit „mittel“ reicht; kein eigenes Verfahren für Verwaltungsvorlagen zur Entscheidung in der Bezirksvertretung |

## Noch zu tun (Auftraggeber)

- Stichprobe von Hand prüfen (Spalten `pruef_*`, `pruefvermerk`).
- Über die offene Empfehlung entscheiden.
- Kontakt zum Autor von „Bonn entscheidet“; ein Hinweis auf die zwei Merkmale der Zuständigkeitsordnung (Phase 0) ist möglich.
