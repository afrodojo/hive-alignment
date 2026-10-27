import { CalendarClock, GitCommitHorizontal } from 'lucide-react';
import { domainMeta } from '@/lib/domains';

export default function SignalBanner({ signal }) {
  const meta = domainMeta(signal.domain);
  const Icon = signal.source === 'GITHUB' ? GitCommitHorizontal : CalendarClock;

  return (
    <div className={`animate-rise flex items-center gap-2 rounded-lg border px-3 py-2 ${meta.badge}`}>
      <Icon className="h-3.5 w-3.5 shrink-0" />
      <p className="truncate font-mono text-[9.5px] uppercase tracking-[0.1em]">{signal.title}</p>
      <span className="ml-auto shrink-0 font-mono text-[8.5px] uppercase tracking-[0.12em] opacity-60">
        {meta.shortLabel}
      </span>
    </div>
  );
}