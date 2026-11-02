# Graue Hintergrundkarte aus OSM-Daten vom eigenen Server: Phase 0 (02.11.2026)

> Phase 0 als Prüfung ohne Änderung im Repository (Agent, 02.11.2026); Prüfskripte, Messwerte und Bilder lagen nur in der Arbeitsumgebung. Entscheidung und Umsetzung stehen am Ende.

## Vorgehen

- Ausschnitt aus dem Protomaps-Build 20261101 (OSM-Stand 01.11.2026) per HTTP-Range mit der Python-Bibliothek `pmtiles` (69 Anfragen, 51 MB, 33 s). Rahmen: Zoom 10–12 Bonn ±0,5°/±0,35°, ab Zoom 13 Bonn ±0,03°.
- **A**: PMTiles-Datei, gezeichnet mit protomaps-leaflet 5.1.0 (Stil „grayscale“, `lang: "de"`); verschlankt ohne die nicht gezeichneten Schichten und Flächenarten (Bild pixelgleich).
- **B**: Dieselben Daten mit MapLibre GL JS 6.15.0 in Chromium ohne Bildschirm gerendert (Blöcke zu 8×8 Kacheln mit Rand), zerlegt, auf 16 Graustufen (4-Bit-PNG) verringert.
- Bytes wie im Bericht `kartenquellen` (412×823, DPR 1,75). Lighthouse 12.8.2 mobil auf Kopien der Seite mit getauschter Kartenebene, Median aus 5 Läufen (A: 3).

## Ergebnisse

| Weg | Start (Zoom 11) | Zoom 14 | Bibliothek (gz) | Umfang auf dem Server |
|---|---|---|---|---|
| OSM heute (CSS-Filter) | 511 KB, 15 Kacheln | 260 KB | – | – (extern) |
| basemap.de Grau, 16 Graustufen | 266 KB (mit dem Verfahren hier: 235) | 165 (143) | – | geschätzt 55 MB bis Zoom 16 |
| A Vektor, protomaps-leaflet | 853 KB | 151 KB | 38 KB | 47 MB (eine Datei, bis Zoom 15) |
| A Vektor, verschlankt | 454 KB | 130 KB | 38 KB | 33 MB |
| A mit MapLibre GL JS (nur Bytes) | 584 KB + 140 KB Schrift | 151 KB + 140 KB | rund 440 KB | 47 MB |
| **B Raster, 16 Graustufen** | **148 KB** | **74 KB** | – | **19 MB, 4.042 Dateien (Zoom 10–16)** |
| B Raster @2x (Stichprobe) | 343 KB | 182 KB | – | geschätzt 45 MB |

Weitere Zoomstufen, B gegenüber OSM: Zoom 12 82/365 KB, 13 114/351, 15 95/348, 16 67/273. Kachelgrößen B: Mittel 4,0 KB (Zoom 16) bis 10,2 KB (Zoom 11), höchstens 12,7 KB.

| Lighthouse mobil | Start LCP | Start SI / TBT | Endenich LCP | Endenich SI / TBT |
|---|---|---|---|---|
| OSM heute | 4,8 s (2,3–5,4) | 1,7 s / 151 ms | 4,5 s (3,2–5,4) | 1,8 s / 664 ms |
| A protomaps-leaflet (verschlankt) | 6,3 s* | 2,4 s / 1.108 ms | 6,0 s* | 2,0 s / 861 ms |
| B Raster | 3,2 s (3,2–4,1) | 1,5 s / 167 ms | 3,0 s (2,9–4,6) | 1,7 s / 459 ms |

\* Canvas zählt nicht als LCP-Element; gemessen wurde ein Textabsatz, der wegen der Zeichenarbeit später erscheint. Die Streuung bei OSM kommt vom fremden Server (Vergleichswert vom Vormittag 3,1/4,2 s).

