# Weitere Themenseiten – Phase 0: Prüfung des Materials (01.11.2026)

> **Entscheidungen des Auftraggebers (02.11.2026):** zuerst „Kinder, Jugend und Familie“ (Phase 1: `kinder/PHASE1.md`); Spielplätze auf der Kinder- und der Klimaseite; Beirat Kinder- und Jugendbeteiligung dazu (nur mit Kindern oder Jugend im Titel); Offener Ganztag und Schulsozialarbeit bleiben auf der Schulseite; im Prozessbild Rat, Hauptausschuss und Fachausschuss; Haushalt Produktbereich 06 mit Link in die Kachel der Haushaltsseite.

**Anlass:** Der Auftraggeber hat „Weitere Themenseiten“ gewählt. Vorgeschlagen sind Soziales, Sicherheit und Ordnung sowie Wirtschaft und Digitales. Zum Vergleich wurde Kinder, Jugend und Familie geprüft; Produktbereich 06 ist im Plan 2026 der größte des Haushalts.

**Frage:** Welches Thema lässt sich wie die fünf vorhandenen Seiten zeigen – mit Strängen, Prozessbild, Kasten „Wer berät mit“, Haushalt und Prüfbogen – und welches zuerst?

**Datenstand und Methode:**
- Lokale Datenbank vom 26.10.2026, nur lesend geöffnet. Grundlage ist der Abruf der OParl-API vom 18.10.2026; die jüngste Vorlage ist vom 16.10.2026. Die Seite ist inzwischen etwas weiter.
- Weitere Quellen: Sitzungen aus `meetings.json` (18.10.2026), Besetzung zum Stichtag 27.10.2026, Haushaltsplan 2025/2026 (`data/haushalt/`).
- Zeitraum wie bei den anderen Seiten: 12. Wahlperiode ab 01.11.2025 mit 3.518 Vorlagen. Zum Vergleich: ab 01.01.2020.
- Je Kandidat ein Regelentwurf aus Amt, Abteilung, Gremium und Wörtern im Titel; die erste passende Regel gilt (wie `dossier.zuordnen`).
  - Alle Zuordnungen sind **abgeleitet und ungeprüft**. Sie dienen der Abschätzung und sind keine Fassung zur Veröffentlichung.
  - Die Zahlen schwanken mit den Regeln um einige Prozent.
- Kontrolle: Mit denselben Daten ergeben die Regeln der fünf Seiten 143 (Kultur), 900 (Verkehr), 159 (Schule), 350 (Wohnen) und 418 (Klima) Vorlagen, wie der Export. Die Überschneidungen beziehen sich auf diese Zahlen.
- Skripte und Listen lagen im Arbeitsverzeichnis dieser Prüfung (nicht im Repository):
  - `cache.py` (Vorgänge wie im Export);
  - `lib.py`, `kandidaten.py` (Regelentwürfe);
  - `auswertung.py`, `bericht_daten.py`;
  - Ergebnisse: `zuordnung_<kandidat>.tsv` (jede Vorlage mit Strang und Grund), `ergebnis.txt`, `kennzahlen.txt`.
  - Aufruf: zuerst `cache.py`, dann `auswertung.py` und `bericht_daten.py`, mit einer Python-Umgebung nach `requirements.txt` (shapely, pyproj, pyshp) und `PYTHONDONTWRITEBYTECODE=1`. Die Datenbank wird nur lesend geöffnet (`mode=ro`).

## Überblick

| | Soziales, Gesundheit, Integration | Sicherheit und Ordnung | Wirtschaft und Digitales | Kinder, Jugend und Familie |
|---|---|---|---|---|
| Vorlagen seit 01.11.2025 (Verfahren) | 252 (133) | 206 (117) | 320 (196) | 127 (91) |
| Vorlagen seit 01.01.2020 | 1.271 | 903 | 1.632 | 1.229 |
| davon auf keiner der fünf Seiten (WP) | 196 | 155 | 241 | 102 |
| Fachausschuss (beraten, WP) | Sozialausschuss 107, dazu ACI 72 | Sicherheitsausschuss 62 | drei Ausschüsse: 57 / 73 / 44 | Ausschuss für Kinder, Jugend und Familie 57 |
| Produktbereich, Plan 2026 | 05: 304,0 Mio. € | 02: 137,0 Mio. € | 15: 33,4 Mio. € | 06: 372,3 Mio. € |
| Punkte im Prozessbild¹ | 54 | 34 | 49 | 28 |
| Stand „entschieden“ | 68 | 61 | 76 | 52 |

