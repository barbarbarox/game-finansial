/**
 * energy.js — Player energy domain logic for Life Journey (Rule 74).
 * Pure functions without DOM or Phaser dependencies.
 */

export const DEFAULT_ENERGY_CONFIG = {
  max: 100,
  start: 100,
  passiveDrainPerGameHour: 2,
  warnAt: 25,
  criticalAt: 10,
  exhaustedSpeedMultiplier: 0.7,
  sleepRecoveryPerHour: 10,
  restRecoveryPerHour: 5,
  activityEnergyCostPerHour: {
    belajar_mandiri: 10,
    ikut_pelajaran: 5,
    main_game: 4,
    nongkrong_kafe: 2,
    baca_perpustakaan: 3,
    nonton_tv: 1
  },
  heavyActivities: [
    'belajar_mandiri',
    'ikut_pelajaran',
    'main_game'
  ],
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
    exhaustionCount: 0
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
 * @returns {{ state: object, wasExhausted: boolean, nowExhausted: boolean }}
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

  return {
    state: {
      current: next,
      max,
      exhaustionCount
    },
    wasExhausted,
    nowExhausted
  };
}

/**
 * Calculate energy drain for an activity with a specific duration in minutes.
 * @param {string} activityId
 * @param {number} minutes
 * @param {object} [config]
 * @returns {number} positive drain amount
 */
export function calculateActivityDrain(activityId, minutes, config = DEFAULT_ENERGY_CONFIG) {
  const rates = config.activityEnergyCostPerHour || DEFAULT_ENERGY_CONFIG.activityEnergyCostPerHour;
  const costPerHour = rates[activityId] || 0;
  const passivePerHour = config.passiveDrainPerGameHour ?? 2;
  const totalRatePerHour = costPerHour + passivePerHour;
  return Math.round((totalRatePerHour * minutes) / 60);
}

/**
 * Check if player can perform an activity.
 * @param {object} energyState
 * @param {string} activityId
 * @param {number} minutes
 * @param {object} [config]
 * @returns {{ canPerform: boolean, reason: string|null }}
 */
export function canPerformActivity(energyState, activityId, minutes, config = DEFAULT_ENERGY_CONFIG) {
  const current = energyState?.current ?? 100;
  const heavy = config.heavyActivities || DEFAULT_ENERGY_CONFIG.heavyActivities;

  if (current <= 0 && heavy.includes(activityId)) {
    return {
      canPerform: false,
      reason: 'Kamu terlalu lelah (Energi 0%). Beristirahatlah, makan, atau tidur terlebih dahulu!'
    };
  }

  const cost = calculateActivityDrain(activityId, minutes, config);
  if (cost > 0 && current < cost && current < 10) {
    return {
      canPerform: false,
      reason: `Energi tidak mencukupi untuk ${activityId.replace('_', ' ')} selama ${minutes} menit. Dibutuhkan minimal ${cost} energi.`
    };
  }

  return {
    canPerform: true,
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
    isWarning: percent <= 25 && percent > 10,
    isCritical: percent <= 10 && percent > 0,
    isExhausted: percent === 0,
    color: percent <= 25 ? '#C0654A' : '#6F9262'
  };
}

