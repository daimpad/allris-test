# Kultur und Haushalt – Phase 2: Prozessbild (25.10.2026)

Ziel: Der Ablauf soll grafisch statt textlich zu erkennen sein. Man soll sehen, was entschieden ist, was noch entschieden wird und wo man sich einbringen kann.

Entscheidungen des Auftraggebers:
- Zeitleiste mit Bahnen
- als Punkte die Beschlüsse und Anträge
- alle vier Aufrufe
- Platz oben auf der Themenseite

## Umsetzung (`pipeline/prozessbild.py`, Daten aus `pipeline/dossier.py`)
- **Zeitleiste (SVG, ohne Skript erzeugt).**
  - **Zeitachse:** Sie reicht von November 2025 bis März 2027. Die Monate ab September 2026 sind breiter gezeichnet. Eine Linie zeigt den Datenstand.
  - **Bahnen:** „Haushalt 2027/2028“ mit Aufstellung (nicht öffentlich), Einbringung und Beratung, Beschluss und Genehmigung; darunter Bezirksvertretungen, Kulturausschuss, andere Ausschüsse, Finanzausschuss sowie Hauptausschuss und Rat.
  - **Phasen:** geplant laut Terminplan 261064, abgeleitet.
  - **Punkte:** Beschlüsse und Anträge (25 am 25.10.2026, nach Aufnahme von „Schauspiel“ in die Bühnen-Regel) aus den Strängen Haushalt, Bühnen und Kulturförderung, nummeriert und unterschieden nach entschieden, beraten oder offen.
  - **Lage eines Punkts:** die letzte Beratung mit Ergebnis, sonst die nächste. Ohne Beratungsfolge liegt der Punkt auf der Bahn des ersten Gremiums, ersatzweise des Rates, am Tag der Vorlage.
  - **Sitzungen:** Kommende öffentliche Sitzungen tragen ein Hand-Symbol, dazu die Frist 21 Tage vorher (GeschO §§ 26, 27; berechnet). Der Zeitraum der Haushaltsberatung ist farbig hinterlegt.
  - **Barrierefreiheit:** Die Grafik hat einen Titel und eine Beschreibung. Die nummerierte Liste darunter ist die Textfassung.
  - **Schmale Bildschirme:** Die Zeitleiste ist waagerecht verschiebbar. `site/thema.js` setzt sie beim Laden auf den Datenstand.
- **Stand je Strang:** gestapelte Balken in HTML (entschieden, in Beratung, zur Kenntnis genommen oder ohne Votum, offen).
- **Aufrufe:**
  - Kalender `dossiers/kultur.ics`: Sitzungen von Kulturausschuss, Kulturkommission, Finanzausschuss, Hauptausschuss, Rat und Bezirksvertretungen.
  - Feed `dossiers/kultur.xml`.
  - Sitzung besuchen.
  - Frage oder Anregung einreichen: Einwohnerfrage nur in den Bezirksvertretungen (GeschO § 26), Bürgerantrag nach § 24 GO NRW, mit der nächsten offenen Frist.
- **Liste „Nächste Sitzungen“:** Sie nennt jetzt auch je eine Sitzung jeder Bezirksvertretung, mit Frist. Der Satz zur Einwohnerfragestunde ist berichtigt: Es gibt sie in den Bezirksvertretungen, nicht in allen Sitzungen.

## Grenzen
- Die Phasen sind geplant. Der Kulturausschuss tagt am 01.12.2026, also nach dem Finanzausschuss am 26.11.2026. Ob der Haushalt dort beraten wird, zeigt erst die Tagesordnung.
- Die Linie des Datenstands ändert die Seite täglich.

## Nachtrag: Bild zum Teilen (25.10.2026)
- **Dateien:** `dossiers/kultur-zeitleiste.svg` und `.png` (doppelte Auflösung), täglich im Export erzeugt und im Datenpaket enthalten.
- **Inhalt:** die Zeitleiste mit Überschrift, Datenstand, Hinweis auf die abgeleiteten Angaben, Adresse der Themenseite (Nummern, Vorlagen, Fristen) und Quellen. So ist das Bild auch ohne die Seite verständlich.
- **Auf der Seite:** Links zu PNG und SVG unter der Grafik. Das PNG dient als Vorschaubild beim Teilen (Open Graph, `summary_large_image`).
- **Technik:** Das PNG erzeugt `cairosvg` (in `requirements.txt`). Fehlt Cairo auf dem Server, entsteht nur das SVG; Seite und Vorschaubild entfallen dann ohne Fehler.
