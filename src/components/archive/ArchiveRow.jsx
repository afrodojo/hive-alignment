import { Bookmark, CheckCircle2, EyeOff } from 'lucide-react';
import DomainBadge from '@/components/DomainBadge';
import { format } from 'date-fns';

const ACTION_META = {
  SAVED: { icon: Bookmark, label: 'Saved', className: 'text-amber-400/80' },
  MASTERED: { icon: CheckCircle2, label: 'Internalized', className: 'text-emerald-400/80' },
  DISMISSED: { icon: EyeOff, label: 'Passed', className: 'text-slate-500' },
};

export default function ArchiveRow({ card, action, onClick }) {
  const meta = ACTION_META[action] || ACTION_META.SAVED;
  const Icon = meta.icon;

  return (
    <button
      type="button"
      onClick={onClick}
      className="group w-full rounded-xl border border-slate-800 bg-slate-900/40 p-3.5 text-left transition hover:border-slate-700 hover:bg-slate-900/70"
    >
      <div className="flex items-center justify-between gap-2">
        <DomainBadge domain={card.domain} compact />
        <span className={`flex items-center gap-1 font-mono text-[9px] uppercase tracking-[0.14em] ${meta.className}`}>
          <Icon className="h-3 w-3" /> {meta.label}
        </span>
      </div>
      <p className="mt-2.5 text-[13.5px] font-medium leading-snug text-slate-100">{card.title}</p>
      <p className="mt-1 line-clamp-2 text-[12px] leading-relaxed text-slate-500">{card.hook}</p>
      {card.updated_date && (
        <p className="mt-2 font-mono text-[9px] uppercase tracking-[0.14em] text-slate-700">
          {format(new Date(card.updated_date), 'MMM d')}
        </p>
      )}
    </button>
  );
}