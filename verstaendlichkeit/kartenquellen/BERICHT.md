# Hintergrundkarte für die graue Standardansicht: Prüfung der Kandidaten (02.11.2026)

> Messskripte, Ergebnisse und Bildschirmfotos (`messung/…`) lagen im Arbeitsordner der Prüfung und sind nicht im Repository. Die Berichtigung in `../LADEZEIT.md` ist erledigt (02.11.2026).

## Wichtigster Befund

CARTO liefert inzwischen (Bedingungen vom 29.09.2026, Schlüsselpflicht) ohne Schlüssel nur Platzhalterkacheln mit der Aufschrift „API KEY REQUIRED“ (je 2,0 KB; Bildschirmfoto `messung/bilder/carto_light.png`). Die lokale Gegenprobe (31 KB, LCP 3,8 s) hat diese Platzhalter gemessen und taugt deshalb nicht als Beleg. Der Satz in `verstaendlichkeit/LADEZEIT.md` (Zeile 30) muss berichtigt werden.

## Messung

Playwright/Chromium, lokale Leaflet-Seite (`site/vendor/leaflet`), 412×823, DPR 1,75, ohne Cache. Grenzen Bonn mit den mobilen Abständen der App ergeben Zoom 11; dazu Zoom 14 um Bonn-Zentrum. Gezählt: übertragener Antwortkörper (`request.sizes()`).

| Kandidat | Start z11: Kacheln/KB | z14: Kacheln/KB | gegenüber OSM (z11) |
|---|---|---|---|
| OSM Standard (heute, mit CSS-Filter grau) | 15 / 511 | 8 / 260 | – |
| CARTO light_all, light_nolabels | 15 / 30 (nur Platzhalter) | – | ohne Schlüssel nicht messbar |
| basemap.de Grau, live vom BKG | 15 / 1.075 | 8 / 678 | +110 % |
| basemap.de Grau, auf 16 Graustufen umgewandelt (lokal berechnet) | 15 / 266 | 8 / 165 | −48 % |
| tile.openstreetmap.de (mit Filter) | 15 / 489 | 8 / 261 | −4 % |
| Stadia Stamen Toner Lite | 15 / 164 | 8 / 150 | −68 % |
| Stadia Alidade Smooth | 15 / 327 | 8 / 218 | −36 % |
| Geobasis NRW DTK schwarz-weiß (zusätzlich) | 15 / 466 | – | −9 %, nur NRW, grob |

basemap.de liefert ungepackte RGBA-PNG; mit 16 Graustufen ist kein Unterschied zu sehen (`messung/bilder/vergleich_16grau.png`). Stadia war nur von localhost aus ohne Schlüssel abrufbar.

## Kandidaten

**CARTO Positron** (CartoDB Inc., New York)
- Bedingungen: Schlüssel Pflicht (§ 8), sonst Wasserzeichen (§ 3.d); nicht-kommerziell kostenlos bis 5 Mio. Kachelabrufe im Monat (§ 12).
- Quellenvermerk: „© OpenStreetMap contributors, © CARTO“, beide verlinkt.
- Datenschutz: IP-Adresse, Referer, User-Agent; Protokolle 30 Tage in den USA (§ 10); CARTO als Auftragsverarbeiter (Vertrag nötig); zertifiziert nach dem EU-US Data Privacy Framework. Zwischenspeichern auf dem eigenen Server verboten.
- Technik: `https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png?key=…`, Zoom 0–20, @2x, CORS `*`.
- Eignung: erst mit Schlüssel messbar; der Schlüssel stünde öffentlich im Repository.

**basemap.de Web Raster Grau** (AdV/ZSGT; Server `sgx.geodatenzentrum.de` im Netz des BKG, Deutschland)
- Bedingungen: kein Schlüssel, „geldleistungsfrei“, laut Capabilities „Es gelten keine Zugriffsbeschränkungen“.
- Lizenz CC BY 4.0; Vermerk „© GeoBasis-DE / BKG (2026) CC BY 4.0“, „BKG“ und „CC BY 4.0“ verlinkt; bei Bearbeitung zusätzlich ein Veränderungshinweis.
- Datenschutz: Protokolle mit IP-Adresse (Art. 6 Abs. 1 lit. e DSGVO, § 5 BSIG); keine Speicherfrist, nichts zu den Kacheln.
- Technik: `…/de_basemapde_web_raster_grau/default/GLOBAL_WEBMERCATOR/{z}/{y}/{x}.png` (Zeile vor Spalte), Zoom 0–19, kein @2x, CORS gibt den Origin zurück, Zwischenspeicher 3 Tage.
- Eignung: rechtlich passend, live aber doppelt so schwer wie heute.

**tile.openstreetmap.de** (FOSSGIS e.V.; Hetzner, laut RIPE Deutschland und Finnland)
- Bedingungen: kein Schlüssel; Websites mit hohem Aufkommen „grundsätzlich nicht“; ein Server, keine Verfügbarkeitszusage. Kacheln CC BY-SA 2.0, Vermerk mit Link „fixthemap“, E-Mail des Betreibers sichtbar.
- Datenschutz: Die Erklärung des Vereins erwähnt den Kachelserver nicht.
- Eignung: farbig und kaum leichter, ohne Nutzen für das Ziel.

