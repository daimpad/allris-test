# Verkehr und Mobilität – Phase 1: Regelentwurf und Prüfbogen (26.10.2026)

**Grundlage:** `phase0/BERICHT.md` mit den Entscheidungen vom 26.10.2026.

**Stand:** Entwurf. Die Seite ist nicht veröffentlicht: `verkehr` steht in `ENTWUERFE`, nicht in `ALLE`. Deshalb gibt es weder eine Seite noch Daten im Export.

## Regeln (`pipeline/themenseiten/verkehr.py`, abgeleitet, je Vorlage mit Grund)
Die erste passende Regel gilt.

0. **Ausschluss:** Grünpflege an Straßen („Verkehrsgrün“, „Straßenbegleitgrün“ u. Ä.).
1. **Sperrung der Nordbrücke:**
   - Vorlagen, deren Titel die Nordbrücke nennt;
   - ganze Verfahren, wenn schon die Stammvorlage sie nennt.

   Dies gilt auch außerhalb der Themenzuordnung. Ein einzelner Änderungsantrag zieht kein Verfahren mit; so bleibt der Nahverkehrsplan bei Bus und Bahn.
2. **Bus und Bahn:** Thema Verkehr und Mobilität, und der Titel nennt ÖPNV, Bus, Haltestelle, Stadtbahn, Seilbahn, Bahnhof, Fahrplan, Takt, Linie, Ticket o. Ä.
3. **Parken:** Thema, und der Titel nennt Parken, Parkplätze, Parkraum, Gebühren, Halteverbot o. Ä. Fahrradparken zählt nicht dazu.
4. **Rad- und Fußverkehr:** Thema, und der Titel nennt Radverkehr, Radwege, Fahrrad, Gehwege, Zebrastreifen, Querungen, E-Scooter o. Ä.
5. **Weitere:** übrige Vorlagen des Themas, nach Stadtbezirk gegliedert und je Bezirk eingeklappt.

## Weitere Festlegungen
- **Prozessbild:** nur Beschlüsse und Anträge mit Beratung in Rat, Hauptausschuss oder Ausschuss für Mobilität und Verkehr. Am 26.10.2026 sind das 65.
- **Bahnen:** Die Bahn „Haushalt 2027/2028“ steht oben im Bild. Ihre Phasen und Schritte liegen gemeinsam mit Kultur in `themenseiten/haushalt.py`.

## Erweiterungen im allgemeinen Teil (`dossier.py`)
Die Kulturseite bleibt Zeichen für Zeichen gleich; geprüft mit Referenztest und echten Daten. Neu sind:
- eine Regel nach Thema;
- ein Ausschluss über den Titel;
- `nur_stammvorlage` für ganze Verfahren;
- Punkte nur aus bestimmten Gremien;
- Gliederung nach Stadtbezirk;
- Daten eines Entwurfs direkt aus der Datenbank (`entwurf`).

## Stand 26.10.2026
906 Vorlagen:

| Strang | Vorlagen |
|---|---|
| Nordbrücke | 59 |
| Bus und Bahn | 155 |
| Parken | 80 |
| Rad- und Fußverkehr | 192 |
| weitere | 420 |

Die 420 weiteren Vorlagen verteilen sich so: Bonn 150, Beuel 79, Bad Godesberg 61, Hardtberg 19, mehrere Stadtbezirke 10, ohne Ortsbezug 101.

## Prüfbogen
`data/export/verkehr/stichprobe_verkehr.tsv`, Schritt `verkehr-stichprobe`; er wird einmal gezogen und danach nicht überschrieben.
- **24 zugeordnete Vorlagen:** Nordbrücke 4, Bus und Bahn 5, Parken 5, Rad- und Fußverkehr 5, weitere 5. Frage: Passt der Strang?
- **6 nicht zugeordnete Vorlagen** mit Verkehrsbezug im Titel (Gegenprobe). Frage: Fehlt die Vorlage auf der Seite?

Erste Auffälligkeiten beim Ziehen:
- Altglascontainer an einer Bushaltestelle stehen unter Bus und Bahn.
- Das Abwasserbeseitigungskonzept steht unter „weitere“, weil die Themenzuordnung das Tiefbauamt ganz dem Verkehr zurechnet.

Die Prüfung erfolgt im Gespräch wie bei Kultur. Danach werden die Regeln angepasst, und erst dann kommt `verkehr` in `ALLE`.
