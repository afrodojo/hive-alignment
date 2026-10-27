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

/** ISO bounds for the 20-minute priming window around now — feed straight into a query. */
export function upcomingMeetingWindow(now = new Date()) {
  return {
    from: new Date(now.getTime() - PRIMING_GRACE_MS).toISOString(),
    to: new Date(now.getTime() + PRIMING_WINDOW_MS).toISOString(),
  };
}

/** The domain a meeting primes — stored value first, otherwise classified from its text. */
export function meetingPrimingDomain(meeting) {
  if (!meeting) return null;
  return (
    meeting.domain || classifyMeetingDomain({ title: meeting.summary, description: meeting.description })
  );
}

/** The soonest active meeting inside the window — starting soon, or just started. */
export function soonestMeeting(meetings = [], now = new Date()) {
  const candidates = meetings
    .filter((m) => m.active !== false && m.startTime)
    .map((m) => ({ meeting: m, startsAt: new Date(m.startTime) }))
    .filter(({ startsAt }) => !Number.isNaN(startsAt.getTime()))
    .filter(({ startsAt }) => {
      const delta = startsAt.getTime() - now.getTime();
      return delta <= PRIMING_WINDOW_MS && delta >= -PRIMING_GRACE_MS;
    })
    .sort((a, b) => a.startsAt - b.startsAt);

  return candidates[0]?.meeting || null;
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