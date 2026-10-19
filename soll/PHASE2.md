# Soll-Modell – Phase 2: Anzeige in der Prozesslinie

Stand: 19.10.2026. Grundlage: `soll/PHASE1.md`.

## Umsetzung

| Baustein | Datei |
|---|---|
| Soll je Vorlage (Verfahren, Sicherheit, Grund, Passung, Gremienarten) | `pipeline/soll.py` (`lookup`), Feld `soll` im Export |
| Daten für Seite und Assistent | `data/export/bonn/soll.json` (`site_data`) |
| Rechtsgrundlagen als Links | `soll.rechtsgrundlagen` (nach `recht.py` aus „Bonn entscheidet“, MIT) |
| Abschnitt „Nach Regelwerk (Soll)“ im Vorgang | `site/app.js` (`showSoll`), `site/style.css` |
| Assistent | `hole_prozesslinie` liefert `soll_nach_regelwerk`; Systemprompt Änderung 16 |
| Glossar, Grenzen | `pipeline/glossar.py` (Status `soll`), Grenzen-Text der Seite, Lücken des Assistenten |
| Tests | `tests/test_soll.py` (9), `tests/js/tools.test.mjs` |

## Darstellung

- Verfahren mit Kurzbeschreibung; Zuordnung als „abgeleitet“ mit Grund und Sicherheit.
- Schritte nach Regelwerk mit „Wer“, Rechtsgrundlage und Link; eigene Ergänzungen als „Ergänzung der RIS-Karte“.
- Status je Schritt:
  - „Gremienart hat beraten (belegt)“, wenn Bezirksvertretung, Ausschuss oder Rat im Vorgang beraten haben;
  - „soll, keine Beratung dieser Gremienart“;
  - „soll, nicht abgeglichen“ für Schritte von Einwohner:innen, Fraktionen und Verwaltung.
- Abweichung als Befund: „Beraten hat auch …; das Regelwerk sieht das für dieses Verfahren nicht vor. Das ist ein Befund, keine Bewertung.“
- Akkordeons: „Wer entscheidet was?“ (Fragen mit Fundstelle; Abschnitt der Zuständigkeitsordnung je beratendem Ausschuss mit den Entscheidungsrechten, wörtlich), „Fristen vor einer Sitzung“, „Quelle des Soll-Modells“.
- Bürgerbrief: kein Soll angenommen, mit Begründung.

Geprüft im Browser auf Desktop (1440 px) und Mobil (390 px); axe-core ohne Verstöße.

## Grenzen

- Der Abschnitt der Zuständigkeitsordnung erscheint nur bei gleichem Gremiennamen. Der Ausschuss IX heißt in der Zuständigkeitsordnung „… Gesundheit und Senioren“, in den Daten „… Gesundheit, Wohnen und Senioren“; er wird nicht zugeordnet. Ausschüsse früherer Wahlperioden mit anderem Namen ebenfalls nicht.
- Welches Recht im Einzelfall greift, steht nur in der Vorlage.
- Der Status „belegt“ eines Soll-Schritts heißt nur, dass ein Gremium dieser Art beraten hat; Rolle und Reihenfolge sind nicht geprüft.

## Nächster Schritt

Phase 3 (nach Freigabe): Mitwirkung. Die Einflussregeln des Modells erscheinen unter „Selbst mitwirken“.
