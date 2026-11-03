# Haushalt Option 5: Ertragsarten (03.11.2026)

Entscheidungen des Auftraggebers (03.11.2026): Zeilen 1–9 der Teilergebnispläne je Produktbereich und Produktgruppe aus beiden Haushaltsplänen und dem Jahresabschluss 2024 (alle vier Ansichten); Anzeige in jeder Ebene unter den Aufwandsarten („Woher kommt das Geld?“, Balken und Tabelle); negative Werte wie bei den Aufwandsarten ohne Fläche, nur in der Tabelle; Prüfbogen im Gespräch vor der Veröffentlichung.

## Daten

- `pipeline/haushaltsplan.py`, Schritt `haushalt-ertragsarten` (einmalig, lokal, `pdftotext -bbox`; dieselben PDF wie die Ebenen, SHA-256 laut `STAND.json`):
  - `data/haushalt/ertragsarten.tsv`: Zeilen 1–10 je Produktbereich und Produktgruppe, Haushaltspläne 2023/2024 und 2025/2026, Euro, ohne Finanzplanung (16.700 Werte);
  - `data/haushalt/jahresabschluss_ertragsarten.tsv`: dieselben Zeilen aus den Teilergebnisrechnungen des Jahresabschlusses 2024, sechs Spalten, Cent (9.480 Werte).
- Bezeichnungen der Zeilen in allen Seiten gleich: 1 Steuern und ähnliche Abgaben, 2 Zuwendungen und allgemeine Umlagen, 3 Sonstige Transfererträge, 4 Öffentlich-rechtliche Leistungsentgelte, 5 Privatrechtliche Leistungsentgelte, 6 Kostenerstattungen und Kostenumlagen, 7 Sonstige ordentliche Erträge, 8 Aktivierte Eigenleistungen, 9 Bestandsveränderungen.

| Prüfsumme je Spalte | Spalten | größte Abweichung |
|---|---|---|
| Haushaltsplan: Zeilen 1–9 = Zeile 10 (PB und PG) | 1.670 | 0 € |
| Haushaltsplan: Summe der PG = PB (Zeile 10) | 170 | 5 € |
| Haushaltsplan: Zeile 10 = `produktbereiche.tsv` | 170 | 0 € |
| Jahresabschluss: Zeilen 1–9 = Zeile 10 (PB und PG) | 948 | 0 Cent |
| Jahresabschluss: Summe der PG = PB (Zeile 10) | 102 | 0 Cent |
| Jahresabschluss: Zeile 10 = `jahresabschluss.tsv` | 948 | 0 Cent |

## Seite

Sichtbar mit `ERTRAGSARTEN_FREIGEGEBEN` (vor der Freigabe mit `HAUSHALT_ERTRAGSARTEN=vorschau`). Je Produktbereich (Ebene 2) und Produktgruppe (Ebene 3) unter den Aufwandsarten: Absatz „Woher kommt das Geld? Ertragsarten“, Balken je Ansicht (Klasse `hh-eb`, eigene Farben, keine Kacheln), Tabelle mit den vier Ansichten (Ebene 2 mit Anteil am Plan 2026), Summe Zeile 10. Ertragsarten ohne Betrag in allen Ansichten nur als Liste darunter; negative Werte ohne Balkenstück, in der Tabelle und im Hinweis.

## Prüfbogen

`data/export/haushalt/pruefbogen_haushalt_ertragsarten.tsv` (`haushalt-pruefbogen-ertragsarten`, wird nicht überschrieben): 24 Zellen, 16 aus dem Haushaltsplan 2025/2026, 8 aus dem Jahresabschluss 2024 (negative Werte, teilweise gefüllte Zeilen, größte Steuern, Zuwendungen und Gebühren, aktivierte Eigenleistungen, PB 03, Stichprobe). Zweiter Leseweg (KI-gestützt, `pdftotext -layout`, Kopf jeder Seite und Spalte 5 = 4 − 2 im Jahresabschluss geprüft): 24 von 24 gleich. Vom Auftraggeber im Gespräch bestätigt und freigegeben 03.11.2026 (`ERTRAGSARTEN_FREIGEGEBEN = True`; Vermerk in der Spalte `pruefung`).
