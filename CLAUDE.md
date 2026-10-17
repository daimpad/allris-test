# Prompt: „allris-bonn“ – Ratsinformationen der Stadt Bonn räumlich, zeitlich und nach Akteuren erschließen

> Entwurf v0.3 (17.10.2026) · Kontext: Hackathon „Hack den Stadtrat“ · Zur Ausführung in Claude Code
> Änderungen gegenüber v0.1: Datenquellen nachrecherchiert und korrigiert (Abschnitt 3), Entscheidungen aus Rückfragen eingearbeitet (Abschnitt 2), Geokodierung in drei Stufen präzisiert (5.2), Vorgehen mit Prüfpunkten (7).

---

## 1. Rolle

Du arbeitest als Webentwickler:in mit Erfahrung in Open-Data-Pipelines und Geodaten **und** als Beauftragte:r für Bürgerbeteiligung. Technische Entscheidungen triffst du so, dass Bürger:innen ohne Verwaltungswissen Ratsinformationen finden, verstehen und einordnen können. Du arbeitest quellentreu: keine erfundenen Inhalte; jede angezeigte Information ist auf ihr Quellobjekt rückführbar. Vor jeder Phase (Abschnitt 7) legst du einen kurzen Plan vor und wartest auf Freigabe.

## 2. Festgelegte Rahmenentscheidungen

| Punkt | Entscheidung |
|---|---|
| Projektname / Repository | `allris-bonn`, öffentlich auf GitHub |
| Code-Lizenz | MIT |
| Räumlicher Umfang | Ganz Bonn; Pilot und erste Auslieferung: Ortsteil **Endenich** (Stadtbezirk Bonn) |
| Einsatz von Sprachmodellen | Zulässig für Ortsextraktion und Kurzfassungen – mit Kennzeichnung, Konfidenz und Link zum Original |
| Auslieferung | Ergebnisse als Zip-Paket; Audit-Protokolle als TSV |
| Abgeleitete Daten | Aus den OParl-Lite-Volltexten abgeleitete Ortsdaten und kurze Zitate (Fundstellen) dürfen im Repository veröffentlicht werden; Quelle und Lizenz (CC BY 4.0, machdenstaat) werden je Datensatz genannt; Datendateien erhalten eine eigene LICENSE-Datei getrennt vom MIT-Code |

## 3. Datenquellen (recherchiert, Stand 17.10.2026)

### 3.1 Primärquelle: OParl-API der Stadt Bonn (ALLRIS)
- Einstieg: `https://www.bonn.sitzung-online.de/oparl/bodies` → Body 1 „Bundesstadt Bonn“ mit Listen `papers`, `meetings`, `organizations`, `persons`, `locations`
- Lizenz laut Open-Data-Portal Bonn: **CC0** (Datensatz „Ratsinformationssystem OParl-API“, tägliche Aktualisierung, ohne angehängte Dokumente)
- Umfang: 24.916 Vorlagen (Stand heute), Drucksachennummern ab 2019 (z. B. `190001`); 368 Organisationen; Paginierung `?page=N&size=100`
- Zwei Felder, die für dieses Projekt zentral sind und **im Spiegel OParl-Lite derzeit fehlen**:
  - `underDirectionOf` → federführender **Verwaltungsbereich** (`organizationType: "Verwaltungsbereich"`, z. B. „61-1 Stadtentwicklung und Statistik“, `classification: "61 Stadtplanungsamt"`). In einer Stichprobe von 500 Vorlagen bei 100 % gesetzt. Damit ist die Akteursdimension „Ämter“ strukturiert verfügbar.
  - `location` → OParl-Location mit `streetAddress`, `postalCode`, teils `subLocality` (Stadtbezirk) und `geojson` (Punktkoordinate, WGS84). In der Stichprobe bei **39 von 500 Vorlagen (≈ 8 %)** gesetzt, überwiegend bei Bürgeranträgen (§ 24 GO NRW), „Anregungen und Beschwerden“ und zugehörigen Stellungnahmen. Für die übrigen ~92 % muss der Ortsbezug abgeleitet werden (5.2).
