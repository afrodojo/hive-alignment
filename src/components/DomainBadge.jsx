import { domainMeta } from '@/lib/domains';
import { cn } from '@/lib/utils';

export default function DomainBadge({ domain, compact = false, className }) {
  const meta = domainMeta(domain);
  const Icon = meta.icon;
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 font-mono uppercase',
        compact ? 'text-[9px] tracking-[0.14em]' : 'text-[10px] tracking-[0.16em]',
        meta.badge,
        className
      )}
    >
      <Icon className="h-3 w-3 shrink-0" strokeWidth={2} />
      {compact ? meta.shortLabel : meta.label}
    </span>
  );
}