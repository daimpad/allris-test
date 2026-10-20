# Prompt: „allris-bonn“ – Ratsinformationen der Stadt Bonn räumlich, zeitlich und nach Akteuren erschließen

> Fassung v0.5 (20.10.2026) · Kontext: Hackathon „Hack den Stadtrat“ · Zur Ausführung in Claude Code
> Änderungen gegenüber v0.4: Startzustand „ganz Bonn“ (Abschnitt 2), Stand der Umsetzung mit Reiter „Prozesse“, Gebieten auf der Karte, Übersichtskarte und „Mitmachen in Bonn“ (Abschnitt 9), offene Punkte aktualisiert (8). Arbeitsweise im Repository: `.claude/skills/allris-bonn/SKILL.md`.

---

## 1. Rolle

Du arbeitest als Webentwickler:in mit Erfahrung in Open-Data-Pipelines und Geodaten **und** als Beauftragte:r für Bürgerbeteiligung. Technische Entscheidungen triffst du so, dass Bürger:innen ohne Verwaltungswissen Ratsinformationen finden, verstehen und einordnen können. Du arbeitest quellentreu: keine erfundenen Inhalte; jede angezeigte Information ist auf ihr Quellobjekt rückführbar. Vor jeder Phase (Abschnitt 7) legst du einen kurzen Plan vor und wartest auf Freigabe.

## 2. Festgelegte Rahmenentscheidungen

| Punkt | Entscheidung |
|---|---|
| Projektname / Repository | `allris-bonn`, öffentlich auf GitHub als `daimpad/allris-test`; die Seite heißt **RIS-Karte Bonn** |
| Veröffentlichung | Hauptadresse https://ris-bonn.datenatlas.de/ (netcup-Webhosting, Plesk-Git aus dem Branch `deploy` mit Webhook; `SITE_URL`); Spiegel auf GitHub Pages (https://daimpad.github.io/allris-test/); täglich 04:17 UTC neu erzeugt |
| Gestaltung | Leiste mit Suche (ganz Bonn, Schnellfilter) und Mega-Menüs Auswertung, Mitmachen, Daten; interaktive Angebote als deutliche Schaltflächen; Liste und Vorgang in der Breite ziehbar; Karte vollflächig, alle Flächen einklappbar darüber; Glass-Stil (DESIGN.md „Arc Browser Glass“), Akzent für Text abgedunkelt (Kontrast); Kartenhintergrund grau mit Umschalter „Farbige Karte“; Quellen stets im Akkordeon; beim Start nur das Fenster „Los geht's“ mit Tour durch alle Funktionen, Start mit der Übersicht über ganz Bonn (Stadtbezirke anklickbar, noch keine Vorlagen; seit 20.10.2026, zuvor Bonn-Zentrum); WCAG 2.1 AA |
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
- Straßenverzeichnis: umgesetzt mit OpenStreetMap (Overpass, ODbL) → `data/geo/strassen_bonn.json` mit Ortsteilen je Straße; das städtische Straßenverzeichnis liefert keine Geometrien
- **Bebauungspläne** (Geltungsbereiche, 1.128 rechtskräftige Pläne, CC0): `https://stadtplan.bonn.de/geojson?Thema=20074` – Datensatz `https://opendata.bonn.de/dataset/lage-der-bebauungspläne`; Felder Plannummer, in Kraft seit, Plan- und Begründungs-PDF. Pläne im Verfahren sind nicht enthalten.
- Sitzungen, Wahlperioden: OParl-API (`meetings`, `legislativeTerms`); Tagesordnung (`web`), Einladung und TOPs erscheinen etwa zwei Wochen vor der Sitzung; TOPs der Stadt verweisen nicht auf Vorlagen (Verknüpfung nur über OParl-Lite)

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

