"""Release Guardrails — the audit record (pure logic).

Wired into the Antigravity SDK's post-tool Inspect hook (see agent.py), this
turns each completed tool call into one reviewable log line. Inspect hooks are
read-only and non-blocking: they never change a decision, they only record.

`audit_line` is pure so it can be unit-tested offline. It accepts either a real
SDK `ToolResult` (which carries `.name` / `.result` / `.error`) or a plain dict
fixture of the same shape.
"""


def _get(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def audit_line(result) -> str:
    name = _get(result, "name") or _get(result, "tool_name") or "unknown"
    error = _get(result, "error")
    status = "ERROR" if error else "ok"
    return f"[audit] {name}: {status}"
