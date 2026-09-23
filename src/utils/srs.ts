import type { SrsRating, SrsState } from '../data/types'

const DAY_MS = 24 * 60 * 60 * 1000

/**
 * Lightweight SM-2 inspired SRS scheduler.
 *
 * Ratings:
 *  again  (0) => lapses++, reset to learning, short interval
 *  hard   (3) => small interval bump, ease slightly down
 *  good   (4) => normal interval bump
 *  easy   (5) => bigger interval bump, ease slightly up
 */
export function scheduleNext(
  prev: SrsState[string] | undefined,
  rating: SrsRating,
  now: number = Date.now(),
): SrsState[string] {
  const base = prev ?? {
    status: 'new' as const,
    interval: 0,
    easeFactor: 2.5,
    dueAt: 0,
    reps: 0,
    lapses: 0,
  }

  let { interval, easeFactor, reps, lapses, status } = base

  reps += 1

  if (rating === 'again') {
    lapses += 1
    status = 'learning'
    interval = 0 // show again in ~10 minutes
    easeFactor = Math.max(1.3, easeFactor - 0.2)
  } else {
    if (status === 'new') status = 'learning'
    else if (status === 'learning' && reps >= 2) status = 'review'

    if (rating === 'hard') {
      easeFactor = Math.max(1.3, easeFactor - 0.15)
      interval = interval === 0 ? 1 : Math.max(1, Math.round(interval * 1.2))
    } else if (rating === 'good') {
      if (interval === 0) interval = 1
      else if (interval === 1) interval = 3
      else interval = Math.max(1, Math.round(interval * easeFactor))
    } else if (rating === 'easy') {
      easeFactor = easeFactor + 0.15
      if (interval === 0) interval = 2
      else if (interval === 1) interval = 4
      else interval = Math.max(2, Math.round(interval * easeFactor * 1.3))
    }
  }

  const dueAt = now + (interval === 0 ? 10 * 60 * 1000 : interval * DAY_MS)

  return {
    status,
    interval,
    easeFactor: Number(easeFactor.toFixed(2)),
    dueAt,
    reps,
    lapses,
    lastRating: rating,
  }
}

export function isDue(state: SrsState[string] | undefined, now = Date.now()) {
  if (!state) return true
  return state.dueAt <= now
}

/**
 * Automatically determine SRS rating based on answer performance.
 * - 0 wrong attempts + correct on 1st try → easy (7+ days)
 * - 1 wrong attempt + 'almost' feedback → good (3 days)
 * - 1 wrong attempt + 'not_quite' feedback → hard (1 day)
 * - 2+ wrong attempts → hard (1 day)
 * - Answer revealed → again (10 min)
 */
export function autoRateFromAttempts(
  attempts: number,
  feedbackLevel: 'almost' | 'not_quite',
  revealed: boolean,
): SrsRating {
  if (revealed) return 'again'
  if (attempts === 0) return 'easy'
  if (attempts === 1 && feedbackLevel === 'almost') return 'good'
  return 'hard'
}

export function sortByDue<T extends { id: string }>(
  cards: T[],
  srs: SrsState,
): T[] {
  const now = Date.now()
  return [...cards].sort((a, b) => {
    const sa = srs[a.id]
    const sb = srs[b.id]
    const na = sa?.dueAt ?? 0
    const nb = sb?.dueAt ?? 0
    // new (undefined status undefined) first
    if (na === 0 && nb === 0) return 0
    if (na === 0) return -1
    if (nb === 0) return 1
    // then earliest due first
    return na - nb
    void isDue(sa, now)
  })
}
