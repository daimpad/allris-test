# Haushalt – Phase 1: Auslesung und Abschnitt auf den Themenseiten (27.10.2026)

**Auslesung** (`python -m pipeline haushalt-ausschnitt`, einmalig, lokal mit `pdftotext`): je Ausgabe (2023/2024, 2025/2026) die 17 Teilergebnispläne der Produktbereiche und der Gesamtergebnisplan von bonn.de. Gelesen werden die Zeilen 10 (ordentliche Erträge), 17 (ordentliche Aufwendungen) und 18 (ordentliches Ergebnis) mit den Spalten des Tabellenkopfs; die Finanzplanung (Spalten „Planung“) wird nicht übernommen. Ergebnis: `data/haushalt/produktbereiche.tsv` (510 Werte mit Datei und Seite), `data/haushalt/STAND.json` (Adressen, Prüfsummen der PDF).

**Prüfung:** Je Ausgabe und Spalte trifft die Summe der 17 Produktbereiche den Gesamtergebnisplan auf höchstens 9 € (Rundung); eine Abweichung über 1.500 € bricht die Auslesung ab. Eine Zeile mit einer anderen Zahl von Werten als Spalten (leere Zelle) bricht ebenfalls ab.

**Themenseiten:** Abschnitt „Haushalt im Produktbereich“ mit Ergebnis (Ist) 2022 und 2023 aus dem Haushaltsplan 2025/2026 und Ansatz (Plan) des jeweiligen Haushaltsjahres 2023–2026 aus der Ausgabe des Doppelhaushalts, in Mio. € ohne Preisbereinigung, mit Seite und Link auf das PDF. Hinweise: Produktbereich und Thema decken sich nicht genau; interne Leistungen und Umgliederungen; keine Beträge je Vorlage; Entwurf 2027/2028 noch nicht eingebracht.

**Freigabe:** Prüfbogen `data/export/haushalt/pruefbogen_haushalt.tsv` (30 Werte, je Wert mit Fundstelle) im Gespräch am 27.10.2026 vorgelegt und vom Auftraggeber freigegeben (`haushaltsplan.FREIGEGEBEN`); Grundlage: Prüfsumme gegen den Gesamtergebnisplan und Abgleich mit Phase 0.

**Lizenz:** Die Stadt nennt für die PDF keine Lizenz. Der Haushaltsplan ist Teil der Haushaltssatzung; als amtliches Werk nach § 5 UrhG dürfte er frei sein (Einschätzung, keine gesicherte Auskunft). Quelle und Abrufdatum werden genannt.