¹ Beschlussvorlagen und Anträge mit Beratung in Rat, Hauptausschuss oder Fachausschuss; zum Vergleich: Kultur 25 am 25.10.2026.

Zum Vergleich die Größe der vorhandenen Seiten in derselben Wahlperiode: Kultur 143, Schule 159, Wohnen 350, Klima 418, Verkehr 900 Vorlagen.

## (a) Soziales, Gesundheit und Integration

**Abgrenzung im Entwurf:**
- Ämter: 50 Soziales und Wohnen (ohne Wohnen), 05 Integration und Vielfalt, 53 Gesundheitsamt, Seniorenzentren, 04 Gleichstellung.
- Ausschüsse: „Ausschuss für Soziales, Migration, Gesundheit, Wohnen und Senioren“ und „Ausschuss für Chancengerechtigkeit und Integration“ (ACI, früher Integrationsrat).
- Wohnen bleibt auf der Seite Wohnen und Bauen.

**Umfang:**
- 252 Vorlagen, davon 141 Folgevorlagen. Arten:

  | Vorlagenart | Vorlagen |
  |---|---|
  | Stellungnahmen der Verwaltung | 86 |
  | Große Anfragen | 45 |
  | Beschlussvorlagen | 41 |
  | Änderungsanträge | 30 |
  | Anträge | 22 |
  | Mitteilungen | 17 |
- Kaum örtlich: 34 Vorlagen mit Ortsbezug, 12 nur in Bezirksvertretungen beraten, 4 aus der Einwohnerschaft.

**Federführung und Gremien:**

| Federführend | Vorlagen |
|---|---|
| Ratsbüro (Anträge) | 88 |
| Amt für Integration und Vielfalt | 52 |
| Amt für Soziales und Wohnen | 42 |
| Gesundheitsamt | 13 |
| Seniorenzentren | 9 |

| Gremium | Vorlagen |
|---|---|
| Sozialausschuss | 107 |
| Rat | 93 |
| ACI | 72 |
| Sicherheitsausschuss | 21 |
| Hauptausschuss | 15 |
| Finanzausschuss | 15 |

**Stränge (Entwurf, abgeleitet):**

| Strang | WP | ab 2020 | Beispiele |
|---|---|---|---|
| Geflüchtete und Unterbringung | 23 | 123 | 260306 Vergabe von Betreuungsleistungen in Unterkünften für Geflüchtete; 261133 Satzung über die Unterhaltung von Unterkünften (Grundgebühr) |
| Integration und Vielfalt | 63 | 255 | 260314 Große Anfrage: Sparkurs bei Integrationskursen; 260182 Geschäftsordnung des Integrationsrates (neu: ACI); 260780 Große Anfrage: Integrationsmittel und Migrantenselbstorganisationen |
| Armut und soziale Leistungen | 44 | 128 | 261082 MobilPass-Tickets aus Bonn-Ausweis-Mitteln ab 01.06.2026; 261116 Richtwerte für die angemessenen Bedarfe für Unterkunft 2026; 260069 Antrag „Housing First“ (11 Vorlagen) |
| Senioren, Pflege und Inklusion | 35 | 195 | 261835 Seniorenzentren Pflegesatzanpassung 2026; 253937 Wiedereinrichtung des Projektbeirats Behindertenpolitischer Teilhabeplan; 260423 Kommunale Konferenz Alter und Pflege, Bericht 2025 |
| Gesundheit und Sucht | 34 | 142 | 261220 Antrag: gestiegener Drogenkonsum (insbes. Crack); 260481 Versorgungsbedarfsanalyse Gesundheitskiosk; 261647 Weiterfinanzierung der Hebammen Ambulanz |
| weitere (Ämter, Ausschüsse) | 53 | 428 | Zuschüsse an Träger, z. B. 260422 Bildungswerk interKultur; 260296 Bericht Bürgerschaftliches Engagement |

**Fachausschuss und Haushalt:**
- Fachausschuss: „Ausschuss für Soziales, Migration, Gesundheit, Wohnen und Senioren“ mit 20 Sitzen. Nächste Sitzungen: 10.11.2026, 08.12.2026 und 27.01.2027.
- Der ACI hat 28 Sitze, davon 18 ohne Fraktion (gewählte Mitglieder). Der Kasten „Wer berät mit“ kennt bisher nur einen Ausschuss und müsste diese Sitze erklären. Nächste Sitzungen des ACI: 18.11.2026 und 28.01.2027.
- Produktbereich 05 Soziale Leistungen: Ist 2023 305,4 Mio. €, Plan 2026 304,0 Mio. €.
  - Davon im Plan 2026 Leistungen nach SGB II 106,3 Mio. € und SGB XII 130,7 Mio. €. Das sind Pflichtleistungen, zu denen es kaum Vorlagen gibt.
  - Gesundheit liegt in Produktbereich 07 Gesundheitsdienste (9,3 Mio. €).

