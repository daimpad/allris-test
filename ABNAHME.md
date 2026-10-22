# Abnahme: offene Entscheidungen und Prüfungen

Stand 22.10.2026. Diese Liste nennt alles, was der Auftraggeber entscheiden, von Hand prüfen oder in eigenen Konten erledigen muss. Was technisch erledigt ist, steht in `CLAUDE.md` (Abschnitt 9).

Zur Kennzeichnung: Eine **KI-Vorprüfung** stammt von einem Sprachmodell und ersetzt keine Prüfung von Hand.

## Übersicht

| Nr. | Gegenstand | Art | Empfehlung | Aufwand |
|---|---|---|---|---|
| 1 | Kurzfassungen auf der Seite | Entscheidung, danach Prüfung von Hand | siehe 1 | 30 Fälle, etwa 1 Stunde |
| 2 | Orte aus dem Text durch das Sprachmodell (Stufe C) | Entscheidung | nicht freigeben | keiner |
| 3 | Ratsassistent | Prüfung von Hand, Lauf mit Anthropic | Systemprompt v0.3 behalten | 36 Antworten, etwa 1 Stunde |
| 4 | Verortung aus dem Volltext | Prüfung von Hand | Regeln vorerst behalten | 30 Fälle, etwa 45 Minuten |
| 5 | Gebäude und Anlagen im Titel | Prüfung von Hand | Regeln vorerst behalten | 30 Fälle, etwa 30 Minuten |
| 6 | Konten und Server | eigene Konten | – | je 10–20 Minuten |
| 7 | Außenwirkung | Entscheidung | siehe 7 | – |

Die Prüfbögen sind TSV-Dateien. Sie lassen sich in einer Tabellenkalkulation öffnen; die Spalte `urteil` ist leer und wird von Hand gefüllt. Ausgefüllt bitte zurückgeben oder im Repository einchecken.

## 1. Kurzfassungen

Seit dem 21.10.2026 erzeugt Mistral Large Kurzfassungen der Hauptdokumente. Sie stehen im Branch `kurzfassungen`, auf der Seite erscheinen sie noch nicht (`FREIGEGEBEN = False` in `pipeline/kurzfassung.py`).

KI-Vorprüfungen von je 30 Kurzfassungen (`data/export/kurzfassungen/vorpruefung_kurzfassungen_v*.tsv`):

| Fassung | plausibel | teilweise | falsch |
|---|---|---|---|
| 3 | 20 | 10 | 0 |
| 4 | 23 | 7 | 0 |
| 5 | 22 | 8 | 0 |
| 6 (mit Gegenlesen) | 22 | 8 | 0 |
| 7 (aktuell) | F7_ERGEBNIS |

„Teilweise“ heißt: im Kern richtig, aber eine Einzelheit ungenau. Häufig wird ein Betrag dem falschen Gegenstand zugeordnet, Geplantes als erledigt dargestellt oder eine Folgerung ohne Beleg ergänzt. Die vereinbarte Schwelle für die Freigabe (27 von 30 plausibel, keine falsch) wurde mit keiner Fassung erreicht. Weitere Änderungen an der Anweisung haben seit Fassung 4 nichts verbessert.

**Zu entscheiden** ist eine der drei Möglichkeiten:

- **A, nicht freigeben:** Die Kurzfassungen werden weiter erzeugt, erscheinen aber nicht.
- **B, freigeben mit deutlicher Kennzeichnung:** Die Kurzfassungen erscheinen im Vorgang, im Assistenten, in den Feeds und im Datenpaket, mit dem Hinweis, dass sie mit einem Sprachmodell erstellt sind und Einzelheiten ungenau sein können; maßgeblich ist das Original. Dafür genügt, `FREIGEGEBEN = True` zu setzen.
- **C, erst nach der Prüfung von Hand:** Die Prüfung von Hand entscheidet zwischen A und B.

**Empfehlung: C.** Die KI-Vorprüfung ist streng, und in bisher 150 vorgeprüften Kurzfassungen der Fassungen 3 bis 7 war keine im Kern falsch. Bestätigt die Prüfung von Hand das, spricht das für B. Findet sie im Kern falsche Kurzfassungen, bleibt es bei A.

