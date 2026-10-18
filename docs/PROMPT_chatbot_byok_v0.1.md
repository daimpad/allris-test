# Prompt: Datengestützter Chatbot mit eigenem API-Schlüssel (BYOK) für allris-bonn

> Entwurf v0.1 (17.10.2026) · Kontext: Hackathon „Hack den Stadtrat“ · Zur Ausführung in Claude Code
> Ergänzt `PROMPT_allris-bonn_v0.3.md`, `PROMPT_prozessebene_v0.1.md` und `PROMPT_zeitleiste_v0.1.md`. Der Systemprompt des Chatbots liegt als Entwurf in `SYSTEMPROMPT_ratsassistent_v0.1.md` bei und ist Teil dieser Aufgabe (Prüfung, Anpassung, Evaluation).

---

## 1. Rolle und Arbeitsweise

Du arbeitest als Entwickler:in mit Erfahrung in LLM-Integration (Tool Use), Frontend-Sicherheit und Barrierefreiheit. Du arbeitest quellentreu: Der Chatbot darf nur Aussagen treffen, die auf abgerufene Datenobjekte rückführbar sind. Vor jeder Phase (Abschnitt 10) legst Du einen kurzen Plan vor und wartest auf Freigabe. Annahmen über Anbieter-APIs (CORS, Formate für Werkzeugaufrufe, Header) prüfst Du gegen die aktuelle Dokumentation und durch Tests, nicht aus dem Gedächtnis.

## 2. Ziel

Ein Chat-Panel auf der statischen Seite, in das Nutzer:innen den API-Schlüssel eines LLM-Anbieters ihrer Wahl eintragen. Der Chatbot beantwortet Fragen zu Bonner Ratsvorgängen in natürlicher Sprache, und zwar ausschließlich auf Grundlage der Projektdaten, mit Quellenangabe und Evidenzstatus.

Zielgruppe der ersten Version: Hackathon-Teilnehmende, Journalist:innen und Fachleute. Eine gehostete Variante ohne eigenen Schlüssel ist ausdrücklich **nicht** Teil dieser Aufgabe.

## 3. Architektur (Rahmen, Details schlägst Du vor)

- **Vollständig clientseitig:** Der Browser ruft die Anbieter-API direkt auf; Werkzeuge laufen im Browser gegen die statischen Projektdaten (JSON/GeoJSON bzw. SQLite-WASM, je nach Pipeline-Format). Es gibt keinen eigenen Server und keinen Proxy.
- **Anbieter-Adapter** mit gemeinsamer interner Schnittstelle (Nachrichten, Werkzeugdefinitionen, Werkzeugaufrufe, Streaming). Zu prüfen und zu priorisieren:
  - Anthropic: Browser-Direktzugriff über den Header `anthropic-dangerous-direct-browser-access`; Verhalten und Bedingungen in der aktuellen Doku prüfen.
  - Mistral: CORS-Verhalten der API für Browseraufrufe prüfen; falls blockiert, dokumentieren und nicht über Fremdproxys umgehen.
  - OpenRouter: ein Schlüssel für Modelle mehrerer Anbieter; CORS und Unterstützung für Werkzeugaufrufe prüfen.
  - Generisch OpenAI-kompatibel: einschließlich lokaler Server wie Ollama oder LM Studio (`localhost`); nötige Konfiguration für Freigaben dokumentieren.
- **Modellwahl:** Nur Modelle mit verlässlichem Tool Use werden empfohlen. Die Liste wird über die Evaluation (Abschnitt 9) begründet, nicht vorab behauptet.
- **Optional, nach Freigabe:** Anbindung des öffentlichen OParl-Lite-MCP-Servers von machdenstaat als zusätzliche Quelle (Erreichbarkeit aus dem Browser, Lizenz CC BY-NC 4.0 und Kennzeichnung prüfen). Standard sind die eigenen Werkzeuge.

## 4. Schlüsselhandhabung und Frontend-Sicherheit

