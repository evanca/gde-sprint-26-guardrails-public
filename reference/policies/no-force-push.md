# Policy: No force-push

Force-pushing rewrites shared release history. The agent may push, but never
with `--force`, `--force-with-lease`, or `-f`.

Inspect:

- `run_shell_command` whose command is a `git push` carrying a force flag.

Decide:

- `deny`. A normal `git push` is fine; force is a human decision.

Fixture: `fixtures/git-force-push.json` → **deny**.
