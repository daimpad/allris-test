# Haushalt – Erträge, Ergebnis und je Einwohner (02.11.2026)

**Grundlage:** `phase0/ERWEITERUNG.md`, Optionen 1 und 2.

**Entscheidungen des Auftraggebers (02.11.2026):**
- Ergebnis vor internen Leistungen (Zeile 18).
- Je Einwohner mit den Zahlen von IT.NRW je Jahr: Ist mit dem 31.12. seines Jahres, Plan mit dem jüngsten Stand (31.12.2024).
- Direkt veröffentlichen ohne Prüfbogen; Prüfung durch den Auftraggeber danach. Die Werte stammen aus `data/haushalt/produktbereiche.tsv` (Zeilen 10 und 18), deren Prüfsummen schon in Phase 0 aufgingen.

**Umsetzung** (`pipeline/haushaltsseite.py`):
- Abschnitt „Erträge und Ergebnis“ unter der Tabelle der Aufwendungen.
- Treemap des Zuschussbedarfs im jüngsten Plan, breit und hoch. Flächen haben nur die 14 Produktbereiche mit negativem Ergebnis; die Überschüsse (11, 15, 16) sind in der Bildunterschrift genannt und stehen in der Tabelle. Ein Klick führt zur Zeile der Ergebnistabelle (`#erg-XX`).
- Zwei Tabellen: Ergebnis (Zeile 18) und ordentliche Erträge (Zeile 10), je Ist 2023, Plan 2025 und Plan 2026, jede Zelle mit Betrag je Einwohner (abgeleitet).
- Lesehilfe ergänzt um Ergebnis, Produktbereich 16, interne Leistungen und je Einwohner. Hinweis auf die Einwohnerzahl der Haushaltssatzung (340.226, rund 5 % kleinere Werte).
- Einwohnerzahlen in `EINWOHNER` mit Quelle; Lizenzzeile in `data/LICENSE-DATA.md`.

**Prüfung:**
- Summen wie im Gesamtergebnisplan 2025/2026 (S. 2): Plan 2026 Erträge 1.776,1 Mio. €, Ergebnis −108,0 Mio. €. Erträge minus Aufwendungen ergeben je Ansicht das Ergebnis.
- Beispiel Schulträgeraufgaben (PB 03): Plan 2026 −49,3 Mio. €, −152 € je Einwohner (49.254.097 / 323.336); Ist 2023 −35,8 Mio. €, −111 € je Einwohner.
- Tests in `tests/test_haushaltsseite.py`; axe ohne Verstöße bei 1440 und 390 px.
- Die Seite wächst roh um 27 KB auf 823 KB, gepackt um 4 KB auf 75 KB. Die Vorgabe im Test steigt von 800 auf 850 KB.

**Offen** (Phase 0, Optionen 3–7): Veränderung Plan gegen Ist, Ist 2024 aus dem Jahresabschluss, Ertragsarten, Investitionen, Einzelmaßnahmen.
