/**
 * clock.js — Game clock & 24-Hour Time System for Life Journey.
 * Complies with Rule 72 (Time System & Activities).
 * 
 * 1 game minute = 1 real second (60 game min = 1 real min, 1440 game min = 24 real min).
 * 1 month = 28 days (4 weeks @ 7 days: Senin - Minggu).
 * New game starts: Day 1 (Senin), 06:00 (minute 360).
 */

export const DAYS_OF_WEEK = [
  'Senin',
  'Selasa',
  'Rabu',
  'Kamis',
  'Jumat',
  'Sabtu',
  'Minggu'
];

export const DAYS_PER_MONTH = 28;

export const DEFAULT_OPENING_HOURS = {
  school: { openMinute: 7 * 60, closeMinute: 15 * 60, days: [1, 2, 3, 4, 5] }, // Sen - Jum (1-5)
  minimarket: { openMinute: 7 * 60, closeMinute: 22 * 60, days: [1, 2, 3, 4, 5, 6, 7] },
  toko_kosmetik: { openMinute: 9 * 60, closeMinute: 20 * 60, days: [1, 2, 3, 4, 5, 6, 7] },
  game_center: { openMinute: 10 * 60, closeMinute: 22 * 60, days: [1, 2, 3, 4, 5, 6, 7] },
  spbu: { openMinute: 6 * 60, closeMinute: 23 * 60, days: [1, 2, 3, 4, 5, 6, 7] },
  home: { openMinute: 0, closeMinute: 24 * 60, days: [1, 2, 3, 4, 5, 6, 7] }
};

/**
 * Determine sky phase and display metadata for a given minute of the day (0..1439).
 * Rule 72:
 *  - Pagi  : 06:00 - 11:59 (360..719)
 *  - Siang : 12:00 - 16:59 (720..1019)
 *  - Sore  : 17:00 - 18:59 (1020..1139)
 *  - Malam : 19:00 - 05:59 (1140..1439, 0..359)
 */
export function getTimeOfDayPhase(minuteOfDay) {
  const m = ((minuteOfDay % 1440) + 1440) % 1440;
  if (m >= 360 && m < 720) {
    return { phase: 'pagi', skyClass: 'sky-pagi', label: 'PAGI', emoji: '🌅' };
  } else if (m >= 720 && m < 1020) {
    return { phase: 'siang', skyClass: 'sky-siang', label: 'SIANG', emoji: '☀️' };
  } else if (m >= 1020 && m < 1140) {
    return { phase: 'sore', skyClass: 'sky-sore', label: 'SORE', emoji: '🌇' };
  } else {
    return { phase: 'malam', skyClass: 'sky-malam', label: 'MALAM', emoji: '🌙' };
  }
}

/**
 * Create a new game clock state.
 * @param {object} [config]
 * @returns {object}
 */
export function createClock(config = {}) {
  const initialMinute = 6 * 60; // 06:00
  return {
    gameMinutes: initialMinute,
    day: 1,
    month: 1,
    year: 1,
    timeOfDay: initialMinute,
    totalDays: 0,
    accumulatedMs: 0,
    dayDurationMs: 24 * 60 * 1000, // 24 minutes real time = 1 day
    monthDays: config.monthDays ?? DAYS_PER_MONTH,
    totalMonths: config.months ?? 2,
    paused: false,
    finished: false,
  };
}

/**
 * Check if a building/location is open at the given clock state.
 * @param {string} locationId
 * @param {object} clock
 * @param {object} [openingHours]
 * @returns {{ open: boolean, reason?: string, openMinute: number, closeMinute: number }}
 */
