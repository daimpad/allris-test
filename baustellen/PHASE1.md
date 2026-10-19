# Phase 1 – Bebauungspläne (Methode B3)

Stand: 19.10.2026. Grundlage: OParl-Abruf vom 18.10.2026 (24.915 Vorlagen), Plandatensatz der Stadt Bonn (1.128 Objekte, CC0).

## Umsetzung

| Baustein | Datei | Ergebnis |
|---|---|---|
| Nummernerkennung im Titel | `pipeline/geocode.py` (`plan_numbers`) | 556 Vorlagen mit Plannummer (bisher 523); Listen, Tippfehler, Zusätze („Teil A“, „II“, „-A“), Flurstücke ausgeschlossen |
| Einstufung | `pipeline/plans.py` (`Plans.classify`) | eindeutig → Konfidenz **hoch** (321 Vorlagen); Grundnummer oder mehrdeutig → niedrig; nicht im Datensatz → ohne Fläche |
| Vorrang | `pipeline/build.py`, Tabelle `plan_precedence` | Bei eindeutigem Plan treten 433 Ortsbezüge aus Straßen- und Ortsnamen im Titel zurück; 22 Vorlagen verlieren dadurch einen Ortsteil, in dem keine Planfläche liegt (Audit, Spalte „zurueckgestellt“) |
| Flächen | `pipeline/plans.py` | mehrere Flächen eines Plans (z. B. 7219-15) zusammengeführt |
| Audit | `data/export/audit_bebauungsplaene.tsv`, Pilot `data/export/endenich/audit_bebauungsplaene.tsv` | je Vorlage und Nummer: Treffer, Pläne, Inkrafttreten, Ortsteile, Konfidenz, zurückgestellte Ortsbezüge, Prüfstatus |
| Planregister | `data/export/bonn/plaene.json` | 142 Plannummern mit Plänen (belegt), Ortsteilen und Vorlagen chronologisch; Verfahrensschritte aus dem Titel (abgeleitet) mit Fundstelle im BauGB; Grundlage der Planchronik (Phase 4) |
| Änderungsprotokoll | `data/geo/bebauungsplaene_protokoll.tsv` (`pipeline/fetch.py`) | neu, entfallen (Kandidat für Aufhebung), Inkrafttreten geändert – je Abruf (montags) |
| Oberfläche | `site/app.js` | Teilpläne und Grundnummern werden angezeigt; „gesichert“ umfasst eindeutige Bebauungspläne |

## Stichprobe Endenich (Vorprüfung durch KI, nicht von Hand)

32 Vorlagen mit Plannummer im Pilot (`audit_bebauungsplaene.tsv` im Ordner `endenich`):

- 17 Vorlagen zu den Plänen 6322-1 (1), 6322-2 Teil A (9) und 6322-3 (7): eindeutig, Fläche in Endenich; die zurückgestellten Straßen (Am Propsthof, Siemensstraße, Václav-Havel-Platz) liegen im Plangebiet oder daneben – plausibel.
- 13 Vorlagen zu 6421-1 „Universitäts-Campus Endenich“: Plan im Verfahren, daher nicht im Datensatz; Verortung bleibt beim Ortsteilnamen – plausibel.
- 2 Vorlagen zu 7522-77: Aufhebung beschlossen (2024), Plan nicht mehr im Datensatz – plausibel; die Geschichte des Plans ist nur über die Vorlagen nachvollziehbar.

Der Prüfstatus im Audit bleibt „ungeprüft“, bis eine Prüfung von Hand erfolgt ist.

## Grenzen

- Verfahrensschritte stammen aus Titelstichworten und sind abgeleitet; vereinfachte Verfahren (§§ 13, 13a BauGB) haben weniger Schritte, fehlende Schritte sind keine Lücke.
- Pläne im Verfahren (56 Nummern) und aufgehobene Pläne haben keine Fläche.
- Das Änderungsprotokoll beginnt mit dem ersten Abruf nach dieser Änderung.

## Nächste Schritte

- Phase 2: Archiv der Baustellen (täglicher Abruf, Momentaufnahmen, Änderungen) – Lizenz CC0 laut Auftraggeber.
- Phase 4: Planchronik und Planebene auf der Karte aus `plaene.json`.
