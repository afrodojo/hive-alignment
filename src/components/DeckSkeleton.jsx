export default function DeckSkeleton() {
  return (
    <div className="flex min-h-0 flex-1 flex-col rounded-2xl border border-slate-800 bg-slate-900/40 p-5">
      <div className="flex animate-pulse flex-col">
        <div className="h-5 w-32 rounded-full bg-slate-800" />
        <div className="mt-6 h-7 w-4/5 rounded bg-slate-800" />
        <div className="mt-3 h-4 w-3/5 rounded bg-slate-800/60" />
        <div className="mt-7 space-y-2.5">
          <div className="h-3 w-full rounded bg-slate-800/50" />
          <div className="h-3 w-11/12 rounded bg-slate-800/50" />
          <div className="h-3 w-3/4 rounded bg-slate-800/50" />
        </div>
        <div className="mt-8 space-y-2">
          <div className="h-2.5 w-40 rounded bg-slate-800/40" />
          <div className="h-2.5 w-52 rounded bg-slate-800/40" />
          <div className="h-2.5 w-44 rounded bg-slate-800/40" />
        </div>
        <div className="mt-8 h-24 w-full rounded-xl bg-black/40" />
      </div>
    </div>
  );
}