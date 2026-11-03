# Haushalt – Erweiterung: Ist 2024 und Investitionen (03.11.2026)

**Entscheidungen des Auftraggebers (03.11.2026):** Option 4 (Ist 2024 je Produktbereich und Produktgruppe aus dem festgestellten Jahresabschluss 2024, ohne Entwurf 2025) und Option 6 (Investitionen aus dem Teilfinanzplan A, ohne Verpflichtungsermächtigungen und Finanzplanung) aus `haushalt/phase0/ERWEITERUNG.md`. Option 3 (Veränderung) rechnet der Auftraggeber später auf der Seite. Veröffentlichung erst nach Prüfbogen und Freigabe: `haushaltsplan.ERWEITERUNG_FREIGEGEBEN = False`.

## Quellen
- **Jahresabschluss 2024 Teil 2**, festgestellt am 12.03.2026: https://www.bonn.de/medien-global/amt-20-und-21/jahresabschluesse/Jahresabschluss-2024_Teil-2.pdf. Die Datei ist verlinkt auf https://www.bonn.de/service-bieten/aktuelles-zahlen-fakten/jahresabschluesse.php. Sie hat 674 Seiten, Last-Modified ist der 16.03.2026; die SHA-256 steht in `STAND.json`. Die Seitenzahlen im Prüfbogen sind Seiten der PDF; die gedruckte Zählung liegt um 184 höher (PDF-Seite 2 = „Seite 186 von 858“).
  - Gesamtergebnisrechnung: S. 2.
  - Teilergebnisrechnungen: je Produktbereich ab S. 8 (PB 01), danach je Produktgruppe.
- **Haushaltspläne 2023/2024 und 2025/2026**: je 17 PDF der Produktbereiche und `gepp.pdf`, alle SHA-256 gleich `STAND.json`. Für 2023/2024 sind die übrigen 12 Produktbereiche am 03.11.2026 nachgeladen.
  - Teilfinanzplan A: S. 3 jedes Produktbereichs und je Produktgruppe.
  - Gesamtfinanzplan: Zeilen 18–31, `gepp.pdf` S. 5–6.

## Spalten des Jahresabschlusses (Wortlaut im Kopf)
| Spalte | Kopf | `art`, `jahr` in der Datei |
|---|---|---|
| 1 | Ergebnis des Vorjahres 2023 | Ergebnis 2023 |
| 2 | fortgeschriebener Ansatz des Haushaltsjahres 2024 | Ansatz fortgeschrieben 2024 |
| 3 | davon Ermächtigungsübertragungen aus dem Vorjahr | Teil von Spalte 2 |
| 4 | Ist-Ergebnis des Haushaltsjahres 2024 | Ergebnis 2024 |
| 5 | Vergleich Ansatz/Ist (Sp. 4 ./. Sp. 2) | gilt in allen 1.422 Zellen genau: Spalte 4 − Spalte 2 |
| 6 | Ermächtigungsübertragungen in das Folgejahr | 2024 → 2025; in Aufwandszeilen negativ geschrieben |

- **Fortgeschriebener Ansatz:** Er ist nicht der Ansatz 2024 des Haushaltsplans.
  - Summe Zeile 17: 1.819,6 Mio. € fortgeschrieben zu 1.771,1 Mio. € im Plan (`produktbereiche.tsv`, in beiden Ausgaben gleich). Darin stecken 91,6 Mio. € Ermächtigungsübertragungen aus dem Vorjahr.
  - Je Produktbereich weicht er in beide Richtungen ab, z. B. PB 01 291,4 zu 319,6 Mio. € und PB 06 364,5 zu 327,6 Mio. €.
  - Die PDF nennen keine Gründe. **Entscheidung des Auftraggebers (03.11.2026):** Für „Ist 2024 zum Ansatz 2024“ gilt der Ansatz der Satzung (Haushaltsplan 2023/2024; bei den Investitionen `investitionen.tsv`, Ausgabe 2023/2024). Der fortgeschriebene Ansatz bleibt in den Dateien.
- **Zeile 18** heißt in den Teilergebnisrechnungen „Ergebnis der laufenden Verwaltungstätigkeit“, in der Gesamtergebnisrechnung und im Haushaltsplan „Ordentliches Ergebnis“. Gerechnet wird beide Male 10 − 17.