- Themen und Parteien: Grundversion umgesetzt (Abschnitt 9); Stichprobe der Zuordnung von Hand geprüft am 20.10.2026 (`data/export/endenich/stichprobe_themen.tsv`: 46 von 49 passend, 2 teilweise, 1 unpassend; `themen/PRUEFUNG.md`; Regeln unverändert); Punkte lassen sich nach Thema färben, die Übersichtskarte nennt je Gebiet ein auffälliges Thema (20.10.2026); offen ist die Suche im Volltext der Dokumente (abhängig von der PDF-Lizenz)
- Stufe C (Volltext, Sprachmodell) zurückgestellt, bis die Lizenz der PDFs geklärt ist
- Stichprobe zur Prüfung von Hand: `data/export/endenich/stichprobe_pruefung.tsv` (50 Vorlagen) geprüft am 20.10.2026 (41 richtig, 4 teilweise, 5 falsch; `verortung/PRUEFUNG.md`); Regel R1 (Kreuzung bestimmt den Ortsteil) umgesetzt, auf R2 verzichtet (Ortsnamen in Bautiteln meinen oft die Gemarkung, nicht den Ortsteil), R3 nicht umgesetzt; Baustellen-Stichprobe (30) geprüft; Text im Dialog „Über“ gegengelesen und ergänzt (20.10.2026)
- Eigene Domain läuft (19.10.2026), `SITE_URL` umgestellt; offen: Google Search Console (Eigentum bestätigen, Sitemap einreichen). Verbesserungsliste als GitHub-Issues #23–#35 abgearbeitet (keine offenen Issues, 20.10.2026); Datenschutzerklärung (`site/datenschutz.html`) geprüft (19.10.2026)
- Soll-Modell der Prozessebene: Übernahme aus „Bonn entscheidet“ (anster2025/bonn-entscheidet, MIT, feste Kopie) geprüft – Phase 0 `soll/phase0/BERICHT.md` (Zuordnung 99 %, Belege 18/20 bestätigt, Zuständigkeitsordnung 331/333 wortgleich); Phase 1 umgesetzt (`data/soll/`, `pipeline/soll.py`, `audit_soll.tsv`, `soll/PHASE1.md`); Phase 2 umgesetzt (Abschnitt „Nach Regelwerk (Soll)“ im Vorgang, `soll.json`, Assistent; `soll/PHASE2.md`); Phase 3 umgesetzt (Einflussregeln in „Selbst mitwirken“, `site/mitwirken.js`; `soll/PHASE3.md`); Phase 4 umgesetzt (Stichprobe `data/export/soll/stichprobe_soll.tsv` mit KI-Vorprüfung, vier Korrekturen; `soll/PHASE4.md`); Abgleich nur aus dem Hauptweg (Nachtrag Phase 4, 230577 kein Befund mehr); Belege der Ergänzungen von Hand geprüft und präzisiert (`soll/pruefung/belege_ergaenzungen.tsv`); Stichprobe von Hand geprüft (30/30 bestätigt, zwei Regeln angepasst; `soll/PHASE4.md`); Kontakt zum Autor später
- Beitrag an OParl-Lite (Felder `location`, `underDirectionOf`) als Issue auf Codeberg – nur nach Rückfrage, da nach außen wirksam
- Hackathon-Rahmen: Datum, Teilnehmende, erwartetes Ergebnisformat (Demo, Repository, Datensatz); danach Leitfaden und „good first issues“ für Teilnehmende
- Vom Auftraggeber zu erledigen: Google Search Console; Testläufe des Ratsassistenten mit Anthropic und Mistral; Entscheidung über das Issue an OParl-Lite. Das Baustellen-Archiv läuft (Branch `archiv` vorhanden, 20.10.2026)

## 9. Stand der Umsetzung (20.10.2026)

