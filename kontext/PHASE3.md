# Kontextdaten je Ortsteil – Phase 3: Vorgang und Assistent (24.10.2026)

Umsetzung nach Freigabe des Plans durch den Auftraggeber (24.10.2026).

## Vorgang: „Zum Ortsteil …“
- Zwei bis drei Kennzahlen passend zum abgeleiteten Thema der Vorlage, neben dem eigenen Stadtbezirk:

  | Thema | Kennzahlen |
  |---|---|
  | Bauen und Stadtentwicklung | Bodenrichtwert, Nettokaltmiete |
  | Soziales, Wohnen und Gesundheit | Nettokaltmiete, Anteil ab 65, Anteil unter 18 |
  | Schule und Bildung | Anteil unter 18, Kitas, Plätze ab 3 Jahren |
  | Kinder, Jugend und Familie | Anteil unter 18, Kitas, Plätze unter 3 Jahren |
  | Verkehr und Mobilität | Haltestellen, Einwohner |
  | Umwelt, Grün und Klima | Hitze, Überschwemmungsgebiet |

  Bei mehreren Themen gilt die Reihenfolge der Themen der Vorlage, höchstens drei Kennzahlen. Für Kultur, Wirtschaft, Sicherheit und Beteiligung gibt es keine passende Kennzahl; dann entfällt der Abschnitt.
- Nur wenn die Vorlage selbst in **genau einem Ortsteil** verortet ist (übernommene Orte zählen nicht) und keine Ortsbezüge in einem anderen Stadtbezirk hat.
- Gekennzeichnet als „abgeleitet“, mit Quelle, Lizenz und Stand; Hinweis: „Einordnung, kein Beleg für die Vorlage und kein Urteil über den Ortsteil“.

## Ratsassistent
- Werkzeug `hole_kontext(gebiet, kennzahlen?)`: Ortsteil, Stadtbezirk oder „ganz Bonn“; je Kennzahl Wert, Vergleichswert (Stadtbezirk bzw. ganz Bonn), Quelle, Lizenz, Stand, Methode; `evidenz: abgeleitet`.
- `kontext.json` enthält dafür die Zuordnung Ortsteil → Stadtbezirk (`stadtbezirk_je_ortsteil`).
- Systemprompt v0.5 (Änderung 27): Zahlen nur mit Quelle und Stand, als abgeleitet; kein Beleg und keine Begründung einer Vorlage; keine Rangfolge oder Wertung von Ortsteilen; Zensus-Miete ist kein Mietspiegel.
- Fragenkatalog: F09 (Miete in Endenich mit Vergleich) und B05 (Frage nach dem „schlechtesten“ Ortsteil). Noch nicht mit einem Anbieter gelaufen.

## Prüfung
- Node-Tests (Werkzeug mit nachgebildeten Daten und gegen den echten Export), Python-Tests, Browser-Test (Vorgang in Endenich mit Thema Bauen), axe ohne Verstöße bei 1440 und 390 px.

## Offen
- Zuschaltbare Flächen für Überschwemmungsgebiete und Bodenrichtwertzonen.
- Wanderung, sobald die Statistikstelle antwortet.
