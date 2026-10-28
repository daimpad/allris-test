# Haushalt – Schritt 1 der Visualisierung: Treemap der Produktbereiche (28.10.2026)

**Anlass:** Der Auftraggeber fragte, ob sich der Haushalt so zeigen lässt wie in den Berliner Haushaltsdaten (https://haushaltsdaten.odis-berlin.de/visualisierung/; Treemap mit D3, Code MIT, github.com/berlin/haushaltsdaten). **Entscheidung:** erst die Produktbereiche, dann eine tiefere Ebene; eine eigene Seite `haushalt/`.

## Umsetzung
- **Daten:** `data/haushalt/produktbereiche.tsv`, Zeile 17 „Ordentliche Aufwendungen“ der 17 Teilergebnispläne. Die Werte sind geprüft und freigegeben (`haushalt/PHASE1.md`). Plan ist der Ansatz des Haushaltsjahres, Ist das Ergebnis aus der jüngsten Ausgabe (`haushaltsplan.reihe`).
- **Ansichten:** Plan 2026 (1.884,1 Mio. €), Plan 2025 (1.797,0 Mio. €, gleich dem Gesamtergebnisplan), Ist 2023 (1.659,4 Mio. €). Die Finanzplanung ab 2027 ist nicht übernommen.
- **Darstellung** (`pipeline/haushaltsseite.py`, im Schritt `seo`):
  - Squarified Treemap (Bruls, Huizing, van Wijk 2000) als SVG, je Ansicht ein breites und ein hohes Format.
  - Gewechselt wird mit Auswahlknöpfen und CSS; die Seite braucht kein Skript.
  - Jede Fläche ist ein Link auf ihre Zeile in der Tabelle und hat einen Titel mit Betrag und Anteil.
  - Die fünf Produktbereiche mit Themenseite (03, 04, 10, 12, 13) tragen deren dunkle Farbe, die übrigen ein helles Grau-Violett.
  - Passt der Name nicht in die Fläche, stehen dort nur Nummer und Betrag.
- **Tabelle:** alle 17 Produktbereiche mit Ist 2023, Plan 2025 und Plan 2026, Fundstelle (Ausgabe, Seite), Anteil, Link zum Teilergebnisplan (PDF) und zur Themenseite; dazu die Summe.
- **Verweise:** Menü „Auswertung“ (Karte „Haushalt auf einen Blick“), Haushaltsabschnitt jeder Themenseite (`haushalt/#pb-XX`), Sitemap, „Seit Version 1.0“.
- **Neutralität:** Die Seite sagt nicht, ob ein Betrag hoch oder niedrig ist. Plan und Ist sind getrennt, alle Werte nominal. Die Grenzen stehen auf der Seite: keine Einzelposten, keine Erträge und Investitionen, Eigenbetriebe und Gebäudemanagement fehlen, keine Zuordnung zu Vorlagen.
- **Geprüft:** `tests/test_haushaltsseite.py` (Flächen proportional, Beispiel aus der Literatur, Summen, 6 × 17 Flächen) und ein Browser-Test in `thema.test.mjs` (Wechsel ohne Skript, Sprung zur Tabelle, 1440 und 390 px, axe ohne Verstöße).

## Nächster Schritt (offen, nach Phase 0)
Eine zweite Ebene beim Hineinzoomen in einen Produktbereich, aus denselben PDFs. Infrage kommen zwei Gliederungen:
- **Aufwandsarten:** Zeilen 11–16, etwa Personal, Sach- und Dienstleistungen, Abschreibungen, Transferaufwand.
- **Produktgruppen:** die Teilergebnispläne je Produktgruppe.

Prüfsumme gegen Zeile 17 je Produktbereich, dazu ein Prüfbogen im Gespräch.
