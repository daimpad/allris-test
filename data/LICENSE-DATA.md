# Lizenzen der Datendateien

Die Dateien in diesem Verzeichnis sind Rohdaten Dritter und stehen nicht unter der MIT-Lizenz des Codes.

| Datei | Quelle | Lizenz | Abruf |
|---|---|---|---|
| raw/papers.jsonl (24.912 Vorlagen), raw/organizations.json (368), raw/verwaltungsbereiche.json (145) | OParl-API der Stadt Bonn, https://www.bonn.sitzung-online.de/oparl/bodies/1 – Datensatz „Ratsinformationssystem OParl-API“, https://opendata.bonn.de/dataset/ratsinformationssystem-oparl-api | CC0 1.0 (Stadt Bonn); angehängte Dokumente (PDFs) sind vom Datensatz ausgenommen | 17.10.2026 |
| geo/ortsteile_bonn.geojson (51 Ortsteile), geo/stadtbezirke_bonn.geojson (4 Stadtbezirke) | Stadt Bonn, https://stadtplan.bonn.de/geojson?Thema=21247 und ?Thema=14574 – https://opendata.bonn.de/dataset/flächen-der-ortsteile, https://opendata.bonn.de/dataset/flächen-der-stadtbezirke | CC0 1.0 (Stadt Bonn) | 17.10.2026 |
| phase0/endenich_streets_photon.json | Photon (photon.komoot.io), Daten © OpenStreetMap-Mitwirkende | ODbL 1.0 | 17.10.2026 |
| raw/consultations_lite.jsonl (lokal, nicht im Repository) | OParl-Lite Bonn, https://oparl.bonn.machdenstaat.de/graphql | CC BY 4.0 (machdenstaat) | bei Abruf |
| raw/osm_streets.json, raw/osm_tiles/ (lokal, nicht im Repository) | OpenStreetMap über Overpass API | ODbL 1.0, © OpenStreetMap-Mitwirkende | bei Abruf |
| export/endenich/vorlagen.json, export/endenich/vorlagen.geojson | abgeleitet aus OParl-API Stadt Bonn (CC0), OParl-Lite Bonn (Sitzung, Tagesordnungspunkt, Ergebnis), Ortsteilpolygonen (CC0) und OSM (Straßenlage, Ortsbezüge mit `source: osm`); Quellen und Abrufzeitpunkte stehen in `meta.sources` | Felder aus OParl-Lite: CC BY 4.0 (Namensnennung: OParl-Lite Bonn, machdenstaat); Ortsbezüge aus OSM: ODbL 1.0 (© OpenStreetMap-Mitwirkende); übrige Felder: CC0 1.0 | siehe `meta` |
| export/audit_geokodierung_bonn.tsv, export/endenich/audit_geokodierung.tsv, export/endenich/stichprobe_pruefung.tsv | Audit der Geokodierung (Stufe, Methode, Treffer, Konfidenz, Fundstelle, Prüfstatus) | wie oben; Zeilen mit Treffern aus OSM: ODbL 1.0 | siehe Export |
