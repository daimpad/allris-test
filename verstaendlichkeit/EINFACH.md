# Seite in Einfacher Sprache (02.11.2026)

**Grundlage:** `phase0/BERICHT.md`, Abschnitt 3.

**Entscheidungen des Auftraggebers (02.11.2026):**
- acht Abschnitte;
- überall gut sichtbar verlinkt;
- direkt veröffentlichen, geprüft wird danach.

## Umsetzung
- **Seite `einfach/`** (`pipeline/einfachseite.py`, Schritt `seo`, Sitemap), acht Abschnitte:
  - Was ist die RIS-Karte?
  - Wer entscheidet in Bonn?
  - Wie läuft eine Sache ab? (fünf Schritte als nummerierte Liste)
  - Was bedeuten die Wörter? (14 Wörter)
  - Wie benutze ich die Karte?
  - Wie kann ich mitmachen?
  - Was die Karte nicht kann
  - Kontakt
- **Umfang:** rund 810 Wörter Fließtext, im Mittel acht Wörter je Satz.
- **Fundstellen:** Fünf Zeilen „Für Fachleute“ nennen die Fundstellen (GO NRW, Geschäftsordnung des Rates, Quellen der Daten).
- **Wörter:** Die 14 Wörter haben denselben Sinn wie das Glossar, sie sind nur einfacher gesagt. „zur Kenntnis genommen“ ist ausdrücklich nicht „abgelehnt“.
- **Grenzen der Seite:**
  - Sie heißt „Einfache Sprache“ und nicht „Leichte Sprache“, weil keine Prüfgruppe sie geprüft hat.
  - Sie enthält keine Bewertung und keine Zusagen zum Erfolg eines Bürgerantrags.
- **Verlinkung:**
  - im Startfenster „Los geht's“;
  - im Fuß aller statischen Seiten;
  - im Menü „Daten“;
  - im Dialog „Über“ (Weitere Seiten, Was ist neu?).

## Prüfung
- Unit-Tests: `tests/test_einfachseite.py` prüft Abschnitte, Umfang, Satzlänge, Fundstellen und den Link im Fuß.
- Browser-Test in `tests/browser/begriffe.test.mjs` geprüft:
  - acht Abschnitte;
  - Links im Startfenster und im Fuß;
  - axe ohne Verstöße bei 1440 und 390 px.
- Die Prüfung des Textes durch den Auftraggeber steht aus. Er hat entschieden, dass sie nach der Veröffentlichung folgt.
