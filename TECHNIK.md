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

Die Verortung ist regelbasiert. Sie nutzt reguläre Ausdrücke und Geometrie (shapely), kein Sprachmodell, und arbeitet nur mit Titel und Metadaten der Vorlagen. Sie läuft im Schritt `build` (`pipeline/build.py`) und schreibt die Tabellen `location` (Orte) und `paper_location` (Ortsbezug je Vorlage) in die SQLite-Datenbank. `export` gibt die Ergebnisse an Seite, GeoJSON und Audits weiter.

| Stufe | Methode | Konfidenz |
|---|---|---|
| A | `location` aus der OParl-API (Punkt der Stadt; Ortsteil per Point-in-Polygon) | hoch |
| B | Straßen-, Ortsteil- und Bezirksnamen im Titel; Straßenpunkt = Mitte des längsten Abschnitts je Ortsteil (OSM); Eingrenzung mehrdeutiger Straßen über genannten Ortsteil oder befasste Bezirksvertretung; Folgevorlagen erben den Ortsbezug (`vererbt`, höchstens „mittel“) | mittel, bei Mehrdeutigkeit niedrig |
| B3 | Plannummern im Titel (Listen, Zusätze wie „Teil A“), abgeglichen mit den Geltungsbereichen: eindeutig, Grundnummer, mehrdeutig, nicht im Datensatz; Ortsteile über Überschneidung ab 5 %; ein eindeutiger Plan hat Vorrang vor Straßen- und Ortsnamen | hoch bei eindeutigem Plan, sonst niedrig |
| C | Volltext mit Sprachmodell | zurückgestellt (Lizenz der PDFs) |

### Grundlagen

- **Flächen:** 51 Ortsteile und 4 Stadtbezirke der Stadt Bonn (CC0) in `data/geo/`.
  - `pipeline/geo.py` hält sie in einem räumlichen Index (STRtree).
  - Er beantwortet zwei Fragen: In welchem Ortsteil liegt ein Punkt (Point-in-Polygon)? Welche Ortsteile schneidet eine Fläche, und zu welchem Anteil?
- **Straßenverzeichnis** (`python -m pipeline gazetteer` → `data/geo/strassen_bonn.json`, `Gazetteer._streets` in `pipeline/geocode.py`), derzeit 2.376 Straßennamen:
  1. Abruf aller benannten OSM-Ways mit `highway`-Tag im Stadtgebiet, in Kacheln über Overpass. Haltestellen, geplante, abgerissene und aufgegebene Wege bleiben außen vor (`SKIP_HIGHWAY`).
  2. Abschnitte gleichen Namens werden zusammengeführt. Abschnitte, die mehr als 150 m auseinanderliegen, gelten als getrennte Lagen (`component`). Derzeit haben 23 Namen mehr als eine Lage, zum Beispiel „Kapellenstraße“.
  3. Jede Lage wird mit den Ortsteilen verschnitten, in einer flächentreuen Projektion in Metern. Ein Ortsteil zählt, wenn mindestens 150 m oder 15 % der Straße darin liegen.
  4. Je Straße und Ortsteil gilt als Punkt die Mitte des längsten Abschnitts. Ein Straßenpunkt steht damit für die Straße im Ortsteil, nicht für ein Gebäude.
  5. Straßennamen, die nur in den OParl-Orten der Stadt vorkommen, werden zur Laufzeit ergänzt (`_add_points`, Quelle `oparl-bonn`).
  6. **Kreuzungen** (`_crossings`): Für je zwei Straßen, deren Linien sich berühren, speichert das Verzeichnis die Ortsteile der Berührungspunkte (derzeit 4.532 Paare, Schlüssel `kreuzungen`).
- **Namensvarianten der Ortsteile** (`ORTSTEIL_ALIASES`):
  - Teilnamen zusammengesetzter Ortsteile, etwa „Lessenich“ und „Meßdorf“ für „Lessenich/Meßdorf“.
  - Adjektive auf „-er“ wie „Endenicher“.
  - Für die Bezirke Bad Godesberg, Beuel und Hardtberg die Namen samt Adjektiv (`BEZIRKE`).
  - Ortsteil- und Bezirksnamen sind als Straßennamen gesperrt, damit „Beuel“ nicht als Straße gilt.

### Ablauf je Vorlage

**Stufe A – Ort der Stadt** (`pipeline/build.py`, Schleife über `location`)
- Enthält die Vorlage in der OParl-API ein Feld `location` mit Punktgeometrie, wird die Koordinate übernommen, Konfidenz „hoch“, Methode `oparl_location`.
- Der Ortsteil ergibt sich per Point-in-Polygon.
- Orte ohne Koordinate werden mit Konfidenz „niedrig“ gespeichert und erscheinen nicht auf der Karte.
- Straße und Beschreibung werden wörtlich übernommen. `check` bricht ab, sobald darin eine Ziffer außer einer Postleitzahl steht.

