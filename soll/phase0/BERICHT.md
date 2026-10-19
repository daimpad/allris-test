# Soll-Modell – Phase 0: Prüfung von Verfahrensmodell und Zuständigkeitsordnung

Stand: 19.10.2026. Quelle: `anster2025/bonn-entscheidet`, Commit `26641f7` (MIT): `data/verfahren.json`, `data/zustaendigkeitsordnung.json`. Kein Produktionscode; Skripte in `scripts/`, Ergebnisse in `out/`.

## 1. Zuordnung unserer Vorlagen zu den Verfahren

Die Regeln aus `einordnung.py` (Funktion `assign`) wurden unverändert übertragen. Grundlage sind Vorlagenart, beratende Gremienarten und Titel. Die Beratungsfolge vom Deckblatt fehlt bei uns. Ein Vorgang umfasst alle Vorlagen einer Stammnummer.

| Kennzahl | Wert |
|---|---|
| Vorlagen / Vorgänge (2019–2026) | 24.915 / 14.104 |
| Zuordnung „hoch“ / „mittel“ | 12.581 (89 %) / 1.523 (11 %) |
| ohne eigenes Verfahren | 165 (Bürgerbrief 159, Stellungnahme ohne Hauptvorlage 6) |
| größte Gruppen | Beschlussvorlage 3.008, Mitteilung 2.986, Bürgerantrag 1.651, Ausschussentscheidung 1.340, Große Anfrage 1.302, Antrag in der BV 1.231 |
| Einwohnerantrag, Bürgerbegehren | 0 – im Modell vorhanden, keine eigene Vorlagenart in den Daten |

**Passung der Gremien:** Gezählt wird, ob die tatsächlich beratenden Gremienarten (Bezirksvertretung, Ausschuss, Rat) im Soll des zugeordneten Verfahrens vorkommen.

- passt: 11.451 (81 %)
- weicht ab: 2.356 (17 %)
- ohne Beratung: 297 (2 %)

Die Abweichungen gehen fast ganz auf vier Lücken des Modells zurück, nicht auf Fehler in den Daten:

| Lücke | Fälle | Regel, die sie schließt |
|---|---|---|
| Große Anfragen in Bezirksvertretungen und Fachausschüssen (Modell: nur Fragestunde im Rat) | 1.168 | GeschO § 22 Abs. 1 (sinngemäß für Ausschüsse), § 23 (Bezirksvertretungen) |
| Anträge in Fachausschüssen (Modell „Antrag im Rat“ ohne Ausschuss) | 745 | GeschO § 22 Abs. 1, § 7 Abs. 6 (Verweisung) |
| Dringlichkeitsanträge in Bezirksvertretung oder Ausschuss | 244 | GeschO § 22 Abs. 1, § 23 |
| Kleine Anfragen mit Beratung (Modell: nur schriftliche Antwort) | 134 | GeschO § 12 Abs. 3 |
| Ausschussentscheidung mit Anhörung der Bezirksvertretung | 63 | BezS § 9 |

## 2. Belege (Rechtsgrundlagen)

`verfahren.json` enthält 193 Belege, davon 114 verschiedene. Verteilung: Geschäftsordnung des Rates 118, Hauptsatzung 26, GO NRW 24, Bezirkssatzung 23, Zuständigkeitsordnung 21, Satzung zum Einwohnerantrag 17, BauGB 3, Leitlinien 1.

**Stichprobe:** 20 Belege, je Gesetz mindestens einer, sonst zufällig mit festem Startwert. Geprüft gegen die Texte auf bonn.de, recht.nrw.de und gesetze-im-internet.de, abgerufen am 19.10.2026 (`out/belege_stichprobe.tsv`). Die Vorprüfung hat eine KI (Claude) vorgenommen; sie ersetzt nicht die Prüfung von Hand.

- **18 bestätigt.**
- **2 teilweise:**
  - GeschO § 7 Abs. 5 trägt die Folge „Antrag geht in die nächste Sitzung“ nicht ausdrücklich; die Folge ist abgeleitet.
  - GeschO § 22 Abs. 8 nennt den Unterausschuss des Hauptausschusses Finanzen und Beteiligungsmanagement, nicht den „Finanzausschuss“.
- **0 falsch.**
- **Hinweis:** Das BauGB spricht heute von „Veröffentlichung im Internet“, das Modell von „Offenlage“.

## 3. Zuständigkeitsordnung

Abgleich mit der Seite der Stadt („Stand: 9. Juli 2026“, gleicher Stand wie in der Datei; `out/zusto_abgleich.tsv`):

- 18 Ausschüsse, 333 Rechte auf beiden Seiten.
- Art des Rechts in allen 333 Fällen gleich.
- Inhalt in 331 Fällen wortgleich.
- **2 Abweichungen** (VII 2.16, VIII 1.10): Die Seite ergänzt „Empfehlung an die zuständige Bezirksvertretung“, in der Datei steht dort `an_bezirksvertretung: false`. Das Merkmal ist an diesen zwei Stellen falsch.
- Abschnitt XVIII („Alle Ausschüsse“) ist auf der Seite ein Fließtext ohne Einzelrechte; die Datei führt ihn ohne Rechte. Das ist korrekt.

## 4. Bewertung

Die Übernahme trägt:
- Die Zuordnung deckt 99 % der Vorgänge mit einem eigenen Verfahren ab.
- Die Belege der Stichprobe sind belastbar.
- Die Zuständigkeitsordnung entspricht bis auf zwei Merkmale der amtlichen Fassung.

Zu beachten:
- Das Modell bildet den Rat ab; für Ausschüsse und Bezirksvertretungen fehlen eigene Wege für Anträge und Anfragen.
- Ohne Ergänzung erschiene ein Sechstel der Vorgänge als „Abweichung vom Soll“, obwohl sie regelkonform ablaufen.

## 5. Empfehlung für Phase 1

1. Feste Kopie beider Dateien nach `data/soll/`, mit Quelle, Commit und MIT-Hinweis.
2. Eigene, gekennzeichnete Ergänzungen in einer getrennten Datei:
   - Wege für Antrag, Große Anfrage und Dringlichkeitsantrag in Ausschuss und Bezirksvertretung;
   - Kleine Anfrage mit Beratung;
   - Bürgerbrief;
   - Anhörung der Bezirksvertretung bei Ausschussentscheidungen.

   Jede Ergänzung erhält einen Beleg.
3. Die zwei Merkmale `an_bezirksvertretung` korrigieren und die Bezeichnung in GeschO § 22 Abs. 8 übernehmen; beides als eigene Korrektur kennzeichnen.
4. Erst danach Soll-Ist-Abgleich und Anzeige (Phase 2). Abweichungen erscheinen als Befund, nicht als Fehler.

## Dateien

- `scripts/zuordnung.py` → `out/zuordnung.tsv` (je Vorgang: Verfahren, Sicherheit, Grund, Gremien Ist/Soll, Passung; ohne Titel), `out/zuordnung_summary.json`
- `scripts/belege.py` → `out/belege_stichprobe.tsv` (mit KI-Vorprüfung)
- `scripts/zusto_abgleich.py` → `out/zusto_abgleich.tsv`