**Überschneidungen:**
- 56 Vorlagen stehen schon auf einer der fünf Seiten:

  | Seite | Vorlagen | Beispiele |
  |---|---|---|
  | Wohnen | 24 | Housing First, Unterkünfte |
  | Schule | 11 | Sozialticket und Schülerticket 261103 |
  | Klima | 10 | Hitze |
  | Kultur | 7 | Fest „Vielfalt“ |
  | Verkehr | 4 | |
- Kartenthema „Soziales, Wohnen und Gesundheit“: 260 Vorlagen, davon 156 im Entwurf. Die übrigen betreffen vor allem Wohnen.
- Mit den anderen Kandidaten: Sicherheit 25 (Drogen, Krankenhäuser im Zivilschutz), Wirtschaft 25, Kinder 12.

**Stolpersteine:**
- **Abgrenzung zu Wohnen:**
  - Amt 50 und der Sozialausschuss sind auch für Wohnen zuständig. Ohne eigene Regel kämen 29 Vorlagen hinzu, etwa Baulandmodell, Mietspiegel oder Handlungskonzept Wohnen.
  - Die Regeln kennen bisher nur `ohne_thema` (Kartenthema). „Ohne die Vorlagen der Seite Wohnen“ braucht eine kleine Erweiterung.
- **Mehrdeutige Wörter:**
  - „Migration“ steht auch für IT-Migration (260142).
  - „Pflege“ steht auch für Heimat- und Grünpflege.
  - „barrierefrei“ betrifft meist Haltestellen (Verkehr).
  - „Tafel“ steckt auch in „Gedenktafel“.
- **Zuschüsse:** 30 Zuschüsse an Träger und Vereine, viele aus Integrationsmitteln im ACI. Sie bilden einen eigenen Strang oder stehen unter „weitere“.
- **Datenschutz:**
  - Einzelfälle der Sozialhilfe erscheinen in den Daten nicht als Vorlage; Titel mit Einzelfällen wurden nicht gefunden. Es gibt 9 Sammellisten nichtöffentlicher Punkte.
  - Unterkünfte für Geflüchtete und Wohnungslose werden mit Straße genannt (Frage 4).
- **Umstrittene Titel:** Titel zu Asyl und Migration sind teils politisch zugespitzt. Die Seite übernimmt sie wörtlich und ordnet nur zu, ohne Bewertung.

## (b) Sicherheit und Ordnung

**Abgrenzung im Entwurf:**
- Ämter:
  - 37 Feuerwehr und Rettungsdienst;
  - vom Amt 33 Bürgerdienste nur die Abteilungen 33-2 (Ordnungswidrigkeiten, Stadtordnungsdienst) und 33-5 (Veranstaltungskoordination und Märkte) sowie das Amt allgemein.
  - Ohne 33-1 Straßenverkehrsbehörde (Verkehr), 33-4 Dienstleistungszentrum, 33-6 Ausländeramt und 33-0 Wahlen.
- Ausschuss: „Ausschuss für Sicherheit, Ordnung und Bevölkerungsschutz“, neu in dieser Wahlperiode (79 von 82 Vorlagen seit 11/2025).

**Umfang:**
- 206 Vorlagen. Arten:

  | Vorlagenart | Vorlagen |
  |---|---|
  | Stellungnahmen der Verwaltung | 72 |
  | Beschlussvorlagen | 30 |
  | Große Anfragen | 21 |
  | Anträge | 19 |
  | Änderungsanträge | 16 |
  | Mitteilungen | 16 |
  | Anregungen und Beschwerden | 14 |
  | Einleitungen von Vergaben | 12 |
- Stärker örtlich als Soziales: 70 Vorlagen mit Ortsbezug, 70 nur in Bezirksvertretungen beraten (Märkte, Kirmes, Feste), 15 aus der Einwohnerschaft.

**Federführung und Gremien:**

| Federführend | Vorlagen |
|---|---|
| Ratsbüro | 60 |
| Feuerwehr (37 und 37-0) | 34 |
| Veranstaltungen und Märkte (33-5) | 29 |
| Bürgerbüro | 15 |
| Straßenverkehrsbehörde (33-1), nur mit Wort im Titel | 13 |
| Stadtordnungsdienst (33-2) | 10 |

