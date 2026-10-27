import { DOMAIN_ORDER, domainMeta } from '@/lib/domains';

export default function AlignmentPanel({ counts, total }) {
  const max = Math.max(1, ...DOMAIN_ORDER.map((d) => counts[d] || 0));

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/40 p-4">
      <div className="flex items-baseline justify-between">
        <h2 className="font-mono text-[9px] uppercase tracking-[0.24em] text-slate-500">Alignment</h2>
        <span className="font-mono text-[9px] tracking-[0.1em] text-slate-600">{total} signals</span>
      </div>
      <div className="mt-4 space-y-2.5">
        {DOMAIN_ORDER.map((key) => {
          const meta = domainMeta(key);
          const value = counts[key] || 0;
          return (
            <div key={key} className="flex items-center gap-3">
              <span className="w-20 shrink-0 font-mono text-[9px] uppercase tracking-[0.1em] text-slate-500">
                {meta.shortLabel}
              </span>
              <div className="h-1 flex-1 overflow-hidden rounded-full bg-slate-800">
                <div
                  className={`h-full rounded-full ${meta.bar} transition-all duration-500`}
                  style={{ width: `${Math.round((value / max) * 100)}%` }}
                />
              </div>
              <span className="w-4 text-right font-mono text-[9px] text-slate-600">{value}</span>
            </div>
          );
        })}
      </div>
    </section>
  );
}