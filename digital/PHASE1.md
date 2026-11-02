# Digitale Verwaltung – Phase 1: Regelentwurf und Prüfbogen (02.11.2026)

**Grundlage:** `../themen/phase0/WEITERE.md`, Abschnitt (c), mit den Entscheidungen vom 02.11.2026 (zwei Seiten statt einer; die erste ist `../wirtschaft/PHASE1.md`).

**Stand:** Entwurf (`ENTWUERFE`), keine Seite, kein Export. Veröffentlichung erst nach Prüfung des Prüfbogens.

**Datenstand:** lokale Datenbank vom 02.11.2026; jüngste Vorlage vom 31.10.2026; Besetzung zum Stichtag 27.10.2026.

## Regeln (`pipeline/themenseiten/digital.py`, abgeleitet, je Vorlage mit Grund)
Die erste passende Regel gilt. Alle Regeln überspringen Vorlagen der Seite Wirtschaft und Wissenschaft (`ohne_seite`); die beiden Seiten nennen keine Vorlage doppelt.

0. **Ausschluss:** Formalien und Sammellisten nichtöffentlicher Punkte; **Personalangelegenheiten** (Beigeordnete, Ausschreibung von Stellen, Stellenplan, Gesundheitsbericht, Firmenfitness, Vergütung); Büromaterial, Bürostühle, Lieferungen, Aktenvernichtung, Geldtransporte, Beflaggung; Inhalte einzelner Internetseiten (Stadttauben); Bewohnerparkausweise, Fahrgastanzeigen, digitale Lehrpfade; Vertretung im Aufsichtsrat.
1. **Digitale Strategie und Steuerung:** Digitalisierungsstrategie, Dachstrategie Digitale Transformation (261619), Bestandsaufnahme, Binnendigitalisierung, Urban Data Platform, Open Data, algorithmische Systeme.
2. **Online-Dienste und Bürgerservice:** Online, Website, Terminbuchung, Bürgerservice, „Digitale Bürgerwabe“, Dienstleistungszentrum, Bezahldienst (Wero), Teilhabe an der digitalen Verwaltung, „Recht auf analoges Leben“, Informationsfreiheit, Bezirksverwaltungsstelle.
3. **IT, Software und Sicherheit:** „IT“ nur in Großbuchstaben, RegioIT, Software und Lizenzen, Open Source, Cyberangriffe, Penetrationstests, ODF, Microsoft 365, digitale Souveränität, Fachverfahren, Apps, KI, Digitalisierungsprojekte.
4. **Verwaltungsmodernisierung und Organisation:** Verwaltungsmodernisierung, Organisationsuntersuchung, organisatorische Leistungsfähigkeit, Aufgabenkritik, Dezernatsneuverteilung, Strukturreform, Umzug aus dem Stadthaus, Verwaltungsgebührenordnung.
5. **„Digital“ allgemein** → IT, nicht mit Kartenthema Verkehr.
6. **Stabsstelle CDO** federführend → Strategie; **Abteilung 10-2 IT** federführend → IT.
7. **Weitere:** Beratung im Digitalisierungsausschuss; nicht Vorlagen der übrigen neun Seiten; eingeklappt.

**Amt 10:** Nur die Abteilung 10-2 zählt über die Federführung. 10-1 (Personal- und Organisationsentwicklung), 10-3 (Zentrale Dienste) und 10-4 (Personalservice) zählen nur mit Wörtern des Themas im Titel.

**Vor dem Ziehen korrigiert:** Ich habe die vollständige Liste durchgesehen. Von 115 Vorlagen fielen 7 weg:
- Stadthaus-Areal (4, Städtebau), Großbaustellen Oper, Stadthaus und Nordbrücke, SPNV-Strukturreform NRW (Verkehr);
- Vertretung im Aufsichtsrat der Digital Hub AG.

Schon im ersten Entwurf ausgeschlossen: Personalvorlagen des Amts 10 (Beigeordnete, Stellenplan, Gesundheitsbericht; 7), Beschaffungen von Möbeln, Material und Diensten (9), „Digital Hub“ und Cybersicherheits-Standort (Wirtschaftsseite).

## Weitere Festlegungen (Entscheidungen 02.11.2026)
- **Prozessbild:** Punkte nur mit Beratung in Rat, Hauptausschuss oder Digitalisierungsausschuss; eigene Bahn „Digitalisierungsausschuss“.
- **Sitzungen:** Digitalisierungsausschuss, Finanzausschuss, Hauptausschuss, Rat, Bezirksvertretungen.
- **Haushalt:** kein Abschnitt (`produktbereich=None`). Die Sprungleiste nennt dann keinen Haushalt, die Kachel keinen Produktbereich (geprüft im Test). Unter „Was diese Seite nicht zeigt“ steht: Digitalisierung gehört zu Produktbereich 01 Innere Verwaltung (Plan 2026: 304,1 Mio. €), der fast die ganze Verwaltung umfasst; dazu ein Link auf „Haushalt auf einen Blick“.
- **„Wer berät mit“:** Ausschuss für Digitalisierung, Dienstleistung und Verwaltungsmodernisierung (20 Mitglieder, davon 9 sachkundige Bürger:innen).
- **Farben:** Schiefer zu Himmelblau (Schrift #334155, Kontrast 10,4:1 auf Weiß, 9,1:1 auf der hellen Kachelfläche); Symbol: Bildschirm mit spitzen Klammern.

## Stand 02.11.2026
108 Vorlagen in 53 Verfahren, 24 Punkte im Prozessbild:

| Strang | Vorlagen |
|---|---|
| Digitale Strategie und Steuerung | 24 |
| Online-Dienste und Bürgerservice | 16 |
| IT, Software und Sicherheit | 48 |
| Verwaltungsmodernisierung und Organisation | 20 |
| weitere | 0 |

**Überschneidungen:** mit Wirtschaft und Wissenschaft keine. Soziales 9 („Wohni“, „Recht auf analoges Leben“, Ausländerbehörde, Amt für Soziales und Wohnen), Sicherheit 8 (Abrechnung im Rettungsdienst, Funkmeldeempfänger), Wohnen 5 (Urban Data Platform, Bürgerantrag zum Bauordnungsamt), Verkehr 5 (Dezernatsneuverteilung, Baumkontrollsoftware), Kinder 2, Schule 2 (Microsoft 365 an Schulen).

## Prüfbogen
`data/export/digital/stichprobe_digital.tsv`, Schritt `digital-stichprobe`. Er wird einmal gezogen und danach nicht überschrieben.
- **25 zugeordnete Vorlagen:** Strategie 6, Online 6, IT 7, Organisation 6; „weitere“ war leer. Frage: Passt der Strang?
- **5 nicht zugeordnete Vorlagen** mit Wörtern des Themas am Wortanfang (Gegenprobe). Frage: Fehlt die Vorlage?

## Grenzen und offene Fragen
- „weitere“ ist leer: Alle übrigen Vorlagen des Ausschusses stehen in einem Strang, auf einer anderen Seite oder sind Formalien. Soll der Strang bleiben?
- Die Dezernatsneuverteilung (261626) steht unter Organisation. Ist sie eine Personalangelegenheit?
- Digitale Projekte der Fachämter (Rettungsdienst, Wohngeld, Spielplätze, Bauaufsicht) stehen unter IT und auf der Seite des Fachthemas. Reicht das?
- Die Verwaltungsgebührenordnung steht unter Organisation. Gehört sie zum Thema?
- Die Übersicht `thema/` sagt, jede Seite nenne einen Produktbereich. Vor der Veröffentlichung ist der Satz anzupassen.
