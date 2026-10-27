# Haushaltsdaten – Phase 0: Prüfung des Materials (27.10.2026)

**Anlass:** Die Themenseiten nennen bisher keine Beträge (`kultur/phase0/BERICHT.md`, `pipeline/themenseiten/haushalt.py`). Es bleibt die Frage, ob es offene, maschinenlesbare Haushaltsdaten gibt.

**Frage:** Gibt es offene Haushaltsdaten der Stadt? Lassen sich Beträge je Produktbereich über mehrere Jahre und neben den Vorlagen zeigen, ohne zu bewerten?

**Datenstand:** Abrufe am 27.10.2026 von opendata.bonn.de (DCAT `catalog.xml`, Datensatzseiten, Dateien), bonn.de (Haushalt, Haushaltspläne 2021/22 bis 2025/26, Jahresabschlüsse), offenerhaushalt.de, Landesdatenbank NRW, OParl-Lite. Nicht erreichbar aus der Sitzung: ckan.open.nrw.de und der interaktive Haushalt (primary.axians-ikvs.de); beide Verbindungen brachen ab.

## Ergebnis: offene Tabellen nur bis 2021/22, aktuelle Pläne nur als PDF (gut auslesbar)
- **opendata.bonn.de:** 80 Datensätze in „Öffentliche Verwaltung, Haushalt und Steuern“, alle CC0 (cc-zero). Die maschinenlesbaren Haushaltsdaten enden mit dem Entwurf 2021/2022 (letzte Änderung 15.12.2020):

  | Datensatz | Format | Inhalt |
  |---|---|---|
  | Haushalt Finanzen Plandaten | ZIP (85 MB, 17 CSV, 1,16 GB) | Plan 2008–2024 je Profitcenter × Konto × Kostenstelle, 0,2–1,0 Mio. Zeilen je Jahr |
  | Haushaltsplanentwurf 2021/2022 | CSV | „Plandaten 2021 bis 2025“, enthält aber nur das Jahr 2025 (Version 5); dazu Investitionen 2021–2025 je Finanzstelle |
  | Haushaltsplanentwurf 2017/18, 2015/16 | XLSX/CSV | Planwerte je Produktgruppe, 2015–2024 |
  | Profitcenter-, Konten-, Finanzpositionen-Metadaten | XLSX (Stand 2016) | Profitcenter → Produktbereich |

  Satzungen, Vorberichte, Produktpläne, Eckdaten und Controllingberichte bis 2019/20 gibt es nur als PDF oder DOC. Zu 2023/24, 2025/26, 2027/28 und zu den Jahresabschlüssen gibt es keinen Datensatz.
- **Mängel der Dateien:** Im ZIP ist „Plan 2022“ byte-gleich mit „Plan 2021“ (Jahr 2021). Kopfzeilen und Spalten wechseln 2020. Die Codierung ist Latin-1 mit deutschem Zahlformat. Die Bedeutung der „Version“ (5, 8) ist nicht beschrieben. Der Inhalt passt zu den Plan-PDFs: Ansatz 2020 je Produktbereich auf 0,2 Mio. € gleich (PB 03 51,3; 04 73,7; 12 91,6).
- **bonn.de:** Haushaltspläne 2021/22, 2023/24 und 2025/26 (genehmigt 19.05.2025) mit je 39–50 PDF, darunter je ein PDF pro Produktbereich 01–17 (2025/26: 806 Seiten). Die Seiten nennen keine Lizenz. Jahresabschlüsse 2012–2025 gibt es nur als PDF (2025 als Entwurf, Rat 09.07.2026). Den interaktiven Haushalt (Axians IKVS) gibt es ab 2021; ob er eine Ausfuhr bietet, ließ sich nicht prüfen.
- **Entwurf 2027/2028:** Weder auf bonn.de noch im Ratsinformationssystem (OParl-Lite: drei Treffer für „2027/2028“, darunter 261064). Laut Pressemitteilung 08.09.2026 gilt eine Haushaltssperre (Prognose Defizit 2026: 167,5 statt 123,4 Mio. €). Laut Pressemitteilung 03.10.2026 gibt es weitere Konsolidierungsmaßnahmen der Klausur, z. B. Prüfung des Schauspiels und Kürzungen im Klimaplan.
- **Gliederung:** 17 Produktbereiche, Produktgruppen, Teilergebnis- und Teilfinanzpläne mit festen Zeilen 1–31. Die Profitcenter-Nummer enthält Amt, Produktbereich und Produktgruppe (141000401 = Amt 41, PB 04, PG 01) und ist seit 2016 unverändert. Damit ist eine Verbindung zur Federführung (`underDirectionOf`) möglich.
- **PDF-Auszug (Probe):** Die PDFs haben eine Textebene (Foxit, getaggt). Zeile 17 der 17 PDFs 2025/26 summiert sich je Spalte auf den Gesamtergebnisplan (1.797,1 zu 1.797,0 Mio. € im Jahr 2025). Ordentliche Aufwendungen (Zeile 17, vor internen Leistungen, nominal, Mio. €):

  | PB | Plan 2022 (HH 21/22) | Ist 2022 | Ist 2023 | Plan 2025 | Plan 2026 |
  |---|---|---|---|---|---|
  | 03 Schulträgeraufgaben | 63,9 | 68,0 | 70,1 | 77,9 | 84,7 |
  | 04 Kultur und Wissenschaft | 78,5 | 77,1 | 80,2 | 89,2 | 92,8 |
  | 10 Bauen und Wohnen | 19,9 | 32,4 | 35,9 | 35,5 | 34,9 |
  | 12 Verkehrsflächen, ÖPNV | 86,7 | 83,9 | 101,2 | 127,5 | 135,3 |
  | 13 Natur und Landschaft | 31,2 | 31,5 | 33,7 | 37,0 | 38,2 |

  Jedes Plan-PDF enthält zwei Ist-Jahre, den Ansatz des Vorjahres, zwei Planjahre und drei Jahre Finanzplanung. Aus drei Ausgaben lässt sich eine Ist-Reihe 2018–2023 bilden.
