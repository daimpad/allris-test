# Prompt: Bebauungspläne und Baustellen in allris-bonn einbinden

> Entwurf v0.1 (17.10.2026) · Kontext: Hackathon „Hack den Stadtrat“ · Zur Ausführung in Claude Code
> Ergänzt `PROMPT_allris-bonn_v0.3.md` (Geokodierung 5.2), `PROMPT_prozessebene_v0.1.md` (Evidenzstatus), `PROMPT_zeitleiste_v0.1.md` und `PROMPT_chatbot_byok_v0.1.md`.

---

## 1. Rolle und Arbeitsweise

Du arbeitest als Entwickler:in mit Erfahrung in Geodaten, Open-Data-Pipelines und Datenverknüpfung. Du arbeitest quellentreu: Jede Verknüpfung zwischen einer Vorlage und einem Bebauungsplan oder einer Baustelle trägt Methode, Konfidenz und Fundstelle. Eine räumliche oder zeitliche Nähe ist ein Hinweis, kein Beleg. Vor jeder Phase (Abschnitt 7) legst Du einen kurzen Plan vor und wartest auf Freigabe. Ressourcen-URLs, Felder und Formate ermittelst Du aus den Quellen, nicht aus Annahmen.

## 2. Ziel

Zwei städtische Datensätze werden eingebunden, die je eine Lücke schließen:

| Datensatz | Lücke | Nutzen |
|---|---|---|
| **Lage der Bebauungspläne** | Stufe B der Geokodierung ist bei Planungsvorlagen ungenau (mehrdeutige Straßennamen) | Vorlagen mit Bebauungsplan-Bezug werden der Planfläche zugeordnet; Chronik der Vorlagen je Plan |
| **Baustellen** (tagesaktuell; geplant für 30 Tage bzw. 1 Jahr) | Vollzug von Beschlüssen ist bisher `unklar` | Baustellen als **Indiz** für die Umsetzung von Tiefbau- und Verkehrsbeschlüssen |

## 3. Datenquellen (Stand 17.10.2026, in Phase 0 zu prüfen)

**Lage der Bebauungspläne** (opendata.bonn.de/dataset/lage-der-bebauungspläne)
- Laut Beschreibung liefert die API Planumrisse mit Links zum Bebauungsplan und zur Begründung; Aktualisierung laut Metadaten täglich.
- Zu ermitteln: Ressourcen-URL, Format (vermutlich GeoJSON über stadtplan.bonn.de), Felder (Plannummer, Bezeichnung, Verfahrensstand, Rechtskraftdatum?), Bezug zu aufgehobenen oder geänderten Plänen.

**Baustellen tagesaktuell mit Ortsangabe** (opendata.bonn.de/dataset/baustellen-tagesaktuell-mit-ortsangabe-bonn)
- Laut Beschreibung Baumaßnahmen verschiedener Bauherren, beschränkt auf solche mit nennenswertem Einfluss auf den Verkehr.

**Geplante Straßenbaustellen 30 Tage und 1 Jahr mit Ortsangabe** (opendata.bonn.de/dataset/geplante-straßenbaustellen-30-tage-und-1-jahr-mit-ortsangabe-bonn)
- Laut Beschreibung Masterplan des Baustellenmanagements des Tiefbauamts: größere Tiefbaumaßnahmen ab einer Woche Dauer oder mit verkehrlicher Bedeutung.

Für beide Baustellendatensätze gilt:
- Termine für Baubeginn und Bauende sind laut Quelle **nicht verbindlich**.
- Zu ermitteln: Felder (Bauherr, Maßnahme, Zeitraum, Geometrie als Punkt oder Linie), ob eine stabile ID existiert, ob historische Stände abrufbar sind (vermutlich nicht).

**Lizenz:** Auf opendata.bonn.de für die übrigen Geodaten CC0. Auf open.nrw werden Bonner Datensätze teils als „non_open“ geführt, auch solche, die im Quellportal CC0 sind. Lizenz je Datensatz im Quellportal festhalten; Unklarheiten in die Liste offener Punkte aufnehmen.

## 4. Teil A: Bebauungspläne

**Verknüpfung Vorlage ↔ Plan**
- **B3 (neue Methode):** Plannummern aus Titel und, soweit verfügbar, Volltext extrahieren. Das Nummernschema der Stadt Bonn leitest Du aus den Plandaten ab und prüfst es gegen Vorlagentitel; Du setzt es nicht voraus.
- Ein eindeutiger Treffer auf eine vorhandene Plannummer ergibt Konfidenz **hoch**. Mehrdeutige oder nur teilweise passende Treffer werden mit **niedrig** markiert und zur Prüfung vorgemerkt.
- **Räumliche Ergänzung:** Punkte aus Stufe A, die in einer Planfläche liegen, werden als räumliche Überlagerung vermerkt. Das ist eine Überlagerung, keine inhaltliche Zuordnung, und so zu benennen.
- Bei Vorlagen mit Plannummer gilt die Planfläche als Verortung und hat Vorrang vor Straßentreffern (B2). Abweichungen zwischen B2 und B3 werden im Audit ausgewiesen.

