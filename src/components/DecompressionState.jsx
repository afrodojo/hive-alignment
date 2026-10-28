import HoldToConfirmButton from '@/components/HoldToConfirmButton';
import { formatClock } from '@/lib/focusSession';

export default function DecompressionState({ remaining = 0, onOverride }) {
  return (
    <div className="animate-rise flex flex-1 flex-col items-center justify-center rounded-2xl border border-cyan-500/15 bg-black/50 px-6 py-8 text-center">
      <div className="relative flex h-44 w-44 items-center justify-center">
        <span className="breathe-ring absolute h-44 w-44 rounded-full border border-cyan-400/20 bg-cyan-500/5" />
        <span className="breathe-ring absolute h-28 w-28 rounded-full border border-cyan-400/25 bg-cyan-500/10" />
        <span className="relative font-mono text-[10px] uppercase tracking-[0.22em] text-cyan-300/80">
          {formatClock(remaining)}
        </span>
      </div>

      <p className="mt-8 font-mono text-[9px] uppercase tracking-[0.26em] text-cyan-400/70">
        Decompression &amp; Reset
      </p>

      <h2 className="mt-3 max-w-[17rem] text-[19px] font-semibold leading-snug tracking-tight text-slate-100">
        Step away from the screen. Hydrate. Ground the physical posture.
      </h2>

      <p className="mt-2 font-mono text-[9px] uppercase tracking-[0.18em] text-slate-600">
        4s inhale · 4s hold · 4s exhale
      </p>

      <HoldToConfirmButton
        label="Override Reset"
        holdingLabel="Hold 2s to override"
        onConfirm={onOverride}
        className="mt-8 w-full max-w-[16rem]"
      />
    </div>
  );
}