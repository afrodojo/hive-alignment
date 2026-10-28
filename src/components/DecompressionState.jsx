import { useState } from 'react';
import HoldToConfirmButton from '@/components/HoldToConfirmButton';
import BreathHalo from '@/components/breath/BreathHalo';
import BreathModeSelector from '@/components/breath/BreathModeSelector';
import { BREATH_MODES, useBreathingEngine } from '@/lib/breathing';
import { formatClock } from '@/lib/focusSession';

export default function DecompressionState({ remaining = 0, onOverride }) {
  const [modeId, setModeId] = useState(BREATH_MODES[0].id);
  const { phase, secondsLeft } = useBreathingEngine(modeId);

  return (
    <div className="animate-rise flex flex-1 flex-col items-center justify-between rounded-2xl border border-slate-800/80 bg-slate-950 px-6 py-5 text-center">
      <div className="space-y-1">
        <p className="font-mono text-[9px] uppercase tracking-[0.26em] text-emerald-400/70">
          Decompression &amp; Reset
        </p>
        <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-slate-600">
          {formatClock(remaining)} until next sprint
        </p>
      </div>

      <BreathHalo phase={phase} seconds={secondsLeft} />

      <div className="w-full space-y-4">
        <BreathModeSelector value={modeId} onChange={setModeId} />
        <HoldToConfirmButton
          label="Override Reset"
          holdingLabel="Hold 2s to override"
          onConfirm={onOverride}
          className="mx-auto w-full max-w-[16rem]"
        />
      </div>
    </div>
  );
}