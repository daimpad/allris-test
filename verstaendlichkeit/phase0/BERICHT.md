# Phase 0: Verständlichkeit und Auffindbarkeit

> **Nachtrag und Entscheidungen (01./02.11.2026):** Die Lücke der Maske ist geschlossen (27 Titel aus 15 Vorgängen, `maske.WORT`). Der Auftraggeber hat gewählt: Begriffe sichtbar machen, Karte mobil schneller laden, Seite in Einfacher Sprache; Seiten je Vorgang vorerst nicht (erst mit der Search Console).

Stand: 01.11.2026 · Datenstand des lokalen Exports: 28.10.2026 (24.915 Vorlagen) · nur gelesen, keine Änderung im Repository

## Anlass

Der Auftraggeber hat als nächsten Schwerpunkt „Verständlichkeit und Auffindbarkeit“ gewählt. Zielgruppe sind Bürger:innen ohne Verwaltungswissen; Maßstab bleibt WCAG 2.1 AA. Diese Phase 0 misst den Ist-Stand und bereitet Entscheidungen vor.

## Fragen

1. Wie schnell laden Startseite, ein Gebiet, `haushalt/` und eine Themenseite?
2. Welche Verwaltungsbegriffe stehen ohne Erklärung auf der Seite, was deckt das Glossar ab, wo hilft eine Erklärung am meisten?
3. Was enthielte eine kleine Seite in Leichter oder Einfacher Sprache?
4. Lohnen sich statische Seiten je Vorgang für Suchmaschinen (Umfang, Größe, Laufzeit, Sitemap, Deploy, Datenschutz)?
5. Welche 3 bis 5 Schritte folgen daraus?

## 1 Ladezeit

### Messung

Lokale Kopie der Seite (Befehle im Anhang), ausgeliefert mit einem kleinen Node-Server mit gzip (Stufe 6, im Speicher zwischengespeichert). Die Hauptadresse liefert Brotli (geprüft für `zeit.json`, `endenich.json`, `app.js`, `haushalt/`, Themenseite); gzip ist etwas größer, die lokalen Werte sind daher eher vorsichtig. Lighthouse 12.8.2, Chromium 141 headless, Voreinstellungen „mobil“ (simuliert: 150 ms RTT, 1,6 Mbit/s, CPU × 4) und „desktop“; je drei Läufe, Median.

| Seite | Gerät | Score | FCP | LCP | TBT | CLS | Übertragen | Anfragen |
|---|---|---|---|---|---|---|---|---|
| Start `/` | mobil | 80 | 1,4 s | 5,2 s | 107 ms | 0,00 | 842 KB | 37 |
| Start `/` | desktop | 96 | 0,4 s | 1,4 s | 0 ms | 0,00 | 1.281 KB | 52 |
| Gebiet `?gebiet=ortsteil:endenich` | mobil | 68 | 1,4 s | 5,8 s | 404 ms | 0,05 | 858 KB | 36 |
| Gebiet `?gebiet=ortsteil:endenich` | desktop | 93 | 0,4 s | 1,7 s | 57 ms | 0,01 | 1.558 KB | 59 |
| `haushalt/` | mobil | 99 | 1,5 s | 1,7 s | 0 ms | 0,00 | 133 KB | 6 |
| `haushalt/` | desktop | 100 | 0,3 s | 0,4 s | 0 ms | 0,00 | 133 KB | 6 |
| `thema/verkehr-und-mobilitaet/` | mobil | 99 | 1,5 s | 1,7 s | 5 ms | 0,00 | 134 KB | 6 |
| `thema/verkehr-und-mobilitaet/` | desktop | 100 | 0,3 s | 0,3 s | 0 ms | 0,02 | 134 KB | 6 |

Gegenprobe ohne Kompression (lokal, mobil, ein Lauf): Start LCP 12,2 s (2.076 KB), Endenich LCP 21,1 s (3.917 KB). Kompression ist für die Karte unverzichtbar; die Hauptadresse komprimiert.

