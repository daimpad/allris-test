# Soll-Modell – Phase 1: Übernahme mit Ergänzungen

Stand: 19.10.2026. Grundlage: `soll/phase0/BERICHT.md`.

## Umsetzung

| Baustein | Datei |
|---|---|
| Feste Kopie, unverändert | `data/soll/verfahren.json`, `data/soll/zustaendigkeitsordnung.json` (anster2025/bonn-entscheidet, Commit `26641f7`), Lizenz `data/soll/LICENSE-bonn-entscheidet`, Herkunft `data/soll/QUELLE.md` |
| Eigene Ergänzungen und Korrekturen | `data/soll/ergaenzungen.json`, beim Laden angewandt; die Kopie bleibt unverändert |
| Zuordnung und Abgleich | `pipeline/soll.py`, Schritt `python -m pipeline soll`, im täglichen Workflow nach `export` |
| Audit | `data/export/audit_soll.tsv` (je Vorgang: Verfahren, Sicherheit, Grund, Gremien Ist und Soll, Passung, Abweichung; ohne Titel) |
| Tests | `tests/test_soll.py` |

**Ergänzungen:** 10 eigene Schritte, je mit Beleg und als `eigen` gekennzeichnet:

| Verfahren | Ergänzte Schritte | Beleg |
|---|---|---|
| Antrag im Rat | Fachausschuss; Anhörung der Bezirksvertretung | GeschO § 22 Abs. 1, § 7 Abs. 6; BezS § 9 |
| Große Anfrage | in einem Fachausschuss; in der Bezirksvertretung | GeschO § 22 Abs. 1, § 11; § 23 Abs. 1, 3 |
| Dringlichkeitsantrag | in einem Fachausschuss; in der Bezirksvertretung | GeschO § 22 Abs. 1; § 23 Abs. 1 |
| Kleine Anfrage | Kenntnisnahme in Ausschuss, Bezirksvertretung oder Rat | GeschO § 12 Abs. 3 |
| Entscheidung im Ausschuss | Anhörung der Bezirksvertretung | BezS § 9 |

**Korrekturen:**
- Zuständigkeitsordnung VII 2.16 und VIII 1.10: `an_bezirksvertretung` wird `true`.
- Ausgang „Kosten ohne Haushaltsmittel“ bei der Beschlussvorlage: Unterausschuss des Hauptausschusses Finanzen und Beteiligungsmanagement, nach GeschO § 22 Abs. 8.

Jede Korrektur prüft beim Laden, ob der alte Wert noch in der Quelle steht. Weicht er ab, bricht der Schritt ab.

**Ohne Soll:** Für den Bürgerbrief nennt das Regelwerk kein Verfahren. Kein Soll wird angenommen; der Vorgang erscheint als „ohne Soll“.

## Ergebnis (14.104 Vorgänge, 2019–2026)

| Passung der Gremien | Phase 0 | Phase 1 |
|---|---|---|
| passt | 11.451 (81 %) | 13.646 (97 %) |
| weicht ab | 2.356 | 2 (Einwohnerfragen mit Beratung in Ausschuss oder Rat) |
| ohne Beratung (seit Phase 4: „nur Beirat“) | 297 | 297 |
| ohne Soll | – | 159 (Bürgerbrief) |

Sicherheit der Zuordnung: hoch 12.581, mittel 1.364.

## Grenzen

- Die Passung prüft nur, ob die beratenden **Gremienarten** im Soll vorkommen. Reihenfolge, Fristen und Rollen (Empfehlung, Entscheidung) prüft sie nicht. Die Ergänzungen schließen Lücken des Modells; dass die Passung dadurch steigt, ist erwartbar und kein unabhängiger Beleg.
- Das Soll ist ein vereinfachtes Modell des Regelwerks, keine Rechtsauskunft. Die Fassungen von Geschäftsordnung und Satzungen gelten zum Stand des Abrufs, 19.10.2026.
- Die Belege der Ergänzungen sind von mir aus den Rechtstexten abgeleitet und nicht von Hand geprüft.

## Nächster Schritt

Phase 2: Anzeige in der Prozesslinie.
- Soll-Schritte ohne Beleg erscheinen gestrichelt als „soll“.
- Fristen, „Wer entscheidet?“ mit Fundstelle in der Zuständigkeitsordnung.
- Abweichungen erscheinen als Befund.
- Glossar, Grenzen-Text und Systemprompt werden angepasst.
