"""Release Guardrails — the pure decision logic (YOU IMPLEMENT THIS).

This is the starter stub. Right now it is permissive: every predicate says "not
sensitive", the kubectl sanitizer changes nothing, and decide() allows
everything. So the offline tests in ../tests/test_policy.py are RED.

Your job (see the codelab): implement the deny-by-default release posture so the
tests go green. Keep the function signatures — agent.py and tools.py import them:

- is_secret(path)      -> True for sealed secrets (e.g. secrets.json, .env)
- is_protected(path)   -> True for paths that must not be edited (migrations, secrets)
- sanitize_kubectl(cmd)-> (safe_cmd, rewritten); a destructive `delete` gets
                          `--dry-run=client` appended
- decide(call)         -> offline mirror used by the tests: allow / deny / allow+rewrite

No SDK import belongs in this file — keep it pure so it stays testable offline.
"""


def is_secret(path: str) -> bool:
    # TODO: return True for sealed secrets that must never be read.
    return False


def is_protected(path: str) -> bool:
    # TODO: return True for paths that must not be edited or created
    # (migration history and secrets).
    return False


def sanitize_kubectl(command: str):
    # TODO: append `--dry-run=client` to a destructive `delete` (and only then).
    return (command or "").strip(), False


def decide(call: dict) -> dict:
    # TODO: implement the deny-by-default posture. For now, allow everything.
    return {"decision": "allow"}