Hauptadresse (je ein Lauf, über den Proxy dieser Umgebung): Start mobil LCP 6,1 s; Endenich mobil LCP 7,2 s, TBT 653 ms; `haushalt/` mobil 1,2 s; Themenseite mobil 1,6 s; Antwortzeit des Dokuments 230–270 ms. Start desktop brach ab (Verbindung zurückgesetzt). Erreichbarkeit von hier: 13 von 20 Abrufen der Startseite erfolgreich, Spiegel 20 von 20. Ob die Abbrüche am Server oder am Proxy dieser Umgebung liegen, lässt sich von hier nicht klären.

### Ursachen

- **Karte (Start, Gebiet):** Das größte Element (LCP) ist eine OSM-Kachel. Die Kacheln werden erst angefordert, wenn Leaflet, `app.js` und die Startdaten geladen sind. Aufteilung beim Start mobil: Antwort 8 %, Wartezeit bis zur Anforderung 26 %, Laden der Kachel 55 %, Zeichnen 11 %. OSM-Kacheln sind 515 KB von 842 KB (61 %) beim Start und 398 KB von 857 KB beim Gebiet; 12–15 Kacheln zu je 25–42 KB.
- **Blockierende Stile und Skripte:** vier Stylesheets im Kopf (Leaflet, zwei MarkerCluster, `style.css`) und fünf Skripte ohne `defer` am Ende des Body; Lighthouse schätzt 830 ms (Start) und 610 ms (Endenich) Einsparung.
- **Vorab angeforderte Daten** konkurrieren mit den Kacheln um die Bandbreite: sieben `preload` (u. a. `zeit.json` 746 KB entpackt / 52 KB gz, `flaechen/ortsteile.json` 175 / 53 KB, `kontext.json`, `glossar.json`, `baustellen.json`). Eine Vorverbindung zu `tile.openstreetmap.org` fehlt (Lighthouse: rund 300 ms beim Gebiet).
- **Gebiet:** `ortsteile/endenich.json` ist 1,96 MB entpackt (132 KB gz) für 557 Vorlagen, mit Prozess- und Schrittdaten je Vorlage. Auswerten und Zeichnen erzeugen eine lange Aufgabe von 419 ms in `app.js` und 3.686 DOM-Elemente; daher TBT 404 ms.
- **Statische Seiten** sind schnell, aber groß im DOM: `haushalt/` 790 KB HTML entpackt (74 KB gz), 17.981 Elemente; Themenseite Verkehr 645 KB (76 KB gz), 10.547 Elemente, 850 ms für Stil und Layout bei simulierter langsamer CPU.
- CLS ist überall unter 0,1.

## 2 Begriffe

### Was es gibt

- `pipeline/glossar.py` → `data/export/glossar.json`: 16 Ergebnistexte, 4 Rollen, Stände, Evidenzstatus, Schritte und **21 allgemeine Begriffe** mit Fundstelle (Vorlage, Drucksachennummer, Beschlussvorlage, Mitteilungsvorlage, Antrag, Änderungsantrag, Stellungnahme der Verwaltung, Anfrage, Bürgerantrag, Einwohnerantrag, Einwohnerfragestunde, Rat, Bezirksvertretung, Ausschuss, Hauptausschuss, Dringlichkeitsentscheidung, Fraktion, Öffentlichkeit, Federführendes Amt, Beratungsfolge, Tagesordnungspunkt).
- Auf der Seite gezeigt werden davon nur die **Ergebnistexte und Rollen**, im Vorgang im eingeklappten Akkordeon „Was bedeuten die Begriffe?“ (`site/app.js`, `glossary()`). Die 21 allgemeinen Begriffe nutzt nur der Ratsassistent (Werkzeug `erklaere_begriff`).
- Weitere Erklärungen: Dialog „Über“ („Was ist eine Vorlage?“, „Was bedeutet der Stand?“), Reiter „Prozesse → Gremien“ („Wer entscheidet was? Kurz erklärt“), Abschnitt „Nach Regelwerk (Soll)“ im Vorgang (je Verfahren ein Satz), `haushalt/` „So lesen Sie die Zahlen“ (eingeklappt).
- Keine Tooltips für Begriffe: 0 `<abbr>`/`<dfn>` in allen geprüften Zuständen; die 11 `title`-Attribute gehören zu Bedienelementen. Gebiets- und Themenseiten haben kein Glossar.

