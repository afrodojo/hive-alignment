import { cn } from '@/lib/utils';

export default function ContextPrimingBanner({ summary, domain, onClick }) {
  if (!summary) return null;

  const Tag = onClick ? 'button' : 'div';

  return (
    <Tag
      {...(onClick ? { type: 'button', onClick } : {})}
      className={cn(
        'animate-rise flex w-full items-center gap-2 rounded-lg border border-emerald-500/30 bg-emerald-950/40 px-3 py-2 text-left',
        onClick && 'transition hover:border-emerald-500/50 hover:bg-emerald-950/60'
      )}
    >
      <span className="relative flex h-1.5 w-1.5 shrink-0">
        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
        <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-emerald-400" />
      </span>
      <p className="truncate font-mono text-[9.5px] uppercase tracking-[0.1em] text-emerald-200">
        Context Priming: {summary}
        {domain && <span className="ml-1 text-cyan-300/90">({domain})</span>}
      </p>
    </Tag>
  );
}