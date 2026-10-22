# RIS-Karte Bonn

Womit befassen sich Rat, Bezirksvertretungen und Ausschüsse der Stadt Bonn – **wo**, **wann** und **wer** ist beteiligt? Die RIS-Karte macht die Vorlagen aus dem Ratsinformationssystem auf einer Karte, einer Zeitleiste und in einer Prozesslinie sichtbar. Jede Angabe ist auf ihre Quelle rückführbar. Was nicht in der Quelle steht, sondern erschlossen ist, trägt den Hinweis „abgeleitet“.

**Seite:** https://ris-bonn.datenatlas.de/ (Spiegel: https://daimpad.github.io/allris-test/) · **Datenpaket:** [Zip](https://daimpad.github.io/allris-test/data/export/allris-bonn-export.zip) · **Technik:** [TECHNIK.md](TECHNIK.md)

## Was die Seite zeigt

- **Ganz Bonn im Überblick:** Die Seite startet mit ganz Bonn. Die Farbstärke der Stadtbezirke und Ortsteile zeigt, wie viele Vorlagen mit Ortsbezug dort in den letzten zwölf Monaten erschienen sind; beim Überfahren nennt die Karte ein Thema, das im Gebiet auffällig häufig vorkommt (abgeleitet). Ein Klick auf einen Bezirk zeigt seine Ortsteile, ein Klick auf einen Ortsteil lädt dessen Vorlagen; dasselbe geht über die Auswahl oben.
- **Wo?** Eine Karte und eine gleichwertige Liste der Vorlagen je Ortsteil oder Stadtbezirk. Vorlagen ohne erkennbaren Ort stehen unter „stadtweit / ohne Ortsbezug“. Jeder Ort sagt, woher er stammt und wie sicher er ist.
- **Wann?** Eine Zeitleiste zeigt, wie viele Vorlagen je Monat entstanden, wann Gremien tagen und welche Wahlperiode gilt. Ein gewählter Zeitraum filtert Karte und Liste.
- **Wie läuft ein Verfahren?** Die Prozesslinie einer Vorlage zeigt ihre Stationen: Einreichung, Beratungen mit Gremium, Datum und wörtlichem Ergebnis, Folgevorlagen. Unter „Auswertung“ stehen die häufigsten Wege je Vorlagenart.
- **Prozesse: Wer entscheidet was?** Der Reiter „Prozesse“ zeigt alle Verfahrensarten – vom Bürgerantrag bis zum Bebauungsplan – mit Schritten, Fristen, Rechtsgrundlagen, Wegen zum Mitwirken und der Zahl der Vorgänge in Bonn, dazu die Gremien (Rat, Ausschüsse, Bezirksvertretungen, Beiräte) mit Zuständigkeit laut Zuständigkeitsordnung und nächster Sitzung, sowie die Ämter der Verwaltung mit Abteilungen, federführenden Vorlagen und den Gremien, die diese beraten. Alles lässt sich als Schaubild oder als Liste ansehen.
- **Suchen:** Die Suche oben findet Vorlagen in ganz Bonn nach Titel und Drucksache. Auf Wunsch sucht sie auch im Text der Dokumente (über die Volltextsuche von OParl-Lite, erst nach einem Klick); gezeigt werden dann die Vorlagen, kein Textausschnitt.
- **Wer?** Das federführende Amt, die beratenden Gremien und die Einreichenden, soweit erkennbar; dazu Filter nach zehn Themen und nach Partei bzw. Fraktion.
- **Bebauungspläne:** Die Geltungsbereiche der rechtskräftigen Pläne lassen sich einblenden. Die Planchronik zeigt je Plan die Verfahrensschritte nach dem Baugesetzbuch und die Vorlagen dazu.
- **Baustellen:** Gemeldete Baustellen der Stadt mit unverbindlichen Terminen, auf der Karte und in der Zeitleiste.
- **Mitmachen:** Sitzungstermine mit Tagesordnung, Kalenderdatei, Feeds je Gebiet und je Vorgang. Unter „Selbst mitwirken“ nennt jeder Vorgang die Wege, die das Regelwerk in seinem Stand vorsieht, mit Frist und Rechtsgrundlage: Sitzung besuchen, Einwohnerfrage, Fraktionen oder Bezirksverordnete ansprechen, eigener Bürgerantrag nach § 24 GO NRW mit zuständigem Gremium und nächster erreichbarer Sitzung. „Verortung falsch?“ meldet einen Fehler.
- **Mitmachen in Bonn:** Je Stadtbezirk die nächsten Sitzungen der Bezirksvertretung und des Rates, die nächste Frist für Einwohnerfragen und Bürgeranträge (berechnet, 21 Tage vor der Sitzung), die Fristen rund um eine Sitzung und alle Wege, sich einzubringen, jeweils mit Rechtsgrundlage.
- **Ratsassistent:** Ein Sprachmodell beantwortet Fragen ausschließlich mit den Daten dieser Seite. Man braucht dafür einen eigenen Schlüssel eines Anbieters; der Browser spricht den Anbieter direkt an.
- **Einstieg:** Das Fenster „Los geht's“ und eine Tour in 15 Schritten erklären alle Funktionen.