### Messung

Sichtbarer Text (`innerText`) in 12 Zuständen bei 1440 px mit Playwright gezählt (Start, drei Vorgänge, Liste Endenich, Prozesse ×3, Mitmachen, Gebietsseite, Themenseite Verkehr, Haushalt); Häufigkeit in den Daten aus dem Export. Ergebnis: `begriffe/begriffe.tsv`.

| # | Begriff | Häufigkeit in den Daten | sichtbar in | erklärt im Glossar | auf der Seite erklärt |
|---|---|---|---|---|---|
| 1 | Vorlagenart „Stellungnahme der Verwaltung“ | 6.788 Vorlagen | Liste, Vorgang „Art“, Themen-/Gebietsseiten (352×) | ja | nein |
| 2 | Beschlussvorlage (mit „: Einleitung“, „: Auftrag“) | 4.894 | wie 1 | ja | nur im Dialog „Über“ beiläufig |
| 3 | Mitteilungsvorlage | 3.374 | wie 1 | ja | nein |
| 4 | Änderungsantrag, Suffix „AA“ | 2.352 (AA: 2.343) | wie 1, Drucksache | ja (AA nein) | nein |
| 5 | Drucksache, Suffix „ST“ | alle; ST: 6.651 | Liste, Vorgang | ja („-01“; ST nein) | nein |
| 6 | Große/Kleine Anfrage | 1.722 | wie 1 (174×) | „Anfrage“ ja | im Soll-Abschnitt ein Satz |
| 7 | Bürgerantrag § 24 GO / Anregungen und Beschwerden | 1.708 | wie 1, Mitwirken (297×) | ja | im Mitwirken-Abschnitt |
| 8 | Dringlichkeitsantrag, Dringlichkeitsentscheidung OB/BV, Eilentscheidung HA | 512 | wie 1 | teils (Abkürzungen OB, BV, HA nein) | nein |
| 9 | Tagesordnungspunkte in nichtöffentlicher Sitzung | 879 | wie 1 | „Öffentlichkeit“ ja | Hinweis in der Prozesslinie |
| 10 | Bezirksvertretung | 11.885 Vorlagen | Prozesslinie, Mitmachen, Themenseiten (303×) | ja | Prozesse → Gremien |
| 11 | Hauptausschuss | 1.625 Vorlagen | Prozesslinie, Themenseiten | ja | nein |
| 12 | Rolle „Kenntnisnahme“, „Entscheidung“, „Empfehlung“, „Anhörung“ | 37.000 Beratungen | Prozesslinie | ja | Akkordeon im Vorgang |
| 13 | „zur Kenntnis genommen“ | 14.711 Beratungen | Prozesslinie, Themenseiten (146× sichtbar, mit „Kenntnisnahme“) | ja | nur im Vorgang (Akkordeon) |
| 14 | „(un)geändert beschlossen“, „abgelehnt“ | 14.514 | wie 13 (80×) | ja | wie 13 |
| 15 | „vertagt“, „verwiesen“, „ohne Votum“, „mit Maßgabe“, „Protokollnotiz“, „erledigt durch Stellungnahme“ | 3.655 | wie 13 (99× „vertagt“) | ja | wie 13 |
| 16 | Stand („beraten, ohne Entscheidung“ usw.) | alle | Liste, Vorgang, Gebietsseiten | ja | nur Dialog „Über“ |
| 17 | Prozessschritte „Initiierung“, „Vorbereitung“, „Vollzug“, „Folgevorlage“ | alle | Prozesslinie | Bezeichnung, keine Erklärung | Hinweistext je Schritt |
| 18 | Evidenzstatus „belegt/abgeleitet“, „Stufe B“, „Soll, nicht abgeglichen“, „Gremienart“ | alle | Vorgang | ja (Evidenz) | Legende (eingeklappt) |
| 19 | Amt mit Nummer („63 Bauordnungsamt“), federführend | alle | Vorgang „Amt“, Prozesse → Ämter | ja | nein |
| 20 | GO NRW, Geschäftsordnung § …, Hauptsatzung, Zuständigkeitsordnung | – | Vorgang (10–16× je Vorgang), Mitmachen | nein | verlinkt, Abkürzung „GO“ nicht aufgelöst |
| 21 | Produktbereich, Produktgruppe, Aufwandsart, ordentliche Aufwendungen | – | `haushalt/`, Haushaltsabschnitt der Themenseiten | – | `haushalt/` (eingeklappt); „Ansatz“, „Teilergebnisplan“ ohne Erklärung |
| 22 | Bebauungsplan, Offenlage, Satzungsbeschluss | 574 Titel | Titel, Planchronik | nein | Planchronik (BauGB-Schritte) |

