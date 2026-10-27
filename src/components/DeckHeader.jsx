import { Link } from 'react-router-dom';
import { BookMarked, Flame, Timer } from 'lucide-react';
import { formatSeconds } from '@/lib/format';

export default function DeckHeader({ sessionSeconds, streak, archiveLink = true }) {
  return (
    <header className="flex shrink-0 items-center justify-between gap-2">
      <div className="flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-950/30 px-2.5 py-1">
        <span className="relative flex h-1.5 w-1.5">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
          <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-emerald-400" />
        </span>
        <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-emerald-300">Hive Focus</span>
      </div>

      <div className="flex items-center gap-2">
        <span className="flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-[0.1em] text-slate-500">
          <Timer className="h-3 w-3" /> {formatSeconds(sessionSeconds)}
        </span>
        <span className="flex items-center gap-1 rounded-full border border-amber-500/25 bg-amber-950/30 px-2 py-1 font-mono text-[10px] tracking-[0.06em] text-amber-400">
          <Flame className="h-3 w-3" /> {streak ?? 0}
        </span>
        {archiveLink && (
          <Link
            to="/archive"
            aria-label="Your archive"
            className="flex h-7 w-7 items-center justify-center rounded-full border border-slate-800 bg-slate-900/60 text-slate-500 transition hover:border-slate-700 hover:text-slate-200"
          >
            <BookMarked className="h-3.5 w-3.5" />
          </Link>
        )}
      </div>
    </header>
  );
}