// Darstellung der Antworten: kein HTML aus Modellausgaben, Links nur aus Werkzeugergebnissen, Drucksachen
import { test } from "node:test";
import assert from "node:assert/strict";
import { renderMarkdown, collectUrls, resolveRef, esc } from "../../site/chat/render.js";

const URL1 = "https://www.bonn.sitzung-online.de/public/VO020?VOLFDNR=2029541";
const ctx = { urls: new Set([URL1]), refs: new Set(["261798", "261798-01 ST"]) };

test("Kein HTML aus der Modellausgabe (XSS)", () => {
  const evil = `<img src=x onerror=alert(1)> <script>alert(2)</script> [klick](javascript:alert(3)) <a href="https://evil.example">x</a>`;
  const html = renderMarkdown(evil, ctx);
  assert.doesNotMatch(html, /<img|<script|<a href="javascript|<a href="https:\/\/evil/i);
  assert.match(html, /&lt;img src=x onerror=alert\(1\)&gt;/);
  assert.match(html, /Link entfernt/);
  const attr = renderMarkdown(`[a"onmouseover="x](${URL1}")`, ctx);
  assert.doesNotMatch(attr, /onmouseover="x"/);
});

test("Links nur zu Adressen aus Werkzeugergebnissen", () => {
  const html = renderMarkdown(`[Original](${URL1}) und [Fremd](https://example.org/x) und ${URL1}`, ctx);
  assert.equal((html.match(/<a href=/g) || []).length, 2);
  assert.match(html, /target="_blank" rel="noopener noreferrer"/);
  assert.match(html, /Fremd <span class="link-removed">/);
});

test("Drucksachen: belegte als Schaltfläche (volle Nummer), unbelegte markiert", () => {
  const html = renderMarkdown("Die Vorlage 261798 und ihre Stellungnahme 261798-01; 123456 ist unbekannt.", ctx);
  assert.match(html, /<button type="button" class="ref" data-ref="261798" [^>]*>261798<\/button>/);
  assert.match(html, /data-ref="261798-01 ST"[^>]*>261798-01<\/button>/);
  assert.match(html, /<mark class="unbelegt"[^>]*>123456<\/mark>/);
  assert.equal(resolveRef("261798-01", ctx.refs), "261798-01 ST");
  assert.equal(resolveRef("261798-0", ctx.refs), null);
});

test("Markdown: Absätze, Listen, Überschriften, Hervorhebung, Code, Tabelle", () => {
  const md = "# Stand\n**Entschieden** am *24.09.2026*.\nZweite Zeile\n\n- eins\n- zwei\n1. a\n2. b\n\n`code <b>`\n\n| Gremium | Ergebnis |\n|---|---|\n| Rat | vertagt |\n\n```\n<x>\n```";
  const html = renderMarkdown(md, ctx);
  assert.match(html, /<p class="md-h"><strong>Stand<\/strong><\/p>/);
  assert.match(html, /<strong>Entschieden<\/strong> am <em>24\.09\.2026<\/em>\.<br>Zweite Zeile/);
  assert.match(html, /<ul><li>eins<\/li><li>zwei<\/li><\/ul><ol><li>a<\/li><li>b<\/li><\/ol>/);
  assert.match(html, /<code>code &lt;b&gt;<\/code>/);
  assert.match(html, /<th scope="col">Gremium<\/th>.*<td>vertagt<\/td>/s);
  assert.match(html, /<pre><code>&lt;x&gt;<\/code><\/pre>/);
});

test("Adressen aus Ergebnissen sammeln; Maskierung", () => {
  const urls = collectUrls({ links: { ratsinformationssystem: URL1, dokument: null }, quelle_id: "https://www.bonn.sitzung-online.de/oparl/papers/1", titel: "Siehe https://x.example im Text" });
  assert.deepEqual([...urls].sort(), ["https://www.bonn.sitzung-online.de/oparl/papers/1", URL1].sort());
  assert.equal(esc(`<"'&>`), "&lt;&quot;&#39;&amp;&gt;");
});
