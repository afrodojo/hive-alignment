import { CheckCircle2, Crosshair, X } from 'lucide-react';
import DomainBadge from '@/components/DomainBadge';
import ProofBlock from '@/components/ProofBlock';

/** Full-screen interruption: one invariant, one operational action, nothing else. */
export default function EmergencyRecenter({ card, mastered, onMaster, onClose }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/97 px-5 backdrop-blur-sm">
      <div className="relative flex w-full max-w-sm flex-col">
        <button
          type="button"
          onClick={onClose}
          aria-label="Close re-center"
          className="absolute -top-10 right-0 flex h-8 w-8 items-center justify-center rounded-full border border-slate-800 bg-slate-900/70 text-slate-500 transition hover:text-slate-200"
        >
          <X className="h-4 w-4" />
        </button>

        <div className="flex items-center gap-2">
          <Crosshair className="h-3.5 w-3.5 text-rose-400" />
          <DomainBadge domain={card.domain} />
        </div>

        <h2 className="mt-4 text-[21px] font-semibold leading-snug tracking-tight text-white">
          {card.title}
        </h2>

        {card.proof_or_code ? (
          <ProofBlock value={card.proof_or_code} />
        ) : (
          <p className="mt-4 text-[13.5px] leading-relaxed text-slate-300">{card.core_insight}</p>
        )}

        <button
          type="button"
          onClick={onMaster}
          className="mt-6 flex items-center justify-center gap-2 rounded-xl border border-emerald-500/40 bg-emerald-500/10 py-3 font-mono text-[10px] uppercase tracking-[0.18em] text-emerald-300 transition hover:bg-emerald-500/20 active:scale-[0.99]"
        >
          <CheckCircle2 className="h-4 w-4" />
          {mastered ? 'Internalized' : 'Internalize Invariant'}
        </button>
      </div>
    </div>
  );
}