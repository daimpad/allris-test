# Soziales, Gesundheit und Integration – Phase 1: Regelentwurf und Prüfbogen (02.11.2026)

**Grundlage:** `../themen/phase0/WEITERE.md`, Abschnitt (a), mit den Entscheidungen vom 02.11.2026.

**Stand:** Entwurf. `soziales` steht in `ENTWUERFE`, nicht in `ALLE`: keine Seite, kein Export. Der Prüfbogen ist noch nicht geprüft.

**Datenstand:** lokale Datenbank vom 02.11.2026; jüngste Vorlage vom 31.10.2026; Besetzung zum Stichtag 27.10.2026.

## Regeln (`pipeline/themenseiten/soziales.py`, abgeleitet, je Vorlage mit Grund)
Die erste passende Regel gilt.

0. **Ausschluss:** Formalien (Schriftführung, Sitzungstermine, Vorsitz, Benennungen, Zuständigkeitsordnung), Sammellisten nichtöffentlicher Punkte, Straßenbenennungen, Baumfällungen, Parken; Wohnprojekte und Bauleitplanung, außer mit Wohnungslosigkeit, Geflüchteten oder Unterkünften im Titel.
1. **Zuschüsse an Träger** („Zuschuss an“, „Zuwendung an“, „Förderung der … e. V.“) aus den Ämtern und Ausschüssen des Themas → „weitere“.
2. **Geflüchtete und Unterbringung:** Geflüchtete, Asyl, Unterkünfte, Übergangswohnheime, Aufnahme, Bezahlkarte, „Sichere Häfen“.
3. **Armut und soziale Leistungen:** Wohnungslosigkeit, Obdachlosigkeit, Housing First (eigene Regel); Bonn-Ausweis, MobilPass, Sozialticket, Grundsicherung, Bürgergeld, Kosten der Unterkunft, Wohngeld, Tafel, Bildung und Teilhabe.
4. **Senioren, Pflege und Inklusion:** Senioren, Pflegewörter (Pflegesatz, Pflegeversicherung, Pflegedienst …), ältere Menschen, Demenz, Inklusion, Behinderung, Teilhabeplan, Hospiz; nicht Verkehr. „Barrierefrei“ nur mit Amt oder Ausschuss des Themas.
5. **Gesundheit und Sucht:** Gesundheit, Krankenhaus, Ärzte, Hebammen, Schwangerschaft, Drogen, Sucht, Methadon, Impfung, Psychiatrie; nicht Verkehr.
6. **Integration und Vielfalt:** Integration, Migration, Vielfalt, Diskriminierung, Rassismus, Einbürgerung, Ausländeramt, Aufenthaltsrecht, Gleichstellung, Frauenhaus, Rechtsextremismus; nicht Verkehr.
7. **Weitere:** Ämter 50, 05, 53, Seniorenzentren und 04 federführend oder Beratung im Sozialausschuss oder im ACI, **ohne Vorlagen der Seite Wohnen und Bauen**; eingeklappt.

**Abgrenzung zu Wohnen (Entscheidung 2):** neues Regel-Feld `ohne_seite` in `dossier.Regel`. Eine Regel mit `ohne_seite=wohnen.THEMA` überspringt Vorlagen, die auf der Wohnseite stehen; die Regeln müssen nicht doppelt gepflegt werden. Das Feld tragen nur die Regeln 1 und 7 (Amt und Ausschuss). Die Titelregeln für Wohnungslosigkeit und Unterkünfte gelten vorher; Housing First und Unterkünfte stehen daher auf beiden Seiten. 30 Vorlagen fallen heraus, z. B. Mietspiegel, Baulandmodell, Handlungskonzept Wohnen. Die Wohnseite erfasst „Wohnprojekte“ nicht (260484); das Wort steht deshalb im Ausschluss.

**Vor dem Ziehen korrigiert:** Ich habe die vollständige Liste durchgesehen, bevor ich den Prüfbogen gezogen habe. Danach fielen rund 60 Fehltreffer weg:
- „Unterbringung“ allein (Stadtmuseum), „Gedenkstein/-tafel“, „Pflege“ von Grünflächen, „inklusive“;
- „barrierefrei“ an Haltestellen, „Klinik“ an Zufahrten, „medizinisch“ bei Vergaben;
- „Migrationsunterstützung“ (IT, 260142), „Integration von Bordsteinladesäulen“, „Biodiversität“;
- der Name des ACI im Titel und Formalien des ACI; Gesundheit beim Verkehr (Ausweichrouten, Ärztehaus).

