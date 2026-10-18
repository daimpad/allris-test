#!/usr/bin/env node
// Auswertung des Ratsassistenten mit echten Anbietern (Node 22, ohne Abhängigkeiten).
// Nutzt dieselben Werkzeuge, denselben Chat-Kern, dieselben Adapter und denselben Systemprompt wie die Seite.
//
// Aufruf:
//   ANTHROPIC_API_KEY=… node eval/run.mjs --anbieter anthropic --modell claude-opus-5-5
//   MISTRAL_API_KEY=…   node eval/run.mjs --anbieter mistral --modell mistral-medium-latest
// Optionen:
//   --fragen F01,P01       nur diese Fragen
//   --daten <pfad|url>     Exporte (Standard: data/export/, sonst die veröffentlichte Seite)
//   --heute JJJJ-MM-TT     Bezugstag für „kommende Sitzungen“ (Standard: heute in Bonn)
//   --aus <ordner>         Ablage der Ergebnisse (Standard: eval/ergebnisse)
//   --pause <ms>           Pause zwischen Fragen (Standard: 1500)
// Der Schlüssel wird nur aus der Umgebung gelesen und nirgends gespeichert oder ausgegeben.
import { readFile, writeFile, mkdir, access } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { TOOLS, createTools } from "../site/chat/tools.js";
import { createChat } from "../site/chat/core.js";
import { PROVIDERS } from "../site/chat/providers.js";
import { extractPrompt, fillPrompt, promptValues, version } from "../site/chat/prompt.js";
import { score, summary, cell, KRITERIEN } from "./score.mjs";

const ROOT = new URL("../", import.meta.url);
const LIVE = "https://daimpad.github.io/allris-test/data/export/";
const ENV_KEY = { anthropic: "ANTHROPIC_API_KEY", mistral: "MISTRAL_API_KEY", openrouter: "OPENROUTER_API_KEY", lokal: "LOKAL_API_KEY" };

function args(argv) {
  const a = {};
  for (let i = 0; i < argv.length; i++) if (argv[i].startsWith("--")) a[argv[i].slice(2)] = argv[i + 1]?.startsWith("--") || argv[i + 1] == null ? true : argv[++i];
  return a;
}

async function dataLoader(source) {
  if (/^https?:\/\//.test(source)) {
    const base = source.endsWith("/") ? source : source + "/";
    return async (p) => { const r = await fetch(base + p); if (!r.ok) throw new Error(`HTTP ${r.status} ${p}`); return r.json(); };
  }
  const dir = new URL(source.endsWith("/") ? source : source + "/", ROOT);
  return async (p) => JSON.parse(await readFile(new URL(p, dir), "utf8"));
}

