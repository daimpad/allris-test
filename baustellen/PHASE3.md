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

`data/export/baustellen/stichprobe_kandidaten.tsv` – hoch vor mittel, höchstens zwei je Baustelle, ein Vorgang je Baustelle; wird nie überschrieben. Prüfung von Hand ausstehend (Spalte `pruefvermerk`).

KI-Vorprüfung (`vorpruefung_kandidaten.tsv`, gekennzeichnet, ersetzt nicht die Prüfung von Hand):

| Konfidenz | plausibel | unklar | nicht plausibel |
|---|---|---|---|
| hoch (9) | 9 | 0 | 0 |
| mittel (21) | 2 | 6 | 13 |

Befund: „mittel“ besteht überwiegend aus Bürgeranträgen zu Tempo 30, Ampeln oder Parkregeln in derselben Straße. Das Thema Verkehr trennt dort nicht, das Bau-Stichwort schon.

## Empfehlung

- Schwelle für die Freischaltung je Stufe: mindestens 70 % plausibel in der Prüfung von Hand.
- Nach der Vorprüfung käme nur **hoch** in Frage (6 Baustellen); **mittel** bleibt im Audit.
- Die Stichprobe für „hoch“ ist klein (9). Vor der Freischaltung weitere Tage des Archivs abwarten und nachprüfen.
- Kalibrierung der Regeln erst nach der Prüfung von Hand, damit die Stichprobe nicht an die Regeln angepasst wird.

## Nächster Schritt

Prüfung von Hand. Danach Phase 4: Anzeige als „möglicher Zusammenhang“ mit den erfüllten Kriterien.
