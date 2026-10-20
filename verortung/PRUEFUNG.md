# Prüfung der Verortung: Stichprobe Endenich

Stand 20.10.2026. Stichprobe: `data/export/endenich/stichprobe_pruefung.tsv` (50 Vorlagen mit Ortsbezug in Endenich, zufällig gezogen, wird nie überschrieben). KI-Vorprüfung: `data/export/endenich/vorpruefung_verortung.tsv` (gekennzeichnet, ersetzt nicht die Prüfung von Hand).

**Prüffrage:** Liegt der Ort, um den es in der Vorlage geht, in Endenich? Geprüft von Hand durch den Auftraggeber am 20.10.2026, in Gruppen zu sechs bzw. acht Vorlagen.

## Ergebnis

| Urteil | Anzahl | Anteil |
|---|---|---|
| richtig | 41 | 82 % |
| teilweise (Endenich ist nur ein Teil des Gebiets) | 4 | 8 % |
| falsch | 5 | 10 % |

Nach Methode:

| Methode | richtig | teilweise | falsch |
|---|---|---|---|
| `strasse` | 27 | 1 | 4 |
| `strasse+ortsteil` | 2 | – | – |
| `ortsteil_name` | 7 | 3 | – |
| `ortsteil_adjektiv` | 5 | – | – |
| `vererbt` | – | – | 1 |

Die KI-Vorprüfung stimmte in 47 von 50 Fällen. Die drei Abweichungen sind Nr. 1 und 12 (KI: unklar, von Hand: falsch) und Nr. 3 (KI: richtig, von Hand: falsch; die Kreuzung liegt laut OSM-Geometrie in der Weststadt).

## Fehlerarten

1. **Straße über mehrere Ortsteile, der Ort liegt außerhalb Endenichs** (Nr. 1, 3, 12, 27). Drei der vier betreffen Straßen, die nach Endenich benannt sind, aber in der Weststadt oder in Poppelsdorf beginnen (Endenicher Allee, Endenicher Straße). Der Titel nennt eine Einrichtung, eine Kreuzung oder ein Bauwerk am anderen Ende der Straße.
2. **Tippfehler im Ortsteilnamen** (Nr. 4, „Poppeldorf“): Die Eingrenzung auf den genannten Ortsteil greift nicht.
3. **Teilweise:** Strecken und Gebiete, die über Endenich hinausreichen (A 565 ab der Anschlussstelle Endenich, Nr. 9, 49, 50; ZOB und Siemensstraße, Nr. 14).

Außerdem vermerkt, ohne Einfluss auf das Urteil: Nr. 31 nennt den Ortsteil Endenich und eine Straße, die das Straßenverzeichnis nur in Ippendorf und Poppelsdorf kennt. Die Straßenpunkte landen deshalb außerhalb des genannten Ortsteils.

## Regeln (Entscheidung des Auftraggebers 20.10.2026: R1 umsetzen, auf R2 verzichten)

| Regel | Wirkung in der Stichprobe | betroffene Vorlagen in Bonn |
|---|---|---|
| R1 Kreuzung: Nennt der Titel zwei Straßen, die sich kreuzen, gilt der Ortsteil der Kreuzung | behebt Nr. 3 | 628 von 7.162 mit Straßenbezug |
| R2 Widerspruch: Nennt der Titel einen Ortsteil, in dem die Straße nicht liegt, entfällt der Straßenpunkt (der Ortsteil bleibt) | betrifft Nr. 31 | 84 |
| R3 Schreibvarianten: bekannte Tippfehler der Ortsteilnamen als Varianten | behebt Nr. 4 | gering, je Variante |

Nr. 1, 12 und 27 behebt keine dieser Regeln; dafür wäre der Ort der Einrichtung nötig (Volltext oder Stufe C).

## Umsetzung

**R1 umgesetzt** (`_crossings` und `_resolve_street` in `pipeline/geocode.py`, Kreuzungen in `data/geo/strassen_bonn.json`, Tests in `tests/test_geocode.py`):

| Kennzahl | vorher | nachher |
|---|---|---|
| Straßenpunkte der Stufe B | 12.048 | 11.058 |
| Vorlagen mit Straßenbezug | 6.722 | 6.722 |
| davon Ortsteil über Kreuzung bestimmt | – | 969 |
| Straßenpunkte im Ortsteil der Stadt (Vorlagen mit Stufe A) | 73,8 % (1.982 von 2.687) | 78,3 % (1.905 von 2.434) |
| Vorlagen in Endenich | 574 | 556 |