| Gremium | Vorlagen |
|---|---|
| Sicherheitsausschuss | 62 |
| Rat | 42 |
| Bezirksvertretung Bonn | 39 |
| Bezirksvertretung Beuel | 35 |
| Finanzausschuss | 22 |
| Bezirksvertretung Bad Godesberg | 16 |
| Umweltausschuss | 15 |

**Stränge (Entwurf, abgeleitet):**

| Strang | WP | ab 2020 | Beispiele |
|---|---|---|---|
| Feuerwehr und Rettungsdienst | 41 | 192 | 261642 Neufassung der Gebührensatzung Rettungsdienst; 260154 Vergabe: fünf Rettungswagen; 260697 Große Anfrage: Rückstand der Gebührenabrechnungen |
| Bevölkerungsschutz und Krisenvorsorge | 31 | 99 | 261107 Antrag: Grundzüge des Bonner Bevölkerungsschutzes; 261106 Antrag: Resilienzstrategie; 260387 Sachstand Bevölkerungsschutz |
| Sicherheit und Ordnung im öffentlichen Raum | 43 | 150 | 260667 Große Anfrage: Sicherheitslage und Prävention in Tannenbusch; 261876 Schutz in der Silvesternacht; 261059 Bürgerantrag: Glasflaschenverbot Altstadt und Innenstadt |
| Veranstaltungen, Märkte und Kirmes | 60 | 227 | 253749 Marktverzeichnis Stadtbezirk Beuel 2026 (7 Vorlagen); 260396 „Rhein in Flammen“ (7); 254086 Weihnachtsmarkt 2026/27 |
| weitere (Ämter, Ausschuss) | 31 | 235 | 261067 Vergabe: mobile Geschwindigkeitsüberwachung; 261220 Drogenkonsum (im Sicherheitsausschuss beraten) |

**Fachausschuss und Haushalt:**
- Fachausschuss: „Ausschuss für Sicherheit, Ordnung und Bevölkerungsschutz“ mit 21 Sitzen. Nächste Sitzung: 17.11.2026.
- Produktbereich 02 Sicherheit und Ordnung: Ist 2023 121,5 Mio. €, Plan 2026 137,0 Mio. €.
  - Davon im Plan 2026 Brandschutz 43,1 Mio. €, Rettungsdienst 36,7 Mio. € und Großschadensereignisse 4,5 Mio. € (Amt 37).
  - Der Rest betrifft Einwohnerangelegenheiten, Kfz-Zulassung, Personenstand und Wahlen (Amt 33), die auf der Seite kaum vorkommen.

**Überschneidungen:**
- 51 Vorlagen stehen schon auf einer der fünf Seiten, vor allem auf der Klimaseite (37): Lärm bei Kirmes und Festen, „Rhein in Flammen“, Waldbrand, Feuerwerk.
- Kartenthema „Sicherheit und Ordnung“: 160 Vorlagen, davon 93 im Entwurf. 54 Vorlagen des Entwurfs haben kein Kartenthema, weil das Amt 33 in der Themenzuordnung fehlt.

**Stolpersteine:**
- **Amt 33 ist zu breit:**
  - Die Straßenverkehrsbehörde (33-1) hatte 122 Vorlagen in der Wahlperiode, meist Verkehrsanordnungen.
  - Die Regeln der Themenseiten prüfen nur die Amtsbezeichnung („33 Bürgerdienste“). Für Regeln auf Abteilungsebene braucht `dossier.Zustaendig` eine kleine Erweiterung; die Abteilung steht schon in `responsibility`.
  - Nebenbefund: 41 Vorlagen der Straßenverkehrsbehörde stehen auf keiner Seite, z. B. „Parksituation“, „Halteverbot“, „Tempo-30-Lückenschluss“ mit Bindestrich. Das ist ein Hinweis für die Verkehrsseite.
- **„Feuerwehrtopf“** sind Mittel der Bezirksvertretungen für Vereine, nicht für die Feuerwehr (18 Vorlagen in 11 Verfahren). Der Entwurf schließt sie aus.
- **„Sicherheit“ ist mehrdeutig:** auch Verkehrs-, Versorgungs-, Informations- und Cybersicherheit.
- **Feuerwehr:** Viele Vorlagen sind Gebührensatzungen und Vergaben (16 Einleitungen im Thema).
  - Die Vorlagen zum Brandschutzbedarfsplan (zuletzt 2025) und zum Rettungsdienstbedarfsplan (2021) liegen vor der Wahlperiode.
  - Ein großes Verfahren gibt es derzeit nicht. Am größten sind Marktverzeichnisse, „Rhein in Flammen“ und die Osterkirmes Beuel (je 7–8 Vorlagen).

## (c) Wirtschaft und Digitales