## Ergebnis
- **`data/haushalt/jahresabschluss.tsv`** (8.532 Werte): 17 Produktbereiche und 141 Produktgruppen, Zeilen 10–18, sechs Spalten.
  - `betrag_cent` als ganze Zahl in Cent: So bleiben die Beträge des PDF genau, und die Prüfsummen rechnen ohne Rundung. Die Spalte heißt anders als `betrag` (Euro) der übrigen Dateien, damit niemand sie verwechselt.
  - Leer sind 159 Zellen der Produktbereiche und 2.204 der Produktgruppen; sie stehen als 0 mit `leer = ja`.
- **`data/haushalt/investitionen.tsv`** (14.630 Werte): Zeilen 1–14, Spalten Ergebnis und Ansatz, VE und Planung weggelassen.
  - 2023/2024: 17 Produktbereiche und 88 Produktgruppen, Ergebnis 2020–2021, Ansatz 2022–2024.
  - 2025/2026: 17 Produktbereiche und 87 Produktgruppen, Ergebnis 2022–2023, Ansatz 2024–2026.
  - Leer: 690/4.257 (2023/2024) und 687/4.197 (2025/2026) Zellen der Produktbereiche/Produktgruppen.
- **Personen:** Aus dem Kopf werden wie bisher nur Nummer, Name und Organisationseinheit gelesen. Die Angabe „verantwortlich: …“ wird nicht gelesen und nicht gespeichert; ein Test prüft das an den Dateien.

| Prüfsumme je Spalte (Abbruch über der Toleranz) | Spalten | größte Abweichung |
|---|---|---|
| Jahresabschluss: Zeilen 11–16 = 17 (PB, PG, Gesamt) | 954 | 0 Cent |
| Jahresabschluss: 10 − 17 = 18 | 954 | 0 Cent |
| Jahresabschluss: Summe der PG = PB, Zeilen 10–18 | 918 | 0 Cent |
| Jahresabschluss: Summe der 17 PB = Gesamtergebnisrechnung | 54 | 0 Cent (ohne die belegte Abweichung unten) |
| Ergebnis 2023 (Sp. 1) = Ist 2023 des Haushaltsplans 2025/2026, PB 10–18 und PG 11–17 | 1.140 | 2 € |
| Teilfinanzplan A: 1–5 = 6, 7–12 = 13, 6 − 13 = 14 (beide Ausgaben) | je 1.045 | 1 € |
| Teilfinanzplan A: Summe der PG = PB, Zeilen 1–14 | 2.380 | 2 € |
| Teilfinanzplan A: Summe der 17 PB = Gesamtfinanzplan, Zeilen 18–31 | 140 | 3 € |

Toleranzen: 2 Cent innerhalb des Jahresabschlusses, 9 € gegen den Haushaltsplan und im Teilfinanzplan A.

## Befunde und Sonderfälle
- **Gesamtergebnisrechnung:** Der fortgeschriebene Ansatz 2024 der Personalaufwendungen ist dort um 28.806,75 € höher als die Summe der 17 Teilergebnisrechnungen.
  - Die Werte: 420.457.278,52 € (S. 2) zu 420.428.471,77 €. Dieselbe Differenz zeigen Zeile 17, Zeile 18 und Spalte 5.
  - Ein zweiter Leseweg (`pdftotext -layout`) ergibt dieselben Werte; alle übrigen 48 Zellen treffen genau.
  - Die Abweichung ist als `JA_ABWEICHUNG_GESAMT` festgehalten. Weicht die Gesamtrechnung anders ab oder gar nicht mehr, bricht die Prüfung ab.
- **Produktgruppen:** Im Jahresabschluss fehlen 9 Produktgruppen des Plans 2025/2026: 1.01.24, 1.02.15, 1.04.08, 1.04.13, 1.04.14, 1.09.03, 1.09.06, 1.10.06, 1.15.10. Alle neun haben im Plan 0 € im Ist 2023 und im Ansatz 2024 (Zeile 17); 1.04.08 hat erst ab 2025 Beträge. Keine Produktgruppe ist neu.
- **Name:** 1.04.07 heißt im Jahresabschluss „Zentrum für Stadtgeschichte u. Erinnerungskultur“, im Plan 2025/2026 „Stadtarchiv“.
- **Negative Aufwendungen:**
  - im Ist 2024 bei 1.03.10 (Zeile 15), 1.09.04 und 1.12.08 (Zeile 13);
  - im fortgeschriebenen Ansatz bei 1.01.28 Liegenschaftsmanagement, Zeile 13: −9.771.943,92 € (S. 97).
