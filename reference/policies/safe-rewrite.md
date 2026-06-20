# Policy: Safely rewrite destructive commands (Transform)

Some commands are useful but dangerous in their raw form. Instead of denying
outright, rewrite them into a safe equivalent before they run.

Inspect:

- `run_shell_command` matching `kubectl delete ...`.

Transform:

- If the command already has `--dry-run`, allow it unchanged.
- Otherwise return `decision: "allow"` with
  `hookSpecificOutput.tool_input.command` set to the original command plus
  `--dry-run=client`. The agent sees a success; nothing is actually deleted.

Fixture: `fixtures/kubectl-delete.json` → **allow + transform** (adds `--dry-run=client`).
