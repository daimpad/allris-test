# Kinder, Jugend und Familie – Phase 1: Regelentwurf und Prüfbogen (02.11.2026)

**Grundlage:** `../themen/phase0/WEITERE.md` mit den Entscheidungen vom 02.11.2026.

**Stand:** Nach der Prüfung im Gespräch am 02.11.2026 sind die Regeln ergänzt (A und B), und die Seite ist veröffentlicht (`PRUEFUNG.md`). Bis dahin war `kinder` ein Entwurf ohne Seite und ohne Export.

**Datenstand:** OParl-API und OParl-Lite neu abgerufen am 02.11.2026; jüngste Vorlage vom 31.10.2026.

## Regeln (`pipeline/themenseiten/kinder.py`, abgeleitet, je Vorlage mit Grund)
Die erste passende Regel gilt.

0. **Ausschluss:**
   - Formalien und Sammellisten nichtöffentlicher Punkte, Entsendungen, Zuständigkeitsordnung.
   - Bauanträge auf Grundstücken und Haustypen („Einfamilienhaus“).
   - Offener Ganztag und Schulsozialarbeit (bleiben auf der Schulseite).
   - Kitas als bloße Ortsangabe bei Parken, Halteverbot, Winterdienst, Laternen, Abfallbehältern und Wahlwerbung.
1. **Kitas und Kindertagespflege:** Kita, Kindertagesstätte, Kindergarten, Kindertagespflege, Familienzentrum, Betreuungszeiten, Elternbeiträge, KiBiz. Ausgenommen sind Vorlagen mit dem Kartenthema Verkehr.
2. **Spielplätze und Freiflächen:** Spielplatz, Spielfläche, Bolzplatz, Skateanlage, Pumptrack, Kletterturm, Spielgeräte, „kinderfreundlich“. Ausgenommen sind Vorlagen mit dem Kartenthema Verkehr. Spielplätze stehen auch auf der Klimaseite.
3. **Beteiligung:** Kinder- und Jugendbeteiligung, Jugendrat, Kinderrechte, Weltkindertag.
4. **Jugendarbeit und Jugendförderung:** Jugendzentrum, Jugendtreff, Jugendarbeit, Jugendförderung, Jugendring, Streetwork, Gewaltprävention, Ferienangebote.
5. **Familie, Kinderschutz und Hilfen:** Frühe Hilfen, Kinderschutz, Hilfen zur Erziehung, Jugendhilfe, Inklusionsassistenz, Familien, Kinderarmut, Pflegekinder, Alleinerziehende.
6. **Weitere:** Amt 51 federführend oder Beratung im Ausschuss für Kinder, Jugend und Familie (oder in seinem Unterausschuss); eingeklappt.
7. **Beteiligung (Beirat):** Beratung im Beirat Kinder- und Jugendbeteiligung, nur mit „Kinder“ oder „Jugend“ im Titel.

**Vor dem Ziehen korrigiert:** Ich habe die vollständige Liste durchgesehen, bevor ich den Prüfbogen gezogen habe. Danach fielen 12 Fehltreffer weg:
- Kitas als Ortsangabe (Parksituation, Winterdienst, Laternen, Abfallbehälter, Wahlwerbung);
- „Familienfest“;
- „Elternbefragung“ zu Gesamtschulplätzen;
- ein Wettbewerb im Skateboarding;
- Formalien (Entsendung, Zuständigkeitsordnung).

„Familie“ im Namen des Amts zählt nicht als Titelwort.

## Weitere Festlegungen (Entscheidungen 02.11.2026)
- **Prozessbild:** Punkte nur mit Beratung in Rat, Hauptausschuss oder Ausschuss für Kinder, Jugend und Familie.
- **Bahnen:** Haushalt 2027/2028, Bezirksvertretungen, „Jugendhilfeausschuss“, andere Ausschüsse, Finanzausschuss, Hauptausschuss und Rat. „Jugendhilfeausschuss“ ist der gesetzliche Name nach § 71 SGB VIII; der volle Name passt nicht in die Spalte.
- **Sitzungen:** Fachausschuss, Beirat Kinder- und Jugendbeteiligung, Finanzausschuss, Hauptausschuss, Rat und die Bezirksvertretungen.
- **Spielplätze** werden je Stadtbezirk gegliedert.
- **Haushalt:** Produktbereich 06. Der Link führt bei der Veröffentlichung direkt in die Kachel 06 der Haushaltsseite.
- **Sitzungen ohne Gremium** (25.11.2026, Titel mit „Kinder-, Jugend“) erhalten den Namen des bekannten Gremiums (`export.gremium_der_sitzung`).

## Stand 02.11.2026
122 Vorlagen:

| Strang | Vorlagen |
|---|---|
| Kitas und Kindertagespflege | 40 |
| Spielplätze und Freiflächen | 37 |
| Jugendarbeit und Jugendförderung | 18 |
| Familie, Kinderschutz und Hilfen | 7 |
| Beteiligung von Kindern und Jugendlichen | 7 |
| weitere | 13 |

## Prüfbogen
`data/export/kinder/stichprobe_kinder.tsv`, erzeugt mit dem Schritt `kinder-stichprobe`. Er wird einmal gezogen und danach nicht überschrieben.
- **25 zugeordnete Vorlagen:** Kitas 5, Spielplätze 5, Jugendarbeit 4, Familie 4, Beteiligung 3, weitere 4. Frage: Passt der Strang?
- **5 nicht zugeordnete Vorlagen** mit Kinder, Jugend, Eltern, Ferien, Schwimmen oder Betreuung im Titel (Gegenprobe). Frage: Fehlt die Vorlage auf der Seite?