## Wie die Orte zustande kommen

Die Stadt nennt nur bei etwa 8 % der Vorlagen selbst einen Ort. Für die übrigen erschließt die Karte den Ort aus dem Titel:

1. **Ort der Stadt** – liegt eine Koordinate aus dem Ratsinformationssystem vor, wird sie übernommen (sicher).
2. **Name im Titel** – Straßen-, Ortsteil- oder Bezirksnamen im Titel werden mit einem Straßenverzeichnis und den Flächen der Stadt abgeglichen (erschlossen; unsicher, wenn ein Name auf mehrere Orte passt). Nennt der Titel zwei Straßen, die sich kreuzen, gilt der Ortsteil der Kreuzung. Folgt auf die Straße eine Hausnummer, bestimmt das Hausnummernverzeichnis der Stadt den Ortsteil; angezeigt wird weiter nur die Straße.
3. **Bebauungsplan im Titel** – eine eindeutige Plannummer verweist auf den Geltungsbereich des Plans (sicher).
4. **Text des Dokuments** – hat eine Vorlage keinen Ort aus 1 bis 3, werden dieselben Regeln auf den Text des Hauptdokuments angewandt (erschlossen oder unsicher). Angezeigt wird nur der erkannte Ort, kein Textauszug. Listen mit vielen Ortsteilen und Eingaben von Bürger:innen werden so nicht verortet.
5. **Übernommen** – eine Stellungnahme oder ein Änderungsantrag ohne eigenen Ort übernimmt den Ort der Vorlage, auf die er sich bezieht.

Etwa 57 % der Vorlagen haben keinen erkennbaren Ortsbezug. Orte erscheinen nur auf Ebene der Straße oder des Ortsteils, nie mit Hausnummer; Wohnadressen von Privatpersonen werden nicht verortet.

## Wie Verfahren dargestellt werden

Jeder Schritt der Prozesslinie hat einen **Evidenzstatus**:

- **belegt** – in den Daten dokumentiert;
- **abgeleitet** – erschlossen, etwa das Datum einer Beratung oder die Einreichenden aus dem Titel;
- **nicht öffentlich** – findet statt, ist aber von außen nicht einsehbar, etwa die Vorbereitung in der Verwaltung;
- **unklar** – aus öffentlichen Quellen nicht bestimmbar, vor allem, ob ein Beschluss umgesetzt wurde;
- **soll** – ein Schritt, den das Regelwerk vorsieht, der in den Daten aber nicht dokumentiert ist. Das heißt nicht, dass er fehlt.

