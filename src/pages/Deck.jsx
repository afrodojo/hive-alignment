import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { base44 } from '@/api/base44Client';
import DeckHeader from '@/components/DeckHeader';
import InsightCard from '@/components/InsightCard';
import ActionBar from '@/components/ActionBar';
import SessionComplete from '@/components/SessionComplete';
import SignalBanner from '@/components/SignalBanner';
import DeckSkeleton from '@/components/DeckSkeleton';
import SyncGitHubButton from '@/components/SyncGitHubButton';
import {
  activeSignalDomains,
  buildSession,
  bumpPreferences,
  nextStreak,
  primarySignal,
  sumReadTime,
} from '@/lib/feed';

const SESSION_SIZE = 5;

export default function Deck() {
  const [user, setUser] = useState(null);
  const [cards, setCards] = useState([]);
  const [interactions, setInteractions] = useState([]);
  const [signals, setSignals] = useState([]);
  const [session, setSession] = useState([]);
  const [index, setIndex] = useState(0);
  const [savedIds, setSavedIds] = useState([]);
  const [masteredIds, setMasteredIds] = useState([]);
  const [phase, setPhase] = useState('loading');

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const me = await base44.auth.me();
      const [cardPage, interactionPage, signalList] = await Promise.all([
        base44.entities.Card.list({ sort: 'created_date', limit: 200 }),
        base44.entities.UserCardInteraction.filter(
          { user_id: me.id },
          { sort: '-created_date', limit: 200 }
        ),
        base44.entities.FocusSignal.filter({ status: 'ACTIVE' }).catch(() => []),
      ]);
      if (cancelled) return;

      const allCards = cardPage?.items ?? cardPage ?? [];
      const history = interactionPage?.items ?? interactionPage ?? [];
      const live = signalList ?? [];
      const built = buildSession(allCards, history, {
        preferences: me.domain_preferences,
        signalDomains: activeSignalDomains(live),
        size: SESSION_SIZE,
      });

      setUser(me);
      setCards(allCards);
      setInteractions(history);
      setSignals(live);
      setSession(built);
      setSavedIds(history.filter((i) => i.action === 'SAVED').map((i) => i.card_id));
      setMasteredIds(history.filter((i) => i.action === 'MASTERED').map((i) => i.card_id));
      setPhase(built.length ? 'session' : 'empty');
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const card = session[index];
  const sessionSeconds = useMemo(() => sumReadTime(session), [session]);
  const signal = useMemo(() => primarySignal(signals), [signals]);

  const next = useCallback(() => {
    if (index >= session.length - 1) setPhase('summary');
    else setIndex((i) => i + 1);
  }, [index, session.length]);

  const prev = () => setIndex((i) => Math.max(0, i - 1));

  useEffect(() => {
    if (phase !== 'session') return;
    const onKey = (e) => {
      if (e.target instanceof HTMLElement && ['INPUT', 'TEXTAREA'].includes(e.target.tagName)) return;
      if (e.key === 'ArrowRight') next();
      if (e.key === 'ArrowLeft') prev();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [phase, next]);

  const logInteraction = async (target, action) => {
    const record = await base44.entities.UserCardInteraction.create({
      user_id: user.id,
      card_id: target.id,
      domain: target.domain,
      action,
    });
    setInteractions((prevList) => [record, ...prevList]);
    return record;
  };

  const persistWeights = async (target, action) => {
    const preferences = bumpPreferences(user.domain_preferences, target.domain, action);
    await base44.auth.updateMe({ domain_preferences: preferences });
    setUser((u) => ({ ...u, domain_preferences: preferences }));
  };

  const onSave = async () => {
    if (!card) return;
    const existing = interactions.find((i) => i.card_id === card.id && i.action === 'SAVED');
    if (existing) {
      await base44.entities.UserCardInteraction.delete(existing.id);
      setInteractions((prevList) => prevList.filter((i) => i.id !== existing.id));
      setSavedIds((prevList) => prevList.filter((id) => id !== card.id));
      return;
    }
    await logInteraction(card, 'SAVED');
    setSavedIds((prevList) => [...prevList, card.id]);
    await persistWeights(card, 'SAVED');
  };

  const onMaster = async () => {
    if (!card || masteredIds.includes(card.id)) return;
    await logInteraction(card, 'MASTERED');
    setMasteredIds((prevList) => [...prevList, card.id]);
    const patch = {
      current_streak: nextStreak(user),
      last_active_at: new Date().toISOString(),
      domain_preferences: bumpPreferences(user.domain_preferences, card.domain, 'MASTERED'),
    };
    await base44.auth.updateMe(patch);
    setUser((u) => ({ ...u, ...patch }));
  };

  const onDismiss = async () => {
    if (!card) return;
    await logInteraction(card, 'DISMISSED');
    const remaining = session.filter((c) => c.id !== card.id);
    if (!remaining.length) {
      setPhase('summary');
      return;
    }
    setSession(remaining);
    setIndex((i) => Math.min(i, remaining.length - 1));
  };

  const onShare = async () => {
    if (!card) return;
    const text = `${card.title} — ${card.hook}`;
    if (navigator.share) await navigator.share({ title: card.title, text });
    else await navigator.clipboard.writeText(text);
  };

  const restart = () => {
    const built = buildSession(cards, interactions, {
      preferences: user?.domain_preferences,
      signalDomains: activeSignalDomains(signals),
      size: SESSION_SIZE,
    });
    setSession(built);
    setIndex(0);
    setPhase(built.length ? 'session' : 'empty');
  };

  const onSynced = (created) => {
    if (!created?.length) return;
    const merged = [...created, ...cards];
    setCards(merged);
    if (phase === 'empty') {
      const built = buildSession(merged, interactions, {
        preferences: user?.domain_preferences,
        signalDomains: activeSignalDomains(signals),
        size: SESSION_SIZE,
      });
      setSession(built);
      setIndex(0);
      setPhase(built.length ? 'session' : 'empty');
    }
  };

  return (
    <div className="relative flex min-h-[100dvh] w-full flex-col bg-slate-950">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-64 bg-[radial-gradient(ellipse_at_top,rgba(16,185,129,0.10),transparent_65%)]" />
      <div className="relative mx-auto flex h-[100dvh] w-full max-w-md flex-col justify-between gap-3 p-4">
        <DeckHeader
          sessionSeconds={sessionSeconds}
          streak={user?.current_streak ?? 0}
          syncSlot={user?.role === 'admin' ? <SyncGitHubButton onSynced={onSynced} /> : null}
        />

        {signal && <SignalBanner signal={signal} />}

        {phase === 'loading' && <DeckSkeleton />}

        {phase === 'session' && card && (
          <>
            <InsightCard
              key={card.id}
              card={card}
              position={index + 1}
              total={session.length}
              className="animate-card-in flex-1"
            />
            <ActionBar
              saved={savedIds.includes(card.id)}
              mastered={masteredIds.includes(card.id)}
              canPrev={index > 0}
              isLast={index === session.length - 1}
              index={index}
              total={session.length}
              onSave={onSave}
              onMaster={onMaster}
              onShare={onShare}
              onPrev={prev}
              onNext={next}
              onDismiss={onDismiss}
            />
          </>
        )}

        {(phase === 'summary' || phase === 'closed') && (
          <SessionComplete
            mode={phase}
            masteredCount={masteredIds.length}
            savedCount={savedIds.length}
            sessionSeconds={sessionSeconds}
            streak={user?.current_streak ?? 0}
            onClose={() => setPhase('closed')}
            onRestart={restart}
          />
        )}

        {phase === 'empty' && (
          <div className="flex flex-1 flex-col items-center justify-center px-4 text-center">
            <p className="font-mono text-[9px] uppercase tracking-[0.26em] text-emerald-400/70">Library clear</p>
            <h2 className="mt-3 text-2xl font-semibold tracking-tight text-white">
              Nothing left this cycle.
            </h2>
            <p className="mt-2 max-w-[17rem] text-[13px] leading-relaxed text-slate-500">
              Every insight in the current rotation has been internalized. Review what you have kept, then come back.
            </p>
            <Link
              to="/archive"
              className="mt-7 rounded-xl border border-slate-700 bg-slate-100 px-5 py-2.5 font-mono text-[10px] uppercase tracking-[0.2em] text-slate-950"
            >
              Open archive
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}