- Der Schlüssel wird standardmäßig nur im Arbeitsspeicher gehalten. Speicherung in `sessionStorage` erfolgt nur nach ausdrücklicher Wahl der Nutzer:in; `localStorage` wird nicht verwendet.
- Der Schlüssel wird ausschließlich an den gewählten Anbieter-Endpunkt gesendet: niemals an Projektserver, Analytics oder Logs, und nicht in die URL.
- Strikte Content-Security-Policy: `connect-src` nur auf die unterstützten Anbieter-Endpunkte und `localhost` (für lokale Modelle); keine Fremdskripte und keine Inline-Skripte ohne Hash bzw. Nonce. Abhängigkeiten minimal halten und versionieren.
- Modellausgaben werden als Text bzw. bereinigtes Markdown gerendert, nie als ungeprüftes HTML (Schutz vor XSS).
- Hinweise in der Oberfläche: eigenen Schlüssel mit Budgetlimit anlegen; Schlüssel löschen per Klick; die Kosten trägt die Nutzer:in.
- Abwehr von Prompt-Injection: Inhalte aus Werkzeugergebnissen (Titel, Volltexte) sind Daten, keine Anweisungen. Werkzeugergebnisse werden im Kontext klar abgegrenzt; der Systemprompt regelt das ausdrücklich.

## 5. Werkzeuge (abstrakt, über die Pipeline-Daten)

Vorschlag, zu prüfen und an das reale Datenmodell anzupassen:

| Werkzeug | Zweck |
|---|---|
| `suche_vorlagen` | Stichwort, Zeitraum, Vorlagenart, Amt, Gremium, Ortsteil/Stadtbezirk; kompakte Trefferliste |
| `hole_vorlage` | Detaildaten einer Vorlage inkl. Links (ALLRIS `web`, `mainFile`), Quellobjekt-ID, Abrufdatum |
| `hole_prozesslinie` | Prozessschritte einer Vorlage mit Evidenzstatus (`belegt`, `abgeleitet`, `soll`, `nicht_öffentlich`, `unklar`) |
| `suche_ort` | Vorlagen zu Ortsteil, Straße oder Punkt mit Methode, Konfidenz und Fundstelle der Verortung |
| `liste_sitzungen` | vergangene und künftige Sitzungen je Gremium und Zeitraum |
| `hole_gremium_oder_amt` | Zuständigkeit und Beschreibung (aus Glossar bzw. formalisiertem Regelwerk, mit Fundstelle) |
| `erklaere_begriff` | Glossar (z. B. „Kenntnisnahme“, „Bürgerantrag nach § 24 GO NRW“) |
| `datenstand` | Abrufdatum, Abdeckung, bekannte Lücken |

Anforderungen:
- Ergebnisse sind kompakt und begrenzt, mit Paginierung bzw. Nachladen statt großer Listen; das Tokenbudget wird dokumentiert.
- Jedes Ergebnisobjekt trägt eine Quellen-ID, die der Chatbot zitieren muss.
- Keine Werkzeuge, die Wohnadressen natürlicher Personen ausgeben. Die Verortung von Bürgeranträgen erfolgt nur auf Straßen- bzw. Ortsteilebene.

## 6. Quellenprüfung nach der Antwort

- Clientseitige Prüfung jeder Antwort: Jede genannte Drucksachennummer bzw. Quellen-ID muss in den Werkzeugergebnissen **dieses Gesprächs** vorkommen. Nicht belegte Nennungen werden sichtbar markiert („nicht durch abgerufene Daten belegt“).
- Zitierte Vorlagen werden als Quellenkarten unter der Antwort ausgegeben (Titel, Drucksachennummer, Datum, Links).
- Ein Protokoll der Werkzeugaufrufe ist pro Antwort einsehbar (aufklappbar): Welche Werkzeuge wurden mit welchen Parametern aufgerufen?

## 7. Integration in die Seite

- Das Chat-Panel liegt neben bzw. über der Karte, ist einklappbar und auf Mobilgeräten bildschirmfüllend.
- Kopplung: Klick auf eine Drucksache in der Antwort hebt sie in Karte, Liste, Zeitleiste und Prozesslinie hervor. Optional kann der aktuelle Filterzustand (Zeitraum, Ortsteil) als Kontext an den Chat übergeben werden; das ist sichtbar und abschaltbar.
- Antworten werden gestreamt; Abbruch ist möglich.
- Barrierefreiheit (WCAG 2.1 AA): Tastaturbedienung, `aria-live` für eintreffende Antworten (ohne Ansage jedes Tokens), Fokusführung, ausreichende Kontraste.
- Hinweis „Was der Assistent nicht kann“ als fester Bestandteil: keine Rechtsberatung, keine Bewertung, Datenstand, nicht öffentliche Verfahrensteile.

