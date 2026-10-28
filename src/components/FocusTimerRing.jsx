import { cn } from '@/lib/utils';
import { formatClock } from '@/lib/focusSession';

const RADIUS = 13;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

export default function FocusTimerRing({ remaining = 0, total = 0, phase = 'idle', active, onClick }) {
  const progress = total > 0 ? Math.min(1, Math.max(0, remaining / total)) : 0;
  const isBreak = phase === 'break';

  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={active ? 'Stop focus mode' : 'Start focus mode'}
      title={active ? 'Focus timer running — tap to stop' : 'Start focus mode'}
      className={cn(
        'relative flex h-8 w-8 items-center justify-center rounded-full transition active:scale-95',
        active ? 'text-slate-200' : 'text-slate-500 hover:text-slate-300'
      )}
    >
      <svg viewBox="0 0 32 32" className="h-8 w-8 -rotate-90">
        <circle
          cx="16"
          cy="16"
          r={RADIUS}
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          className="text-slate-800"
        />
        {active && (
          <circle
            cx="16"
            cy="16"
            r={RADIUS}
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeDasharray={CIRCUMFERENCE}
            strokeDashoffset={CIRCUMFERENCE * (1 - progress)}
            className={cn(
              'transition-[stroke-dashoffset] duration-500',
              isBreak ? 'text-cyan-400' : 'text-emerald-400'
            )}
          />
        )}
      </svg>
      <span
        className={cn(
          'absolute font-mono text-[7.5px] tabular-nums tracking-tight',
          active ? (isBreak ? 'text-cyan-300' : 'text-emerald-300') : 'text-slate-600'
        )}
      >
        {active ? formatClock(remaining) : '--:--'}
      </span>
    </button>
  );
}