# Prompt: „Ratskarte Bonn“ – Ratsinformationen räumlich, zeitlich und nach Akteuren erschließen

> Entwurf v0.1 · Kontext: Hackathon „Hack den Stadtrat“ (Bonn) · Zur Ausführung in Claude Code

## 1. Rolle

Du arbeitest als Webentwickler:in mit Erfahrung in Open-Data-Pipelines und Geodaten **und** als Beauftragte:r für Bürgerbeteiligung. Du triffst technische Entscheidungen so, dass Bürger:innen ohne Verwaltungswissen die Informationen finden, verstehen und einordnen können. Du arbeitest quellentreu: keine erfundenen Inhalte, jede angezeigte Information ist auf ihre Quelle rückführbar.

## 2. Ausgangslage

- Die Stadt Bonn veröffentlicht ihre Ratsinformationen im ALLRIS; eine OParl-Schnittstelle existiert.
- Die eigentlichen Inhalte (Vorlagen, Anträge, Niederschriften) liegen überwiegend als PDF vor. Für Außenstehende sind sie schwer zu finden, zu lesen und zu filtern.
- Ein Ortsbezug ist in den Daten **nicht strukturiert** vorhanden: Der OParl-Typ `Location` ist im Spiegel derzeit leer (0 Einträge). Ortsbezüge stehen nur im Titel oder im Volltext.

## 3. Datenquellen

| Quelle | Inhalt | Hinweise |
|---|---|---|
| OParl-Lite Bonn – https://oparl.bonn.machdenstaat.de/ | Lesbarer Spiegel des ALLRIS, ca. 200.000 Objekte (Stand 03.09.2026): Vorlagen, Sitzungen, Tagesordnungspunkte, Beratungen, Dateien, Gremien, Personen, Mitgliedschaften | Inhalte unter **CC BY-NC 4.0**; Bestand wächst rückwirkend, ist unvollständig |
| MCP-Server – `claude mcp add --transport http oparl-bonn https://oparl.bonn.machdenstaat.de/mcp` | 11 Tools, u. a. `search_papers`, `get_paper`, `get_paper_meetings` (Beratungsfolge mit Ergebnis), `search_fulltext` (Volltextsuche in PDFs, deutsch gestemmt), `get_file_text`, `search_meetings`, `get_meeting`, `search_organizations`, `get_organization`, `search_persons`, `get_person` | Für Exploration und Prototyping; für Massenabruf die akkumulierte Datei bzw. GraphQL-API nutzen |
| Akkumulierte OParl-Lite-Datei | Alle Ratsinformationsdaten in einer Datei | **URL/Format noch zu klären** |
| Quellcode – codeberg.org/machdenstaat/oparl-lite-2 (GPL-3.0), codeberg.org/machdenstaat/stadt-bonn-oparl (Crawler) | Datenmodell, Crawler | Datenmodell vor Implementierung lesen |
| Geobasisdaten | Stadtbezirke, Ortsteile, Straßenverzeichnis, Adressen | Open-Data-Portal Bonn bzw. OpenStreetMap; Quelle und Lizenz dokumentieren |

**Bekannte Lücken im Spiegel** (im Code berücksichtigen, nicht überdecken): Beratungsfolge verweist auf die Sitzung, nicht direkt auf das Gremium; Tagesordnungspunkte sind nicht immer mit der Vorlage verknüpft; Mitgliedschaften unvollständig; Einreicher:innen selten erfasst; federführende Ämter stehen meist nur im PDF.

## 4. Ziel

Eine öffentliche Webanwendung, die Ratsinformationen in **drei Dimensionen** erschließt – jeweils mit Quellenangabe:

1. **Räumlich (Wo?)** – Karte aller Vorlagen mit Ortsbezug; Filter nach Stadtbezirk und Ortsteil (Pilot: **Endenich**, Stadtbezirk Bonn), wo möglich feiner auf Straßen- oder Objektebene.
2. **Zeitlich (Wann? Wo steht das Verfahren?)** – Für jede Vorlage eine einfache Prozesslinie: Einreichung → Beratungen in Gremien → Beschluss / Vertagung / Kenntnisnahme → Folgevorlagen (Änderungsanträge, Stellungnahmen). Der aktuelle Stand ist hervorgehoben.
3. **Akteursbezogen (Wer?)** – Welche Gremien (Rat, Ausschüsse, Bezirksvertretung, Beiräte), Fraktionen und Verwaltungsstellen/Ämter sind zu welchem Zeitpunkt womit befasst?

## 5. Funktionale Anforderungen

### 5.1 Karte
- Marker bzw. Flächen je Vorlage; Clustering bei hoher Dichte.
- Filter: Stadtbezirk/Ortsteil, Zeitraum, Vorlagenart (Antrag, Bürgerantrag, Beschlussvorlage, Anfrage …), Gremium, Status, Stichwort.
- Detailansicht beim Anklicken: Titel, Nummer, Art, Datum, Kurzbeschreibung, Prozesslinie, beteiligte Akteure, Link zum Original-PDF im ALLRIS.

