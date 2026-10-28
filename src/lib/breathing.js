import { useEffect, useState } from 'react';

/**
 * Adaptive breath protocols. `scale` is the halo radius each phase drives to:
 * inhale expands to full, exhale contracts back to baseline.
 */
export const BREATH_MODES = [
  {
    id: 'focus_reset',
    label: 'Focus Reset',
    hint: 'Box',
    pattern: '4s inhale · 4s hold · 4s exhale · 4s hold',
    phases: [
      { key: 'inhale', seconds: 4, scale: 1 },
      { key: 'hold', seconds: 4, scale: 1 },
      { key: 'exhale', seconds: 4, scale: 0.52 },
      { key: 'hold', seconds: 4, scale: 0.52 },
    ],
  },
  {
    id: 'vagal_downshift',
    label: 'Vagal Downshift',
    hint: '4-7-8',
    pattern: '4s inhale · 7s hold · 8s exhale',
    phases: [
      { key: 'inhale', seconds: 4, scale: 1 },
      { key: 'hold', seconds: 7, scale: 1 },
      { key: 'exhale', seconds: 8, scale: 0.52 },
    ],
  },
];

export const PHASE_COPY = {
  inhale: 'Inhale through nose',
  hold: 'Hold stillness',
  exhale: 'Long slow exhale',
};

export function breathMode(id) {
  return BREATH_MODES.find((m) => m.id === id) ?? BREATH_MODES[0];
}

const HAPTICS = {
  inhale: 14,
  hold: 8,
  exhale: 22,
};

/** Subtle phase-change vibration where the browser supports it. */
function haptic(key) {
  if (typeof navigator === 'undefined' || typeof navigator.vibrate !== 'function') return;
  try {
    navigator.vibrate(HAPTICS[key] ?? 12);
  } catch {
    /* vibration is a nicety, never a failure */
  }
}

/** Advances through the mode's phases, one second-count per phase. */
export function useBreathingEngine(modeId) {
  const mode = breathMode(modeId);
  const [phaseIndex, setPhaseIndex] = useState(0);
  const [startedAt, setStartedAt] = useState(() => Date.now());
  const [now, setNow] = useState(() => Date.now());

  // Switching protocols restarts the cycle from the first inhale.
  useEffect(() => {
    setPhaseIndex(0);
    setStartedAt(Date.now());
    setNow(Date.now());
  }, [modeId]);

  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 100);
    return () => clearInterval(id);
  }, []);

  const phase = mode.phases[phaseIndex] ?? mode.phases[0];
  const elapsed = Math.max(0, (now - startedAt) / 1000);

  useEffect(() => {
    if (elapsed < phase.seconds) return;
    const nextIndex = (phaseIndex + 1) % mode.phases.length;
    setPhaseIndex(nextIndex);
    setStartedAt((prev) => prev + phase.seconds * 1000);
    haptic(mode.phases[nextIndex].key);
  }, [elapsed, phase.seconds, phaseIndex, mode]);

  return {
    mode,
    phase,
    secondsLeft: Math.max(1, Math.ceil(phase.seconds - elapsed)),
  };
}