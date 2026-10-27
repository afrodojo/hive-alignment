import { differenceInCalendarDays } from 'date-fns';
import { DOMAIN_ORDER } from '@/lib/domains';

export const DEFAULT_PREFERENCES = DOMAIN_ORDER.reduce((acc, key) => {
  acc[key] = 1;
  return acc;
}, {});

/** Collapse interaction history into the latest action per card id. */
export function latestActions(interactions = []) {
  const map = new Map();
  interactions.forEach((i) => {
    if (!i?.card_id || map.has(i.card_id)) return;
    map.set(i.card_id, i.action);
  });
  return map;
}

/**
 * Rank the library into a capped session: unread first, boosted by the user's
 * domain weights and any live calendar/GitHub signal, capped at two per domain.
 */
export function buildSession(cards, interactions, options = {}) {
  const { preferences = DEFAULT_PREFERENCES, signalDomains = [], size = 5, excludeIds = [] } = options;
  const latest = latestActions(interactions);
  const signals = new Set(signalDomains);

  const ranked = cards
    .filter((c) => !excludeIds.includes(c.id) && latest.get(c.id) !== 'MASTERED')
    .map((card) => {
      const action = latest.get(card.id);
      let score = 0;
      if (!action) score += 100;
      if (action === 'SAVED') score += 12;
      if (action === 'DISMISSED') score -= 45;
      score += (Number(preferences?.[card.domain]) || 1) * 6;
      if (signals.has(card.domain)) score += 90;
      return { card, score };
    })
    .sort((a, b) => b.score - a.score);

  const perDomain = {};
  const picked = [];
  for (const entry of ranked) {
    if (picked.length >= size) break;
    const d = entry.card.domain;
    if ((perDomain[d] || 0) >= 2) continue;
    perDomain[d] = (perDomain[d] || 0) + 1;
    picked.push(entry.card);
  }
  for (const entry of ranked) {
    if (picked.length >= size) break;
    if (!picked.some((c) => c.id === entry.card.id)) picked.push(entry.card);
  }
  return picked;
}

/** Today's streak given the stored user state. */
export function nextStreak(user, now = new Date()) {
  const streak = Number(user?.current_streak) || 0;
  if (!user?.last_active_at) return 1;
  const last = new Date(user.last_active_at);
  if (Number.isNaN(last.getTime())) return 1;
  const days = differenceInCalendarDays(now, last);
  if (days <= 0) return streak || 1;
  if (days === 1) return streak + 1;
  return 1;
}

/** Nudge one domain's weight after an interaction. */
export function bumpPreferences(preferences, domain, action) {
  const base = { ...DEFAULT_PREFERENCES, ...(preferences || {}) };
  const weights = { SAVED: 0.5, MASTERED: 1, DISMISSED: -0.5 };
  const delta = weights[action] ?? 0;
  base[domain] = Math.min(6, Math.max(0, Number(base[domain] || 1) + delta));
  return base;
}

export function sumReadTime(cards = []) {
  return cards.reduce((total, c) => total + (Number(c.read_time_seconds) || 0), 0);
}

export function activeSignalDomains(signals = [], now = new Date()) {
  return signals
    .filter((s) => s.status !== 'DONE')
    .filter((s) => !s.expires_at || new Date(s.expires_at) >= now)
    .map((s) => s.domain);
}

export function primarySignal(signals = [], now = new Date()) {
  const live = signals
    .filter((s) => s.status !== 'DONE')
    .filter((s) => !s.expires_at || new Date(s.expires_at) >= now);
  if (!live.length) return null;
  return live
    .slice()
    .sort((a, b) => new Date(a.expires_at || 0) - new Date(b.expires_at || 0))[0];
}