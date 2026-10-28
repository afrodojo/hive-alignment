const STORAGE_KEY = 'hive_daily_internalized';

export const DAILY_GOAL = 5;

function dayKey(now = new Date()) {
  const pad = (n) => String(n).padStart(2, '0');
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
}

/** Card ids internalized today (local calendar day). */
export function readDailyInternalized() {
  try {
    const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null');
    if (parsed?.date === dayKey() && Array.isArray(parsed.cardIds)) return parsed.cardIds;
  } catch (error) {
    console.debug('Daily habit log unavailable:', error);
  }
  return [];
}

/** Record a digest for today and return the day's updated card ids. */
export function logDailyInternalized(cardId) {
  const cardIds = readDailyInternalized();
  if (cardIds.includes(cardId)) return cardIds;

  const next = [...cardIds, cardId];
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ date: dayKey(), cardIds: next }));
  } catch (error) {
    console.debug('Daily habit log unavailable:', error);
  }
  return next;
}