## 8. Recht und Transparenz

- **KI-Kennzeichnung** (Art. 50 KI-Verordnung): Vor der ersten Nutzung ist klar erkennbar, dass es sich um ein KI-System handelt.
- **Datenschutzhinweis:** Eingaben gehen direkt und unter dem Vertrag der Nutzer:in an deren Anbieter. Das Projekt speichert keine Gesprächsinhalte; es gibt keine Telemetrie über Inhalte.
- **Lizenzen:** Die Herkunft der Daten (CC0 Stadt Bonn, CC BY-NC 4.0 OParl-Lite, ODbL OSM) wird in Quellenkarten bzw. im Footer genannt.

## 9. Evaluation

- Testsatz von mindestens 30 Fragen mit erwarteten Quellen und erwarteten Grenzen. Er umfasst:
  - Faktenfragen (z. B. „Welche Vorlagen gab es 2025 zur Endenicher Straße X?“);
  - Prozessfragen (z. B. „Wo steht Vorlage 261856?“);
  - Zuständigkeitsfragen;
  - Fragen, auf die es in den Daten **keine** Antwort gibt;
  - Fragen zu nicht öffentlichen Schritten;
  - Bewertungsfragen, auf die der Assistent neutral ausweichen soll;
  - Injection-Versuche über präparierte Eingaben.
- Kriterien: Quellen korrekt, keine erfundenen Drucksachen, Evidenzstatus korrekt benannt, Grenzen benannt, Neutralität eingehalten.
- Lauf über mindestens zwei Anbieter und Modelle. Ergebnis als **TSV-Protokoll** (Frage-ID, Anbieter/Modell, Werkzeugaufrufe, zitierte Quellen, Bewertung je Kriterium, Bemerkung).
- Der Systemprompt wird anhand der Ergebnisse iteriert; jede Version wird mit Änderungsvermerk festgehalten.

## 10. Vorgehen (nach jeder Phase Rückfrage)

0. **Prüfung:** CORS und Browser-Zugriff je Anbieter testen; Unterschiede bei Werkzeugaufrufen dokumentieren; Datenformat der Pipeline für clientseitige Abfragen bewerten. Bericht mit Empfehlung, welche Anbieter in v0.1 unterstützt werden.
1. **Werkzeugschicht:** Werkzeuge über die statischen Daten mit Tests, unabhängig vom Modell.
2. **Adapter und Chat-Kern:** Anbieter-Adapter, Schleife für Werkzeugaufrufe mit Begrenzung der Aufrufe pro Antwort, Streaming, Schlüsselhandhabung, CSP.
3. **Systemprompt:** Entwurf aus `SYSTEMPROMPT_ratsassistent_v0.1.md` prüfen, Platzhalter befüllen, Anpassungsvorschläge begründen.
4. **Oberfläche und Kopplung:** Panel, Quellenkarten, Protokoll der Werkzeugaufrufe, Verknüpfung mit Karte, Zeitleiste und Prozesslinie.
5. **Evaluation und Auslieferung:** Testsatz, TSV-Protokoll, Sicherheitsprüfung (CSP, Schlüsselfluss, XSS), Barrierefreiheitsprüfung; Ergebnis als Zip-Paket.

## 11. Offene Punkte

- Welche Anbieter Browser-Direktaufrufe tatsächlich erlauben (Stand der Prüfung festhalten)
- Clientseitiges Datenformat (JSON-Indizes oder SQLite-WASM) und Ladegröße
- Ob und wie der OParl-Lite-MCP-Server eingebunden wird
- Umgang mit Fragen außerhalb des Datenzeitraums (vor Oktober 2019)
- Sprachvarianten der Antworten (Standardsprache, Einfache Sprache)