- `web` → Link in die ALLRIS-Oberfläche (`/public/VO020?VOLFDNR=…`); die Oberfläche selbst ist bei Direktaufruf zugriffsgeprüft, die OParl-API ist offen.

### 3.2 Spiegel und Volltexte: OParl-Lite Bonn (machdenstaat)
- Oberfläche: `https://oparl.bonn.machdenstaat.de/` – Abdeckung laut `/progress` 99,7 % der vergleichbaren Objekte (168.291 von 168.727, Stand 17.10.2026)
- **GraphQL-API**: `https://oparl.bonn.machdenstaat.de/graphql` – Listen mit `limit`/`offset`/`where`/`orderBy` für `papers`, `consultations`, `meetings`, `agendaItems`, `files`, `organizations`, `persons`, `memberships`; Volltextsuche `fileFullTextSearch(query)`; Stichwortsuche `searchPapersByKeyword(keyword)` (Treffer „Endenich“: 284 Vorlagen)
- **MCP-Server**: `claude mcp add --transport http oparl-bonn https://oparl.bonn.machdenstaat.de/mcp` – 11 Werkzeuge (`search_papers`, `get_paper`, `get_paper_meetings` = Beratungsfolge mit Ergebnis, `search_fulltext`, `get_file_text`, `search_meetings`, `get_meeting`, `search_organizations`, `get_organization`, `search_persons`, `get_person`) und 3 Prompts (`track_topic`, `trace_paper`, `prepare_meeting`); öffentlich, nur lesend, Streamable HTTP
- Lizenzen: Inhalte der Oberfläche CC BY 4.0; Code GPL-3.0 (`https://codeberg.org/machdenstaat/oparl-lite-2`); Crawler `https://codeberg.org/machdenstaat/stadt-bonn-oparl`; Teildatensatz auf Kaggle (`cgoern/stadt-bonn-allris-partial`)
- **Korrektur zu v0.1**: Eine „akkumulierte Datei“ zum Download ist weder in der README noch auf dem Server auffindbar (`/export`, `/download`, `/data` → 404). Der Massenabruf erfolgt über die GraphQL-API (paginiert) oder direkt über die OParl-API der Stadt. Die Locations sind im Spiegel noch nicht erfasst (0 Objekte).
- Bekannte Lücken im Spiegel: Beratung verweist auf die Sitzung, nicht direkt auf das Gremium; Tagesordnungspunkte nicht immer mit Vorlage verknüpft; Einreicher:innen selten erfasst; `underDirectionOf` nicht enthalten.

### 3.3 Geobasisdaten der Stadt Bonn (CC0, Open-Data-Portal)
- **Ortsteile** (51 Polygone, WGS84, Felder `ortsteil`, `ortsteil_bez`, `bezirk`, `bezirk_bez`): `https://stadtplan.bonn.de/geojson?Thema=21247` – Datensatz `https://opendata.bonn.de/dataset/flächen-der-ortsteile`
- **Stadtbezirke** (4 Polygone): `https://stadtplan.bonn.de/geojson?Thema=14574` – Datensatz `https://opendata.bonn.de/dataset/flächen-der-stadtbezirke`
- Straßenverzeichnis (Straßennamen, Herkunft): Datensatz „Straßenliste Straßennamen Straßenverzeichnis Herkunft Entstehung“ auf opendata.bonn.de / open.nrw – Ressourcen-URL und Felder (Ortsteilzuordnung? Koordinaten?) vor Nutzung prüfen
- Straßengeometrien und Adresspunkte: OpenStreetMap (ODbL; Nominatim/Photon oder lokaler Extrakt), falls das städtische Straßenverzeichnis keine Geometrien liefert; Lizenzhinweis ODbL beachten
- Bebauungspläne (Geltungsbereiche): INSPIRE/GDK-Metadatensatz vorhanden; WFS-URL noch zu ermitteln

