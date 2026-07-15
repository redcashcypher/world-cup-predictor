const API_BASE = "http://127.0.0.1:8000";

async function getJson(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    throw new Error(`${path} failed: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

/** GET /api/v1/fixtures -> { data: Match[] } */
export function fetchFixtures() {
  return getJson("/api/v1/fixtures");
}

/** GET /api/v1/golden-boot -> { data: Player[] } */
export function fetchGoldenBoot() {
  return getJson("/api/v1/golden-boot");
}

/**
 * GET /api/v1/bracket -> { rounds: Round[] }
 * Round = { round: string, matches: Match[] }, each round having half
 * the matches of the previous one, in bracket-position order.
 * This endpoint doesn't exist yet on the backend — returns null
 * instead of throwing so the UI can hide the bracket section
 * gracefully until the knockout stage is implemented.
 */
export async function fetchBracket() {
  try {
    return await getJson("/api/v1/bracket");
  } catch {
    return null;
  }
}
