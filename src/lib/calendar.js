import { base44 } from '@/api/base44Client';

/** A meeting counts as imminent once it starts inside this window. */
export const PRIMING_WINDOW_MS = 15 * 60 * 1000;

export const PRIMING_DOMAINS = [
  'CYBER_DEFENSE',
  'CS_RESEARCH',
  'BIZ_ACUMEN',
  'COMMUNITY_UPLIFT',
  'SPIRITUAL_PILLARS',
];

const DOMAIN_BRIEF = `
- CYBER_DEFENSE: security operations, threat intelligence, zero-trust architecture, incident response, adversary TTPs, controls and compliance, red/blue teaming.
- CS_RESEARCH: computer science research, algorithms, distributed systems, consensus, formal methods, ML or data engineering, academic and lab work.
- BIZ_ACUMEN: business execution, GovCon captures, proposals, pricing and margins, contracts, hiring, leadership, client relationships.
- BIZ_ACUMEN also covers revenue, partnerships, and operational scaling.
- COMMUNITY_UPLIFT: mentorship, education, nonprofits, workforce pipelines, equity, community programs.
- SPIRITUAL_PILLARS: faith, prayer, character, ethics, service, family, spiritual study.
`.trim();

const CLASSIFIER_SCHEMA = {
  type: 'object',
  properties: {
    domain: { type: 'string', enum: PRIMING_DOMAINS },
    rationale: { type: 'string', description: 'One short clause naming the signal that decided it.' },
  },
  required: ['domain', 'rationale'],
};

const domainCache = new Map();

/** Classify a meeting's title and description into one of the five focus domains. */
export async function classifyMeetingDomain({ title, description } = {}) {
  const body = [title, description].filter(Boolean).join('\n\n').slice(0, 1600);
  if (!body.trim()) return 'CS_RESEARCH';

  const result = await base44.integrations.Core.InvokeLLM({
    prompt: `You classify an upcoming calendar meeting so a micro-learning feed can prime the reader before it starts.

Pick exactly one domain from these five:
${DOMAIN_BRIEF}

Rules:
- Judge from the title, description, agenda, attendees, and project codenames present in the text.
- Prefer the domain the participant must be sharpest in during the meeting, not the department hosting it.
- Use CS_RESEARCH only when nothing else genuinely fits.
- Return the domain and a rationale of at most 12 words.

MEETING
Title: ${title || '(none)'}
Description: ${description || '(none)'}`,
    response_json_schema: CLASSIFIER_SCHEMA,
  });

  const domain = result?.domain;
  return PRIMING_DOMAINS.includes(domain) ? domain : 'CS_RESEARCH';
}

/** Classify once per signal; repeat renders reuse the verdict. */
export async function resolvePrimingDomain(signal) {
  if (!signal) return null;
  if (domainCache.has(signal.id)) return domainCache.get(signal.id);
  const domain = await classifyMeetingDomain({ title: signal.title, description: signal.detail });
  domainCache.set(signal.id, domain);
  return domain;
}

/** The calendar event starting inside the priming window, earliest first. */
export function primingEvent(signals = [], now = new Date()) {
  const candidates = signals
    .filter((s) => s.source === 'CALENDAR' && s.status !== 'DONE' && s.starts_at)
    .map((s) => ({ signal: s, startsAt: new Date(s.starts_at) }))
    .filter(({ startsAt }) => !Number.isNaN(startsAt.getTime()))
    .filter(({ startsAt }) => startsAt.getTime() - now.getTime() <= PRIMING_WINDOW_MS)
    .sort((a, b) => a.startsAt - b.startsAt);

  const next = candidates.find(({ startsAt }) => startsAt.getTime() - now.getTime() >= 0);
  return next || null;
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