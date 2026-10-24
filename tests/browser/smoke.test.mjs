// Browser-Prüfung der fertigen Seite (Playwright, Chromium): Start mit der Übersicht über ganz Bonn, Navigation
// über die Flächen, Link mit Gebiet und Vorgang, Flächen „Prozesse“ und „Mitmachen in Bonn“, Kartenmenü mobil,
// Ratsassistent (erst beim Öffnen geladen), Tour.
// Barrierefreiheit mit axe-core (WCAG 2.1 A und AA). Erwartet die zusammengestellte Seite unter SITE
// (Standard http://localhost:8765/), siehe Workflow tests.yml.
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

// neue Seite; Fehler im Skript und in der Konsole werden gesammelt (fehlende Dateien, 404, zählen nicht)
async function open(path = "", { width = 1440, height = 900 } = {}) {
  const page = await browser.newPage({ viewport: { width, height }, bypassCSP: true });
  page.errors = [];
  page.on("pageerror", (e) => page.errors.push(String(e)));
  page.on("console", (m) => { if (m.type() === "error" && !/404|Failed to load resource/.test(m.text())) page.errors.push(m.text()); });
  await page.goto(SITE + path, { waitUntil: "networkidle" });
  // erst prüfen, wenn app.js gestartet ist (auf einem langsamen Server kann das nach „networkidle“ liegen)
  await page.waitForFunction(() => document.querySelector("#f-area")?.value);
  return page;
}

async function axe(page) {
  if (!(await page.evaluate(() => "axe" in window))) await page.addScriptTag({ content: AXE });
  return page.evaluate(async () => (await window.axe.run(document, { runOnly: ["wcag2a", "wcag2aa"] }))
    .violations.map((v) => `${v.id}: ${v.nodes.map((n) => n.html.slice(0, 100)).join(" | ")}`));
}

// Punkt auf der Karte, an dem eine Fläche der Navigation obenauf liegt (wie ein Klick mit der Maus)
async function areaPoint(page) {
  const pts = await page.evaluate(() => {
    const o = [];
    for (let y = 100; y < innerHeight - 40; y += 15) for (let x = 20; x < innerWidth - 20; x += 15) {
      const el = document.elementFromPoint(x, y);
      if (el && el.closest(".leaflet-gebiete-pane path")) o.push({ x, y });
    }
    return o;
  });
  assert.ok(pts.length, "keine anklickbare Fläche auf der Karte");
  return pts[Math.floor(pts.length / 2)];
}

test("Start: Übersicht über ganz Bonn, Fenster „Los geht's“, ohne Verstöße", async () => {
  const page = await open();
  await page.waitForFunction(() => document.querySelectorAll(".nav-label-bz").length === 4);
  assert.equal(await page.locator("#detail-heading").textContent(), "Los geht's");
  assert.equal(await page.locator("#f-area").inputValue(), "bonn:alle");
  assert.equal(await page.locator(".nav-label-bz").count(), 4, "Namen der vier Stadtbezirke");
  assert.ok(!/gebiet=/.test(page.url()), "die Übersicht schreibt kein Gebiet in die Adresse");
  assert.deepEqual(await axe(page), []);
  assert.deepEqual(page.errors, []);
  await page.close();
});

test("Karte: Stadtbezirk anklicken, dann Ortsteil laden", async () => {
  const page = await open();
  let pt = await areaPoint(page);
  await page.mouse.click(pt.x, pt.y);
  await page.waitForFunction(() => document.querySelectorAll(".nav-label-ot").length > 0);
  pt = await areaPoint(page);
  await page.mouse.click(pt.x, pt.y);
  await page.waitForFunction(() => document.querySelector("#f-area").value.startsWith("ortsteil:"));
  // Liste des Ortsteils geladen („N von M Vorlagen“); einige Ortsteile wie Hardthöhe haben keine Vorlage mit
  // Ortsbezug, welcher getroffen wird, hängt vom Kartenausschnitt ab. Die leere Liste der Übersicht zählt nicht.
  await page.waitForFunction(() => /\d+ von \d+ Vorlagen/.test(document.querySelector("#count")?.textContent || ""));
  assert.match(page.url(), /gebiet=ortsteil/);
  assert.deepEqual(page.errors, []);
  await page.close();
});

