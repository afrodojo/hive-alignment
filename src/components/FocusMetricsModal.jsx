import { useEffect, useMemo, useState } from 'react';
import { CheckCircle2, CloudUpload, Copy, Flame, Loader2 } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import DomainBadge from '@/components/DomainBadge';
import { DAILY_GOAL, buildDigest, commitDigest, readGithubPat } from '@/lib/telemetry';

export default function FocusMetricsModal({ open, onOpenChange, entries = [], streak = 0 }) {
  const [status, setStatus] = useState('idle'); // idle | working | manual | synced | error
  const [message, setMessage] = useState('');
  const [copied, setCopied] = useState(false);
  const digest = useMemo(() => buildDigest(entries), [entries]);

  useEffect(() => {
    if (open) {
      setStatus('idle');
      setMessage('');
      setCopied(false);
    }
  }, [open]);

  const exportNow = async () => {
    if (!entries.length) return;
    const token = readGithubPat();
    if (!token) {
      setStatus('manual');
      return;
    }
    setStatus('working');
    try {
      await commitDigest(digest.payload, digest.path, token);
      setStatus('synced');
      setMessage(digest.path);
    } catch (error) {
      setStatus('error');
      setMessage(error.message);
    }
  };

  const copyDigest = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(digest.payload, null, 2));
      setCopied(true);
    } catch (error) {
      setMessage(error.message);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md gap-0 border-slate-800 bg-slate-950 p-0">
        <DialogHeader className="border-b border-slate-800/80 px-5 py-4 text-left">
          <p className="font-mono text-[9px] uppercase tracking-[0.24em] text-emerald-400/70">Focus metrics</p>
          <DialogTitle className="mt-1 text-[17px] font-semibold tracking-tight text-slate-100">
            Today&apos;s record
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4 px-5 py-4">
          <div className="grid grid-cols-2 gap-2">
            <div className="rounded-xl border border-emerald-500/20 bg-emerald-950/20 px-3 py-3">
              <p className="font-mono text-[9px] uppercase tracking-[0.16em] text-emerald-300/80">Internalized</p>
              <p className="mt-1 font-mono text-[22px] leading-none text-emerald-200">
                {entries.length}
                <span className="text-[12px] text-emerald-400/60"> / {DAILY_GOAL}</span>
              </p>
            </div>
            <div className="rounded-xl border border-amber-500/20 bg-amber-950/20 px-3 py-3">
              <p className="font-mono text-[9px] uppercase tracking-[0.16em] text-amber-300/80">Streak</p>
              <p className="mt-1 flex items-center gap-1.5 font-mono text-[22px] leading-none text-amber-200">
                <Flame className="h-4 w-4" /> {streak}
              </p>
            </div>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900/40">
            <p className="border-b border-slate-800/80 px-3 py-2 font-mono text-[9px] uppercase tracking-[0.18em] text-slate-500">
              Internalized today · resets 04:00
            </p>
            {entries.length ? (
              <ul className="no-scrollbar max-h-36 overflow-y-auto p-2">
                {entries.map((entry) => (
                  <li key={`${entry.card_id}-${entry.timestamp}`} className="flex items-center justify-between gap-2 rounded-lg px-1.5 py-1.5">
                    <span className="truncate text-[12px] leading-snug text-slate-300">{entry.title}</span>
                    <DomainBadge domain={entry.domain} compact className="shrink-0" />
                  </li>
                ))}
              </ul>
            ) : (
              <p className="px-3 py-4 text-[12px] leading-relaxed text-slate-600">
                Nothing internalized yet this cycle. Mark a card internalized to start today&apos;s record.
              </p>
            )}
          </div>

          <div className="space-y-2">
            <button
              type="button"
              onClick={exportNow}
              disabled={!entries.length || status === 'working'}
              className="flex w-full items-center justify-center gap-2 rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-2.5 font-mono text-[10px] uppercase tracking-[0.16em] text-emerald-200 transition hover:border-emerald-400/50 disabled:cursor-not-allowed disabled:opacity-40"
            >
              {status === 'working' ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <CloudUpload className="h-3.5 w-3.5" />}
              Export Today&apos;s Invariants
            </button>

            {status === 'synced' && (
              <p className="flex items-center gap-1.5 font-mono text-[9.5px] tracking-[0.06em] text-emerald-300/80">
                <CheckCircle2 className="h-3 w-3" /> Committed to {message}
              </p>
            )}
            {status === 'error' && (
              <p className="font-mono text-[9.5px] leading-relaxed text-red-400/80">{message}</p>
            )}

            {status === 'manual' && (
              <div className="space-y-2">
                <p className="font-mono text-[9px] uppercase tracking-[0.12em] text-slate-500">
                  No GitHub token found · copy the digest
                </p>
                <pre className="no-scrollbar max-h-40 overflow-auto rounded-xl border border-slate-800 bg-black/60 p-3 font-mono text-[9.5px] leading-relaxed text-slate-400">
{JSON.stringify(digest.payload, null, 2)}
                </pre>
                <button
                  type="button"
                  onClick={copyDigest}
                  className="flex w-full items-center justify-center gap-2 rounded-xl border border-slate-700 bg-slate-900/60 px-4 py-2.5 font-mono text-[10px] uppercase tracking-[0.16em] text-slate-300 transition hover:border-slate-600"
                >
                  {copied ? <CheckCircle2 className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
                  {copied ? 'Copied to clipboard' : 'Copy JSON'}
                </button>
                <p className="font-mono text-[9px] tracking-[0.04em] text-slate-600">
                  Target: {digest.path}
                </p>
              </div>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}