**Stufe B – Namen im Titel** (`Gazetteer.locate` in `pipeline/geocode.py`)
1. **Straßen:**
   - Ein regulärer Ausdruck enthält alle Straßennamen ab vier Zeichen, die längsten zuerst. So gewinnt „Marienforster Steinweg“ vor „Steinweg“.
   - Es gelten Wortgrenzen, und „Straße“ wird auch als „Strasse“ oder „Str.“ erkannt.
   - Gefundene Stellen werden im Titel ausgeblendet, damit ein Ortsteilname in einem Straßennamen nicht doppelt zählt.
2. **Ortsteile:** im verbleibenden Text, mit den Varianten oben. Auch nach einem Bindestrich wird gesucht, etwa „Bonn-Endenich“.
3. **Stadtbezirke:** ebenso im verbleibenden Text.
4. **Eingrenzung einer Straße** (`_resolve_street`), in dieser Reihenfolge:

   | Lage | Methode | Konfidenz |
   |---|---|---|
   | Der Titel nennt einen Ortsteil, in dem die Straße liegt | `strasse+ortsteil` | mittel |
   | Der Titel nennt eine zweite Straße, die diese kreuzt; es gilt der Ortsteil der Kreuzung (R1, seit 20.10.2026) | `strasse+kreuzung` | mittel |
   | Mehrere getrennte Lagen; der genannte Bezirk oder der Bezirk der befassten Bezirksvertretung lässt genau eine übrig | `strasse+bezirk` | mittel |
   | Mehrere Lagen, keine Eingrenzung möglich | `strasse_mehrdeutig` | niedrig |
   | Eine Lage, die außerhalb des Bezirks der befassten Bezirksvertretung oder des genannten Bezirks liegt | `strasse` | niedrig |
   | Eine Lage ohne Widerspruch | `strasse` | mittel |

   Namen, die im Titel oft keine Straße meinen („Rheinufer“, „Markt“, „Kirchberg“, „Wasserland“), erhalten stets „niedrig“.
5. **Ortsteile ohne Straßentreffer:** Ein genannter Ortsteil, für den keine Straße gefunden wurde, wird als Fläche mit innerem Punkt eingetragen.
   - Methode `ortsteil_name` oder `ortsteil_adjektiv`, Konfidenz „mittel“.
   - Die Konfidenz sinkt auf „niedrig“, wenn der Ortsteil nicht im Bezirk der befassten Bezirksvertretung liegt.
6. **Stadtbezirke ohne Treffer darunter:** Ein Bezirk, für den kein Ortsteil oder keine Straße gefunden wurde, wird eingetragen. Methode `stadtbezirk_name` mit „mittel“, `stadtbezirk_adjektiv` mit „niedrig“.

**B3 – Bebauungspläne** (`plan_numbers` in `pipeline/geocode.py`, `pipeline/plans.py`)
- **Erkennung im Titel:**
  - Eine Plannummer zählt nur hinter einem Stichwort: „Bebauungsplan“ (auch mit Tippfehlern), „B-Plan“, „Bauleitplan“, „Satzung“ oder „Vorhaben- und Erschließungsplan“.
  - Erkannt werden auch Listen („6322-2 und 6322-3“) und Zusätze („a“, „II“, „Teil A“).
  - Flurstückskennungen werden vorher entfernt.
- **Abgleich mit den 1.128 Geltungsbereichen** (`Plans.classify`):

  | Treffer | Bedeutung | Konfidenz |
  |---|---|---|
  | eindeutig | genau ein Plan | hoch |
  | grundnummer | der Titel nennt einen Zusatz, der Datensatz nur die Grundnummer | niedrig |
  | mehrdeutig | mehrere Pläne | niedrig |
  | nicht im Datensatz | kein rechtskräftiger Plan, etwa weil er noch im Verfahren ist | keine Fläche |

- **Ortsteile:** Die Planfläche wird mit den Ortsteilen verschnitten. Ein Ortsteil zählt ab 5 % der Planfläche, sonst der mit dem größten Anteil. Der Punkt ist ein innerer Punkt der Schnittfläche.
- **Vorrang:** Bei einem eindeutigen Plan entfallen die übrigen Ortsbezüge der Stufe B derselben Vorlage, weil der Geltungsbereich genauer ist als ein Straßenname im Titel.

