# Prozessebene und Zeitleiste – Phase 0: Prüfung

Stand 18.10.2026 · Datenbasis: OParl-API der Stadt Bonn (Abruf 18.10.2026), OParl-Lite Bonn · reproduzierbar mit `prozess/analyse_phase0.py` · Stichprobe: `prozess/stichprobe_endenich.tsv` (28 Endenicher Vorlagen, geschichtet nach Art der Initiierung)

## 1. Schritttypen und Evidenz

| Schritt (Prompt Abschnitt 4) | Befund | Status |
|---|---|---|
| Initiierung | Vorlagenart in jeder Vorlage gesetzt; Einreichende nur im Titel | `belegt`; Einreichende `abgeleitet` |
| Verwaltungsinterne Vorbereitung | in keiner Quelle sichtbar | `nicht_öffentlich` (ohne Datum) |
| Veröffentlichung | `paper.date` bei 100 % gesetzt; Semantik nicht dokumentiert (s. 3) | `belegt`, Bedeutung `unklar` |
| Beratung | 38.043 Beratungen mit Gremium und Rolle (Stadt); 90,7 % mit Sitzung, Datum und TOP über OParl-Lite | Beratung `belegt`, Datum/Ergebnis `abgeleitet` |
| Entscheidung | `authoritative` bei 42,5 % der Vorlagen; Ergebnis wörtlich aus OParl-Lite | `belegt` / `abgeleitet` |
| Schleifen, Verzweigungen | vertagt 1.047, verwiesen 414 Ergebnisse; 2.352 Änderungsanträge, 6.788 Stellungnahmen als Folgevorlagen verknüpft | `belegt` |
| Vollzug | Beschlusskontrolle ohne Schnittstelle | `unklar` |
| Abschluss / Stand | aus Beratungsfolge ableitbar (entschieden, in Beratung, offen) | `abgeleitet` |
| Soll-Schritte | Regelwerk nicht formalisiert | nicht ausgewiesen (Phase 2 optional) |

## 2. Sonderwege

- **Dringlichkeits- und Eilentscheidungen:** eigene Vorlagenarten (OB 89, BV 35, HA 10); alle 134 haben eine Beratungsfolge (nachträgliche Genehmigung).
- **Nichtöffentliche Tagesordnungspunkte:** als Vorlagenart erfasst (879), ohne Inhalt; das Feld `public = 0` ist nur bei 2 TOPs gesetzt.
- **Rat ohne Vorberatung:** 1.301 Vorlagen, deren einzige Beratung eine Entscheidung im Rat ist.
- **Ohne Beratungsfolge:** 3 Vorlagen.

## 3. Zeitdimensionen

| Dimension | Abdeckung | Befund |
|---|---|---|
| Datum der Vorlage | 24.915 von 24.915 (07.10.2019–16.10.2026) | 795 Beratungen liegen **vor** dem Datum ihrer Vorlage; das Datum ist daher nicht sicher die Erstveröffentlichung |
| Sitzungsdatum der Beratung | 90,7 % (über OParl-Lite) | Median 28 Tage nach dem Datum der Vorlage, 90 % binnen 119 Tagen |
| Sitzungen (Termine) | 1.541, davon 90 künftig, 144 abgesagt | direkt aus der OParl-API (`meetings`), auch künftige |
| Wahlperioden | 12 aus OParl `legislativeTerms` | `belegt` |
| `created`/`modified` | durchgängig 01.01.2000 | technisch, ohne Aussage; nicht dargestellt |

## 4. Entscheidungen für Phase 1–4

- Schrittfolge je Vorlage mit Evidenzstatus wird in der Pipeline erzeugt (`pipeline/process.py`) und in jeden Export geschrieben.
- Zeitleiste: Standardachse Datum der Vorlage, wählbar Sitzungsdatum (gekennzeichnet als abgeleitet); Sitzungsspur aus der städtischen API; Kontextspur aus `legislativeTerms`.
- Gestaltung: Variante „Dichteband mit Brush“ plus Sitzungs- und Auswahlspur; mobil nur Dichte und Brush.
- Nicht umgesetzt: Soll-Modell (Regelwerk-Fassungen ungeklärt), Beschlusskontrolle.
