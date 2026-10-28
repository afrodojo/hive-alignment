import { CATEGORIES } from '@/lib/categories';
import { cn } from '@/lib/utils';

export default function CategoryTabs({ value, counts = {}, onChange }) {
  return (
    <div className="no-scrollbar -mx-1 shrink-0 overflow-x-auto px-1">
      <div className="flex w-max snap-x snap-mandatory items-center gap-1.5 py-0.5">
        {CATEGORIES.map(({ key, label }) => {
          const active = key === value;
          return (
            <button
              key={key}
              type="button"
              onClick={() => onChange(key)}
              aria-pressed={active}
              className={cn(
                'snap-start whitespace-nowrap rounded-full border px-3 py-1.5 font-mono text-[10px] uppercase tracking-[0.16em] transition',
                active
                  ? 'border-emerald-400/70 bg-slate-900 text-white shadow-[0_0_16px_-2px_rgba(16,185,129,0.55)] ring-1 ring-cyan-400/30'
                  : 'border-slate-800 bg-slate-900/40 text-slate-400 hover:border-slate-700 hover:text-slate-200'
              )}
            >
              {label}
              <span
                className={cn(
                  'ml-1.5 tabular-nums',
                  active ? 'text-cyan-300' : 'text-slate-600'
                )}
              >
                ({counts[key] ?? 0})
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}