### Wo eine Erklärung am meisten hilft

1. **Vorlagenart im Vorgang und in der Liste** (Zeilen 1–9): steht bei jeder Vorlage; die Erklärungen liegen fertig im Glossar, werden aber nicht angezeigt. Für 8 der 19 Arten fehlt ein eigener Eintrag (Dringlichkeitsantrag, Informationsbrief, Bürgerbrief, Einwohnerfrage, Tagesordnungspunkte in nichtöffentlicher Sitzung, Eilentscheidung HA, Beschlussvorlage: Einleitung und : Auftrag), ebenso für „ST“ und „AA“.
2. **Ergebnistexte auf Themen- und Gebietsseiten** (Zeilen 13–15): dort stehen sie hundertfach ohne jede Erklärung.
3. **Gremien in der Prozesslinie** (Zeilen 10–11): ein Satz und ein Link in den Reiter „Prozesse“.
4. **Eigene Begriffe der Seite** (Zeilen 17–18): „Initiierung“, „Vollzug“, „Stufe B“, „Konfidenz“, „Gremienart“ stammen aus dem Projekt; einfachere Wörter oder ein Satz daneben genügen.
5. **Haushalt** (Zeile 21): „Ansatz“ erklärt „Plan“, ist selbst aber nicht erklärt.

Hinweis: WCAG 2.1 verlangt Erklärungen ungewöhnlicher Wörter und Abkürzungen erst auf Stufe AAA (3.1.3, 3.1.4); für AA ist das kein Mangel. Tooltips per `title` sind mit Tastatur und auf Touchgeräten schlecht erreichbar; besser sind aufklappbare Erklärungen oder Links auf eine Begriffsseite.

## 3 Leichte oder Einfache Sprache

**Unterscheidung:** Leichte Sprache folgt festen Regeln (Netzwerk Leichte Sprache; DIN SPEC 33429) und wird üblicherweise von einer Prüfgruppe aus der Zielgruppe geprüft. Einfache Sprache (DIN ISO 24495-1, DIN 8581-1) ist weniger streng und braucht keine Prüfgruppe. Ohne Prüfgruppe sollte die Seite „Einfache Sprache“ heißen. BITV 2.0 § 4 verlangt von Bundesbehörden auf der Startseite Erläuterungen in Leichter Sprache (Inhalt, Bedienung, Barrierefreiheit); die RIS-Karte ist keine öffentliche Stelle, die Vorgabe taugt aber als Mindestumfang. Die genaue Rechtslage für NRW (BITV NRW) ist nicht geprüft.

