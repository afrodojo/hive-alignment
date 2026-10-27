import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { ChevronLeft, Flame } from 'lucide-react';
import { base44 } from '@/api/base44Client';
import AlignmentPanel from '@/components/archive/AlignmentPanel';
import ArchiveRow from '@/components/archive/ArchiveRow';
import InsightCard from '@/components/InsightCard';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { DOMAIN_ORDER, domainMeta } from '@/lib/domains';
import { latestActions } from '@/lib/feed';
import { loadGitHubCards, mergeFeedCards, readCachedGitHubCards } from '@/lib/ghCards';
import { cn } from '@/lib/utils';

const TABS = [
  { key: 'SAVED', label: 'Saved' },
  { key: 'MASTERED', label: 'Internalized' },
];

export default function Archive() {
  const [user, setUser] = useState(null);
  const [cards, setCards] = useState([]);
  const [interactions, setInteractions] = useState([]);
  const [tab, setTab] = useState('SAVED');
  const [domainFilter, setDomainFilter] = useState('ALL');
  const [active, setActive] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const me = await base44.auth.me();
      const [interactionPage, researchCards] = await Promise.all([
        base44.entities.UserCardInteraction.filter(
          { user_id: me.id },
          { sort: '-created_date', limit: 200 }
        ),
        loadGitHubCards()
          .then(({ cards: fetched }) => fetched)
          .catch(() => readCachedGitHubCards()),
      ]);
      if (cancelled) return;
      setUser(me);
      setCards(mergeFeedCards(researchCards));
      setInteractions(interactionPage?.items ?? interactionPage ?? []);
      setLoading(false);
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const byId = useMemo(() => new Map(cards.map((c) => [c.id, c])), [cards]);
  const history = useMemo(() => [...latestActions(interactions).entries()], [interactions]);

  const counts = useMemo(() => {
    const acc = {};
    history.forEach(([cardId, action]) => {
      if (action === 'DISMISSED') return;
      const domain = byId.get(cardId)?.domain;
      if (domain) acc[domain] = (acc[domain] || 0) + 1;
    });
    return acc;
  }, [history, byId]);

  const totalSignals = Object.values(counts).reduce((a, b) => a + b, 0);

  const rows = useMemo(
    () =>
      history
        .filter(([, action]) => action === tab)
        .map(([cardId, action]) => ({ card: byId.get(cardId), action }))
        .filter((row) => row.card)
        .filter((row) => domainFilter === 'ALL' || row.card.domain === domainFilter),
    [history, byId, tab, domainFilter]
  );

  const savedCount = history.filter(([, a]) => a === 'SAVED').length;
  const masteredCount = history.filter(([, a]) => a === 'MASTERED').length;

  return (
    <div className="relative min-h-[100dvh] bg-slate-950">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-56 bg-[radial-gradient(ellipse_at_top,rgba(16,185,129,0.08),transparent_65%)]" />
      <div className="relative mx-auto w-full max-w-md px-4 pb-10 pt-4">
        <div className="flex items-center justify-between">
          <Link
            to="/"
            className="flex items-center gap-1 font-mono text-[10px] uppercase tracking-[0.16em] text-slate-500 transition hover:text-slate-200"
          >
            <ChevronLeft className="h-3.5 w-3.5" /> Feed
          </Link>
          <span className="flex items-center gap-1 rounded-full border border-amber-500/25 bg-amber-950/30 px-2 py-1 font-mono text-[10px] text-amber-400">
            <Flame className="h-3 w-3" /> {user?.current_streak ?? 0}
          </span>
        </div>

        <h1 className="mt-6 text-[30px] font-semibold leading-tight tracking-tight text-white">Your hive</h1>
        <p className="mt-1.5 text-[13px] leading-relaxed text-slate-500">
          {masteredCount} internalized · {savedCount} saved
        </p>

        <div className="mt-6">
          <AlignmentPanel counts={counts} total={totalSignals} />
        </div>

        <div className="mt-6 flex items-center gap-1 rounded-xl border border-slate-800 bg-slate-900/40 p-1">
          {TABS.map(({ key, label }) => (
            <button
              key={key}
              type="button"
              onClick={() => setTab(key)}
              className={cn(
                'flex-1 rounded-lg py-2 font-mono text-[9.5px] uppercase tracking-[0.16em] transition',
                tab === key ? 'bg-slate-800 text-slate-100' : 'text-slate-500 hover:text-slate-300'
              )}
            >
              {label}
            </button>
          ))}
        </div>

        <div className="mt-3 flex flex-wrap gap-1.5">
          <button
            type="button"
            onClick={() => setDomainFilter('ALL')}
            className={cn(
              'rounded-full border px-2.5 py-1 font-mono text-[9px] uppercase tracking-[0.14em] transition',
              domainFilter === 'ALL'
                ? 'border-slate-600 bg-slate-800 text-slate-100'
                : 'border-slate-800 text-slate-500 hover:text-slate-300'
            )}
          >
            All
          </button>
          {DOMAIN_ORDER.map((key) => {
            const meta = domainMeta(key);
            return (
              <button
                key={key}
                type="button"
                onClick={() => setDomainFilter(key)}
                className={cn(
                  'flex items-center gap-1.5 rounded-full border px-2.5 py-1 font-mono text-[9px] uppercase tracking-[0.14em] transition',
                  domainFilter === key ? meta.badge : 'border-slate-800 text-slate-500 hover:text-slate-300'
                )}
              >
                <span className={cn('h-1 w-1 rounded-full', meta.dot)} />
                {meta.shortLabel}
              </button>
            );
          })}
        </div>

        <div className="mt-4 space-y-2">
          {loading &&
            Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-[92px] animate-pulse rounded-xl border border-slate-800 bg-slate-900/40" />
            ))}

          {!loading && rows.length === 0 && (
            <div className="rounded-xl border border-dashed border-slate-800 px-4 py-10 text-center">
              <p className="font-mono text-[9px] uppercase tracking-[0.22em] text-slate-600">
                {tab === 'SAVED' ? 'Nothing saved yet' : 'Nothing internalized yet'}
              </p>
              <p className="mt-2 text-[12.5px] leading-relaxed text-slate-500">
                {tab === 'SAVED'
                  ? 'Tap the bookmark on any card to keep it here.'
                  : 'Internalize a card to bank it and extend your streak.'}
              </p>
            </div>
          )}

          {!loading &&
            rows.map(({ card, action }) => (
              <ArchiveRow key={card.id} card={card} action={action} onClick={() => setActive(card)} />
            ))}
        </div>
      </div>

      <Dialog open={!!active} onOpenChange={(open) => !open && setActive(null)}>
        <DialogContent className="max-w-md gap-0 border-slate-800 bg-slate-950 p-0">
          <DialogHeader className="sr-only">
            <DialogTitle>{active?.title}</DialogTitle>
          </DialogHeader>
          {active && <InsightCard card={active} className="max-h-[82vh] rounded-xl" />}
        </DialogContent>
      </Dialog>
    </div>
  );
}