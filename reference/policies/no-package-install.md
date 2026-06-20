# Policy: No package installs

Installing packages widens the supply-chain attack surface. The agent works with
vendored, local dependencies only.

Inspect:

- `run_shell_command` matching `npm install/i/add/ci`, `yarn add/install`, or
  `pnpm add/install`.

Decide:

- `deny`. Note that `npm test` is explicitly allowed — deny-by-default is not
  deny-everything.

Fixtures: `fixtures/npm-install.json` → **deny**; `fixtures/npm-test.json` → **allow**.
