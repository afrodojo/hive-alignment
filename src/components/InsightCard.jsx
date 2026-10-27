import { Clock3, Code2 } from 'lucide-react';
import DomainBadge from '@/components/DomainBadge';
import ProofBlock from '@/components/ProofBlock';
import { GITHUB_REPO_URL, LIVE_SITE_URL, commitUrl, fileUrl, liveSiteHost } from '@/lib/github';
import { domainMeta } from '@/lib/domains';
import { cn } from '@/lib/utils';
import { formatSeconds } from '@/lib/format';

export default function InsightCard({ card, position, total, className }) {
  const meta = domainMeta(card.domain);
  const isResearch = card.domain === 'CS_RESEARCH';
  const repoUrl = card.repo_url || GITHUB_REPO_URL;
  const liveUrl = card.live_site_url || LIVE_SITE_URL;

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

        {isResearch && (card.commit_hash || card.external_reference) && (
          <div className="mt-4 flex flex-wrap items-center gap-1.5">
            {card.commit_hash && (
              <a
                href={commitUrl(card.commit_hash)}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1 rounded border border-slate-700/80 bg-black/50 px-1.5 py-1 font-mono text-[9.5px] tracking-[0.04em] text-emerald-300/90 transition hover:border-emerald-500/40 hover:text-emerald-200"
              >
                <Code2 className="h-2.5 w-2.5" />
                commit [{card.commit_hash}]
              </a>
            )}
            {card.external_reference && (
              <a
                href={fileUrl(card.external_reference)}
                target="_blank"
                rel="noreferrer"
                className="max-w-full truncate rounded border border-slate-800 bg-black/40 px-1.5 py-1 font-mono text-[9.5px] tracking-[0.02em] text-slate-500 transition hover:border-slate-700 hover:text-slate-300"
              >
                {card.external_reference}
              </a>
            )}
          </div>
        )}

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

        {card.proof_or_code && <ProofBlock value={card.proof_or_code} />}
      </div>

      {isResearch && (
        <a
          href={liveUrl}
          target="_blank"
          rel="noreferrer"
          className="mx-5 mb-3 flex shrink-0 items-center justify-center gap-1.5 rounded-xl border border-emerald-500/25 bg-emerald-950/20 px-3 py-2 font-mono text-[9px] uppercase tracking-[0.14em] text-emerald-300/90 transition hover:border-emerald-500/45 hover:bg-emerald-950/40 hover:text-emerald-200"
        >
          Inspect live on {liveSiteHost(liveUrl)} ↗
        </a>
      )}

      <footer className="flex shrink-0 items-center justify-between border-t border-slate-800 px-5 py-3 font-mono text-[10px] uppercase tracking-[0.16em] text-slate-600">
        <span>
          {typeof position === 'number' && total ? `Card ${position} of ${total}` : meta.focus}
        </span>
        <span>{formatSeconds(card.read_time_seconds)} read</span>
      </footer>
    </article>
  );
}