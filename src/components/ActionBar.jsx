import { Bookmark, CheckCircle2, ChevronLeft, ChevronRight, Share2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function ActionBar({
  saved,
  mastered,
  canPrev,
  isLast,
  index,
  total,
  onSave,
  onMaster,
  onShare,
  onPrev,
  onNext,
  onDismiss,
}) {
  return (
    <div className="shrink-0 space-y-3">
      <div className="flex items-stretch gap-2">
        <button
          type="button"
          onClick={onSave}
          aria-label="Save insight"
          aria-pressed={saved}
          className={cn(
            'flex h-12 w-12 items-center justify-center rounded-xl border transition active:scale-95',
            saved
              ? 'border-amber-500/50 bg-amber-950/40 text-amber-400'
              : 'border-slate-800 bg-slate-900/60 text-slate-500 hover:border-slate-700 hover:text-slate-200'
          )}
        >
          <Bookmark className={cn('h-4 w-4', saved && 'fill-amber-400')} />
        </button>

        <button
          type="button"
          onClick={onMaster}
          className={cn(
            'flex h-12 flex-1 items-center justify-center gap-2 rounded-xl border font-mono text-[10px] uppercase tracking-[0.18em] transition active:scale-[0.99]',
            mastered
              ? 'border-emerald-500/60 bg-emerald-500/20 text-emerald-200'
              : 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300 hover:bg-emerald-500/20'
          )}
        >
          <CheckCircle2 className="h-4 w-4" />
          {mastered ? 'Internalized' : 'Internalize'}
        </button>

        <button
          type="button"
          onClick={onShare}
          aria-label="Share insight"
          className="flex h-12 w-12 items-center justify-center rounded-xl border border-slate-800 bg-slate-900/60 text-slate-500 transition hover:border-slate-700 hover:text-slate-200 active:scale-95"
        >
          <Share2 className="h-4 w-4" />
        </button>
      </div>

      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={onPrev}
          disabled={!canPrev}
          className="flex items-center gap-1 font-mono text-[10px] uppercase tracking-[0.16em] text-slate-500 transition enabled:hover:text-slate-200 disabled:opacity-30"
        >
          <ChevronLeft className="h-3.5 w-3.5" /> Prev
        </button>

        <div className="flex items-center gap-1.5">
          {Array.from({ length: total }).map((_, i) => (
            <span
              key={i}
              className={cn(
                'h-1 rounded-full transition-all duration-300',
                i === index ? 'w-4 bg-slate-300' : i < index ? 'w-1 bg-slate-600' : 'w-1 bg-slate-800'
              )}
            />
          ))}
        </div>

        <button
          type="button"
          onClick={onNext}
          className="flex items-center gap-1 font-mono text-[10px] uppercase tracking-[0.16em] text-slate-300 transition hover:text-white"
        >
          {isLast ? 'Finish' : 'Next Insight'} <ChevronRight className="h-3.5 w-3.5" />
        </button>
      </div>

      <button
        type="button"
        onClick={onDismiss}
        className="mx-auto block font-mono text-[9px] uppercase tracking-[0.24em] text-slate-700 transition hover:text-slate-500"
      >
        Not now
      </button>
    </div>
  );
}