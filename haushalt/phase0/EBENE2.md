# Haushalt – Phase 0 der zweiten Ebene: Aufwandsarten und Produktgruppen (28.10.2026)

**Anlass:** Die Seite `haushalt/` zeigt die ordentlichen Aufwendungen (Zeile 17) der 17 Produktbereiche als Treemap (`haushalt/PHASE2.md`). Der nächste Schritt ist eine zweite Ebene beim Hineinzoomen, aus denselben PDF.

**Frage:** Lassen sich (1) die Aufwandsarten (Zeilen 11–16) und (2) die Teilergebnispläne der Produktgruppen zuverlässig auslesen, und gehen die Prüfsummen auf? (3) Gibt es eine tiefere Gliederung? (4) Wie hoch sind Aufwand und Risiko?

**Datenstand:** PDF laut `data/haushalt/STAND.json`, am 28.10.2026 neu geladen (SHA-256 gleich): alle 17 Produktbereiche und der Gesamtergebnisplan 2025/2026 (806 Seiten), dazu als Stichprobe PB 03, 04 und 12 sowie der Gesamtergebnisplan 2023/2024. Gelesen mit `pdftotext -bbox` (Wortkoordinaten). Die Prüfskripte liegen nur in der Sitzung, nicht im Repository.

## Ergebnis: beide Gliederungen vollständig lesbar, alle Prüfsummen der Zeile 17 gehen auf
- **Aufbau:** Jedes PB-PDF beginnt mit dem Teilergebnisplan des Produktbereichs (S. 1–2) und dem Teilfinanzplan (S. 3). Danach folgen je Produktgruppe Teilergebnisplan, Teilfinanzplan A und B und teils eine Liste der Transferaufwendungen. Jeder Teilergebnisplan hat genau zwei Seiten: Zeilen 1–18 auf der ersten, 19–31 auf der zweiten (167 von 167 Plänen 2025/2026). Die Zeilen 11–17 stehen also immer auf einer Seite.
- **(1) Aufwandsarten:** Die Zeilen 11 Personal, 12 Versorgung, 13 Sach- und Dienstleistungen, 14 bilanzielle Abschreibungen, 15 Transfer und 16 sonstige ordentliche Aufwendungen haben in allen Plänen dieselben Nummern und Namen.
- **(2) Produktgruppen:** 2025/2026 gibt es 150 Produktgruppen mit Teilergebnisplan. Je PB: 01: 27, 02: 13, 03: 10, 04: 14, 05: 10, 06: 7, 07: 4, 08: 3, 09: 8, 10: 4, 11: 2, 12: 8, 13: 5, 14: 3, 15: 6, 16: 6, 17: 20. Fünf weitere Nummern haben nur einen Teilfinanzplan (1.01.11, 1.02.09, 1.06.07, 1.15.04, 1.15.06), z. B. „Kfz- und Gerätemanagement bis 2012“ (PB01.pdf S. 33). Der Kopf nennt Nummer, Kurzname, Organisationseinheit (bei 138 von 155 Nummern ein Amt), Profitcenter und eine verantwortliche Person.

  | Prüfung (Toleranz 9 € je Spalte) | 2025/2026, 17 PB | 2023/2024, PB 03, 04, 12 |
  |---|---|---|
  | Zeilen 11–16 = Zeile 17, Produktbereich | 136 von 136 | 24 von 24 |
  | Zeilen 11–16 = Zeile 17, Produktgruppen | 1.200 von 1.200 | 256 von 256 |
  | Summe der 17 PB, Zeilen 11–17 = Gesamtergebnisplan | 56 von 56 (höchstens 4 €) | nicht geprüft |
  | Summe der PG = PB, Zeilen 10–18 | 1.224 von 1.224 | 216 von 216 |
  | Summe der PG = PB, Zeilen 27, 29, 31 (interne Leistungen) | 405 von 408 | 72 von 72 |
  | PB-Werte der Zeilen 10, 17, 18 = `produktbereiche.tsv` | 255 von 255 | 45 von 45 |

- **Leere Zellen:** Zählen leere Zellen als 0, gehen alle Summen auf. 2025/2026 sind in den Zeilen 11–16 auf PB-Ebene 51 von 816 Zellen leer. PB 16 hat keine Werte für Personal, Versorgung und Abschreibungen, PB 17 keine für Personal und Versorgung. Auf PG-Ebene sind 1.906 von 7.200 Zellen leer (26 %). Teilweise gefüllt sind 2 Zeilen bei den PB (PB 09 Zeile 15, PB 16 Zeile 13) und 88 bei den PG; in der Stichprobe 2023/2024 sind es 0 und 18. Bei diesen Zeilen bricht das bisherige Verfahren ab (`haushaltsplan.zeile` liest die Werte der Reihe nach). Über die Koordinaten ist die Spalte eindeutig: Der rechte Rand der Zahl liegt 31–32 pt rechts der Spaltennummer, auf Seite 2 von PB 14 und 16 nur 2 pt.
- **Stabilität (PB 03, 04, 12):** Die 32 Produktgruppen haben in beiden Ausgaben dieselben Nummern. Der Ansatz 2024 (Zeilen 11–17) ist in beiden Ausgaben gleich (224 von 224 Zellen). Zwei Namen haben sich geändert:
  - 1.04.07: „Z. f. Stadtgesch. u. Erinnerungskulturen“ heißt jetzt „Stadtarchiv“.
  - 1.04.08: „Stadtmuseum“ (Ansatz 2023 und 2024 sowie Planung bis 2027 je 0 €, pb04.pdf 2023/24 S. 35) heißt jetzt „Stadtm., Gedenkstätte, Zentrale Projekte“ (Ansatz 2025: 1.343.826 €, PB04.pdf 2025/26 S. 34). Die Nummer ist gleich, der Inhalt ein anderer; eine Ursache nennt das PDF nicht.
