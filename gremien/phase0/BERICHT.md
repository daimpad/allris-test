# Ratsmitglieder und Besetzung der Gremien – Phase 0: Prüfung des Materials (27.10.2026)

**Anlass:** Auftrag vom 27.10.2026, Personen und Mitgliedschaften aus der OParl-API zu prüfen (bisher ruft `pipeline/fetch.py` nur Organisationen, Vorlagen und Sitzungen ab).

**Frage:** Lässt sich die aktuelle Besetzung der Gremien und die Sitzverteilung nach Fraktion quellentreu und datenschutzgerecht zeigen?

**Datenstand:** OParl-API Bonn, `bodies/1/persons` (26 Seiten) und `bodies/1/memberships` (101 Seiten), abgerufen 27.10.2026 13:00 UTC; OParl-Lite GraphQL am selben Tag; Organisationen aus `data/raw/organizations.json` (18.10.2026); Stichtag „aktiv“: 27.10.2026. Skripte und Ergebnis je Gremium im Arbeitsordner der Prüfung (nicht im Repository).

## Ergebnis: Besetzung von Rat, Hauptausschuss und Bezirksvertretungen vollständig ableitbar, in Fachausschüssen nur teilweise
- **Umfang:** 2.582 Personen, 10.041 Mitgliedschaften (seit 1971). Aktiv am Stichtag: 1.579 Mitgliedschaften von 666 Personen; alle 27 laufenden Ratsgremien und Bezirksvertretungen haben aktive Mitglieder.
- **Felder der Mitgliedschaft:** `role`, `votingRight`, `organization`, `person` immer gesetzt; `startDate` 9.710 (97 %), `endDate` 8.467. `onBehalfOf` (für wen jemand im Gremium sitzt) ist **nie** gesetzt.
- **Felder der Person:** `name` immer; `familyName`/`givenName`, `status`, `web` (Link auf ALLRIS-Personenseite) 1.041; `formOfAddress`/`gender` 1.036; `affix` 738; `title` 108; **`email` 376, `phone` 260, Anschrift (`locationObject`) 262**. Kein Feld für Partei, Foto oder Beruf. Von den 666 aktiven Personen haben 76 nur einen Namen (55 davon Schriftführung, 17 Beiratsmitglieder).
- **Partei/Fraktion** nur über die Mitgliedschaft in einer Fraktions-Organisation (Klassen Fraktion, Gruppen, Einzelmandate, Bezirksfraktionen). Im Rat haben 66 von 67 Mitgliedern eine aktive Fraktion (ohne: Vorsitz, d. h. Oberbürgermeister:in).
- **Rollen** (aus den Daten, Deutung abgeleitet): „Mitglied (Stv.)“ = Stadtverordnete:r als ordentliches Mitglied (nicht Stellvertretung), „Sachkundige/r Bürger/in“, „Stellv. Mitglied“, „Beratendes Mitglied“, „Schriftführung“ (Verwaltung).
- **Sitze am Stichtag** (ordentliche Mitglieder nach Rolle, Fraktion über Mitgliedschaft; in allen Fällen `votingRight` = true):

  | Gremium | Sitze | nach Fraktion | Fraktion unbekannt |
  |---|---|---|---|
  | Rat | 67 | CDU 21, Grüne 17, SPD 8, Linke 6, AfD 4, BBB 3, Volt 2, BSW/SBI 2, FDP 2, PARTEI 1 | 1 (Vorsitz) |
  | Hauptausschuss | 22 | CDU 7, Grüne 5, SPD 2, Linke 2, je 1 FDP, Volt, AfD, BBB, BSW/SBI | 1 (Vorsitz) |
  | Kulturausschuss | 21 | 12 mit Fraktion (CDU 5, Grüne 3, je 1 SPD, Linke, FDP, BSW/SBI); 9 sachkundige Bürger:innen | 9 |
  | Mobilität und Verkehr | 21 | 14 mit Fraktion; 9 sachkundige | 7 |
  | Schulausschuss | 21 | 11 mit Fraktion; 10 sachkundige | 10 |
  | Planen, Bauen und Denkmalschutz | 21 | 14 mit Fraktion; 7 sachkundige | 7 |
  | Umwelt, Klima und Lokale Agenda | 21 | 12 mit Fraktion; 10 sachkundige | 9 |
  | BV Bonn / Bad Godesberg / Beuel / Hardtberg | je 19 | über Bezirksfraktion | 1 / 0 / 0 / 2 |

  Dazu je Fachausschuss 24–28 Stellvertretungen und 3–7 beratende Mitglieder.
