# Haushalt – Schritt 2 der Visualisierung: Produktgruppen und Aufwandsarten (28.10.2026)

**Anlass:** Phase 0 der zweiten Ebene (`haushalt/phase0/EBENE2.md`) ergab, dass sich Aufwandsarten und Produktgruppen aus denselben PDF lesen lassen und alle Prüfsummen aufgehen. **Entscheidung des Auftraggebers:** Ein Klick führt bis zur feinsten Aufschlüsselung der PDF (Option 3): Produktbereich → Produktgruppe → Aufwandsart.

## Daten
- **Auslesung** (`python -m pipeline haushalt-ebenen`, einmalig, lokal mit `pdftotext -bbox`): je Ausgabe (2023/2024, 2025/2026) die 17 PDF der Produktbereiche. Gelesen werden über die Wortkoordinaten:
  - der Teilergebnisplan des Produktbereichs (S. 1), Zeilen 11–16;
  - jeder Teilergebnisplan einer Produktgruppe (150 je Ausgabe), Zeilen 11–17.
- **Spalte eindeutig:** Der rechte Rand jedes Betrags liegt in festem Abstand rechts der Spaltennummer; der häufigste Abstand der Seite bestimmt die Spalte. So stimmen auch teilweise gefüllte Zeilen (3 bei den Produktbereichen, 166 bei den Produktgruppen). Die Bezeichnung jeder Zeile muss dem Namen im PDF entsprechen.
- **Kopf der Produktgruppe:** nur Nummer, Name und Organisationseinheit (meist ein Amt, bei vier Bezirksverwaltungsstellen keine). Die Angabe „verantwortlich: …“ wird nicht gelesen.
- **Leere Zellen** zählen als 0 und sind in der Spalte `leer` vermerkt: 57 bei den Produktbereichen, 2.332 bei den Produktgruppen. Die Finanzplanung ab 2027 ist nicht übernommen.
- **Ergebnis:** `data/haushalt/aufwandsarten.tsv` (1.020 Werte), `data/haushalt/produktgruppen.tsv` (10.500 Werte), je mit Datei und Seite; Schlüssel `ebenen` in `STAND.json`. Die PDF sind dieselben wie in Phase 1 (SHA-256 geprüft).

| Prüfsumme je Spalte (Toleranz 1.500 €, sonst Abbruch) | Spalten | größte Abweichung |
|---|---|---|
| Zeilen 11–16 = Zeile 17 des Produktbereichs (`produktbereiche.tsv`) | 170 | 0 € |
| Zeilen 11–16 = Zeile 17 der Produktgruppe | 1.500 | 0 € |
| Summe der Produktgruppen = Zeile 17 des Produktbereichs | 170 | 6 € |

## Seite `haushalt/`
- **Ebene 1** bleibt: Treemap der 17 Produktbereiche. Mit den Ebenen führt ein Klick auf `#zoom-XX`; die Zeilen `#pb-XX` der Tabelle bleiben Sprungziele der Themenseiten.
- **Ebene 2** (`#zoom-XX`):
  - Treemap der Produktgruppen je Ansicht und Format, in der Farbe des Produktbereichs.
  - Darunter die Aufwandsarten des Produktbereichs als schmaler gestapelter Balken je Ansicht mit Tabelle.
  - Eine Tabelle der Produktgruppen mit Organisationseinheit und Seite im PDF.
  - Ein Klick auf eine Produktgruppe führt auf `#pg-1-XX-YY`.