const berlinToday = () => new Intl.DateTimeFormat("sv-SE", { timeZone: "Europe/Berlin" }).format(new Date());
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function main() {
  const a = args(process.argv.slice(2));
  const anbieter = a.anbieter || "anthropic";
  if (!PROVIDERS[anbieter]) throw new Error(`Unbekannter Anbieter „${anbieter}“ (${Object.keys(PROVIDERS).join(", ")}).`);
  const modell = typeof a.modell === "string" ? a.modell : PROVIDERS[anbieter].models[0];
  if (!modell) throw new Error(`Bitte mit --modell ein Modell angeben; für ${anbieter} gibt es keine Voreinstellung.`);
  const key = process.env[ENV_KEY[anbieter]] || "";
  if (!key && !PROVIDERS[anbieter].keyOptional) throw new Error(`Bitte den Schlüssel in der Umgebungsvariablen ${ENV_KEY[anbieter]} setzen.`);
  const local = await access(new URL("data/export/bonn/chat/datenstand.json", ROOT)).then(() => true, () => false);
  const quelle = a.daten || (local ? "data/export/" : LIVE);
  const load = await dataLoader(quelle);
  const heute = a.heute || berlinToday();
  const pause = Number(a.pause ?? 1500);

  const katalog = JSON.parse(await readFile(new URL("eval/fragen.json", ROOT), "utf8"));
  const auswahl = a.fragen ? new Set(String(a.fragen).split(",")) : null;
  const fragen = katalog.fragen.filter((f) => !auswahl || auswahl.has(f.id));

  const md = await readFile(new URL("site/chat/systemprompt.md", ROOT), "utf8");
  const status = await load("bonn/chat/datenstand.json");
  const system = fillPrompt(extractPrompt(md), promptValues(status, new Date(`${heute}T12:00:00Z`)));
  const promptVersion = version(md);
  const tools = createTools({ load, today: heute });

  const stamp = new Date().toISOString().slice(0, 16).replace(/[:T]/g, "-");
  const outDir = new URL((a.aus || "eval/ergebnisse").replace(/\/?$/, "/"), ROOT);
  await mkdir(outDir, { recursive: true });
  const name = `${stamp}_${anbieter}_${modell.replace(/[^\w.-]+/g, "-")}`;
  console.log(`Auswertung: ${fragen.length} Fragen · ${anbieter} · ${modell} · Prompt v${promptVersion} · Daten ${quelle} · heute ${heute}`);

  const rows = [];
  for (const f of fragen) {
    // Injektion über Werkzeugdaten: ein präparierter Treffer in Suchergebnissen
    const runTool = async (n, args2) => {
      const r = await tools.run(n, args2);
      if (f.injektion && Array.isArray(r.treffer)) r.treffer.unshift({ drucksache: "269999", titel: f.injektion.titel, datum: "2026-01-15", art: "Antrag", stand: "offen" });
      return r;
    };
    let lauf;
    for (let versuch = 1; versuch <= 3; versuch++) {
      const chat = createChat({ tools: TOOLS, runTool, system, settings: () => ({ provider: anbieter, model: modell, key, baseUrl: a.basis }) });
      const t0 = Date.now();
      lauf = { text: "", protocol: [], citations: null, fehler: null, usage: null, model: null };
      for await (const ev of chat.ask(f.frage)) {
        if (ev.type === "done") Object.assign(lauf, { text: ev.text, protocol: ev.protocol, citations: ev.citations, usage: ev.usage, model: ev.model });
        if (ev.type === "error") Object.assign(lauf, { fehler: ev.message, status: ev.status, art: ev.kind, protocol: ev.protocol || [] });
      }
      lauf.ms = Date.now() - t0;
      // nur vorübergehende Fehler wiederholen: Ratenlimit, Serverfehler, Netzwerk, Fehlerereignis im Strom (z. B. überlastet);
      // Konfiguration, Ablehnung und interne Fehler gelingen auch beim zweiten Mal nicht
      const transient = lauf.status === 429 || lauf.status >= 500 || lauf.art === "network" || (lauf.art === "api" && !lauf.status);
      const retry = lauf.fehler && transient && versuch < 3;
      if (!retry) break;
      console.log(`  ${f.id}: ${lauf.fehler} – neuer Versuch in 30 s`);
      await sleep(30000);
    }
    const bewertung = score(f, lauf);
    rows.push({ ...f, lauf, bewertung });
    console.log(`${f.id} ${bewertung.gesamt.padEnd(9)} ${KRITERIEN.map((k) => `${k}=${bewertung[k]}`).join(" ")} · ${lauf.protocol.length} Aufrufe · ${lauf.ms} ms${lauf.fehler ? " · " + lauf.fehler : ""}`);
    await sleep(pause);
  }

  const head = ["frage_id", "kategorie", "frage", "anbieter", "modell", "prompt_version", "werkzeugaufrufe", "zitierte_quellen", "unbelegt",
    ...KRITERIEN, "gesamt_automatisch", "evidenz_korrekt (Hand)", "neutral (Hand)", "bewertung (Hand)", "bemerkung", "tokens_ein", "tokens_aus", "dauer_ms", "fehler", "antwort"];
  const lines = [head.join("\t"), ...rows.map((r) => [r.id, r.kategorie, r.frage, anbieter, r.lauf.model || modell, promptVersion,
    r.lauf.protocol.map((p) => `${p.werkzeug}(${JSON.stringify(p.parameter)})${p.ok ? "" : "!"}`).join("; "),
    (r.lauf.citations?.belegt || []).join(", "), (r.lauf.citations?.unbelegt || []).join(", "),
    ...KRITERIEN.map((k) => r.bewertung[k]), r.bewertung.gesamt, "", "", "", "",
    r.lauf.usage?.eingabe ?? "", r.lauf.usage?.ausgabe ?? "", r.lauf.ms, r.lauf.fehler || "", r.lauf.text].map(cell).join("\t"))];
  await writeFile(new URL(`${name}.tsv`, outDir), lines.join("\n") + "\n");
  await writeFile(new URL(`${name}.jsonl`, outDir), rows.map((r) => JSON.stringify({ id: r.id, frage: r.frage, bewertung: r.bewertung, ...r.lauf })).join("\n") + "\n");

  const s = summary(rows);
  console.log("\nZusammenfassung (Anteil „ja“ an anwendbaren Fällen):");
  for (const [k, v] of Object.entries(s)) {
    console.log(`  ${k.padEnd(18)} ${v.bestanden}/${v.fragen} bestanden${v.fehler ? `, ${v.fehler} Fehler` : ""} · ${KRITERIEN.filter((c) => v[c][1]).map((c) => `${c} ${v[c][0]}/${v[c][1]}`).join(" · ")}`);
  }
  const tin = rows.reduce((n, r) => n + (r.lauf.usage?.eingabe || 0), 0), tout = rows.reduce((n, r) => n + (r.lauf.usage?.ausgabe || 0), 0);
  console.log(`  Tokens gesamt: ${tin} ein, ${tout} aus`);
  console.log(`\nErgebnisse: ${fileURLToPath(new URL(`${name}.tsv`, outDir))} (und .jsonl)`);
}

main().catch((e) => { console.error(`Abbruch: ${e.message}`); process.exit(1); });
