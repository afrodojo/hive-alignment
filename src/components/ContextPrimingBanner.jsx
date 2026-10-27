import { CalendarClock } from 'lucide-react';
import { domainMeta } from '@/lib/domains';
import { cn } from '@/lib/utils';

export default function ContextPrimingBanner({ name, domain }) {
  if (!name) return null;
  const meta = domainMeta(domain);

  return (
    <div className={cn('animate-rise flex items-center gap-2 rounded-lg border px-3 py-2', meta.badge)}>
      <CalendarClock className="h-3.5 w-3.5 shrink-0" />
      <p className="truncate font-mono text-[9.5px] uppercase tracking-[0.1em]">
        Context Priming: {name}
      </p>
      <span className="ml-auto shrink-0 font-mono text-[8.5px] uppercase tracking-[0.12em] opacity-60">
        {meta.shortLabel}
      </span>
    </div>
  );
}