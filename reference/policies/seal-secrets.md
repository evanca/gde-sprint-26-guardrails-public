# Policy: Seal production secrets

The agent must never read or edit production secrets.

Inspect:

- `read_file` / `read_many_files` / `write_file` / `replace` whose path matches
  `secrets.json`, anything under `secrets/`, or any `.env` file.

Decide:

- `deny` with a clear reason. The agent should ask a human or use the masked
  console view instead.

Fixture: `fixtures/read-secret.json` → **deny**.
