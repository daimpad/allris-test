# Wirtschaft und Wissenschaft – Phase 1: Regelentwurf und Prüfbogen (02.11.2026)

**Grundlage:** `../themen/phase0/WEITERE.md`, Abschnitt (c), mit den Entscheidungen vom 02.11.2026 (zwei Seiten statt einer; die zweite ist `../digital/PHASE1.md`).

**Stand:** geprüft und veröffentlicht am 02.11.2026 (`PRUEFUNG.md`).

**Datenstand:** lokale Datenbank vom 02.11.2026; jüngste Vorlage vom 31.10.2026; Besetzung zum Stichtag 27.10.2026.

## Regeln (`pipeline/themenseiten/wirtschaft.py`, abgeleitet, je Vorlage mit Grund)
Die erste passende Regel gilt.

0. **Ausschluss:** Formalien (Schriftführung, Sitzungstermine, Vorsitz, Benennungen, Vertretung in Organen und Aufsichtsräten, Projektbeiräte), Sammellisten nichtöffentlicher Punkte; Wirtschaftspläne, Jahresabschlüsse und Entlastungen; „haushaltswirtschaftlich“, „personalwirtschaftlich“, Bewirtschaftung von Parkraum, Parken; Theaterliegenschaften, Energieverbrauch und Photovoltaik kommunaler Liegenschaften; Bauanträge und Fällgenehmigungen auf Grundstücken; Anfragen zur Beethovenhalle (Kulturseite).
1. **Liegenschaften:** Liegenschaften, Grundstücksgeschäfte, Ankaufsrecht, Veräußerung, Verpachtung, Zwischennutzung, Amerikanischer Club, Viktoriabad, Stadthalle; **nicht Vorlagen der Seite Wohnen und Bauen** (`ohne_seite=wohnen.THEMA`).
2. **Wirtschaftsförderung und Arbeit:** Wirtschaftsförderung, Wirtschaftsbericht, Unternehmen, Gründungen, Start-ups, Digital Hub, Gewerbeflächen, Industrie, Büromarkt, Arbeits- und Ausbildungsmarkt, Fachkräfte, Glasfaserausbau, Region Köln/Bonn.
3. **Tourismus, Zentren und Stadtmarketing:** Tourismus, Bonn-Information, Stadtmarketing, Imagekampagnen, Nachtbürgermeister, Einzelhandel und Zentren, WorldCCBonn.
4. **Wissenschaft und Internationales:** Wissenschaft (nicht „wissenschaftlich“), Hochschulen, Forschung, Studierende, UN und VN, Europäische Union, Städtepartnerschaften, Berlin/Bonn-Gesetz, Delegationen, internationale Konferenzen.
5. **Abteilung 03-4** federführend → Liegenschaften (ohne Wohnseite).
6. **Amt 02** federführend → Wissenschaft und Internationales.
7. **Weitere:** Amt 03 federführend oder Beratung im Wirtschafts- oder Wissenschaftsausschuss; **nicht Vorlagen, die auf einer der acht veröffentlichten Seiten stehen**; eingeklappt.

**Neues Feld:** `ohne_seite` nimmt jetzt auch ein Tupel von Seiten (`dossier.Regel`). Die übrigen Seiten sind unverändert (Referenztest der Kulturseite grün).

**Vor dem Ziehen korrigiert:** Ich habe die vollständige Liste durchgesehen. Von 184 Vorlagen fielen 19 weg, 3 kamen hinzu, 4 wechselten den Strang.
- **Entfallen:** Vergütung in kommunalen Unternehmen, Glasfaserverteiler als Ortsangabe, Beherbergungssteuer, „Feuerwehrtopf“, Lieferung von Schließfächern „für die Liegenschaften“, Projektbeirat Stadthalle (Besetzung, nichtöffentliche Punkte), Campus Endenich (Bauprojekte), EU-Verordnungen (Kunstrasen, Luftqualität), Verband binationaler Familien und Partnerschaften, Anfrage zur Beethovenhalle, Tafel und Abfallvermeidung („weitere“, stehen auf anderen Seiten).
- **Umgeordnet:** UCLG World Congress von Zentren zu Internationales; Cybersicherheits-Standort und „Hightech Spaces“ von „weitere“ zu Wirtschaftsförderung.
- **Neu:** Geschäftssituation in der Friedrich-Breuer-Straße (Zentren, 2), Anfrage zum Cybersicherheits-Standort (261656, Wirtschaftsförderung).

