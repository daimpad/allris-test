// Anbieter-Adapter: nachgebildete Antworten (SSE) statt echter Aufrufe; geprüft werden Anfrageform,
// Auswertung der Streams, Werkzeugaufrufe, Fehler und Schlüsselschutz.
import { test } from "node:test";
import assert from "node:assert/strict";
import { stream, toAnthropic, toOpenAI, endpoint, sse, explain, ProviderError, listModels } from "../../site/chat/providers.js";

const KEY = "sk-test-geheim-0123456789";
const TOOLS = [{ name: "hole_vorlage", description: "Details einer Vorlage", parameters: { type: "object", properties: { drucksache: { type: "string" } }, required: ["drucksache"] } }];

// Antwort als Strom in kleinen, ungünstig geschnittenen Stücken
function sseResponse(events, { chunk = 7, status = 200 } = {}) {
  const text = events.map((e) => (typeof e === "string" ? e : (e.event ? `event: ${e.event}\n` : "") + `data: ${JSON.stringify(e.data)}\n\n`)).join("");
  const bytes = new TextEncoder().encode(text);
  let i = 0;
  const body = new ReadableStream({ pull(c) { if (i >= bytes.length) c.close(); else { c.enqueue(bytes.slice(i, i + chunk)); i += chunk; } } });
  return new Response(body, { status, headers: { "content-type": "text/event-stream" } });
}
function fakeFetch(response) {
  const calls = [];
  const f = async (url, init) => { calls.push({ url, init, body: JSON.parse(init.body) }); return typeof response === "function" ? response() : response; };
  f.calls = calls;
  return f;
}
async function collect(gen) { const out = []; for await (const e of gen) out.push(e); return out; }

const A = (type, rest) => ({ event: type, data: { type, ...rest } });
const ANTHROPIC_TOOL_TURN = [
  A("message_start", { message: { model: "claude-opus-5-5", usage: { input_tokens: 10 } } }),
  "event: ping\ndata: {\"type\":\"ping\"}\n\n",
  A("content_block_start", { index: 0, content_block: { type: "thinking", thinking: "" } }),
  A("content_block_delta", { index: 0, delta: { type: "signature_delta", signature: "sig-abc" } }),
  A("content_block_stop", { index: 0 }),
  A("content_block_start", { index: 1, content_block: { type: "text", text: "" } }),
  A("content_block_delta", { index: 1, delta: { type: "text_delta", text: "Ich suche " } }),
  A("content_block_delta", { index: 1, delta: { type: "text_delta", text: "die Vorlage." } }),
  A("content_block_stop", { index: 1 }),
  A("content_block_start", { index: 2, content_block: { type: "tool_use", id: "toolu_1", name: "hole_vorlage", input: {} } }),
  A("content_block_delta", { index: 2, delta: { type: "input_json_delta", partial_json: "{\"druck" } }),
  A("content_block_delta", { index: 2, delta: { type: "input_json_delta", partial_json: "sache\": \"261798\"}" } }),
  A("content_block_stop", { index: 2 }),
  A("message_delta", { delta: { stop_reason: "tool_use" }, usage: { output_tokens: 40 } }),
  A("message_stop", {}),
];

test("SSE: Ereignisse über Stückgrenzen, Kommentare, CRLF", async () => {
  const res = sseResponse([": kommentar\r\n", "event: a\r\ndata: 1\r\n\r\n", "data: x\ndata: y\n\n"], { chunk: 3 });
  assert.deepEqual(await collect(sse(res.body)), [{ event: "a", data: "1" }, { event: "", data: "x\ny" }]);
});

