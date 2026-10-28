import { BREATH_MODES } from '@/lib/breathing';
import { cn } from '@/lib/utils';

export default function BreathModeSelector({ value, onChange }) {
  const active = BREATH_MODES.find((m) => m.id === value) ?? BREATH_MODES[0];

  return (
    <div className="w-full">
      <div className="mx-auto flex w-full max-w-[20rem] items-center gap-1 rounded-full border border-slate-800/80 bg-slate-900/40 p-1">
        {BREATH_MODES.map((mode) => (
          <button
            key={mode.id}
            type="button"
            onClick={() => onChange(mode.id)}
            aria-pressed={value === mode.id}
            className={cn(
              'flex-1 rounded-full px-2 py-2 font-mono text-[9px] uppercase tracking-[0.12em] transition',
              value === mode.id
                ? 'bg-emerald-500/15 text-emerald-200 shadow-[inset_0_0_0_1px_rgba(16,185,129,0.35)]'
                : 'text-slate-500 hover:text-slate-300'
            )}
          >
            {mode.label}
          </button>
        ))}
      </div>
      <p className="mt-2.5 font-mono text-[9px] uppercase tracking-[0.16em] text-slate-600">
        {active.hint} · {active.pattern}
      </p>
    </div>
  );
}