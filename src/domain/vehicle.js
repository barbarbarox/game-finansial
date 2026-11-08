/**
 * vehicle.js — Player vehicle (motorcycle) domain logic (Rule 75).
 * Pure functions with zero DOM or Phaser dependencies.
 */

export const DEFAULT_VEHICLE_CONFIG = {
  speedMultiplier: 1.8,
  fuelTickSeconds: 5,
  fuelPerTick: 2,
  toggleKey: 'V',
  allowedMapKinds: ['hub'],
  autoDismountOnInterior: true,
  parkedMotorAfterDismount: true,
  mountAnimationMs: 350,
  riderColliderPx: [24, 12]
};

/**
 * Check if player can mount motorcycle.
 * @param {object} state - game state containing gasoline and vehicle info
 * @param {string} currentMapId - current map id
 * @param {object} [config]
 * @returns {{ canMount: boolean, reason: string|null }}
 */
export function canMountVehicle(state, currentMapId, config = DEFAULT_VEHICLE_CONFIG) {
  const gasoline = state?.gasoline ?? 100;

  // 1. Check fuel
  if (gasoline <= 0) {
    return {
      canMount: false,
      reason: 'Bensin habis! Dorong atau isi bensin di SPBU terlebih dahulu.'
    };
  }

  // 2. Check map allowed (hub only)
  if (currentMapId !== 'town_hub') {
    return {
      canMount: false,
      reason: 'Motor hanya dapat dikendarai di luar ruangan (Kota Harmoni)!'
    };
  }

  return {
    canMount: true,
    reason: null
  };
}

/**
 * Calculate gasoline consumption for riding.
 * Consumes fuelPerTick (default 2%) per fuelTickSeconds (default 5s) of movement.
 * @param {number} currentGasoline - 0..100
 * @param {number} deltaMs - elapsed milliseconds while moving
 * @param {number} accumulatorMs - carried over ms
 * @param {object} [config]
 * @returns {{ newGasoline: number, newAccumulatorMs: number, outOfFuel: boolean }}
 */
export function drainMovingFuel(currentGasoline, deltaMs, accumulatorMs = 0, config = DEFAULT_VEHICLE_CONFIG) {
  const tickMs = (config.fuelTickSeconds || 5) * 1000;
  const perTick = config.fuelPerTick || 2;

  let totalMs = accumulatorMs + deltaMs;
  let gas = currentGasoline;

  if (totalMs >= tickMs) {
    const ticks = Math.floor(totalMs / tickMs);
    totalMs %= tickMs;
    gas = Math.max(0, gas - (ticks * perTick));
  }

  return {
    newGasoline: gas,
    newAccumulatorMs: totalMs,
    outOfFuel: gas === 0
  };
}