test("Anthropic: Anfrageform mit Browser-Header, Werkzeugen und Ausweichmodell", async () => {
  const f = fakeFetch(sseResponse(ANTHROPIC_TOOL_TURN));
  await collect(stream({ provider: "anthropic", model: "claude-opus-5-5", key: KEY, system: "S", history: [{ role: "user", text: "Frage" }], tools: TOOLS, fetchImpl: f }));
  const { url, init, body } = f.calls[0];
  assert.equal(url, "https://api.anthropic.com/v1/messages");
  assert.ok(!url.includes(KEY));
  assert.equal(init.headers["x-api-key"], KEY);
  assert.equal(init.headers["anthropic-dangerous-direct-browser-access"], "true");
  assert.equal(init.headers["anthropic-version"], "2023-06-01");
  assert.equal(init.headers["anthropic-beta"], "server-side-fallback-2026-07-01");
  assert.equal(body.fallbacks, "default");
  assert.equal(body.stream, true);
  assert.equal(body.system, "S");
  assert.deepEqual(body.tools[0].input_schema, TOOLS[0].parameters);
  assert.equal(body.tools[0].eager_input_streaming, true);
  assert.deepEqual(body.tool_choice, { type: "auto" });
  assert.equal(body.thinking, undefined);
  // Haiku: kein serverseitiges Ausweichmodell
  const g = fakeFetch(sseResponse(ANTHROPIC_TOOL_TURN));
  await collect(stream({ provider: "anthropic", model: "claude-haiku-5-5", key: KEY, history: [{ role: "user", text: "x" }], tools: TOOLS, toolChoice: "none", fetchImpl: g }));
  assert.equal(g.calls[0].body.fallbacks, undefined);
  assert.equal(g.calls[0].init.headers["anthropic-beta"], undefined);
  assert.deepEqual(g.calls[0].body.tool_choice, { type: "none" });
});

test("Anthropic: Text, Werkzeugaufruf und unveränderte Blöcke für die Wiedergabe", async () => {
  const ev = await collect(stream({ provider: "anthropic", model: "claude-opus-5-5", key: KEY, history: [{ role: "user", text: "x" }], tools: TOOLS, fetchImpl: fakeFetch(sseResponse(ANTHROPIC_TOOL_TURN)) }));
  assert.equal(ev.filter((e) => e.type === "text").map((e) => e.text).join(""), "Ich suche die Vorlage.");
  const call = ev.find((e) => e.type === "tool_call");
  assert.deepEqual(call, { type: "tool_call", id: "toolu_1", name: "hole_vorlage", args: { drucksache: "261798" } });
  const done = ev.at(-1);
  assert.equal(done.stop, "tool_use");
  assert.equal(done.model, "claude-opus-5-5");
  assert.deepEqual(done.raw.content.map((b) => b.type), ["thinking", "text", "tool_use"]);
  assert.equal(done.raw.content[0].signature, "sig-abc");
  assert.deepEqual(done.raw.content[2].input, { drucksache: "261798" });
});

test("Anthropic: ungültiges JSON im Werkzeugaufruf wird markiert, nicht verworfen", async () => {
  const turn = ANTHROPIC_TOOL_TURN.map((e) => (e.data?.delta?.partial_json === "sache\": \"261798\"}" ? A("content_block_delta", { index: 2, delta: { type: "input_json_delta", partial_json: "sache\": 26" } }) : e));
  const ev = await collect(stream({ provider: "anthropic", model: "claude-opus-5-5", key: KEY, history: [{ role: "user", text: "x" }], tools: TOOLS, fetchImpl: fakeFetch(sseResponse(turn)) }));
  const call = ev.find((e) => e.type === "tool_call");
  assert.equal(call.invalid, "{\"drucksache\": 26");
  assert.deepEqual(ev.at(-1).raw.content[2].input, {});
  assert.equal("_invalid" in ev.at(-1).raw.content[2], false);
});

test("Anthropic: Wechsel auf Ausweichmodell – vor der Grenze nur Text behalten", async () => {
  const turn = [
    A("message_start", { message: { model: "claude-opus-5-5" } }),
    A("content_block_start", { index: 0, content_block: { type: "thinking", thinking: "" } }),
    A("content_block_stop", { index: 0 }),
    A("content_block_start", { index: 1, content_block: { type: "text", text: "Teil" } }),
    A("content_block_stop", { index: 1 }),
    A("content_block_start", { index: 2, content_block: { type: "tool_use", id: "t0", name: "hole_vorlage", input: {} } }),
    A("content_block_stop", { index: 2 }),
    A("content_block_start", { index: 3, content_block: { type: "fallback", from: { model: "claude-opus-5-5" }, to: { model: "claude-opus-5" } } }),
    A("content_block_stop", { index: 3 }),
    A("content_block_start", { index: 4, content_block: { type: "text", text: "" } }),
    A("content_block_delta", { index: 4, delta: { type: "text_delta", text: " weiter" } }),
    A("content_block_stop", { index: 4 }),
    A("message_delta", { delta: { stop_reason: "end_turn" } }),
  ];
  const ev = await collect(stream({ provider: "anthropic", model: "claude-opus-5-5", key: KEY, history: [{ role: "user", text: "x" }], fetchImpl: fakeFetch(sseResponse(turn)) }));
  assert.deepEqual(ev.find((e) => e.type === "fallback"), { type: "fallback", from: "claude-opus-5-5", to: "claude-opus-5" });
  assert.equal(ev.filter((e) => e.type === "tool_call").length, 0);
  assert.deepEqual(ev.at(-1).raw.content.map((b) => b.type), ["text", "text"]);
  assert.equal(ev.at(-1).stop, "end");
});