- **Investitionen:**
  - Die Finanzanlagen 2026 betragen bei 1.01.29 Gebäudemanagement (SGB) 99.558.600 € (PB01.pdf S. 96) und bei 1.16.04 Forderungsverwaltung 70.000.000 € (PB16.pdf S. 15).
  - PB 03 hat 940.000 € investive Auszahlungen im Plan 2026.
  - Negativ sind „sonstige Investitionseinzahlungen“ 2023 bei PB 02 (−74.603 €) und 1.02.19 (−221.550 €).
  - In 93 Zellen ist der Saldo positiv (mehr Ein- als Auszahlungen), 41 in 2023/2024 und 52 in 2025/2026.
- **Versetzte Schrift:** Auf den gelesenen Seiten gab es keine. Im Jahresabschluss ist auf S. 3 (Gesamtergebnisrechnung, Zeile 22, Spalte 5) ein Betrag umgebrochen („107.985.995,6“ und „7“); diese Zeile wird nicht gelesen. Der Leser bricht ab, wenn ein Betrag außerhalb der Tabellenzeilen steht oder eine Bezeichnung nicht passt.

## Lesen
- **Jahresabschluss** (`koordinaten_ja`): Er hat keine Spaltennummern.
  - Die Spalte eines Betrags folgt aus den Kopfwörtern „Vorjahres“, „fortgeschriebener“, „davon“, „Ist-Ergebnis“, „Vergleich“ und „Folgejahr“. Ein Betrag gehört zur Spalte, deren Kopf links von seinem rechten Rand steht; der häufigste rechte Rand je Spalte muss auf 4 pt passen.
  - Die Jahre kommen aus dem Kopf; Spalte 1 muss das Vorjahr der Spalten 2 und 4 sein.
  - Der Seitenfuß zählt nicht: Zeilen ohne Nummer, die mehr als 12 pt von jeder Tabellenzeile entfernt sind, werden übergangen.
- **Teilfinanzplan A:** Gelesen wird wie die Teilergebnispläne (`koordinaten`), mit den Spaltenarten VE und Zwischenüberschriften im selben Abstand.
- **Umbau:** `koordinaten()` ist in Teile zerlegt (`_tabelle`, `_werte`). `haushalt-ebenen` ergibt danach dieselben Dateien, Zeichen für Zeichen.

## Prüfbogen
`data/export/haushalt/pruefbogen_haushalt_erweiterung.tsv` (`haushalt-pruefbogen-erweiterung`, wird nicht überschrieben) enthält 36 Zellen mit Link `…pdf#page=N`, 19 aus dem Jahresabschluss und 17 aus dem Teilfinanzplan A. Darin stehen:
- negative Werte und teilweise gefüllte Zeilen;
- die größten Werte;
- die Finanzanlagen 1.01.29 (beide Ausgaben) und 1.16.04;
- PB 03;
- der fortgeschriebene Ansatz mit der größten Abweichung vom Plan (PB 06);
- die größte Ermächtigungsübertragung (1.04.11 Theater) und der größte Vergleich (PB 16);
- je eine Stichprobe über mehrere Produktbereiche.

Eine Gegenprobe über `pdftotext -layout` fand alle 31 gefüllten Beträge in ihrer Zeile. Die Spalte ist damit nur bei vollen Zeilen bestätigt, die Prüfung von Hand steht aus.

## Grenzen
- **Ist und Plan:** Ist 2024 und Plan sind nominal. Der fortgeschriebene Ansatz enthält Übertragungen und Veränderungen im Jahr, die die PDF nicht erklären.
- **Investitionen:** Das Ist liegt weit unter dem Ansatz (Phase 0). Die Teilfinanzrechnungen des Jahresabschlusses mit dem Ist 2024 der Investitionen (z. B. S. 10) sind nicht gelesen, weil sie nicht beauftragt waren.
- **Zeilen 1–9 und 19–31:** Die Erträge nach Arten und die Zeilen nach dem Ergebnis der laufenden Verwaltungstätigkeit sind im Jahresabschluss nicht gelesen.
- **Lizenz:** Wie beim Haushaltsplan nennt die Stadt keine Lizenz (amtliches Werk nach § 5 UrhG, Einschätzung).

