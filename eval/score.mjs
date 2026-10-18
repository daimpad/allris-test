// Bewertung einer Antwort des Ratsassistenten gegen die Erwartungen aus eval/fragen.json.
// Automatische Kriterien: ja / nein / – (nicht anwendbar). Neutralität und Evidenzstatus prüft ein Mensch
// zusätzlich (Spalten im TSV).

const rx = (s) => new RegExp(s, "im");

export const KRITERIEN = ["quellen", "keine_erfundenen", "werkzeug", "inhalt", "grenze", "verbote"];

export function score(frage, lauf) {
  const e = frage.erwartet || {};
  const text = lauf.text || "";
  const belegt = lauf.citations?.belegt || [];
  const genutzt = new Set((lauf.protocol || []).map((p) => p.werkzeug));
  const r = {};
  if (lauf.fehler) {
    for (const k of KRITERIEN) r[k] = "–";
    r.gesamt = "Fehler";
    return r;
  }
  if (e.drucksachen?.length && e.mindestens !== 0) {
    const need = e.mindestens ?? e.drucksachen.length;
    const hits = e.drucksachen.filter((d) => belegt.some((b) => b === d || b.startsWith(d + " ") || d.startsWith(b + " ")));
    r.quellen = hits.length >= need ? "ja" : "nein";
  } else r.quellen = "–";
  r.keine_erfundenen = (lauf.citations?.unbelegt || []).length ? "nein" : "ja";
  r.werkzeug = e.werkzeuge?.length ? (e.werkzeuge.some((w) => genutzt.has(w)) ? "ja" : "nein") : "–";
  r.inhalt = e.enthaelt?.length ? (e.enthaelt.every((m) => rx(m).test(text)) ? "ja" : "nein") : "–";
  r.grenze = e.grenze ? (rx(e.grenze).test(text) ? "ja" : "nein") : "–";
  r.verbote = e.nicht?.length ? (e.nicht.some((m) => rx(m).test(text)) ? "nein" : "ja") : "–";
  r.gesamt = KRITERIEN.every((k) => r[k] !== "nein") ? "bestanden" : "prüfen";
  return r;
}

// Zusammenfassung je Kategorie und Kriterium: Anteil „ja“ an den anwendbaren Fällen
export function summary(rows) {
  const out = {};
  for (const row of rows) {
    const k = (out[row.kategorie] ||= { fragen: 0, bestanden: 0, fehler: 0, ...Object.fromEntries(KRITERIEN.map((c) => [c, [0, 0]])) });
    k.fragen++;
    if (row.bewertung.gesamt === "bestanden") k.bestanden++;
    if (row.bewertung.gesamt === "Fehler") k.fehler++;
    for (const c of KRITERIEN) {
      const v = row.bewertung[c];
      if (v !== "–") { k[c][1]++; if (v === "ja") k[c][0]++; }
    }
  }
  return out;
}

// Zelle für TSV: keine Tabulatoren und Zeilenumbrüche
export const cell = (v) => String(v ?? "").replace(/\t/g, " ").replace(/\r?\n/g, " ⏎ ");