„Bezuschussung“ von MobilPass-Tickets steht bei Armut, nicht unter Zuschüssen.

Beim ersten Ziehen traf das Kandidatenwort „Frauen“ den „Liebfrauenweg“. Danach habe ich den Prüfbogen einmal neu gezogen (gleicher Startwert): Die 25 zugeordneten Vorlagen blieben gleich, in der Gegenprobe wechselten 2 von 5.

## Weitere Festlegungen (Entscheidungen 02.11.2026)
- **Prozessbild:** Punkte nur mit Beratung in Rat, Hauptausschuss oder Sozialausschuss. Bahnen: Haushalt 2027/2028, Bezirksvertretungen, Sozialausschuss, andere Ausschüsse (darunter der ACI), Finanzausschuss, Hauptausschuss und Rat.
- **Sitzungen:** Sozialausschuss, ACI, Finanzausschuss, Hauptausschuss, Rat und die Bezirksvertretungen.
- **Haushalt:** Produktbereich 05 Soziale Leistungen. Gesundheit liegt in Produktbereich 07 und ist nicht enthalten.
- **„Wer berät mit“:** beide Ausschüsse (`fachausschuss` als Tupel; die übrigen Seiten bleiben gleich). Im ACI haben 18 von 28 Mitgliedern keine Fraktion. Ihre Rollen stehen gezählt wie in der Quelle: 15 „Mitglied Ausschuss für Chancengerechtigkeit und Integration“, 3 im Vorsitz oder in der Stellvertretung. „Gewählt“ steht nicht in den Daten.
- **Farben:** Fuchsia (Schrift #86198f, Kontrast 8,2:1 auf Weiß); Symbol: Herz mit Kreuz.

## Stand 02.11.2026
254 Vorlagen in 134 Verfahren, 54 Punkte im Prozessbild:

| Strang | Vorlagen |
|---|---|
| Geflüchtete und Unterbringung | 20 |
| Armut und soziale Leistungen | 45 |
| Senioren, Pflege und Inklusion | 29 |
| Gesundheit und Sucht | 39 |
| Integration und Vielfalt | 49 |
| weitere | 72 |

**Überschneidungen:**

| Seite | Vorlagen | Beispiele |
|---|---|---|
| Wohnen | 26 | davon 18 zu Wohnungslosigkeit und Unterkünften, dazu Methadon-Praxis, muslimische Bestattungsfläche |
| Klima | 15 | Hitze, Friedhöfe |
| Schule | 11 | Sozialticket und Schülerticket |
| Kinder | 11 | Rucksack KiTa, Inklusionsassistenz |
| Kultur | 8 | Fest „Vielfalt“ |
| Verkehr | 6 | |

## Prüfbogen
`data/export/soziales/stichprobe_soziales.tsv`, erzeugt mit dem Schritt `soziales-stichprobe`. Er wird einmal gezogen und danach nicht überschrieben.
- **25 zugeordnete Vorlagen:** je 4 aus den fünf Strängen, 5 aus „weitere“. Frage: Passt der Strang?
- **5 nicht zugeordnete Vorlagen** mit Wörtern des Themas im Titel (Gegenprobe). Frage: Fehlt die Vorlage auf der Seite?

## Grenzen und offene Fragen
- Titel zu Asyl und Migration stehen wörtlich wie in der Quelle, auch zugespitzte Titel; die Seite bewertet sie nicht.
- Unter „weitere“ stehen Vorlagen, die der ACI oder der Sozialausschuss nur mitberät, z. B. Friedhofsgebühren oder Sicherheit in Tannenbusch. Sollen sie bleiben?
- Soll der ACI eine eigene Bahn im Prozessbild erhalten? Bisher steht er unter „andere Ausschüsse“.
- Soll der Kasten zum ACI die Rechtsgrundlage (§ 27 GO NRW) nennen? Das ginge nur mit einer Fundstelle.