| Bereich | Umgesetzt |
|---|---|
| Phasen 0–5 (Abschnitt 7) | Exploration, Pipeline (`python -m pipeline all`), Geokodierung A/B mit Audit, Frontend, Repository mit README/LICENSE/CONTRIBUTING/Issue-Vorlagen, tägliche Aktualisierung, Verifikation und Zip-Paket |
| Geokodierung | Stufe A (OParl `location`), Stufe B (Straßen, Ortsteile, Stadtbezirke im Titel; Bebauungsplan-Nummern mit Geltungsbereich), Vererbung von übergeordneten Vorlagen (Stufe B, höchstens „mittel“); Stufe C offen |
| Prozessebene | Schritte mit Evidenzstatus (belegt, abgeleitet, nicht öffentlich, unklar), Stand (entschieden; beraten, ohne Entscheidung; in Beratung; offen; ohne Beratungsfolge), typische Wege je Vorlagenart, Audit |
| Zeitleiste | Dichte je Monat, Sitzungen, Wahlperioden, Auswahlspur, Zeitraumfilter mit URL-Zustand, Datumsaudit, Verifikation gegen die OParl-API |
| Themen und Parteien | zehn Themen (Amt, Fachausschuss, Stichwort; abgeleitet mit Fundstelle), Parteien aus Einreichenden (Bezirksfraktionen → Partei, Koalition eigene Kategorie), Filter im Gebiet und Suche über ganz Bonn (`suche.json`), URL-Zustand |
| Abonnieren und Termine | Atom-Feeds je Gebiet und je Vorlage, Sitzungskalender (Seite und `termine.ics`) |
| Offene Daten | `vorlagen.geojson`, `dcat.jsonld` (DCAT-AP), Datenpaket |
| Ratsassistent (BYOK) | Phase 0 (Anbieterprüfung, 18.10.2026): Anthropic (mit `anthropic-dangerous-direct-browser-access`), Mistral, OpenRouter, OpenAI, Gemini, Groq erlauben Browseraufrufe; v0.1 unterstützt Anthropic, Mistral, OpenRouter und lokale Modelle; OParl-Lite-MCP später. Phase 1: Werkzeugschicht `site/chat/tools.js` mit Daten aus `pipeline/chat.py`. Phase 2: Adapter (`providers.js`), Chat-Kern (`core.js`), Schlüsselverwaltung (`keys.js`), CSP mit SRI; Tests mit nachgebildeten Anbietern. Phase 3: Systemprompt v0.2 (`site/chat/systemprompt.md`, 13 begründete Änderungen gegenüber v0.1) mit Platzhaltern aus dem Datenstand. Phase 4: Oberfläche (Fläche „Assistent“, KI-Hinweis, Einstellungen, gestreamte Antworten mit bereinigtem Markdown, Quellenkarten, Markierung unbelegter Drucksachen, Protokoll, Kopplung mit Karte und Vorgang, Kontext Gebiet/Zeitraum abschaltbar). Phase 5 (begonnen): Fragenkatalog (36 Fragen, 7 Kategorien) und Auswerteskript `eval/run.mjs`; Läufe mit Anthropic und Mistral durch den Auftraggeber. Lizenz OParl-Lite: CC BY 4.0 (der Chatbot-Entwurf nennt irrtümlich CC BY-NC) |
| Einstieg | Startfenster „Los geht's“ (Liste und Zeitleiste eingeklappt, außer der Link enthält Filter oder Zeitraum); Tour in 15 Schritten (`site/tour.js`: abgedunkelte Umgebung, pulsierender Rahmen und Punkte, Beispielvorgang aus Bonn-Zentrum, wenn noch kein Gebiet gewählt ist, Tastatur, reduzierte Bewegung); Start mit der Übersicht über ganz Bonn (20.10.2026) |
| Bebauungspläne und Baustellen | Phase 0 (19.10.2026, `baustellen/phase0/BERICHT.md`); Phase 1: Methode B3 (556 Vorlagen mit Plannummer, 321 eindeutig → Konfidenz hoch, Vorrang vor Titel-Ortsbezügen), Audit, Planregister `plaene.json`, Änderungsprotokoll; Baustellen: Lizenz CC0 laut Auftraggeber, Datensätze nicht mehr im Katalog, Anfrage an opendata@bonn.de versandt am 19.10.2026 (`baustellen/ANFRAGE_opendata_bonn.md`); Phase 2: tägliches Archiv (`pipeline/baustellen.py`, Workflow `baustellen.yml`, Branch `archiv`) mit Zustand je Baustelle, Ereignisprotokoll und Momentaufnahmen, ab 19.10.2026; Phase 3: Kandidaten Beschluss ↔ Baustelle (`pipeline/kandidaten.py`, Kriterien räumlich ≤ 150 m, zeitlich, Straße, Amt/Thema, Bau-Stichwort passend zur Maßnahme; Audit `baustellen_kandidaten.tsv`; Stichprobe 30, KI-Vorprüfung: hoch 9/9, mittel 2/21 plausibel; Freischaltung nur nach Prüfung von Hand, `baustellen/PHASE3.md`; Stichprobe von Hand geprüft 19.10.2026: „hoch“ nur für Baubeschlüsse, dann 6/6 plausibel); Phase 4: Ebene Bebauungspläne mit Planchronik (BauGB-Soll, URL `plaene=1`, `plan=`), Ebene und Zeitleistenspur Baustellen (`baustellen-seite` → `baustellen.json`, URL `baustellen=1`, `baustelle=`), Station „Mögliche Umsetzung“ nur für Konfidenz hoch (nach Prüfung der Stichprobe freigeschaltet, Hinweis „vorläufig“ entfallen, 19.10.2026), Werkzeuge `suche_bebauungsplan`, `suche_baustellen`; Phase 5: Datenpaket mit Plänen, Protokollen, Audits, Stichprobe, Archivprotokoll und Berichten, DCAT-Distributionen, Lizenzzeilen (`baustellen/PHASE5.md`) |
| Auffindbarkeit, Impressum | Favicons und Web-Manifest, Beschreibung, canonical, Open Graph mit Vorschaubild, strukturierte Daten (schema.org), `noscript`, `404.html`, `robots.txt` und `sitemap.xml` aus `SITE_URL` (`pipeline/seo.py`); „Über“ nennt Damian Paderta als Ersteller (Hackathon „Hack den Stadtrat“), Kontakt, Impressum und Datenschutz (nozilla.de/impressum, eigene Seite datenschutz.html); Schrift und Leaflet lokal (`site/fonts/`, `site/vendor/`), extern nur OSM-Kacheln |
| Reiter „Prozesse“ | Schritt 1 (20.10.2026): Verfahren (15 Arten aus dem Soll-Modell als Bahnendiagramm oder Liste, Schritte, Fristen, Wege zum Mitwirken, Zahl der Vorgänge und Beispiele) und Gremien (Organigramm oder Liste, Zuständigkeit laut ZustO, Sitzungen, Filter); `site/prozesse.js`, `pipeline/prozessarten.py` → `prozessarten.json`, URL-Zustand, Tour-Schritt; Schritt 2 (20.10.2026): Ämter (52 aktive Ämter und Stellen, gruppiert nach Amtsnummer, abgeleitet; Dezernate fehlen in der Quelle; Ratsbüro und Bürgerbüro mit Hinweis „formal federführend“ und fachlich zuständigen Ämtern laut Stellungnahmen; Abteilungen, beratende Gremien, Filter; URL `amt=`) |
| Gebiete auf der Karte | Farbstärke der Flächen nach Vorlagen der letzten 12 Monate (fünf Stufen, Legende), Zahl in der Beschriftung, beim Überfahren Gesamtzahl und auffälliges Thema (`pipeline/gebietszahlen.py`, abgeleitet); Glaseffekt beim Überfahren; Stadtbezirke (herausgezoomt mit Namen; Klick zoomt hinein und zeigt die Ortsteile mit Namen) und Ortsteile (Klick lädt das Gebiet wie das Dropdown) als Flächen anklickbar, „Ganz Bonn ansehen“ (20.10.2026) |
| Mitmachen in Bonn | Fläche je Stadtbezirk: nächste Sitzungen, berechnete Einreichungsfristen (abgeleitet), Fristen-Zeitstrahl und Wege nach dem Regelwerk mit Rechtsgrundlagen (`site/beteiligung.js`, URL `mitmachen=1`, `bezirk=`; 20.10.2026) |
| Ideen aus Abschnitt 6 offen | Kurzfassungen (Sprachmodell; sinnvoll erst mit Volltexten, abhängig von der PDF-Lizenz), Themen als eigene Flächenebene, Beitrag an OParl-Lite (nur nach Rückfrage); umgesetzt sind Stadtteil-Abo, Sitzungskalender, Beteiligungshinweise („Selbst mitwirken“, „Mitmachen in Bonn“), Gremien- und Ämterkarte (Reiter „Prozesse“), Farbe nach Thema, Linked-Open-Data-Export und Rückmeldung zur Verortung |
