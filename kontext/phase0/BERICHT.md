# Kontextdaten je Ortsteil – Phase 0: Prüfung (24.10.2026)

Abruf, Umrechnung auf die 51 Ortsteile und Plausibilitätsprüfung der sieben Kennzahlen aus `../KONZEPT.md`. Kein Produktionscode; die Skripte liegen in `skripte/`, das Ergebnis in `ortsteile_phase0.tsv` (51 Ortsteile, 4 Stadtbezirke). Alle Werte sind **abgeleitet**.

## Ergebnis für drei Ortsteile

| Kennzahl | Endenich | Tannenbusch | Beuel-Mitte | Bezirk Bonn | Bezirk Beuel |
|---|---|---|---|---|---|
| Einwohner (Zensus, 15.05.2022) | 12.733 | 15.930 | 12.319 | 150.114 | 65.447 |
| unter 18 Jahre | 13,2 % | 25,0 % | 12,2 % | 15,9 % | 16,4 % |
| ab 65 Jahre | 14,1 % | 14,5 % | 17,7 % | 16,2 % | 20,3 % |
| Nettokaltmiete (Zensus 2022) | 10,12 €/m² | 8,17 €/m² | 9,57 €/m² | 9,58 €/m² | 8,67 €/m² |
| Bodenrichtwert Wohnen 2026 (Median nach Einwohnern) | 740 €/m² | 530 €/m² | 800 €/m² | – | – |
| Haltestellen | 25 | 19 | 17 | 244 | 113 |
| Kitas (Plätze U3 / Ü3) | 8 (117 / 382) | 10 (140 / 604) | 10 (112 / 390) | 110 | 41 |
| Einwohner in Flächen mit dringendem Handlungsbedarf (Hitze) | 53 % | 70 % | 87 % | 67 % | 57 % |
| Einwohner im Überschwemmungsgebiet | 8,1 % | 0 % | 31,1 % | 2,5 % | 8,1 % |

## Methode und Prüfungen

| Kennzahl | Umrechnung | Prüfung |
|---|---|---|
| Einwohner | 100-m-Zellen nach Mittelpunkt im Ortsteil | Summe Bonn 321.351; IT.NRW 31.12.2022 (Basis Zensus) 322.221 – Abweichung 0,3 % |
| Altersanteile | Anteilsdateien des Zensus, nach Einwohnern der Zelle gewichtet; geheim gehaltene Zellen (Bonn 6 % bzw. 4 % der Einwohner) zählen mit 0 | Bonn 16,8 % unter 18 und 18,6 % ab 65; IT.NRW 31.12.2024: 16,5 % und 19,1 %. Die erste Rechnung mit den Altersgruppen war unbrauchbar (bis 86 % der Einwohner in Zellen mit geheim gehaltenen Werten) |
| Miete | Mittel der Zellen, gewichtet nach Wohnungen | Bonn 9,09 €/m²; kein amtlicher Vergleichswert je Gemeinde abrufbar (Zensus-Datenbank nur mit Anmeldung) |
| Bodenrichtwert | Zonen Wohnbauland (NUTA W*, baureif), ohne „ASB“ (bebaute Flächen im Außenbereich, eine Zone 23 km²); Median über die Zellen nach Einwohnern | Abgleich mit dem Median der Zonen, die der Gutachterausschuss dem Ortsteil zuordnet: Abweichung im Median 6,2 %, im Mittel 9,3 %; 13 Ortsteile über 15 % (verschiedene Zonenzuschnitte) |
| Haltestellen | Haltestellennamen (Steige zusammengefasst) nach Lage | Bonn 543 |
| Kitas | Lage laut Datei des Landes | Bonn 228 Einrichtungen |
| Hitze | Planungshinweiskarte der Klimaanalyse NRW 2026: Einwohner der Karte in Flächen mit Handlungspriorität 1–2 („dringender Handlungsbedarf“), anteilig nach Fläche | Einwohner laut Karte für Bonn 321.396 (Zensus 321.351) |
| Überschwemmung | Einwohner in Zellen, deren Mittelpunkt in einem festgesetzten oder vorläufig gesicherten Überschwemmungsgebiet liegt | Bonn 15.057; Anteil nach Fläche verworfen (zählt die Wasserfläche des Rheins mit) |

## Befunde

1. **Kleine Ortsteile:** Hardthöhe hat laut Zensus 20 Einwohner. Unter 100 Einwohnern zeigt die Tabelle keine Anteile und keine Mittelwerte.
2. **Hitze ist stadtweit verbreitet:** 55 % der Einwohner Bonns leben in Flächen mit Priorität 1–2. Für die Unterscheidung der Ortsteile ist nur Priorität 1 (Bonn 3 %) zu schmal. Vorschlag: den Anteil 1–2 zeigen, mit dem Wortlaut der Karte.
3. **Überschwemmung:** Hohe Werte auch abseits des Rheins (Alt-Godesberg 26,5 %, Lessenich/Meßdorf 19,5 %). Vermutlich Überschwemmungsgebiete kleiner Gewässer; nicht von Hand geprüft.
4. **Bodenrichtwert:** Rund 30 % der Einwohner von Beuel-Mitte liegen in keiner Zone für Wohnbauland (vermutlich Misch- oder Kerngebiet) und fehlen im Median. Den Wert für den Stadtbezirk berechne ich erst in Phase 1.
5. **Zeitbezug:** Zensus 15.05.2022, Bodenrichtwerte 01.01.2026, Kitas 06/2025, Haltestellen tagesaktuell, Klimaanalyse 2026. Jede Zahl braucht ihren Stichtag.

## Lizenzen und Namensnennung
- Zensus 2022: © Statistisches Bundesamt (Destatis), dl-de/by-2.0.
- Kitas: Land NRW, dl-de/by-2.0.
- BORIS NRW, Klimaanalyse NRW, Überschwemmungsgebiete NRW und VRS: dl-de/zero-2.0.

## Für Phase 1 zu entscheiden
- Hitze als Anteil der Prioritäten 1–2 (Vorschlag) oder nur Priorität 1.
- Bodenrichtwert nur Wohnbauland (Vorschlag) oder einschließlich Misch- und Kerngebieten.
- Mindestgröße 100 Einwohner für Anteile (Vorschlag).