**Abgrenzung im Entwurf:**
- Ämter: 03 Wirtschaftsförderung (mit Liegenschaften), 10 Personal- und Organisationsamt (mit IT), Stabsstelle CDO (Dezernat OB), 02 Amt für Internationales und globale Nachhaltigkeit (über Ausschuss und Wörter).
- Drei Ausschüsse:
  - „Ausschuss für Wirtschaft, Liegenschaften und Arbeit“;
  - „Ausschuss für Digitalisierung, Dienstleistung und Verwaltungsmodernisierung“;
  - „Ausschuss für Wissenschaft, Europa und Internationales“.

  Alle drei sind neu in dieser Wahlperiode.

**Umfang:**
- 320 Vorlagen. Arten:

  | Vorlagenart | Vorlagen |
  |---|---|
  | Stellungnahmen der Verwaltung | 96 |
  | Mitteilungen | 59 |
  | Beschlussvorlagen | 35 |
  | Änderungsanträge | 32 |
  | Große Anfragen | 30 |
  | Anträge | 27 |
  | Einleitungen von Vergaben | 23 |
- 77 Vorlagen mit Ortsbezug, 49 nur in Bezirksvertretungen beraten.

**Federführung und Gremien:**

| Federführend | Vorlagen |
|---|---|
| Ratsbüro | 98 |
| Wirtschaftsförderung (mit Liegenschaften) | 62 |
| Personal- und Organisationsamt (davon IT 15) | 54 |
| Amt für Internationales | 19 |
| Stabsstelle CDO und Dezernat OB | 9 |

| Gremium | Vorlagen |
|---|---|
| Rat | 108 |
| Digitalisierungsausschuss | 73 |
| Wirtschaftsausschuss | 57 |
| Wissenschaftsausschuss | 44 |
| Bezirksvertretung Bad Godesberg | 35 |
| Finanzausschuss | 30 |
| Hauptausschuss | 29 |

**Stränge (Entwurf, abgeleitet):**

| Strang | WP | ab 2020 | Beispiele |
|---|---|---|---|
| Digitalisierung und Verwaltung | 100 | 319 | 261619 Dachstrategie Digitale Transformation; 260693 Antrag: Open-Source-Software; 260354 Aufarbeitung des IT-Ausfalls bei RegioIT |
| Wirtschaftsförderung und Arbeit | 34 | 224 | 261528 Jahreswirtschaftsbericht 2026; 260427 Gründungstätigkeit und Bestandsunternehmensbetreuung; 261752 Ausbildungsmarkt Bonn/Rhein-Sieg 2025/2026 |
| Tourismus, Zentren und Stadtmarketing | 18 | 98 | 261262 Image- und Marketingkonzept Bad Godesberger Zentrum; 260645 Bonn-Information: Rückblick und Ausblick; 242284-01 Tätigkeitsbericht des Nachtbürgermeisters 2025 |
| Liegenschaften | 44 | 204 | 260084 Weiteres Vorgehen zum Amerikanischen Club / „Open Embassy“; 260011 Zwischennutzung des Viktoriabads; 261266 Sanierung der Stadthalle Bad Godesberg |
| Wissenschaft und Internationales | 40 | 214 | 261043 Antrag: Standort internationaler Wissenschaftsdiplomatie; 260500 30 Jahre UN-Stadt Bonn; 260460 15. Bonner Wissenschaftsnacht |
| weitere (Ämter, Ausschüsse) | 84 | 573 | Beschaffungen der Zentralen Dienste; 260138 Verwaltungsgebührenordnung; 261626 Dezernatsneuverteilung |

**Fachausschuss und Haushalt:**
- Es gibt keinen einzelnen Fachausschuss. Der Kasten „Wer berät mit“ könnte einen der drei zeigen; alle sind lesbar (20–21 Sitze).
- Nächste Sitzungen:
  - Wirtschaftsausschuss: 03.11. und 01.12.2026;
  - Digitalisierungsausschuss: 18.11.2026;
  - Wissenschaftsausschuss: 02.12.2026.
- Produktbereich 15 Wirtschaft und Tourismus: Ist 2023 28,9 Mio. €, Plan 2026 33,4 Mio. €.
  - Davon im Plan 2026 WorldCCBonn 21,1 Mio. € und Beethovenhalle 6,0 Mio. €, Wirtschaftsförderung nur 4,0 Mio. € und Tourismus 2,0 Mio. €.
  - Die Beethovenhalle steht auf der Kulturseite.
  - Digitalisierung und Verwaltung gehören zu Produktbereich 01 Innere Verwaltung (Plan 2026: 304,1 Mio. €), der fast die ganze Verwaltung umfasst.

