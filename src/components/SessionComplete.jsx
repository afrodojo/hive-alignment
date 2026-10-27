import { ArrowRight, CheckCircle2, Bookmark, Flame } from 'lucide-react';
import { formatSeconds } from '@/lib/format';

export default function SessionComplete({
  mode,
  masteredCount,
  savedCount,
  sessionSeconds,
  streak,
  onClose,
  onRestart,
}) {
  if (mode === 'closed') {
    return (
      <div className="flex flex-1 flex-col items-center justify-center px-2 text-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-full border border-emerald-500/30 bg-emerald-950/30">
          <span className="h-2 w-2 rounded-full bg-emerald-400" />
        </div>
        <h2 className="mt-6 text-2xl font-semibold tracking-tight text-white">Feed closed.</h2>
        <p className="mt-2 max-w-[16rem] text-[13px] leading-relaxed text-slate-500">
          Nothing else is queued. Go build, teach, or pray — the next insight will still be here.
        </p>
        <button
          type="button"
          onClick={onRestart}
          className="mt-8 font-mono text-[10px] uppercase tracking-[0.22em] text-slate-500 underline decoration-slate-800 underline-offset-4 transition hover:text-slate-200"
        >
          Begin another session
        </button>
      </div>
    );
  }

  const stats = [
    { icon: CheckCircle2, label: 'Internalized', value: masteredCount, tone: 'text-emerald-400' },
    { icon: Bookmark, label: 'Saved', value: savedCount, tone: 'text-amber-400' },
    { icon: Flame, label: 'Streak', value: streak ?? 0, tone: 'text-amber-400' },
  ];

  return (
    <div className="flex flex-1 flex-col justify-center">
      <p className="font-mono text-[9px] uppercase tracking-[0.26em] text-emerald-400/80">Session complete</p>
      <h2 className="mt-3 text-[30px] font-semibold leading-tight tracking-tight text-white">
        Close the feed.<br />Keep the anchor.
      </h2>
      <p className="mt-3 text-[13px] leading-relaxed text-slate-500">
        You read for {formatSeconds(sessionSeconds)} instead of scrolling. That is the whole point.
      </p>

      <div className="mt-7 grid grid-cols-3 gap-2">
        {stats.map(({ icon: Icon, label, value, tone }) => (
          <div key={label} className="rounded-xl border border-slate-800 bg-slate-900/50 p-3">
            <Icon className={`h-3.5 w-3.5 ${tone}`} />
            <p className="mt-2 text-xl font-semibold tracking-tight text-white">{value}</p>
            <p className="mt-0.5 font-mono text-[8.5px] uppercase tracking-[0.12em] text-slate-600">{label}</p>
          </div>
        ))}
      </div>

      <button
        type="button"
        onClick={onClose}
        className="mt-8 flex h-12 items-center justify-center gap-2 rounded-xl border border-slate-700 bg-slate-100 font-mono text-[10px] uppercase tracking-[0.2em] text-slate-950 transition hover:bg-white active:scale-[0.99]"
      >
        Exit focus mode <ArrowRight className="h-3.5 w-3.5" />
      </button>
      <button
        type="button"
        onClick={onRestart}
        className="mt-3 font-mono text-[9px] uppercase tracking-[0.22em] text-slate-600 transition hover:text-slate-400"
      >
        Continue — 5 more cards
      </button>
    </div>
  );
}