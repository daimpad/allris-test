# Karte mobil schneller – Schritt 1 (02.11.2026)

**Grundlage:** `phase0/BERICHT.md`, Abschnitt 1. Ziel des Auftraggebers (02.11.2026) ist der Richtwert von 2,5 s für das größte Element (LCP, mobil). Über Schritt 2 (Gebietsdaten teilen) wird nach der Messung entschieden.

## Änderungen
- **Karte vor den Daten:** Karte und Kacheln werden angelegt, bevor die übrigen Startdaten da sind (`createMap`, Ausschnitt ganz Bonn). Ein Gebiet im Link setzt seinen Ausschnitt, sobald die Flächen geladen sind (`fruehAnsicht`).
- **Gebietsdatei früher:** Nennt der Link ein Gebiet, fordert der Start dessen Datei gleich mit an.
- **Daten nachrangig:** Zeitleiste, Baustellen, Kontext und Mängelmelder laden mit niedriger Priorität (Priority Hints) und nicht mehr vorab.
- **Vorverbindung** zu `tile.openstreetmap.org`.
- **Stile zusammengefasst:** Leaflet und MarkerCluster stehen jetzt in einer Datei mit Integritätsprüfung (`vendor/leaflet/karte.min.css`).

## Messung
Lighthouse 12.8.2 mobil (simuliert 150 ms RTT, 1,6 Mbit/s, CPU × 4). Lokale Kopie mit gzip, je 3 Läufe, Median:

| Seite | | Score | FCP | LCP | TBT | Übertragen |
|---|---|---|---|---|---|---|
| Start | vorher | 76 | 1,6 s | 5,8 s | 165 ms | 845 KB |
| Start | nachher | 76 | 1,3 s | 6,0 s | 129 ms | 846 KB |
| Endenich | vorher | 57 | 1,6 s | 6,0 s | 883 ms | 861 KB |
| Endenich | nachher | 62 | 1,3 s | 5,9 s | 666 ms | 860 KB |

**Ergebnis:** Der erste sichtbare Inhalt kommt früher, und die Blockierzeit im Gebiet sinkt um ein Viertel. Das LCP bleibt gleich.

**Warum das LCP gleich bleibt:**
- Das größte Element ist eine OSM-Kachel.
- Beim Start werden 15 Kacheln mit zusammen 515 KB geladen, das sind 61 % aller Daten.
- Bei 1,6 Mbit/s teilen sich die Kacheln die Bandbreite, deshalb ist die letzte erst spät fertig.

**Gegenprobe, nur lokal und nicht übernommen (berichtigt 02.11.2026):**
- Die Gegenprobe mit CARTO Positron hat nicht die echte Karte gemessen. CARTO verlangt inzwischen einen API-Schlüssel. Ohne Schlüssel liefert jede Kachel nur den Platzhalter „API KEY REQUIRED“ mit rund 2 KB.
- Die zuerst genannten Werte (362 KB, LCP 3,8 s bzw. 4,4 s) gelten deshalb nur für diese Platzhalter und sind ungültig.
- Den Vergleich der Kartenquellen mit echten Kacheln enthält `kartenquellen/BERICHT.md` (in diesem Ordner).
- Ein Wechsel der Kartenquelle ist eine Entscheidung des Auftraggebers: Es käme ein weiterer Anbieter mit Nutzungsbedingungen hinzu, und Datenschutzerklärung und Quellenangabe müssten angepasst werden.

## Schritt 1b: Daten nach den Kacheln (02.11.2026)
Entscheidung des Auftraggebers vom 02.11.2026: Zeitleiste, Gebietsflächen und weitere Daten laden erst nach den Kacheln.

**Umsetzung:**
- Der Start lädt zuerst nur `index.json`. Die Datei ist klein, wird vorab angefordert und enthält jetzt den Umriss (`bbox`) jedes Ortsteils und Stadtbezirks.
- Daraus ergibt sich der erste Kartenausschnitt, und die Kacheln laden sofort.
- Glossar, Flächen, Zeitleiste, Baustellen, Kontext, Mängelmelder und die Gebietsdatei aus dem Link folgen, sobald die sichtbaren Kacheln geladen sind. Länger als 2,5 s wartet der Start nicht.
- Vorab angefordert werden nur noch `index.json` und die Schrift.

**Messung** (wie oben, je 3 Läufe):

| Seite | | Score | FCP | LCP | TBT | Übertragen |
|---|---|---|---|---|---|---|
| Start | Schritt 1 | 76 | 1,3 s | 6,0 s | 129 ms | 846 KB |
| Start | Schritt 1b | 92 | 1,3 s | 3,1 s | 115 ms | 846 KB |
| Endenich | Schritt 1 | 62 | 1,3 s | 5,9 s | 666 ms | 860 KB |
| Endenich | Schritt 1b | 69 | 1,3 s | 4,2 s | 676 ms | 861 KB |

**Ergebnis:**
- Die übertragene Menge bleibt gleich, aber die Kacheln teilen die Bandbreite nicht mehr mit den übrigen Daten.
- Der Richtwert von 2,5 s ist auf der Startseite fast erreicht.
- Größter verbleibender Hebel ist die Kartenquelle. Die Bedingungen der Anbieter werden geprüft, bevor etwas umgestellt wird.
- Die Blockierzeit im Gebiet (rund 670 ms) betrifft Schritt 2.