test("Link mit Gebiet: Liste, Vorgang mit Prozesslinie, ohne Verstöße", async () => {
  const page = await open("?gebiet=ortsteil:endenich");
  assert.equal(await page.locator("#f-area").inputValue(), "ortsteil:endenich");
  await page.waitForFunction(() => document.querySelectorAll("#papers button[data-ref]").length > 0);
  await page.locator('.toggle[data-panel="panel-list"]').click();
  const first = page.locator("#papers button[data-ref]").first();
  const ref = await first.getAttribute("data-ref");
  await first.click();
  await page.waitForFunction(() => document.querySelector("#detail-heading").textContent === "Vorgang");
  assert.ok(await page.locator("#detail .steps li").count() > 0, "Prozesslinie mit Stationen");
  // Drucksachen wie „260745-03 ST“ stehen kodiert im Anker (%20)
  assert.equal(decodeURIComponent(new URL(page.url()).hash.slice(1)), ref, "Drucksache in der Adresse");
  assert.deepEqual(await axe(page), []);
  assert.deepEqual(page.errors, []);
  await page.close();
});

test("Themenebene: Flächen nach Anteil eines Themas, Zustand in der Adresse", async () => {
  const page = await open();
  await page.locator("#nav-metric").selectOption("verkehr");
  assert.match(page.url(), /flaechen=verkehr/);
  assert.match(await page.locator(".nav-legend summary").textContent(), /Verkehr/);
  // alte Beschriftungen blendet Leaflet 200 ms lang aus, bevor sie entfernt werden
  await page.waitForFunction(() => [...document.querySelectorAll(".nav-label-bz")].every((e) => /%$/.test(e.textContent)));
  assert.equal(await page.locator(".nav-label-bz").count(), 4);
  assert.deepEqual(await axe(page), []);
  await page.goto(SITE + "?flaechen=umwelt", { waitUntil: "networkidle" });
  await page.waitForFunction(() => document.querySelector("#nav-metric")?.value === "umwelt");
  assert.deepEqual(page.errors, []);
  await page.close();
});

test("Zahlen zum Gebiet: Flächen nach Kontextdaten, Steckbrief im Ortsteil", async () => {
  const page = await open();
  await page.locator("#nav-metric").selectOption("kontext-miete");
  assert.match(page.url(), /flaechen=kontext-miete/);
  assert.match(await page.locator(".nav-legend").textContent(), /Zensus 2022.*Stand 15\.05\.2022.*kein Urteil/s);
  await page.waitForFunction(() => [...document.querySelectorAll(".nav-label-bz")].every((e) => /€\/m²$/.test(e.textContent)));
  assert.deepEqual(await axe(page), []);
  // Steckbrief: Ortsteil neben dem Stadtbezirk, Kennzahlen in fester Reihenfolge
  await page.goto(SITE + "?gebiet=ortsteil:endenich", { waitUntil: "networkidle" });
  await page.waitForFunction(() => !document.querySelector("#kontext-box")?.hidden);
  await page.locator('.toggle[data-panel="panel-list"]').click();
  await page.locator("#kontext-box > summary").click();
  const head = await page.locator("#kontext-box thead").textContent();
  assert.match(head, /Endenich.*Stadtbezirk Bonn/s);
  assert.match(await page.locator("#kontext-box tbody tr").first().textContent(), /Einwohner/);
  assert.deepEqual(await axe(page), []);
  // Vorgang in genau einem Ortsteil: Kennzahlen passend zum Thema, als Einordnung gekennzeichnet
  const ende = (await (await fetch(SITE + "data/export/bonn/ortsteile/endenich.json")).json()).papers;
  const bau = ende.find((p) => (p.themes || [])[0]?.theme === "bauen" && p.locations.every((l) => l.method !== "vererbt" && l.ortsteil === "Endenich"));
  await page.goto(SITE + "?gebiet=ortsteil:endenich#" + encodeURIComponent(bau.reference), { waitUntil: "networkidle" });
  await page.waitForFunction(() => document.querySelector("#detail-heading").textContent === "Vorgang");
  const box = page.locator("#detail .kontext-vorgang");
  assert.match(await box.locator("h4").textContent(), /Zum Ortsteil Endenich.*abgeleitet/s);
  assert.match(await box.locator("tbody").textContent(), /Bodenrichtwert.*Nettokaltmiete/s);
  assert.match(await box.locator(".hint").textContent(), /kein Beleg für die Vorlage.*Stand/s);
  assert.deepEqual(await axe(page), []);
  assert.deepEqual(page.errors, []);
  await page.close();
});

