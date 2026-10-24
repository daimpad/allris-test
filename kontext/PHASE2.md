# Kontextdaten je Ortsteil – Phase 2: Karte und Steckbrief (24.10.2026)

Umsetzung nach Freigabe des Plans. Daten: `export/bonn/kontext.json` (Phase 1), beim Start mitgeladen (15 KB).

- **Flächen färben:** In der Legende oben links neue Gruppe „Zahlen zum Gebiet (abgeleitet)“ mit Anteil unter 18 und ab 65 Jahren, Nettokaltmiete, Bodenrichtwert Wohnbauland, Hitze (dringender Handlungsbedarf) und Überschwemmungsgebiet. Fünf Stufen nach den Werten der Ortsteile (gleiche Stufen für Stadtbezirke), grau „keine Angabe (unter 100 Einwohnern)“; Legende mit Methode, Quelle, Lizenz und Stand und dem Hinweis „zur Einordnung, kein Urteil“. Adresse: `flaechen=kontext-…`.
- **Nicht gefärbt:** Zahl der Kitas, Kita-Plätze und Haltestellen – absolute Zahlen bilden vor allem die Größe eines Ortsteils ab; sie stehen im Steckbrief.
- **Beim Überfahren:** Wert des Gebiets, Wert des Stadtbezirks und ganz Bonns, Stand, „abgeleitet“.
- **Steckbrief:** In der Liste unter „Abonnieren“ der einklappbare Abschnitt „Zahlen zu …“: alle Kennzahlen des Ortsteils neben dem Stadtbezirk (bei einem Stadtbezirk neben ganz Bonn), Hinweis zur Einordnung, Quellen und Methode im Akkordeon; keine Rangfolge, keine Wertung.
- Quellen-Akkordeon und Tour ergänzt; Browser-Test (Färbung, Adresse, Legende, Steckbrief, axe); Test-Workflow erzeugt `kontext.json`.
- Geprüft: Desktop 1440 px und Mobil 390 px, axe (WCAG 2.1 A/AA) ohne Verstöße, keine Skriptfehler.

Später (nicht in dieser Phase): zuschaltbare Flächen für Überschwemmungsgebiete und Bodenrichtwertzonen (etwa 1,7 MB); Phase 3: Vorgang und Ratsassistent.
