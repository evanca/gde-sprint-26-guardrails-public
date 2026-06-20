"""Release Guardrails — the pure decision logic (no SDK import).

These helpers are plain Python so they can be unit-tested offline (see
../tests/test_policy.py) with no agent, no network, and no SDK install. The live
layer (agent.py) imports the same predicates and the kubectl sanitizer, so the
behavior the tests pin down is exactly what the agent enforces.

The release posture:
- raw shell (`run_command`) is DISABLED entirely at the capability layer, so
  force-push, package installs, and `rm` are simply unavailable to the agent;
- reads of sealed secrets are DENIED with a reason;
- edits/creates on protected paths (migrations, secrets) are DENIED with a reason;
- a curated `kubectl` tool is allowed, but a destructive `delete` is rewritten to
  `--dry-run=client` before it runs.
"""

import re

# A path points at a sealed secret (never readable).
SECRET_RE = re.compile(r"(^|/)secrets\.json$|\.env(\.|$)|(^|/)secrets/", re.I)
# A path is protected from edits/creates (migrations history + secrets).
PROTECTED_RE = re.compile(r"(^|/)migrations/|(^|/)secrets\.json$|(^|/)secrets/", re.I)


def is_secret(path: str) -> bool:
    """True if the path is a sealed secret that must never be read."""
    return bool(path) and bool(SECRET_RE.search(path))


def is_protected(path: str) -> bool:
    """True if the path must not be edited, created, or overwritten."""
    return bool(path) and bool(PROTECTED_RE.search(path))


def sanitize_kubectl(command: str):
    """Make a kubectl command safe before it runs.

    A destructive `delete` is the dangerous case: append `--dry-run=client` so
    nothing is actually removed. Everything else passes through unchanged.

    Args:
      command: the kubectl args, without the leading "kubectl"
        (e.g. "delete deployment web-frontend").

    Returns:
      (safe_command, rewritten) — the (possibly modified) command and whether it
      was changed.
    """
    cmd = (command or "").strip()
    is_delete = re.match(r"^delete\b", cmd, re.I) is not None
    already_dry = "--dry-run" in cmd
    if is_delete and not already_dry:
        return f"{cmd} --dry-run=client", True
    return cmd, False


# --- Offline decision summary --------------------------------------------------
# decide() is a SDK-free mirror of the live policy used only by the tests. It maps
# a tool call ({"name", "args"}) to allow / deny / allow-with-rewrite so the whole
# posture can be verified deterministically without spawning an agent.

def _deny(reason: str) -> dict:
    return {"decision": "deny", "reason": reason}


def _path(args: dict) -> str:
    return args.get("path") or args.get("file_path") or args.get("TargetFile") or ""


def decide(call: dict) -> dict:
    name = (call or {}).get("name") or ""
    args = (call or {}).get("args") or {}

    if name == "run_command":
        return _deny("raw shell is disabled in this release repo; use a curated tool")
    if name == "view_file":
        return _deny("sealed secret — reads are blocked") if is_secret(_path(args)) else {"decision": "allow"}
    if name in ("edit_file", "create_file"):
        return _deny("protected path (migration history or secret)") if is_protected(_path(args)) else {"decision": "allow"}
    if name == "kubectl":
        safe, rewritten = sanitize_kubectl(args.get("command", ""))
        return {"decision": "allow", "rewritten": rewritten, "command": safe}
    return _deny("not on the allowlist (deny by default)")