**Überschneidungen:**
- 79 Vorlagen stehen schon auf einer der fünf Seiten:

  | Seite | Vorlagen | Beispiele |
  |---|---|---|
  | Wohnen | 40 | Amerikanischer Club und VEBOWAG, Einzelhandels- und Zentrenkonzept, ISEK |
  | Verkehr | 14 | |
  | Klima | 14 | |
  | Schule | 10 | |
- Kartenthema „Wirtschaft und Finanzen“: 578 Vorlagen, davon nur 146 im Entwurf. Das Kartenthema besteht vor allem aus Haushalt, Gebühren und Vergaben.

**Stolpersteine:**
- **Uneinheitlich:** drei Ausschüsse, zwei Produktbereiche.
- **Mehrdeutige Wörter:**
  - „Wirtschaft“: Wirtschaftsplan, haushaltswirtschaftliche Lage, Parkraumbewirtschaftung, „Vertretung … in Organen wirtschaftlicher Unternehmen“ (Besetzungen);
  - „Liegenschaften“: Theaterliegenschaften, Energieverbrauch kommunaler Liegenschaften.
- **Wenig Beschlüsse:** viele interne Beschaffungen (24 Einleitungen von Vergaben) und Mitteilungen ohne Beschluss (59).
- **Personalangelegenheiten** wie Wahl von Beigeordneten oder Stellenplan sind im Entwurf ausgeschlossen. Es gibt 14 Sammellisten nichtöffentlicher Punkte.

## (d) Kinder, Jugend und Familie

**Abgrenzung im Entwurf:**
- Amt 51 Kinder, Jugend und Familie.
- „Ausschuss für Kinder, Jugend und Familie“ (Jugendhilfeausschuss).
- „Beirat Kinder- und Jugendbeteiligung“, nur mit Kindern oder Jugend im Titel.
- Wörter für Kitas, Spielplätze, Jugendarbeit und Familie im Titel.
- Kitas stehen ausdrücklich nicht auf der Schulseite (Entscheidung 26.10.2026).

**Umfang:**
- 127 Vorlagen, davon nur 49 Folgevorlagen. Arten:

  | Vorlagenart | Vorlagen |
  |---|---|
  | Beschlussvorlagen | 36 |
  | Stellungnahmen der Verwaltung | 25 |
  | Mitteilungen | 18 |
  | Anträge | 12 |
  | Änderungsanträge | 12 |
  | Große Anfragen | 8 |
  | Anregungen und Beschwerden | 7 |
- 58 Vorlagen mit Ortsbezug, 41 nur in Bezirksvertretungen beraten (vor allem Spielplätze), 9 aus der Einwohnerschaft.
- 52 Vorlagen sind „entschieden“, ein höherer Anteil als bei den anderen Kandidaten. Viele entscheidet der Ausschuss selbst; nur 19 gehen in den Rat.

**Federführung und Gremien:**

| Federführend | Vorlagen |
|---|---|
| Amt 51 | 53 |
| Ratsbüro | 30 |
| Amt für Umwelt und Stadtgrün (Spielplätze) | 10 |
| Bürgerbüro | 9 |
| Gebäudemanagement (Kita-Bau) | 7 |

| Gremium | Vorlagen |
|---|---|
| Ausschuss für Kinder, Jugend und Familie | 57 |
| Rat | 19 |
| Bezirksvertretung Hardtberg | 19 |
| Bezirksvertretung Bonn | 11 |
| Bezirksvertretung Beuel | 10 |

**Stränge (Entwurf, abgeleitet):**

| Strang | WP | ab 2020 | Beispiele |
|---|---|---|---|
| Kitas und Kindertagespflege | 45 | 405 | 261048 Bedarfsplan: Herausforderungen in der vorschulischen Kinderbetreuung 2026; 260362 Zuschuss nach § 48 KiBiz zur Flexibilisierung der Betreuungszeiten; 260718 dreigruppiger Kita-Neubau Riemannstraße (Brüser Berg) |
| Spielplätze und Freiflächen | 37 | 243 | 254077 Umbau Kinderspielplatz Königsberger Weg (Duisdorf); 260896 kinderfreundliche Umgestaltung des Möhneplatzes; 261063 Bürgerantrag: Spielplatz im Brandengarten (Lengsdorf) |
| Jugendarbeit und Jugendförderung | 18 | 126 | 261037 Fortschreibung des Kinder- und Jugendförderplans 2026–2030; 261514 Richtlinien zur Förderung der Jugendarbeit; 261231 Ausstattung Jugendzentrum Brüser Berg |
| Familie, Kinderschutz und Hilfen | 9 | 127 | 261066 Arbeit der Frühen Hilfen Bonn; 261189 Entwicklung der Inklusionsassistenz; 261135 Landesprogramm „kinderstark“ |
| Beteiligung von Kindern und Jugendlichen | 6 | 25 | 260275 Neubesetzung des Beirats Kinder- und Jugendbeteiligung; 261159 Kinder- und Jugendrechtewoche und Weltkindertag |
| weitere (Amt, Ausschuss) | 12 | 303 | 260433 Förderung „Neustart – Bildung ab der ersten Minute“ |

