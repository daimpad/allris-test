# Klima und Umwelt – Phase 1: Regelentwurf und Prüfbogen (26.10.2026)

**Grundlage:** `phase0/BERICHT.md` mit den Entscheidungen vom 26.10.2026.

**Stand:** Entwurf. `klima` steht in `ENTWUERFE`, nicht in `ALLE`: kein Export, keine Seite, bis der Prüfbogen im Gespräch geprüft ist.

## Regeln (`pipeline/themenseiten/klima.py`, abgeleitet, je Vorlage mit Grund)
Die erste passende Regel gilt. Keine Regel gilt für Vorlagen mit dem Thema Verkehr (`ohne_thema`); sie bleiben auf der Verkehrsseite.

0. **Ausschluss:** Sammellisten nichtöffentlicher Punkte, Schriftführung, Sitzungstermine.
1. **Klimaschutz und Energie:** Titel nennt Klimaschutz, Klimaplan, Klimaneutralität (nicht das Sondervermögen „Infrastruktur und Klimaneutralität“), Klimabeirat, CO2, Wärmeplanung, Solar, Photovoltaik, Fernwärme, Windenergie oder Energieeinsparung.
2. **Klimaanpassung:** Titel nennt Klimaanpassung, Hitze, Starkregen, Hochwasser, Überschwemmung, Entsiegelung, Trinkbrunnen, kühle Orte oder Regenwasser.
3. **Bäume, Grün und Natur:** Titel nennt Bäume (nicht „Baumaßnahme“), Fällungen, Grünflächen, Parkanlagen, Naturschutz, Biotope, Wald, Kleingärten, Begrünung, Artenschutz, den Freiraumplan oder die Rheinaue.
4. **Abfall und Sauberkeit:** Titel nennt Abfall, Müll, Sauberkeit, Wertstoffe, Glascontainer, Verpackung, Mehrweg, Straßenreinigung oder bonnorange.
5. **Weitere:** Amt für Umwelt und Stadtgrün federführend oder Beratung im Umweltausschuss oder Naturschutzbeirat; darunter Lärm, Luft und Friedhöfe. Nach Stadtbezirk gegliedert, je Bezirk eingeklappt.

## Weitere Festlegungen
- **Prozessbild:** nur Beschlüsse und Anträge mit Beratung in Rat, Hauptausschuss oder Umweltausschuss; am 26.10.2026 sind das 79.
- **Bahnen:** Haushalt 2027/2028 oben (`themenseiten/haushalt.py`), darunter Bezirksvertretungen, Umweltausschuss, andere Ausschüsse, Finanzausschuss, Hauptausschuss und Rat.
- **Karte:** Die Seite verweist auf die Färbung der Gebiete nach Hitze (`?flaechen=kontext-hitze`) und auf die Ebene Überschwemmungsgebiete (`?ebenen=uesg`).

Der allgemeine Teil (`dossier.py`) bleibt unverändert.

## Stand 26.10.2026
403 Vorlagen:

| Strang | Vorlagen |
|---|---|
| Klimaschutz und Energie | 41 |
| Klimaanpassung | 26 |
| Bäume, Grün und Natur | 139 |
| Abfall und Sauberkeit | 40 |
| weitere | 157 |

Die 157 weiteren Vorlagen verteilen sich so: Bonn 28, Bad Godesberg 23, Hardtberg 9, Beuel 7, mehrere Stadtbezirke 3, ohne Ortsbezug 87.

## Prüfbogen
`data/export/klima/stichprobe_klima.tsv`, Schritt `klima-stichprobe`; einmal gezogen, danach nicht überschrieben.
- **25 zugeordnete Vorlagen:** je Strang 5. Frage: Passt der Strang?
- **5 nicht zugeordnete Vorlagen** mit Klima, Umwelt, Natur, Energie, Lärm, Nachhaltigkeit o. Ä. im Titel (Gegenprobe). Frage: Fehlt die Vorlage auf der Seite?

Erste Auffälligkeiten beim Ziehen:
- Ein Zustimmungsbeschluss nach § 36a BauGB steht unter „weitere“, weil auch der Umweltausschuss berät.
- Toiletten am Eingang der Rheinaue stehen unter „Bäume, Grün und Natur“.
- Die Gegenprobe enthält zwei Vorlagen zu Lärm im Verkehr; sie fehlen, weil Verkehr ausgeschlossen ist.

Die Gegenprobe wurde vor der Prüfung zweimal neu gezogen: „Grün“ traf den Parteinamen, „Tier“ traf „Quartier“, „Wasser“ und „Garten“ trafen Ortsnamen. Vor dem Ziehen wurde das Sondervermögen „Infrastruktur und Klimaneutralität“ aus dem Klimaschutz genommen.
