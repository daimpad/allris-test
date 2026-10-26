# Wohnen und Bauen – Phase 1: Regelentwurf und Prüfbogen (26.10.2026)

**Grundlage:** `phase0/BERICHT.md` mit den Entscheidungen vom 26.10.2026.

**Stand:** Entwurf. `wohnen` steht in `ENTWUERFE`, nicht in `ALLE`: kein Export, keine Seite, bis der Prüfbogen im Gespräch geprüft ist.

## Regeln (`pipeline/themenseiten/wohnen.py`, abgeleitet, je Vorlage mit Grund)
Die erste passende Regel gilt.

0. **Ausschluss:** Sammellisten nichtöffentlicher Punkte, Formalien (Schriftführung, Sitzungstermine), „Miet…“ ohne Wohnbezug (Fahrradmietsystem, Anmietung, Mietzuschuss, mietzinsfreie Veranstaltungen), Wohnmobile; Bühnen und Beethovenhalle (Gebäude der Stadt, Kulturseite).
1. **„Bau-Turbo“ und schnellere Planung:** Titel nennt „Bau-Turbo“, § 36a oder § 246e BauGB, „Planungsturbo“ oder Verfahrensbeschleunigung.
2. **Bebauungspläne:** Titel nennt Bebauungsplan, Flächennutzungsplan, Veränderungssperre, Bauleitplanung oder einen vorhabenbezogenen Plan.
3. **Wohnraum:** Titel nennt Wohnungsbau, Wohnraum, geförderte oder bezahlbare Wohnungen, VEBOWAG, Wohnungsbaugenossenschaft, Mietspiegel, Leerstand, Zweckentfremdung, das Handlungskonzept Wohnen oder Wohnungslosigkeit (auch Housing First).
4. **Denkmalschutz:** Titel nennt Denkmal, Denkmalschutz oder Denkmalbereichssatzung, nicht bei Vorlagen zum Verkehr.
5. **Weitere:** Stadtplanungsamt, Bodenmanagement oder Bauordnungsamt federführend oder Beratung im Ausschuss für Planen, Bauen und Denkmalschutz; nicht bei Vorlagen zum Verkehr (Abteilung Stadtverkehr gehört zum Stadtplanungsamt). Nach Stadtbezirk gegliedert, je Bezirk eingeklappt.

Die Regeln 1 bis 4 gelten unabhängig von Amt und Thema, weil Wohnen oft beim Sozialamt, im Sozialausschuss oder als Antrag über das Ratsbüro läuft.

## Weitere Festlegungen
- **Prozessbild:** nur Beschlüsse und Anträge mit Beratung in Rat, Hauptausschuss, Planungsausschuss oder Sozialausschuss; am 26.10.2026 sind das 97.
- **Bahnen:** Haushalt 2027/2028 oben (`themenseiten/haushalt.py`), darunter Bezirksvertretungen, Planungsausschuss, andere Ausschüsse, Finanzausschuss, Hauptausschuss und Rat.
- **Bebauungspläne auf der Karte:** Die Seite verweist auf die Ebene „Bebauungspläne“ mit Planchronik.

## Erweiterung im allgemeinen Teil (`dossier.py`)
- `ohne_thema`: Eine Regel gilt nicht für Vorlagen mit diesem Thema der Themenzuordnung (hier: Verkehr).

Kultur, Verkehr und Schule bleiben unverändert (Referenztest).

## Stand 26.10.2026
339 Vorlagen:

| Strang | Vorlagen |
|---|---|
| „Bau-Turbo“ und schnellere Planung | 20 |
| Bebauungspläne | 74 |
| Wohnraum | 72 |
| Denkmalschutz | 32 |
| weitere | 141 |

Die 141 weiteren Vorlagen verteilen sich so: Bonn 47, Beuel 18, Bad Godesberg 16, Hardtberg 5, mehrere Stadtbezirke 4, ohne Ortsbezug 51.

## Prüfbogen
`data/export/wohnen/stichprobe_wohnen.tsv`, Schritt `wohnen-stichprobe`; einmal gezogen, danach nicht überschrieben.
- **25 zugeordnete Vorlagen:** je Strang 5. Frage: Passt der Strang?
- **5 nicht zugeordnete Vorlagen** mit Wohnen, Grundstück, Quartier, Stadtentwicklung o. Ä. im Titel (Gegenprobe). Frage: Fehlt die Vorlage auf der Seite?

Erste Auffälligkeiten beim Ziehen:
- Jahresabschlüsse der VEBOWAG stehen unter Wohnraum.
- Anfragen zu Gesellschafterrechten mit „denkmalrechtlichen Verpflichtungen“ stehen unter Denkmalschutz.
- Eine Straßenbenennung steht unter „weitere“, weil das Bauordnungsamt federführend ist.

Vor dem Ziehen wurden drei Lücken geschlossen: Bühnen ausgeschlossen, Denkmalschutz ohne Verkehr, „Handlungskonzept Wohnen“ zu Wohnraum.
