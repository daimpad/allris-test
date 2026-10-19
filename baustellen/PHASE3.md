# Phase 3 – Kandidaten „Beschluss ↔ Baustelle“

Stand: 19.10.2026. Ergebnis ist ein **Kandidat** („möglicher Zusammenhang“) mit Konfidenz und einzeln ausgewiesenen Kriterien, nie die Aussage „umgesetzt“. Noch keine Anzeige auf der Seite.

## Kriterien (`pipeline/kandidaten.py`, Schritt `python -m pipeline kandidaten`)

| Kriterium | Regel | Begründung |
|---|---|---|
| räumlich | Abstand Baustelle ↔ Ortsbezug der Vorlage (Straße, Bebauungsplan) ≤ 150 m; vererbte Orte zählen nicht | Straßenpunkte stehen für ganze Straßen; 150 m fängt Abschnitte, ohne Nachbarstraßen weit einzubeziehen |
| zeitlich | Vorlage entschieden, Baubeginn am oder nach dem Tag der Entscheidung | Umsetzung folgt dem Beschluss |
| Straße | Straßenname der Baustelle (Bezeichnung, Adresse) gleich einem Straßennamen der Vorlage | Nähe allein trifft oft die Querstraße |
| thematisch | Amt 66 (Tiefbau) oder 61-3 (Stadtverkehr) oder Thema Verkehr | Zuständigkeit für Straßenbau |
| Stichwort | Bau-Stichwort im Titel passend zur Maßnahme (Kanalbau: Kanal, Entwässerung …; sonst Ausbau, Umgestaltung, Erneuerung …) | trennt Baubeschlüsse von verkehrsrechtlichen Anordnungen |
| Baubeschluss | „hoch“ nur für Beschlussvorlagen, Dringlichkeits- und Eilentscheidungen (ergänzt 19.10.2026 nach Prüfung der Stichprobe) | Bürgeranträge und Anträge mit Planungsbezug sind kein Baubeschluss |

Konfidenz: **hoch** = alle Kriterien; **mittel** = räumlich, zeitlich, Straße und thematisch oder Stichwort; **niedrig** = übrige. Baustellen fremder Träger (SWB Bonn-Netz, Straßen NRW, Deutsche Bahn) stehen getrennt als **fremd**.

## Probelauf (48 Baustellen vom 19.10.2026)

| Konfidenz | Kandidaten | Baustellen |
|---|---|---|
| hoch | 11 | 6 |
| mittel | 46 | 21 |
| niedrig | 253 | 30 |
| fremd | 146 | 12 |

Audit: `data/export/baustellen_kandidaten.tsv` (alle Kandidaten mit Kriterien, Begründung, Prüfvermerk).

## Stichprobe (30 Kandidaten)

`data/export/baustellen/stichprobe_kandidaten.tsv` – hoch vor mittel, höchstens zwei je Baustelle, ein Vorgang je Baustelle; wird nie überschrieben. Prüfung von Hand abgeschlossen (Spalte `pruefvermerk`).

KI-Vorprüfung (`vorpruefung_kandidaten.tsv`, gekennzeichnet, ersetzt nicht die Prüfung von Hand):

| Konfidenz | plausibel | unklar | nicht plausibel |
|---|---|---|---|
| hoch (9) | 9 | 0 | 0 |
| mittel (21) | 2 | 6 | 13 |

Befund: „mittel“ besteht überwiegend aus Bürgeranträgen zu Tempo 30, Ampeln oder Parkregeln in derselben Straße. Das Thema Verkehr trennt dort nicht, das Bau-Stichwort schon.

## Prüfung von Hand (abgeschlossen 19.10.2026)

| Kandidaten | Ergebnis | Folge |
|---|---|---|
| 1–6 (hoch) | plausibel; 212110 und 221785 sind Bürgeranträge mit Planungsbezug | „hoch“ nur noch für Baubeschlüsse (Kriterium Baubeschluss); Kandidaten mit „hoch“ in ganz Bonn von 11 auf 7 |
| 7–12 | wie Vorprüfung: 4 plausibel, 1 unklar, 1 nicht plausibel | 211463 (Grundsatzbeschluss Stiftsplatz) bleibt „mittel“; kein neues Bau-Stichwort |
| 13–18 | wie Vorprüfung: 1 plausibel, 1 unklar, 4 nicht plausibel (Tempo 30, Parkverbot, Glascontainer) | keine |
| 19–24 | wie Vorprüfung: 3 unklar, 3 nicht plausibel | keine |
| 25–30 | wie Vorprüfung: 1 unklar, 5 nicht plausibel | keine |

**Ergebnis (30 von 30 geprüft):**
- „hoch“ nach der neuen Regel (nur Baubeschlüsse): 6 von 6 plausibel (100 %). Die 3 Bürgeranträge mit Planungsbezug sind nun „mittel“.
- „mittel“: 2 plausibel, 6 unklar, 13 nicht plausibel (10 % plausibel). Die Stufe bleibt verborgen.
- Die vorgeschlagene Schwelle (70 % plausibel je Stufe) erreicht nur „hoch“.
- Die KI-Vorprüfung stimmte in allen Fällen mit dem Urteil von Hand überein. Die Regel zu Baubeschlüssen hat erst der Auftraggeber festgelegt.
- Freischaltung: „hoch“ bleibt sichtbar, der Hinweis „vorläufig“ entfällt (Entscheidung des Auftraggebers 19.10.2026). Die Anzeige bleibt ein Indiz, der Vollzug „unklar“.

## Empfehlung

- Schwelle für die Freischaltung je Stufe: mindestens 70 % plausibel in der Prüfung von Hand.
- Nach der Vorprüfung käme nur **hoch** in Frage (6 Baustellen); **mittel** bleibt im Audit.
- Die Stichprobe für „hoch“ ist klein (9). Vor der Freischaltung weitere Tage des Archivs abwarten und nachprüfen.
- Kalibrierung der Regeln erst nach der Prüfung von Hand, damit die Stichprobe nicht an die Regeln angepasst wird.

## Nächster Schritt

Nachprüfen, sobald das Archiv weitere Baustellen erfasst hat; neue Kandidaten „hoch“ erscheinen im Änderungsprotokoll.