test("Zuschaltbare Flächen: erst beim Hineinzoomen, Legende mit Quelle, Zustand in der Adresse", async () => {
  const page = await open("?gebiet=ortsteil:beuel-mitte");
  await page.locator(".map-kx-uesg").click();
  await page.locator(".map-kx-brw").click();
  assert.match(page.url(), /ebenen=uesg%2Cbrw|ebenen=uesg,brw/);
  const legend = page.locator(".map-legend");
  await page.waitForFunction(() => /Überschwemmungsgebiet, festgesetzt/.test(document.querySelector(".map-legend").textContent));
  // ab Ortsteil-Zoom gezeichnet: Flächen in der eigenen Ebene, Stufen der Bodenrichtwerte in der Legende
  await page.waitForFunction(() => document.querySelectorAll(".leaflet-kontextflaechen-pane path").length > 10);
  await page.waitForFunction(() => /€\/m²/.test(document.querySelector(".map-legend").textContent));
  assert.match(await legend.textContent(), /vorläufig gesichert.*Verbindlich sind die Karten des Landes.*dl-de\/zero-2\.0.*Wohnbauland.*BORIS NRW/s);
  assert.deepEqual(await axe(page), []);
  // herausgezoomt: keine Flächen, Hinweis in der Legende
  for (let i = 0; i < 4; i++) await page.locator(".leaflet-control-zoom-out").click();
  await page.waitForFunction(() => document.querySelectorAll(".leaflet-kontextflaechen-pane path").length === 0);
  assert.match(await legend.textContent(), /hineinzoomen/);
  assert.deepEqual(page.errors, []);
  await page.close();
});

test("Suche im Text der Dokumente: erst nach Klick, ohne Textausschnitt", async () => {
  const page = await open();
  const suche = await (await fetch(SITE + "data/export/bonn/suche.json")).json();
  // zwei Vorlagen, deren Titel das Suchwort nicht enthalten, als nachgebildete Treffer von OParl-Lite
  const word = "zzqxtest", hits = suche.rows.slice(0, 2).map((r) => r[0]);
  const asked = [];
  await page.route("https://oparl.bonn.machdenstaat.de/graphql", async (route) => {
    asked.push(JSON.parse(route.request().postData()));
    await route.fulfill({ contentType: "application/json", body: JSON.stringify({ data: { fileFullTextSearch: {
      totalCount: 2, pageInfo: { hasNextPage: false }, items: hits.map((reference) => ({ file: { papers: [{ reference }] } })) } } }) });
  });
  await page.locator("#q").fill(word);
  await page.waitForTimeout(400);
  assert.equal(asked.length, 0, "keine Anfrage vor dem Klick");
  await page.locator("#doc-search").click();
  await page.waitForFunction(() => /erwähn/.test(document.querySelector("#doc-status").textContent));
  assert.equal(asked.length, 1);
  assert.ok(!/snippet/.test(asked[0].query), "kein Textausschnitt angefragt");
  assert.match(await page.locator("#count").textContent(), /2 nur im Text der Dokumente/);
  assert.equal(await page.locator("#papers .doc-tag").count(), 2);
  assert.deepEqual(await axe(page), []);
  assert.deepEqual(page.errors, []);
  await page.close();
});