**Planchronik**
- Je Plan werden alle verknüpften Vorlagen chronologisch dargestellt (Anknüpfung an Prozessebene und Zeitleiste).
- Die gesetzlichen Verfahrensschritte der Bauleitplanung nach BauGB (u. a. Aufstellungsbeschluss, Beteiligung der Öffentlichkeit, Satzungsbeschluss) können als **Soll**-Schritte modelliert werden. Jeder Schritt erhält eine Fundstelle (Paragraph). Die Zuordnung einer Vorlage zu einem Verfahrensschritt erfolgt über Vorlagenart bzw. Titelmuster und ist `abgeleitet`.
- Verfahrensschritte ohne zugeordnete Vorlage erscheinen als `soll` bzw. `unklar`, nicht als erledigt.

**Darstellung**
- Planflächen als eigener, abschaltbarer Kartenlayer; Detailansicht mit Links zu Plan und Begründung (aus der Quelle) und der Liste verknüpfter Vorlagen.

## 5. Teil B: Baustellen als Vollzugsindiz

**Archivierung (Voraussetzung)**
- Die APIs liefern voraussichtlich nur aktuelle bzw. künftige Stände. Ein täglicher Abruf (z. B. GitHub Actions) speichert Momentaufnahmen mit Abrufdatum. Der historische Bestand beginnt mit dem ersten Abruf; das wird in der Oberfläche benannt.
- Änderungen einer Baustelle über die Zeit (Termine verschoben, entfallen) werden aus den Momentaufnahmen abgeleitet und protokolliert.

**Verknüpfung Beschluss ↔ Baustelle (Kandidaten)**
- Drei Kriterien, einzeln ausgewiesen:
  - räumlich: Abstand bzw. Überschneidung mit der Verortung der Vorlage, Puffer begründen;
  - zeitlich: Baustelle beginnt nach dem Beschluss;
  - thematisch: federführendes Amt (z. B. Tiefbauamt), Stichworte, gegebenenfalls Bauherr.
- Daraus ergibt sich ein **Kandidatenstatus mit Konfidenz**, niemals die Aussage „umgesetzt“. Darstellung als „mögliche Umsetzung“ mit Begründung, welche Kriterien erfüllt sind.
- Baustellen fremder Bauherren (z. B. Versorgungsunternehmen) werden, soweit das Feld vorhanden ist, getrennt behandelt, da sie in der Regel keinen Ratsbeschluss umsetzen.
- Eine manuelle Prüfung einer Stichprobe (z. B. 30 Kandidaten) gegen ALLRIS bzw. Pressemitteilungen bestimmt, ob die Kandidatenlogik trägt. Ohne ausreichende Trefferquote wird die Funktion nicht freigeschaltet.

**Darstellung**
- Baustellen als Kartenlayer (aktuell und geplant unterscheidbar).
- Auf der Zeitleiste als eigene Spur mit Zeiträumen. Unverbindliche Termine werden mit unscharfen Rändern oder einer anderen Linienart gezeichnet.
- In der Prozesslinie erscheint optional eine Station „mögliche Umsetzung“ mit Status `abgeleitet`; der Status `unklar` für den Vollzug bleibt daneben bestehen.

## 6. Anbindung an die übrigen Ebenen

- **Geokodierung:** B3 wird in das Audit-TSV aufgenommen (Methode, Konfidenz, Fundstelle).
- **Chatbot:** Zwei zusätzliche Werkzeuge (`suche_bebauungsplan`, `suche_baustellen`) liefern Ergebnisse mit Evidenzstatus. Der Systemprompt wird ergänzt: Baustellen nie als Beleg für Umsetzung darstellen.
- **Transparenz:** Im Hinweisbereich wird ergänzt, dass Baustellendaten unverbindlich sind, die Historie erst ab Archivbeginn vorliegt und Verknüpfungen auf Indizien beruhen.

## 7. Vorgehen (nach jeder Phase Rückfrage)

0. **Prüfung:**
   - Ressourcen-URLs, Felder, Geometrietypen, IDs und Aktualität beider Datensätze ermitteln.
   - Nummernschema der Bebauungspläne und dessen Vorkommen in Vorlagentiteln auswerten (Anzahl Treffer stadtweit und für Endenich).
   - Prüfen, ob Baustellen einen Bauherrn bzw. Träger ausweisen.
   - Bericht mit Mengengerüst und Empfehlung.
1. **Bebauungspläne:** Abruf, Normalisierung, B3-Verknüpfung, Audit-TSV; Prüfung an einer Stichprobe aus Endenich.
2. **Baustellenarchiv:** täglicher Abruf mit Momentaufnahmen und Änderungsprotokoll.
3. **Kandidatenverknüpfung:** Regeln, Konfidenz, Stichprobenprüfung; Entscheidung über Freischaltung nach Vorlage der Ergebnisse.
4. **Darstellung:** Kartenlayer, Zeitleistenspur, Planchronik, Werkzeuge für den Chatbot.
5. **Auslieferung:** Audit-TSVs (B3-Zuordnung; Baustellenkandidaten mit Kriterien und Prüfvermerk), Lizenzhinweise, Ergebnis als Zip-Paket.

## 8. Offene Punkte

- Ressourcen-URLs und Felder beider Datensätze
- Nummernschema der Bonner Bebauungspläne und Umgang mit Änderungsplänen
- Ob ein Bauherr bzw. Träger in den Baustellendaten erfasst ist
- Ob die Stadt historische Baustellendaten bereitstellen kann (Anfrage an opendata@bonn.de)
- Schwelle für die Freischaltung der Kandidatenverknüpfung
- Lizenzbestätigung je Datensatz
