# Entwurf: Issue an OParl-Lite (Codeberg)

Stand: Entwurf vom 20.10.2026, noch nicht veröffentlicht. Veröffentlichung durch den Auftraggeber unter
https://codeberg.org/machdenstaat/oparl-lite-2/issues (Spiegel) bzw. https://codeberg.org/machdenstaat/stadt-bonn-oparl/issues (Crawler).

---

**Titel:** Felder `underDirectionOf` und `location` aus der OParl-API Bonn übernehmen

Hallo,

danke für OParl-Lite Bonn. Für die RIS-Karte Bonn (https://ris-bonn.datenatlas.de/, Hackathon „Hack den Stadtrat“) nutze ich die GraphQL-API für Sitzungen, Tagesordnungspunkte und Ergebnisse. Zwei Felder der städtischen OParl-API fehlen im Spiegel; ich lese sie deshalb zusätzlich direkt bei der Stadt.

1. **`underDirectionOf` (federführender Verwaltungsbereich)** am Objekt `Paper`: in der OParl-API Bonn bei allen 24.915 Vorlagen gesetzt, als Verweis auf eine `Organization` mit `organizationType: "Verwaltungsbereich"`, zum Beispiel „61-3 Stadtverkehr“ mit `classification: "61 Stadtplanungsamt"`. Damit lässt sich je Vorlage das zuständige Amt angeben und nach Amt filtern.
2. **`location` (Ort der Vorlage)** am Objekt `Paper`: bei 1.816 Vorlagen gesetzt (7,3 %), überwiegend bei Bürgeranträgen, Anregungen und Beschwerden und den Stellungnahmen dazu. Das Objekt `Location` enthält `streetAddress`, `postalCode`, teils `subLocality` und `geojson` (Punkt, WGS84). Im Spiegel ist die Liste der Locations derzeit leer.

**Vorschlag:**
- `Paper.underDirectionOf` als Verweis auf `Organization` aufnehmen; die Verwaltungsbereiche sind über `/organizations` bereits vorhanden.
- `Location` als eigenes Objekt und `Paper.location` als Verweis aufnehmen.

**Hinweis zum Datenschutz:** Bei Bürgeranträgen kann `streetAddress` eine Hausnummer enthalten. Die RIS-Karte zeigt solche Orte nur auf Ebene der Straße oder des Ortsteils. Für den Spiegel wäre zu überlegen, ob er die Adresse unverändert durchreicht.

Lizenz der Felder: OParl-API der Stadt Bonn, CC0 (laut opendata.bonn.de).

Viele Grüße
Damian Paderta
