# Anliegen- und Mängelmelder – Phase 0: Prüfung des Materials (27.10.2026)

**Anlass:** Auftrag vom 27.10.2026, den Mängelmelder der Stadt Bonn (https://anliegen.bonn.de, Open311/GeoReport v2) als Kontext zu den Ratsvorlagen zu prüfen.

**Frage:** Lassen sich Meldungen der Einwohnerschaft nach Kategorie, Zeit und Ortsteil auswerten, ohne Personenbezug, und wo passen sie zur Seite?

**Datenstand:** Abruf 27.10.2026 (rund 75 Anfragen mit Pausen): Monatszahlen 11/2021–10/2026 (je Monat eine Anfrage mit `limit=1`), volle Datensätze 01.05.–26.10.2026 (2.034 Meldungen); Archiv-CSV 2018/2019 von opendata.bonn.de (11.264 Meldungen). Nichts im Repository abgelegt.

## Ergebnis: Material ist nutzbar, aber nur als grobe Zählung
- **Schnittstelle:** Es antwortet `https://anliegen.bonn.de/api/georeport/v2/requests.json` (ohne Anmeldung; Parameter `start_date`, `end_date`, `service_code`, `bbox`, `limit` bis 500, `offset`, `extensions=true`, `meta=true` mit Gesamtzahl). Die im Portal genannte Adresse `…/georeport/v2/services.json` liefert 404, unter `/api/…` 403; `/open311` (Dokumentation) liefert 404; `api.anliegen.bonn.de` war aus der Arbeitsumgebung nicht erreichbar. Die Kategorien kommen ersatzweise aus `/api/jsonapi/taxonomy_term/service_category` (24 Einträge). Plattform: Mark-a-Spot (Drupal), neue Oberfläche (Nuxt).
- **Felder je Meldung:** Nummer (`44312-2026`), Kategorie (`service_code`, `service_name`), Status (`open`/`closed`, dazu „Unbearbeitet“, „In Bearbeitung“, „Erledigt / Beauftragt“, „Nicht Stadtverwaltung“, „Archiv“), Zeitpunkte erstellt/geändert, Statusverlauf mit Texten der Verwaltung, `lat`/`long` (2.034 von 2.034), Adresse mit PLZ (2.034, davon 1.914 = 94 % mit Hausnummer), Beschreibung (2.016), Foto (1.588 = 78 %, öffentlich abrufbar) mit Bildbeschreibung (Alt-Text, 1.588).
- **Zeitliche Abdeckung:** Die Schnittstelle zeigt 9.053 Meldungen ab 23.11.2021 (Nummer `1-2021`). „Seit Ende 2012“ ist nicht belegt: Das Archiv auf opendata.bonn.de reicht von 01.01.2018 bis 01.02.2020; 2012–2017 und 02/2020–11/2021 fehlen in beiden Quellen. Aktuell: letzte Meldung vom 26.10.2026, Statusänderungen vom selben Tag.
- **Umfang je Monat (öffentlich sichtbar):**

  | Zeitraum | Meldungen | je Monat |
  |---|---|---|
  | Archiv 2018 / 2019 / Jan. 2020 | 5.007 / 5.622 / 635 | 345–617 |
  | 2022 (Jan.–Okt.) | 5.146 | 433–663, Okt. 127, ab Nov. 4 |
  | 2023 / 2024 / 2025 | 295 / 230 / 570 | 3–102 |
  | 2026 Mai–Aug. / Sep. / Okt. | 544 / 449 / 1.041 | 110–147, dann Anstieg |

  Die Nummern laufen lückenhaft: Von den vergebenen Nummern sind Mai–Aug. 2026 nur 9–14 % öffentlich, Sep. 36 %, Okt. 99 %. Zwei fehlende Nummern ergaben beim Einzelabruf keinen Treffer. Ältere Meldungen verschwinden offenbar aus der öffentlichen Liste oder wurden nie veröffentlicht; die Monatszahlen spiegeln die Veröffentlichung, nicht die Zahl der Meldungen.
- **Kategorien (Mai–Okt. 2026, 2.034):** Abfall 1.389 (Wilde Müllkippe 1.031, Herrenlose Fahrräder/Schrottfahrzeuge 195, Papierkorb überfüllt 93, Sammelcontainer Altpapier 56, Papierkorb defekt 14); Stadtbild und Grün 342 (Grünüberwuchs Verkehrsraum 252, Spielgeräte 31, Graffiti 27, Bachlauf 12, Parkbank 11, Grünpate werden 9); Straßen und Verkehr 303 (Straßenschild 85, Gully verstopft 57 / klappert 16, Glassplitter 56, Ampel 55, Poller 29, Fahrradständer 4, Sitzbank 1). „Straßenlaterne defekt“ und „E-Scooter falsch abgestellt“ sind angelegt, aber ohne Meldung im Zeitraum. Das Archiv hat 15 Kategorien mit gekürzten Namen (z. B. „Laterne defekt“ 1.778).
- **Passung zu den Themenseiten:** Klima und Umwelt, Strang „Abfall und Sauberkeit“: Müllkippe, Papierkörbe, Container, Graffiti, Glassplitter (rund 1.280); Strang „Bäume, Grün und Natur“: Bachlauf, Grünpate (21). Verkehr und Mobilität: Straßenschild, Ampel, Poller, Gully, Fahrradständer, E-Scooter (rund 250), Schrottfahrräder zu „Rad- und Fußverkehr“ oder „Parken“ (195), Grünüberwuchs Verkehrsraum zu Verkehr oder Grün (252, Entscheidung nötig). Wohnen und Bauen, Schule, Kultur: keine passende Kategorie.
- **Räumlich:** Alle 2.034 Koordinaten liegen in einem der 51 Ortsteile (`data/geo/ortsteile_bonn.geojson`, Punkt im Polygon); alle 51 Ortsteile haben Meldungen (Nordstadt 168, Duisdorf 123, Endenich 119, Beuel-Mitte 92, Kessenich 73 … Hardthöhe 4, Ückesdorf 2, Hoholz 2). Stadtbezirke: Bonn 1.034, Bad Godesberg 398, Beuel 373, Hardtberg 229. Archiv: 11.226 von 11.264 in Bonn. Koordinaten mit 6–9 Nachkommastellen (1.011 mit 9); die Genauigkeit entspricht dem gesetzten Punkt, die Adresse ist daraus abgeleitet.

## Grenzen
- **Datenschutz:** In den Beschreibungen fanden sich 2 E-Mail-Adressen, 6 Treffer für Kfz-Kennzeichen, 29 Straßen mit Hausnummer, Angaben zu Dritten („Mieter“, Alter und Geschlecht gestolperter Personen). Fotos und Bildbeschreibungen zeigen teils Personen. Die Adresse nennt meist eine Hausnummer, oft ein privates Wohnhaus. Die Statustexte der Verwaltung nennen „Eigentümer“ (45). Nach 5.2 dürfen Beschreibung, Bildbeschreibung, Foto, Adresse, Koordinate und Statustexte nicht übernommen werden.
- **Zeitreihen** sind derzeit nicht verlässlich (Veröffentlichungsquote 9–99 % je Monat, Bruch 11/2022, neue Nummerierung 11/2021, Lücke 2020–2021). Vergleiche zwischen Monaten und mit dem Archiv nur nach Klärung mit der Stadt.
- **Stabilität:** Dokumentierte Adressen veraltet (404), Kategorienliste nur über die interne JSON-API der Oberfläche; Schema kann sich mit der Plattform ändern.
- **Archiv-CSV:** nur Nummer, Datum, gekürzte Kategorie, Koordinate; Zeichensatz fehlerhaft (Umlaute teils verloren); andere Kategorien als heute.
- **Lizenz:** CC0 für beide Datensätze (Open311: veröffentlicht 24.04.2014, angepasst 15.06.2026; Archiv: 25.03.2020). Für Fotos der Einwohnerschaft ist eine Lizenz nicht erkennbar.
- **Kein Kausalschluss:** Meldungen sind Hinweise der Einwohnerschaft an die Verwaltung, keine Ratsvorlagen; ein Zusammenhang mit Beschlüssen ist nicht belegt. In Vorlagentiteln seit 2019 kommt „Mängelmelder“ nicht vor (Graffiti 17, Glascontainer 12, Laterne/Straßenbeleuchtung 27, Schrottfahrräder 8).

## Vorschlag Datenumfang
Je Meldung nur **Kategorie (Code), Monat, Ortsteil, Status (offen/erledigt)**; Ortsteil per Punkt im Polygon, Koordinate danach verwerfen; Nummer nur im Audit (TSV). Zellen unter 3 Meldungen als „unter 3“. Kein Link auf einzelne Meldungen, nur auf anliegen.bonn.de.

## Optionen zur Entscheidung
1. **Kontext je Ortsteil:** Zahl der Meldungen der letzten 90 Tage nach drei Gruppen (Abfall, Grün, Verkehr) im Steckbrief „Zahlen zu …“, auf Wunsch je 1.000 Einwohner (Zensus liegt vor). Aufwand klein bis mittel (Schritt in `pipeline/kontext.py`, Audit, Prüfung in `check`). Grenze: Veröffentlichungsquote unklar, daher nur „öffentlich sichtbare Meldungen“.
2. **Hinweis „Meldungen in diesem Gebiet“** in Liste und Vorgang (nur bei genau einem Ortsteil), deutlich getrennt von den Vorlagen („Meldungen der Einwohnerschaft, keine Ratsvorlagen“), mit Link zum Mängelmelder. Aufwand klein. Grenze: lädt zu Kausalschlüssen ein; Text muss das ausschließen.
3. **Eigenes tägliches Archiv der Zählungen** (Kategorie × Ortsteil × Tag, ohne Einzeldaten) im Branch `archiv`, wie bei den Baustellen. Aufwand klein bis mittel. Damit entsteht ab jetzt eine verlässliche Zeitreihe, auch wenn die Stadt ältere Meldungen aus der Liste nimmt.
4. **Zeitreihe auf den Themenseiten** Klima (Abfall und Sauberkeit) und Verkehr. Aufwand mittel. Erst nach Option 3 oder nach Auskunft der Stadt, warum ältere Meldungen fehlen (Anfrage an opendata@bonn.de, auch zur Lücke 2012–2017 und 2020–2021 und zur Lizenz der Fotos).

## Entscheidungen (27.10.2026)
- Tägliches Archiv der Zählungen im Branch `archiv` (Ordner `anliegen/`), danach Zahlen je Ortsteil im Steckbrief, deutlich getrennt von den Vorlagen.
- Gruppen wie die Oberkategorien der Stadt; „Grünüberwuchs Verkehrsraum“ bleibt bei „Stadtbild und Grün“.
- Anfrage an opendata@bonn.de zu fehlenden Meldungen entwerfen (Versand durch den Auftraggeber).