- **Sachkundige Bürger:innen:** 158 aktive Personen, nur 19 davon mit einer Fraktionsmitgliedschaft. Für welche Fraktion sie benannt sind, steht nicht in der API (`onBehalfOf` fehlt). Die Sitzverteilung der Fachausschüsse ist deshalb nur für die Stadtverordneten belegbar.
- **Einreichende (Frage 3):** In der 12. Wahlperiode haben 1.086 von 1.179 Anträgen und Anfragen eine abgeleitete Fraktion mit Organisations-ID (`paper_originator`, 1.353 Fraktion/Gruppe, 161 von 170 Bezirksfraktion). Die 26 IDs sind dieselben wie in den Mitgliedschaften; 24 haben aktive Mitglieder (BSW und SBI als Einzelmandate endeten am 25.11.2025, danach Gruppe). Verbindung also auf **Fraktionsebene** möglich, auf Personenebene nicht: `originatorPerson` ist in keiner der 24.915 Vorlagen gesetzt.
- **OParl-Lite:** 2.578 Personen, 10.040 Mitgliedschaften (4 bzw. 1 weniger); E-Mail, Telefon, Anschrift und `affix` leer; 22 Mitgliedschaften ohne das Enddatum, das die Stadt schon führt. Nicht vollständiger; die städtische API ist die bessere Quelle.

## Grenzen
- **Stimmrecht:** In `persons` eingebettete Mitgliedschaften haben immer `votingRight: false` (10.041 von 10.041), die Liste `memberships` dagegen 7.848 × true. Nur die Liste ist brauchbar.
- **Bezirksvertretungen:** Neben den 19 Bezirksverordneten führt die Quelle Ratsmitglieder mit der Rolle „Stadtverordnete/r in Bezirksvertretung“ (BV Bonn 35, Bad Godesberg 12, Beuel 11, Hardtberg 3) mit `votingRight: true`; nach GO NRW nehmen sie mit beratender Stimme teil (§ 36 Abs. 6 GO NRW; geprüft 27.10.2026, zuvor irrtümlich Abs. 5). Zählung daher nach Rolle, nicht nach `votingRight`.
- **Fehlende Enddaten:** 34 aktive Mitgliedschaften begannen vor 2020, 29 hängen an beendeten Gremien (19 Gutachterausschuss, 2 Volt-Fraktion neben der Volt-Gruppe); 3 Personen haben zwei Fraktionen zugleich. Für die gewählten Gremien unkritisch, für eine Gesamtliste nicht.
- **Aktualität:** `modified` steht bei 99 % auf 01.01.2000; Änderungen sind nur durch vollständigen Abruf erkennbar (127 Seiten, rund 9 MB, wenige Minuten). Nachbesetzungen kommen laufend (Starts 23.01., 13.03., 08.05.2026).
- **Lizenz:** CC0 laut Open-Data-Portal (OParl-API); OParl-Lite CC BY 4.0. CC0 hebt den Datenschutz nicht auf: personenbezogene Daten bleiben nach DSGVO zu behandeln.

