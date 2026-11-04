# Weiterleitung der alten Spiegel-Adresse (daimpad.github.io)

Das Repository heißt seit dem 04.11.2026 `daimpad/ratsatlas-bonn` (vorher `daimpad/allris-test`). GitHub leitet
Links auf das Repository weiter, nicht aber die Seite auf GitHub Pages: `daimpad.github.io/allris-test/…` liefert
404, der Spiegel liegt jetzt unter `daimpad.github.io/ratsatlas-bonn/`.

Diese Dateien gehören in ein eigenes Repository **`daimpad/daimpad.github.io`** (Benutzerseite, Branch `main`,
GitHub Pages aus dem Wurzelverzeichnis):

- `404.html`: GitHub Pages zeigt sie für jede Adresse unter `daimpad.github.io`, die es nicht gibt, also auch für
  alle alten Pfade unter `/allris-test/`. Ein kleines Skript leitet auf denselben Pfad unter `/ratsatlas-bonn/` um,
  mit Suchparametern und Anker (Links auf Gebiete und Vorgänge bleiben gültig).
- `index.html`: dieselbe Seite für `daimpad.github.io/` selbst.

Grenzen: GitHub Pages kennt keine Weiterleitungen auf dem Server. Feedreader und Programme, die kein JavaScript
ausführen, erhalten für alte Adressen weiter 404; Abos und Einbindungen über den Spiegel müssen die neue Adresse
eintragen. Die Feeds der Hauptadresse sind nicht betroffen. Kein Repository mit dem alten Namen `allris-test`
anlegen: Dann hebt GitHub die Weiterleitung der Repository-Links auf.
