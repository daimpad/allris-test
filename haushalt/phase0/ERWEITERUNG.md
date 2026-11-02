# Haushalt – Phase 0 der Erweiterung: Veränderung, Erträge, Investitionen, je Einwohner (01.11.2026)

> **Entscheidung des Auftraggebers (02.11.2026):** Wenn der Haushalt an der Reihe ist, zuerst Ergebnis, Erträge und Beträge je Einwohner (Optionen 1 und 2) aus vorhandenen Daten.

**Anlass:** Die Seite `haushalt/` zeigt die ordentlichen Aufwendungen (Zeile 17) der 17 Produktbereiche mit Produktgruppen und Aufwandsarten (`haushalt/PHASE2.md`, `PHASE3.md`). Der Auftraggeber hat „Haushalt erweitern“ gewählt.

**Frage:** (1) Trägt ein Vergleich Plan 2026 gegenüber Ist 2023 je Produktbereich und Produktgruppe? (2) Lassen sich Erträge (Zeilen 1–10) und Ergebnis (Zeile 18) lesen und prüfen wie die Aufwandsarten? (3) Welche Zeilen der Teilfinanzpläne A und B sind verlässlich, enthalten sie Heikles? (4) Welche Einwohnerzahl passt? (5) Aufwand, Risiko, Reihenfolge.

**Datenstand:** PDF laut `data/haushalt/STAND.json` (SHA-256 gleich): 17 Produktbereiche und Gesamtplan 2025/2026; aus 2023/2024 PB 01, 03, 04, 12, 16 und Gesamtplan. Am 01.11.2026 geladen: Haushaltssatzung und Vorbericht 2025/2026, Jahresabschluss 2023 Teil 1, Jahresabschluss 2024 Teil 2 (bonn.de), Kommunalprofil Bonn von IT.NRW (Stand 15.01.2026). Gelesen mit `pdftotext -bbox`; die Prüfskripte liegen nur in der Sitzung.

## Ergebnis: Erträge und Investitionen vollständig lesbar, alle Prüfsummen gehen auf; der Vergleich Plan–Ist braucht Hinweise
| Prüfung (Toleranz 9 € je Spalte) | 2025/2026, 17 PB | 2023/2024, 5 PB |
|---|---|---|
| Zeilen 1–9 = 10 und 10 − 17 = 18, PB / PG | je 136/136, 1.200/1.200 | je 40/40, 520/520 |
| Summe der PG = PB, Zeilen 1–10 und 18 | 1.496/1.496 (höchstens 6 €) | 440/440 |
| Summe der 17 PB = Gesamtergebnisplan, Zeilen 1–10, 17, 18 | 96/96 (höchstens 9 €) | nicht geprüft |
| Gelesen = `produktbereiche.tsv` (10, 17, 18) und `produktgruppen.tsv` (17) | 255/255, 750/750 | 75/75, 325/325 |
| Teilfinanzplan A: 1–5 = 6, 7–12 = 13, 6 − 13 = 14 (PB / PG) | je 170/170, 870/870 | je 50/50, 440/440 |
| Teilfinanzplan A: Summe der PG = PB, Zeilen 1–14 | 2.380/2.380 (höchstens 2 €) | 700/700 |
| Teilfinanzplan A: Summe der 17 PB = Gesamtfinanzplan, Zeilen 18–31 | 112/112 (höchstens 3 €) | nicht geprüft |

