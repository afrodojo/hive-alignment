import { PRIMING_GRACE_MS, PRIMING_WINDOW_MS, classifyMeetingDomain } from '@/lib/calendar';

export const ACTIVE_MEETING_URL =
  'https://raw.githubusercontent.com/afrodojo/hive-alignment/main/data/active_meeting.json';

/** The meeting file is re-read once a minute. */
export const ACTIVE_MEETING_POLL_MS = 60 * 1000;

/** Fetch the live meeting file, busting the browser cache with a timestamp. */
export async function fetchActiveMeeting() {
  const res = await fetch(`${ACTIVE_MEETING_URL}?t=${Date.now()}`, { cache: 'no-store' });
  if (!res.ok) return null;
  return res.json();
}

/**
 * The meeting that should prime the feed right now: active, starting within the
 * next 20 minutes or started no more than 5 minutes ago. Otherwise null.
 */
export function primedMeeting(meeting, now = new Date()) {
  if (!meeting || meeting.active !== true || !meeting.startTime) return null;

  const startsAt = new Date(meeting.startTime);
  if (Number.isNaN(startsAt.getTime())) return null;

  const delta = startsAt.getTime() - now.getTime();
  if (delta > PRIMING_WINDOW_MS || delta < -PRIMING_GRACE_MS) return null;

  return {
    ...meeting,
    domain:
      meeting.domain ||
      classifyMeetingDomain({ title: meeting.summary, description: meeting.description }),
  };
}