export function isLocationOpen(locationId, clock, openingHours = DEFAULT_OPENING_HOURS) {
  const rule = openingHours[locationId];
  if (!rule) {
    return { open: true, openMinute: 0, closeMinute: 1440 };
  }

  const dayNumber = clock.day ?? (1 + Math.floor((clock.gameMinutes ?? 0) / 1440));
  const dayOfWeek = ((dayNumber - 1) % 7) + 1; // 1 = Senin ... 7 = Minggu
  const minuteOfDay = (clock.gameMinutes ?? (clock.timeOfDay ?? 360)) % 1440;

  if (rule.days && !rule.days.includes(dayOfWeek)) {
    const dayName = DAYS_OF_WEEK[dayOfWeek - 1] || 'Hari ini';
    return {
      open: false,
      reason: `Tutup pada hari ${dayName}.`,
      openMinute: rule.openMinute,
      closeMinute: rule.closeMinute
    };
  }

  if (minuteOfDay < rule.openMinute || minuteOfDay >= rule.closeMinute) {
    const openH = String(Math.floor(rule.openMinute / 60)).padStart(2, '0');
    const openM = String(rule.openMinute % 60).padStart(2, '0');
    const closeH = String(Math.floor(rule.closeMinute / 60)).padStart(2, '0');
    const closeM = String(rule.closeMinute % 60).padStart(2, '0');
    return {
      open: false,
      reason: `Tutup. Jam operasional: ${openH}:${openM} - ${closeH}:${closeM}.`,
      openMinute: rule.openMinute,
      closeMinute: rule.closeMinute
    };
  }

  return { open: true, openMinute: rule.openMinute, closeMinute: rule.closeMinute };
}

/**
 * Calculate minutes to advance until 06:00 next morning (for sleep).
 * @param {object} clock
 * @param {number} [targetWakeMinute=360] 06:00
 * @returns {number} minutes to advance
 */
export function getTimeUntilWakeup(clock, targetWakeMinute = 360) {
  const currentMin = (clock.gameMinutes ?? (clock.timeOfDay ?? 360)) % 1440;
  if (currentMin < targetWakeMinute) {
    return targetWakeMinute - currentMin;
  }
  return (1440 - currentMin) + targetWakeMinute;
}

/**
 * Format clock for display & UI bindings.
 * @param {object} clock
 * @returns {object}
 */
export function formatClock(clock) {
  const totalMin = clock.gameMinutes ?? (clock.timeOfDay ?? 360);
  const minuteOfDay = totalMin % 1440;
  const hours = Math.floor(minuteOfDay / 60);
  const mins = minuteOfDay % 60;
  const hh = String(hours).padStart(2, '0');
  const mm = String(mins).padStart(2, '0');

  const day = clock.day ?? (1 + Math.floor(totalMin / 1440));
  const month = clock.month ?? 1;
  const dayIndex = (day - 1) % 7;
  const dayName = DAYS_OF_WEEK[dayIndex] || 'Senin';
  const phaseInfo = getTimeOfDayPhase(minuteOfDay);

  return {
    day,
    month,
    dayIndex,
    dayOfWeek: dayIndex + 1,
    dayName,
    timeString: `${hh}:${mm}`,
    dateString: `Hari ${day} · Bln ${month}`,
    minuteOfDay,
    phase: phaseInfo.phase,
    skyClass: phaseInfo.skyClass,
    phaseLabel: phaseInfo.label,
    emoji: phaseInfo.emoji
  };
}

/**
 * Internal single sub-step advancement (up to 5 minutes).
 */