**Minimaler Umfang** (eine Seite `einfach/`, rund 600–900 Wörter, kurze Sätze, ein Gedanke je Satz):

1. Was ist die RIS-Karte? (Karte, Liste, Zeitleiste; Daten der Stadt; täglich neu)
2. Wer entscheidet in Bonn? Rat, Bezirksvertretungen, Ausschüsse, Verwaltung – je zwei Sätze
3. Wie läuft eine Sache ab? Vorlage → Beratung → Ergebnis, mit einem Bild
4. Was bedeuten die Wörter? 12–15 Begriffe (Vorlage, Drucksache, Beschlussvorlage, Mitteilungsvorlage, Antrag, Stellungnahme, Bürgerantrag, Bezirksvertretung, Ausschuss, beschlossen, zur Kenntnis genommen, vertagt, Stand)
5. Wie benutze ich die Karte? (Gebiet wählen, Vorgang öffnen, Original ansehen)
6. Wie kann ich mitmachen? (Sitzung besuchen, Einwohnerfragestunde, Bürgerantrag – mit Link zur Stadt)
7. Was die Karte nicht kann (keine Rechtsauskunft, manches ist abgeleitet, maßgeblich ist das Original)
8. Kontakt

**Rahmen:**
- Quellentreu: jede Aussage zu Rechten und Abläufen mit Fundstelle (GO NRW, Geschäftsordnung), z. B. in einer Zeile „Für Fachleute“; Vereinfachung darf den Sinn nicht ändern („zur Kenntnis genommen“ heißt nicht „abgelehnt“).
- Keine Bewertung von Politik, Parteien oder Entscheidungen; keine Zusagen zum Erfolg eines Bürgerantrags.
- Keine Texte zu einzelnen Vorlagen in Leichter Sprache. Die vorhandenen KI-Kurzfassungen („einfache Sprache“, gekennzeichnet; auf dem Spiegel rund 5.470, im lokalen Export 44) bleiben, was sie sind, und gelten nicht als Leichte Sprache.
- Begriffe aus derselben Quelle wie das Glossar (`glossar.json`), damit Seite, Vorgang und Assistent gleich erklären.
- Prüfung vor der Veröffentlichung wie in den anderen Phasen (Prüfbogen im Gespräch); für das Etikett „Leichte Sprache“ zusätzlich eine Prüfgruppe.

## 4 Seiten je Vorgang

### Messung

Prototyp `tools/vorgangsseiten.py` (nur im Arbeitsordner): liest die Gebietsexporte, nutzt die Seitenhülle von `pipeline/gebietsseiten.py` und schreibt je Vorlage `vorgang/<drucksache>/index.html` mit Titel, Art (mit Glossarsatz), Datum, federführendem Amt, Stand (mit Erklärung), Ort (nur Namen, ohne Fundstelle), Beratungsfolge (Ergebnis wörtlich, Erläuterung allgemein), Bezügen als Links, Links zu Karte, Original und PDF, Quellenzeile. Keine Erzeugungszeitpunkte.

| Umfang | Seiten | Summe | gz | Median je Seite | größte | Sitemap | Laufzeit |
|---|---|---|---|---|---|---|---|
| alle Vorlagen | 24.915 | 91,5 MB | 39,4 MB | 3,5 KB (1,5 KB gz) | 41 KB | 1,83 MB | 9,9 s |
| seit 01.01.2024 | 9.664 | 35,4 MB | 15,2 MB | 3,5 KB | 41 KB | 0,71 MB | 4,5 s |
| mit Ortsbezug | 11.783 | 43,8 MB | 18,9 MB | 3,6 KB | 14 KB | 0,87 MB | 5,8 s |