## Weitere Festlegungen (Entscheidungen 02.11.2026)
- **Prozessbild:** Punkte nur mit Beratung in Rat, Hauptausschuss, Wirtschafts- oder Wissenschaftsausschuss; je eine Bahn für beide Ausschüsse.
- **Sitzungen:** beide Ausschüsse, Finanzausschuss, Hauptausschuss, Rat, Bezirksvertretungen.
- **Haushalt:** Produktbereich 15. Unter „Was diese Seite nicht zeigt“: Plan 2026 vor allem WorldCCBonn (21,1 Mio. €) und Beethovenhalle (6,0 Mio. €, Kulturseite), Wirtschaftsförderung 4,0 Mio. €, Tourismus 2,0 Mio. € (Fundstelle `WEITERE.md`).
- **„Wer berät mit“:** beide Ausschüsse (je 21 Mitglieder; 9 bzw. 10 sachkundige Bürger:innen).
- **Farben:** Indigo (Schrift #3730a3, Kontrast 9,9:1 auf Weiß, 8,7:1 auf der hellen Kachelfläche); Symbol: Balken mit Linie.

## Stand 02.11.2026
168 Vorlagen in 103 Verfahren, 23 Punkte im Prozessbild:

| Strang | Vorlagen |
|---|---|
| Wirtschaftsförderung und Arbeit | 34 |
| Tourismus, Zentren und Stadtmarketing | 22 |
| Liegenschaften | 44 |
| Wissenschaft und Internationales | 63 |
| weitere | 5 |

**Überschneidungen:** mit Digitale Verwaltung keine (die Digitalseite überspringt Vorlagen dieser Seite). Soziales 9 (Ausbildungsmarkt, Unternehmer mit Migrationshintergrund), Wohnen 7 (Einzelhandels- und Zentrenkonzept, Gewerbestandort Beuel), Schule 6 (Städtepartnerschaften mit Schulen), Klima 5 (eumayors, Verpachtung), Sicherheit 3, Verkehr 3 (Nordbrücke).

**Liegenschaften ohne Wohnseite:** 20 Vorlagen aus 8 Verfahren bleiben nur auf der Wohnseite: Teile des Amerikanischen Clubs (260012, 260084-01, 260379, 260668, VEBOWAG 261018), 261791 (Stadthalle), 260684 (Leerstand von Infrastruktur) und 261253 (Leerstands-Liegenschaften des Gebäudemanagements für Wohnraum). 35 Vorlagen des Amts 03 oder der Ausschüsse fallen in „weitere“ weg, weil sie auf einer anderen Seite stehen.

## Prüfbogen
`data/export/wirtschaft/stichprobe_wirtschaft.tsv`, Schritt `wirtschaft-stichprobe`. Er wird einmal gezogen und danach nicht überschrieben.
- **25 zugeordnete Vorlagen:** je 5 aus den fünf Strängen („weitere“ vollständig). Frage: Passt der Strang?
- **5 nicht zugeordnete Vorlagen** mit Wörtern des Themas am Wortanfang (Gegenprobe). Frage: Fehlt die Vorlage?

## Grenzen und offene Fragen
- Der Amerikanische Club ist geteilt: Gutachten und Dringlichkeitsanträge stehen hier, Denkmalschutz und VEBOWAG nur auf der Wohnseite. So ist es entschieden; soll das Verfahren trotzdem ganz hier stehen?
- Das Grundstücksgeschäft Hangelar (17 Vorlagen in 4 Verfahren, Beteiligung Flugplatzgesellschaft) steht unter Liegenschaften. Gehört es dorthin?
- Städtepartnerschaften der Bezirksvertretungen (12 Vorlagen, meist Zuschüsse an Schulen und Vereine) stehen unter Internationales. Sollen sie bleiben?
- „weitere“ hat nur 5 Vorlagen. Viele Mitberatungen stehen auf anderen Seiten.
- Glasfaserausbau steht bei der Wirtschaftsförderung, nicht bei der digitalen Verwaltung. Ist das richtig?
