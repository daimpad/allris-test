# Archiv des Mängelmelders der Stadt Bonn

Dieser Ordner wird täglich vom Workflow `baustellen.yml` im Repository [daimpad/allris-test](https://github.com/daimpad/allris-test) fortgeschrieben (RIS-Karte Bonn, https://ris-bonn.datenatlas.de/).

**Quelle:** Stadt Bonn, Anliegen- und Mängelmelder (https://anliegen.bonn.de), Schnittstelle Open311 GeoReport v2 (`/api/georeport/v2/requests.json`). **Lizenz:** CC0 1.0 (Datensatz auf opendata.bonn.de).

**Warum ein Archiv:** Die Schnittstelle zeigt nicht alle Meldungen; ältere verschwinden aus der öffentlichen Liste (am 27.10.2026 waren für Mai bis August 2026 nur 9–14 % der vergebenen Nummern sichtbar, für Oktober 99 %). Das Archiv hält jede Meldung fest, sobald sie sichtbar ist. Der erste Abruf übernimmt alle bis dahin sichtbaren Meldungen ab November 2021; danach werden täglich die Monate der letzten 120 Tage erneut abgerufen.

**Was gespeichert wird:** je Meldung nur Nummer, Tag der Meldung, Kategorie, Gruppe (Oberkategorie der Stadt), Ortsteil und Stadtbezirk (aus der Koordinate bestimmt), Status. **Nicht** gespeichert werden Beschreibung, Foto, Bildbeschreibung, Adresse, Koordinate und Statustexte: Sie enthalten teils Namen, Kfz-Kennzeichen und Wohnadressen.

**Einordnung:** Meldungen sind Hinweise der Einwohnerschaft an die Verwaltung, keine Ratsvorlagen. Ihre Zahl hängt davon ab, wer meldet und was veröffentlicht wird; sie ist kein Maß für den Zustand eines Gebiets.

| Datei | Inhalt |
|---|---|
| `meldungen.tsv` | je Meldung: `nummer`, `tag`, `kategorie_code`, `kategorie`, `gruppe`, `ortsteil`, `stadtbezirk`, `status` (open/closed), `status_name`, `erstmals_gesehen`, `zuletzt_gesehen` |
| `abrufe.tsv` | je Abruf und Monat: Zahl laut Schnittstelle, erhalten, neu, Status geändert, Fehler |
| `STAND.json` | letzter Abruf, Zahl der Meldungen, Beginn des Archivs |
