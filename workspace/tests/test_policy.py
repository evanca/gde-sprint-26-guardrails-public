"""Offline tests for the deny-by-default release guard.

Run from the project root with:
  python -m unittest discover -s tests -p "test_*.py"

No agent, no network, no SDK install — policy.py is pure logic.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from guard.policy import decide, is_protected, is_secret, sanitize_kubectl  # noqa: E402

FIXTURES = ROOT / "fixtures"


def fixture(name):
    return json.loads((FIXTURES / f"{name}.json").read_text())


class DenyByDefaultGuard(unittest.TestCase):
    def test_sealed_secret_read_is_denied(self):
        self.assertEqual(decide(fixture("read-secret"))["decision"], "deny")

    def test_non_secret_read_is_allowed(self):
        self.assertEqual(decide(fixture("read-config"))["decision"], "allow")

    def test_benign_flag_edit_is_allowed(self):
        self.assertEqual(decide(fixture("edit-flag"))["decision"], "allow")

    def test_editing_a_migration_is_denied(self):
        self.assertEqual(decide(fixture("edit-migration"))["decision"], "deny")

    def test_raw_shell_is_disabled(self):
        # run_command is disabled at the capability layer; the offline mirror
        # treats it as denied (the agent never even sees it live).
        self.assertEqual(decide(fixture("run-command"))["decision"], "deny")

    def test_kubectl_delete_is_rewritten_to_dry_run(self):
        result = decide(fixture("kubectl-delete"))
        self.assertEqual(result["decision"], "allow")
        self.assertTrue(result["rewritten"])
        self.assertIn("--dry-run=client", result["command"])

    def test_safe_kubectl_is_not_rewritten(self):
        result = decide(fixture("kubectl-get"))
        self.assertEqual(result["decision"], "allow")
        self.assertFalse(result["rewritten"])

    def test_unknown_tool_is_denied_by_default(self):
        self.assertEqual(decide({"name": "exfiltrate_data", "args": {}})["decision"], "deny")

    def test_every_deny_carries_a_reason(self):
        denied = decide(fixture("read-secret"))
        self.assertIsInstance(denied["reason"], str)
        self.assertGreater(len(denied["reason"]), 0)


class Predicates(unittest.TestCase):
    def test_is_secret(self):
        self.assertTrue(is_secret("data/secrets.json"))
        self.assertTrue(is_secret("config/.env"))
        self.assertFalse(is_secret("data/services.json"))

    def test_is_protected(self):
        self.assertTrue(is_protected("migrations/0007_add_orders_index.sql"))
        self.assertTrue(is_protected("data/secrets.json"))
        self.assertFalse(is_protected("data/flags.json"))

    def test_sanitize_kubectl_appends_dry_run_once(self):
        safe, rewritten = sanitize_kubectl("delete deployment web-frontend")
        self.assertEqual(safe, "delete deployment web-frontend --dry-run=client")
        self.assertTrue(rewritten)
        # idempotent: already-safe delete is left alone
        safe2, rewritten2 = sanitize_kubectl("delete pod x --dry-run=client")
        self.assertFalse(rewritten2)

    def test_sanitize_kubectl_leaves_reads_alone(self):
        safe, rewritten = sanitize_kubectl("get pods")
        self.assertEqual(safe, "get pods")
        self.assertFalse(rewritten)


if __name__ == "__main__":
    unittest.main()
