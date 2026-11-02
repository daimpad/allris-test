# Entwurf: Anfrage an das BKG zu basemap.de Web Raster Grau

> **Entfallen** (Entscheidung des Auftraggebers 02.11.2026): Die graue Karte wird aus OSM-Daten selbst erzeugt (`OSM_GRAU.md`); die Anfrage wird nicht versandt.

An: info@basemap.de
Betreff: basemap.de Web Raster Grau – einmaliger Abruf der Kacheln für Bonn und Quellenvermerk

Sehr geehrte Damen und Herren,

im Rahmen des Hackathons „Hack den Stadtrat“ entwickle ich die RIS-Karte Bonn (https://ris-bonn.datenatlas.de/). Die Seite macht Vorlagen aus dem Ratsinformationssystem der Stadt Bonn auf einer Karte zugänglich. Sie ist nicht kommerziell, und ihr Quellcode ist offen (https://github.com/daimpad/allris-test).

Als graue Hintergrundkarte möchte ich basemap.de Web Raster Grau nutzen. Damit die Seite auf Mobilgeräten schneller lädt, möchte ich die Kacheln nicht bei jedem Aufruf von Ihrem Dienst laden. Mein Vorgehen wäre:

- Die Kacheln für das Stadtgebiet Bonn werden einmal abgerufen, Zoomstufen 10 bis 16. Das sind rund 2.800 Kacheln mit zusammen etwa 55 MB. Der Abruf erfolgt langsam, mit Pausen zwischen den Anfragen.
- Die Kacheln werden auf 16 Graustufen umgewandelt, damit die Dateien kleiner werden. Am Bild ändert sich sichtbar nichts.
- Ausgeliefert werden sie vom eigenen Server der Seite. Erneuert würden sie höchstens einmal im Jahr oder nach einer Aktualisierung Ihrerseits.
- Als Quellenvermerk stünde auf der Karte „© GeoBasis-DE / BKG (2026) CC BY 4.0, verändert (Graustufen reduziert)“, mit Links auf das BKG und die Lizenz.

Dazu habe ich vier Fragen:

1. Ist ein einmaliger Abruf in dieser Menge für Sie in Ordnung, oder gibt es einen bevorzugten Weg, etwa einen Download?
2. Welches Jahr gehört in den Quellenvermerk: das Jahr des Abrufs oder das Jahr des Datenstands?
3. Wie oft wird die Karte aktualisiert, und wie oft sollten die Kacheln erneuert werden?
4. Passt der vorgesehene Veränderungshinweis „verändert (Graustufen reduziert)“, oder wünschen Sie eine andere Formulierung?

Vielen Dank für das offene Angebot von basemap.de.

Mit freundlichen Grüßen
Damian Paderta
NOZILLA · contact@nozilla.de