- **(1) Gleiche Ausgabe, gleiche Gliederung:** Ist 2023, Plan 2025 und Plan 2026 stammen alle aus dem Haushaltsplan 2025/2026. Beide Ausgaben haben dieselben 150 Nummern; der Ansatz 2024 steht in beiden und ist überall gleich (153 Zellen der PB, 1.050 der PG). Das Ist 2023 ist der festgestellte Jahresabschluss (Rat 12.12.2024): 1.659.370.772,26 € (Jahresabschluss 2023 Teil 1, S. 9) zu 1.659.370.773 € (gepp.pdf 2025/2026 S. 2). Die Vorjahresspalte des Jahresabschlusses 2024 (Teil 2, ab S. 8) trifft Zeile 17 bei 17/17 PB und 141/141 PG auf höchstens 2 €.
- **(1) Was den Vergleich verzerrt:**
  - Der globale Minderaufwand (2026: 37,5 Mio. €) steht nur im Plan, in Zeile 30 von PB 01 (PB01.pdf S. 2), nicht in Zeile 17. Summe Zeile 17: Ist 2023 1.659,4, Plan 2026 1.884,1 Mio. € (+13,5 %; mit Minderaufwand +11,3 %; abgeleitet).
  - Plan und Ist desselben Jahres weichen in beide Richtungen ab: Ansatz 2022 1.507,8 zu Ist 1.558,7, Ansatz 2023 1.698,9 zu Ist 1.659,4 Mio. € (gepp.pdf beider Ausgaben, S. 2); je PB 2023 von −25 % (PB 07) bis +87 % (PB 17) (abgeleitet).
  - Frühere Jahre werden nicht auf neue Inhalte umgerechnet; Ursachen nennen die PDF nicht:
    - 1.04.08 „Stadtm., Gedenkstätte, Zentrale Projekte“: Ist 2023 0 €, Plan 2026 1.274.986 € (PB04.pdf S. 34);
    - 1.05.11 Schwerbehindertenrecht nach SGB IX: Ist 2023 29,5, Ansatz 2024 55,1, Plan 2026 8,7 Mio. €, fast nur Transferaufwand (PB05.pdf S. 30);
    - 1.01.16 Personalmanagement: Personalaufwand Ist 2023 15,5, Ansatz 2024 67,6, Plan 2026 33,5 Mio. € (PB01.pdf S. 50).
  - Weitere Sonderfälle (Zeile 17, Ist 2023 → Plan 2026): 10 PG mit 0 € in beiden Ansichten; 1.15.09 0 → 308.000 € (PB15.pdf S. 25); 1.16.04 11.134 € → 0 (PB16.pdf S. 13); 1.15.08 Beethovenhalle 0,68 → 5,97 Mio. € (PB15.pdf S. 21); 1.14.03 Umweltvorsorge 1,25 → 7,03 Mio. € (PB14.pdf S. 13).
  - Umbenannt sind nur 1.01.04, 1.04.07, 1.04.08; bei den ersten beiden laufen die Beträge weiter.
  - Plan 2026 ist der Ansatz der Satzung (Rat 20.03.2025), keine Prognose; laut Pressemitteilung vom 08.09.2026 erwartet die Stadt für 2026 ein höheres Defizit (`haushalt/phase0/BERICHT.md`).
- **(2) Erträge und Ergebnis:**
  - Zeilen 10 und 18 je PB stehen schon in `produktbereiche.tsv`. Die Zeilen 1–9 lassen sich wie die Aufwandsarten über Koordinaten lesen; Bezeichnungen und Prüfsummen stimmen.
  - Leer sind 331 von 765 Zellen der PB und 4.366 von 6.750 der PG (Zeilen 1–9, ohne Finanzplanung); Zeile 9 „Bestandsveränderungen“ ist überall leer. Negativ sind in den Ansichten nur 1.01.28, Zeile 6, Ist 2023 −748.432 € (PB01.pdf S. 87) und 1.09.01, Zeile 2, −8.502 € (PB09.pdf S. 4).
  - **Lesart:** Erträge und Aufwendungen stehen positiv. Ein negativer Wert in Zeile 18 heißt bei der Stadt „Zuschussbedarf“, ein positiver „Überschuss“ (Jahresabschluss 2024 Teil 2, S. 1). Im Plan 2026 haben PB 11 (+18,4), 15 (+5,3) und 16 (+853,9 Mio. €) einen Überschuss, bei den PG 9; die Summe der PB ist −108,0 Mio. € (= gepp.pdf S. 2).
  - PB 16 trägt 1.021,0 der 1.776,1 Mio. € Erträge, darunter 800,6 der 862,1 Mio. € Steuern (abgeleitet). Erträge je PB zeigen daher vor allem die Finanzierung, nicht die Aufgaben.
  - **Interne Leistungen:** Die Zeilen 27 und 28 ergeben über alle PB je 289,8 Mio. € (Plan 2026) und heben sich auf, verschieben aber Beträge: PB 01 erhält 187,6 Mio. € (PB01.pdf S. 2), PB 03 trägt 50,0 Mio. € (PB03.pdf S. 2); sein Ergebnis ist −49,3 Mio. € vor (Zeile 18) und −99,1 Mio. € nach internen Leistungen (Zeile 29).
