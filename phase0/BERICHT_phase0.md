# allris-bonn – Phase 0: Explorationsbericht

Stand: 17.10.2026 · Datenbasis: OParl-API der Stadt Bonn (CC0), OParl-Lite Bonn (GraphQL), Ortsteilpolygone der Stadt Bonn (CC0), Photon (OSM, ODbL) · Kein Produktionscode; alle Zahlen reproduzierbar mit `fetch_papers.py` und den im Bericht beschriebenen Auswertungen.

## 1. Zusammenfassung

- Die OParl-API der Stadt Bonn liefert **24.912 Vorlagen** (Oktober 2019 bis 16.10.2026), vollständig mit federführendem Verwaltungsbereich (`underDirectionOf`, 100 %) und Beratungsfolge (`consultation`, 99,99 %).
- **1.816 Vorlagen (7,3 %)** tragen eine Punktkoordinate (`location.geojson`). Davon liegen 1.814 innerhalb der 51 Bonner Ortsteile, **98 in Endenich**.
- Über Titelmuster (Ortsteilname oder bekannte Straße) sind für Endenich **522 Kandidaten** identifizierbar; 98 davon mit Koordinate (hohe Konfidenz), 390 mit mittlerer, 34 mit niedriger Konfidenz. Stadtweit nennen 5.720 Titel (23 %) einen Ortsteilnamen; zusammen mit Koordinaten sind **7.085 Vorlagen (28 %)** ohne Volltextanalyse räumlich zuordenbar.
- Die Volltextbasis bei OParl-Lite ist derzeit dünn: **3.993 von 89.889 Dateien (4,4 %)** haben extrahierten Text. Stufe C (Volltext/LLM) erfordert daher eine eigene PDF-Extraktion in der Pipeline.
- Die Prozesslinie lässt sich nur aus **zwei Quellen zusammengesetzt** bauen: Die städtische API verknüpft Vorlage ↔ Gremium ↔ Rolle, aber nicht Vorlage ↔ Sitzung/Tagesordnungspunkt; OParl-Lite liefert diese Verknüpfung samt Ergebnis für bereits durchgeführte Sitzungen.

## 2. Datenbestand der städtischen OParl-API

| Kennzahl | Wert |
|---|---|
| Vorlagen (`papers`) | 24.912 (Paginierung `size=100`, 250 Seiten, Abruf ca. 2 Minuten) |
| Zeitraum (`date`) | 2019-10-07 bis 2026-10-16; Drucksachennummern ab `190001` |
| `underDirectionOf` gesetzt | 24.912 (100 %) → 145 Verwaltungsbereiche, davon 117 ohne `endDate` (aktiv); `classification` nennt das Amt (z. B. „61 Stadtplanungsamt“) |
| `consultation` gesetzt | 24.909; Felder: `organization`, `role`, `authoritative` – **kein** `meeting`/`agendaItem` |
| `location` gesetzt | 1.816 Vorlagen (1.814 mit `geojson`-Punkt); 520 Vorlagen mit mehr als einem Ort |
| `originatorPerson`/`originatorOrganization` | 0 – Einreichende stehen nur im Titel („SPD-Bezirksfraktion: …“) |
| `mainFile` | 24.896 (`accessUrl` zum PDF) |
| Organisationen | 368: 223 Gremien (48 Ratsgremien, 29 Beiräte/Kommissionen, 4 Bezirksvertretungen, Fraktionen …), 145 Verwaltungsbereiche |
| Tagesordnungspunkte (`meeting.agendaItem`) | `number`, `name`, `result`, `resolutionFile`, `public` – **kein** Verweis auf die Vorlage |

Vorlagenarten (Top 10): Stellungnahme der Verwaltung 6.787 · Beschlussvorlage 4.207 · Mitteilungsvorlage 3.375 · Änderungsantrag 2.349 · Antrag 2.191 · Große Anfrage 1.571 · Bürgerantrag § 24 GO 1.153 · TOP in nichtöffentlicher Sitzung 879 · Beschlussvorlage: Einleitung 684 · Anregungen und Beschwerden 555.

**Hinweis zur Dokumentlizenz:** Der Open-Data-Datensatz „Ratsinformationssystem OParl-API“ ist unter CC0 veröffentlicht, laut Beschreibung „ohne angehängte oder externe Dokumente“. Die PDFs selbst sind damit nicht ausdrücklich lizenziert; für Stufe C sollte das mit opendata@bonn.de geklärt werden.

## 3. Räumliche Zuordnung

### 3.1 Stufe A – Koordinaten aus der Quelle
- Point-in-Polygon gegen die 51 Ortsteile: 1.814 Punkte zugeordnet, 2 außerhalb des Stadtgebiets.
- Verteilung: Kessenich 136, Nordstadt 129, Bonn-Zentrum 127, Gronau 121, Beuel-Mitte 98, **Endenich 98**, Plittersdorf 72 … (vollständig in `stufeA_vorlagen_je_ortsteil.tsv`; 50 von 51 Ortsteilen mit mindestens einem Treffer; Summe 2.144 wegen Mehrfachzählung bei Vorlagen mit mehreren Orten).
- Koordinaten stammen überwiegend aus Bürgeranträgen (574 von 1.153 Bürgeranträgen, 50 %), „Anregungen und Beschwerden“ und zugehörigen Stellungnahmen.
- Qualitätsbefund: Die Punktkoordinate ist belastbar, die Postleitzahl im selben Objekt teils nicht (z. B. „Steinweg 35, 53121 Bonn“ im Titel, `postalCode` „53229“). Zuordnung daher über die Koordinate, nicht über PLZ.

