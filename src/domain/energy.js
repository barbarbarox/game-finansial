/**
 * energy.js — Player energy domain logic for Life Journey (Rules 74 & 83 - Energy v2).
 * Pure functions without DOM or Phaser dependencies.
 */

export const DEFAULT_ENERGY_CONFIG = {
  max: 100,
  start: 100,
  passiveDrainPerGameHour: 1.5,
  warnBelowPercent: 50,
  warnRearmAbovePercent: 60,
  warnText: 'Energi kamu di bawah 50%, silakan makan untuk menambahnya.',
  criticalAtPercent: 25,
  veryLowAtPercent: 10,
  veryLowSpeedMultiplier: 0.85,
  confirmIfProjectedBelowPercent: 10,
  walkDrainPerMovingSecond: 0.03,
  sleepRecoveryPerHour: 10,
  restRecoveryPerHour: 5,
  activityCosts: {
    ikut_pelajaran: {
      totalPercent: 20,
      sessions: {
        sesi1: { hours: 3 }, // 180 min -> ~9%
        sesi2: { hours: 4 }  // 240 min -> ~11%
      }
    },
    pelajaran_sekolah: {
      totalPercent: 20
    },
    main_game: { percentPerHour: 20 },
    belajar_mandiri: { percentPerHour: 8 },
    baca_perpustakaan: { percentPerHour: 3 },
    baca_buku: { percentPerHour: 3 },
    nongkrong_kafe: { percentPerHour: 4 },
    nonton_mini: { percentPerHour: 2 },
    nonton_tv: { percentPerHour: 1 },
    tv: { percentPerHour: 1 },
    mandi: { flatPercent: 1 }
  },
  heavyActivities: [
    'belajar_mandiri',
    'ikut_pelajaran',
    'pelajaran_sekolah',
    'main_game'
  ],
  exhausted: {
    wakeHour: 10,
    wakeEnergyPercent: 50,
    attendanceMissedIncrement: 1,
    message: 'Kamu bangun kesiangan karena kelelahan.'
  },
  makan_rumah: {
    energy: 40,
    minutes: 20,
    cost: 0
  }
};

/**
 * Create initial energy state.
 * @param {object} [config]
 * @returns {object}
 */
export function createEnergyState(config = DEFAULT_ENERGY_CONFIG) {
  return {
    current: config.start ?? 100,
    max: config.max ?? 100,
    exhaustionCount: 0,
    warn50Triggered: false,
    warn25Triggered: false
  };
}

/**
 * Clamp energy value between 0 and max.
 * @param {number} val
 * @param {number} max
 * @returns {number}
 */
export function clampEnergy(val, max = 100) {
  return Math.max(0, Math.min(max, Math.round(val)));
}

/**
 * Apply energy change.
 * @param {object} energyState
 * @param {number} delta - positive for recovery, negative for drain
 * @param {object} [config]
 * @returns {{ state: object, wasExhausted: boolean, nowExhausted: boolean, showWarn50: boolean, showWarn25: boolean }}
 */
export function changeEnergy(energyState, delta, config = DEFAULT_ENERGY_CONFIG) {
  const current = energyState.current ?? 100;
  const max = config.max ?? energyState.max ?? 100;
  const next = clampEnergy(current + delta, max);
  const wasExhausted = current === 0;
  const nowExhausted = next === 0;
  const exhaustionCount = (nowExhausted && !wasExhausted)
    ? (energyState.exhaustionCount || 0) + 1
    : (energyState.exhaustionCount || 0);

  let warn50Triggered = energyState.warn50Triggered || false;
  let warn25Triggered = energyState.warn25Triggered || false;

  let showWarn50 = false;
  let showWarn25 = false;

  // Thresholds (Rule 83 §2)
  if (next < 50 && !warn50Triggered && next > 0) {
    showWarn50 = true;
    warn50Triggered = true;
  }
  if (next >= 60) {
    warn50Triggered = false;
  }

  if (next <= 25 && !warn25Triggered && next > 0) {
    showWarn25 = true;
    warn25Triggered = true;
  }
  if (next > 30) {
    warn25Triggered = false;
  }

  return {
    state: {
      current: next,
      max,
      exhaustionCount,
      warn50Triggered,
      warn25Triggered
    },
    wasExhausted,
    nowExhausted,
    showWarn50,
    showWarn25
  };
}