## Datenschutz (Frage 4)
- **Anzeigen (öffentliche Funktion):** Name, akademischer Titel, Rolle, Gremium, Fraktion, Beginn/Ende, Link zur ALLRIS-Personenseite (`web`) – für Rats- und Bezirksvertretungsmitglieder.
- **Weglassen:** Anschrift (rund 200 der 262 sind Einzeladressen, vermutlich privat; Berliner Platz 2 und Fraktionsbüros selten), private E-Mail und Telefon (von 466 Adressen 135 bei bonn.de, viele private Anbieter), `gender`/`formOfAddress`, Personen mit Status „Verwaltung“ und „Fraktionsgeschäftsstellen“, Schriftführung.
- **Sachkundige Bürger:innen und Einwohner:innen** (158 aktiv, 56 mit E-Mail, 26 mit Anschrift): vom Rat gewählt, aber kein Mandat aus einer Wahl. Vorschlag: nur Name und Rolle in der Besetzung des eigenen Ausschusses, ohne eigene Personenseite, ohne Suche und ohne Verknüpfung über Gremien hinweg; alternativ nur als Zahl.
- **Beiräte:** Rollen wie „Beiratsmitglied Jugend“ (29) können Minderjährige betreffen → keine Namen.

## Optionen zur Entscheidung
1. **Besetzung im Reiter „Prozesse“ (Gremien):** Sitze nach Fraktion je Gremium, Vorsitz, Liste mit Name, Rolle und ALLRIS-Link; Fachausschüsse mit Stadtverordneten nach Fraktion und sachkundigen Bürger:innen als Zahl. Aufwand: Abruf `persons`/`memberships` in `fetch.py`, Tabelle `membership` ohne Kontaktfelder, Export, Anzeige; etwa 1–2 Tage. Grenze: Rollen-Deutung und fehlendes `onBehalfOf`.
2. **Fachausschuss auf den Themenseiten:** Kasten „Wer berät mit“ mit Vorsitz und Sitzverteilung des zuständigen Ausschusses (Kultur, Mobilität, Schule, Planen, Umwelt). Aufwand gering nach Option 1. Grenze wie oben: 7–10 von 21 Sitzen ohne Fraktion.
3. **Fraktionsstärken neben Einreichenden:** Zahl der Ratssitze je Fraktion an den Filtern „Partei“ und in der Akteursangabe. Aufwand gering. Grenze: keine Kennzahlen wie „Anträge je Sitz“, um keine Bewertung nahezulegen.
4. **Werkzeug für den Ratsassistenten** (`hole_besetzung`: Gremium → Sitze, Vorsitz). Aufwand gering nach Option 1; dieselben Felder wie auf der Seite, keine Kontaktdaten.

## Entscheidungen (27.10.2026) und Umsetzung
- Besetzung im Reiter „Prozesse“ (Gremien) mit Name, Rolle, Fraktion (abgeleitet), Beginn und Link zur Personenseite, ohne Kontaktdaten; Kasten auf den Themenseiten und Werkzeug für den Assistenten in einem zweiten Schritt.
- Abruf täglich nur über `persons` (26 Seiten; die eingebetteten Mitgliedschaften gleichen der Liste `memberships` bis auf `votingRight`), Auszug `data/raw/besetzung.json` (`pipeline/besetzung.py`).
- Ohne Namen: Stellvertretungen (nur gezählt), Verwaltung, Beiräte mit Jugendmitgliedern; Schriftführung entfällt. Gewählte Mitglieder stets mit Namen, auch wenn die Quelle sie mit Status „Fraktionsgeschäftsstellen“ führt.
- Mitgliedschaften in Rat, Ausschüssen und Bezirksvertretungen mit Beginn vor der Wahlperiode und in beendeten Gremien entfallen (Audit `data/export/audit_besetzung.tsv`, ohne Namen).
- Ergebnis am 27.10.2026: Rat 67 Mitglieder, davon 66 mit Fraktion (ohne: Vorsitz); 1.278 laufende Mitgliedschaften, 351 Personen namentlich.
