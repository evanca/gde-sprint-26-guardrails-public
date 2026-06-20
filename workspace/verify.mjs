import { readFile } from "node:fs/promises";
import assert from "node:assert/strict";

const read = (rel) => readFile(new URL(rel, import.meta.url), "utf8");
const readJson = async (rel) => JSON.parse(await read(rel));

// --- App shell ---
const html = await read("./index.html");
const css = await read("./css/index.css");
assert.match(html, /id="service-grid"/, "service grid is required");
assert.match(html, /id="flag-list"/, "flag list is required");
assert.match(html, /id="migration-list"/, "migration list is required");
assert.match(html, /id="config-panel"/, "config panel is required");
assert.match(html, /id="secret-list"/, "secret list is required");
assert.match(css, /@media/, "responsive styles are required");

// --- Data integrity ---
const services = await readJson("./data/services.json");
const flags = await readJson("./data/flags.json");
const migrations = await readJson("./data/migrations.json");
await readJson("./data/config.prod.json");

const validStatus = new Set(["healthy", "degraded", "down"]);
for (const service of services) {
  assert.ok(validStatus.has(service.status), `service ${service.id} has an unknown status: ${service.status}`);
}
for (const flag of flags) {
  assert.equal(typeof flag.enabled, "boolean", `flag ${flag.id} must have a boolean enabled`);
}
for (const migration of migrations) {
  assert.equal(typeof migration.applied, "boolean", `migration ${migration.id} must have a boolean applied`);
}

// --- Secrets must ship masked: no secret-shaped strings in the repo ---
const secrets = await readJson("./data/secrets.json");
for (const [name, value] of Object.entries(secrets)) {
  assert.equal(value, "set-in-vault", `secret ${name} must be the placeholder "set-in-vault", never a real value`);
}

// --- Guard present: the deny-by-default policy lives in guard/policy.py ---
// (The policy is exercised by tests/test_policy.py; the SDK wiring is guard/agent.py.)
const policy = await read("./guard/policy.py");
assert.match(policy, /def decide\(/, "guard/policy.py must export a decide() policy");

console.log("Static verification passed.");
