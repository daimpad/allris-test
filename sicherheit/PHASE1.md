# Sicherheit und Ordnung – Phase 1: Regelentwurf und Prüfbogen (02.11.2026)

**Grundlage:** `../themen/phase0/WEITERE.md`, Abschnitt (b), mit den Entscheidungen vom 02.11.2026.

**Stand:** geprüft und veröffentlicht am 02.11.2026 (`PRUEFUNG.md`).

**Datenstand:** lokale Datenbank vom 02.11.2026; jüngste Vorlage vom 31.10.2026; Besetzung zum Stichtag 27.10.2026.

## Regeln (`pipeline/themenseiten/sicherheit.py`, abgeleitet, je Vorlage mit Grund)
Die erste passende Regel gilt.

0. **Ausschluss:** „Feuerwehrtopf“ (Entscheidung 4) und andere Vereinsförderung (Heimatpflege, Brauchtum), Formalien und Sammellisten nichtöffentlicher Punkte, Wahlen, Ausländeramt und Staatsangehörigkeit, Aufsichtsräte, Projektberichte des Gebäudemanagements; Verkehr ohne Kartenthema Verkehr (Bewohnerparken, Parksituation, Radfahrer, Tempo, Geschwindigkeit, Messanlagen, Stadtbahn).
1. **Feuerwehr und Rettungsdienst:** Feuerwehr, Rettungsdienst, Rettungswagen, Krankentransport, Leitstelle, vorbeugender Brandschutz, Waldbrände.
2. **Bevölkerungsschutz und Krisenvorsorge:** Bevölkerungsschutz, Katastrophen, zivile Verteidigung, Krisenmanagement, Resilienz, Extremwetter, Blackout, BCM.
3. **Veranstaltungen, Märkte und Kirmes:** Kirmes, Märkte, Marktverzeichnisse, Feste (nicht Beethoven-, Lese-, Film- und Musikfeste), „Rhein in Flammen“, Karneval, Offenhalten von Verkaufsstellen; nicht Vorlagen der Verkehrsseite. Gegliedert nach Stadtbezirk.
4. **Sicherheit und Ordnung im öffentlichen Raum:** „Sicherheit“ als eigenes Wort (nicht „Sicherheit der Stromversorgung“), Ordnungsdienst, ordnungsbehördliche Maßnahmen, Polizei, Kriminalität, Videoüberwachung, Glas- und Böllerverbote, Silvester, Feuerwerk, Graffiti; nicht Vorlagen der Verkehrsseite.
5. **Amt 37** federführend → Feuerwehr und Rettungsdienst.
6. **Abteilung 33-5** federführend → Veranstaltungen.
7. **Weitere:** Amt 33 allgemein oder Abteilung 33-2 federführend, oder Beratung im Sicherheitsausschuss; nicht Vorlagen der Verkehrsseite; eingeklappt.

**Abteilungsregel (Entscheidung 1):** neues Feld `abteilungen` in `dossier.Zustaendig`. Es prüft den Anfang des Namens der federführenden Organisationseinheit (`responsibility`, `kind = federfuehrend`), z. B. „33-2 “. „33 “ mit Leerzeichen trifft nur das Amt allgemein („33 Bürgerdienste“), nicht 33-1. `aemter` prüft weiter nur die Amtsbezeichnung; die übrigen Seiten bleiben gleich (Referenztest der Kulturseite grün). Seit 11/2025: 33-1 135 Vorlagen, 33-5 33, 33 allgemein 23, 33-2 23.

**Verkehrssicherheit (Entscheidung 6):** `ohne_seite=verkehr.THEMA` an den Regeln 3, 4, 6 und 7. Verkehrsthemen ohne Kartenthema Verkehr fängt der Ausschluss ab. Versorgungs-, Informations- und Cybersicherheit treffen die Titelregel nicht. Die Versorgungssicherheit der Krankenhäuser steht nur über die Beratung im Sicherheitsausschuss unter „weitere“.

**Vor dem Ziehen korrigiert:** Ich habe die vollständige Liste durchgesehen. Von 236 Vorlagen fielen 44 weg, 8 kamen hinzu.
- **Entfallen:**
  - Wahlen (6, Amt 33 allgemein) und Ausländeramt (3);
  - Verkehr (13): Bewohnerparkausweise, Brötchentaste, Radfahrer, Tempo 30, Geschwindigkeitsüberwachung, Stadtbahn-Ausfall, Parksituation am Bundesamt für Bevölkerungsschutz;
  - Gewaltprävention an Schulen (5, Kinderseite), „Bauordnungsamt“, „Gesinnungspolizei“, Graffiti-Wettbewerb, Lesefest, Aufsichtsrat Beethovenfest;
  - Karnevalsvereine (Heimatpflege), Haus des Karnevals, Stromversorgungsinfrastruktur, Sicherheitskosten von Unterkünften, Formalien (Kreispolizeibeirat, Sachverständige), Projektbericht des Gebäudemanagements.
