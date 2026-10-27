import { useState } from 'react';
import { Loader2, RefreshCw } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import { loadGitHubCards } from '@/lib/ghCards';
import { cn } from '@/lib/utils';

export default function SyncFeedButton({ onSynced, className }) {
  const { toast } = useToast();
  const [busy, setBusy] = useState(false);

  const run = async () => {
    if (busy) return;
    setBusy(true);
    try {
      const { cards } = await loadGitHubCards({ force: true });
      onSynced?.(cards);
      toast(
        cards.length
          ? {
              title: 'Feed synced',
              description: `${cards.length} research card${cards.length === 1 ? '' : 's'} pulled from afrodojo/hive-alignment.`,
            }
          : {
              title: 'No research cards published',
              description: 'data/cards in afrodojo/hive-alignment is empty.',
            }
      );
    } catch (error) {
      toast({
        title: 'Feed sync failed',
        description: error?.message ?? 'Could not reach GitHub.',
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
      aria-label="Sync feed"
      className={cn(
        'flex h-7 items-center gap-1 rounded-full border border-slate-800 bg-slate-900/60 px-2 font-mono text-[9px] uppercase tracking-[0.12em] text-slate-500 transition hover:border-slate-700 hover:text-slate-200 active:scale-95 disabled:opacity-60',
        className
      )}
    >
      {busy ? <Loader2 className="h-3 w-3 animate-spin" /> : <RefreshCw className="h-3 w-3" />}
      {busy ? 'Syncing' : 'Sync'}
    </button>
  );
}