Weitere Teilmengen (gezählt, nicht erzeugt): Regel der Vorgangsfeeds (seit 01.01.2025 oder offen/in Beratung) 8.096; seit Beginn der Wahlperiode (01.11.2025) 3.518; mit Ortsbezug ohne Vorlagen der Einwohnerschaft 7.650. Keine Kollisionen der Adressen. Belegter Platz auf der Platte bei 4-KB-Blöcken: 205 MB für alle Seiten.

- **Sitemap:** 24.915 Adressen, 1,83 MB – unter den Grenzen von 50.000 Adressen und 50 MB je Datei. Sinnvoll ist ein Sitemap-Index mit getrennter Datei für die Vorgänge und `lastmod` aus dem Datum der letzten Beratung.
- **Deploy:** Der Branch `deploy` hat heute 8.803 Dateien und 250,7 MB (davon Feeds 8.343 Dateien / 25,1 MB, Gebietsdaten 68,5 MB, Assistent 64,1 MB). Alle Seiten: +24.915 Dateien (dazu ebenso viele Ordner) und +91,5 MB, also rund 33.700 Dateien und 342 MB (+37 %). Der Branch wächst mit jeder Änderung weiter (`pages.yml` hängt Commits an). Grenzen des netcup-Webhostings (Speicher, Zahl der Dateien) und die Dauer des Plesk-Abgleichs sind nicht bekannt. GitHub Pages erlaubt 1 GB je Seite.
- **Änderungen pro Tag:** 2026 im Mittel 10,5 neue Vorlagen je Tag, dazu neue Beratungsergebnisse. Seiten ohne datumsabhängige Inhalte (z. B. ohne „nächste Sitzung“) ändern sich nur mit dem Inhalt.
- **Datenschutz:** Die Exporte tragen bereits die mit `pipeline/maske.py` maskierten Titel; der Prototyp übernimmt sie (764 Titel mit „[Hausnummer ausgelassen]“). **Befund:** 26 Titel aus 14 Vorgängen im Kreis der Maske (Einwohnerschaft, Bauordnung, Naturschutz und verbundene Vorlagen; 5.450 Vorlagen) zeigen weiter eine Hausnummer, weil sie nach „Hausnummer“, „Haus-Nr.“ oder „Haus Nr.“ steht und nicht direkt hinter dem Straßennamen (Drucksachen 200669, 210218, 212251, 220681, 221093, 221241, 222327, 222328, 230761, 252701, 260361, 260745, 260782 mit Folgevorlagen; Prüfbefehl im Anhang). Das betrifft schon heute Karte, Liste, Feeds und `suche.json`; Seiten je Vorgang würden diese Titel einzeln auffindbar machen.
- **Nutzen:** Heute erscheinen 2.192 der 24.915 Vorlagen (9 %) mit Titel in statischen Seiten (Themen- und Gebietsseiten); alle übrigen nur über JavaScript und Adressen mit `#Drucksache`, die Suchmaschinen nicht als eigene Seite werten. Das Ratsinformationssystem antwortet auf Abrufe wie `robots.txt` mit einer Seite „Zugriff pruefen“; OParl-Lite liefert eine Single-Page-Anwendung. Eigene Seiten wären vermutlich eine der wenigen durchsuchbaren Fassungen der Bonner Vorlagen – belegt ist das nicht, weil die Google Search Console noch nicht eingerichtet ist.
- **Kosten und Risiken:** gleichförmige Seiten mit wenig eigenem Text (Suchmaschinen nehmen oft nur einen Teil auf), größerer Deploy, mehr Sichtbarkeit von Titeln aus der Einwohnerschaft, Pflege einer weiteren Ausgabe. Die Erzeugung selbst ist mit rund 10 s unerheblich.

## Grenzen

