# Wahlen 2025 – Phase 1: Wahlbeteiligung je Ortsteil (Übergang, 27.10.2026)

**Entscheidung:** Die Kennzahl wird jetzt als Übergang veröffentlicht. Die Dateien der Stadt auf wahlen.bonn.de und die Flächen der Stimmbezirke 2025 auf stadtplan.bonn.de antworten seit dem 22.10.2026 nicht.

## Daten
- **Zahlen:** IT.NRW, endgültige Ergebnisse der Ratswahl nach Stimmbezirken. Daraus kommen nur Wahlberechtigte, davon mit Sperrvermerk „W“, und Wähler, ohne die Stimmen der Parteien. Abgelegt in `data/kontext/wahl2025_stimmbezirke.tsv` mit 177 Urnen- und 65 Briefwahlbezirken. Die Summen gleichen Heft 3 der Stadt: 247.052 Wahlberechtigte, 160.220 Wähler, 64,9 %.
- **Zuordnung:** Straßenverzeichnis zur Kommunalwahl 2020 der Stadt (CC0) mit `data/geo/hausnummern_bonn.json`. Gelesen werden nur Straße, Hausnummernbereich und Stimmbezirk; Wahllokale und Wahlvorstände bleiben außen vor. 58.616 von 58.965 Adressen sind zugeordnet (99,4 %). Ergebnis: `data/kontext/wahl2025_zuordnung.tsv`.
- **Schritt:** `python -m pipeline wahlen-ausschnitt` läuft einmalig, lokal. Den Vermerk trägt `data/kontext/STAND.json` unter dem Schlüssel `wahl2025`, mit dem Hinweis „Übergang“.

## Methode (`pipeline/kontext.py`, `wahlbeteiligung`)
- Je Urnenstimmbezirk zählen die Wähler an der Urne. Dazu kommen die Briefwähler des Wahlbezirks, verteilt im Verhältnis der Wahlberechtigten mit Sperrvermerk „W“.
- Die Gruppen des Straßenverzeichnisses werden anteilig nach Adressen auf die Ortsteile verteilt.
- **Werte:** Ortsteile und Stadtbezirke sind geschätzt und auf ganze Prozent gerundet. Ganz Bonn ist amtlich (64,9 %).
- **Ohne Wert:** Beuel-Ost, Hardthöhe und Hoholz haben keinen eigenen Stimmbezirk, das heißt keinen, dessen Adressen überwiegend im Ortsteil liegen.
- **Audit:** `export/audit_wahlbeteiligung.tsv` enthält je Gruppe Wahlberechtigte, Wähler an der Urne, zugeteilte Briefwähler, Schätzung, Hauptortsteil und weitere Ortsteile.
- **Prüfung in `check`:** Ganz Bonn muss den amtlichen Wert ergeben, Ortsteile müssen zwischen 20 und 95 % liegen.

## Ergebnis
- **Spanne der Ortsteile:** 40 bis 78 %, wie in Phase 0 (39,7 bis 77,6 %).
- **Stadtbezirke:** Bad Godesberg 63 %, Beuel 69 %, Bonn 65 %, Hardtberg 59 %. Zur Gegenprobe meldet IT.NRW für die Wahlen der Bezirksvertretungen Bonn 64,8 % und Hardtberg 59,2 %.

## Anzeige
- **Liste und Karte:** „Zahlen zu …“ in der Liste und die Flächenfarbe „Wahlbeteiligung Ratswahl 2025“ (`flaechen=kontext-wahlbeteiligung`). Bei fehlendem Wert steht „ohne eigenen Stimmbezirk“.
- **Assistent:** `hole_kontext` liefert die Kennzahl mit dem Hinweis auf den Übergang. Der Systemprompt v0.7 verlangt, sie als geschätzt zu nennen und keine Schlüsse auf Parteien oder Bewohner zu ziehen.
- Keine Ergebnisse der Parteien je Gebiet (Entscheidung 27.10.2026).

## Grenzen und nächster Schritt
- **Schätzfehler:** bis etwa 3 Prozentpunkte. Adressen sind nicht dasselbe wie Wahlberechtigte, und die Grenzen der Stimmbezirke 2025 können von 2020 abweichen. Die Nummern sind gleich (177/177).
- **Wenn die Stadt wieder liefert:** `quellen.yml` versucht es montags erneut. Liegen Dateien und Flächen 2025 vor, werden die Zahlen gegen die Stadt geprüft, die Zuordnung über die Flächen 2025 und die Zensus-Einwohner neu gebildet und die Quelle getauscht.
