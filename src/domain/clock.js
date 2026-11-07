/**
 * clock.js — Game clock for Life Journey.
 * Manages day/month progression and fires timed events.
 */

/**
 * Create a new game clock.
 * @param {object} config - phase1.config.json
 * @returns {object} clock state
 */
export function createClock(config) {
  return {
    day: 1,
    month: 1,
    totalDays: 0,
    accumulatedMs: 0,
    dayDurationMs: (config.dayDurationSeconds ?? 12) * 1000,
    monthDays: config.monthDays ?? 30,
    totalMonths: config.months ?? 2,
    paused: false,
    finished: false,
  };
}

/**
 * Advance the clock by deltaMs milliseconds.
 * Returns { clock, events } where events is an array of event objects.
 * @param {object} clock
 * @param {number} deltaMs
 * @returns {{ clock: object, events: object[] }}
 */
export function tick(clock, deltaMs) {
  if (clock.paused || clock.finished) {
    return { clock, events: [] };
  }

  const events = [];
  let newClock = { ...clock, accumulatedMs: clock.accumulatedMs + deltaMs };

  while (newClock.accumulatedMs >= newClock.dayDurationMs) {
    newClock = {
      ...newClock,
      accumulatedMs: newClock.accumulatedMs - newClock.dayDurationMs,
    };
    const dayEvents = advanceDay(newClock);
    newClock = dayEvents.clock;
    events.push(...dayEvents.events);
  }

  return { clock: newClock, events };
}

/**
 * Advance clock by one day.
 * @param {object} clock
 * @returns {{ clock: object, events: object[] }}
 */
export function advanceDay(clock) {
  const events = [];
  let newClock = { ...clock };

  newClock.totalDays = (newClock.totalDays ?? 0) + 1;

  // Check if month ends
  if (newClock.day >= newClock.monthDays) {
    // End of month
    events.push({ type: 'month_change', month: newClock.month, day: newClock.day });

    if (newClock.month >= newClock.totalMonths) {
      // Game ends
      newClock.finished = true;
      events.push({ type: 'game_end', month: newClock.month });
    } else {
      newClock.month = newClock.month + 1;
      newClock.day = 1;
      // Allowance due at start of new month
      events.push({ type: 'allowance_due', month: newClock.month, day: 1 });
      events.push({ type: 'day_change', day: 1, month: newClock.month });
      events.push({ type: 'autosave' });
    }
  } else {
    newClock.day = newClock.day + 1;
    events.push({ type: 'day_change', day: newClock.day, month: newClock.month });

    // autosave every 5 days
    if (newClock.day % 5 === 0) {
      events.push({ type: 'autosave' });
    }
  }

  return { clock: newClock, events };
}

/**
 * Get a human-readable time of day string based on accumulated ms.
 * @param {object} clock
 * @returns {string} 'pagi' | 'siang' | 'sore' | 'malam'
 */
export function getTimeOfDay(clock) {
  const fraction = clock.accumulatedMs / clock.dayDurationMs;
  if (fraction < 0.25) return 'pagi';
  if (fraction < 0.5)  return 'siang';
  if (fraction < 0.75) return 'sore';
  return 'malam';
}

/**
 * Pause/unpause the clock.
 */
export function pauseClock(clock) {
  return { ...clock, paused: true };
}

export function resumeClock(clock) {
  return { ...clock, paused: false };
}
