import { useState } from 'react';
import { Github, Loader2 } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import { syncLatestGitHubCommits } from '@/lib/github';
import { cn } from '@/lib/utils';

export default function SyncGitHubButton({ onSynced, className }) {
  const { toast } = useToast();
  const [busy, setBusy] = useState(false);

  const run = async () => {
    if (busy) return;
    setBusy(true);
    try {
      const created = await syncLatestGitHubCommits(3);
      onSynced?.(created);
      toast(
        created.length
          ? {
              title: `${created.length} new card${created.length > 1 ? 's' : ''} ingested`,
              description: 'Synthesized from afrodojo/hive-alignment.',
            }
          : {
              title: 'Already in sync',
              description: 'No unprocessed commits in afrodojo/hive-alignment.',
            }
      );
    } catch (error) {
      toast({
        title: 'GitHub sync failed',
        description: error?.message ?? 'Could not reach the repository.',
        variant: 'destructive',
      });
    } finally {
      setBusy(false);
    }
  };

  return (
    <button
      type="button"
      onClick={run}
      disabled={busy}
      aria-label="Sync GitHub"
      className={cn(
        'flex h-7 items-center gap-1 rounded-full border border-slate-800 bg-slate-900/60 px-2 font-mono text-[9px] uppercase tracking-[0.12em] text-slate-500 transition hover:border-slate-700 hover:text-slate-200 active:scale-95 disabled:opacity-60',
        className
      )}
    >
      {busy ? <Loader2 className="h-3 w-3 animate-spin" /> : <Github className="h-3 w-3" />}
      {busy ? 'Syncing' : 'Sync'}
    </button>
  );
}