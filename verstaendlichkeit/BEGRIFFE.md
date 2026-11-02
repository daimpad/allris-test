# Begriffe sichtbar machen (02.11.2026)

**Grundlage:** `phase0/BERICHT.md`, Abschnitt 2, mit den Entscheidungen des Auftraggebers vom 02.11.2026: Erklärung zum Aufklappen im Vorgang, Akkordeon auf Themen- und Gebietsseiten, einfachere Wörter, eigene Seite `begriffe/`.

## Umsetzung
- **Glossar** (`pipeline/glossar.py` → `glossar.json`, eine Quelle für Seite und Ratsassistent):
  - Alle 19 Vorlagenarten der Daten sind jetzt erklärt; dafür sind 8 Einträge neu (Dringlichkeitsantrag, Informationsbrief, Bürgerbrief, Einwohnerfrage, Tagesordnungspunkte in nichtöffentlicher Sitzung, Beschlussvorlage: Einleitung und : Auftrag, Eilentscheidung des Hauptausschusses).
  - Dazu kommen die Kürzel ST, AA, DA, TOP, GO NRW, OB, BV und HA, außerdem Produktbereich, Ansatz, ordentliche Aufwendungen und Bebauungsplan. Neu sind auch die Rollen „Genehmigung“ und „Eilentscheidung“.
  - Jeder Eintrag hat eine Fundstelle. Wo eine Vorlagenart in keinem Regelwerk beschrieben ist, steht „aus Titeln und Beratungsfolge erschlossen“ (Informationsbrief, Bürgerbrief, Beschlussvorlage: Einleitung und : Auftrag).
  - Neu im Glossar: Gruppe und Sprungmarke je Begriff, die Zuordnung Vorlagenart → Begriff (`arten`) und Kürzel → Begriff (`kuerzel`).
- **Vorgang** (`site/app.js`):
  - Neben Drucksache (Kürzel), Art, Amt und Stand steht ein „?“. Ein Klick oder Enter zeigt einen Satz darunter, mit Link auf `begriffe/` (Schalter mit `aria-expanded`).
  - Die Gremien der Prozesslinie öffnen den Reiter „Prozesse“ mit dem Gremium.
  - Das Akkordeon „Was bedeuten die Begriffe?“ verlinkt auf `begriffe/`.
- **Einfachere Wörter:**
  - In der Prozesslinie heißen die Schritte jetzt „Anstoß“ statt „Initiierung“ und „Umsetzung (durch die Verwaltung)“ statt „Vollzug“.
  - Bei Orten steht „Angabe der Stadt“, „nach festen Regeln erschlossen“ oder „mit einem Sprachmodell erschlossen“ statt „Stufe A/B/C“.
  - Im Soll-Abschnitt heißt es „Gremium dieser Art“ statt „Gremienart“.
  - Daten, Audits und Assistent behalten die Fachwörter.
- **Seite `begriffe/`** (`pipeline/begriffsseite.py`, Schritt `seo`, Sitemap):
  - Gruppen: Vorlagen, Gremien, Verfahren, Kürzel, Haushalt, Planung, Ergebnisse, Rollen, Stand, Schritte, Sicherheit der Angaben.
  - Jeder Eintrag hat eine Sprungmarke. Die Seite ist aus dem Menü „Daten“, dem Dialog „Über“, dem Vorgang und der Haushaltsseite verlinkt.
- **Themen- und Gebietsseiten:** Ein eingeklapptes Akkordeon „Begriffe auf dieser Seite“ zeigt nur die Vorlagenarten, Stände und Ergebnisse, die auf der Seite vorkommen.

## Prüfung
- Unit-Tests (`tests/test_begriffsseite.py`: alle Vorlagenarten erklärt, Sprungmarken eindeutig, Akkordeon, Gebietsseite) und JS-Tests grün.
- Browser-Test `tests/browser/begriffe.test.mjs` geprüft:
  - Aufklappen per Maus und Tastatur;
  - „Anstoß“ statt „Initiierung“, kein „Stufe A/B/C“ beim Ort;
  - das Gremium öffnet den Reiter „Prozesse“;
  - `begriffe/#st` springt zum richtigen Eintrag;
  - das Akkordeon auf der Kulturseite;
  - axe ohne Verstöße bei 1440 und 390 px.