### 3.2 Stufe B – Titelmuster (Pilot Endenich)
| Methode | Treffer | Bemerkung |
|---|---|---|
| B1: „Endenich“/„Endenicher“ im Titel | 285 | deckt sich mit der Stichwortsuche von OParl-Lite (284) |
| B2: eine von 32 Endenicher Straßen im Titel | 283 | Straßenliste aus Stufe A abgeleitet |
| B1 ∪ B2 | 518 | |
| A ∪ B1 ∪ B2 | **522** | 94 der 98 Stufe-A-Vorlagen werden auch von B erkannt |

- Fehlerquellen bei B2: Straßennamen, die mehrfach im Stadtgebiet vorkommen. Belegt: „Marienforster Steinweg“ (Bad Godesberg) wird als Endenicher „Steinweg“ erkannt. Photon meldet für 3 der 32 Straßen mehrere Lagen (Hainstraße, Pfaffenweiherweg, Robert-Havemann-Straße); generische Namen (Steinweg, Wiesenweg, Kapellenstraße, Kolpingstraße, Konradstraße) sind in der Audit-TSV als „niedrig“ markiert (34 Vorlagen).
- Verbesserung für Phase 2: vollständiges Straßenverzeichnis mit Ortsteilzuordnung (städtische Straßenliste als CSV über `stadtplan.bonn.de/csv?OD=…`, Ressourcen-ID noch zu ermitteln) statt der aus Stufe A abgeleiteten 32 Straßen; Geokodierung je Straße über Photon (`locality` liefert den Ortsteil).
- Stadtweit: 5.720 Titel nennen einen Ortsteilnamen; mit Koordinaten zusammen 7.085 Vorlagen (28 %). Straßennamen stadtweit sind noch nicht ausgewertet.

### 3.3 Stufe C – Volltext
- OParl-Lite: `fileFullTextSearch("Endenich")` → 84 Dateien, überwiegend „Öffentliches Sitzungspaket“ (Sammel-PDFs einer Sitzung, nicht einzelne Vorlagen).
- Nur 3.993 von 89.889 Dateien haben extrahierten Text. Für eine belastbare Stufe C muss die Pipeline die `mainFile.accessUrl` der 24.896 Vorlagen selbst laden und extrahieren (Lizenzfrage s. o.).
- Overpass (OSM-Rohdaten) ist aus dieser Umgebung nicht erreichbar; Photon (photon.komoot.io) funktioniert und liefert Ortsteil und Koordinate je Straße.

## 4. Akteure und Prozess (Endenich, 522 Kandidaten)

- Nach Jahr: 2019: 32 · 2020: 80 · 2021: 68 · 2022: 67 · 2023: 60 · 2024: 96 · 2025: 74 · 2026 (bis Oktober): 45.
- Federführung (`classification`): Co-Dezernat 217 · 61 Stadtplanungsamt 110 · 66 Tiefbauamt 56 · 33 Bürgerdienste 46 · 63 Bauordnungsamt 28 · 67 Amt für Umwelt und Stadtgrün 22. „Co-Dezernat“ ist eine Sammelklasse (u. a. für Fraktionsanträge), die für die Anzeige aufgelöst werden sollte.
- Gremien in der Beratungsfolge: Bezirksvertretung Bonn 404 · Rat 92 · Ausschuss für Mobilität und Verkehr 48 · Ausschuss für Wohnen, Planung und Bauen 43 · Hauptausschuss 24.
- Rollen: Kenntnisnahme 336 · Entscheidung 254 · Empfehlung 99 · Anhörung 49; 254 von 762 Beratungen sind `authoritative` (entscheidende Station).
- Prozesslinie: Die städtische API liefert Gremium und Rolle je Beratung, OParl-Lite liefert für durchgeführte Sitzungen `meeting.startDate`, `agendaItem.number` und `result` (Beispiel 191010: Bezirksvertretung Bonn, 25.08.2020, TOP 6.3, „geändert beschlossen“). Für noch nicht beratene Vorlagen (z. B. 261856) bleibt `meeting` leer. Der Join erfolgt über die OParl-URI (`idRef`).

## 5. Konsequenzen für Phase 1–3

1. **Primärquelle** bleibt die städtische OParl-API (CC0, vollständig, mit Ämtern und Koordinaten). OParl-Lite ergänzt Sitzungs-/TOP-Verknüpfung und – begrenzt – Volltexte.
2. **Geokodierung**: Stufe A sofort nutzbar (98 Vorlagen Endenich, 1.814 stadtweit). Stufe B braucht ein vollständiges Straßenverzeichnis mit Ortsteil; Konfidenzstufen und Audit-TSV wie hier fortführen. Stufe C erst nach Klärung der Dokumentlizenz.
3. **Datenmodell**: Vorlage – Beratung (Gremium, Rolle, authoritative) – Sitzung/TOP (aus OParl-Lite) – Verwaltungsbereich – Ort (Stufe, Konfidenz, Fundstelle).
4. **Anzeige**: Einreichende aus dem Titelpräfix ableiten („CDU-Bezirksfraktion-Antrag: …“), als abgeleitet kennzeichnen.
5. **Offen**: Ressourcen-URL der städtischen Straßenliste; Lizenz der PDFs; Umgang mit „Co-Dezernat“.

## 6. Dateien

- `audit_endenich_kandidaten.tsv` – 522 Zeilen: Drucksache, Datum, Art, Titel, Methode (A/B1/B2), Konfidenz, Straßentreffer, Quelladresse, Amt, Gremien mit Rolle, OParl-ID, ALLRIS-Link, PDF-Link
- `stufeA_vorlagen_je_ortsteil.tsv` – Vorlagen mit Koordinate je Ortsteil
- `verwaltungsbereiche.tsv` – 145 Verwaltungsbereiche mit Amtszuordnung
- `fetch_papers.py` – Abrufskript (paginiert, 6 parallele Verbindungen)