**Vererbung** (`_inherited` in `pipeline/build.py`)
- Eine Vorlage ohne eigenen Ortsbezug, zum Beispiel eine Stellungnahme oder ein Änderungsantrag, übernimmt die Ortsbezüge ihrer übergeordneten Vorlage (`superordinatedPaper`).
- Methode `vererbt`, Stufe B, Konfidenz höchstens „mittel“.
- Als Beleg dient die Drucksachennummer der übergeordneten Vorlage.

**Zusammenführung** (`_locations` in `pipeline/export.py`)
- Belegt Stufe A einen Ortsteil, entfallen dort die Treffer der Stufe B. Bebauungspläne bleiben stehen.
- Vorlagen ganz ohne Ortsbezug stehen unter „stadtweit / ohne Ortsbezug“.

### Jeder Ortsbezug trägt

- `stage` (A, B), `method` (siehe oben), `confidence` (hoch, mittel, niedrig);
- `evidence`: die Fundstelle im Titel bzw. die Beschreibung der Stadt;
- `source_object`: die OParl-ID der Vorlage oder des Orts;
- `source` des Orts: `oparl-bonn`, `osm`, `geo-bonn` oder `bplan-bonn`; daraus folgt die Lizenzzeile.

### Kennzahlen (Stand 19.10.2026)

| Kennzahl | Wert |
|---|---|
| Vorlagen | 24.915 |
| mit Ortsbezug insgesamt | 10.781 (43,3 %) |
| Stufe A | 1.816 (7,3 %) |
| Stufe B einschließlich B3 | 10.409 (41,8 %) |
| B3 mit eindeutigem Plan | 321 von 556 Vorlagen mit Plannummer |
| vererbt | 159 |

Die Zahlen gibt `python -m pipeline check` aus.

### Prüfung

- **Gegenprobe:**
  - `check` vergleicht Stufe B mit Stufe A bei den 1.816 Vorlagen mit Ort der Stadt.
  - Für 87,1 % findet Stufe B ebenfalls einen Ortsteil.
  - Bei Straßen aus OSM stimmt der Ortsteil in 96,0 % der Fälle.
  - Das Audit vermerkt je Treffer „bestätigt durch Stufe A“ oder „abweichend von Stufe A“.
- **Prüfprotokolle:**
  - `data/export/audit_geokodierung_bonn.tsv` enthält eine Zeile je Ortsbezug mit Drucksache, Stufe, Methode, Treffer, Ortsteil, Konfidenz, Fundstelle, Quellobjekt und Prüfstatus.
  - `data/export/audit_bebauungsplaene.tsv` enthält eine Zeile je Plannummer mit der Trefferklasse.
- **Stichprobe:** `data/export/endenich/stichprobe_pruefung.tsv` umfasst 50 Vorlagen und wird nie überschrieben. Die KI-Vorprüfung `vorpruefung_verortung.tsv` ist gekennzeichnet und ersetzt die Prüfung von Hand nicht. Prüfung von Hand am 20.10.2026: 41 richtig, 4 teilweise, 5 falsch; Fehlerarten und mögliche Regeln in `verortung/PRUEFUNG.md`.
- **Datenschutz:**
  - Es gibt keine Hausnummern und keine Wohnadressen.
  - Bürgeranträge erscheinen nur auf Straßen- oder Ortsteilebene.
  - `check` bricht die Pipeline ab, wenn eine Ortsangabe der Stadt eine Hausnummer enthält.
- **Tests:**
  - `tests/test_geocode.py`: Abkürzungen, längster Name, Eingrenzung mehrdeutiger Straßen, Ortsteilvarianten, Konfidenz bei abweichendem Bezirk, Plannummern.
  - `tests/test_plans.py`: Einstufung, Teilpläne, Flächenanteile je Ortsteil.

### Ausgabe

- `export` schreibt die Ortsbezüge je Vorlage in die Gebietsdateien unter `data/export/bonn/`.
- Die Datei `data/export/bonn/vorlagen.geojson` (`write_geojson` in `pipeline/publish.py`) enthält einen Punkt je Vorlage und Ort, mit Stufe, Methode, Konfidenz, Fundstelle, Quelle und Link ins Ratsinformationssystem.
- Lizenzen: Orte aus OSM unter ODbL 1.0, Stand und Ergebnisse aus OParl-Lite unter CC BY 4.0, übrige Felder CC0 1.0.

### Grenzen

- Orte, die nur im Dokument stehen, fehlen, weil Stufe C zurückgestellt ist.
- Ein Straßenpunkt steht für die ganze Straße im Ortsteil.
- Ein Name im Titel kann etwas anderes meinen als einen Ort, etwa eine Einrichtung, die nach einer Straße benannt ist. Solche Fälle sollen die Stichprobe und die Rückmeldung „Verortung falsch?“ aufdecken.

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