- Lighthouse simuliert ein langsames Mobilnetz und eine langsame CPU; reale Werte auf 4G/5G liegen meist darunter. Felddaten (CrUX) gibt es für die Seite nicht.
- Lokal fehlen `baustellen.json` und `anliegen.json` (Branch `archiv`; 22 KB und 6 KB); vernachlässigbar.
- Messungen der Hauptadresse nur je ein Lauf und durch den Proxy dieser Umgebung; die Verbindungsabbrüche lassen sich nicht zuordnen.
- Begriffszählung nur in 12 Zuständen bei 1440 px; eingeklappte Inhalte zählen nicht als sichtbar.
- Der Nutzen von Seiten je Vorgang für Suchmaschinen ist nicht gemessen, nur abgeschätzt.
- Rechtslage zu Leichter Sprache in NRW nicht geprüft; DIN-Normen nur dem Namen nach genannt.

## Vorschläge zur Entscheidung

| # | Vorschlag | Aufwand | Risiko |
|---|---|---|---|
| 1 | **Lücke der Hausnummern-Maske schließen**: Muster um „Hausnummer(n)/Haus-Nr./Haus Nr./Hausnr. + Zahl“ erweitern, in `maske.py` und `masker()` in `site/chat/tools.js` gleich; Prüfung in `check`. Voraussetzung für Vorschlag 4. | klein | gering |
| 2 | **Glossar sichtbar machen**: im Vorgang je Vorlagenart ein Satz aus `glossar.json` (fehlende 8 Arten, „ST“, „AA“, „GO NRW“, „Ansatz“ ergänzen, je mit Fundstelle); Gremien in der Prozesslinie mit Link in den Reiter „Prozesse“; eigene Begriffe („Initiierung“, „Vollzug“, „Stufe B“) in einfachere Wörter fassen; statische Seite `begriffe/` aus derselben Quelle, verlinkt aus Vorgang, Themen-, Gebiets- und Haushaltsseite. | klein bis mittel | gering; Texte sind allgemeine Erklärungen, Ergebnistexte bleiben wörtlich |
| 3 | **Karte mobil schneller**: Vorverbindung zu `tile.openstreetmap.org`; Vorab-Anforderungen ohne Bedarf beim Start zurückstellen oder niedriger priorisieren (`zeit.json`, `kontext.json`, `baustellen.json` prüfen); Vendor-Stile zusammenfassen oder nicht blockierend laden, Skripte mit `defer`. Danach neu messen. In einem zweiten Schritt (mittel bis groß) Gebietsdaten in Liste und Detail teilen, um die 419-ms-Aufgabe und 1,96 MB je Gebiet zu verringern. | klein (Schritt 1) | gering; CSP und Integritätsprüfung beachten, Browser-Tests |
| 4 | **Seiten je Vorgang, gestuft**: Stufe 1 nach der Regel der Vorgangsfeeds (8.096 Seiten, rund 30 MB) oder ab Beginn der Wahlperiode (3.518); Vorlagen der Einwohnerschaft ohne Seite oder mit `noindex` (Entscheidung); Sitemap-Index; Link „Seite zu dieser Vorlage“ im Vorgang; nach 4–8 Wochen Search Console auswerten, dann über alle Vorlagen entscheiden. | mittel | mittel: Deploy-Größe auf netcup unbekannt, dünne Seiten, Datenschutz |
| 5 | **Seite in Einfacher Sprache** `einfach/` mit den acht Abschnitten aus Abschnitt 3, verlinkt aus „Los geht's“, Kopf und Fuß der statischen Seiten; Prüfbogen im Gespräch. Leichte Sprache erst mit Prüfgruppe. | klein bis mittel | gering, wenn quellentreu und ohne Bewertung |

Empfohlene Reihenfolge: 1 → 2 → 3 → 5 → 4 (4 erst mit Search Console).

## Offene Fragen an den Auftraggeber