**Stadia Maps** (Stadia Maps, Inc., USA)
- Bedingungen: kostenlos nur nicht-kommerziell, 200.000 Credits im Monat (1 je Kachel), keine Überziehung; Konto und Freigabe beider Domains nötig, sonst 401. Neue Bedingungen ab 09.11.2026.
- Quellenvermerk: „© Stadia Maps © Stamen Design © OpenMapTiles © OpenStreetMap“.
- Datenschutz: Protokolle 7–14 Tage; USA über Standardvertragsklauseln (Data Privacy Framework nur für Dienstleister genannt).
- Technik: `https://tiles.stadiamaps.com/tiles/stamen_toner_lite/{z}/{x}/{y}{r}.png`, @2x, CORS `*`.
- Eignung: größte Einsparung bei Live-Abruf; dagegen Drittland, Konto, harte Obergrenze (bei 15–60 Kacheln je Besuch etwa 3.000–13.000 Besuche im Monat), sparsame Beschriftung.

## Empfehlung

**basemap.de Grau als Quelle, die Kacheln für Bonn auf 16 Graustufen umgewandelt vom eigenen Server ausliefern.** Für den Schalter „Farbige Karte“ bleibt OSM.

Gründe:
- Beim Start 245 KB weniger (−48 %), bei Zoom 14 95 KB weniger (−37 %).
- Beim Start und in Gebietsansichten wird kein fremder Server abgefragt; OSM erst nach „Farbige Karte“.
- Amtliche Quelle; CC BY 4.0 erlaubt Vervielfältigung und Bearbeitung; kein Schlüssel, keine Obergrenze, kein Drittland.

Umfang (Schätzung bei 20 KB je Kachel):
- Zoom 10–14 mit Rand: bis rund 950 Kacheln, etwa 19 MB.
- Bis Zoom 16, nur Bonn: rund 2.800 Kacheln, etwa 55 MB.
- Darüber: Kacheln live vom BKG (schwerer) oder eine Zoomgrenze.

Aufwand: ein Pipelineschritt für Abruf (vierteljährlich, wie basemap.de aktualisiert) und Umwandlung; vorher beim BKG (info@basemap.de) nachfragen, ob der Abruf in dieser Menge in Ordnung ist.

Rückfall, falls der Aufwand zu groß ist: Stadia Toner Lite, live abgerufen. Nicht empfohlen: basemap.de live, CARTO ohne Schlüssel, tile.openstreetmap.de.

## Zu ändernde Stellen

- `site/app.js` (`createMap`, Schalter): zwei Ebenen statt CSS-Filter (eigene graue Kacheln, OSM farbig), Quellenvermerk je Ebene, etwa `© <a href="https://www.bkg.bund.de">GeoBasis-DE / BKG</a> (2026) <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>, Graustufen verringert`. Der Filter `.map-gray` in `style.css` entfällt für diese Ebene.
- `site/index.html`:
  - CSP `img-src`: Für eigene Kacheln genügt `'self'`; `https://tile.openstreetmap.org` bleibt. Bei Live-Abruf kommt `https://sgx.geodatenzentrum.de` bzw. `https://tiles.stadiamaps.com` hinzu.
  - `preconnect` zu OSM entfernen bzw. ersetzen.
  - Text im Dialog „Über“ (Zeile 510) anpassen.
- `site/datenschutz.html`, Abschnitt „Kartenkacheln“: OSM nur nach Wahl „Farbige Karte“ (die Wahl wird im Browser gespeichert). Bei Stadia ein eigener Abschnitt mit USA, Standardvertragsklauseln und Speicherfrist.
- Akkordeon „Quellen, Lizenzen und Datenstand“, README, `verstaendlichkeit/LADEZEIT.md` und die Zeile „extern nur OSM-Kacheln“ in CLAUDE.md.

## Offene Fragen

- Lighthouse mit dem gewählten Kandidaten neu messen (Start und Gebiet).
- BKG: Ist der Abruf in Ordnung? Welches Jahr gehört in den Quellenvermerk?
- netcup/nginx: Die Kopfzeilen für statische Dateien werden heute nicht gesetzt (Abschnitt 8). Für Kacheln wäre lange Zwischenspeicherung nötig.
- Besuchszahlen, um die Obergrenzen von Stadia oder CARTO einzuschätzen.
- CARTO: tatsächliche Größe mit Schlüssel; Einschränkung des Schlüssels auf Domains ist ungeklärt.

## Quellen

- CARTO: https://carto.com/legal/basemap-terms/ (Stand 29.09.2026), https://carto.com/basemaps/apikey/, https://carto.com/attributions, https://carto.com/privacy, https://github.com/CartoDB/basemap-styles
- basemap.de: https://basemap.de/web-raster/, https://sgx.geodatenzentrum.de/public/gdz/lizenz/deu/nutzungsbedingungen_basemapde.pdf, https://sgx.geodatenzentrum.de/wmts_basemapde/1.0.0/WMTSCapabilities.xml, https://basemap.de/datenschutz-und-impressum/
- FOSSGIS: https://www.fossgis.de/arbeitsgruppen/osm-server/nutzungsbedingungen/ (Seite für Browser ohne Bildschirm gesperrt; gelesen in der Quelle github.com/fossgis/fossgis-webseite, master), https://www.fossgis.de/datenschutzerklärung/
- Stadia: https://stadiamaps.com/pricing/, https://stadiamaps.com/terms-of-service/, https://stadiamaps.com/privacy/privacy-policy/, https://docs.stadiamaps.com/authentication/, https://docs.stadiamaps.com/attribution/
- OSM: https://operations.osmfoundation.org/policies/tiles/
- Netze: rdap.db.ripe.net (BKG 141.74.0.0/16; Hetzner), rdap.arin.net (Stadia: Linode)
- Messung: `messung/messen.js`, `ergebnis_bonn.tsv`, `ergebnis_z14.tsv` in diesem Ordner
