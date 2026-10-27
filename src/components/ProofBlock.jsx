import { useEffect, useState } from 'react';
import katex from 'katex';
import 'katex/dist/katex.min.css';
import { Check, Copy } from 'lucide-react';
import { renderProof } from '@/lib/latex';
import { cn } from '@/lib/utils';

export default function ProofBlock({ value, className }) {
  const [copied, setCopied] = useState(false);
  const { mode, html } = renderProof(value);

  useEffect(() => {
    if (!copied) return;
    const timer = setTimeout(() => setCopied(false), 1600);
    return () => clearTimeout(timer);
  }, [copied]);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(String(value || ''));
      setCopied(true);
    } catch {
      setCopied(false);
    }
  };

  return (
    <div className={cn('mt-6 overflow-hidden rounded-xl border border-slate-800 bg-black/60', className)}>
      <div className="flex items-center justify-between border-b border-slate-800/80 px-3 py-1.5">
        <span className="font-mono text-[9px] uppercase tracking-[0.2em] text-slate-600">
          Proof / Invariant
        </span>
        <div className="flex items-center gap-2">
          <span className="font-mono text-[9px] text-slate-700">{mode === 'latex' ? 'latex' : 'mono'}</span>
          <button
            type="button"
            onClick={copy}
            aria-label={copied ? 'Snippet copied' : 'Copy snippet'}
            className={cn(
              'flex h-5 w-5 items-center justify-center rounded border border-slate-800 transition',
              copied
                ? 'border-emerald-500/40 text-emerald-400'
                : 'text-slate-600 hover:border-slate-700 hover:text-slate-300'
            )}
          >
            {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
          </button>
        </div>
      </div>

      {mode === 'latex' ? (
        <div
          className="proof-math no-scrollbar overflow-x-auto px-3 py-4 text-[13.5px] text-slate-200"
          dangerouslySetInnerHTML={{ __html: html }}
        />
      ) : (
        <pre className="no-scrollbar overflow-x-auto px-3 py-3 font-mono text-[11px] leading-[1.7] text-slate-400">
          {value}
        </pre>
      )}
    </div>
  );
}