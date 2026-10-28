export const DAILY_GOAL = 5;

/** The hive day rolls over at 04:00 local, not midnight. */
export const HIVE_DAY_START_HOUR = 4;

const STORAGE_KEY = 'hive_internalized_today';
const PAT_KEYS = ['github_pat', 'hive_github_pat', 'GITHUB_PAT'];
export const DIGEST_REPO = 'afrodojo/hive-alignment';
const DIGEST_BRANCH = 'main';

/** Most recent 04:00 boundary at or before `now`. */
export function hiveDayStart(now = new Date()) {
  const start = new Date(now);
  if (start.getHours() < HIVE_DAY_START_HOUR) start.setDate(start.getDate() - 1);
  start.setHours(HIVE_DAY_START_HOUR, 0, 0, 0);
  return start;
}

/** YYYY-MM-DD label of the current hive day. */
export function hiveDayKey(now = new Date()) {
  const start = hiveDayStart(now);
  const pad = (n) => String(n).padStart(2, '0');
  return `${start.getFullYear()}-${pad(start.getMonth() + 1)}-${pad(start.getDate())}`;
}

function write(entries) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
  } catch (error) {
    console.debug('Telemetry log unavailable:', error);
  }
}

/** Entries recorded since the last 04:00 rollover; older ones are dropped. */
export function readInternalizedToday(now = new Date()) {
  let stored;
  try {
    stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
  } catch (error) {
    console.debug('Telemetry log unavailable:', error);
    return [];
  }
  if (!Array.isArray(stored)) return [];

  const start = hiveDayStart(now).getTime();
  const today = stored.filter((entry) => {
    const at = new Date(entry?.timestamp).getTime();
    return Number.isFinite(at) && at >= start;
  });
  // The counter resets itself the moment 04:00 passes.
  if (today.length !== stored.length) write(today);
  return today;
}

/** Append one internalized card to today's local record. */
export function recordInternalized(card, now = new Date()) {
  const today = readInternalizedToday(now);
  const entry = {
    card_id: card?.commit_hash || card?.title,
    domain: card?.domain,
    title: card?.title,
    core_insight: card?.core_insight,
    timestamp: now.toISOString(),
  };
  if (!entry.card_id || today.some((e) => e.card_id === entry.card_id)) return today;

  const next = [...today, entry];
  write(next);
  return next;
}

/** The end-of-day payload the nightly sync commits to the repo. */
export function buildDigest(entries = [], now = new Date()) {
  const digestDate = hiveDayKey(now);
  return {
    path: `data/telemetry/digest-${digestDate}.json`,
    payload: {
      digest_date: digestDate,
      generated_at: now.toISOString(),
      source: 'hive-alignment',
      repo: DIGEST_REPO,
      total: entries.length,
      invariants: entries,
    },
  };
}

/** GitHub personal access token, when the operator has stored one. */
export function readGithubPat() {
  for (const key of PAT_KEYS) {
    try {
      const value = localStorage.getItem(key);
      if (value) return value.trim();
    } catch (error) {
      console.debug('GitHub token lookup unavailable:', error);
    }
  }
  return null;
}

function toBase64(text) {
  const bytes = new TextEncoder().encode(text);
  let binary = '';
  bytes.forEach((byte) => {
    binary += String.fromCharCode(byte);
  });
  return btoa(binary);
}

/** Commit the digest straight to the public research repo. */
export async function commitDigest(payload, path, token) {
  const url = `https://api.github.com/repos/${DIGEST_REPO}/contents/${path}`;
  const headers = {
    Authorization: `Bearer ${token}`,
    Accept: 'application/vnd.github+json',
    'Content-Type': 'application/json',
  };

  // An existing digest for the day must be updated, which needs its blob sha.
  const existing = await fetch(`${url}?ref=${DIGEST_BRANCH}`, { headers });
  let sha;
  if (existing.ok) sha = (await existing.json()).sha;
  else if (existing.status !== 404) throw new Error(`GitHub replied ${existing.status}`);

  const body = {
    message: `chore(telemetry): digest ${payload.digest_date}`,
    content: toBase64(JSON.stringify(payload, null, 2)),
    branch: DIGEST_BRANCH,
    ...(sha ? { sha } : {}),
  };

  const res = await fetch(url, { method: 'PUT', headers, body: JSON.stringify(body) });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.message || `GitHub replied ${res.status}`);
  }
  return res.json();
}