## Nachtrag: Ist 2024 der Investitionen (03.11.2026)
**Entscheidung des Auftraggebers:** dazu das Ist 2024 der Investitionen aus den Teilfinanzrechnungen des Jahresabschlusses 2024 Teil 2. Schritt `haushalt-ist2024-investitionen`, Datei `data/haushalt/jahresabschluss_investitionen.tsv` (5.488 Werte, Cent, Spalten wie `jahresabschluss.tsv`).
- **Eigene Datei:** Die Zeilennummern 10–14 gibt es auch in der Ergebnisrechnung, und die Spalten 3 und 6 fehlen hier. In einer gemeinsamen Datei müsste jede Auswertung nach der Rechnung filtern. So bleibt `jahresabschluss.tsv` unverändert, und die neue Datei lässt sich über `zeile` direkt an `investitionen.tsv` anlegen.
- **Gelesen:** „Teilfinanzrechnung, Teil A: Zahlungsnachweis“ je Produktbereich (erste Seite nach der Teilergebnisrechnung, z. B. S. 10) und Produktgruppe. Teil B (Investitionseinzelmaßnahmen, 109 Seiten) ist nicht gelesen.
  - 16 Produktbereiche und 82 Produktgruppen. **PB 17 Stiftungen hat keine Teilfinanzrechnung**; im Plan 2025/2026 ist das Ist 2023 dort 0.
  - Gesamtfinanzrechnung: S. 6, Zeilen 18–31 = 1–14.
- **Zeilen:** Die Nummern sind dieselben wie im Teilfinanzplan A. In `zeile_name` steht der Wortlaut des Plans; der Wortlaut des Jahresabschlusses steht in `STAND.json`:
  - Einzahlungen: 1 „aus Zuwendungen für Investitionsmaßnahmen“, 2 „aus der Veräußerung von Sachanlagen“, 3 „… von Finanzanlagen“, 4 „aus Beiträgen u. ä. Entgelten“, 5 „Sonstige Investitionseinzahlungen“, 6 „Summe: (invest. Einzahlungen)“;
  - Auszahlungen: 7 „für den Erwerb von Grundstücken und Gebäuden“, 8 „für Baumaßnahmen“, 9 „… von beweglichem Anlagevermögen“, 10 „… von Finanzanlagen“, 11 „von aktivierbaren Zuwendungen“, 13 „Summe: (invest. Auszahlungen)“;
  - 14 „Saldo: der Investitionstätigkeit (Einzahlungen ./. Auszahlungen)“.
  - Zeile 12 kommt 2024 nirgends vor; ihr Wortlaut ist erschlossen. Leere Zeilen druckt der Jahresabschluss nicht; sie stehen als 0 mit `leer = ja` (512 Zellen der Produktbereiche, 3.293 der Produktgruppen).
- **Spalten:** dieselben sechs wie in der Ergebnisrechnung. Übernommen sind 1 (Ergebnis 2023), 2 (fortgeschriebener Ansatz 2024), 4 (Ist 2024) und 5 (Vergleich). Ohne eigene Werte bleiben 3 (davon Ermächtigungsübertragungen aus dem Vorjahr) und 6 (Ermächtigungsübertragungen in das Folgejahr).
- **Lesen:** Die Nummer steht teils mittig neben einer zweizeiligen Bezeichnung, die Beträge stehen dann in deren zweiter Zeile (z. B. Zeile 1 auf S. 10). Beträge einer Bezeichnungszeile zählen deshalb zur nächsten Nummer. Auf S. 608 (PB 16) steht im Kopf „-1“ statt 2023, und das Jahr 2024 fehlt; die Jahre gelten wie auf den übrigen Seiten (Vermerk in `STAND.json`). Die Ergebnisrechnung ergibt danach dieselbe Datei.

| Prüfsumme je Spalte | Spalten | größte Abweichung |
|---|---|---|
| 1–5 = 6, 7–12 = 13, 6 − 13 = 14 (PB, PG, Gesamt) | je 396 | 0 Cent |
| Spalte 5 = Spalte 4 − Spalte 2 | 1.386 | 0 Cent |
| Summe der PG = PB, Zeilen 1–14 | 896 | 0 Cent |
| Summe der PB = Gesamtfinanzrechnung, Zeilen 18–31 | 56 | 0 Cent (ohne die belegte Abweichung unten) |
| Ergebnis 2023 (Sp. 1) = Ist 2023 aus `investitionen.tsv` 2025/2026; fehlende Einheiten als 0 | 1.484 | 1 € |

