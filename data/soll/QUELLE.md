# Soll-Modell der Prozessebene – Quelle

| Datei | Herkunft | Lizenz |
|---|---|---|
| `verfahren.json` | anster2025/bonn-entscheidet, `data/verfahren.json`, Commit `26641f7` (19.10.2026), unverändert | MIT, © 2026 anster2025 (`LICENSE-bonn-entscheidet`) |
| `zustaendigkeitsordnung.json` | anster2025/bonn-entscheidet, `data/zustaendigkeitsordnung.json`, Commit `26641f7`, unverändert; Inhalt aus der Zuständigkeitsordnung der Ratsausschüsse der Stadt Bonn, Stand 9.7.2026 | MIT (Datei), amtliches Werk (Inhalt) |
| `ergaenzungen.json` | eigene Ergänzungen und Korrekturen der RIS-Karte Bonn mit Belegen | MIT |

Die übernommenen Dateien bleiben unverändert (feste Kopie). Korrekturen und Ergänzungen stehen getrennt in `ergaenzungen.json` und werden beim Laden angewandt (`pipeline/soll.py`). Prüfung vor der Übernahme: `soll/phase0/BERICHT.md`.

Das Soll ist ein vereinfachtes Modell des Regelwerks (Gemeindeordnung NRW, Geschäftsordnung des Rates, Haupt- und Bezirkssatzung, Zuständigkeitsordnung), keine Rechtsauskunft. Maßgeblich sind die jeweils gültigen Fassungen auf bonn.de und recht.nrw.de.
