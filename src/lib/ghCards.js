import { GITHUB_REPO_URL, LIVE_SITE_URL } from '@/lib/github';
import { DOMAIN_ORDER } from '@/lib/domains';
import { SEED_CARDS } from '@/data/seedCards';

export const GH_CARDS_CACHE_KEY = 'hive_cached_gh_cards_v2';
export const GH_CARDS_TTL_MS = 30 * 60 * 1000;

const CONTENTS_URL = 'https://api.github.com/repos/afrodojo/hive-alignment/contents/data/cards';
const RAW_BASE = 'https://raw.githubusercontent.com/afrodojo/hive-alignment/main/data/cards';

const toSeconds = (value) => {
  const seconds = Number(value);
  return Number.isFinite(seconds) && seconds > 0 ? seconds : 45;
};

/** Coerce one JSON object published in the repo into a feed card. */
function normalizeCard(raw, name) {
  if (!raw || typeof raw !== 'object' || !raw.title || !raw.core_insight) return null;
  return {
    id: `gh:${name}`,
    domain: DOMAIN_ORDER.includes(raw.domain) ? raw.domain : 'CS_RESEARCH',
    title: String(raw.title),
    hook: raw.hook ?? '',
    core_insight: String(raw.core_insight),
    takeaways: Array.isArray(raw.takeaways) ? raw.takeaways.filter(Boolean) : [],
    proof_or_code: raw.proof_or_code ?? '',
    read_time_seconds: toSeconds(raw.read_time_seconds),
    repo_url: raw.repo_url || GITHUB_REPO_URL,
    commit_hash: raw.commit_hash ? String(raw.commit_hash).slice(0, 7) : undefined,
    live_site_url: raw.live_site_url || LIVE_SITE_URL,
    external_reference: raw.external_reference || `data/cards/${name}`,
  };
}

export function readGitHubCache() {
  try {
    const parsed = JSON.parse(localStorage.getItem(GH_CARDS_CACHE_KEY) || 'null');
    if (!parsed || !Array.isArray(parsed.cards)) return null;
    return { cards: parsed.cards, fetchedAt: Number(parsed.fetched_at) || 0 };
  } catch {
    return null;
  }
}

export function readCachedGitHubCards() {
  return readGitHubCache()?.cards ?? [];
}

export function isGitHubCacheFresh(now = Date.now()) {
  const cache = readGitHubCache();
  return Boolean(cache && now - cache.fetchedAt < GH_CARDS_TTL_MS);
}

function writeGitHubCache(cards) {
  try {
    localStorage.setItem(GH_CARDS_CACHE_KEY, JSON.stringify({ cards, fetched_at: Date.now() }));
  } catch (error) {
    console.debug('Research card cache unavailable:', error);
  }
}

async function getJson(url) {
  const res = await fetch(url, { headers: { Accept: 'application/vnd.github+json' } });
  if (!res.ok) throw new Error(`GitHub responded ${res.status}`);
  return res.json();
}

async function readCardFile(file) {
  const url = file.download_url || `${RAW_BASE}/${file.name}`;
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`raw content responded ${res.status}`);
    const parsed = await res.json();
    if (Array.isArray(parsed)) {
      return parsed
        .map((entry, i) => normalizeCard(entry, `${file.name}-${i + 1}`))
        .filter(Boolean);
    }
    const single = normalizeCard(parsed, file.name);
    return single ? [single] : [];
  } catch (error) {
    console.debug(`Skipped ${file.name}:`, error.message);
    return [];
  }
}

/** Every research card JSON published under data/cards in the public repo. */
export async function fetchGitHubCards() {
  const listing = await getJson(CONTENTS_URL);
  const entries = Array.isArray(listing) ? listing : [listing];
  const files = entries.filter((entry) => entry?.type === 'file' && entry.name !== '.gitkeep');

  const seen = new Set();
  const groups = await Promise.all(files.map(readCardFile));
  return groups.flat().filter((card) => {
    if (seen.has(card.id)) return false;
    seen.add(card.id);
    return true;
  });
}

let inFlight = null;

/**
 * The 30-minute localStorage cache, or a fresh pull from GitHub.
 * `force` bypasses the cache — that is what the Sync Feed button uses.
 */
export function loadGitHubCards({ force = false } = {}) {
  const cache = readGitHubCache();
  if (!force && cache && Date.now() - cache.fetchedAt < GH_CARDS_TTL_MS) {
    return Promise.resolve({ cards: cache.cards, fromCache: true });
  }
  if (!force && inFlight) return inFlight;

  const run = fetchGitHubCards()
    .then((cards) => {
      writeGitHubCache(cards);
      return { cards, fromCache: false };
    })
    .finally(() => {
      inFlight = null;
    });

  inFlight = run;
  return run;
}

/** Static seeds for the four local domains plus whatever GitHub returned. */
export function mergeFeedCards(githubCards = []) {
  const seen = new Set(SEED_CARDS.map((card) => card.id));
  return [...SEED_CARDS, ...githubCards.filter((card) => card && !seen.has(card.id))];
}