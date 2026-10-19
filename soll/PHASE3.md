# Soll-Modell – Phase 3: Mitwirkung

Stand: 19.10.2026. Grundlage: `soll/PHASE2.md`.

## Umsetzung

| Baustein | Datei |
|---|---|
| Einflussregeln (14) aus `verfahren.json`, Anrede „Sie“ | `data/soll/ergaenzungen.json` (Abschnitt `anrede`, alter Wortlaut wird beim Laden geprüft), `pipeline/soll.py` |
| Regeln mit Rechtsgrundlagen für Seite und Assistent | `data/export/bonn/soll.json` (`mitwirken`, `buergerantrag_ziel`) |
| Auswertung je Vorlage und Tag | `site/mitwirken.js` (Regelauswertung wie `mitwirken` in `einordnung.py` des Originals) |
| Anzeige | „Selbst mitwirken“ im Vorgang (`site/app.js`, `fillMitwirken`) |
| Assistent | `hole_prozesslinie` → `soll_nach_regelwerk.mitwirken`, `mitwirken_einordnung`; Systemprompt Änderung 17 |
| Tests | `tests/js/mitwirken.test.mjs` (5), `tests/js/tools.test.mjs`, `tests/test_soll.py` (10) |

## Übertragung auf unsere Daten

Das Original leitet den Status eines Vorgangs aus eigenen Abrufen ab. Hier wird er aus vorhandenen Angaben abgeleitet:

| Merkmal | Ableitung |
|---|---|
| Status | Stand der Vorlage: „entschieden“ → abgeschlossen; „beraten, ohne Entscheidung“ → vertagt bei Vertagung, sonst unklar; „in Beratung“, „offen“ → offen oder vertagt; „ohne Beratungsfolge“ → unklar. Ohne Termin schließen Kenntnisnahme oder Erledigung (ohne ausstehende Entscheidung), eine Mitteilung und die Genehmigung durch den Rat den Vorgang (ergänzt in Phase 4, `soll/PHASE4.md`) |
| Abschluss | Ergebnisgruppen des Originals (beschlossen, abgelehnt, zur Kenntnis, erledigt) aus dem wörtlichen Ergebnis |
| Termin | nächste Beratung dieser Vorlage ab heute ohne Ergebnis (Sitzung über OParl-Lite verknüpft) |
| Ebene | „bezirk“, wenn nur Bezirksvertretungen beraten, sonst „stadt“ |
| Ziel eines Bürgerantrags | Bezirksvertretung (Ebene Bezirk) oder Ausschuss für Beteiligung der Bürgerinnen und Bürger; nächste Sitzung laut Sitzungskalender, deren Frist (21 Tage vorher) noch nicht verstrichen ist |

**Eigene Festlegung:** Ein offener oder vertagter Vorgang ohne Termin und ohne Datum in den letzten 12 Monaten gilt als „unklar“. Meist fehlt dann die Verknüpfung der Beratung, nicht die Entscheidung. Für Vorgänge ohne Soll (Bürgerbrief) gelten keine Regeln.

## Darstellung

- Die Regeln ergänzen „Selbst mitwirken“. Jede Regel zeigt ihre Frist, bei festem Bezug mit Datum („also bis …“). Eine verstrichene Frist ist gekennzeichnet. Die Rechtsgrundlagen sind verlinkt.
- Wo eine Regel genauer ist, ersetzt sie den allgemeinen Hinweis:
  - Sitzungshinweis bei Termin;
  - Bürgerantrag mit zuständigem Gremium;
  - Hinweis zur Entscheidung.
- Ein abgeschlossener Vorgang zeigt keinen Sitzungshinweis.
- Ein Satz nennt die Herkunft: vereinfachtes Modell, Anrede angepasst, Stand und Termin abgeleitet, keine Rechtsauskunft.

Verteilung in Endenich (574 Vorlagen, 19.10.2026):

| Status | Vorlagen |
|---|---|
| abgeschlossen | 442 |
| unklar | 90 |
| offen | 21 |
| vertagt | 14 |
| ohne Soll | 7 |

Kommende Termine kommen derzeit nicht vor: OParl-Lite verknüpft Tagesordnungen erst etwa zwei Wochen vor der Sitzung. Geprüft im Browser auf Desktop (1440 px) und Mobil (390 px); axe-core ohne Verstöße.

## Grenzen

- Die Einordnung ist abgeleitet und nicht von Hand geprüft. Phase 4 sieht dafür eine Stichprobe vor.
- Die Sie-Fassung ändert nur die Anrede. Inhalt und Belege bleiben die des Originals.
- Die Hinweise sind keine Rechtsauskunft. Maßgeblich sind Geschäftsordnung, Satzungen und die zuständige Stelle.

## Nächster Schritt

Phase 4 (nach Freigabe): Prüfung. Stichprobe von 30 Vorgängen zu Zuordnung, Befund und Mitwirkung; danach Datenpaket und Dokumentation abschließen.
