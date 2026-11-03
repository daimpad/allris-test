// Browser-Prüfung der Begriffe (Entscheidungen 02.11.2026): Erklärung zum Aufklappen im Vorgang (Maus und Tastatur),
// Gremium der Prozesslinie öffnet den Reiter „Prozesse“, einfachere Wörter, Seite begriffe/ und Akkordeon auf den
// Themenseiten; Barrierefreiheit (axe, WCAG 2.1 A und AA) bei 1440 und 390 px.
import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { chromium } from "playwright";

const SITE = process.env.SITE || "http://localhost:8765/";
const AXE = readFileSync(createRequire(import.meta.url).resolve("axe-core/axe.min.js"), "utf8");
let browser;
before(async () => { browser = await chromium.launch(); });
after(async () => { await browser?.close(); });

async function axe(page) {
  if (!(await page.evaluate(() => "axe" in window))) await page.addScriptTag({ content: AXE });
  return page.evaluate(async () => (await window.axe.run(document, { runOnly: ["wcag2a", "wcag2aa"] }))
    .violations.map((v) => `${v.id}: ${v.nodes.map((n) => n.html.slice(0, 100)).join(" | ")}`));
}

test("Vorgang: Erklärung zur Art aufklappen, per Tastatur, Gremium führt in den Reiter Prozesse", async () => {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, bypassCSP: true });
  const errors = [];
  page.on("pageerror", (e) => errors.push(String(e)));
  await page.goto(SITE + "?gebiet=ortsteil:endenich", { waitUntil: "networkidle" });
  await page.waitForFunction(() => document.querySelectorAll("#papers button[data-ref]").length > 0);
  await page.locator('.toggle[data-panel="panel-list"]').click();
  await page.locator("#papers button[data-ref]").first().click();
  await page.waitForFunction(() => document.querySelector("#detail-heading").textContent === "Vorgang");
  const knopf = page.locator('#detail .facts dd button.erkl-btn').first();
  assert.equal(await knopf.getAttribute("aria-expanded"), "false");
  const text = page.locator(`#${await knopf.getAttribute("aria-controls")}`);
  assert.equal(await text.isVisible(), false);
  await knopf.click();
  assert.equal(await knopf.getAttribute("aria-expanded"), "true");
  assert.equal(await text.isVisible(), true);
  assert.ok((await text.textContent()).length > 20);
  await knopf.focus();
  await page.keyboard.press("Enter");
  assert.equal(await text.isVisible(), false, "Enter klappt wieder zu");
  // einfachere Wörter in der Prozesslinie
  const koepfe = await page.locator("#detail .step-head").allTextContents();
  assert.ok(koepfe.some((k) => k.startsWith("Anstoß")), koepfe.join(" | "));
  assert.ok(!koepfe.some((k) => /Initiierung|Vollzug/.test(k)));
  assert.doesNotMatch(await page.locator("#detail .locs").textContent(), /Stufe [ABC]/);
  // Gremium der Prozesslinie → Reiter „Prozesse“, Gremien
  const gremium = page.locator("#detail [data-gremium-name]").first();
  if (await gremium.count()) {
    const name = await gremium.getAttribute("data-gremium-name");
    await gremium.click();
    await page.waitForFunction(() => !document.getElementById("panel-prozesse").hidden);
    await page.waitForFunction((n) => [...document.querySelectorAll("#panel-prozesse [aria-pressed='true'], #panel-prozesse details[open] .pz-title")]
      .some((e) => e.textContent.includes(n)), name, { timeout: 5000 });
  }
  assert.deepEqual(errors, []);
  await page.close();
});

test("Seite begriffe/ und Akkordeon auf den Themenseiten, ohne Verstöße", async () => {
  for (const width of [1440, 390]) {
    const page = await browser.newPage({ viewport: { width, height: 900 }, bypassCSP: true });
    await page.goto(SITE + "begriffe/#st", { waitUntil: "networkidle" });
    assert.equal(await page.locator("h1").textContent(), "Begriffe");
    assert.match(await page.locator("dt:target + dd").textContent(), /Stellungnahme der Verwaltung/);
    assert.ok(await page.locator("dl.begriffe dt").count() > 80);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth), width);
    assert.deepEqual(await axe(page), []);
    await page.goto(SITE + "thema/kunst-und-kultur/", { waitUntil: "networkidle" });
    const acc = page.locator("details.begriffe-acc");
    assert.equal(await acc.count(), 1);
    await acc.locator("summary").click();
    assert.ok(await acc.locator("dt a[href*='begriffe/#']").count() > 0);
    assert.deepEqual(await axe(page), []);
    await page.close();
  }
});

test("Seite einfach/: acht Abschnitte, Link im Startfenster und im Fuß, ohne Verstöße", async () => {
  for (const width of [1440, 390]) {
    const page = await browser.newPage({ viewport: { width, height: 900 }, bypassCSP: true });
    await page.goto(SITE + "einfach/", { waitUntil: "networkidle" });
    assert.equal(await page.locator("h1").textContent(), "Die RIS-Karte in Einfacher Sprache");
    assert.equal(await page.locator(".einfach h2").count(), 8);
    assert.equal(await page.locator("ol.einfach-weg li").count(), 5);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth), width);
    assert.deepEqual(await axe(page), []);
    await page.close();
  }
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto(SITE, { waitUntil: "networkidle" });
  await page.waitForFunction(() => document.querySelector("#detail .intro"));
  assert.equal(await page.locator('#detail .intro a[href="einfach/"]').count(), 1, "Link im Startfenster");
  await page.goto(SITE + "thema/", { waitUntil: "networkidle" });
  assert.equal(await page.locator('footer a[href="../einfach/"]').count(), 1, "Link im Fuß");
  await page.close();
});

test("So funktioniert die Karte: Klick auf einen Kasten zeigt die Erklärung, Tastatur, ohne Verstöße", async () => {
  for (const [width, format] of [[1440, "breit"], [390, "hoch"]]) {
    const page = await browser.newPage({ viewport: { width, height: 900 }, bypassCSP: true });
    const fehler = [];
    page.on("pageerror", (e) => fehler.push(String(e)));
    await page.goto(SITE + "technik/", { waitUntil: "networkidle" });
    assert.equal(await page.locator(`.tk-svg.hh-${format}`).filter({ visible: true }).count(), 4, "vier Grafiken");
    const kasten = page.locator(`#datenfluss + p + .tk-grafik .tk-svg.hh-${format} a[href="#tk-s-check"]`);
    await kasten.click();
    const feld = page.locator("#datenfluss + p + .tk-grafik .tk-detail");
    assert.equal(await feld.isVisible(), true);
    assert.match(await feld.textContent(), /^Prüfung: Prüft Kennzahlen und Datenschutz/);
    assert.equal(await kasten.getAttribute("aria-current"), "true");
    assert.equal(new URL(page.url()).hash, "#tk-s-check");
    // Tastatur: Kasten des Zeitplans per Enter
    await page.locator(`#zeitplan + p + .tk-grafik .tk-svg.hh-${format} a[href^="#tk-z-pages-"]`).focus();
    await page.keyboard.press("Enter");
    assert.match(await page.locator("#zeitplan + p + .tk-grafik .tk-detail").textContent(), /täglich 04:17 UTC/);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth), width);
    assert.deepEqual(await axe(page), []);
    assert.deepEqual(fehler, []);
    await page.close();
  }
});
