import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { base44 } from '@/api/base44Client';
import DeckHeader from '@/components/DeckHeader';
import InsightCard from '@/components/InsightCard';
import ActionBar from '@/components/ActionBar';
import SessionComplete from '@/components/SessionComplete';
import SignalBanner from '@/components/SignalBanner';
import ContextPrimingBanner from '@/components/ContextPrimingBanner';
import DeckSkeleton from '@/components/DeckSkeleton';
import SyncFeedButton from '@/components/SyncFeedButton';
import CategoryTabs from '@/components/CategoryTabs';
import FocusTimerRing from '@/components/FocusTimerRing';
import FocusModeToggle from '@/components/FocusModeToggle';
import DecompressionState from '@/components/DecompressionState';
import EmergencyRecenterButton from '@/components/EmergencyRecenterButton';
import EmergencyRecenter from '@/components/EmergencyRecenter';
import FocusMetricsModal from '@/components/FocusMetricsModal';
import { isGitHubCacheFresh, loadGitHubCards, mergeFeedCards, readCachedGitHubCards } from '@/lib/ghCards';
import { DAILY_GOAL, readInternalizedToday, recordInternalized } from '@/lib/telemetry';
import { useFocusTimer } from '@/lib/focusSession';
import {
  categoryCounts,
  categoryForDomain,
  categoryIncludes,
  cardsInCategory,
} from '@/lib/categories';
import { pinPrimedCard } from '@/lib/calendar';
import { ACTIVE_MEETING_POLL_MS, fetchActiveMeeting, primedMeeting } from '@/lib/activeMeeting';
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
  const [meeting, setMeeting] = useState(null);
  const [session, setSession] = useState([]);
  const [index, setIndex] = useState(0);
  const [savedIds, setSavedIds] = useState([]);
  const [masteredIds, setMasteredIds] = useState([]);
  const [phase, setPhase] = useState('loading');
  const [category, setCategory] = useState('ALL');
  const [todayEntries, setTodayEntries] = useState(() => readInternalizedToday());
  const [metricsOpen, setMetricsOpen] = useState(false);
  const [recenterCard, setRecenterCard] = useState(null);
  const primedRef = useRef(null);
  const categoryRef = useRef('ALL');
  const focus = useFocusTimer();

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const me = await base44.auth.me();
      const [interactionPage, signalList] = await Promise.all([
        base44.entities.UserCardInteraction.filter(
          { user_id: me.id },
          { sort: '-created_date', limit: 200 }
        ),
        base44.entities.FocusSignal.filter({ status: 'ACTIVE' }).catch(() => []),
      ]);
      if (cancelled) return;

      const allCards = mergeFeedCards(readCachedGitHubCards());
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

      if (isGitHubCacheFresh()) return;

      // Research cards are published in the public repo; the 30-minute cache keeps this off the hot path.
      try {
        const { cards: researchCards } = await loadGitHubCards();
        if (cancelled) return;

        const merged = mergeFeedCards(researchCards);
        setCards(merged);
        if (!built.length) {
          const refreshed = buildSession(cardsInCategory(merged, categoryRef.current), history, {
            preferences: me.domain_preferences,
            signalDomains: activeSignalDomains(live),
            size: SESSION_SIZE,
          });
          setSession(refreshed);
          setPhase(refreshed.length ? 'session' : 'empty');
        }
      } catch (error) {
        console.debug('Research feed refresh skipped:', error);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const card = session[index];
  const sessionSeconds = useMemo(() => sumReadTime(session), [session]);
  const signal = useMemo(() => primarySignal(signals), [signals]);
  const counts = useMemo(() => categoryCounts(cards), [cards]);

  // Tapping a category resets the deck to card 1 of that filtered subset.
  const selectCategory = (key) => {
    if (key === category) return;
    categoryRef.current = key;
    setCategory(key);

    const subset = cardsInCategory(cards, key);
    const built = buildSession(subset, interactions, {
      preferences: user?.domain_preferences,
      signalDomains: activeSignalDomains(signals),
      size: SESSION_SIZE,
    });
    const pinned =
      meeting?.domain && categoryIncludes(key, meeting.domain)
        ? pinPrimedCard(built, meeting.domain, subset)
        : built;

    setSession(pinned);
    setIndex(0);
    setPhase(built.length ? 'session' : 'empty');
  };

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

  const masterCard = async (target) => {
    if (!target || masteredIds.includes(target.id)) return;
    await logInteraction(target, 'MASTERED');
    setMasteredIds((prevList) => [...prevList, target.id]);
    // Digested for the day: the local record both the header and the export read.
    setTodayEntries(recordInternalized(target));
    const patch = {
      current_streak: nextStreak(user),
      last_active_at: new Date().toISOString(),
      domain_preferences: bumpPreferences(user.domain_preferences, target.domain, 'MASTERED'),
    };
    await base44.auth.updateMe(patch);
    setUser((u) => ({ ...u, ...patch }));
  };

  const onMaster = () => masterCard(card);

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

  // Anti-paralysis: one random Armor or Pillars invariant, nothing else on screen.
  const openRecenter = () => {
    const pool = cards.filter((c) =>
      ['WARRIOR_ETHOS', 'SPIRITUAL_PILLARS', 'OMEGA_HISTORY'].includes(c.domain)
    );
    if (!pool.length) return;
    setRecenterCard(pool[Math.floor(Math.random() * pool.length)]);
  };

  const restart = () => {
    const subset = cardsInCategory(cards, category);
    const built = buildSession(subset, interactions, {
      preferences: user?.domain_preferences,
      signalDomains: activeSignalDomains(signals),
      size: SESSION_SIZE,
    });
    const pinned =
      meeting?.domain && categoryIncludes(category, meeting.domain)
        ? pinPrimedCard(built, meeting.domain, subset)
        : built;
    setSession(pinned);
    setIndex(0);
    setPhase(built.length ? 'session' : 'empty');
  };

  const onFeedSynced = (researchCards) => {
    const merged = mergeFeedCards(researchCards);
    setCards(merged);
    if (phase !== 'empty') return;

    const subset = cardsInCategory(merged, category);
    const built = buildSession(subset, interactions, {
      preferences: user?.domain_preferences,
      signalDomains: activeSignalDomains(signals),
      size: SESSION_SIZE,
    });
    const pinned =
      meeting?.domain && categoryIncludes(category, meeting.domain)
        ? pinPrimedCard(built, meeting.domain, subset)
        : built;
    setSession(pinned);
    setIndex(0);
    setPhase(built.length ? 'session' : 'empty');
  };

  // The live meeting is published to GitHub; poll it once a minute, timestamped to skip caches.
  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const payload = await fetchActiveMeeting();
        if (!cancelled) setMeeting(primedMeeting(payload));
      } catch (error) {
        console.debug('Active meeting check skipped:', error);
      }
    };
    load();
    const timer = setInterval(load, ACTIVE_MEETING_POLL_MS);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, []);

  // Context priming: a meeting inside the window pins a card of its domain to the head of the deck.
  useEffect(() => {
    if (!meeting || primedRef.current === meeting.startTime) return;
    if (!categoryIncludes(category, meeting.domain)) return;

    primedRef.current = meeting.startTime;
    setSession((current) => pinPrimedCard(current, meeting.domain, cards));
    setIndex(0);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [meeting, category]);

  // The daily record rolls over at 04:00 local; refresh it while the deck stays open.
  useEffect(() => {
    const id = setInterval(() => setTodayEntries(readInternalizedToday()), 60 * 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="relative flex min-h-[100dvh] w-full flex-col bg-slate-950">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-64 bg-[radial-gradient(ellipse_at_top,rgba(16,185,129,0.10),transparent_65%)]" />
      <div className="relative mx-auto flex h-[100dvh] w-full max-w-md flex-col justify-between gap-3 p-4">
        <DeckHeader
          sessionSeconds={sessionSeconds}
          streak={user?.current_streak ?? 0}
          masteredToday={todayEntries.length}
          dailyGoal={DAILY_GOAL}
          onOpenMetrics={() => setMetricsOpen(true)}
          focusSlot={
            <FocusTimerRing
              remaining={focus.remaining}
              total={focus.total}
              phase={focus.phase}
              active={focus.active}
              onClick={focus.active ? focus.stop : focus.start}
            />
          }
          focusBar={
            <FocusModeToggle
              active={focus.active}
              presetId={focus.presetId}
              onToggle={focus.active ? focus.stop : focus.start}
              onSelectPreset={focus.selectPreset}
            />
          }
          syncSlot={<SyncFeedButton onSynced={onFeedSynced} />}
        />

        {focus.phase === 'break' ? (
          <DecompressionState remaining={focus.remaining} onOverride={focus.endBreak} />
        ) : (
          <>
        <CategoryTabs value={category} counts={counts} onChange={selectCategory} />

        {signal && <SignalBanner signal={signal} />}

        {meeting && (
          <ContextPrimingBanner
            summary={meeting.summary}
            domain={meeting.domain}
            onClick={() => selectCategory(categoryForDomain(meeting.domain))}
          />
        )}

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
              {category === 'ALL' ? 'Nothing left this cycle.' : 'Nothing in this lane yet.'}
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
          </>
        )}

        {phase === 'session' && card && focus.phase !== 'break' && (
          <EmergencyRecenterButton onClick={openRecenter} />
        )}

        <FocusMetricsModal
          open={metricsOpen}
          onOpenChange={setMetricsOpen}
          entries={todayEntries}
          streak={user?.current_streak ?? 0}
        />

        {recenterCard && (
          <EmergencyRecenter
            card={recenterCard}
            mastered={masteredIds.includes(recenterCard.id)}
            onMaster={() => masterCard(recenterCard)}
            onClose={() => setRecenterCard(null)}
          />
        )}
      </div>
    </div>
  );
}