test("Prozesse: Verfahren, Gremien und Ämter", async () => {
  for (const tab of ["verfahren", "gremien", "aemter"]) {
    const page = await open(`?prozesse=${tab}&ansicht=liste`);
    const panel = page.locator("#panel-prozesse");
    assert.ok(await panel.isVisible(), `Fläche Prozesse (${tab})`);
    assert.ok((await panel.textContent()).length > 500, `Inhalt im Reiter ${tab}`);
    assert.deepEqual(await axe(page), [], `Reiter ${tab}`);
    assert.deepEqual(page.errors, []);
    await page.close();
  }
});

test("Mitmachen in Bonn: Stadtbezirk wechseln", async () => {
  const page = await open("?mitmachen=1&bezirk=Beuel");
  await page.waitForFunction(() => /Wege, sich einzubringen/.test(document.querySelector("#bt-body").textContent));
  assert.match(await page.locator("#bt-next-h").textContent(), /Beuel/);
  await page.locator("#bt-bezirk").selectOption("Hardtberg");
  assert.match(await page.locator("#bt-next-h").textContent(), /Hardtberg/);
  assert.deepEqual(await axe(page), []);
  assert.deepEqual(page.errors, []);
  await page.close();
});

test("Mobil: Kartenoptionen in einem Menü, ohne Verstöße", async () => {
  const page = await open("", { width: 390, height: 844 });
  // auf dem Telefon liegt das Fenster „Los geht's“ über der Karte; erst schließen
  await page.locator('.toggle[data-panel="panel-detail"]').click();
  const menu = page.locator(".map-menu");
  assert.equal(await menu.getAttribute("aria-expanded"), "false");
  assert.equal(await page.locator(".map-whole").isVisible(), false, "„Ganz Bonn ansehen“ steckt im Menü");
  await menu.click();
  assert.equal(await menu.getAttribute("aria-expanded"), "true");
  assert.ok(await page.locator(".map-whole").isVisible());
  assert.deepEqual(await axe(page), []);
  assert.deepEqual(page.errors, []);
  await page.close();
});

test("Ratsassistent: erst beim Öffnen geladen, ohne Verstöße", async () => {
  const page = await open();
  const chatFiles = () => page.evaluate(() => performance.getEntriesByType("resource").filter((e) => e.name.includes("/chat/")).length);
  assert.equal(await chatFiles(), 0, "beim Start keine Module des Assistenten");
  await page.locator('.toggle[data-panel="panel-assistent"]').click();
  await page.waitForFunction(() => document.querySelectorAll("#chat-provider option").length > 0);
  assert.ok(await chatFiles() >= 7, "Module beim Öffnen geladen");
  await page.locator("#chat-consent").click();
  assert.ok(await page.locator("#chat-settings").isVisible(), "Einstellungen nach dem KI-Hinweis");
  assert.deepEqual(await axe(page), []);
  assert.deepEqual(page.errors, []);
  await page.close();
});

test("Tour: alle Schritte bis zum Ende", async () => {
  const page = await open();
  await page.locator("[data-tour]").first().click();
  const titles = [];
  for (let i = 0; i < 30; i++) {
    // Schritte mit Ladevorgang zeigen „Einen Moment …“, bis Gebiet oder Vorgang geladen sind
    await page.waitForFunction(() => !document.querySelector("#tour-text")?.textContent.startsWith("Einen Moment"));
    // nach dem letzten Schritt ist die Karte der Tour entfernt oder ausgeblendet
    if (!(await page.locator("#tour-title").isVisible())) break;
    const title = await page.locator("#tour-title").textContent();
    titles.push(title);
    await page.locator('[data-tour-act="next"]').click();
    await page.waitForFunction((t) => {
      const el = document.querySelector("#tour-title");
      return !el || !el.offsetParent || el.textContent !== t || document.querySelector("#tour-text").textContent.startsWith("Einen Moment");
    }, title);
  }
  assert.ok(titles.length >= 15, `nur ${titles.length} Schritte: ${titles.join(" | ")}`);
  assert.ok(titles.includes("Der Vorgang"), "Schritt mit dem Beispielvorgang");
  assert.equal(await page.locator(".tour-card").isVisible(), false, "Tour ist beendet");
  assert.deepEqual(page.errors, []);
  await page.close();
});
