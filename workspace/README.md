# Release Guardrails Console

A mock release/deploy repository for practicing runtime guardrails on an
autonomous agent. Everything is local JSON — no real secrets, backend, or network.

## Layout

- `data/services.json` — services by environment.
- `data/flags.json` — feature flags (e.g. dark-mode).
- `data/migrations.json` — applied database migrations.
- `data/config.prod.json` — production config.
- `data/secrets.json` — **sealed secrets** (masked; must never be read or edited).
- `migrations/` — applied migration SQL files (**immutable**).
- `index.html`, `js/`, `css/` — the static release console.
- `guard/` — the deny-by-default guard:
  - `policy.py` — pure decision logic (unit-tested offline).
  - `tools.py` — the curated `kubectl` tool (rewrites destructive deletes).
  - `agent.py` — wires the guard into the Antigravity SDK.
  - `audit.py` — the post-tool audit line.
- `tests/` — offline policy tests (`python -m unittest discover -s tests -p "test_*.py"`).

## Guardrails

Raw shell (`run_command`) is disabled. Reading sealed secrets and editing
protected paths (migrations, secrets) is denied. Cluster access goes through the
`kubectl` tool, which rewrites a destructive `delete` to `--dry-run=client`.
