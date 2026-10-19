# Phase 0 – Bebauungspläne und Baustellen: Prüfbericht

Stand: 19.10.2026, Abrufe 08:40–08:53 UTC. Im Repository wurde nichts geändert. Skripte, Rohdaten und Tabellen liegen unter
`baustellen/phase0/` (`scripts/`, `out/`; die Rohabrufe liegen nicht im Repository).
Grundlage für die Vorlagen ist `data/build/allris.sqlite` (24.915 Vorlagen, OParl-Abruf vom 18.10.2026, 12:13 UTC; Bebauungspläne vom 18.10.2026, 18:31 UTC).

## 1. Datensätze

| | Bebauungspläne | Baustellen tagesaktuell | Baustellen geplant (30 Tage / 1 Jahr) |
|---|---|---|---|
| Ressource | `https://stadtplan.bonn.de/geojson?Thema=20074` | `…/geojson?Thema=14403` | `…/geojson?Thema=14755` (30 Tage), `…?Thema=14698` (1 Jahr) |
| Herkunft der URL | CKAN `package_show?id=lage-der-bebauungspläne` | OGD-Cockpit „API Beschreibungen“; opengeodata-bonn.de | opengeodata-bonn.de (Kopie der Portalressourcen, Stand 20.06.2018) |
| Eintrag auf opendata.bonn.de | vorhanden | **nicht mehr vorhanden** | **nicht mehr vorhanden** |
| Format, Geometrie | GeoJSON (EPSG:4326), Fläche: 869 MultiPolygon, 259 Polygon | GeoJSON, Punkt | GeoJSON, Punkt |
| Felder | `bplan_name`, `inkraft_seit`, `pdf_link`, `begruendung_link` | `baustelle_id`, `bezeichnung`, `stadtbezirk`, `stadtbezirk_bez`, `adresse`, `von`, `bis` (TT.MM.JJJJ), `traeger`, `massnahme`, `sperrung` | wie tagesaktuell |
| Stabile ID | nur `bplan_name` (1.127 verschiedene bei 1.128 Objekten; 7219-15 zweimal) | `baustelle_id` (ganzzahlig) | `baustelle_id` |
| Objekte am 19.10.2026 | 1.128 (`totalFeatures`) | 7 | 48 / 48 |
| Aktualisierung laut Quelle | täglich (CKAN, open.nrw `DAILY`, OGD-Cockpit) | täglich (OGD-Cockpit) | „laufend fortgeschrieben“ |
| Lizenz laut Quelle | CC0 (CKAN `license_title`, OGD-Cockpit) | CC0 (OGD-Cockpit, Stand 03.02.2020) | CC0 (opengeodata-bonn.de, Stand 2018) |
| Lizenz auf open.nrw | „Andere geschlossene Lizenz“, `non_open: true` | kein Eintrag (404) | kein Eintrag (404) |
| Bauherr/Träger | – | ja (`traeger`) | ja (`traeger`) |
| Historische Stände | nein; aufgehobene Pläne entfallen | nein | nein |

Abrufwege der Metadaten: `https://opendata.bonn.de/api/3/action/package_show?id=…`, `…/package_list` (287 Datensätze), Portalsuche `https://opendata.bonn.de/search/type/dataset?query=baustellen` (ein Treffer: Fahrradmessstellen), `https://open.nrw/api/3/action/package_show?id=…` sowie `package_search` mit `fq=organization:bonn` (284 Datensätze, keiner zu Baustellen), `https://ogdcockpit.bonn.de/Baustellen_tagesaktuell`, `https://ogdcockpit.bonn.de/API_Beschreibungen`, `https://opengeodata-bonn.de/baustellen-tagesaktuell-mit-ortsangabe-bonn/`.
Die beiden im Auftrag genannten Seiten zu den Baustellen leiten mit HTTP 301 auf die Suche um. Die Schnittstellen selbst liefern aber weiter Daten.

