import { useCallback, useEffect, useState } from 'react';

/** The two sprint protocols: deep-work window, then enforced reset window. */
export const FOCUS_PRESETS = [
  { id: 'tactical', label: 'Tactical Sprint', short: '25 / 5', work: 25 * 60, rest: 5 * 60 },
  { id: 'architect', label: 'Architect Deep Block', short: '50 / 10', work: 50 * 60, rest: 10 * 60 },
];

export function formatClock(totalSeconds = 0) {
  const safe = Math.max(0, Math.round(totalSeconds));
  return `${String(Math.floor(safe / 60)).padStart(2, '0')}:${String(safe % 60).padStart(2, '0')}`;
}

/**
 * Sprint timer. A finished work window locks the feed for the reset window,
 * then the next sprint starts automatically.
 */
export function useFocusTimer() {
  const [presetId, setPresetId] = useState('tactical');
  const [phase, setPhase] = useState('idle'); // idle | work | break
  const [endsAt, setEndsAt] = useState(0);
  const [remaining, setRemaining] = useState(0);

  const preset = FOCUS_PRESETS.find((p) => p.id === presetId) ?? FOCUS_PRESETS[0];

  useEffect(() => {
    if (phase === 'idle' || !endsAt) return undefined;

    const tick = () => {
      const left = Math.max(0, Math.round((endsAt - Date.now()) / 1000));
      setRemaining(left);
      if (left > 0) return;

      const nextPhase = phase === 'work' ? 'break' : 'work';
      const seconds = nextPhase === 'break' ? preset.rest : preset.work;
      setPhase(nextPhase);
      setEndsAt(Date.now() + seconds * 1000);
      setRemaining(seconds);
    };

    tick();
    const id = setInterval(tick, 500);
    return () => clearInterval(id);
  }, [phase, endsAt, preset.rest, preset.work]);

  const start = useCallback(() => {
    setPhase('work');
    setEndsAt(Date.now() + preset.work * 1000);
    setRemaining(preset.work);
  }, [preset.work]);

  const stop = useCallback(() => {
    setPhase('idle');
    setEndsAt(0);
    setRemaining(0);
  }, []);

  // Switching protocols mid-session restarts the work window at the new length.
  const selectPreset = (id) => {
    const next = FOCUS_PRESETS.find((p) => p.id === id);
    if (!next) return;
    setPresetId(id);
    if (phase !== 'idle') {
      setPhase('work');
      setEndsAt(Date.now() + next.work * 1000);
      setRemaining(next.work);
    }
  };

  const endBreak = () => {
    setPhase('work');
    setEndsAt(Date.now() + preset.work * 1000);
    setRemaining(preset.work);
  };

  return {
    active: phase !== 'idle',
    phase,
    preset,
    presetId,
    remaining,
    total: phase === 'break' ? preset.rest : preset.work,
    start,
    stop,
    selectPreset,
    endBreak,
  };
}