**Fachausschuss und Haushalt:**
- Fachausschuss: „Ausschuss für Kinder, Jugend und Familie“. Die Besetzung ist lesbar: 15 Sitze, davon 9 ohne Fraktion, dazu 16 beratende Mitglieder.
- Nächste Sitzung: 25.11.2026; Beirat Kinder- und Jugendbeteiligung: 27.11.2026.
- Produktbereich 06 Kinder-, Jugend- und Familienhilfe: Ist 2023 301,4 Mio. €, Plan 2026 372,3 Mio. €.
  - Im Plan 2026 ist er der größte der 17 Produktbereiche; im Ist 2023 liegt er knapp hinter 05.
  - Davon im Plan 2026 (Produktgruppen):

    | Produktgruppe | Plan 2026 |
    |---|---|
    | Tageseinrichtungen für Kinder | 199,3 Mio. € |
    | Kindertagespflege | 27,5 Mio. € |
    | Sonstige Leistungen zur Förderung junger Menschen und Familien | 130,7 Mio. € |
    | Jugendarbeit mit Einrichtungen | 11,0 Mio. € |

    Der Strang Kitas passt damit zum größten Teil des Produktbereichs.

**Überschneidungen:**
- Nur 25 Vorlagen stehen schon auf einer der fünf Seiten:
  - Klima 14: Spielplätze des Amts für Umwelt und Stadtgrün im Strang „weitere“;
  - Schule 11: Inklusionsassistenz, Pumptrack an einer Gesamtschule, Schulhöfe als Spielplätze;
  - Wohnen 2.
- Kartenthema „Kinder, Jugend und Familie“: 155 Vorlagen, davon 107 im Entwurf.

**Stolpersteine:**
- **Kita als Ortsangabe:** Kitas werden in Anträgen zu Parken, Winterdienst, Straßenlaternen oder Wahlwerbung als Ort genannt. Regel `ohne_thema="verkehr"` und Prüfbogen.
- **Spielplätze** baut und pflegt das Amt für Umwelt und Stadtgrün. Dieselbe Vorlage stünde auf der Klimaseite und hier.
- **„Familie“** steckt auch in „Einfamilienhaus“ und im Namen des Amts. Der Entwurf schließt Haustypen aus.
- **Sitzungsname:** Die Sitzung am 25.11.2026 hat in der Quelle kein Gremium. Der aus dem Sitzungstitel gebildete Name „Ausschuss für Kinder-, Jugend und Familie“ (mit Bindestrich) passt nicht zum Gremiumsnamen. Kalender und Sitzungsliste bräuchten einen Ausweichnamen.
- **Weniger Beratungen:** Der Ausschuss beriet 2023 und 2024 je rund 155 Vorlagen, 2025 noch 92 und 2026 bis Mitte Oktober 67. Die Seite ist kleiner als frühere Jahre vermuten lassen.
- **Datenschutz:**
  - Einzelfälle der Jugendhilfe erscheinen nicht als Vorlage. Es gibt 5 Sammellisten nichtöffentlicher Punkte.
  - Ein Antrag betrifft die frühere Tätigkeit einer Person in Kitas, ohne Namen; im Prüfbogen ansehen.
  - Titel neuer Kitas nennen die Anschrift der Einrichtung (keine Privatpersonen).

## Grenzen

- **Regeln:** Die Regelentwürfe sind ungeprüft. Gegenprobe und Prüfbogen folgen erst in Phase 1. Vereinzelt stehen Vorlagen falsch zugeordnet in den Listen, etwa der Amtsname im Titel oder IT-Migration.
- **Datenstand:** 18.10.2026. Seither sind Vorlagen hinzugekommen. Sitzungen ab November sind laut Quelle geplant.
- **Quellen:** Zugeordnet wird nur nach Titel, Amt und Gremium. Keine Texte der Dokumente, keine Zitate; Beträge nur je Produktbereich oder Produktgruppe.
- **Ausschüsse:** Sie wurden zur 12. Wahlperiode neu zugeschnitten, außer dem Ausschuss für Kinder, Jugend und Familie. Zahlen seit 2020 beruhen deshalb vor allem auf Ämtern und Wörtern.
- **Mehrfachnennung:** Eine Vorlage kann auf mehreren Seiten stehen, wie bisher Schulweg und Verkehr.

