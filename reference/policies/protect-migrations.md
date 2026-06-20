# Policy: Protect migrations

Applied database migrations are immutable. The agent may not delete or rewrite
files under `migrations/`.

Inspect:

- `write_file` / `replace` with a path under `migrations/`.
- `run_shell_command` whose command contains `rm` and targets `migrations/`.

Decide:

- `deny`. Migration changes are a human, reviewed operation.

Fixture: `fixtures/rm-migration.json` → **deny**.