In der Stichprobe ist Nr. 3 behoben (jetzt nur Weststadt); bei Nr. 7, 11 und 24 sind die Punkte enger gefasst, Endenich bleibt. Keine als richtig geprüfte Vorlage verliert Endenich. Die 18 Vorlagen, die Endenich verlassen, betreffen Kreuzungen in der Weststadt, der Nordstadt und in Lengsdorf; bei fünf bestätigt der Ort der Stadt (Stufe A) den neuen Ortsteil.

**Auf R2 verzichtet** (Entscheidung des Auftraggebers 20.10.2026, nach Auswertung für ganz Bonn). Gründe:

1. Ortsnamen in Titeln wie „Grundstück in Bonn-Kessenich, Haager Weg“ bezeichnen meist die **Gemarkung** (Katasterbezirk), nicht den statistischen Ortsteil, dessen Flächen die Karte nutzt. Die Straße liegt dann richtig, der genannte Ort folgt anderen Grenzen. R2 hätte in rund 30 solchen Bauvorlagen den genauen Straßenpunkt durch den Mittelpunkt eines falschen Ortsteils ersetzt. Das betrifft vermutlich auch Nr. 31.
2. Ohne Einschränkung entfernte R2 auch Straßen, wenn der Titel zwei getrennte Orte nennt („in der Weststadt und am Hermann-Wandersleb-Ring“) oder ein Adjektiv einen Flurnamen meint („am Meßdorfer Feld“).

Eine auf Namen wie „Rheinufer“ beschränkte Fassung wurde erwogen und ebenfalls nicht umgesetzt; solche Namen tragen ohnehin die Konfidenz „niedrig“.

**R3 umgesetzt** (Freigabe des Auftraggebers 20.10.2026; `ORTSTEIL_VARIANTEN`, `BEZIRK_VARIANTEN` in `pipeline/geocode.py`):
- Kandidaten: Wörter in allen Titeln mit Editierdistanz 1 (bei Namen ab 8 Zeichen: 2) zu einem Ortsteil- oder Bezirksnamen, von Hand gesichtet.
- Aufgenommen als Variante: Poppeldorf, Plitterdorf(er), Pennefeld, Holtdorf, Schwarz-Rheindorf, Bad-Godesberg, Goesberg, Beuler.
- Aufgenommen als Genitiv: zum Beispiel „Rüngsdorfs“, „Villenviertels“, „Bad Godesbergs“ (Wortformen, keine Fehler).
- Nicht aufgenommen:
  - andere Orte: Medinghoven, Godesburg, Bendenfeld, Mondorf, Roisdorf, Meindorf, Buschhof, Dollendorf;
  - Straßennamen: Pützchens Chaussee, Venusbergweg, Auerbergweg;
  - „Pützchens“ als Genitiv, weil es in Eigennamen steht. Die Kreuzung Siegburger Straße/Pützchens Chaussee liegt in Vilich und wäre sonst auf Pützchen eingegrenzt worden.
- Wirkung in ganz Bonn: 23 Vorlagen geändert, davon 12 neu verortet und 11 enger eingegrenzt. Nr. 4 der Stichprobe ist behoben (Sebastianstraße nur noch Poppelsdorf, nicht mehr Endenich). Keine weitere Vorlage verliert oder gewinnt Endenich.

## Stichprobe zur Hausnummernregel

Regel `strasse+hausnummer` seit 20.10.2026 (TECHNIK.md).
- Stichprobe: `data/export/hausnummern/stichprobe_hausnummern.tsv`, 30 Vorgänge, wird nie überschrieben. Darin alle 5 Vorgänge mit geändertem Ortsteil und 25 zufällig gezogene mit „eindeutig statt mehrerer Ortsteile“, je Vorgang eine Zeile.
- Prüffrage: Liegt der Ort, um den es in der Vorlage geht, im Ortsteil der Hausnummer?
- Vorprüfung (`vorpruefung_hausnummern.tsv`, ersetzt nicht die Prüfung von Hand):
  - maschinell: 30 von 30 Adressen nennt auch die Ortsteil-Angabe der Stadt im Verzeichnis so;
  - KI-Vorprüfung: 29 plausibel, 1 teilweise (Nr. 1, Strecke zwischen zwei Adressen). Drei Sammelvorlagen nennen mehrere Grundstücke; die Regel gilt dort je Straße.
- Ergebnis (20.10.2026): Der Auftraggeber hat die Einschätzung der KI-Vorprüfung für alle 30 Vorgänge übernommen. Danach sind 29 richtig und 1 teilweise; falsch ist keiner, die Regel bleibt unverändert.
  - Das Urteil ist in der Spalte „anmerkung“ jeder Zeile so gekennzeichnet. Die Vorgänge wurden nicht einzeln von Hand am Original geprüft.
  - Gestützt wird das Ergebnis vor allem durch den unabhängigen Abgleich mit der Ortsteil-Angabe der Stadt (30 von 30 gleich).