## Optionen zur Entscheidung, mit Empfehlung

1. **Kinder, Jugend und Familie als nächste Seite (empfohlen).**
   - Ein Fachausschuss, ein Amt und ein Produktbereich; dieser ist im Plan 2026 der größte, die Kitas allein 199 Mio. €.
   - Eine klare Lücke: Kitas sind auf der Schulseite ausdrücklich ausgeschlossen.
   - Größe wie Kultur und Schule (127 Vorlagen).
   - Wenig Überschneidung (25 Vorlagen).
   - Technisch fast ohne Änderung; nur der Ausweichname der Sitzung ist nötig.

   Vorschlag:
   - Stränge: Kitas und Kindertagespflege; Spielplätze (nach Stadtbezirk, eingeklappt); Jugendarbeit (mit Beteiligung); Familie und Hilfen; weitere eingeklappt.
   - Prozessbild: Rat, Hauptausschuss und Ausschuss für Kinder, Jugend und Familie, oben die Haushaltsbahn. Laut 261064 berät jeder Fachausschuss den Entwurf.
2. **Soziales, Gesundheit und Integration als zweite Seite.**
   - Vorher entscheiden: Grenze zu Wohnen, Umgang mit dem ACI und Darstellung der Unterkünfte.
   - Größe wie Wohnen (252 Vorlagen); wenig örtlich, viele Anfragen und Stellungnahmen.
3. **Sicherheit und Ordnung danach.**
   - Vorher eine Regel auf Abteilungsebene (Amt 33), dazu die Abgrenzung zu Verkehr und Klima.
   - Ein klarer Ausschuss. Der Haushalt passt zur Hälfte (Feuerwehr und Rettungsdienst).
4. **Wirtschaft und Digitales zurückstellen oder teilen.**
   - Möglich wäre eine kleinere Seite „Digitale Verwaltung“: Digitalisierungsausschuss, rund 100 Vorlagen, mit der Dachstrategie Digitale Transformation (261619) als Verfahren.
   - Wirtschaftsförderung allein ist schmal (34 Vorlagen). Ihr Produktbereich wird von WorldCCBonn und Beethovenhalle bestimmt.

Nach jeder Entscheidung folgen wie bisher: Phase 1 (Regelentwurf als Entwurf in `pipeline/themenseiten/`), Prüfbogen mit 30 Vorlagen im Gespräch, danach die Seite.

## Offene Fragen an den Auftraggeber

1. **Reihenfolge:** Kinder, Jugend und Familie zuerst? Und welche der drei vorgeschlagenen Seiten danach?
2. **Kinder:**
   - Sollen Spielplätze dazugehören, auch wenn sie auf der Klimaseite unter „weitere“ stehen?
   - Gehört der Beirat Kinder- und Jugendbeteiligung dazu?
   - OGS und Schulsozialarbeit bleiben auf der Schulseite?
3. **Soziales, Umfang:**
   - Gehören Gesundheit (Gesundheitsamt, Produktbereich 07) und Integration (ACI, Amt 05) dazu?
   - Bleibt Wohnen ganz auf der Seite Wohnen und Bauen, Wohnungslosigkeit also doppelt?
   - Soll der Kasten „Wer berät mit“ zwei Ausschüsse zeigen? Das wäre eine Erweiterung.
4. **Unterkünfte für Geflüchtete und Wohnungslose:** auf Karte und Seite nur auf Ortsteilebene zeigen, auch wo der Titel eine Straße nennt?
5. **Sicherheit, Umfang:**
   - Gehören Veranstaltungen, Märkte und Kirmes dazu?
   - Ausländeramt, Dienstleistungszentrum und Wahlen bleiben außen vor?
   - Ist die Erweiterung der Regeln um Abteilungen in Ordnung?
6. **Wirtschaft:** eine Seite, eine Seite „Digitale Verwaltung“ oder zurückstellen? Gehören Wissenschaft und Internationales sowie Liegenschaften dazu?
7. **Haushalt:** Bei Kinder (06) und Sicherheit (02) die Produktgruppen nennen (Kitas, Brandschutz, Rettungsdienst) oder wie bisher nur den Produktbereich? Die Produktgruppen sind seit 28.10.2026 freigegeben.
8. **Nebenbefund Verkehr:** Rund 40 Verkehrsanordnungen der Straßenverkehrsbehörde fehlen auf der Verkehrsseite. Prüfen beim nächsten Durchgang der Verkehrsregeln?