1. Ist die Google Search Console inzwischen eingerichtet? Ohne sie lässt sich der Nutzen von Vorschlag 4 nicht messen.
2. Welche Grenzen hat das netcup-Webhosting (Speicher, Zahl der Dateien)? Wie lange dauert der Plesk-Abgleich heute?
3. Sollen Vorlagen aus der Einwohnerschaft (5.450 einschließlich verbundener Vorlagen) eigene Seiten bekommen, und wenn ja, mit `noindex`?
4. Dürfen KI-Kurzfassungen auf Seiten erscheinen, die Suchmaschinen aufnehmen (Gefahr, dass Auszüge ohne Kennzeichnung in Suchergebnissen stehen)?
5. „Einfache Sprache“ ohne Prüfgruppe oder „Leichte Sprache“ mit Prüfgruppe (Kosten, Partner)?
6. Ziel für die Ladezeit: genügt „gut“ auf dem Desktop und eine Verbesserung mobil, oder soll mobil der LCP-Richtwert von 2,5 s erreicht werden? Mit OSM-Kacheln als größtem Element ist das unter der Lighthouse-Simulation kaum erreichbar.
7. Treten die Verbindungsabbrüche der Hauptadresse auch außerhalb dieser Umgebung auf (`live.yml`, eigene Beobachtung)?

## Anhang: Befehle und Dateien

Arbeitsordner `D` der Prüfung (nicht im Repository).

```bash
# Seite bauen (aus dem Repository, schreibt nur nach $D/site)
mkdir -p $D/site/data/geo && cp -r site/. $D/site/ && cp -r data/export $D/site/data/ && cp data/LICENSE-DATA.md $D/site/data/ \
  && cp data/geo/*.geojson $D/site/data/geo/ \
  && .venv/bin/python -c "from pathlib import Path; from pipeline import seo; seo.write(Path('$D/site'), 'https://ris-bonn.datenatlas.de/')"
# Ausliefern mit gzip (8790) und ohne (8791)
node $D/tools/serve.mjs $D/site 8790 1 &  node $D/tools/serve.mjs $D/site 8791 0 &
# Lighthouse (in $D/tools: npm install lighthouse@12; Chromium aus /opt/pw-browsers)
CHROME_PATH=/opt/pw-browsers/chromium-1194/chrome-linux/chrome $D/tools/run_lh.sh http://localhost:8790 lokal-gzip 3
$D/tools/run_lh.sh https://ris-bonn.datenatlas.de produktion 1
python3 $D/tools/auswerten.py $D/lh/lokal-gzip --anfragen
# Begriffe (in $D/tools: npm install playwright@1.56.1)
node $D/tools/begriffe.mjs http://localhost:8790          # → $D/begriffe/begriffe.tsv, zustaende.json
# Seiten je Vorgang (Prototyp)
python3 $D/tools/vorgangsseiten.py data/export/bonn $D/proto/alle --alle     # ebenso --seit 2024, --ort
# Prüfung der Maske: Titel im Kreis der Maske mit „Hausnummer/Haus-Nr./Haus Nr. + Zahl“
python3 -I -c "import sys,re; sys.path[:0]=['$D/tools','.']; import alle_vorlagen; from pipeline import chat, maske; \
v=alle_vorlagen.alle(); ew=set(chat.einwohner(list(v.values()), auch=maske.privat)); \
rx=re.compile(r'(Hausnummer|Hausnr\.?|Haus-Nr\.?|Haus Nr\.?|Hausnummern)\s*\d+', re.I); \
print(sorted(r for r in ew if rx.search(v[r]['name'])))"
# Größe des Branch deploy
gh api "repos/daimpad/allris-test/git/trees/deploy?recursive=1" --jq '[.tree[]|select(.type=="blob")|.size]|add'
```

Ergebnisdateien: `$D/lh/` (Lighthouse-JSON, `auswertung-*.txt`, `erreichbarkeit.txt`), `$D/begriffe/begriffe.tsv`, `$D/proto/` (Prototyp-Seiten), `$D/tools/` (Skripte).