Unter **„Nach Regelwerk (Soll)“** zeigt jeder Vorgang, welches Verfahren Gemeindeordnung, Geschäftsordnung des Rates, Hauptsatzung, Bezirkssatzung und Zuständigkeitsordnung vorsehen: die Schritte mit Rechtsgrundlage und Link, die Fristen vor einer Sitzung und „Wer entscheidet was?“ mit dem Abschnitt der Zuständigkeitsordnung. Das Modell stammt aus dem Projekt [„Bonn entscheidet“](https://github.com/anster2025/bonn-entscheidet) von Thomas ([anster2025](https://github.com/anster2025), MIT-Lizenz) und ist um eigene, belegte Schritte ergänzt. Die Zuordnung zum Verfahren ist abgeleitet. Abgeglichen wird nur, welche Gremienarten beraten haben. Weicht das ab, erscheint ein **Befund**; ein Befund ist keine Bewertung und kein Regelverstoß. Die Planchronik zeigt die Schritte nach Baugesetzbuch.

Der **Stand** einer Vorlage ist *entschieden*, *beraten, ohne Entscheidung*, *in Beratung*, *offen* oder *ohne Beratungsfolge*. Lücken bleiben als eigene Schritte sichtbar.

## Baustellen und Beschlüsse

Ob ein Beschluss umgesetzt ist, steht in keiner öffentlichen Schnittstelle. Eine Baustelle kann ein **Indiz** sein, aber kein Beleg. Die Karte zeigt bei einer Vorlage die Station **„Mögliche Umsetzung“** nur, wenn alle sechs Kriterien zutreffen:

- die Baustelle liegt höchstens 150 m vom Ort der Vorlage entfernt;
- sie beginnt nach der Entscheidung;
- beide betreffen dieselbe Straße;
- die Vorlage gehört zu Tiefbau oder Verkehr;
- der Titel nennt eine passende Baumaßnahme;
- die Vorlage ist ein Baubeschluss, also eine Beschlussvorlage der Verwaltung; ein Bürgerantrag oder Antrag, der eine Planung anstößt, zählt nicht.

Eine Stichprobe von 30 Kandidaten ist von Hand geprüft; alle Kandidaten, die diese Kriterien erfüllen, waren plausibel. Der Vollzug bleibt daneben „unklar“. Baustellen von Versorgern, Straßen NRW oder der Bahn setzen in der Regel keinen Ratsbeschluss um und werden getrennt gezeigt. Die Historie der Baustellen beginnt mit dem Archiv am 19.10.2026.

## Sprachmodelle: was erprobt wird

Zwei Auswertungen mit einem Sprachmodell (Mistral) laufen täglich im Hintergrund. Auf der Seite erscheinen sie erst, wenn eine Stichprobe die vereinbarte Güte erreicht; bis dahin werden sie nur geprüft.

- **Kurzfassungen** in einfacher Sprache, je Vorlage zwei bis drei Sätze. Jede wird automatisch geprüft: keine längeren Wortfolgen aus dem Dokument, keine Hausnummer, keine Zahl, Fraktion oder Gremium, die weder Titel noch Text nennen. In acht Stichproben zu je 30 Kurzfassungen fand die KI-Vorprüfung in den letzten fünf keine falsche; 18 bis 23 waren plausibel, die übrigen im Kern richtig, aber in einer Einzelheit ungenau. Eine Prüfung von Hand (22.10.2026) ergab 18 zutreffende und 12 teilweise zutreffende, keine falsche; seitdem erscheinen die Kurzfassungen im Vorgang, im Assistenten, in den Feeds und im Datenpaket, gekennzeichnet mit dem Hinweis, dass Einzelheiten ungenau sein können und das Original maßgeblich ist. Ein zweiter Schritt, in dem das Modell jede Kurzfassung gegen den Text gegenliest, brachte keine Verbesserung (22 von 30) und ist wieder abgeschaltet. Offene Entscheidungen und Prüfbögen stehen in [`ABNAHME.md`](ABNAHME.md).
- **Orte aus dem Text (Stufe C):** Das Modell unterscheidet Orte, die Gegenstand einer Vorlage sind, von solchen, die nur erwähnt werden. Beispielorte in stadtweiten Konzepten erkennt es nicht verlässlich (zuletzt 9 von 20 plausibel). Auch das bloße Herabstufen nur erwähnter Orte war in einer KI-Vorprüfung nur in 19 von 31 Fällen richtig; freigegeben ist nichts. Ein Prüfbogen für die Prüfung von Hand liegt bei ([`data/export/stufe_c/pruefung_herabstufungen.tsv`](data/export/stufe_c/pruefung_herabstufungen.tsv)).

Gespeichert werden nur die Ergebnisse des Modells, nie Text der Dokumente (Branch `kurzfassungen`). Stichproben und Vorprüfungen liegen unter `data/export/kurzfassungen/` und `data/export/stufe_c/`; Einzelheiten in [`TECHNIK.md`](TECHNIK.md).

## Grenzen

- Texte der Dokumente gibt es bisher nur für etwa 5 % der Vorlagen (Textauszug durch OParl-Lite, wächst täglich); bei den übrigen fehlen Orte, die nur im Dokument stehen. Aus dem Text werden keine Auszüge gezeigt.
- Vorlagen vor Oktober 2019 und nichtöffentliche Beratungen sind nicht enthalten.
- Ein Straßenpunkt steht für die ganze Straße, nicht für ein Gebäude.
- Die Übersichtskarte zählt nur Vorlagen mit Ortsbezug. Große Ortsteile haben schon wegen ihrer Größe mehr Vorlagen; eine Zahl je Einwohner:in wird nicht berechnet.
- Berechnete Fristen in „Mitmachen in Bonn“ beruhen auf den Sitzungsterminen; maßgeblich sind Einladung und Geschäftsordnung.
- Einreichende stehen nicht strukturiert in der Quelle; sie werden aus Vorlagenart und Titel erschlossen.
- Das Soll nach Regelwerk ist ein vereinfachtes Modell und keine Rechtsauskunft. Reihenfolge, Fristen und Rollen werden nicht abgeglichen.
- Die Stichproben zur Verortung, zu den Themen, zu den Baustellen und zum Soll nach Regelwerk sind von Hand geprüft. In der Stichprobe Endenich (50 Vorlagen) lag der Ort in 41 Fällen richtig, in 4 teilweise und in 5 falsch, meist bei Straßen, die durch mehrere Ortsteile führen ([`verortung/PRUEFUNG.md`](verortung/PRUEFUNG.md)). Bei den Themen passten 46 von 49 geprüften Vorlagen, zwei teilweise ([`themen/PRUEFUNG.md`](themen/PRUEFUNG.md)). Vorprüfungen durch KI sind als solche gekennzeichnet und ersetzen die Prüfung von Hand nicht.

## Datenquellen und Lizenzen

| Quelle | Inhalt | Lizenz |
|---|---|---|
| [OParl-API der Stadt Bonn](https://www.bonn.sitzung-online.de/oparl/bodies/1) (Ratsinformationssystem) | Vorlagen, Beratungen, Gremien, Ämter, Orte | CC0 1.0 (ohne PDFs) |
| [OParl-Lite Bonn](https://oparl.bonn.machdenstaat.de/) (machdenstaat) | Sitzung, Tagesordnungspunkt und Ergebnis je Beratung | CC BY 4.0 |
| Stadt Bonn, [Ortsteile und Stadtbezirke](https://opendata.bonn.de/dataset/flächen-der-ortsteile) | Flächen | CC0 1.0 |
| Stadt Bonn, [Lage der Bebauungspläne](https://opendata.bonn.de/dataset/lage-der-bebauungspläne) | 1.128 rechtskräftige Pläne mit Plan und Begründung | CC0 1.0 |
| Stadt Bonn, [Hausnummern georeferenziert](https://opendata.bonn.de/dataset/strassenliste-straßennamen-straßenverzeichnis-hausnummern-georeferenziert) | Ortsteil je Hausnummer (nur zur Verortung, ohne Anzeige der Nummer) | CC0 1.0 |
| Stadt Bonn, Baustellen (Stadtplan) | laufende und geplante Baustellen | CC0 1.0 (laut Auftraggeber) |
| OpenStreetMap | Straßenverzeichnis, Kartenhintergrund | ODbL 1.0, © OpenStreetMap-Mitwirkende |

Die Daten werden täglich neu abgerufen. Lizenzen je Datei: [`data/LICENSE-DATA.md`](data/LICENSE-DATA.md). Der Code steht unter MIT-Lizenz ([`LICENSE`](LICENSE)).

## Mitmachen, Impressum

Fehler in der Verortung lassen sich direkt bei einer Vorlage melden („Verortung falsch?“). Hinweise zum Mitentwickeln stehen in [`CONTRIBUTING.md`](CONTRIBUTING.md), technische Einzelheiten in [`TECHNIK.md`](TECHNIK.md).

Erstellt von Damian Paderta im Rahmen des Hackathons „Hack den Stadtrat“. Impressum: https://nozilla.de/impressum/ · Datenschutz: [ris-bonn.datenatlas.de/datenschutz.html](https://ris-bonn.datenatlas.de/datenschutz.html)
