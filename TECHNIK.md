# RIS-Karte Bonn – Technik

Technische Beschreibung von Pipeline, Seite und Betrieb. Worum es inhaltlich geht, steht in der [README](README.md).

## Aufbau des Repositorys

- `pipeline/` – Abruf, Aufbereitung, Geokodierung (`geocode.py`, `geo.py`, `plans.py`), Akteure (`actors.py`), Themen (`topics.py`), Prozessschritte (`process.py`), Export (`export.py`, `publish.py`, `chat.py`), Prüfung (`check.py`, `verify.py`), Auffindbarkeit (`seo.py`, `gebietsseiten.py`), Baustellen (`baustellen.py`, `kandidaten.py`)
- `site/` – statische Seite: Leaflet mit OSM-Kacheln (`app.js`), Zeitleiste (`timeline.js`), Tour (`tour.js`), Ratsassistent (`chat/`)
- `data/` – Gremien, Ämter, Sitzungen (`raw/`), Flächen und Straßenverzeichnis (`geo/`), Pilot Endenich und Audits (`export/`), Lizenzen je Datei (`LICENSE-DATA.md`)
- `baustellen/` – Berichte der Phasen 0 bis 5 zu Bebauungsplänen und Baustellen, Anfrage an die Stadt
- `prozess/`, `phase0/` – Exploration der Prozessebene und der Datenquellen
- `eval/` – Fragenkatalog und Auswerteskript für den Ratsassistenten
- `tests/` – Unit-Tests (Python) und `tests/js/` (Node)
- `.github/` – Workflows und Issue-Vorlagen; `CLAUDE.md`, `docs/` – Projektprompts

## Pipeline

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pipeline all      # fetch → build → export → check → verify → package
```

| Schritt | Ergebnis |
|---|---|
| `fetch` (`fetch-papers`, `fetch-organizations`, `fetch-meetings`, `fetch-plans`, `fetch-lite`, `fetch-streets`) | Rohdaten in `data/raw/`, Geltungsbereiche in `data/geo/bebauungsplaene_bonn.geojson`, Änderungsprotokoll der Pläne; Abrufzeitpunkte in `STAND.json` |
| `gazetteer` | `data/geo/strassen_bonn.json`: Straßenverzeichnis aus OSM mit Ortsteilen je Straße |
| `build` | `data/build/allris.sqlite`: Vorlage, Beratung, Sitzung, Tagesordnungspunkt, Organisation, Vorlagenbeziehung, Ort, Ortsbezug, Einreichende, Zuständigkeit, Plannummer |
| `export` | `data/export/endenich/` (Pilot, im Repository) und `data/export/bonn/` (je Ortsteil, Bezirk und Jahr, `zeit.json`, `prozesse.json`, `suche.json`, `plaene.json`, Feeds, Kalender, GeoJSON, DCAT, Daten des Assistenten); Audits als TSV |
| `check`, `verify` | Kennzahlen, Abgleich Stufe B gegen A, Datenschutzprüfung (bricht bei Hausnummern ab); Stichprobe gegen die OParl-API |
| `package` | `data/export/allris-bonn-export.zip` mit `LIESMICH.txt` |
| `seo` | `robots.txt`, `sitemap.xml`, statische Seiten je Gebiet, absolute Adressen aus `SITE_URL` |
| `baustellen` | tägliches Archiv der Baustellen (Branch `archiv`) |
| `kandidaten`, `baustellen-seite` | Audit Beschluss ↔ Baustelle mit Stichprobe; `data/export/bonn/baustellen.json` für die Seite |

Lokale Vorschau:

```bash
mkdir -p _site/data/geo && cp -r site/. _site/ && cp -r data/export _site/data/ \
  && cp data/LICENSE-DATA.md _site/data/ && cp data/geo/*.geojson _site/data/geo/
python3 -m http.server -d _site 8000
```

Tests: `.venv/bin/python -m unittest discover tests` und `node --test "tests/js/**/*.test.mjs"`.

## Geokodierung

| Stufe | Methode | Konfidenz |
|---|---|---|
| A | `location` aus der OParl-API (Punkt der Stadt; Ortsteil per Point-in-Polygon) | hoch |
| B | Straßen-, Ortsteil- und Bezirksnamen im Titel; Straßenpunkt = Mitte des längsten Abschnitts je Ortsteil (OSM); Eingrenzung mehrdeutiger Straßen über genannten Ortsteil oder befasste Bezirksvertretung; Folgevorlagen erben den Ortsbezug (`vererbt`, höchstens „mittel“) | mittel, bei Mehrdeutigkeit niedrig |
| B3 | Plannummern im Titel (Listen, Zusätze wie „Teil A“), abgeglichen mit den Geltungsbereichen: eindeutig, Grundnummer, mehrdeutig, nicht im Datensatz; Ortsteile über Überschneidung ab 5 %; ein eindeutiger Plan hat Vorrang vor Straßen- und Ortsnamen | hoch bei eindeutigem Plan, sonst niedrig |
| C | Volltext mit Sprachmodell | zurückgestellt (Lizenz der PDFs) |

