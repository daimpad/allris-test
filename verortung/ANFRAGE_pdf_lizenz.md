# Entwurf: Anfrage zur Nutzung der Dokumente im Ratsinformationssystem

Stand: Entwurf vom 20.10.2026, noch nicht versandt. Versand durch den Auftraggeber.

An: opendata@bonn.de
Betreff: Ratsinformationssystem (OParl) – Nutzung der Dokumente (PDF); Einwohnerzahlen je Ortsteil

Sehr geehrte Damen und Herren,

im Rahmen des Hackathons „Hack den Stadtrat“ entwickle ich die RIS-Karte Bonn (https://ris-bonn.datenatlas.de/). Sie macht die Vorlagen des Ratsinformationssystems räumlich und zeitlich zugänglich. Grundlage ist Ihr Datensatz „Ratsinformationssystem OParl-API“ (CC0).

In der Beschreibung heißt es: „Die Nutzung umfasst die Textinformationen zu den Ratsterminen und öffentlichen Gremienvorlagen aus dem Ratsinformationssystem ohne angehängte bzw. externen Dokumente.“ Welche Bedingungen für die Dokumente selbst gelten, habe ich nicht gefunden. Die RIS-Karte wertet deshalb bisher nur Titel und Metadaten aus. Etwa 57 % der Vorlagen lassen sich so keinem Ort zuordnen, obwohl der Ort oft im Dokument steht. Daher meine Fragen:

1. **Lizenz der Dokumente.** Unter welchen Bedingungen dürfen die über die OParl-API verlinkten Dokumente (`mainFile`, `auxiliaryFile`) genutzt werden, etwa Vorlagen, Stellungnahmen der Verwaltung und Niederschriften?
2. **Maschinelle Auswertung.** Dürfen die Texte automatisch ausgewertet werden, um Orte (Straße, Ortsteil, Bebauungsplan) zu erkennen und die Vorlagen durchsuchbar zu machen? Die Texte selbst würden nicht veröffentlicht.
3. **Abgeleitete Angaben.** Dürfen daraus gewonnene Angaben veröffentlicht werden: der erkannte Ort, ein kurzes Zitat als Fundstelle (ein Satz) und eine gekennzeichnete Kurzfassung, jeweils mit Link zum Original im Ratsinformationssystem?
4. **Ausnahmen.** Gibt es Dokumente, die davon ausgenommen sind, etwa Anlagen Dritter (Gutachten, Pläne, Fotos)? Sind sie in den Daten erkennbar?
5. **Abruf.** Gibt es eine empfohlene Abrufweise für viele Dokumente, etwa Textfassungen oder eine Obergrenze für Abrufe je Zeit?
6. **Einwohnerzahlen je Ortsteil.** Gibt es die Zahl der Einwohnerinnen und Einwohner je Ortsteil (51 Ortsteile wie im Datensatz „Flächen der Ortsteile“) als offenen Datensatz? Gefunden habe ich die Zahlen je statistischem Bezirk im archivierten Covid-19-Datensatz (Stand 31.12.2020) und im Strukturdatenatlas (Stand 31.12.2024, als PDF). Die statistischen Bezirke lassen sich den Ortsteilen aber nicht eindeutig zuordnen.

Zum Datenschutz: Die RIS-Karte verortet keine Wohnadressen von Privatpersonen. Bürgeranträge erscheinen höchstens auf Ebene der Straße oder des Ortsteils, Namen von Privatpersonen nie. Abgeleitete Angaben sind als solche gekennzeichnet.

Für Rückfragen stehe ich gern zur Verfügung. Vielen Dank für die offenen Daten der Stadt Bonn.

Mit freundlichen Grüßen
Damian Paderta
NOZILLA · contact@nozilla.de

---

**Quelle des Zitats** (nicht Teil der Nachricht): Beschreibung des Datensatzes auf https://opendata.bonn.de/dataset/ratsinformationssystem-oparl-api und https://open.nrw/dataset/ratsinformationssystem-oparl-api-bn, geprüft am 20.10.2026. Die CC0-Freigabe gilt danach für die Daten der Schnittstelle, nicht für die Dokumente; das Recht auf Einsicht in öffentliche Unterlagen klärt die Weiterverwendung nicht.

**Wozu die Antwort dient** (nicht Teil der Nachricht): Frage 6 betrifft die Übersichtskarte („Vorlagen je 1.000 Einwohner:innen“); Prüfung am 20.10.2026: Von 62 statistischen Bezirken liegen nur 10 zu mehr als 95 % in einem Ortsteil, eine Umrechnung nach Fläche wäre eine grobe Schätzung. Stufe C der Verortung (Orte aus dem Volltext, CLAUDE.md 5.2), die Suche im Volltext der Dokumente und verständliche Kurzfassungen (CLAUDE.md Abschnitt 6) sind zurückgestellt, bis die Lizenz der PDFs geklärt ist (CLAUDE.md Abschnitt 8).