/**
 * Calculate energy drain for an activity with a specific duration in minutes.
 * Follows Rule 83 table strictly.
 * @param {string} activityId
 * @param {number} minutes
 * @param {object} [config]
 * @returns {number} positive drain amount
 */
export function calculateActivityDrain(activityId, minutes, config = DEFAULT_ENERGY_CONFIG) {
  // 1. School Lesson (Sesi 1: 180 min -> ~9%, Sesi 2: 240 min -> ~11%, Full day: exact 20%)
  if (activityId === 'ikut_pelajaran' || activityId === 'pelajaran_sekolah') {
    if (minutes <= 180) {
      return Math.round((minutes * 20) / 420); // 180 min -> 9%
    } else if (minutes <= 240) {
      return Math.round((minutes * 20) / 420); // 240 min -> 11%
    } else {
      return Math.min(20, Math.round((minutes * 20) / 420));
    }
  }

  // 2. Game Center (-20% per hour)
  if (activityId === 'main_game') {
    return Math.round((20 * minutes) / 60);
  }

  // 3. Belajar Mandiri (-8% per hour)
  if (activityId === 'belajar_mandiri') {
    return Math.round((8 * minutes) / 60);
  }

  // 4. Perpustakaan (-3% per hour)
  if (activityId === 'baca_perpustakaan' || activityId === 'baca_buku') {
    return Math.round((3 * minutes) / 60);
  }

  // 5. Kafe (-4% per hour)
  if (activityId === 'nongkrong_kafe') {
    return Math.round((4 * minutes) / 60);
  }

  // 6. Bioskop mini (-2% per hour)
  if (activityId === 'nonton_mini') {
    return Math.round((2 * minutes) / 60);
  }

  // 7. TV (-1% per hour)
  if (activityId === 'nonton_tv' || activityId === 'tv') {
    return Math.round((1 * minutes) / 60);
  }

  // 8. Mandi (-1% flat)
  if (activityId === 'mandi') {
    return 1;
  }

  // Fallback to configured rates
  const rates = config.activityEnergyCostPerHour || {};
  const costPerHour = rates[activityId] || 0;
  return Math.round((costPerHour * minutes) / 60);
}

/**
 * Check if player can perform an activity.
 * @param {object} energyState
 * @param {string} activityId
 * @param {number} minutes
 * @param {object} [config]
 * @returns {{ canPerform: boolean, cost: number, projected: number, confirmRequired: boolean, confirmMessage: string|null, reason: string|null }}
 */
export function canPerformActivity(energyState, activityId, minutes, config = DEFAULT_ENERGY_CONFIG) {
  const current = energyState?.current ?? 100;
  const cost = calculateActivityDrain(activityId, minutes, config);

  if (current <= 0) {
    return {
      canPerform: false,
      cost,
      projected: 0,
      confirmRequired: false,
      confirmMessage: null,
      reason: 'Kamu terlalu lelah (Energi 0%). Beristirahatlah, makan, atau tidur terlebih dahulu!'
    };
  }

  const projected = current - cost;
  const confirmRequired = projected < 10;

  return {
    canPerform: true,
    cost,
    projected,
    confirmRequired,
    confirmMessage: confirmRequired ? 'Energi tidak cukup, kamu bisa pingsan. Lanjutkan?' : null,
    reason: null
  };
}

/**
 * Get status label and color token for energy display.
 * @param {number} current
 * @param {number} max
 * @returns {{ percent: number, isWarning: boolean, isCritical: boolean, isExhausted: boolean, color: string }}
 */
export function getEnergyStatus(current, max = 100) {
  const percent = max > 0 ? Math.round((current / max) * 100) : 0;
  return {
    percent,
    isWarning: percent < 50 && percent > 25,
    isCritical: percent <= 25 && percent > 0,
    isExhausted: percent === 0,
    color: percent <= 25 ? '#C0654A' : '#6F9262'
  };
}
