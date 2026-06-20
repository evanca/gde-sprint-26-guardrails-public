import test from "node:test";
import assert from "node:assert/strict";
import { groupByEnvironment, countByStatus, maskSecret, flagState } from "../js/console.js";

// --- Console pure functions -------------------------------------------------
// The deny-by-default policy itself is tested in tests/test_policy.py
// (the guard runs on the Antigravity SDK, which is Python).

test("services group by environment", () => {
  const groups = groupByEnvironment([
    { id: "a", environment: "prod" },
    { id: "b", environment: "dev" }
  ]);
  assert.equal(groups.prod.length, 1);
  assert.equal(groups.dev.length, 1);
});

test("status counts include a total", () => {
  const counts = countByStatus([{ status: "healthy" }, { status: "degraded" }]);
  assert.equal(counts.total, 2);
  assert.equal(counts.healthy, 1);
});

test("secrets are always masked", () => {
  assert.equal(maskSecret("anything-at-all"), "••••••••");
});

test("flag state reads on/off", () => {
  assert.equal(flagState({ enabled: true }), "on");
  assert.equal(flagState({ enabled: false }), "off");
});
