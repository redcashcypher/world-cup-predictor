/**
 * Wraps a promise so the caller waits at least `ms` before resolving,
 * even if the underlying request finishes instantly (common on
 * localhost). Keeps the Cubes loader on screen long enough to see.
 */
export function withMinDelay(promise, ms = 2500) {
  const delay = new Promise((resolve) => setTimeout(resolve, ms));
  return Promise.all([promise, delay]).then(([result]) => result);
}
