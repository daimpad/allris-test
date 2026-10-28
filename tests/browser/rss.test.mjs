// Browser-Prüfung der Seite rss/ (pipeline/rssseite.py, site/rss.js): Feed-Adresse kopieren mit Rückmeldung, Fehler
// und Ausweichweg, Tastatur, ohne Skript, Feed abrufbar, Feed-Erkennung im Kopf (auch neben dem Gebietsfeed der Karte),
// Barrierefreiheit (axe, WCAG 2.1 A und AA) bei 1440 und 390 px.
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

async function open({ width = 1440, clipboard = true, js = true } = {}) {
  const ctx = await browser.newContext({ viewport: { width, height: 900 }, bypassCSP: true, javaScriptEnabled: js,
    permissions: clipboard ? ["clipboard-read", "clipboard-write"] : [] });
  const page = await ctx.newPage();
  page.errors = [];
  page.on("pageerror", (e) => page.errors.push(String(e)));
  return { ctx, page };
}

test("RSS-Seite: Adresse kopieren mit Rückmeldung, per Tastatur, Feed abrufbar, ohne Verstöße", async () => {
  for (const width of [1440, 390]) {
    const { ctx, page } = await open({ width });
    await page.goto(SITE + "rss/", { waitUntil: "networkidle" });
    assert.equal(await page.locator("h1").textContent(), "Inhalte abonnieren und weiterverwenden");
    const url = await page.locator("#rss-url").inputValue();
    assert.match(url, /data\/export\/bonn\/feeds\/ganz-bonn\.xml$/);
    const knopf = page.locator(".rss-cta button[data-kopieren]");
    assert.equal(await knopf.textContent(), "RSS-Adresse kopieren");
    await knopf.click();
    await page.waitForFunction(() => document.getElementById("rss-meldung").textContent.length > 0);
    assert.equal(await page.locator("#rss-meldung").textContent(), "Adresse kopiert. Jetzt im Feed-Reader einfügen.");
    assert.equal(await page.evaluate(() => navigator.clipboard.readText()), url);
    // Tastatur: vom Feld zum Knopf, Enter kopiert
    await page.locator("#rss-url").focus();
    await page.keyboard.press("Tab");
    assert.equal(await page.evaluate(() => document.activeElement.textContent), "RSS-Adresse kopieren");
    // weitere Feeds: Link öffnet die Liste, je Feed ein Kopierknopf
    await page.locator('a[href="#weitere"]').click();
    assert.equal(await page.locator("#weitere").evaluate((d) => d.open), true);
    assert.ok(await page.locator("#weitere a[data-feed]").count() > 50, "Feeds je Gebiet und Thema");
    assert.equal(await page.locator("#weitere button.rss-kopie").count(), await page.locator("#weitere a[data-feed]").count());
    // der Feed selbst: Atom, mit Einträgen
    const feed = await page.request.get(url.replace(/^https?:\/\/[^/]+\//, SITE));
    assert.equal(feed.status(), 200);
    const xml = await feed.text();
    assert.match(xml, /<feed xmlns="http:\/\/www\.w3\.org\/2005\/Atom"/);
    assert.ok((xml.match(/<entry>/g) || []).length > 0);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth), width);
    assert.deepEqual(await axe(page), []);
    assert.deepEqual(page.errors, []);
    await ctx.close();
  }
});

test("RSS-Seite: Kopieren scheitert verständlich, Adresse markiert; ohne Skript markierbares Feld", async () => {
  const { ctx, page } = await open({ clipboard: false });
  await page.addInitScript(() => {
    Object.defineProperty(navigator, "clipboard", { value: { writeText: () => Promise.reject(new Error("verweigert")) } });
    document.execCommand = () => false;
  });
  await page.goto(SITE + "rss/", { waitUntil: "networkidle" });
  await page.locator(".rss-cta button[data-kopieren]").click();
  await page.waitForFunction(() => document.getElementById("rss-meldung").textContent.length > 0);
  assert.match(await page.locator("#rss-meldung").textContent(), /^Kopieren hat nicht geklappt\. Der Text ist markiert: bitte mit (Strg|⌘)\+C kopieren\.$/);
  assert.equal(await page.locator("#rss-meldung").evaluate((m) => m.classList.contains("rss-fehler")), true);
  const markiert = await page.locator("#rss-url").evaluate((i) => [document.activeElement === i, i.selectionStart, i.selectionEnd, i.value.length]);
  assert.deepEqual(markiert.slice(0, 3), [true, 0, markiert[3]]);
  await ctx.close();
  const ohne = await open({ js: false });
  await ohne.page.goto(SITE + "rss/");
  assert.equal(await ohne.page.locator(".rss-cta button[data-kopieren]").isVisible(), false, "Kopierknopf nur mit Skript");
  assert.equal(await ohne.page.locator("#rss-url").isVisible(), true);
  assert.equal(await ohne.page.locator(".rss-cta a", { hasText: "Feed direkt ansehen" }).isVisible(), true);
  await ohne.ctx.close();
});

test("Feed-Erkennung: Startseite und Seiten im Kopf; die Karte ergänzt den Gebietsfeed, ohne den Feed über ganz Bonn zu entfernen", async () => {
  const feeds = (page) => page.evaluate(() => [...document.querySelectorAll('head link[rel="alternate"][type="application/atom+xml"]')]
    .map((l) => l.getAttribute("href").replace(/^(\.\.\/)+/, "")));
  const { ctx, page } = await open();
  await page.goto(SITE + "?gebiet=ortsteil:endenich", { waitUntil: "networkidle" });
  await page.waitForFunction(() => document.querySelector("#f-area")?.value === "ortsteil:endenich");
  await page.waitForFunction(() => document.querySelector('head link[rel="alternate"][data-gebiet]'));
  assert.deepEqual(await feeds(page), ["data/export/bonn/feeds/ganz-bonn.xml", "data/export/bonn/feeds/ortsteil-endenich.xml"]);
  await page.locator("#f-area").selectOption("ortsteil:poppelsdorf");
  await page.waitForFunction(() => document.querySelector('head link[data-gebiet="ortsteil:poppelsdorf"]'));
  assert.deepEqual(await feeds(page), ["data/export/bonn/feeds/ganz-bonn.xml", "data/export/bonn/feeds/ortsteil-poppelsdorf.xml"]);
  for (const [pfad, erwartet] of [["rss/", ["data/export/bonn/feeds/ganz-bonn.xml"]],
    ["ortsteil/endenich/", ["data/export/bonn/feeds/ortsteil-endenich.xml", "data/export/bonn/feeds/ganz-bonn.xml"]],
    ["thema/kultur-und-haushalt/", ["data/export/bonn/dossiers/kultur.xml", "data/export/bonn/feeds/ganz-bonn.xml"]]]) {
    await page.goto(SITE + pfad);
    assert.deepEqual(await feeds(page), erwartet, pfad);
  }
  await ctx.close();
});