test("Anthropic: Verlauf mit Rohblöcken und Werkzeugergebnissen", () => {
  const raw = { provider: "anthropic", content: [{ type: "thinking", thinking: "", signature: "s" }, { type: "tool_use", id: "t1", name: "hole_vorlage", input: { drucksache: "1" } }] };
  const msgs = toAnthropic([
    { role: "user", text: "Frage" },
    { role: "assistant", text: "", toolCalls: [{ id: "t1", name: "hole_vorlage", args: { drucksache: "1" } }], raw },
    { role: "tool", results: [{ id: "t1", name: "hole_vorlage", content: "{}", isError: true }] },
    { role: "assistant", text: "Antwort", toolCalls: [] },
  ]);
  assert.equal(msgs[1].content, raw.content);
  assert.deepEqual(msgs[2], { role: "user", content: [{ type: "tool_result", tool_use_id: "t1", content: "{}", is_error: true }] });
  assert.deepEqual(msgs[3], { role: "assistant", content: [{ type: "text", text: "Antwort" }] });
  assert.equal(toAnthropic([{ role: "assistant", text: "", toolCalls: [] }]).length, 0);
});

const O = (delta, finish = null, extra = {}) => ({ data: { model: "m", choices: [{ index: 0, delta, finish_reason: finish }], ...extra } });

test("OpenAI-kompatibel: Text und in Stücken gelieferte Werkzeugargumente", async () => {
  const f = fakeFetch(sseResponse([
    ": OPENROUTER PROCESSING\n\n",
    O({ role: "assistant", content: "Moment" }),
    O({ tool_calls: [{ index: 0, id: "call_a", type: "function", function: { name: "hole_vorlage", arguments: "{\"drucks" } }] }),
    O({ tool_calls: [{ index: 0, function: { arguments: "ache\":\"261798\"}" } }] }),
    O({ tool_calls: [{ index: 1, id: "call_b", function: { name: "datenstand", arguments: "" } }] }),
    O({}, "tool_calls"),
    "data: [DONE]\n\n",
  ]));
  const ev = await collect(stream({ provider: "openrouter", model: "x/y", key: KEY, system: "S", history: [{ role: "user", text: "q" }], tools: TOOLS, fetchImpl: f }));
  const { url, init, body } = f.calls[0];
  assert.equal(url, "https://openrouter.ai/api/v1/chat/completions");
  assert.equal(init.headers.authorization, `Bearer ${KEY}`);
  assert.equal(init.headers["X-Title"], "RIS-Karte Bonn");
  assert.deepEqual(body.messages[0], { role: "system", content: "S" });
  assert.equal(body.tools[0].function.name, "hole_vorlage");
  assert.equal(body.tool_choice, "auto");
  assert.deepEqual(ev.filter((e) => e.type === "tool_call").map((e) => [e.id, e.name, e.args]),
    [["call_a", "hole_vorlage", { drucksache: "261798" }], ["call_b", "datenstand", {}]]);
  assert.equal(ev.at(-1).stop, "tool_use");
});

