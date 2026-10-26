// Browser-Prüfung der Themenseite „Kultur und Haushalt“ (pipeline/prozessbild.py, site/thema.js): Detailfeld
// zu Punkt und Sitzung, Esc, Schalter der Stränge, Auswahl im Seitenlink; Barrierefreiheit mit axe-core
// (WCAG 2.1 A und AA). Erwartet die zusammengestellte Seite mit dem Schritt seo unter SITE.
import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { chromium } from "playwright";

const SITE = process.env.SITE || "http://localhost:8765/";
const SEITE = SITE + "thema/kultur-und-haushalt/";
const AXE = readFileSync(createRequire(import.meta.url).resolve("axe-core/axe.min.js"), "utf8");
let browser;

before(async () => { browser = await chromium.launch(); });
after(async () => { await browser?.close(); });

async function open(hash = "", { width = 1440, height = 900 } = {}) {
  const page = await browser.newPage({ viewport: { width, height }, bypassCSP: true });
  page.errors = [];
  page.on("pageerror", (e) => page.errors.push(String(e)));
  page.on("console", (m) => { if (m.type() === "error" && !/404|Failed to load resource/.test(m.text())) page.errors.push(m.text()); });
  await page.goto(SEITE + hash, { waitUntil: "networkidle" });
  return page;
}

async function axe(page) {
  await page.addScriptTag({ content: AXE });
  return page.evaluate(async () => (await window.axe.run(document, { runOnly: ["wcag2a", "wcag2aa"] }))
    .violations.map((v) => `${v.id}: ${v.nodes.map((n) => n.html.slice(0, 100)).join(" | ")}`));
}

const feld = (page) => page.evaluate(() => ({
  offen: !document.getElementById("pb-detail").hidden,
  titel: document.getElementById("pb-detail-titel")?.textContent || "",
  hash: location.hash,
}));

test("Themenseite: Punkt öffnet das Detailfeld, Esc schließt es, ohne Verstöße", async () => {
  const page = await open();
  const punkt = page.locator("a.pb-ziel[data-ziel^='punkt-']").first();
  const ref = await punkt.evaluate((a) => JSON.parse(document.getElementById("pb-daten").textContent)
    .punkte[a.dataset.ziel.slice(6)].reference);
  await punkt.click();
  let f = await feld(page);
  assert.ok(f.offen, "Detailfeld offen");
  assert.ok(f.titel.endsWith(ref), `Titel ${f.titel} nennt ${ref}`);
  assert.equal(new URLSearchParams(f.hash.slice(1)).get("auswahl"), ref);
  assert.match(await page.locator("#pb-ansage").textContent(), /^Ausgewählt: /);
  assert.ok(await page.locator("#pb-detail .pb-abgeleitet").count() > 0, "Strang als abgeleitet gekennzeichnet");
  assert.deepEqual(await axe(page), []);
  await page.keyboard.press("Escape");
  f = await feld(page);
  assert.equal(f.offen, false);
  assert.equal(await page.evaluate(() => document.activeElement.dataset.ziel), await punkt.getAttribute("data-ziel"));
  assert.deepEqual(page.errors, []);
  await page.close();
});

test("Themenseite: Sitzung per Tastatur, Schalter der Stränge, Zustand im Seitenlink", async () => {
  const page = await open("", { width: 390, height: 800 });
  await page.locator("a.pb-ziel[data-ziel='sitzung-0']").focus();
  await page.keyboard.press("Enter");
  const f = await feld(page);
  assert.ok(f.offen && f.titel, "Detailfeld zur Sitzung");
  assert.ok(await page.locator("#pb-detail a", { hasText: "Kalender" }).count() === 1);
  const schalter = page.locator(".pb-schalter").first();
  const strang = await schalter.getAttribute("data-strang");
  await schalter.click();
  assert.equal(await schalter.getAttribute("aria-pressed"), "false");
  assert.match(await page.evaluate(() => location.hash), /^#auswahl=sitzung-0&straenge=/);
  const gedimmt = await page.locator(`a.pb-ziel.pb-gedimmt[data-strang='${strang}']`).count();
  assert.equal(gedimmt, await page.locator(`a.pb-ziel[data-strang='${strang}']`).count());
  assert.deepEqual(await axe(page), []);
  assert.deepEqual(page.errors, []);
  await page.close();
});

test("Themenseite: Link mit Auswahl und Strängen stellt den Zustand her", async () => {
  const page = await open("#auswahl=phase-1&straenge=haushalt");
  const f = await feld(page);
  assert.ok(f.offen, "Detailfeld zur Phase");
  const zustand = await page.$$eval(".pb-schalter", (bs) => bs.map((b) => `${b.dataset.strang}=${b.getAttribute("aria-pressed")}`));
  assert.ok(zustand.includes("haushalt=true") && zustand.every((z) => z.startsWith("haushalt") || z.endsWith("false")),
    zustand.join(" "));
  assert.deepEqual(page.errors, []);
  await page.close();
});
