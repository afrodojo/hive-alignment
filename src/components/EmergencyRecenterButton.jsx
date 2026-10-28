import { Crosshair } from 'lucide-react';

export default function EmergencyRecenterButton({ onClick, className = '' }) {
  return (
    <button
      type="button"
      onClick={onClick}
      title="Emergency Re-Center"
      aria-label="Emergency Re-Center"
      className={`absolute bottom-36 right-3 z-30 flex w-16 flex-col items-center gap-1 rounded-2xl border border-rose-500/40 bg-slate-950/90 px-1.5 py-2 text-rose-300 shadow-lg shadow-rose-950/40 backdrop-blur transition hover:border-rose-400/70 hover:text-rose-200 active:scale-95 ${className}`}
    >
      <Crosshair className="h-4 w-4" />
      <span className="font-mono text-[6.5px] uppercase leading-tight tracking-[0.12em]">Re-Center</span>
    </button>
  );
}