**Beispiele (gekürzt)**
- Bebauungsplan: `{"bplan_name":"6119-1","inkraft_seit":"2020-05-27","pdf_link":"http://stadtplan.bonn.de/…/plan_internet/6119-1.pdf", …}`
- Baustelle (tagesaktuell und geplant): `{"baustelle_id":9746,"bezeichnung":"Siemensstraße","adresse":"Siemensstraße 50","von":"03.08.2026","bis":"22.12.2027","traeger":"Bundesstadt Bonn - Amt 66-5","massnahme":"Straßenbau","sperrung":"keine Sperrung"}` (liegt in Endenich)
- Baustelle: `{"baustelle_id":8921,"bezeichnung":"Hermann-Wandersleb-Ring (B56)","von":"08.01.2024","bis":"30.06.2027","traeger":"Straßen NRW","massnahme":"Brückensanierung","sperrung":"Teilsperrung von Fahrbahn und Gehweg"}`

## 2. Bebauungspläne

**Nummernschema** (aus den 1.128 Planobjekten abgeleitet): Die Nummern haben die Form `NNNN-N` (272) oder `NNNN-NN` (839). Hinzu kommen 16 Nummern mit Zusatz: a/A/B (11), I/II (3), `6622-2-A` und `6322-2 Teil A`. Eine Nummer (`Be 4`, von 1913) folgt keinem dieser Muster. Es gibt 143 verschiedene vierstellige Präfixe. Alle numerischen Präfixe beginnen mit 61–85, und ihr Mittelpunkt verschiebt sich mit den ersten beiden Ziffern von West nach Ost. Das deutet auf ein Blattschnittsystem hin; belegt ist es durch eine Quelle nicht. Von den 55 Plänen, die seit 2016 in Kraft getreten sind, tragen 46 die Präfixe 61–71. Ältere Pläne haben 72–85.
- Änderungen sind im Datensatz nicht als solche gekennzeichnet. In den Vorlagen erscheinen sie als „1. Änderung des Bebauungsplans Nr. …“ und tragen dieselbe Nummer.
- Ein Plantitel (etwa „Langwarthöfe“), die Verfahrensart und der Verfahrensstand fehlen.
- Die Pläne traten zwischen 22.07.1913 und 23.09.2026 in Kraft, 39 davon ab 2019. Der Stand im Repository (18.10.) und der Abruf vom 19.10. enthalten dieselben 1.128 Namen.

**Plannummern in Vorlagentiteln** (`out/plannummern_titel.tsv`)

| | stadtweit | Endenich-Bezug¹ |
|---|---|---|
| Vorlagen mit Plannummer – Regex der Pipeline (`pipeline/geocode.py`) | 523 (545 Paare) | – |
| Vorlagen mit Plannummer – erweiterte Prüfregel² | **556** (626 Paare, 142 Nummern) | 34 (36 Paare, 7 Nummern) |
| davon Vorlage mit mind. einer eindeutig zuordenbaren Nummer | 321 (85 Nummern) | 19 (4 Nummern: 6322-1, 6322-2 Teil A, 6322-3, 7520-2) |
| davon nur Grundnummer im Datensatz (7925-18 II → 7925-18) | 2 | 0 |
| mehrdeutig (Nummer passt auf mehrere Pläne) | 0 | 0 |
| davon nur Nummern, die im Datensatz fehlen | 233 (56 Nummern) | 15 (6421-1 „Universitäts-Campus Endenich“, 7522-77, 6320-18) |

¹ Der Plan überdeckt Endenich zu mindestens 5 % seiner Fläche (das trifft auf 39 Pläne im Datensatz zu), oder die Vorlage ist nach Stufe A/B in Endenich verortet, oder „Endenich“ steht im Titel.
² Die Prüfregel erkennt zusätzlich Listen („Nrn. 7721-56, 7721-24 … und 7621-3“), „Plan-Nr.“, Tippfehler („Bebaungsplanes“), „Bauleitplanverfahren“ und „Satzung Nr.“. Dazu kommen Zusätze wie a/A/I/II. Die Regel lässt nur Präfixe 6–8 zu und schließt Flurstücke (`NNNN-N-NNN`) aus. Sie findet 33 Vorlagen mehr als die Pipeline und verliert keine.

