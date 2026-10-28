import { PHASE_COPY } from '@/lib/breathing';

export default function BreathHalo({ phase, seconds }) {
  const motion = {
    transform: `scale(${phase.scale})`,
    opacity: 0.55 + 0.45 * phase.scale,
    transitionProperty: 'transform, opacity',
    // Holds sit still; inhale/exhale breathe over the full phase window.
    transitionDuration: `${phase.key === 'hold' ? 260 : phase.seconds * 1000}ms`,
    transitionTimingFunction: 'cubic-bezier(0.4, 0, 0.6, 1)',
  };

  return (
    <div className="relative flex h-56 w-56 items-center justify-center">
      <div className="absolute inset-0 rounded-full bg-emerald-500/10 blur-3xl" style={motion} />
      <div
        className="absolute inset-0 rounded-full border border-emerald-400/20 bg-gradient-to-b from-emerald-400/10 via-cyan-400/[0.06] to-transparent shadow-[0_0_80px_-18px_rgba(34,211,238,0.6)]"
        style={motion}
      />
      <div
        className="absolute inset-5 rounded-full border border-cyan-300/15"
        style={motion}
      />
      <div className="absolute inset-10 rounded-full border border-emerald-300/10" style={motion} />

      <div className="relative z-10 flex flex-col items-center px-3">
        <p className="text-[13px] leading-snug tracking-[0.02em] text-emerald-50/80">
          {PHASE_COPY[phase.key]}
        </p>
        <p className="mt-3 font-mono text-[40px] font-light leading-none tabular-nums text-slate-100">
          {seconds}
          <span className="ml-0.5 align-super text-[12px] font-normal text-slate-500">s</span>
        </p>
      </div>
    </div>
  );
}