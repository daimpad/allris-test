# RIS-Karte Bonn

Womit befassen sich Rat, Bezirksvertretungen und Ausschüsse der Stadt Bonn – **wo**, **wann** und **wer** ist beteiligt? Die RIS-Karte macht die Vorlagen aus dem Ratsinformationssystem auf einer Karte, einer Zeitleiste und in einer Prozesslinie sichtbar. Jede Angabe ist auf ihre Quelle rückführbar. Was nicht in der Quelle steht, sondern erschlossen ist, trägt den Hinweis „abgeleitet“.

**Seite:** https://ris-bonn.datenatlas.de/ (Spiegel: https://daimpad.github.io/allris-test/) · **Datenpaket:** [Zip](https://daimpad.github.io/allris-test/data/export/allris-bonn-export.zip) · **Technik:** [TECHNIK.md](TECHNIK.md)

## Was die Seite zeigt

- **Wo?** Eine Karte und eine gleichwertige Liste der Vorlagen je Ortsteil oder Stadtbezirk. Vorlagen ohne erkennbaren Ort stehen unter „stadtweit / ohne Ortsbezug“. Jeder Ort sagt, woher er stammt und wie sicher er ist.
- **Wann?** Eine Zeitleiste zeigt, wie viele Vorlagen je Monat entstanden, wann Gremien tagen und welche Wahlperiode gilt. Ein gewählter Zeitraum filtert Karte und Liste.
- **Wie läuft ein Verfahren?** Die Prozesslinie einer Vorlage zeigt ihre Stationen: Einreichung, Beratungen mit Gremium, Datum und wörtlichem Ergebnis, Folgevorlagen. Unter „Auswertung“ stehen die häufigsten Wege je Vorlagenart.
- **Wer?** Das federführende Amt, die beratenden Gremien und die Einreichenden, soweit erkennbar; dazu Filter nach zehn Themen und nach Partei bzw. Fraktion.
- **Bebauungspläne:** Die Geltungsbereiche der rechtskräftigen Pläne lassen sich einblenden. Die Planchronik zeigt je Plan die Verfahrensschritte nach dem Baugesetzbuch und die Vorlagen dazu.
- **Baustellen:** Gemeldete Baustellen der Stadt mit unverbindlichen Terminen, auf der Karte und in der Zeitleiste.
- **Mitmachen:** Sitzungstermine mit Tagesordnung, Kalenderdatei, Feeds je Gebiet und je Vorgang, Hinweise zum Bürgerantrag nach § 24 GO NRW. „Verortung falsch?“ meldet einen Fehler.
- **Ratsassistent:** Ein Sprachmodell beantwortet Fragen ausschließlich mit den Daten dieser Seite. Man braucht dafür einen eigenen Schlüssel eines Anbieters; der Browser spricht den Anbieter direkt an.
- **Einstieg:** Das Fenster „Los geht's“ und eine Tour in 14 Schritten erklären alle Funktionen.

## Wie die Orte zustande kommen

Die Stadt nennt nur bei etwa 8 % der Vorlagen selbst einen Ort. Für die übrigen erschließt die Karte den Ort aus dem Titel:

1. **Ort der Stadt** – liegt eine Koordinate aus dem Ratsinformationssystem vor, wird sie übernommen (sicher).
2. **Name im Titel** – Straßen-, Ortsteil- oder Bezirksnamen im Titel werden mit einem Straßenverzeichnis und den Flächen der Stadt abgeglichen (erschlossen; unsicher, wenn ein Name auf mehrere Orte passt).
3. **Bebauungsplan im Titel** – eine eindeutige Plannummer verweist auf den Geltungsbereich des Plans (sicher).
4. **Übernommen** – eine Stellungnahme oder ein Änderungsantrag ohne eigenen Ort übernimmt den Ort der Vorlage, auf die er sich bezieht.

Etwa 57 % der Vorlagen haben keinen erkennbaren Ortsbezug. Orte erscheinen nur auf Ebene der Straße oder des Ortsteils, nie mit Hausnummer; Wohnadressen von Privatpersonen werden nicht verortet.

## Wie Verfahren dargestellt werden

Jeder Schritt der Prozesslinie hat einen **Evidenzstatus**:

- **belegt** – in den Daten dokumentiert;
- **abgeleitet** – erschlossen, etwa das Datum einer Beratung oder die Einreichenden aus dem Titel;
- **nicht öffentlich** – findet statt, ist aber von außen nicht einsehbar, etwa die Vorbereitung in der Verwaltung;
- **unklar** – aus öffentlichen Quellen nicht bestimmbar, vor allem, ob ein Beschluss umgesetzt wurde;
- **soll** – nur in der Planchronik: ein Verfahrensschritt nach Baugesetzbuch, zu dem keine Vorlage vorliegt. Das heißt nicht, dass er fehlt.

Der **Stand** einer Vorlage ist *entschieden*, *beraten, ohne Entscheidung*, *in Beratung*, *offen* oder *ohne Beratungsfolge*. Lücken bleiben als eigene Schritte sichtbar.

## Baustellen und Beschlüsse

Ob ein Beschluss umgesetzt ist, steht in keiner öffentlichen Schnittstelle. Eine Baustelle kann ein **Indiz** sein, aber kein Beleg. Die Karte zeigt bei einer Vorlage die Station **„Mögliche Umsetzung“** nur, wenn alle fünf Kriterien zutreffen:

- die Baustelle liegt höchstens 150 m vom Ort der Vorlage entfernt;
- sie beginnt nach der Entscheidung;
- beide betreffen dieselbe Straße;
- die Vorlage gehört zu Tiefbau oder Verkehr;
- der Titel nennt eine passende Baumaßnahme.

Diese Anzeige ist vorläufig, bis eine Stichprobe von Hand geprüft ist. Der Vollzug bleibt daneben „unklar“. Baustellen von Versorgern, Straßen NRW oder der Bahn setzen in der Regel keinen Ratsbeschluss um und werden getrennt gezeigt. Die Historie der Baustellen beginnt mit dem Archiv am 19.10.2026.

## Grenzen

- Ausgewertet werden nur Titel und Metadaten, nicht die Texte der Dokumente. Orte, die nur im Dokument stehen, fehlen.
- Vorlagen vor Oktober 2019 und nichtöffentliche Beratungen sind nicht enthalten.
- Ein Straßenpunkt steht für die ganze Straße, nicht für ein Gebäude.
- Einreichende stehen nicht strukturiert in der Quelle; sie werden aus Vorlagenart und Titel erschlossen.
- Was Zuständigkeitsordnung und Bezirkssatzung vorsehen, ist noch nicht erfasst.
- Stichproben zur Verortung, zu den Themen und zu den Baustellen werden noch von Hand geprüft. Vorprüfungen durch KI sind als solche gekennzeichnet und ersetzen diese Prüfung nicht.

## Datenquellen und Lizenzen

| Quelle | Inhalt | Lizenz |
|---|---|---|
| [OParl-API der Stadt Bonn](https://www.bonn.sitzung-online.de/oparl/bodies/1) (Ratsinformationssystem) | Vorlagen, Beratungen, Gremien, Ämter, Orte | CC0 1.0 (ohne PDFs) |
| [OParl-Lite Bonn](https://oparl.bonn.machdenstaat.de/) (machdenstaat) | Sitzung, Tagesordnungspunkt und Ergebnis je Beratung | CC BY 4.0 |
| Stadt Bonn, [Ortsteile und Stadtbezirke](https://opendata.bonn.de/dataset/flächen-der-ortsteile) | Flächen | CC0 1.0 |
| Stadt Bonn, [Lage der Bebauungspläne](https://opendata.bonn.de/dataset/lage-der-bebauungspläne) | 1.128 rechtskräftige Pläne mit Plan und Begründung | CC0 1.0 |
| Stadt Bonn, Baustellen (Stadtplan) | laufende und geplante Baustellen | CC0 1.0 (laut Auftraggeber) |
| OpenStreetMap | Straßenverzeichnis, Kartenhintergrund | ODbL 1.0, © OpenStreetMap-Mitwirkende |

Die Daten werden täglich neu abgerufen. Lizenzen je Datei: [`data/LICENSE-DATA.md`](data/LICENSE-DATA.md). Der Code steht unter MIT-Lizenz ([`LICENSE`](LICENSE)).

## Mitmachen, Impressum

Fehler in der Verortung lassen sich direkt bei einer Vorlage melden („Verortung falsch?“). Hinweise zum Mitentwickeln stehen in [`CONTRIBUTING.md`](CONTRIBUTING.md), technische Einzelheiten in [`TECHNIK.md`](TECHNIK.md).

Erstellt von Damian Paderta im Rahmen des Hackathons „Hack den Stadtrat“. Impressum: https://nozilla.de/impressum/ · Datenschutz: [ris-bonn.datenatlas.de/datenschutz.html](https://ris-bonn.datenatlas.de/datenschutz.html)