- **(3) Investitionen:**
  - **Teilfinanzplan A** (S. 3 jedes PB, dazu 87 PG): nur Investitionstätigkeit, Zeilen 1–14. Zwei der zehn Spalten sind Verpflichtungsermächtigungen (VE 2025, 2026), also Zusagen, keine Zahlungen.
  - Plan 2026: investive Auszahlungen 368,6 Mio. €, davon Finanzanlagen 177,0 Mio. € (48 %, abgeleitet), vor allem 1.01.29 Gebäudemanagement (SGB) 99,6 Mio. € (PB01.pdf S. 96) und 1.16.04 Forderungsverwaltung 70,0 Mio. € (PB16.pdf S. 15). PB 03 Schulträgeraufgaben: 0,9 Mio. € (PB03.pdf S. 3).
  - **Teilfinanzplan B** (Maßnahmen oberhalb der Wertgrenzen): 293 Seiten, rund 880 Maßnahmen, 301 mit Ansatz 2025 oder 2026. Eigene Zeilennummern (1 Investitionszuwendungen, 7 Baumaßnahmen, 8 bewegliches Anlagevermögen, 12 Saldo) und zwei Spalten mehr („bisher bereitgestellt“, Gesamt). Die Maßnahmen decken die Auszahlungen ohne Finanzanlagen weitgehend (Plan 2026: 185,8 von 191,6 Mio. €, abgeleitet); Finanzanlagen und viele Einzahlungen stehen nur in Teil A.
  - Auf 6 Seiten von Teil B ist die Schrift versetzt, z. B. PB12.pdf S. 48 (Maßnahme ohne Namen, Ziffern gesperrt: „- 1.0 0 0“); weiter PB02.pdf S. 42 und 54, PB06.pdf S. 23, PB12.pdf S. 53, PB16.pdf S. 19.
  - **Personen:** Die Maßnahmen heißen meist nach Straße mit Bezirk („Endenicher Allee BN“), Gebäude oder Zweck. Unter den rund 840 Bezeichnungen 2025/2026 steht kein Name einer Privatperson. Personen kommen vor in Namen von Orten und Stiftungen („Stiftungskapital Peter Kemper“, PB17.pdf S. 13; die PG 1.17.03 heißt schon so) und in zwei Posten zu Verträgen mit Einzelnen: „Leibrenten“ (PB01.pdf S. 90) und „Theater Zuschuss gem Intendantenvertrag“ (PB04.pdf S. 50). Der Kopf jeder PG-Seite nennt auch hier eine verantwortliche Person; sie wird nicht gelesen.
- **(4) Einwohner:**

  | Zahl | Stichtag, Grundlage | Fundstelle |
  |---|---|---|
  | 321.351 | 15.05.2022, Summe der Zensus-Zellen (Kontextdaten) | `kontext/phase0/BERICHT.md` |
  | 322.221 / 321.680 / 323.336 | 31.12.2022 / 2023 / 2024, Fortschreibung Basis Zensus 2022 | IT.NRW, Kommunalprofil Bonn, S. 5 |
  | 335.760 | 30.06.2024, „Amtliche Bevölkerungszahl nach dem Ergebnis des Zensus“ (Basis nicht genannt) | Haushaltssatzung 2025/2026, S. 1 |
  | 340.226 | 31.12.2024, eigene Fortschreibung, Hauptwohnung | Haushaltssatzung 2025/2026, S. 1 |

  Plan 2026 je Einwohner: 5.827 € mit 323.336, 5.538 € mit 340.226 Einwohnern (abgeleitet; 5,2 % Unterschied). Laut Vorbericht ergab der Zensus 2022 rund 11.000 Einwohner weniger, mit Folgen für die Schlüsselzuweisungen (vorbe.pdf S. 21).

