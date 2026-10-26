# Schule und Bildung – Phase 1: Regelentwurf und Prüfbogen (26.10.2026)

**Grundlage:** `phase0/BERICHT.md` mit den Entscheidungen vom 26.10.2026.

**Stand:** Entwurf. `schule` steht in `ENTWUERFE`, nicht in `ALLE`: kein Export, keine Seite, bis der Prüfbogen im Gespräch geprüft ist.

## Regeln (`pipeline/themenseiten/schule.py`, abgeleitet, je Vorlage mit Grund)
Die erste passende Regel gilt.

0. **Ausschluss:** Kitas (auch Kindergarten, KiBiz), Musikschule, Volkshochschule, Sammellisten nichtöffentlicher Punkte, Bestellung der Schriftführung.
1. **Schulweg und Schülerticket:** Der Titel nennt eine Schule (Schule, Gymnasium, Berufskolleg, OGS, Ganztag, Schüler) und Schulweg, Schulstraße, Elterntaxi, Schülerticket, Querung, Ampel, Tempo, Radweg, Haltestelle, Parken o. Ä.
2. **Schulbau und Sanierung:** Schulwort und Neubau, Sanierung, Erweiterung, Umbau, Interim, Container, Turnhalle, Mensa, Toiletten, Schulhof, Brandschutz o. Ä.
3. **Schulplätze und Ganztag:** Schulwort und Zügigkeit, Errichtung, Gründung, Anmeldungen, Kapazität, Schulentwicklung, Betreuung, OGS.
4. **Weitere:** Schulamt federführend, Beratung im Schulausschuss oder ein Schulwort im Titel; eingeklappt.

„Hochschule“, „Volkshochschule“, „Musikschule“ und „Schulden“ zählen nicht als Schulwort.

## Weitere Festlegungen
- **Prozessbild:** nur Beschlüsse und Anträge mit Beratung in Rat, Hauptausschuss, Schulausschuss oder Betriebsausschuss SGB; am 26.10.2026 sind das 26.
- **Bahnen:** Haushalt 2027/2028 oben (gemeinsam mit Kultur und Verkehr, `themenseiten/haushalt.py`), darunter Bezirksvertretungen, Schulausschuss, andere Ausschüsse, Finanzausschuss, Hauptausschuss und Rat.

## Erweiterung im allgemeinen Teil (`dossier.py`)
- `bedingung`: Eine Titelregel gilt nur, wenn der Titel zusätzlich ein zweites Muster trifft (hier: ein Schulwort). Der Grund nennt beide Wörter.
- Gegenprobe des Prüfbogens ohne Ausgeschlossenes.

Kultur und Verkehr bleiben unverändert (Referenztest).

## Stand 26.10.2026
162 Vorlagen:

| Strang | Vorlagen |
|---|---|
| Schulweg und Schülerticket | 39 |
| Schulbau und Sanierung | 32 |
| Schulplätze und Ganztag | 15 |
| weitere | 76 |

## Prüfbogen
`data/export/schule/stichprobe_schule.tsv`, Schritt `schule-stichprobe`; einmal gezogen, danach nicht überschrieben.
- **24 zugeordnete Vorlagen:** je Strang 6. Frage: Passt der Strang?
- **6 nicht zugeordnete Vorlagen** ohne Schulwort im Titel, aber mit Sport- oder Turnhalle oder „Kindern und Jugendlichen“ (Gegenprobe). Frage: Fehlt die Vorlage auf der Seite?

Erste Auffälligkeiten beim Ziehen:
- Ein Betreuungsangebot für Vorschulkinder steht unter Schulplätze und Ganztag.
- Eine Schranke am Berufskolleg steht wegen „Errichtung“ unter Schulplätze und Ganztag.

Die Gegenprobe wurde vor der Prüfung zweimal neu gezogen: Die erste enthielt fast nur Sammellisten anderer Ausschüsse, die zweite Grenzfälle außerhalb der Schulen (Hochschule, Ausbildungsmarkt).
