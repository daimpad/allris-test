// Soll-Modell Phase 4: Stichprobe von 30 Vorgängen zur Prüfung von Hand (Zuordnung, Befund, Mitwirkung).
// Auswahl geschichtet mit festem Startwert aus data/export/audit_soll.tsv; Angaben je Vorgang über die Werkzeuge
// des Assistenten (site/chat/tools.js: Titel ohne Hausnummern, Soll, Mitwirkung) zum Stichtag. Die Datei wird nie
// überschrieben. Aufruf nach `python -m pipeline export soll`: node soll/phase4/stichprobe.mjs [Stichtag]
import { readFile, writeFile, access, mkdir } from "node:fs/promises";
import { createTools } from "../../site/chat/tools.js";

const ROOT = new URL("../../", import.meta.url);
const OUT = new URL("data/export/soll/stichprobe_soll.tsv", ROOT);
const STICHTAG = process.argv[2] || "2026-10-19";
if (await access(OUT).then(() => true, () => false)) { console.log(`${OUT.pathname} besteht, bleibt unverändert`); process.exit(0); }

let seed = 20261019;  // fester Startwert
const rnd = () => ((seed = (seed * 1103515245 + 12345) % 2 ** 31) / 2 ** 31);
const pick = (arr, n) => { const a = [...arr], out = []; while (a.length && out.length < n) out.push(a.splice(Math.floor(rnd() * a.length), 1)[0]); return out; };

const [head, ...lines] = (await readFile(new URL("data/export/audit_soll.tsv", ROOT), "utf8")).trim().split("\n");
const cols = head.split("\t");
const rows = lines.map((l) => Object.fromEntries(l.split("\t").map((v, i) => [cols[i], v])));
const chosen = new Map();
const add = (list, grund) => { for (const r of list) if (!chosen.has(r.stammnummer)) chosen.set(r.stammnummer, { ...r, auswahl: grund }); };
add(rows.filter((r) => r.passung === "weicht ab"), "Befund (alle)");
add(pick(rows.filter((r) => r.passung === "ohne Soll"), 1), "ohne Soll");
add(pick(rows.filter((r) => r.passung === "nur Beirat"), 2), "nur Beirat");
for (const v of [...new Set(rows.map((r) => r.verfahren).filter(Boolean))].sort()) add(pick(rows.filter((r) => r.verfahren === v && r.passung === "passt"), 1), `je Verfahren: ${v}`);
add(pick(rows.filter((r) => r.sicherheit === "mittel" && !chosen.has(r.stammnummer)), 4), "Sicherheit mittel");
add(pick(rows.filter((r) => r.jahr >= "2025" && !chosen.has(r.stammnummer)), 30 - chosen.size), "zufällig ab 2025");

const tools = createTools({ today: STICHTAG, load: async (p) => JSON.parse(await readFile(new URL(`data/export/${p}`, ROOT), "utf8")) });
const clean = (s) => String(s ?? "").replace(/[\t\n\r]+/g, " ").trim();
// Hausnummern in allen Titeln auslassen (auch Grundstücksadressen in Verwaltungsvorlagen; Datenschutz)
const ohneNr = (t) => t.replace(/((?:straße|strasse|str\.|weg|platz|gasse|allee|ring|ufer|damm|pfad)\s+)\d+\s*[a-z]?\b(\s*[-–]\s*\d+\s*[a-z]?\b)?/giu, "$1[Hausnummer ausgelassen]");
const out = [];
for (const r of chosen.values()) {
  const v = await tools.run("hole_vorlage", { drucksache: r.stammnummer });
  const p = await tools.run("hole_prozesslinie", { drucksache: r.stammnummer });
  const s = p.soll_nach_regelwerk || {};
  const beratungen = (p.schritte || []).filter((x) => x.schritt === "Beratung" || x.schritt === "Entscheidung")
    .map((x) => `${x.bezeichnung}${x.rolle ? ` (${x.rolle})` : ""}${x.ergebnis ? `: ${x.ergebnis}` : ""}${x.datum ? ` ${x.datum}` : ""}`).join("; ");
  out.push({
    auswahl: r.auswahl, stammnummer: r.stammnummer, jahr: r.jahr, art: r.typ, titel: v.fehler ? "" : ohneNr(clean(v.titel)),
    stand: p.stand ?? "", beratungen: clean(beratungen), verfahren: s.verfahren ?? "", sicherheit: r.sicherheit, grund: r.grund,
    gremien_ist: r.ist_bahnen, gremien_soll: r.soll_bahnen, passung: r.passung, befund: clean(s.befund),
    mitwirken_status: s.mitwirken_einordnung ? [s.mitwirken_einordnung.status, s.mitwirken_einordnung.abschluss].filter(Boolean).join(" / ") : "",
    mitwirken_hinweise: clean((s.mitwirken || []).map((m) => m.hinweis.split(/[.;:]/)[0]).join(" | ")),
    ratsinformationssystem: v.links?.ratsinformationssystem ?? "",
    pruef_verfahren: "", pruef_befund: "", pruef_mitwirken: "", pruefvermerk: "ungeprüft",
  });
}
out.sort((a, b) => a.stammnummer.localeCompare(b.stammnummer));
await mkdir(new URL("data/export/soll/", ROOT), { recursive: true });
const keys = Object.keys(out[0]);
await writeFile(OUT, [keys.join("\t"), ...out.map((o) => keys.map((k) => clean(o[k])).join("\t"))].join("\n") + "\n");
console.log(`Stichprobe: ${out.length} Vorgänge zum Stichtag ${STICHTAG} → ${OUT.pathname}`);
