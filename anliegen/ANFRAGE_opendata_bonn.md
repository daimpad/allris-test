# Entwurf: Anfrage an das Open-Data-Team der Stadt Bonn

An: opendata@bonn.de
Betreff: Mängelmelder (Open311), Baustellen und Wahldaten – Fragen zu Umfang, Historie und Erreichbarkeit

Sehr geehrte Damen und Herren,

für die RIS-Karte Bonn (https://ris-bonn.datenatlas.de/) möchte ich Zahlen aus dem Anliegen- und Mängelmelder je Ortsteil zeigen, getrennt von den Ratsvorlagen und nur nach Kategorie, Monat und Status. Bei der Prüfung der Schnittstelle sind mir einige Fragen aufgefallen:

1. **Sichtbare Meldungen.** Die Schnittstelle `https://anliegen.bonn.de/api/georeport/v2/requests.json` zeigt für Mai bis August 2026 nur 9–14 % der vergebenen Nummern, für Oktober 2026 dagegen 99 % (Abruf am 27.10.2026). Werden Meldungen nach einer bestimmten Zeit oder mit dem Status „Archiv“ aus der öffentlichen Liste genommen? Gibt es eine Abfrage, die alle Meldungen enthält?
2. **Historie.** Das Archiv auf opendata.bonn.de reicht von Januar 2018 bis Februar 2020, die Schnittstelle beginnt mit der Nummer 1-2021 im November 2021. Gibt es Daten für 2012 bis 2017 und für Februar 2020 bis November 2021?
3. **Dokumentation.** Die im Portal genannten Adressen `…/georeport/v2/services.json` und `/open311` liefern derzeit Fehler (404 bzw. 403). Ist eine aktuelle Beschreibung der Schnittstelle und der Kategorien geplant?
4. **Erreichbarkeit weiterer Dienste.** Seit dem 22.10.2026 antworten die GeoJSON-Schnittstellen unter stadtplan.bonn.de nicht mehr (z. B. Baustellen `?Thema=14403`, Wahl- und Stimmbezirke `?OD=4873` und `?OD=4874`; Zeitüberschreitung oder leere Antwort `{}`), ebenso die Seite mit den offenen Wahldaten unter wahlen.bonn.de (Kommunalwahl 2025). Ist eine Umstellung geplant, oder gibt es eine andere Bezugsquelle für diese Daten?
5. **Fotos.** Unter welcher Lizenz stehen die Fotos der Meldungen? Die RIS-Karte übernimmt sie nicht, die Frage betrifft die Angabe im Datensatz.

Für Rückfragen stehe ich gern zur Verfügung. Vielen Dank für die offenen Daten der Stadt Bonn.

Mit freundlichen Grüßen
Damian Paderta
NOZILLA · contact@nozilla.de
