# Kultur und Haushalt – Phase 1: Themenseite (25.10.2026)

Grundlage: `phase0/BERICHT.md`. Die Seite liegt unter `thema/kultur-und-haushalt/` und erscheint in der Sitemap. Sie ist auch über „Auswertung“ → „Thema: Kultur und Haushalt“ erreichbar.

## Umsetzung
- `pipeline/dossier.py`: Die Regeln stehen in `STRAENGE`. Die Daten schreibt `export_all` nach `export/bonn/dossiers/kultur.json`; sie sind im Datenpaket enthalten. Die Seite entsteht im Schritt `seo`, wie die Gebietsseiten, und trägt keine Zeitstempel.
- **Stränge** (abgeleitet, je Vorlage mit Grund; jede Vorlage steht in höchstens einem Strang):
  1. Haushalt und Konsolidierung: Merkmal im Titel.
  2. Zukunft der Bonner Bühnen: Stammnummer 260127.
  3. Kulturförderung, Zuschüsse, Gebühren: Kulturamt, Stadtbibliothek, Kunstmuseum, Theater oder Beethovenorchester federführend, oder Beratung im Kulturausschuss oder in der Kulturkommission; dazu ein Bezug zu Geld im Titel.
  4. Weitere Vorlagen: wie Strang 3, ohne Bezug zu Geld im Titel.
- **Zeitraum:** seit 01.11.2025. Die Bühnen-Vorlagen zählen unabhängig vom Datum.
- **Weiterer Inhalt der Seite:**
  - der Weg des Haushalts 2027/2028 in sechs Schritten, aus 261064 selbst zusammengefasst, ohne Zitate;
  - zum Vergleich die Zahl der Vorlagen zum Haushalt 2025/2026;
  - die nächsten Sitzungen (je Gremium zwei);
  - Wege zum Mitwirken;
  - „Was diese Seite nicht zeigt“.
- Links: Drucksache → Vorgang auf der Karte, „Original“ → Ratsinformationssystem.

## Stand 25.10.2026
126 Vorlagen: 19 Haushalt, 32 Bühnen, 22 Kulturförderung/Zuschüsse/Gebühren, 53 weitere. Sitzungen: Hauptausschuss 05.11., Rat 12.11., Finanzausschuss 26.11., Kulturausschuss 01.12., Hauptausschuss 03.12., Rat 10.12.2026.

## Grenzen
- Die Zuordnung ist nicht von Hand geprüft.
- Den Haushaltsplan auf bonn.de verlinkt die Seite nicht direkt: Die Adressen der PDF-Dateien ließen sich von hier aus nicht prüfen, weil die Seite der Stadt automatische Abrufe abweist.
- Die Vorlage zur Einbringung 2027/2028 fällt unter Strang 1, sobald sie erscheint, weil ihr Titel „Haushaltssatzung“ enthält.

## Prüfbogen (25.10.2026)
`data/export/kultur/stichprobe_kultur.tsv`, Schritt `kultur-stichprobe` (einmalig, wird nicht überschrieben):
- **22 zugeordnete Vorlagen:** 4 Haushalt, 4 Bühnen, 7 Kulturförderung, 7 weitere. Frage: Passt der Strang?
- **8 nicht zugeordnete Vorlagen** mit Kulturbezug im Titel, je Verfahren eine (Gegenprobe). Frage: Fehlt die Vorlage auf der Seite?

Erste Auffälligkeiten beim Ziehen:
- Vorlagen zur Bühnen-Debatte außerhalb der Stammnummer 260127, etwa der Bürger:innenrat 260756, stehen unter „weitere“ oder fehlen.
- Kulturfestivals der Bezirksvertretungen fehlen.