Jeder Ortsbezug trägt `stage`, `method`, `confidence`, `evidence` und `source_object`. Audits: `data/export/audit_geokodierung_bonn.tsv`, `data/export/audit_bebauungsplaene.tsv`; Stichprobe `data/export/endenich/stichprobe_pruefung.tsv` mit KI-Vorprüfung `vorpruefung_verortung.tsv`.

## Prozessebene und Zeitleiste

- Schritte mit Evidenzstatus (`belegt`, `abgeleitet`, `soll`, `nicht_öffentlich`, `unklar`) und Stand; Sitzungsdaten auf den Kalendertag in Bonn umgerechnet. Audit: `data/export/endenich/audit_prozess.tsv`; Bericht: `prozess/BERICHT_phase0.md`.
- Planchronik: Register je Plannummer (`plaene.json`) mit Verfahrensschritten nach BauGB aus dem Titel (§ 2 Abs. 1, § 3 Abs. 1, § 3 Abs. 2, § 10 Abs. 1; Inkrafttreten § 10 Abs. 3 aus den Plandaten).
- Zeitleiste: Monatsaggregate je Gebiet (`zeit.json`), feinere Stufen aus den geladenen Vorlagen; Spur der Baustellen mit unscharfen Enden. Audit der Datumsangaben: `data/export/endenich/audit_zeit.tsv`; Abgleich mit der OParl-API: `data/export/verifikation_zeit.tsv`.

## Soll-Modell der Prozessebene

- `data/soll/`: Verfahrensmodell (13 Verfahren mit Schritten, Bahnen, Fristen, Belegen) und Zuständigkeitsordnung (18 Ausschüsse, 333 Rechte) aus „Bonn entscheidet“ (anster2025/bonn-entscheidet, Commit `26641f7`, MIT) als feste Kopie; `ergaenzungen.json` mit eigenen Schritten (Wege in Ausschuss und Bezirksvertretung, Kleine Anfrage, Anhörung der Bezirksvertretung) und drei Korrekturen, jeweils mit Beleg; `QUELLE.md`.
- `pipeline/soll.py` (`python -m pipeline soll`): ordnet jeden Vorgang (Stammnummer) einem Verfahren zu (Regeln aus `einordnung.py` übernommen), gleicht die beratenden Gremienarten mit dem Soll ab und schreibt `data/export/audit_soll.tsv` (ohne Titel). Prüfung vor der Übernahme: `soll/phase0/BERICHT.md`; Stand: `soll/PHASE1.md`, `soll/PHASE2.md`.
- Anzeige: `export` schreibt je Vorlage das Feld `soll` (Verfahren, Sicherheit, Grund, Passung, Gremienarten Ist und Abweichung) und `data/export/bonn/soll.json` (Verfahren mit Schritten und Rechtsgrundlagen als Links, Bahnen, Fristen, Zuständigkeit, Zuständigkeitsordnung je Ausschuss). Links nach `recht.py` aus „Bonn entscheidet“. Die Seite lädt `soll.json` beim ersten geöffneten Vorgang; der Assistent liefert `soll_nach_regelwerk` in `hole_prozesslinie`.
- Mitwirkung: die 14 Einflussregeln des Modells (Anrede „Sie“ über `ergaenzungen.json`, Abschnitt `anrede`, mit Prüfung des alten Wortlauts) stehen in `soll.json` unter `mitwirken`; `site/mitwirken.js` wertet sie im Browser aus (Status, Abschluss, Termin, Ebene, Ziel eines Bürgerantrags aus Stand, Beratungen und `zeit.json`) und wird von `app.js` (dynamischer Import) und `chat/tools.js` genutzt. Bericht: `soll/PHASE3.md`.
- Zuordnung und Abgleich zählen nur den Hauptweg eines Vorgangs: ohne spätere Anfragen, Einwohnerfragen und Mitteilungen anderer Art; Stellungnahmen und Änderungsanträge gehören zur vorausgehenden Vorlage.
- Passung je Vorgang: `passt`, `weicht ab` (Befund), `nur Beirat` (Beiräte bildet das Modell nicht ab), `ohne Beratung`, `ohne Soll`. Stichprobe zur Prüfung von Hand: `data/export/soll/stichprobe_soll.tsv` (`soll/phase4/stichprobe.mjs`, wird nie überschrieben) mit KI-Vorprüfung `vorpruefung_soll.tsv`; Bericht `soll/PHASE4.md`.

## Baustellen

