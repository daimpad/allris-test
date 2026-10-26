# Verkehr und Mobilität – Phase 0: Prüfung des Materials (26.10.2026)

**Anlass:** Entscheidung des Auftraggebers vom 26.10.2026, weitere Themenseiten anzulegen. Erstes Thema ist Verkehr und Mobilität.

**Frage:** Lässt sich das Thema wie „Kultur und Haushalt“ in Strängen mit Prozessbild zeigen?

**Datenstand und Abgrenzung:**
- Abruf vom 26.10.2026; Vorlagen der 12. Wahlperiode (ab 01.11.2025).
- Grundlage ist die vorhandene, abgeleitete Themenzuordnung „Verkehr und Mobilität“. Sie stützt sich auf das Amt 61-3 Stadtverkehr, das Tiefbauamt (66), den Ausschuss für Mobilität und Verkehr sowie Stichwörter im Titel.

## Ergebnis: positiv, aber anders gebaut als Kultur
- **Umfang:** 897 Vorlagen in 515 Verfahren; zum Vergleich: Kultur hat 143. Davon:
  - 640 mit Ortsbezug;
  - 575 nur in Bezirksvertretungen beraten;
  - 166 aus der Einwohnerschaft (Bürgeranträge, Einwohnerfragen).

  Das Thema ist stark örtlich: viele kleine Vorgänge zu einzelnen Straßen, Kreuzungen und Haltestellen.
- **Federführung:**

  | Federführend | Vorlagen | Inhalt |
  |---|---|---|
  | Ratsbüro | 285 | Anträge der Fraktionen |
  | Stadtplanungsamt | 225 | vor allem 61-3 Stadtverkehr |
  | Tiefbauamt | 148 | |
  | Bürgerbüro | 118 | Bürgeranträge |
  | Bürgerdienste | 73 | |
- **Gremien:**

  | Gremium | Vorlagen |
  |---|---|
  | Bezirksvertretung Bonn | 295 |
  | Bezirksvertretung Beuel | 194 |
  | Ausschuss für Mobilität und Verkehr | 178 |
  | Bezirksvertretung Bad Godesberg | 158 |
  | Rat | 147 |
  | Bezirksvertretung Hardtberg | 67 |
- **Schwerpunkte nach Wörtern im Titel** (überschneiden sich):

  | Schwerpunkt | Vorlagen |
  |---|---|
  | Straßen und Brücken | 220 |
  | Rad- und Fußverkehr | 215 |
  | Verkehrssicherheit (Tempo, Querungen, Ampeln) | 140 |
  | Bus und Bahn | 139 |
  | Parken | 99 |
  | Konzepte und Pläne | 33 |
- **Größere Verfahren:**
  - **Sperrung der Nordbrücke:** 58 Vorlagen in 41 Verfahren, die erste vom 14.01.2026, die letzte vom 15.10.2026. Darunter:
    - Ratsbeschluss 261154 (Erste Maßnahmen zu ÖPNV, Fuß- und Radverkehr; „geändert beschlossen“) und Sachstandsbericht 261154-03;
    - ÖPNV-Ersatzkonzept 260185;
    - Mitteilungen der Taskforce (261618, 261712);
    - Ergebnisse einer Umfrage (261898);
    - 11 Dringlichkeitsanträge.
  - **Nahverkehrsplan:** Fortschreibung mit den Maßnahmen zum Fahrplanwechsel im Dezember 2026 (260890 mit 10 Vorlagen) und Neuaufstellung (240782).
  - **Parken:** 42 Vorlagen, darunter die 16. Änderung der Parkgebührenordnung (260932) und das Parkraumkonzept Beuel-Zentrum.
  - **Weitere:** Seilbahn (8 Vorlagen), Preisanpassung des Schülertickets (253914), Fahrradstraßen.
- **Bezug zu Geld im Titel:** 36 Vorlagen, z. B. Schülerticket, Parkgebühren, Finanzierung des ÖPNV (260353).
- **Haushalt 2027/2028:** Laut 261064 berät jeder Fachausschuss den Entwurf einmal, also auch der Ausschuss für Mobilität und Verkehr. Die Haushaltsbahn der Kulturseite passt deshalb auch hier.
- **Nächste Sitzungen** (laut OParl-API):
  - Ausschuss für Mobilität und Verkehr: 04.11. und 26.11.2026, gemeinsam mit dem Rhein-Sieg-Kreis am 03.12.2026 und 20.01.2027;
  - Hauptausschuss: 05.11. und 03.12.2026;
  - Rat: 12.11. und 10.12.2026;
  - Bezirksvertretungen: im November und Dezember.

## Grenzen und Auffälligkeiten
- **Zuordnung:**
  - 301 Vorlagen sind nur über ein Stichwort im Thema.
  - „Verkehr“ trifft auch die Pflege von „Verkehrsgrün“ (7 Vergabevorlagen des Amts für Umwelt und Stadtgrün). Eine eigene Regel und der Prüfbogen sind daher nötig.
- **Datenschutz:**
  - Bürgeranträge nennen oft Straßen und teils Hausnummern.
  - Hausnummern sind in Titeln aus der Einwohnerschaft schon ausgeblendet (`maske.py`).
  - Die Seite zeigt Vorgänge nur auf Straßen- oder Ortsteilebene.
- **Übersicht:**
  - 897 Vorlagen lassen sich nicht wie bei Kultur in vier Tabellen zeigen.
  - Bei so vielen Punkten wird auch das Prozessbild unübersichtlich: Beschlüsse und Anträge kämen auf 185, davon 61 mit Beratung in Rat, Hauptausschuss oder Ausschuss für Mobilität und Verkehr.
- **Dokumente:** Wie bisher ohne Zitate und Auszüge.
- **Beträge:** Beträge zu Investitionen stehen in den Dokumenten und im Haushaltsplan, nicht in den Metadaten.

## Empfehlung (zur Entscheidung)
Eine Themenseite „Verkehr und Mobilität“ mit wenigen Strängen:

1. **Sperrung der Nordbrücke** – ganzes Verfahren über den Titel, wie die Bühnen bei Kultur.
2. **Bus und Bahn** – Nahverkehrsplan, Stadtbahn, Bus, Haltestellen, Tickets, Seilbahn.
3. **Rad- und Fußverkehr.**
4. **Parken** – Parkraum, Gebühren.
5. **Verkehrssicherheit und Straßen**, eingeklappt.

Die örtlichen Vorgänge der Bezirksvertretungen erscheinen nach Stadtbezirk geordnet und eingeklappt. Das Prozessbild zeigt nur Beschlüsse und Anträge aus Rat, Hauptausschuss und Ausschuss für Mobilität und Verkehr. Danach folgen der Regelentwurf und ein Prüfbogen mit 30 Vorlagen.

## Entscheidungen des Auftraggebers (26.10.2026)
- **Nordbrücke:** ein eigener Strang auf der Verkehrsseite, keine eigene Seite.
- **Stränge:**
  1. Sperrung der Nordbrücke;
  2. Bus und Bahn;
  3. Rad- und Fußverkehr;
  4. Parken.

  Einen Sammelstrang „Sicherheit und Straßen“ gibt es nicht.
- **Übrige Vorlagen:** Die übrigen Vorlagen des Themas erscheinen vollständig, aber nach Stadtbezirk geordnet und eingeklappt.
- **Prozessbild:** nur Beschlüsse und Anträge aus Rat, Hauptausschuss und Ausschuss für Mobilität und Verkehr.
- **Haushalt:** Die Bahn „Haushalt 2027/2028“ steht oben im Bild wie bei Kultur (Phasen laut 261064).
