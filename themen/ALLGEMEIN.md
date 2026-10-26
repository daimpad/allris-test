# Allgemeine Themenseiten – Schritt 1: Umbau (26.10.2026)

Entscheidungen vom 26.10.2026:
- Weitere Themen nach der Kulturseite: Verkehr und Mobilität, Schule und Bildung, Wohnen und Bauen, Klima und Umwelt.
- Je Thema eigene Regeln.
- Die Seiten erscheinen in einer Übersicht `thema/` und im Menü „Auswertung“.

## Umsetzung
- **Beschreibung je Thema:** eine Datei in `pipeline/themenseiten/` (Vorlage: `kultur.py`), eingetragen in `ALLE`. Sie enthält:
  - Stränge mit Regel in Worten und Regeln der Zuordnung (`Regel`, `Zustaendig`);
  - Bahnen und Gremien des Prozessbilds, Sitzungen und Zeitachse;
  - optional Phasen und Schritte laut Terminplan sowie einen Vergleich;
  - die Texte der Seite;
  - die Einstellungen des Prüfbogens.
- **Prüfreihenfolge der Regeln:**
  1. Stammnummern, unabhängig vom Zeitraum;
  2. danach nur Vorlagen ab Beginn des Zeitraums: Verfahren, deren Titel passt (ganzes Verfahren);
  3. dann die übrigen Regeln in ihrer Reihenfolge.

  Die erste passende Regel gilt. Jede Zuordnung bleibt „abgeleitet“ und nennt ihren Grund.
- **Allgemeiner Teil:**
  - `pipeline/dossier.py`: Daten, Seite, Prüfbogen.
  - `pipeline/prozessbild.py`: Bild, Detailfeld, Bild zum Teilen.
  - `export.py` und `seo.py` erzeugen für jedes Thema in `ALLE` die Dateien `dossiers/<key>.json`, `.ics`, `.xml` und `-zeitleiste.svg`/`.png` sowie die Seite unter dem Pfad des Themas.
  - Themen ohne Terminplan zeigen keine Phasen und keinen Abschnitt zum Weg des Verfahrens.
- **Prüfung:** Die Kulturseite blieb Zeichen für Zeichen gleich, mit Testdaten wie mit echten Daten (`kultur.json`, Kalender, Feed, Bild, Seite).
  - `tests/test_themenseiten.py` vergleicht künftig mit den Referenzdateien in `tests/referenz/`, die vor dem Umbau erzeugt wurden.
  - Ein kleines Beispielthema ohne Phasen prüft den allgemeinen Teil.

## Nächste Schritte
- **Übersicht** `thema/`: mit dem ersten neuen Thema.
- **Je Thema, nach jeder Stufe mit Freigabe:**
  - Phase 0 (Material);
  - Regelentwurf;
  - Prüfbogen mit 30 Vorlagen im Gespräch;
  - erst danach geht die Seite online.
