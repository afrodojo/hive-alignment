import { Power } from 'lucide-react';
import { FOCUS_PRESETS } from '@/lib/focusSession';
import { cn } from '@/lib/utils';

export default function FocusModeToggle({ active, presetId, onToggle, onSelectPreset }) {
  return (
    <div className="flex items-center gap-1.5">
      <button
        type="button"
        onClick={onToggle}
        aria-pressed={active}
        className={cn(
          'flex items-center gap-1 rounded-full border px-2 py-1 font-mono text-[9px] uppercase tracking-[0.14em] transition active:scale-95',
          active
            ? 'border-emerald-400/60 bg-emerald-500/15 text-emerald-200 shadow-[0_0_14px_-4px_rgba(16,185,129,0.9)]'
            : 'border-slate-800 bg-slate-900/60 text-slate-500 hover:text-slate-300'
        )}
      >
        <Power className="h-2.5 w-2.5" />
        Focus
      </button>

      {FOCUS_PRESETS.map((preset) => {
        const selected = preset.id === presetId;
        return (
          <button
            key={preset.id}
            type="button"
            onClick={() => onSelectPreset(preset.id)}
            title={preset.label}
            aria-pressed={selected}
            className={cn(
              'rounded-full border px-2 py-1 font-mono text-[9px] tabular-nums tracking-[0.08em] transition active:scale-95',
              selected
                ? 'border-cyan-400/40 bg-cyan-500/10 text-cyan-300'
                : 'border-slate-800 bg-slate-900/40 text-slate-600 hover:text-slate-400'
            )}
          >
            {preset.short}
          </button>
        );
      })}
    </div>
  );
}