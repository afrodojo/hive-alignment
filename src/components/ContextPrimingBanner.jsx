export default function ContextPrimingBanner({ summary, domain }) {
  if (!summary) return null;

  return (
    <div className="animate-rise flex items-center gap-2 rounded-lg border border-emerald-500/30 bg-emerald-950/40 px-3 py-2">
      <span className="relative flex h-1.5 w-1.5 shrink-0">
        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
        <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-emerald-400" />
      </span>
      <p className="truncate font-mono text-[9.5px] uppercase tracking-[0.1em] text-emerald-200">
        Context Priming: {summary}
        {domain && <span className="ml-1 text-cyan-300/90">({domain})</span>}
      </p>
    </div>
  );
}