- **Befund Gesamtfinanzrechnung:** Der fortgeschriebene Ansatz der Baumaßnahmen steht dort mit 224.361.205,29 € (S. 6, Zeile 25). Die Teilfinanzrechnungen ergeben zusammen 224.371.205,29 €, also 10.000,00 € mehr; die Zeilen 13 und 14 und Spalte 5 folgen daraus. Die Werte der zehn Produktbereiche sind über `pdftotext -layout` gegengelesen. Festgehalten ist die Abweichung als `JA_ABWEICHUNG_GESAMTFINANZ`.
- **Weiter in der Gesamtfinanzrechnung:** In Zeile 31 stehen die Spalten 3 und 6 mit dem Vorzeichen von Zeile 30 (354.593.473,79 und −404.163.885,39 €), nicht als 23 − 30 wie in den Teilfinanzrechnungen. Diese Spalten sind nicht übernommen.
- **Produktgruppen:** Nur im Plan 2025/2026 stehen 1.01.04, 1.01.21, 1.02.02, 1.04.12, 1.09.01, 1.17.03 und 1.17.16, nur im Jahresabschluss 1.01.13 und 1.04.03. Für alle ist das Ist 2023 der jeweils anderen Quelle 0.
- **Ist 2024:**
  - Finanzanlagen bei 1.01.29 Gebäudemanagement (SGB) 85.716.146,59 € (S. 104) und bei 1.16.04 Forderungsverwaltung 46.900.000,00 € (S. 623);
  - PB 03: investive Auszahlungen 6.674.039,34 € (S. 182);
  - PB 01, Zeile 2 (Veräußerung von Sachanlagen): −1.725.134,41 € (S. 10).
- **Prüfbogen-Ergänzung:** `data/export/haushalt/pruefbogen_haushalt_erweiterung_finanz.tsv` (`haushalt-pruefbogen-erweiterung-finanz`, 8 Zellen, wird nicht überschrieben). Alle 8 Beträge stehen auch im Text der Seite (`pdftotext -layout`); die Prüfung von Hand steht aus.


## Vorschau auf der Seite `haushalt/` (03.11.2026)

Sichtbar mit `ERWEITERUNG_FREIGEGEBEN` (vor der Freigabe mit `HAUSHALT_ERWEITERUNG=vorschau`); `pipeline/haushaltsseite.py`.

**Freigabe 03.11.2026:** Beide Prüfbögen (44 Zellen) vom Auftraggeber im Gespräch bestätigt; Grundlage war der KI-gestützte zweite Leseweg (44 von 44 gleich), vermerkt in der Spalte `pruefung`. Veröffentlicht auf `haushalt/` und in den Haushaltsabschnitten der Themenseiten (Ist 2024 laut Jahresabschluss, `haushaltsplan.ist_2024`).

- **Ist 2024** als vierte Ansicht (Plan 2026, Plan 2025, Ist 2024, Ist 2023) auf allen Ebenen: Produktbereiche, Erträge, Ergebnis, Aufwandsarten, Produktgruppen. Spalte 4 von `jahresabschluss.tsv`, auf Euro gerundet; Fundstelle „Jahresabschluss 2024, S. …“ mit Link auf das PDF.
- **Veränderung** der ordentlichen Aufwendungen (Zeile 17) je Produktbereich: Ist 2024 zu Ist 2023, Ist 2024 zum Ansatz 2024 der Satzung, Plan 2026 zu Plan 2025; in Mio. € und Prozent, ohne Prozent bei einem Ausgangswert bis 0 €. Hinweise: nominal, fortgeschriebener Ansatz 1.819,6 zu 1.771,1 Mio. €, Umgliederungen und globaler Minderaufwand.
- **Investitionen:** Summen der Stadt (Zeilen 6, 13, 10, 14; Ist 2023, Ist 2024, Ansatz 2024, Plan 2025, Plan 2026) und je Produktbereich die investiven Auszahlungen mit dem Anteil für Finanzanlagen und Fundstelle. Ohne Verpflichtungsermächtigungen und Finanzplanung; PB 17 ohne Teilfinanzrechnung 2024.
- **Grenzen:** die zwei Abweichungen innerhalb des Jahresabschlusses (S. 186, S. 6).
- Tabellen der Seite tragen auf dem Telefon die Spaltennamen (`data-l`).
- Prüfung: Python-Tests (`Erweiterung` in `tests/test_haushaltsseite.py`), Browser-Tests 37/37, axe ohne Verstöße bei 1440 und 390 px.
