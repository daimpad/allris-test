# Konzept: Kontextdaten je Ortsteil (Entwurf 24.10.2026)

Entscheidungen des Auftraggebers (24.10.2026): Kontext zu Vorlagen, kein eigener Atlas; Ebene Ortsteil; Themen Bevölkerung, Wohnen und Boden, Infrastruktur, Umwelt und Klima; Auswahl der ersten Ebenen und Anfrage an die Statistikstelle wie empfohlen; Wanderung als spätere Ebene. Quellen: `QUELLEN.md`.

## Grundsätze
- **Einordnung, kein Urteil.** Kennzahlen stehen neben den Vorlagen, ohne Rangfolge der Ortsteile und ohne Wertung („gut“, „schlecht“).
- **Quellentreu.** Jede Zahl mit Quelle, Lizenz und Stichtag; auf Ortsteile umgerechnete Werte sind als „abgeleitet“ gekennzeichnet, mit Methode.
- **Datenschutz.** Nur Summen je Ortsteil; keine Punkte, die Personen erkennbar machen; Rasterwerte des Zensus mit dem Hinweis auf Verrauschung bei kleinen Zahlen.

## Erste Fassung: sieben Kennzahlen
| Thema | Kennzahl je Ortsteil | Quelle | Umrechnung |
|---|---|---|---|
| Bevölkerung | Einwohner; Anteil unter 18 und ab 65 Jahren | Zensus 2022 | Rasterzellen nach Mittelpunkt im Ortsteil |
| Wohnen | durchschnittliche Nettokaltmiete je m² | Zensus 2022 | nach Wohnungen gewichtetes Mittel der Zellen |
| Boden | Bodenrichtwert Wohnbauland (Median der Zonen), Reihe 2011–2026 | BORIS NRW | nach Fläche der Zonen im Ortsteil |
| Infrastruktur | Haltestellen; Kitas und Plätze | VRS GTFS; Land NRW | Punkt im Ortsteil |
| Klima | Flächenanteil mit hoher Wärmebelastung | Klimaanalyse NRW | Flächenanteil |
| Wasser | Flächenanteil im Überschwemmungsgebiet | Land NRW | Flächenanteil |

## Darstellung
- **Karte:** in der vorhandenen Flächenauswahl (`flaechen=`) zusätzliche Kennzahlen; fünf Stufen wie bisher, Legende mit Quelle und Stichtag. Überschwemmungsgebiete und Bodenrichtwertzonen als zuschaltbare Flächen beim Hineinzoomen; Haltestellen und Kitas als Punkte.
- **Gebiet:** kurzer Steckbrief des Ortsteils (alle Kennzahlen, mit Vergleichswert für den Stadtbezirk).
- **Vorgang:** Feld „Zum Ortsteil“ mit zwei bis drei Kennzahlen passend zum Thema der Vorlage (Wohnen → Miete, Boden; Schule → Kinderanteil, Kitas; Verkehr → Haltestellen; Klima → Hitze, Überschwemmung).
- **Ratsassistent:** Werkzeug `hole_kontext` (umgesetzt unter diesem Namen, passend zu den übrigen Werkzeugen) mit denselben Werten und Quellen.

## Später, wenn Daten freigegeben werden
- **Wanderung:** Zu- und Fortzüge je Ortsteil als Saldo-Farbe; mit Herkunft und Ziel als Pfeile zwischen Ortsteilen. Voraussetzung: Daten der Statistikstelle (Anfrage `ANFRAGE_statistikstelle.md`).
- **Zeitreihen 2014–2025** aus dem Strukturdatenatlas (nach Klärung der Lizenz; Umrechnung von statistischen Bezirken auf Ortsteile über das Zensusraster).
- Mietspiegel, Lärm, Starkregen: erst bei offener Lizenz bzw. auswertbaren Daten.

## Umsetzung in Phasen (je mit Rückfrage)
0. **Prüfung:** Abruf, Ausschnitt Bonn, Umrechnung für Endenich und zwei weitere Ortsteile; Abgleich mit veröffentlichten Werten der Stadt; Bericht.
1. **Pipeline:** `pipeline/kontext.py` → `kontext.json` je Ortsteil, Audit der Umrechnung (TSV), Ausschnitte für Bonn in `data/kontext/` (neu nur bei neuem Stand der Quelle; Haltestellen monatlich), Lizenzzeilen, DCAT.
2. **Karte und Steckbrief.**
3. **Vorgang und Assistent.**

## Entscheidungen zu Einzelfragen (Auftraggeber, 24.10.2026)
- **Nach Phase 0:** Hitze als Anteil der Einwohner in Flächen mit Priorität 1–2 („dringender Handlungsbedarf“); Bodenrichtwert nur Wohnbauland; Anteile und Mittelwerte erst ab 100 Einwohnern.
- **Vergleichswert** im Steckbrief und im Vorgang: der eigene Stadtbezirk.
- **Große Dateien** (Bodenrichtwerte 184 MB, Klimaanalyse bis 3 GB): Ausschnitt für Bonn einmalig erzeugen und im Repository ablegen (`data/kontext/`); neu schneiden nur bei einem neuen Stand der Quelle (Bodenrichtwerte jährlich, Klimaanalyse bei neuer Fassung).