function advanceTimeSubstep(clock, stepMinutes, openingHours) {
  const events = [];
  const prevMin = clock.gameMinutes ?? (clock.timeOfDay ?? 360);
  const nextMin = prevMin + stepMinutes;

  const prevMod = prevMin % 1440;
  const nextMod = nextMin % 1440;

  const prevHour = Math.floor(prevMod / 60);
  const nextHour = Math.floor(nextMod / 60);

  const prevPhase = getTimeOfDayPhase(prevMod).phase;
  const nextPhase = getTimeOfDayPhase(nextMod).phase;

  // 1. Check openStateChanged
  for (const [locId, rule] of Object.entries(openingHours)) {
    const wasOpen = isLocationOpen(locId, { ...clock, gameMinutes: prevMin }, openingHours).open;
    const nowOpen = isLocationOpen(locId, { ...clock, gameMinutes: nextMin }, openingHours).open;
    if (wasOpen !== nowOpen) {
      events.push({
        type: 'openStateChanged',
        locationId: locId,
        open: nowOpen,
        minute: nextMin
      });
    }
  }

  // 2. Check hourChanged
  if (prevHour !== nextHour || Math.floor(prevMin / 60) !== Math.floor(nextMin / 60)) {
    events.push({
      type: 'hourChanged',
      hour: nextHour,
      minuteOfDay: nextMod,
      gameMinutes: nextMin
    });
  }

  // 3. Check phaseChanged
  if (prevPhase !== nextPhase) {
    events.push({
      type: 'phaseChanged',
      from: prevPhase,
      to: nextPhase,
      info: getTimeOfDayPhase(nextMod)
    });
  }

  // 4. Check dayChanged
  let day = clock.day ?? 1;
  let month = clock.month ?? 1;
  let totalDays = clock.totalDays ?? 0;
  let finished = clock.finished ?? false;

  const prevDayIndex = Math.floor(prevMin / 1440);
  const nextDayIndex = Math.floor(nextMin / 1440);

  if (nextDayIndex > prevDayIndex) {
    const daysGained = nextDayIndex - prevDayIndex;
    for (let d = 0; d < daysGained; d++) {
      totalDays += 1;
      day += 1;

      // Day changed hook
      events.push({
        type: 'dayChanged',
        day,
        month,
        dayOfWeek: ((day - 1) % 7) + 1,
        totalDays
      });

      // Weekly allowance check (every Senin / Monday, dayOfWeek === 1)
      if (((day - 1) % 7) + 1 === 1) {
        events.push({
          type: 'allowance_due',
          day,
          month,
          reason: 'weekly_allowance'
        });
      }

      // Check month boundary (28 days per month)
      if (day > DAYS_PER_MONTH) {
        events.push({
          type: 'monthChanged',
          oldMonth: month,
          newMonth: month + 1,
          day: 1
        });
        month += 1;
        day = 1;

        if (month > (clock.totalMonths ?? 2)) {
          finished = true;
          events.push({ type: 'game_end', month });
        }
      }
    }
  }

  const updatedClock = {
    ...clock,
    gameMinutes: nextMin,
    timeOfDay: nextMod,
    day,
    month,
    totalDays,
    finished
  };

  return { clock: updatedClock, events };
}

/**
 * Primary domain entrypoint: advanceTime(clock, minutes, reason, openingHours).
 * Processes time in chunks <= 5 minutes to ensure no triggers or hooks are missed.
 * 
 * @param {object} clock
 * @param {number} minutes
 * @param {string} [reason='tick']
 * @param {object} [openingHours=DEFAULT_OPENING_HOURS]
 * @returns {{ clock: object, events: object[] }}
 */
export function advanceTime(clock, minutes, reason = 'tick', openingHours = DEFAULT_OPENING_HOURS) {
  if (clock.paused || clock.finished || minutes <= 0) {
    return { clock, events: [] };
  }

  let currentClock = { ...clock };
  const allEvents = [];
  let remaining = Math.round(minutes);

  while (remaining > 0) {
    const step = Math.min(remaining, 5);
    const { clock: nextClock, events: stepEvents } = advanceTimeSubstep(currentClock, step, openingHours);
    currentClock = nextClock;
    allEvents.push(...stepEvents);
    remaining -= step;
  }

  return { clock: currentClock, events: allEvents };
}

/**
 * Advance clock by deltaMs milliseconds (tick from game loop).
 * 1000ms = 1 game minute.
 */
export function tick(clock, deltaMs, openingHours = DEFAULT_OPENING_HOURS) {
  if (clock.paused || clock.finished) {
    return { clock, events: [] };
  }

  const accumulatedMs = (clock.accumulatedMs ?? 0) + deltaMs;
  const minutesToAdvance = Math.floor(accumulatedMs / 1000);
  const remainingMs = accumulatedMs % 1000;

  if (minutesToAdvance > 0) {
    const { clock: advancedClock, events } = advanceTime(
      { ...clock, accumulatedMs: remainingMs },
      minutesToAdvance,
      'tick',
      openingHours
    );
    return { clock: advancedClock, events };
  }

  return { clock: { ...clock, accumulatedMs: remainingMs }, events: [] };
}

/**
 * Advance clock by one full day (1440 minutes).
 */
export function advanceDay(clock, openingHours = DEFAULT_OPENING_HOURS) {
  return advanceTime(clock, 1440, 'advance_day', openingHours);
}

/**
 * Get human-readable phase of day.
 */
export function getTimeOfDay(clock) {
  const m = (clock.gameMinutes ?? (clock.timeOfDay ?? 360)) % 1440;
  return getTimeOfDayPhase(m).phase;
}

export function pauseClock(clock) {
  return { ...clock, paused: true };
}

export function resumeClock(clock) {
  return { ...clock, paused: false };
}
