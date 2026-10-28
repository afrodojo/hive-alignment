import { useEffect, useRef, useState } from 'react';
import { cn } from '@/lib/utils';

const HOLD_MS = 2000;

/** A button that only fires after a continuous two-second press. */
export default function HoldToConfirmButton({ label, holdingLabel = 'Keep holding', onConfirm, className }) {
  const [progress, setProgress] = useState(0);
  const startedAt = useRef(0);
  const frame = useRef(0);

  const cancel = () => {
    if (frame.current) cancelAnimationFrame(frame.current);
    frame.current = 0;
    startedAt.current = 0;
    setProgress(0);
  };

  useEffect(() => () => cancelAnimationFrame(frame.current), []);

  const step = () => {
    const ratio = Math.min(1, (Date.now() - startedAt.current) / HOLD_MS);
    setProgress(ratio);

    if (ratio >= 1) {
      cancel();
      onConfirm();
      return;
    }
    frame.current = requestAnimationFrame(step);
  };

  const begin = (event) => {
    event.preventDefault();
    if (frame.current) return;
    startedAt.current = Date.now();
    frame.current = requestAnimationFrame(step);
  };

  return (
    <button
      type="button"
      onPointerDown={begin}
      onPointerUp={cancel}
      onPointerLeave={cancel}
      onPointerCancel={cancel}
      className={cn(
        'relative touch-none select-none overflow-hidden rounded-xl border px-4 py-3 font-mono text-[10px] uppercase tracking-[0.18em] transition',
        'border-cyan-500/30 bg-slate-900/70 text-cyan-200 hover:border-cyan-400/50',
        className
      )}
    >
      <span
        aria-hidden="true"
        className="absolute inset-y-0 left-0 bg-cyan-400/20"
        style={{ width: `${progress * 100}%` }}
      />
      <span className="relative">{progress > 0 ? holdingLabel : label}</span>
    </button>
  );
}