## 4. Ziel

Eine öffentliche, statisch auslieferbare Webanwendung, die Ratsinformationen in **drei Dimensionen** erschließt – jeweils mit Quellenangabe:

1. **Räumlich (Wo?)** – Karte aller Vorlagen mit Ortsbezug; Filter nach Stadtbezirk und Ortsteil, wo belegbar auf Straßen- oder Objektebene.
2. **Zeitlich (Wann? Wo steht das Verfahren?)** – Je Vorlage eine Prozesslinie: Veröffentlichung → Beratungen (Gremium, Datum, Ergebnis) → Folgevorlagen (Änderungsanträge, Stellungnahmen der Verwaltung, Mitteilungen). Aktueller Stand hervorgehoben; kommende Sitzungen als offene Stationen.
3. **Akteursbezogen (Wer?)** – Federführendes Amt (`underDirectionOf`), befasste Gremien (Rat, Fachausschüsse, Bezirksvertretung, Beiräte), einreichende Fraktionen/Personen soweit erfasst.

## 5. Funktionale Anforderungen

### 5.1 Karte und Liste
- Punkte (Adresse/Objekt) und Flächen (Ortsteil, Bebauungsplan) je Vorlage; Clustering bei Dichte; Listenansicht als gleichwertige Alternative (Barrierefreiheit).
- Filter: Ortsteil/Stadtbezirk, Zeitraum, Vorlagenart, federführendes Amt, Gremium, Ergebnis/Status, Stichwort, Konfidenz der Verortung.
- Detailansicht: Titel, Drucksachennummer, Art, Datum, Amt, Prozesslinie, Akteure, Link zum Original (OParl-`web` und `mainFile`), Quellobjekt-IDs und Abrufdatum.

### 5.2 Geokodierung in drei Stufen (Kernaufgabe)
| Stufe | Methode | Konfidenz | Quelle |
|---|---|---|---|
| A | `location.geojson` aus der OParl-API übernehmen | hoch | Stadt Bonn |
| B | Regelbasiert: Ortsteilnamen, Straßennamen (Abgleich gegen Straßenverzeichnis), Bebauungsplan-Nummern, Hausnummern in `name` und Volltext (`get_file_text`/`fileFullTextSearch`); Zuordnung zum Ortsteilpolygon per Point-in-Polygon | mittel | abgeleitet |
| C | LLM-gestützte Extraktion aus dem Volltext mit strukturiertem Output (Ortsname, Typ, Textstelle) und anschließender Verifikation gegen Stufe B | niedrig bis mittel, stets gekennzeichnet | abgeleitet |

- Jede Verortung trägt `method`, `confidence`, `evidence` (Zitat/Fundstelle) und `source_object`.
- Vorlagen ohne Ortsbezug bleiben als „stadtweit / ohne Ortsbezug“ in der Liste.
- Audit-Protokoll der Geokodierung als TSV (Drucksachennummer, Stufe, Treffer, Konfidenz, Fundstelle, Prüfstatus).
- Datenschutz: Keine Verortung von Wohnadressen natürlicher Personen; Bürgeranträge nur auf Straßen-/Ortsteilebene darstellen, auch wenn die Quelle eine Hausnummer enthält.

### 5.3 Prozesslinie
- Datenbasis: Beratungsfolge (`consultation` in der OParl-API bzw. `get_paper_meetings`), Tagesordnungspunkt-Ergebnis, `superordinatedPaper`/`subordinatedPaper`, `underDirectionOf`.
- Darstellung als horizontale Linie mit Stationen; Ergebnistexte („beschlossen“, „vertagt“, „zur Kenntnis genommen“) wörtlich aus der Quelle, mit Glossar-Erklärung.

### 5.4 Transparenz
- Abgeleitete Informationen (Geokodierung B/C, Kurzfassungen) sichtbar als solche markiert, mit Link zum Originaltext.
- Datenstand und Lizenzhinweise (CC0 Stadt Bonn, ggf. ODbL OSM, Nennung von OParl-Lite als Werkzeug) im Footer.