Die 56 fehlenden Nummern lassen sich so einordnen:
- **Aufgehobene Pläne:** 11 dieser Nummern haben einen Satzungsbeschluss im Titel. In 6 Fällen betrifft er eine Aufhebung (7522-77, 7525-47, 7822-22, 7920-22, 8016-89, 8116-13, Beschlüsse 2024–2025). Aufgehobene Pläne fallen also aus dem Datensatz heraus, und ihre Geschichte geht verloren.
- **Beschlossen, aber nicht im Datensatz:** Bei 5 Nummern liegt ein Satzungsbeschluss vor, der Plan fehlt aber noch: 6422-2, 6524-1, 6618-1, 6718-4 und 7213-2 (Beschlussvorlage vom 23.06.2025).
- **Pläne im Verfahren:** Die übrigen Nummern gehören vermutlich zu laufenden Verfahren; bei 27 stammt die letzte Vorlage aus 2025/2026.

Zwei Nummern könnten Tippfehler sein (6198-4, 6781-1); geprüft ist das nicht.

**Verfahrensschritte in Titeln** der 556 Vorlagen (Mehrfachnennung möglich):

| Schritt (Stichwort) | Vorlagen |
|---|---|
| Aufstellung/Einleitung | 142 |
| Frühzeitige Beteiligung | 125 |
| Veröffentlichung/Offenlage | 65 |
| Satzungsbeschluss | 95 |
| Änderung | 122 |
| Aufhebung | 28 |
| Anfrage/Antrag/Stellungnahme | 263 |
| kein Stichwort | 108 |

Von den 85 eindeutig zugeordneten Plänen haben 35 Vorlagen vor dem Inkrafttreten; bei ihnen ist das Verfahren im RIS ab 2019 sichtbar. Bei den übrigen 50 gibt es nur spätere Vorlagen, etwa zum Ausbau oder zu Anfragen.

**Plan-Verortung und Straßentreffer** (`out/vergleich_plan_strasse.tsv`):
- 296 Vorlagen haben in der Datenbank einen Geltungsbereich. 209 davon haben zusätzlich einen Straßentreffer der Stufe B.
- Lage des nächsten Straßenpunkts: bei 62 Vorlagen im Geltungsbereich, bei 137 bis 250 m entfernt, bei 10 zwischen 250 und 1.000 m, bei keiner weiter als 1.000 m.
- Der Ortsteil stimmt in 207 von 209 Fällen überein.
- Stichprobe von 15 Vorlagen (Zufall, Startwert 19102026): alle im selben Ortsteil, Abstände 0–407 m.
- Abstände über 0 m sind kein Fehler, denn der Straßenpunkt ist ein repräsentativer Punkt der ganzen Straße. Die Plannummer verortet genauer als der Straßenname.

## 3. Baustellen

- **Inhalt der Feeds (19.10.2026):**
  - **Die Feeds „30 Tage“ (14755) und „1 Jahr“ (14698) sind inhaltlich gleich:** dieselben 48 IDs mit denselben Eigenschaften.
  - Die 7 tagesaktuellen Baustellen sind eine Teilmenge davon.
  - 47 der 48 „geplanten“ Baustellen haben bereits begonnen (`von` ≤ 19.10.2026). Nur eine beginnt in den nächsten 30 Tagen.
  - Zeitspanne: `von` zwischen 08.01.2024 und 11.11.2026, `bis` zwischen 20.10.2026 und 21.12.2029.
- **Träger (48):**

  | Träger | Anzahl |
  |---|---|
  | Amt 66-2 | 22 |
  | SWB Bonn-Netz | 11 |
  | Amt 66-5 | 9 |
  | Straßen NRW | 2 |
  | Amt 68 | 1 |
  | Amt 66-4 | 1 |
  | Amt 66-6 | 1 |
  | Deutsche Bahn AG | 1 |

  Maßnahmen: Kanalbau 22, Straßenbau 9, Fernwärme 4, Wasserleitung 3, sonstige 10. 42 der 48 Baustellen sind ohne Sperrung. Die Baustellen liegen in 26 Ortsteilen, eine davon in Endenich. Der Stadtbezirk im Feed stimmt in allen 48 Fällen mit dem Ortsteilpolygon überein.