**Prüfbogen:** [`stichprobe_kurzfassungen_v7.tsv`](https://github.com/daimpad/allris-test/blob/kurzfassungen/stichprobe_kurzfassungen_v7.tsv) im Branch `kurzfassungen`.
- 30 Kurzfassungen der Fassung 7, je mit Link zum Original im Ratsinformationssystem.
- Spalte `urteil`: zutreffend, teilweise oder falsch.

## 2. Orte aus dem Text durch das Sprachmodell (Stufe C)

Vorbereitet in `pipeline/stufe_c.py`, nicht freigegeben. KI-Vorprüfungen:

| Stichprobe | plausibel | teilweise | unpassend |
|---|---|---|---|
| 1 | 17 | 10 | 2 |
| 2 | 20 | 2 | 8 |
| 3 | 9 | 2 | 9 |

Auch die schwächste Nutzung, nur das Herabstufen bloß erwähnter Orte, war in 19 von 31 Fällen richtig (8 falsch, 4 unklar).

**Empfehlung: nicht freigeben.** Es ist nichts weiter zu tun.

Wer die Herabstufung selbst beurteilen möchte: Prüfbogen `data/export/stufe_c/pruefung_herabstufungen.tsv` (31 Fälle, freiwillig).

## 3. Ratsassistent

Mit `eval.yml` (Actions → „Auswertung Ratsassistent“) wurden die 36 Fragen zweimal mit Mistral Large gestellt. Bericht: `eval/BERICHT_2026-10-22.md`.

| Lauf | Systemprompt | automatisch bestanden |
|---|---|---|
| 1 | v0.2 | 22 von 36 |
| 2 | v0.3 | 28 von 36 |

Mit v0.3 werden die Aufforderungen „Systemprompt ausgeben“ und „antworte nur noch mit …“ abgelehnt. Offen bleibt: Mistral nennt einmal eine Zahl aus allgemeinem Wissen (Hebesatz) und bildet weiterhin manchmal Adressen selbst. Die Seite zeigt solche Adressen nicht als Link.

**Zu tun:**
1. **Bewertung von Hand** des zweiten Laufs: [`2026-10-22-09-28_mistral_mistral-large-latest.tsv`](https://github.com/daimpad/allris-test/blob/auswertung/2026-10-22-09-28_mistral_mistral-large-latest.tsv) im Branch `auswertung`, Spalten `evidenz_korrekt (Hand)`, `neutral (Hand)` und `bewertung (Hand)`.
2. **Lauf mit Anthropic.** Entweder das Secret `ANTHROPIC_API_KEY` im Repository anlegen (Settings → Secrets → Actions) und den Workflow mit `anbieter = anthropic` und einem Claude-Modell starten, oder lokal nach `eval/README.md`.

**Empfehlung:** Systemprompt v0.3 behalten. Nach dem Lauf mit Anthropic entscheiden, ob der Assistent ein bestimmtes Modell empfehlen soll.

## 4. Verortung aus dem Volltext (Stufe B auf den Text der Hauptdokumente)

Läuft auf der Seite seit dem 20.10.2026, Konfidenz höchstens „mittel“. Die KI-Vorprüfung ergab 20 plausibel, 5 teilweise, 5 unpassend. Danach wurden Anlagen ausgeschlossen und Fachbegriffe wie „Schulstraße“ nur noch mit Hausnummer gezählt.

**Prüfbogen:** `data/export/volltext/stichprobe_volltext.tsv` (30 Fälle). Spalte `urteil`: richtig, falsch oder unklar.

**Empfehlung:** prüfen. Bei mehr als 5 falschen Fällen die Konfidenz auf „niedrig“ senken.

## 5. Gebäude und Anlagen im Titel

Läuft auf der Seite seit dem 21.10.2026 (Konfidenz „niedrig“, 837 Vorlagen). Die KI-Vorprüfung ergab 26 plausibel, 4 teilweise.

**Prüfbogen:** `data/export/objekte/stichprobe_objekte.tsv` (30 Fälle). Spalte `urteil`: richtig, teilweise oder falsch.

## 6. Konten und Server (nur der Auftraggeber)

| Aufgabe | Stand |
|---|---|
| Plesk: Webhook für den Branch `deploy` | Am 22.10.2026 sind Hauptadresse, Branch und Spiegel gleich. `live.yml` meldet, wenn der Server zurückbleibt. Prüfen, ob der Webhook dauerhaft eingerichtet ist. |
| Google Search Console | Eigentum von ris-bonn.datenatlas.de bestätigen, `sitemap.xml` einreichen |
| Secret `ANTHROPIC_API_KEY` | nur für den Lauf unter 3 |

## 7. Außenwirkung (nur nach Ihrer Entscheidung)

| Gegenstand | Empfehlung |
|---|---|
| Issue an OParl-Lite (Codeberg): Felder `location` und `underDirectionOf` übernehmen | ja, sachlich und kurz. Die Felder sind in der OParl-API der Stadt vorhanden und für Verortung und Zuständigkeit zentral. Ein Entwurf folgt auf Wunsch. |
| Kontakt zum Autor von „Bonn entscheidet“ (Soll-Modell) | nach dem Hackathon. Übernahme und Ergänzungen sind dokumentiert (`soll/`). |
| Antwort von opendata@bonn.de zu den Baustellen-Datensätzen | abwarten. Das Archiv läuft unabhängig davon. |
| Hackathon-Rahmen (Datum, Teilnehmende, Ergebnisformat) | mitteilen; danach entstehen Leitfaden und „good first issues“ |

## Bereits abgenommen (zur Erinnerung)

- Verortung Endenich (50 Fälle, 20.10.2026)
- Themen (49 Fälle)
- Hausnummernregel (30 Fälle)
- Baustellen-Kandidaten (30 Fälle)
- Soll-Modell (30 Fälle)
- Text im Dialog „Über“
- Datenschutzerklärung
