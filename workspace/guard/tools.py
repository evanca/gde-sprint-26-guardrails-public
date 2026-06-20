"""Release Guardrails — curated host tools.

Raw shell (`run_command`) is disabled for this agent, so the only way it can touch
the cluster is through this hardened `kubectl` tool. The tool sanitizes its own
arguments before executing — a destructive `delete` is rewritten to
`--dry-run=client` — which is the one place a command is genuinely rewritten
*before execution*. The decision logic lives in policy.py and is unit-tested
offline.
"""

from .policy import sanitize_kubectl


def kubectl(command: str) -> str:
    """Run a kubectl command against the release cluster.

    For safety, a destructive `delete` is automatically run with
    `--dry-run=client`, so nothing is actually removed.

    Args:
      command: the kubectl arguments without the leading "kubectl"
        (for example "get pods" or "delete deployment web-frontend").

    Returns:
      The command output.
    """
    safe, rewritten = sanitize_kubectl(command)
    # No real cluster in the codelab — report what would run. A real deployment
    # would exec `kubectl {safe}` here.
    note = "  (rewritten to --dry-run=client for safety)" if rewritten else ""
    return f"$ kubectl {safe}{note}\n[ok] command accepted"