- **IT.NRW (Landesdatenbank, dl-de/by-2.0):** Statistik 71717 „Rechnungsergebnisse, Sektor Kommunen“ mit Ein- und Auszahlungen (Ist) nach 104 Produktgruppen und 442 Gebietseinheiten, 2009–2024. Dazu kommt die Kassenstatistik 71517 je Quartal. Der Webservice lehnt den Gastzugang ab (Code 15); nötig ist eine Registrierung oder die Ausfuhr über die Oberfläche.
- **offenerhaushalt.de:** Das Projekt ist abgeschlossen und wird nicht mehr aktualisiert. Bonn ist dort mit 2017–2024 enthalten, auf Grundlage der Plandaten oben.

## Grenzen (was irreführen würde)
- **Plan und Ist:** Plan und Ist weichen ab, z. B. PB 10 im Jahr 2022: Plan 19,9, Ist 32,4. Auch der „Ansatz“ desselben Jahres ändert sich zwischen den Ausgaben. Die Finanzplanung 2027–2029 im Haushalt 2025/26 ist kein Entwurf 2027/28 und durch die Sperre und die Klausur überholt.
- **Umgliederungen:** In der CSV-Reihe springt 2017 PB 03 von 77 auf 45 Mio. € und PB 01 von 115 auf 204 Mio. €. Die Ursache ist in den Daten nicht dokumentiert. Interne Leistungsbeziehungen (PB 04 im Jahr 2025: 12,7 Mio. €) und der globale Minderaufwand verschieben Summen.
- **Weitere Verzerrungen:** Alle Werte sind nominal (ohne Preisbereinigung). Aufwand ist nicht gleich Auszahlung; Investitionen stehen getrennt im Teilfinanzplan. Gebäude der Schulen und Bühnen liegen zum Teil beim Städtischen Gebäudemanagement (eigener Wirtschaftsplan).
- **Themen und Produktbereiche:** Sie decken sich nicht 1:1. Wohnen und Bauen liegt in PB 09 und 10, Klima in PB 13 und 14 sowie im Abfall in PB 11. Haushaltsanträge (z. B. 139 Vorlagen zu 240986) nennen Produkte und Beträge nur im Text. Eine Verbindung zu den Vorlagen geht daher nur über das Amt oder den Produktbereich, nicht je Antrag (keine Zitate).
- **Landesdaten:** Statistische Produktgruppen sind nicht die Bonner Produkte. Die Daten sind etwa zwei Jahre alt; Vergleiche zwischen Städten hängen von der Ausgliederung ab (Eigenbetriebe, Anstalten öffentlichen Rechts).

## PDF-Auszug: Aufwand und Risiko
- **Aufwand:** etwa 1–2 Tage für einen Auszug der Zeilen 10, 17, 18 und 29 je Produktbereich und Produktgruppe aus drei Ausgaben (rund 2.400 Seiten). Der Auszug braucht Spaltenpositionen statt Leerzeichen, weil leere Zellen die Spalten verschieben, und eine Prüfsumme gegen den Gesamtplan je Ausgabe.
- **Risiko:** gering auf Ebene der Produktbereiche (Prüfsumme stimmt), mittel auf Ebene der Produktgruppen. Neue Ausgaben brauchen jeweils einen Durchlauf von Hand. Die Lizenz der PDFs ist nicht angegeben.
- **Alternative:** eine Anfrage an opendata@bonn.de nach CSV-Dateien im bisherigen Schema (Profitcenter × Konto) für 2023/24, 2025/26, den Entwurf 2027/28 und die Ist-Werte, mit der Nutzungsfreigabe der PDFs.

## Optionen zur Entscheidung
1. **Beträge je Produktbereich auf den Themenseiten (PDF 2021/22–2025/26):** Ist und Plan in getrennten Spalten, Zeile und Seite als Quelle, nominal, ohne Wertung und ohne Finanzplanung ab 2027.
   - Aufwand: 1–2 Tage, dazu ein Prüfbogen.
   - Grenzen: Lizenz unklar, Zuordnung Thema → Produktbereich nur grob, Entwurf 2027/28 fehlt bis zur Einbringung.
2. **Anfrage an die Stadt (CSV und Lizenz):**
   - Aufwand: gering (Entwurf einer Nachricht).
   - Grenzen: Antwort ungewiss. Bis dahin keine Beträge oder Option 1 als Übergang.
3. **Landesdaten IT.NRW 71717 als Vergleich:** Ist-Auszahlungen je Produktgruppe 2009–2024 für Bonn und vergleichbare Städte, dl-de/by-2.0.
   - Aufwand: 1 Tag; Registrierung für den Webservice nötig.
   - Grenzen: Auszahlungen statt Aufwand, etwa zwei Jahre Verzug, Vergleich nur mit Hinweisen zur Ausgliederung.
4. **Status quo:** Keine Beträge, dazu Links auf die PDFs je Produktbereich und auf den interaktiven Haushalt.
   - Aufwand: Stunden.
   - Grenzen: keine Zahlen auf der Seite.

## Entscheidungen (27.10.2026)
- Option 1: Beträge je Produktbereich aus den PDF auf den Themenseiten, Ist und Plan getrennt, mit Fundstelle; je Themenseite ein Produktbereich (Kultur 04, Schule 03, Verkehr 12, Wohnen 10, Klima 13); keine Finanzplanung ab 2027.
