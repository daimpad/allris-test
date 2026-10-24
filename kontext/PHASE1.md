# Kontextdaten je Ortsteil – Phase 1: Pipeline (24.10.2026)

Umsetzung nach Freigabe des Plans. Entscheidungen des Auftraggebers vom 24.10.2026: Hitze als Anteil der Prioritäten 1–2, Bodenrichtwert nur Wohnbauland, Anteile erst ab 100 Einwohnern. Auf der Seite erscheint noch nichts (Phase 2).

## Was umgesetzt ist
- **Ausschnitte für Bonn** in `data/kontext/` (zusammen 3,4 MB), erzeugt mit `python -m pipeline kontext-ausschnitte`:
  - Zensus-Zellen: 5.463 Zellen, 321.351 Einwohner
  - Bodenrichtwertzonen Wohnbauland: 317 Zonen
  - Planungshinweiskarte: 2.940 Flächen
  - Überschwemmungsgebiete
  - Kitas: 228
  - Quellen mit Lizenz und Stand in `STAND.json`

  Neu geschnitten wird nur bei einem neuen Stand der Quelle.
- **Haltestellen** (`fetch-haltestellen`): 543 Haltestellen, im Workflow am 1. jedes Monats neu. Ein Abruf mit weniger als 300 Haltestellen ersetzt den Stand nicht.
- **Kennzahlen** (`python -m pipeline kontext`, täglich nach `export`):
  - `export/bonn/kontext.json` mit Ortsteilen, Stadtbezirken und ganz Bonn; je Kennzahl Quelle, Lizenz, Stand und Methode; ohne Zeitstempel
  - Audit `export/audit_kontext.tsv`
- **Prüfung** in `check`: Einwohner Bonn höchstens 3 % neben dem amtlichen Wert (IT.NRW, 31.12.2022: 322.221), jede Kennzahl mit Lizenz und Stand, keine Anteile unter 100 Einwohnern. Ein Befund hält die Veröffentlichung an.
- Lizenzen in `data/LICENSE-DATA.md`, README, DCAT (Namensnennung dl-de/by-2.0); Datenpaket mit `kontext.json`, Audit, Quellen und Berichten.

## Änderung gegenüber Phase 0
**Überlagerte Bodenrichtwertzonen:** In BORIS überlagern sich Zonen, etwa für Ein- und Zweifamilienhäuser und für Geschosswohnungsbau im selben Gebiet. Im Mittel wohnen 57 % der Einwohner eines Ortsteils in solchen Zellen. Phase 0 nahm die zuerst gefundene Zone; die Reihenfolge war zufällig. Jetzt verteilen sich die Einwohner einer Zelle zu gleichen Teilen auf alle Zonen. Abgleich mit dem Median der Zonen, die der Gutachterausschuss dem Ortsteil zuordnet: Abweichung im Median 4,3 % (Phase 0: 6,2 %), im Mittel 6,7 %. Endenich bleibt bei 740 €/m², Tannenbusch steigt von 530 auf 560, Beuel-Mitte von 800 auf 860.

## Grenzen
- Bodenrichtwert: In Bonn-Zentrum liegen 66 % der Einwohner in keiner Zone für Wohnbauland (Misch- und Kerngebiet), in Godesberg-Nord 67 %. Der Median beschreibt dort nur einen Teil der Wohnlagen; das Audit nennt den Anteil.
- Alle Werte sind auf Ortsteile umgerechnet (abgeleitet); Stichtage verschieden (Zensus 15.05.2022, Bodenrichtwerte 01.01.2026, Kitas 02.06.2025).

## Nächster Schritt
Phase 2: Karte und Steckbrief des Ortsteils (Vergleich mit dem Stadtbezirk) – Plan folgt zur Freigabe.