- `baustellen.yml` ruft täglich um 05:23 UTC die Feeds 14403, 14698 und 14755 ab (bis zu 10 Versuche, Prüfung gegen `numberMatched`) und schreibt in den Branch `archiv`: `baustellen.json` (Zustand je Baustelle), `protokoll.tsv` (neu, geändert, entfallen), Momentaufnahmen bei Änderungen, `STAND.json`. Eine Baustelle gilt nur bei vollständigem Abruf aller Feeds als entfallen.
- `kandidaten`: Kriterien räumlich (≤ 150 m), zeitlich, gleiche Straße, Amt 66/61-3 oder Thema Verkehr, Bau-Stichwort passend zur Maßnahme; „hoch“ nur für Baubeschlüsse (Beschlussvorlage, Dringlichkeits- oder Eilentscheidung), sonst höchstens „mittel“; Konfidenz hoch, mittel, niedrig, „fremd“ für andere Träger. Audit `data/export/baustellen_kandidaten.tsv`, Stichprobe `data/export/baustellen/stichprobe_kandidaten.tsv` (wird nie überschrieben).
- `baustellen-seite`: `baustellen.json` für die Seite aus dem Archiv, sonst aus den Feeds; Adressen ohne Hausnummer; nur Kandidaten mit Konfidenz hoch.

## Seite

- Statisch, ohne Server-Logik. Strenge Content-Security-Policy; extern nur Kacheln von `tile.openstreetmap.org` und die Anbieter des Assistenten. Leaflet 1.9.4 (BSD-2-Clause), Leaflet.markercluster 1.5.3 (MIT) in `site/vendor/`, Schrift Inter (OFL 1.1) in `site/fonts/`, jeweils mit Lizenzdatei und SRI.
- URL-Zustand: `?gebiet=ortsteil:endenich&von=2025-10-18&bis=2026-10-18&zoom=Quartal&achse=vorlage&thema=verkehr&partei=SPD&suche=bonn&farbe=thema&plaene=1&plan=6122-1&baustellen=1&baustelle=9640#191010`.
- Barrierefreiheit: WCAG 2.1 AA, geprüft mit axe-core auf Desktop und Mobil; Listen als Zugang ohne Maus zu Karte, Plänen und Baustellen.
- Auffindbarkeit: Favicons, Web-Manifest, canonical, Open Graph, schema.org, `noscript`, `404.html`, `robots.txt`, `sitemap.xml`, statische Seiten je Gebiet (`gebiete/`).

## Ratsassistent

Zehn Werkzeuge in `site/chat/tools.js` über die statischen Exporte (`suche_vorlagen`, `hole_vorlage`, `hole_prozesslinie`, `suche_ort`, `liste_sitzungen`, `hole_gremium_oder_amt`, `erklaere_begriff`, `suche_bebauungsplan`, `suche_baustellen`, `datenstand`). Adapter für Anthropic, Mistral, OpenRouter und lokale Modelle (`providers.js`), Chat-Kern (`core.js`), Schlüssel nur im Arbeitsspeicher oder auf Wunsch im Sitzungsspeicher (`keys.js`). Systemprompt mit Änderungsvermerk: `site/chat/systemprompt.md`. Auswertung: `eval/run.mjs`, `eval/fragen.json`.

## Offene Daten

- `data/export/bonn/vorlagen.geojson` – ein Punkt je Vorlage und Ort mit Stufe, Methode, Konfidenz, Fundstelle, OParl-ID
- `data/export/bonn/plaene.json`, `data/export/bonn/baustellen.json`
- `data/export/bonn/dcat.jsonld` – DCAT-AP mit Distributionen und Lizenzen
- `data/export/bonn/termine.ics`, `data/export/bonn/feeds/`
- Datenpaket mit allen Exporten, Audits, Protokollen und Berichten (Inhalt in `LIESMICH.txt`)

## Betrieb

- `pages.yml`: täglich 04:17 UTC und bei jedem Push auf `main`; Abruf mit Rückfall auf den zwischengespeicherten Stand, Bebauungspläne montags und auf Knopfdruck (bis zu 15 Minuten); veröffentlicht auf GitHub Pages und im Branch `deploy`.
- `live.yml`: prüft nach jeder Veröffentlichung und täglich 06:41 UTC Hauptadresse und Spiegel; Fehler meldet GitHub per E-Mail.
- `tests.yml`: Unit-Tests, Syntaxprüfung, Node-Tests bei Pull Requests.
- Eigener Server (Plesk): Subdomain mit Let's-Encrypt-Zertifikat; „Git“ mit `https://github.com/daimpad/allris-test.git`, Branch `deploy`, automatische Bereitstellung; Webhook-URL in GitHub unter Settings → Webhooks (push). `SITE_URL` (Standard `https://ris-bonn.datenatlas.de/`) bestimmt die absoluten Adressen.