- **Zuverlässigkeit des Dienstes:** 9 von 19 Abrufen am 19.10.2026 lieferten HTTP 400 mit `{}`. Derselbe Code kommt bei einer ungültigen Themennummer. Ein Abruf braucht deshalb Wiederholungen und eine Prüfung von `numberMatched`.
- **Räumliche Nähe** (Machbarkeit, `out/baustellen_naehe.tsv`): Gezählt sind die 48 Baustellen, bei denen mindestens eine verortete Vorlage (Straße oder Bebauungsplan) jedes Kriteriums liegt; die Kriterien gelten nacheinander.

  | Kriterium | Baustellen mit Vorlage |
  |---|---|
  | Vorlage höchstens 150 m entfernt | 46 |
  | und gleicher Straßenname | 34 |
  | und federführend Tiefbauamt (66) oder eine Verkehrsstelle | 23 |
  | und Bau-Stichwort im Titel (Ausbau, Erneuerung, Umgestaltung, baureife Planung …) | 11 |

  Sichtprüfung der 11 nach Titeln:
  - **plausibel (6):** Brüdergasse, Am Hauptbahnhof, Gerichtsweg, Im Bonnet, Oppenhoffstraße, Siemensstraße. Bei der Siemensstraße (Endenich) sind das die Vorlagen 240553 „Umgestaltung der Siemensstraße …“ und 252383-01 ST „Siemensstraße Baubeginn“.
  - **unklar (4):** Kölnstraße, Theaterplatz, Werdstraße, An der Ohligsmühle. Hier sind Leitungs- oder Kanalbau von SWB bzw. Amt 66-2 Planungen anderer Art gegenübergestellt.
  - **nicht passend (1):** Wilhelmstraße.

  Ohne thematischen Filter liefert die räumliche Nähe überwiegend unpassende Paare (z. B. Fahrradständer, Glascontainer).
- **Archiv:** Ein tägliches Archiv ist nötig.
  - Die Feeds liefern nur den aktuellen Stand, ohne Parameter für frühere Stände.
  - Die Datensätze sind aus beiden Katalogen verschwunden.
  - Beendete Baustellen fallen heraus.
  - Der Umfang ist klein: rund 20 KB je Tag für beide Feeds, also unter 10 MB im Jahr ohne Komprimierung.

## 4. Risiken

| Risiko | Einschätzung |
|---|---|
| Lizenz Baustellen | Beide Datensätze sind auf opendata.bonn.de und open.nrw nicht mehr verzeichnet. CC0 ist nur im OGD-Cockpit (2020) und auf einer privaten Kopie (2018) belegt. Vor einer Veröffentlichung abgeleiteter Daten sollte die Lizenz geklärt werden. |
| Lizenz Bebauungspläne | Auf opendata.bonn.de gilt CC0. open.nrw zeigt „Andere geschlossene Lizenz“, vermutlich weil die Lizenz-URL nicht erkannt wird. Belegt ist diese Ursache nicht. Maßgeblich ist das Quellportal; die Abweichung sollte in den Quellenhinweis. |
| Unverbindlichkeit | Laut Quelle sind die Termine nicht verbindlich, und der Feed führt nur Baustellen mit „nennenswertem Einfluss auf das Verkehrsgeschehen“. Eine Baustelle ist also weder vollständig erfasst noch ein Beleg für die Umsetzung. |
| Fehlende Historie | Weder Baustellen noch Bebauungspläne haben Versionen. Aufgehobene Pläne und beendete Baustellen verschwinden ohne Spur. |
| Feed „1 Jahr“ | Er ist gleich dem 30-Tage-Feed und enthält fast nur laufende Baustellen. Die Bezeichnung „geplant“ trifft auf den Inhalt nicht zu. |
| Plandatensatz unvollständig | Pläne im Verfahren fehlen (233 Vorlagen, 56 Nummern). Bekannt gemachte Pläne erscheinen erst mit Verzug (z. B. 7213-2). |
| Datenschutz | `adresse` enthält Hausnummern, etwa als Bezugspunkt für Kanalbau. Ein Personenbezug ist nicht erkennbar. Die Anzeige sollte trotzdem auf Straßenebene bleiben, wie bei 5.2. |

