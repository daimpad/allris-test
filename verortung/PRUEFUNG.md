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

## Mögliche Regeln (Entscheidung ausstehend)

| Regel | Wirkung in der Stichprobe | betroffene Vorlagen in Bonn |
|---|---|---|
| R1 Kreuzung: Nennt der Titel zwei Straßen, die sich kreuzen, gilt der Ortsteil der Kreuzung | behebt Nr. 3 | 628 von 7.162 mit Straßenbezug |
| R2 Widerspruch: Nennt der Titel einen Ortsteil, in dem die Straße nicht liegt, entfällt der Straßenpunkt (der Ortsteil bleibt) | betrifft Nr. 31 | 84 |
| R3 Schreibvarianten: bekannte Tippfehler der Ortsteilnamen als Varianten | behebt Nr. 4 | gering, je Variante |

Nr. 1, 12 und 27 behebt keine dieser Regeln; dafür wäre der Ort der Einrichtung nötig (Volltext oder Stufe C). Die Regeln würden erst nach Freigabe umgesetzt und an der Stichprobe nachgeprüft.