## Grenzen und Fallstricke
- **Plan gegen Ist über drei Jahre:** Ein Ansatz ohne Minderaufwand steht gegen ein gebuchtes Ergebnis, dazu drei Jahre Preisentwicklung (nominal). Eine Veränderung sagt nicht, ob eine Aufgabe ausgebaut oder verringert wurde. Prozent sind bei 0 €, negativen oder sehr kleinen Ausgangswerten nicht sinnvoll.
- **Investitionen, Plan und Ist:** Das Ist liegt weit unter dem Ansatz: 2022 164,0 zu 444,7, 2023 169,0 zu 359,0 Mio. € (gepp.pdf beider Ausgaben, S. 5).
- **Gebäudemanagement:** Die Zahlungen an das SGB stehen als Finanzanlage in PB 01; das SGB hat einen eigenen Wirtschaftsplan, die PDF nennen keine Gebäude (`haushalt/PHASE3.md`). Wie viel Schulbau darin steckt, ist offen.
- **Ergebnis vor oder nach internen Leistungen:** Beide Lesarten sind belegt und weichen je PB stark ab; die Seite muss eine wählen und sie benennen.
- **Je Einwohner:** Der Wert hängt um bis zu 5 % von der Zahl ab. Leistungen nutzen auch Menschen aus dem Umland; der Stichtag liegt vor den Planjahren. Bei PB 16 (Steuern, Umlagen) und bei Transfers an bestimmte Gruppen ist „je Einwohner“ keine Last je Person. Die Zensus-Zellen sind für Anteile im Ortsteil gedacht, einzelne sind geheim gehalten.
- **Neueres Ist:** Der Jahresabschluss 2024 (festgestellt 12.03.2026) enthält Teilergebnisrechnungen je PB und PG mit Ist 2024 (Teil 2, 674 S.; Beträge mit Cent, sechs Spalten). Der Entwurf 2025 (Rat 09.07.2026 zur Kenntnis) ist nicht festgestellt und nicht geprüft.
- **Nicht geprüft:** die übrigen 12 PB 2023/2024 für Erträge und Investitionen; Teil B 2023/2024 nur in 5 PB (303 Maßnahmen, ohne Fehler, ohne Privatpersonen).

## Optionen zur Entscheidung
1. **Ergebnis und Erträge je PB aus vorhandenen Daten** (Zeilen 10, 18; Tabelle mit Lesehilfe, Zuschussbedarf als Ansicht nur für die 14 PB mit negativem Ergebnis).
   - Aufwand: ½ Tag mit Prüfbogen. Risiko: gering. Grenzen: interne Leistungen, PB 16 als Finanzierung.
2. **Je Einwohner als zusätzliche Spalte** (abgeleitet; Ist 2023 mit IT.NRW 31.12.2023, Plan mit 31.12.2024, dl-de/by-2.0).
   - Aufwand: Stunden. Risiko: gering bei klarer Beschriftung.
3. **Veränderung:** a) Plan 2026 gegenüber Ist 2023 mit Hinweisen, ohne Prozent bei 0 € oder negativem Ausgangswert, Sonderfälle gekennzeichnet; b) dazu Vergleiche gleicher Art (Plan 2026 zu Plan 2025, Ist 2023 zu Ansatz 2023).
   - Aufwand: je ½ Tag. Risiko: mittel bei der Deutung (keine Wörter wie „Kürzung“).
4. **Ist 2024 (und Entwurf 2025) aus den Jahresabschlüssen**, damit Plan und Ist desselben Jahres vergleichbar werden.
   - Aufwand: kurze Phase 0, dann 1–1,5 Tage (neuer Leser, Prüfsumme gegen die Gesamtergebnisrechnung). Grenzen: Entwurf 2025 nicht festgestellt.
5. **Ertragsarten (Zeilen 1–9) je PB und PG** wie die Aufwandsarten.
   - Aufwand: ½–1 Tag mit Prüfbogen. Risiko: gering bei den Beträgen. Grenzen: viele leere Zellen.
6. **Investitionen aus Teilfinanzplan A** (Ein- und Auszahlungen, Saldo je PB und PG; ohne VE und Finanzplanung).
   - Aufwand: 1 Tag mit Prüfbogen. Risiko: gering bei den Beträgen, mittel bei der Deutung (Finanzanlagen, SGB, Ist etwa halb so hoch wie der Plan).
7. **Einzelmaßnahmen aus Teilfinanzplan B** (später; über Straßennamen evtl. auf der Karte, abgeleitet).
   - Aufwand: 1,5–2 Tage und eine Liste aller Bezeichnungen zur Durchsicht. Risiko: mittel (versetzte Seiten, eingerückte Namen, Verträge mit Einzelnen).

**Vorschlag zur Reihenfolge:** 1 mit 2, dann 3 (a und b), dann 6, dann 5; 4 vor 3, wenn Plan und Ist desselben Jahres gewünscht sind; 7 zuletzt.

**Offene Fragen:** Ergebnis vor (Zeile 18) oder nach internen Leistungen (Zeile 29) oder beide? Nur Plan 2026 gegen Ist 2023 oder auch Vergleiche gleicher Art und die Jahresabschlüsse 2024/2025? Eine Einwohnerzahl je Jahr (IT.NRW) oder eine für alle Ansichten, und sollen die Zahlen der Satzung genannt werden? Finanzanlagen als eigene Fläche oder nur in der Tabelle? Einzelmaßnahmen mit Bezeichnung, und wie mit „Leibrenten“ und „Intendantenvertrag“ umgehen?
