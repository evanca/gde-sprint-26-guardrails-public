// Pure, dependency-free helpers for the Release Guardrails Console.
// These render the dashboard; they never touch secrets in the clear.

export const ENVIRONMENTS = ["prod", "staging", "dev"];

export function groupByEnvironment(services) {
  const groups = Object.fromEntries(ENVIRONMENTS.map((env) => [env, []]));
  for (const service of services) {
    if (!groups[service.environment]) groups[service.environment] = [];
    groups[service.environment].push(service);
  }
  return groups;
}

export function countByStatus(services) {
  const counts = { healthy: 0, degraded: 0, down: 0, total: services.length };
  for (const service of services) {
    counts[service.status] = (counts[service.status] || 0) + 1;
  }
  return counts;
}

// Secrets are never shown in the clear, regardless of their stored value.
export function maskSecret(_value) {
  return "•".repeat(8);
}

export function flagState(flag) {
  return flag.enabled ? "on" : "off";
}
