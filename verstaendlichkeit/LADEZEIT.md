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

**Gegenprobe, nur lokal und nicht übernommen:**
- Mit einer leichteren grauen Hintergrundkarte (CARTO Positron, mit Beschriftung) sind es beim Start 362 KB statt 846 KB.
- Das LCP sinkt auf der Startseite auf 3,8 s und in Endenich auf 4,4 s (je 2 Läufe).
- Der Richtwert von 2,5 s ist damit noch nicht erreicht. Dafür müssten weitere Daten nach die Kacheln rücken (Zeitleiste, Flächen, Schrift).
- Ein Wechsel der Kartenquelle ist eine Entscheidung des Auftraggebers: Es käme ein weiterer Anbieter mit Nutzungsbedingungen hinzu, und Datenschutzerklärung und Quellenangabe müssten angepasst werden.
