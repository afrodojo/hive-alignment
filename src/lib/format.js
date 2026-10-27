export function formatSeconds(total) {
  const s = Math.max(0, Math.round(Number(total) || 0));
  if (s < 60) return `${s}s`;
  const m = Math.floor(s / 60);
  const r = s % 60;
  return r ? `${m}m ${r}s` : `${m}m`;
}