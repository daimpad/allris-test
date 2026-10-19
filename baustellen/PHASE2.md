# Phase 2 – Archiv der Baustellen

Stand: 19.10.2026.

## Umsetzung

| Baustein | Datei | Beschreibung |
|---|---|---|
| Abruf | `pipeline/baustellen.py` (`fetch`) | Themen 14403 (tagesaktuell), 14698 (1 Jahr), 14755 (30 Tage); bis zu 10 Versuche; gültig nur als FeatureCollection mit `numberMatched` = Anzahl der Objekte |
| Normalisierung | `normalize` | je `baustelle_id`: Bezeichnung, Stadtbezirk, Adresse, von, bis, Träger, Maßnahme, Sperrung, Punkt (6 Nachkommastellen) |
| Zustand | `update` → `baustellen.json` | erstes und letztes Auftreten, Feeds, aktiv/entfallen, aktuelle Angaben, Änderungen (von, bis, Sperrung, Maßnahme, Träger, Adresse, Bezeichnung) |
| Protokoll | `protokoll.tsv` | neu, geaendert, entfallen, wieder_da, abruf_fehlgeschlagen |
| Momentaufnahmen | `snapshots/JJJJ/MM/TT/` | nur bei geändertem Inhalt (Prüfsumme in `STAND.json`) |
| Betrieb | `.github/workflows/baustellen.yml` | täglich 05:23 UTC und auf Knopfdruck; Ablage im Branch `archiv` mit README |

Schutz vor Fehlschlüssen: Fehlt ein Feed wegen eines Abruffehlers, wird keine Baustelle als entfallen gewertet. Schlägt jeder Feed fehl, endet der Lauf mit Fehler (Benachrichtigung durch GitHub).

## Probelauf (19.10.2026, 10:39 UTC)

48 Baustellen, davon 7 tagesaktuell; ein Feed brauchte zwei Versuche. Ein zweiter Lauf am selben Tag ergab keine Ereignisse und keine neue Momentaufnahme. Umfang des Archivs nach dem ersten Lauf: 88 KB.

## Grenzen

- Die Historie beginnt mit dem ersten Lauf; frühere Baustellen fehlen (Anfrage an die Stadt vorbereitet).
- Termine sind laut Quelle unverbindlich; erfasst sind nur verkehrsrelevante Maßnahmen.
- Noch keine Anzeige und keine Verknüpfung mit Vorlagen (Phase 3 und 4).

## Nächster Schritt

Phase 3: Kandidatenverknüpfung Beschluss ↔ Baustelle (räumlich, zeitlich, thematisch), mit Konfidenz und Prüfung an einer Stichprobe; Freischaltung erst nach ausreichender Trefferquote.