test("Mistral: vollständige Aufrufe ohne Index; Werkzeugname in der Antwortnachricht", async () => {
  const f = fakeFetch(sseResponse([
    O({ tool_calls: [{ id: "abc123XYZ", function: { name: "hole_vorlage", arguments: "{\"drucksache\":\"1\"}" } }] }, "tool_calls"),
    "data: [DONE]\n\n",
  ]));
  const ev = await collect(stream({ provider: "mistral", model: "mistral-medium-latest", key: KEY, history: [{ role: "user", text: "q" }], tools: TOOLS, fetchImpl: f }));
  assert.deepEqual(ev.find((e) => e.type === "tool_call").args, { drucksache: "1" });
  const msgs = toOpenAI([{ role: "assistant", text: "", toolCalls: [{ id: "abc123XYZ", name: "hole_vorlage", args: { drucksache: "1" } }] },
    { role: "tool", results: [{ id: "abc123XYZ", name: "hole_vorlage", content: "{}" }] }], "", { toolName: true });
  assert.deepEqual(msgs[0].tool_calls[0], { id: "abc123XYZ", type: "function", function: { name: "hole_vorlage", arguments: "{\"drucksache\":\"1\"}" } });
  assert.deepEqual(msgs[1], { role: "tool", tool_call_id: "abc123XYZ", content: "{}", name: "hole_vorlage" });
});

test("Fehler: verständliche Meldung ohne Schlüssel; fehlende Angaben", async () => {
  const f = fakeFetch(() => new Response(JSON.stringify({ error: { message: `invalid x-api-key ${KEY}` } }), { status: 401 }));
  await assert.rejects(collect(stream({ provider: "anthropic", model: "claude-opus-5-5", key: KEY, history: [], fetchImpl: f })),
    (e) => e instanceof ProviderError && e.status === 401 && !e.message.includes(KEY));
  const g = fakeFetch(() => new Response(JSON.stringify({ message: `model foo not found for ${KEY}` }), { status: 400 }));
  await assert.rejects(collect(stream({ provider: "mistral", model: "foo", key: KEY, history: [], fetchImpl: g })),
    (e) => e.status === 400 && e.message.includes("[Schlüssel]") && !e.message.includes(KEY));
  const offline = async () => { throw new TypeError("Failed to fetch"); };
  await assert.rejects(collect(stream({ provider: "mistral", model: "m", key: KEY, history: [], fetchImpl: offline })), (e) => e.kind === "network");
  assert.throws(() => stream({ provider: "anthropic", model: "m", key: "", history: [] }), /Schlüssel/);
  assert.throws(() => stream({ provider: "mistral", model: "", key: KEY, history: [] }), /Modell/);
  assert.match(explain(429), /limit/);
  assert.match(explain(503), /nicht erreichbar/);
});

test("Anthropic: Fehlerereignis im Strom", async () => {
  const f = fakeFetch(sseResponse([A("message_start", { message: { model: "m" } }), A("error", { error: { type: "overloaded_error", message: "Overloaded" } })]));
  await assert.rejects(collect(stream({ provider: "anthropic", model: "claude-opus-5-5", key: KEY, history: [], fetchImpl: f })), /überlastet/);
});

test("Lokal: nur localhost, ohne Schlüssel, eigene Basisadresse", async () => {
  assert.equal(endpoint("lokal"), "http://localhost:11434/v1/chat/completions");
  assert.equal(endpoint("lokal", "http://127.0.0.1:1234/v1/"), "http://127.0.0.1:1234/v1/chat/completions");
  assert.equal(endpoint("lokal", "http://localhost:8080"), "http://localhost:8080/v1/chat/completions");
  assert.throws(() => endpoint("lokal", "https://example.org"), /localhost/);
  const f = fakeFetch(sseResponse([O({ content: "Hallo" }, "stop"), "data: [DONE]\n\n"]));
  const ev = await collect(stream({ provider: "lokal", model: "qwen", key: "", history: [{ role: "user", text: "q" }], fetchImpl: f }));
  assert.equal(f.calls[0].init.headers.authorization, undefined);
  assert.equal(ev.at(-1).stop, "end");
});

test("Modelllisten: OpenRouter nur mit Werkzeugen", async () => {
  const f = async () => new Response(JSON.stringify({ data: [{ id: "a/b", name: "B", supported_parameters: ["tools"] }, { id: "c/d", name: "D", supported_parameters: [] }] }));
  assert.deepEqual(await listModels("openrouter", { fetchImpl: f }), [{ id: "a/b", name: "B" }]);
  assert.equal((await listModels("anthropic")).length, 3);
});