- **Umgeordnet:** Amt 37 von „weitere“ zur Feuerwehr; Waldbrände, Interhospitaltransport, zivile Verteidigung, BCM, Safe Cities, Wache GABI und Gefahrenabwehr aus „weitere“ in ihre Stränge; verkaufsoffene Sonntage zu Veranstaltungen.
- **Neu:** vorbeugender Brandschutz, ordnungsrechtliche Maßnahmen gegen illegale Müllentsorgung, Katastrophenvorsorge am Godesberger Bach.

## Weitere Festlegungen (Entscheidungen 02.11.2026)
- **Prozessbild:** Punkte nur mit Beratung in Rat, Hauptausschuss oder Sicherheitsausschuss; eigene Bahn „Sicherheitsausschuss“. Sitzungen: Sicherheitsausschuss, Finanzausschuss, Hauptausschuss, Rat, Bezirksvertretungen.
- **Haushalt:** Produktbereich 02; dass er auch Einwohnerangelegenheiten, Kfz-Zulassung, Personenstand und Wahlen enthält, steht unter „Was diese Seite nicht zeigt“.
- **„Wer berät mit“:** Ausschuss für Sicherheit, Ordnung und Bevölkerungsschutz (21 Mitglieder, davon 10 sachkundige Bürger:innen).
- **Farben:** Rot (Schrift #991b1b, Kontrast 8,3:1 auf Weiß, 7,2:1 auf der hellen Kachelfläche); Symbol: Schild mit Haken.

## Stand 02.11.2026
200 Vorlagen in 113 Verfahren, 35 Punkte im Prozessbild:

| Strang | Vorlagen |
|---|---|
| Feuerwehr und Rettungsdienst | 51 |
| Bevölkerungsschutz und Krisenvorsorge | 22 |
| Sicherheit und Ordnung im öffentlichen Raum | 31 |
| Veranstaltungen, Märkte und Kirmes | 73 |
| weitere | 23 |

Veranstaltungen nach Stadtbezirk: Beuel 20, Bonn 9, Bad Godesberg 5, Hardtberg 4, ohne Ortsbezug 35.

**Überschneidungen:** Klima 37 (Osterkirmes, „Rhein in Flammen“, Hitze, Waldbrand), Soziales 27 (Drogen, Krankenhäuser, Tannenbusch), Kultur 6 und Soziales (Fest „Vielfalt“), Wohnen 6, Schule 5, Verkehr 2, Kinder 0.

## Prüfbogen
`data/export/sicherheit/stichprobe_sicherheit.tsv`, erzeugt mit dem Schritt `sicherheit-stichprobe`. Er wird einmal gezogen und danach nicht überschrieben.
- **25 zugeordnete Vorlagen:** Feuerwehr 5, Bevölkerungsschutz 4, öffentlicher Raum 6, Veranstaltungen 5, weitere 5. Frage: Passt der Strang?
- **5 nicht zugeordnete Vorlagen** mit Wörtern des Themas am Wortanfang (Gegenprobe). Frage: Fehlt die Vorlage?

## Grenzen und offene Fragen
- Die Geschwindigkeitsüberwachung (33-2) steht hier nicht, aber auch nicht auf der Verkehrsseite. Dort fehlen auch viele Vorlagen der Straßenverkehrsbehörde (Phase 0). Soll die Verkehrsseite sie aufnehmen?
- 33-1 ist auch allgemeine Ordnungsbehörde (Rauchen in Gaststätten, Ratten, Werbesatzung); solche Vorlagen kommen nur über Wörter im Titel. Reicht das?
- Vorlagen der Verkehrsseite mit Bezug zur Sicherheit fehlen hier, z. B. Dunkelstellen in Bad Godesberg, Bodycams für Fahrpersonal, Viktoriaunterführung, Großversammlungen. Sollen sie auf beiden Seiten stehen?
- Unter „weitere“ stehen Vorlagen, die der Sicherheitsausschuss nur mitberät, z. B. Altpapiercontainer oder die Trinkwasserversorgung der Krankenhäuser. Sollen sie bleiben?
- Zuschüsse für Karnevalszüge und das Fest „Vielfalt“ stehen bei den Veranstaltungen, Vereinsförderung nicht. Ist die Grenze richtig?
- 35 Veranstaltungen haben keinen Ortsbezug (z. B. Marktverzeichnis Stadtbezirk Bonn). Der Bonner Wochenmarkt (261307) ist über den Volltext in Bad Godesberg verortet (Befund für die Verortung).
