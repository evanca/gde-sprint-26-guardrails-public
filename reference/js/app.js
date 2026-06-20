import { groupByEnvironment, countByStatus, maskSecret, flagState, ENVIRONMENTS } from "./console.js";

const serviceGrid = document.querySelector("#service-grid");
const statusSummary = document.querySelector("#status-summary");
const flagList = document.querySelector("#flag-list");
const migrationList = document.querySelector("#migration-list");
const configPanel = document.querySelector("#config-panel");
const secretList = document.querySelector("#secret-list");
const errorBox = document.querySelector("#error");

function showError(message) {
  errorBox.hidden = false;
  errorBox.textContent = message;
}

function renderServices(services) {
  const counts = countByStatus(services);
  statusSummary.textContent = `${counts.total} services · ${counts.healthy} healthy · ${counts.degraded || 0} degraded`;
  const groups = groupByEnvironment(services);
  serviceGrid.innerHTML = ENVIRONMENTS.map((env) => `
    <section class="env" aria-label="${env}">
      <h3>${env}</h3>
      ${(groups[env] || []).map((service) => `
        <article class="service-card" data-status="${service.status}">
          <span class="name">${service.name}</span>
          <span class="version">${service.version}</span>
          <span class="status">${service.status}</span>
        </article>
      `).join("")}
    </section>
  `).join("");
}

function renderFlags(flags) {
  flagList.innerHTML = flags.map((flag) => `
    <li class="flag" data-state="${flagState(flag)}">
      <span>${flag.label}</span>
      <span class="flag-state">${flagState(flag)}</span>
    </li>
  `).join("");
}

function renderMigrations(migrations) {
  migrationList.innerHTML = migrations.map((migration) => `
    <li class="migration" data-applied="${migration.applied}">
      <code>${migration.id}</code>
      <span>${migration.applied ? "applied" : "pending"}</span>
    </li>
  `).join("");
}

function renderConfig(config) {
  configPanel.innerHTML = Object.entries(config).map(([key, value]) => `
    <div class="config-row"><span class="key">${key}</span><span class="value">${value}</span></div>
  `).join("");
}

function renderSecrets(secrets) {
  // The console knows secrets exist, but only ever renders a masked placeholder.
  secretList.innerHTML = Object.keys(secrets).map((name) => `
    <li class="secret"><span class="key">${name}</span><span class="masked">${maskSecret(secrets[name])}</span></li>
  `).join("");
}

async function load() {
  try {
    const [services, flags, migrations, config, secrets] = await Promise.all([
      fetch("data/services.json").then((r) => r.json()),
      fetch("data/flags.json").then((r) => r.json()),
      fetch("data/migrations.json").then((r) => r.json()),
      fetch("data/config.prod.json").then((r) => r.json()),
      fetch("data/secrets.json").then((r) => r.json())
    ]);
    renderServices(services);
    renderFlags(flags);
    renderMigrations(migrations);
    renderConfig(config);
    renderSecrets(secrets);
  } catch (cause) {
    showError("Could not load release data. Serve the folder so the data/ files resolve.");
  }
}

load();