- **(3) Tiefere Ebene:** Produkte, Konten oder Kostenstellen enthalten die PDF nicht. Die Köpfe nennen nur Produktbereich und Produktgruppe: 755 Seiten tragen eine Profitcenter-Nummer, keine eine Nummer der Form 1.xx.yy.zz, und die Wörter „Konto“ und „Kostenstelle“ kommen nicht vor. Tiefer gehen nur zwei Teile; beide wurden nicht ausgelesen:
  - **Liste der Transferaufwendungen** für die Planjahre 2025 und 2026: Empfänger oder Zweck mit Ansatz, 74 Seiten bei 72 PG. Eine grobe Probe ergab bei 64 PG für 2025 dieselbe Summe wie Zeile 15. Bei den Pflichtleistungen enthält die Liste nur einen Teil, z. B. 1.05.02 mit 1,35 von 117,7 Mio. € (PB05.pdf S. 7 und 11).
  - **Teilfinanzplan B** „Investitionseinzelmaßnahmen“: rund 290 Seiten, nur Investitionen, kein Aufwand.

## Grenzen und Fallstricke
- **Negative Werte:** Sie kommen nur in den Ist-Spalten vor. Im Ist 2023 betrifft das die Transferaufwendungen von PB 09 (−84.508 €, PB09.pdf S. 1) sowie der PG 1.03.02 (−14.000 €), 1.03.03 (−12.543 €, PB03.pdf S. 9 und 13) und 1.09.04 (−86.000 €, PB09.pdf S. 22). Zeile 17 einer PG ist nur im Jahr 2022 negativ, z. B. 1.04.14 „Beethoven 2020“ mit −516.170 € (PB04.pdf S. 59). Eine Treemap kann negative Werte nicht als Fläche zeigen.
- **Nullen und kleine Flächen:** 11 PG haben im Plan 2025 und 2026 je 0 €, 12 im Ist 2023. 7 PG liegen unter 0,1 % ihres PB.
- **Interne Leistungen:** Die Zeilen 27–28 sind nicht in Zeile 17 enthalten. Die einzige Abweichung zwischen PG und PB liegt in PB 09, Ergebnis 2022, Zeile 27: PB 1.298.762 €, Summe der PG 1.987.553 € (PB09.pdf S. 2).
- **Deutung:**
  - Die Namen sind gekürzt (21 von 150 mit Abkürzungspunkt, z. B. „Wohnr.sich.,-vers./Hilfe Wohn.losigkeit“), und die PDF erläutern sie nicht.
  - Manche PG fassen viel zusammen, z. B. 1.01.29 „Gebäudemanagement (SGB)“: Plan 2026 122,2 Mio. €, 40 % von PB 01, ohne Personalaufwand (PB01.pdf S. 94). Die Seite sagt bisher nur, das Gebäudemanagement habe einen eigenen Wirtschaftsplan.
  - Aufwandsarten sind Kontenarten, keine Aufgaben; Abschreibungen fließen nicht als Geld ab.
  - Die Personennamen im Kopf der PG werden nicht gebraucht.
- **Nicht geprüft:** die übrigen 14 PB der Ausgabe 2023/2024, die Ausgabe 2021/2022 und die Transferlisten im Einzelnen.

## Optionen zur Entscheidung
1. **Aufwandsarten je Produktbereich** (17 × 6 Werte je Ansicht): Lesen über Koordinaten, Prüfsumme gegen Zeile 17 und den Gesamtergebnisplan, Prüfbogen.
   - Aufwand: etwa ½ Tag.
   - Risiko: gering, alle Prüfsummen gehen auf.
   - Grenzen: eine negative Zelle im Ist 2023.
2. **Produktgruppen je Produktbereich** (150 Werte je Ansicht): zusätzlich Abgleich der Nummern zwischen den Ausgaben und Umgang mit Nullen, Kurznamen und Umbenennungen.
   - Aufwand: 1–1,5 Tage.
   - Risiko: gering bei den Beträgen, mittel bei der Deutung.
3. **Beides** (Produktbereich → Produktgruppe → Aufwandsart; 900 Werte je Ansicht):
   - Aufwand: 1,5–2 Tage.
   - Risiko: mehr kleine und leere Flächen, drei negative PG-Zellen im Ist 2023. Ohne Skript braucht jede Ebene eigene Treemaps.
4. **Transferlisten als Ergänzung** (Empfänger, nur Plan 2025/2026):
   - Aufwand: eine eigene Phase 0.
   - Offen: Vollständigkeit der Listen und Namen von Personen.