Bilder (nur in der Arbeitsumgebung): Vergleich OSM/B/A, Stile, Blockgrenze. Beschriftung in beiden Wegen deutsch. A zeichnet scharf, spärlich beschriftet; B (Noto Sans) auf Telefonen so unscharf wie die heutigen 256-px-Kacheln (behebbar mit @2x). „grayscale“ ist dunkler als die heutige Karte (Land #ccc, Wasser #a3a3a3).

## Lizenz und Quellenvermerk

- OSM-Daten ODbL: Vermerk „© OpenStreetMap-Mitwirkende“ mit Link auf openstreetmap.org/copyright.
- A: Die öffentlich abrufbare PMTiles-Datei ist eine aus OSM abgeleitete Datenbank und steht selbst unter ODbL (eigene LICENSE im Kachelordner). B: PNG-Kacheln sind ein „Produced Work“, der Vermerk genügt.
- Protomaps: Code BSD-3, Kartengestaltung CC0, Nennung erbeten; veränderte Fassungen nicht „Protomaps“ nennen. Dazu osmdata.openstreetmap.de (ODbL) und Natural Earth (gemeinfrei).
- Noto Sans (OFL), Symbole MIT: nur für MapLibre bzw. beim Rendern von B.

## Technik

- **CSP**: A mit protomaps-leaflet passt zu `script-src 'self'` (kein Worker, kein `eval`), Daten über `connect-src 'self'`. MapLibre bräuchte einen Modul-Worker von `'self'`, WebGL sowie Schrift und Sprite vom eigenen Server; in Leaflet nur über ein weiteres Plugin. B braucht nur `img-src 'self'`; `tile.openstreetmap.org` bleibt allein für „Farbige Karte“, das `preconnect` entfällt.
- **Server**: netcup (nginx) beantwortet Range-Anfragen mit 206 und gibt PNG `max-age=604800` mit (geprüft); GitHub Pages ebenso Range.
- **Aktualisierung**: nicht im täglichen `pages.yml`, sondern ein eigener Workflow (vierteljährlich oder auf Knopfdruck), der Ausschnitt und Kacheln erzeugt und ablegt; `pages.yml` kopiert sie nur. Dauer B auf 4 Kernen: Abruf 0,5 min, Rendern 11 min (74 Blöcke), Zerlegen 1,5 min, dazu Installation von Playwright/Chromium; Werkzeuge nur über pip und npm. Der Branch `deploy` wird fortgeschrieben, nicht ersetzt: Jede Neuerzeugung fügt der Historie rund 19 MB (B) bzw. 33 MB (A) hinzu.
- **Speicher netcup**: B 19 MB (27 MB belegt), A 33–47 MB, zuzüglich Git-Historie.

## Risiken

- A: Zeichenlast im Hauptthread (TBT +950 ms beim Start); die Karte fällt aus der LCP-Messung; protomaps-leaflet seit Juni 2025 ohne neue Fassung.
- B: Aussehen hängt von Chromium/SwiftShader ab; an Blockgrenzen können Beschriftungen abgeschnitten werden (eine Grenze geprüft, ohne Befund); über Zoom 16 vergrößert (unscharf bei Zoom 17, den die Planebene nutzt); außerhalb der Rahmen keine Kacheln (Leaflet-Option `bounds`, `minZoom` setzen, sonst 404).
- Beide: Kontrast der Marker und violetten Flächen auf dem dunkleren Grau prüfen (WCAG 1.4.11); Farben sind frei änderbar (CC0), bei B beim Rendern.

## Empfehlung

**Weg B**: graue Rasterkacheln aus OSM-Daten einmal je Quartal selbst erzeugen und vom eigenen Server ausliefern.

- Leichteste Variante: beim Start 148 statt 511 KB (−71 %), auch leichter als basemap.de umgewandelt (235–266 KB); bei Zoom 14 74 statt 260 KB.
- Keine zusätzliche Bibliothek, keine Rechenlast im Telefon; LCP mobil im Median 3,2/3,0 s statt 4,8/4,5 s.
- Kein fremder Server beim Start, keine Rückfrage beim BKG nötig, Lizenzen klar (ODbL-Vermerk).

A eignet sich wegen der Rechenlast nicht für Telefone; MapLibre ist für die Seite zu schwer.

## Offene Fragen an den Auftraggeber

1. Farbton: „grayscale“ (dunkler) oder heller angepasst (wie die heutige Karte)?
2. Zoomumfang: bis 16 (19 MB) oder auch 17 für die Planebene (geschätzt 11.000 Kacheln, +35 MB)? Umland bei Zoom 10–12 wie gemessen?
3. @2x-Kacheln für scharfe Schrift (rund 2,4-fache Bytes)?
4. Ablage: Kacheln im Branch `deploy` (Historie wächst) oder getrennt hochladen?
5. Aktualisierung vierteljährlich?
6. „Farbige Karte“ weiter mit OSM?

## Entscheidung und Umsetzung (02.11.2026)

**Entscheidungen des Auftraggebers:**
- Weg B.
- Farbton heller, wie die bisherige graue Ansicht.
- Zoom 10–16 in einfacher Auflösung (ohne @2x).
- Ablage über den Branch `deploy`, Erneuerung vierteljährlich.
- „Farbige Karte“ bleibt OSM.
- basemap.de und die Anfrage an das BKG entfallen.

**Umsetzung:**
- `pipeline/kacheln/`:
  - `rahmen.py` legt den Kachelbereich je Zoomstufe fest: Zoom 10–12 die Region, Zoom 13–14 Bonn mit 0,1° Rand, Zoom 15–16 Bonn mit 0,03° Rand.
  - `ausschnitt.py` holt den Ausschnitt aus dem neuesten Protomaps-Build per HTTP-Range.
  - `rendern.mjs` und `render.html` zeichnen mit MapLibre in Chromium, Stil „light“, Beschriftung deutsch.
  - `zerlegen.py` erzeugt 16 Graustufen nach der bisherigen CSS-Formel `grayscale(1) contrast(.9) brightness(1.08)` und legt `LIZENZ.md` und `stand.json` dazu. Die Prüfung bricht ab, wenn mehr als 25 % der Kacheln einfarbig sind.
- Workflow `kacheln.yml`:
  - Er läuft vierteljährlich (7. Januar, April, Juli, Oktober) und auf Knopfdruck. Danach startet er `pages.yml`.
  - Bei Pull Requests, die die Skripte ändern, läuft er nur zur Prüfung, ohne Ablage.
  - Er ersetzt den Branch `kacheln` jeweils durch einen einzelnen Commit.
  - `pages.yml` kopiert die Kacheln nach `kacheln/` in die Seite und in den Branch `deploy`. Dessen Historie wächst nur, wenn neue Kacheln entstehen, um rund 19 MB.
- Seite:
  - `GrauKacheln` in `site/app.js` fordert nur Kacheln im Kachelbereich an (`KACHEL_RAHMEN`, gleich `rahmen.py`, geprüft in `tests/test_kacheln.py`).
  - Mindestzoom ist 10. Über Zoom 16 werden die Kacheln vergrößert.
  - Außerhalb des Kachelbereichs zeigt die Karte die Landfarbe `#eee`.
  - Fehlen die Kacheln, zeigt die Seite die OSM-Kacheln mit dem bisherigen Graufilter.
  - Vermerk „© OpenStreetMap-Mitwirkende (ODbL), Protomaps“ mit Link. Das `preconnect` zu OSM entfällt.
  - Datenschutzerklärung, Quellen, `LICENSE-DATA.md` und README sind angepasst.
- Live-Prüfung: `live.yml` meldet fehlende Kacheln als Hinweis.

**Prüfung:**
- Erster Lauf lokal: Build 20261102 (OSM-Stand 02.11.2026), 67 Anfragen, 58 MB.
  - Zeichnen 12 min für 85 Blöcke, Zerlegen 1,5 min.
  - Ergebnis: 4.394 Kacheln, 18,6 MB, davon 22 einfarbig.
- Kontrast nach WCAG 1.4.11: Die Kacheln bestehen zu rund 95 % aus den Stufen `#ccc`, `#ddd` und `#eee`, dazu Weiß für Straßen. Die Punktfarben erreichen gegen `#ccc` mindestens 3,3:1 („Ort gesichert“), die Cluster 3,5:1.
- Lighthouse mobil, je 5 Läufe:
  - Start: LCP 4,7 → 3,0 s, übertragen 847 → 473 KB.
  - Endenich: LCP 4,1 → 3,4 s, übertragen 861 → 553 KB (`LADEZEIT.md`).
