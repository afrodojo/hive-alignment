/**
 * The deck's category lanes. A key with `domains: null` is the unfiltered feed.
 * Focus covers community/uplift work, which includes the mental-health cards.
 */
export const CATEGORIES = [
  { key: 'ALL', label: 'All', domains: null },
  { key: 'ARMOR', label: 'Armor', domains: ['WARRIOR_ETHOS'] },
  { key: 'FOCUS', label: 'Focus', domains: ['COMMUNITY_UPLIFT'] },
  { key: 'CODE', label: 'Code', domains: ['CS_RESEARCH'] },
  { key: 'LEVERAGE', label: 'Leverage', domains: ['BIZ_ACUMEN'] },
  { key: 'PILLARS', label: 'Pillars', domains: ['SPIRITUAL_PILLARS', 'OMEGA_HISTORY'] },
];

/** Domains inside a category, or null for the unfiltered feed. */
export function categoryDomains(key) {
  return CATEGORIES.find((c) => c.key === key)?.domains ?? null;
}

/** Whether a card domain belongs to a category. */
export function categoryIncludes(key, domain) {
  const domains = categoryDomains(key);
  return !domains || domains.includes(domain);
}

/** The category a domain lives in (used by context priming). */
export function categoryForDomain(domain) {
  const match = CATEGORIES.find((c) => c.domains?.includes(domain));
  return match?.key ?? 'ALL';
}

export function cardsInCategory(cards = [], key) {
  const domains = categoryDomains(key);
  if (!domains) return cards;
  return cards.filter((card) => domains.includes(card.domain));
}

/** Card count per category, for the tab badges. */
export function categoryCounts(cards = []) {
  return CATEGORIES.reduce((acc, { key, domains }) => {
    acc[key] = domains ? cards.filter((card) => domains.includes(card.domain)).length : cards.length;
    return acc;
  }, {});
}