- **Ebene 3** (`#pg-1-XX-YY`): die sechs Aufwandsarten der Produktgruppe als Balken je Ansicht und Tabelle (Ist 2023, Plan 2025, Plan 2026) mit Fundstelle. Damit die Seite klein bleibt, gibt es hier keine Treemap. Ein Brotkrumenpfad „Alle Produktbereiche › 04 Kultur und Wissenschaft › 1.04.07 Stadtarchiv“ führt zurück.
- **Ohne Skript:** Alle Abschnitte liegen in `.hh-karten`; `:target` zeigt den gewählten, die Auswahlknöpfe wechseln die Ansicht auf allen Ebenen. Auf dem Telefon werden die Tabellen zu Listen mit Spaltennamen.
- **Sonderfälle:**
  - Negative Werte (nur im Ist) haben keine Fläche und kein Balkenstück; die Tabelle nennt sie wörtlich, z. B. Transferaufwendungen PB 09 im Ist 2023 −84.508 €.
  - Produktgruppen mit 0 € in einer Ansicht stehen nur in der Tabelle. Sind alle gezeigten Werte 0, gibt es keine Ebene 3, so bei 10 Produktgruppen.
  - Bei geändertem Namen steht „Name in Haushaltsplan 2023/2024: …“. Das betrifft 1.01.04, 1.04.07 und 1.04.08; Phase 0 hatte nur PB 03, 04 und 12 verglichen.
  - 1.01.29 Gebäudemanagement (SGB): Die PDF nennen nicht, welche Gebäude dort bewirtschaftet werden. Die Liste der Transferaufwendungen nennt nur „SGB Betriebskostenzuschuss“ (PB01.pdf 2025/2026 S. 98). Deshalb gibt es keinen Zusatz.
- **Hinweis auf der Seite:** Aufwandsarten sind Kontenarten, keine Aufgaben; Abschreibungen fließen nicht als Geld ab. Alles ist nominal, ohne Wertung und ohne Finanzplanung.
- **Farben der Aufwandsarten:** sechs feste, ruhige Farben (`page.css`, Klassen `hh-f11` … `hh-f16`). Alle Paare bleiben auch bei Rot- oder Grünschwäche unterscheidbar (OKLab-Abstand ≥ 11). Die Namen stehen immer in der Tabelle.
- **Größe:** `haushalt/index.html` rund 780 KB (gepackt etwa 66 KB), Vorgabe höchstens etwa 800 KB. Dafür sind die Treemaps der Produktgruppen knapp gehalten: Farbe am SVG, ganzzahlige Koordinaten, Schrift über Klassen.

## Prüfbogen und Freigabe
- `data/export/haushalt/pruefbogen_haushalt_ebenen.tsv` (`haushalt-pruefbogen-ebenen`, wird nicht überschrieben): 33 Zellen über beide Ebenen mit Datei und Seite. Darin stehen:
  - alle negativen Werte der Seite;
  - die teilweise gefüllten Zeilen der Produktbereiche und zwei der Produktgruppen;
  - die drei umbenannten Produktgruppen in beiden Ausgaben;
  - eine Produktgruppe mit 0 € im Plan und die größte Produktgruppe;
  - eine Stichprobe der Ebenen 2 und 3.
- Schalter `haushaltsplan.EBENEN_FREIGEGEBEN`: Ohne Freigabe zeigt die Seite nur Ebene 1. Für die Browser-Prüfung erzeugt `tests.yml` die Seite mit `HAUSHALT_EBENEN=vorschau`.
- **Freigabe (28.10.2026):** Der Auftraggeber hat den Prüfbogen im Gespräch freigegeben. Grundlage war eine KI-Gegenprobe aller 33 Zellen über einen zweiten Leseweg (`pdftotext -layout`, Spalte über die Spaltennummern): 33 von 33 gleich, die geänderten Namen ebenso; keine Prüfung von Hand. Danach `EBENEN_FREIGEGEBEN = True`.

## Geprüft
- `tests/test_haushaltsplan.py`:
  - Lesen über Koordinaten mit selbst gebauter Probe, auch teilweise gefüllt, zweizeilig und negativ;
  - Kopf ohne Person;
  - Abbruch bei falscher Bezeichnung oder Spalte;
  - die drei Prüfsummen, auch an den Dateien im Repository.
- `tests/test_haushaltsseite.py`:
  - beide Schalterzustände;
  - jeder Sprung hat ein Ziel;
  - Sonderfälle, Summen je Ansicht und Größe der Seite.
- `tests/browser/thema.test.mjs`:
  - Klickweg über drei Ebenen und Brotkrumen zurück;
  - Ansichtswechsel auf jeder Ebene;
  - Tastatur, 1440 und 390 px ohne waagerechtes Scrollen;
  - axe ohne Verstöße.
