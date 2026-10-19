// Mitwirkung nach Regelwerk (site/mitwirken.js): Einordnung einer Vorlage und Auswertung der Einflussregeln
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile, access } from "node:fs/promises";
import { mitwirken, kontext, gruppe, addDays } from "../../site/mitwirken.js";

const SOLL_URL = new URL("../../data/export/bonn/soll.json", import.meta.url);
const HEUTE = "2026-10-19";
const REGELN = [
  { id: "sitzung-besuchen", wenn: { status: ["offen", "vertagt"], termin: true, nicht_verfahren: ["nichtoeffentlich"] },
    was: "Besuchen Sie die Sitzung: {gremium} am {datum}.", frist: "am Sitzungstag", bezug: "termin", tage: 0, beleg: "GeschO § 5", links: [] },
  { id: "einwohnerfrage", wenn: { status: ["offen", "vertagt"], termin_gremienart: ["Bezirksvertretungen"] },
    was: "Stellen Sie selbst eine Frage: {gremium}.", frist: "21 Tage vor der Sitzung", bezug: "termin", tage: -21, beleg: "GeschO § 26", links: [] },
  { id: "eigener-buergerantrag", wenn: { status: ["offen", "vertagt", "unklar"], nicht_verfahren: ["nichtoeffentlich"] },
    was: "Zuständig ist {ziel}; nächste Sitzung am {ziel_datum}.", frist: "21 Tage vor der Sitzung", bezug: "buergerantrag_ziel", tage: -21, beleg: "§ 24 GO NRW", links: [] },
  { id: "entschieden", wenn: { status: ["abgeschlossen"], abschluss: ["beschlossen"] }, was: "Entschieden.", frist: "jederzeit", tage: 0, links: [] },
  { id: "stand-erfragen", wenn: { status: ["unklar"] }, was: "Stand unklar.", frist: "jederzeit", tage: 0, links: [] },
];
const SOLL = { mitwirken: REGELN, buergerantrag_ziel: { bezirk: "Bezirksvertretung {bezirk}", stadt: "Ausschuss für Beteiligung der Bürgerinnen und Bürger" } };
const MEETINGS = [
  { gremium: "Bezirksvertretung Bonn", date: "2026-11-04", web: "https://example.org/to1" },
  { gremium: "Bezirksvertretung Bonn", date: "2026-12-02", web: null },
  { gremium: "Ausschuss für Beteiligung der Bürgerinnen und Bürger", date: "2026-11-03" },
];
const vorlage = (o) => ({ reference: "261000", date: "2026-09-01", stand: "offen", soll: { verfahren: "antrag-bv" }, steps: [], ...o });

test("gruppe: Ergebnisgruppen wie im Original", () => {
  assert.equal(gruppe("ungeändert beschlossen"), "beschlossen");
  assert.equal(gruppe("vertagt"), "vertagt");
  assert.equal(gruppe("zur Kenntnis genommen"), "zur Kenntnis");
  assert.equal(gruppe("abgelehnt"), "abgelehnt");
  assert.equal(gruppe(null), "offen");
  assert.equal(addDays("2026-11-04", -21), "2026-10-14");
});

test("Termin in der Bezirksvertretung: Sitzung, Einwohnerfrage mit verstrichener Frist, Bürgerantrag an die BV", () => {
  const p = vorlage({ steps: [{ typ: "entscheidung", label: "Bezirksvertretung Bonn", date: "2026-11-04" }] });
  const m = mitwirken(p, SOLL, MEETINGS, HEUTE);
  assert.deepEqual(m.kontext.termin, { datum: "2026-11-04", gremium: "Bezirksvertretung Bonn", gremienart: "Bezirksvertretungen" });
  assert.equal(m.kontext.ebene, "bezirk");
  const by = Object.fromEntries(m.regeln.map((r) => [r.id, r]));
  assert.equal(by["sitzung-besuchen"].text, "Besuchen Sie die Sitzung: Bezirksvertretung Bonn am 04.11.2026.");
  assert.equal(by["sitzung-besuchen"].sitzung.web, "https://example.org/to1");
  assert.equal(by.einwohnerfrage.frist, "21 Tage vor der Sitzung, also bis 14.10.2026");
  assert.equal(by.einwohnerfrage.verstrichen, true);
  // erste Sitzung, deren Frist noch nicht verstrichen ist: 02.12.2026 (Frist 11.11.)
  assert.equal(by["eigener-buergerantrag"].text, "Zuständig ist die Bezirksvertretung Bonn; nächste Sitzung am 02.12.2026.");
});

test("Ebene Stadt: Bürgerantrag an den Ausschuss für Beteiligung, ohne erreichbare Sitzung entfällt die Regel", () => {
  const p = vorlage({ steps: [{ typ: "beratung", label: "Ausschuss für Mobilität und Verkehr", result: "vertagt", date: "2026-10-01" }], stand: "in Beratung" });
  const m = mitwirken(p, SOLL, MEETINGS, "2026-10-10");
  assert.equal(m.kontext.status, "vertagt");
  assert.match(m.regeln.find((r) => r.id === "eigener-buergerantrag").text, /^Zuständig ist der Ausschuss für Beteiligung/);
  assert.ok(!mitwirken(p, SOLL, MEETINGS, HEUTE).regeln.some((r) => r.id === "eigener-buergerantrag"));
});

test("Einordnung: entschieden, alte offene Vorgänge unklar, ohne Soll keine Regeln", () => {
  const ent = vorlage({ stand: "entschieden", steps: [{ typ: "entscheidung", label: "Rat", result: "ungeändert beschlossen", date: "2026-06-01" }] });
  assert.deepEqual(mitwirken(ent, SOLL, MEETINGS, HEUTE).regeln.map((r) => r.id), ["entschieden"]);
  const alt = vorlage({ date: "2022-01-10", steps: [{ typ: "beratung", label: "Rat", date: "2022-02-01" }] });
  assert.equal(kontext(alt, HEUTE).status, "unklar");
  assert.ok(mitwirken(alt, SOLL, MEETINGS, HEUTE).regeln.some((r) => r.id === "stand-erfragen"));
  assert.deepEqual(mitwirken(vorlage({ soll: { verfahren: null } }), SOLL, MEETINGS, HEUTE).regeln, []);
});

test("echter Export: Regeln in Sie-Form mit Rechtsgrundlagen", { skip: !(await access(SOLL_URL).then(() => true, () => false)) }, async () => {
  const s = JSON.parse(await readFile(SOLL_URL, "utf8"));
  assert.equal(s.mitwirken.length, 14);
  for (const r of s.mitwirken) {
    assert.doesNotMatch(r.was, /\b(du|dein|deine|dir|dich)\b/i, r.id);
    if (r.beleg && /GeschO|GO NRW|BauGB/.test(r.beleg)) assert.ok(r.links.length, r.id);
  }
});
