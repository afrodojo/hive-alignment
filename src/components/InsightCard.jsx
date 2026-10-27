import { Clock3 } from 'lucide-react';
import DomainBadge from '@/components/DomainBadge';
import { domainMeta } from '@/lib/domains';
import { cn } from '@/lib/utils';
import { formatSeconds } from '@/lib/format';

export default function InsightCard({ card, position, total, className }) {
  const meta = domainMeta(card.domain);

  return (
    <article
      className={cn(
        'relative flex min-h-0 flex-col overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/40 shadow-2xl shadow-black/60',
        className
      )}
    >
      <div className={cn('h-[2px] w-full shrink-0 bg-gradient-to-r to-transparent', meta.line)} />

      <div className="no-scrollbar flex-1 overflow-y-auto px-5 pb-6 pt-5">
        <div className="flex items-start justify-between gap-2">
          <DomainBadge domain={card.domain} />
          <span className="flex shrink-0 items-center gap-1 font-mono text-[10px] uppercase tracking-[0.14em] text-slate-600">
            <Clock3 className="h-3 w-3" /> {formatSeconds(card.read_time_seconds)}
          </span>
        </div>

        <h1 className="mt-5 text-[26px] font-semibold leading-[1.15] tracking-tight text-white text-balance">
          {card.title}
        </h1>

        <p className={cn('mt-3 border-l-2 pl-3 text-[13.5px] italic leading-relaxed text-slate-400', meta.rule)}>
          {card.hook}
        </p>

        <p className="mt-5 text-[14px] leading-[1.75] text-slate-300">{card.core_insight}</p>

        {card.takeaways?.length > 0 && (
          <div className="mt-6">
            <h2 className="font-mono text-[9px] uppercase tracking-[0.24em] text-slate-500">
              Actionable Principles
            </h2>
            <ul className="mt-3 space-y-2.5">
              {card.takeaways.map((point, i) => (
                <li key={i} className="flex gap-2.5 text-[13px] leading-relaxed text-slate-300">
                  <span className={cn('mt-[7px] h-1 w-1 shrink-0 rounded-full', meta.dot)} />
                  <span>{point}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {card.proof_or_code && (
          <div className="mt-6 overflow-hidden rounded-xl border border-slate-800 bg-black/60">
            <div className="flex items-center justify-between border-b border-slate-800/80 px-3 py-1.5">
              <span className="font-mono text-[9px] uppercase tracking-[0.2em] text-slate-600">
                Proof / Invariant
              </span>
              <span className="font-mono text-[9px] text-slate-700">mono</span>
            </div>
            <pre className="no-scrollbar overflow-x-auto px-3 py-3 font-mono text-[11px] leading-[1.7] text-slate-400">
              {card.proof_or_code}
            </pre>
          </div>
        )}
      </div>

      <footer className="flex shrink-0 items-center justify-between border-t border-slate-800 px-5 py-3 font-mono text-[10px] uppercase tracking-[0.16em] text-slate-600">
        <span>
          {typeof position === 'number' && total ? `Card ${position} of ${total}` : meta.focus}
        </span>
        <span>{formatSeconds(card.read_time_seconds)} read</span>
      </footer>
    </article>
  );
}