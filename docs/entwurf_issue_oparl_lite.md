# Entwurf: Issue an OParl-Lite (Codeberg)

Ziel: https://codeberg.org/machdenstaat/oparl-lite-2/issues · Stand der Prüfung 23.10.2026 · vom Auftraggeber freigegeben, er stellt das Issue selbst ein.

Geprüft vor dem Entwurf:
- `Paper.underDirectionOf` ist in OParl-Lite inzwischen enthalten (100 von 100 neuesten Vorlagen); dieser Teil entfällt.
- `Paper` hat kein Feld `location`; `locations` hat 1.201 Einträge. Bei 20 zufällig gewählten Vorlagen mit `location` in der OParl-API der Stadt war `geoReferences` leer (Stichprobe aus `data/export/audit_geokodierung_bonn.tsv`, Methode `oparl_location`).
- Kein offenes oder geschlossenes Issue zum Thema in `oparl-lite-2` oder `stadt-bonn-oparl`.

---

**Titel:** Ortsangabe der Stadt (`paper.location`) mit den Vorlagen verknüpfen

Hallo,

für die RIS-Karte Bonn (https://ris-bonn.datenatlas.de/, Code: https://github.com/daimpad/allris-test) nutze ich OParl-Lite für Sitzungen, Ergebnisse und Texte – danke dafür. Dass `underDirectionOf` inzwischen enthalten ist, habe ich gesehen.

Eine Lücke ist mir aufgefallen:
- In der OParl-API der Stadt haben 1.816 von 24.915 Vorlagen ein Feld `location` (7 %, Stand 18.10.2026), fast alle mit Punktkoordinate. Es sind vor allem Bürgeranträge nach § 24 GO NRW, Anregungen und Beschwerden und die Stellungnahmen dazu.
- OParl-Lite hat 1.201 Locations, aber die Vorlagen sind nicht damit verknüpft. Bei 20 zufällig gewählten dieser Vorlagen war `geoReferences` jeweils leer, und `Paper` hat kein Feld `location`.

Vorschlag: `paper.location` beim Import übernehmen, etwa als `geoReference` mit eigener `source` (z. B. „oparl“). So lässt sich die Angabe der Stadt von den abgeleiteten Treffern aus geotag unterscheiden.

Viele Grüße
Damian