### 5.2 Geokodierung (Kernproblem)
- Ortsbezüge aus Titel und Volltext extrahieren (Straßennamen, Plätze, Gebäude, Bebauungsplannummern, Ortsteilnamen) und gegen Straßenverzeichnis/Geodaten abgleichen.
- Jede Verortung erhält **Methode und Konfidenz** (z. B. „Straßenname im Titel“, „Ortsteil im Volltext“, „manuell bestätigt“). Unsichere Treffer werden als solche angezeigt.
- Vorlagen ohne Ortsbezug bleiben in einer Listenansicht auffindbar („stadtweit / ohne Ortsbezug“).
- Keine Verortung privater Adressen natürlicher Personen (z. B. aus Bürgeranträgen).

### 5.3 Prozesslinie
- Datenbasis: `get_paper_meetings` (Beratungsfolge, Ergebnis) und über-/untergeordnete Vorlagen aus `get_paper`.
- Darstellung als horizontale Linie mit Stationen (Gremium, Datum, Ergebnis); kommende Sitzungen als offene Stationen.
- Federführende Ämter nur anzeigen, wenn sie aus dem Dokument belegbar sind; Fundstelle angeben.

### 5.4 Quellen und Transparenz
- Jedes angezeigte Datum mit Herkunft: OParl-Objekt-ID, Link zum Original, Abrufdatum.
- Abgeleitete Informationen (Geokodierung, ggf. automatische Zusammenfassungen) sichtbar als solche kennzeichnen.

## 6. Ergänzende Ideen (zur Priorisierung)

- **Stadtteil-Abo**: RSS/Atom-Feed oder E-Mail-Benachrichtigung „Neue Vorlagen in Endenich“ bzw. „Status meines Antrags hat sich geändert“.
- **Sitzungskalender** der zuständigen Bezirksvertretung mit Tagesordnung und öffentlichen Punkten.
- **Beteiligungshinweise**: Wo kann ich mich einbringen? (Einwohnerfragestunde, Anregungen und Beschwerden nach § 24 GO NRW, öffentliche Sitzungen).
- **Glossar und Gremienkarte**: Was macht eine Bezirksvertretung, ein Fachausschuss, der Rat? Zuständigkeiten in einfacher Sprache.
- **Verständliche Kurzfassungen** (optional, LLM-gestützt) mit deutlicher Kennzeichnung und Link zum Originaltext.
- **Themen-Layer**: Verkehr, Bauen, Grün, Schule, Soziales – als zusätzliche Filterebene.
- **Linked-Open-Data-Export** der angereicherten Daten (z. B. GeoJSON, RDF/DCAT-AP-Beschreibung des Datensatzes), damit Dritte darauf aufbauen.
- **Rückmeldung zu Geokodierung**: Nutzer:innen können falsche Verortungen melden (Issue-Formular), um die Datenqualität gemeinschaftlich zu verbessern.
- **Barrierefreiheit** (WCAG 2.1 AA), mobile Nutzung, Listenalternative zur Karte.

## 7. Vorgehen in Claude Code (phasenweise, nach jeder Phase Rückfrage)

0. **Exploration (ohne Code)**: Datenmodell aus dem Codeberg-Repo und über den MCP-Server prüfen; Stichprobe Endenich (Vorlagen mit „Endenich“ in Titel/Volltext); Bericht über Datenqualität und Anteil verortbarer Vorlagen.
1. **Datenpipeline**: Import der akkumulierten Datei, Normalisierung, Verknüpfung Vorlage ↔ Beratung ↔ Sitzung ↔ Gremium.
2. **Geokodierung**: Extraktion und Abgleich, mit Konfidenzwerten und Audit-Protokoll (TSV).
3. **Frontend**: Karte (z. B. MapLibre GL oder Leaflet mit OSM-Kacheln), Filter, Detailansicht, Prozesslinie.
4. **Öffentliches GitHub-Repository**: README (Ziel, Datenquellen, Lizenzen, Grenzen), LICENSE, CONTRIBUTING, Issue-Vorlagen für Hackathon-Teilnehmende, ggf. Deployment über GitHub Pages.

## 8. Rahmenbedingungen

- **Lizenzen klären**: Die Spiegeldaten stehen unter CC BY-NC 4.0, der Quellcode von OParl-Lite unter GPL-3.0. Code-Lizenz des neuen Projekts und Umgang mit (abgeleiteten) Daten im Repository vorab festlegen; Namensnennung umsetzen.
- **Datenschutz**: Keine Personendaten über das hinaus, was öffentlich und mandatsbezogen ist; keine Verortung von Privatpersonen.
- **Sprache**: Oberfläche auf Deutsch, verständlich, ohne Werbesprache.
- **Ergebnisse**: Als Zip-Paket ausliefern; Audit-Protokolle als TSV.

## 9. Offene Punkte

- URL und Format der akkumulierten OParl-Lite-Datei
- GitHub-Account/Organisation, Projektname, Code-Lizenz
- Pilotumfang (nur Endenich oder direkt ganz Bonn)
- Hosting (statisch vs. mit Backend) und Aktualisierungsrhythmus
- Einsatz von LLMs für Extraktion/Zusammenfassung zulässig?