## 5. Empfehlung für Phase 1–4

1. **Daten:**
   - Neuer Abruf `fetch-baustellen` für die Themen 14403 und 14698, mit bis zu 10 Versuchen und Prüfung von `numberMatched`. 14755 nur zur Beobachtung.
   - Tägliche Ablage als JSONL mit `first_seen`, `last_seen` und Änderungen an `von`/`bis`/`sperrung`, dazu Quelle und Abrufzeit.
   - Für Bebauungspläne den wöchentlichen Abruf beibehalten und ein Änderungsprotokoll führen: Plan neu, Plan entfallen (Kandidat für eine Aufhebung), Inkrafttreten geändert.
2. **Methode B3:**
   - Die Pipeline-Regex um die Prüfregel erweitern (33 Vorlagen mehr).
   - Konfidenz „hoch“ nur, wenn die Nummer genau einem Plan entspricht (366 Paare / 321 Vorlagen).
   - Teilpläne (6322-2 → „Teil A“) und Grundnummern kennzeichnen. Die zwei Flächen zu 7219-15 zusammenführen.
   - Fehlende Nummern ohne Fläche anzeigen, mit dem Hinweis „nicht im Datensatz (Verfahren oder aufgehoben)“; die Verortung übernimmt dann Stufe B.
3. **Planchronik und Soll-Schritte:**
   - Vorlagen je Plannummer gruppieren. Schritte aus den Titeln gelten als „abgeleitet“, `inkraft_seit` als „belegt“ (Stadt Bonn).
   - Die Soll-Schritte nach BauGB (§ 2 Abs. 1, § 3/§ 4 Abs. 1, § 3/§ 4 Abs. 2, § 10 Abs. 1, § 10 Abs. 3) nur als Soll darstellen. In vereinfachten und beschleunigten Verfahren (§§ 13, 13a) fehlende Schritte nicht als Lücke werten.
   - Pilot: Endenich mit 6322-2, 6322-3, 6421-1 und 7522-77.
4. **Oberfläche:**
   - Ebene „Baustellen (Stadt Bonn, Termine unverbindlich)“ erst nach Klärung der Lizenz.
   - Verknüpfungen nur als „möglicher Zusammenhang“, mit Angabe der Kriterien: Abstand, Straße, Zeitraum, Amt, Stichwort.
   - Keine Aussage „umgesetzt“.

## 6. Offene Fragen und vorgeschlagene Anfrage an opendata@bonn.de (nicht gesendet)

- Sind die Datensätze „Baustellen tagesaktuell“ und „Geplante Straßenbaustellen“ eingestellt oder nur aus dem Katalog genommen? Welche Lizenz gilt für die weiter erreichbaren Schnittstellen (Thema 14403, 14698, 14755)?
- Gibt es historische Baustellendaten (Archiv, frühere Stände) oder eine Schnittstelle mit Zeitbezug?
- Warum sind die Feeds „30 Tage“ und „1 Jahr“ gleich? Warum antwortet der Dienst zeitweise mit HTTP 400?
- Gibt es Daten zu Bebauungsplänen im Verfahren und zu aufgehobenen Plänen? Kann der Plantitel ergänzt werden?
- Darf die Lizenzangabe auf open.nrw zu „Lage der Bebauungspläne“ (geschlossen statt CC0) korrigiert werden?
- Für das Projekt: Soll die Anfrage gestellt werden? Wer sendet sie?
