/** A meeting counts as imminent once it starts inside this window (next 20 minutes). */
export const PRIMING_WINDOW_MS = 20 * 60 * 1000;

/** A meeting that just started still primes the feed for the first 5 minutes. */
export const PRIMING_GRACE_MS = 5 * 60 * 1000;

export const PRIMING_DOMAINS = [
  'CYBER_DEFENSE',
  'CS_RESEARCH',
  'BIZ_ACUMEN',
  'COMMUNITY_UPLIFT',
  'SPIRITUAL_PILLARS',
];

/**
 * Keyword rules, checked in order — the first domain with a matching term wins.
 * Anything unmatched is treated as general focus (SPIRITUAL_PILLARS).
 */
export const DOMAIN_TERMS = [
  {
    domain: 'CYBER_DEFENSE',
    terms: ['cmmc', 'dod', 'defense', 'stig', 'zero trust', 'nist', 'fedramp'],
  },
  {
    domain: 'CS_RESEARCH',
    terms: ['dissertation', 'advisor', 'tla+', 'bft', 'swarm', 'agent', 'consensus', 'doctoral'],
  },
  {
    domain: 'BIZ_ACUMEN',
    terms: ['investor', 'client', 'contract', 'margin', 'pricing', 'capture', 'proposal'],
  },
  {
    domain: 'COMMUNITY_UPLIFT',
    terms: ['mentorship', 'stem', 'pipeline', 'fraternity', 'omega', 'uplift'],
  },
];

/**
 * Classify a meeting's title and description into one of the five focus domains.
 * The domain matching the most terms wins; ties fall back to rule order.
 */
export function classifyMeetingDomain({ title, description } = {}) {
  const text = `${title ?? ''} ${description ?? ''}`.toLowerCase();

  let best = 'SPIRITUAL_PILLARS';
  let bestHits = 0;
  for (const { domain, terms } of DOMAIN_TERMS) {
    const hits = terms.filter((term) => text.includes(term)).length;
    if (hits > bestHits) {
      best = domain;
      bestHits = hits;
    }
  }
  return best;
}



/**
 * Move a card of the primed domain to the head of the session, pulling one in
 * from the library when the session has none. Length is preserved.
 */
export function pinPrimedCard(session = [], domain, allCards = []) {
  if (!domain || !session.length) return session;

  const inSession = session.find((c) => c.domain === domain);
  if (inSession) return [inSession, ...session.filter((c) => c.id !== inSession.id)];

  const spare = allCards.find(
    (c) => c.domain === domain && !session.some((s) => s.id === c.id)
  );
  if (!spare) return session;

  return [spare, ...session].slice(0, session.length);
}