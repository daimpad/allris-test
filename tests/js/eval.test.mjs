// Auswertung: Fragenkatalog (Aufbau, Werkzeugnamen, gültige Muster, erwartete Drucksachen in den Daten) und Bewertung
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile, access } from "node:fs/promises";
import { score, summary, cell } from "../../eval/score.mjs";
import { TOOLS, createTools } from "../../site/chat/tools.js";

const ROOT = new URL("../../", import.meta.url);
const KATALOG = JSON.parse(await readFile(new URL("eval/fragen.json", ROOT), "utf8"));

test("Fragenkatalog: mindestens 30 Fragen, eindeutig, alle Kategorien belegt", () => {
  const { fragen, meta } = KATALOG;
  assert.ok(fragen.length >= 30);
  assert.equal(new Set(fragen.map((f) => f.id)).size, fragen.length);
  for (const k of Object.keys(meta.kategorien)) assert.ok(fragen.filter((f) => f.kategorie === k).length >= 3, k);
  const names = new Set(TOOLS.map((t) => t.name));
  for (const f of fragen) {
    assert.ok(meta.kategorien[f.kategorie], f.id);
    for (const w of f.erwartet.werkzeuge || []) assert.ok(names.has(w), `${f.id}: ${w}`);
    for (const m of [...(f.erwartet.enthaelt || []), ...(f.erwartet.nicht || []), ...(f.erwartet.grenze ? [f.erwartet.grenze] : [])]) new RegExp(m, "im");
    assert.ok(Object.keys(f.erwartet).length, `${f.id}: keine Erwartung`);
  }
});

test("Bewertung: Kriterien ja / nein / –", () => {
  const frage = { erwartet: { drucksachen: ["261798", "261798-01"], mindestens: 1, werkzeuge: ["hole_prozesslinie"], enthaelt: ["abgelehnt"], grenze: "Datenstand", nicht: ["war richtig"] } };
  const gut = score(frage, { text: "261798 wurde abgelehnt (Datenstand 18.10.2026).", protocol: [{ werkzeug: "hole_prozesslinie" }], citations: { belegt: ["261798-01 ST"], unbelegt: [] } });
  assert.deepEqual(gut, { quellen: "ja", keine_erfundenen: "ja", werkzeug: "ja", inhalt: "ja", grenze: "ja", verbote: "ja", gesamt: "bestanden" });
  const schlecht = score(frage, { text: "Die Ablehnung war richtig, siehe 123456.", protocol: [], citations: { belegt: [], unbelegt: ["123456"] } });
  assert.deepEqual(schlecht, { quellen: "nein", keine_erfundenen: "nein", werkzeug: "nein", inhalt: "nein", grenze: "nein", verbote: "nein", gesamt: "prüfen" });
  assert.equal(score(frage, { fehler: "401", protocol: [] }).gesamt, "Fehler");
  assert.equal(score({ erwartet: {} }, { text: "x", protocol: [], citations: { belegt: [], unbelegt: [] } }).quellen, "–");
  const s = summary([{ kategorie: "fakten", bewertung: gut }, { kategorie: "fakten", bewertung: schlecht }]);
  assert.equal(s.fakten.bestanden, 1);
  assert.deepEqual(s.fakten.quellen, [1, 2]);
  assert.equal(cell("a\tb\nc"), "a b ⏎ c");
});

const REAL = await access(new URL("data/export/bonn/chat/datenstand.json", ROOT)).then(() => true, () => false);

test("Erwartete Drucksachen sind in den Daten enthalten", { skip: !REAL && "kein Export unter data/export/bonn" }, async () => {
  const t = createTools({ load: async (p) => JSON.parse(await readFile(new URL(`data/export/${p}`, ROOT), "utf8")) });
  const refs = [...new Set(KATALOG.fragen.flatMap((f) => f.erwartet.drucksachen || []))];
  for (const r of refs) assert.ok(!(await t.run("hole_vorlage", { drucksache: r })).fehler, r);
  assert.ok((await t.run("hole_vorlage", { drucksache: "999999" })).fehler);
});