## 6. Ergänzende Ideen (zur Priorisierung im Hackathon)

- **Stadtteil-Abo**: Atom-Feed oder E-Mail je Ortsteil („Neu in Endenich“) und je Vorlage („Status geändert“).
- **Sitzungskalender** der Bezirksvertretung Bonn und der Fachausschüsse mit öffentlichen Tagesordnungspunkten des Ortsteils.
- **Beteiligungshinweise**: Einwohnerfragestunde, Bürgerantrag nach § 24 GO NRW, Öffentlichkeit von Sitzungen – mit Verweis auf die zuständige Stelle.
- **Gremien- und Ämterkarte**: Zuständigkeiten in einfacher Sprache; aus `organizationType` „Gremium“ und „Verwaltungsbereich“ generiert.
- **Themen-Layer** (Verkehr, Bauen, Grün, Schule, Soziales), abgeleitet aus Amt und Stichworten.
- **Verständliche Kurzfassungen** (LLM, gekennzeichnet) je Vorlage.
- **Linked-Open-Data-Export**: GeoJSON der verorteten Vorlagen, DCAT-AP-Beschreibung des Datensatzes, optional RDF mit Verweis auf OParl-IDs.
- **Rückmeldung zur Verortung**: Melde-Link je Vorlage, der ein GitHub-Issue mit Drucksachennummer vorausfüllt.
- **Beitrag an OParl-Lite**: Erkenntnisse zu `location` und `underDirectionOf` als Issue/PR auf Codeberg einbringen, damit der Spiegel diese Felder übernimmt.

## 7. Vorgehen in Claude Code (nach jeder Phase Rückfrage)

0. **Exploration (ohne Produktionscode)**: Datenmodell beider APIs prüfen; Stichprobe Endenich (284 Vorlagen per Stichwort, zusätzlich Volltexttreffer und Vorlagen mit `location` im Ortsteilpolygon); Bericht: Anteil Stufe A/B/C, Datenqualität, Lücken.
1. **Datenpipeline** (Python oder Node, reproduzierbar): Abruf aus OParl-API (CC0) als Primärquelle, Anreicherung mit Volltexten über GraphQL; Normalisierung Vorlage ↔ Beratung ↔ Sitzung ↔ Gremium ↔ Amt; Ablage als JSON/GeoJSON/SQLite im Repository oder als Release-Artefakt.
2. **Geokodierung** nach 5.2 mit TSV-Audit; Qualitätsprüfung an einer manuell geprüften Stichprobe (z. B. 50 Vorlagen Endenich).
3. **Frontend**: Statische Seite (z. B. MapLibre GL oder Leaflet mit OSM-Kacheln), Filter, Detailansicht, Prozesslinie; WCAG 2.1 AA; mobil nutzbar.
4. **Repository `allris-bonn`** (MIT): README (Ziel, Datenquellen, Lizenzen, Grenzen, Datenstand), LICENSE, CONTRIBUTING, Issue-Vorlagen für Hackathon-Teilnehmende, GitHub Actions für Datenaktualisierung und Deployment über GitHub Pages.
5. **Verifikation**: Stichprobenprüfung gegen ALLRIS; Lizenzhinweise vollständig; Audit-TSV im Zip-Paket.

## 8. Offene Punkte

- GitHub-Account für `allris-bonn`: eigener Account des Auftraggebers (bei Ausführung per `gh auth status` prüfen; Organisation nur auf ausdrückliche Angabe)
- Ressourcen-URL und Felder des Straßenverzeichnisses; WFS der Bebauungspläne
- Aktualisierungsrhythmus (täglich wie die Quelle?) und Hosting (GitHub Pages reicht für statische Daten bis einige MB)
- Hackathon-Rahmen: Datum, Teilnehmende, erwartetes Ergebnisformat (Demo, Repository, Datensatz)
