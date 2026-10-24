# Kontextdaten je Ortsteil – Zuschaltbare Flächen (24.10.2026)

Umsetzung nach Freigabe des Plans. Entscheidungen des Auftraggebers vom 24.10.2026: Überschwemmungsgebiete nach Art unterscheiden; Flächen erst ab Ortsteil-Zoom.

## Was umgesetzt ist
- **Karte:** zwei Schalter neben „Bebauungspläne“: „Überschwemmungsgebiete“ und „Bodenrichtwerte“. Auf dem Handy liegen sie unter „Kartenoptionen“.
  - Die Daten werden erst beim Einschalten geladen.
  - Gezeichnet wird ab Zoomstufe 13. Darunter steht in der Legende „Zum Anzeigen der Flächen hineinzoomen“.
  - Der Zustand steht in der Adresse (`ebenen=uesg,brw`).
- **Überschwemmungsgebiete:** festgesetzt (dunkler) und vorläufig gesichert (heller, gestrichelt), ohne Klick-Inhalt. Hinweis: Einordnung, keine Aussage zu Starkregen; verbindlich sind die Karten des Landes.
- **Bodenrichtwerte:** 317 Zonen für Wohnbauland in fünf Stufen (Quintile der Zonenwerte, auf 10 €/m² gerundet). Beim Überfahren oder Antippen erscheinen Wert, Ergänzung (Ein- und Zweifamilienhäuser bzw. Mehrfamilienhäuser), Zone und Stichtag. Hinweis: andere Nutzungen fehlen; verbindlich ist BORIS NRW.
- **Legende:** Quelle, Lizenz und Stand je Ebene; Tour und Quellenangaben ergänzt.
- **Pipeline:**
  - Der Schritt `kontext` schreibt `flaechen/ueberschwemmung.json` (rund 280 KB) und `flaechen/bodenrichtwerte.json` (rund 410 KB), um etwa 5 m vereinfacht; komprimiert zusammen rund 170 KB.
  - `kontext-ausschnitte` lässt sich auf einzelne Quellen beschränken (`KONTEXT_NUR=ueberschwemmung`).

## Neuer Ausschnitt der Überschwemmungsgebiete
- Der Ausschnitt enthält jetzt die Gesamtfläche (wie bisher, für die Kennzahl) und zusätzlich die vorläufig gesicherten Teile, die nicht zugleich festgesetzt sind (nur für die Karte).
- Ein erster Versuch, die Flächen nur getrennt nach Art abzulegen, ließ nach der Vereinfachung schmale Spalten an gemeinsamen Grenzen. Vilich-Müldorf fiel dadurch von 6,5 auf 5,6 %. Das Schließen der Spalten mit 2 m veränderte dafür andere Ortsteile (Godesberg-Nord 2,8 → 5,6 %).
- Mit der Gesamtfläche sind alle Kennzahlen unverändert (51 Ortsteile, 4 Stadtbezirke, ganz Bonn).

## Prüfung
- Python- und Node-Tests; Browser-Test (Schalter, Adresse, Flächen ab Zoom 13, Legende mit Quelle, Hinweis beim Herauszoomen); axe ohne Verstöße.

## Offen
- Wanderung, sobald die Statistikstelle antwortet.
