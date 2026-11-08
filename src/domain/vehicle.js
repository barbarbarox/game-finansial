/**
 * vehicle.js — Player vehicle (motorcycle) domain logic (Rule 75 & Rule 78 §4).
 * Pure functions with zero DOM or Phaser dependencies.
 */

import { emit, DOMAIN_EVENTS } from './events.js';

export const DEFAULT_VEHICLE_CONFIG = {
  speedMultiplier: 1.8,
  fuelTickSeconds: 5,
  fuelPerTick: 2,
  toggleKey: 'V',
  allowedMapKinds: ['hub'],
  autoDismountOnInterior: true,
  parkedMotorAfterDismount: true,
  mountAnimationMs: 350,
  riderColliderPx: [24, 12],
  pricePerPercent: 500
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
 * Check if player can refuel.
 * @param {object} state
 * @returns {{ canRefuel: boolean, reason: string|null, currentGasoline: number }}
 */
export function canRefuel(state) {
  const currentGas = state?.gasoline ?? 100;
  if (currentGas >= 100) {
    return {
      canRefuel: false,
      reason: 'Tangki bensin sudah penuh 100%!',
      currentGasoline: currentGas
    };
  }
  return {
    canRefuel: true,
    reason: null,
    currentGasoline: currentGas
  };
}

/**
 * Calculate cost to fill tank to 100%.
 * @param {number} currentGasoline
 * @param {number} [pricePerPercent]
 * @returns {number}
 */
export function calculateFillCost(currentGasoline, pricePerPercent = 500) {
  const needed = Math.max(0, 100 - currentGasoline);
  return needed * pricePerPercent;
}

/**
 * Refuel by a specific percentage.
 * @param {object} state
 * @param {number} percent - percentage to add (e.g. 20 for 20%)
 * @param {number} [pricePerPercent]
 * @returns {{ newState: object, addedPercent: number, cost: number, newGasoline: number }}
 */
export function refuelPercent(state, percent, pricePerPercent = 500) {
  const currentGas = state?.gasoline ?? 100;
  const maxCanAdd = Math.max(0, 100 - currentGas);
  const actualAdd = Math.min(maxCanAdd, Math.max(0, percent));
  const newGas = Math.min(100, Math.round(currentGas + actualAdd));
  const cost = actualAdd * pricePerPercent;

  const newState = {
    ...state,
    gasoline: newGas
  };

  emit(DOMAIN_EVENTS.FUEL_CHANGED, {
    gasoline: newGas,
    previousGasoline: currentGas,
    addedPercent: actualAdd,
    cost
  });

  return {
    newState,
    addedPercent: actualAdd,
    cost,
    newGasoline: newGas
  };
}

/**
 * Refuel by rupiah amount.
 * @param {object} state
 * @param {number} rupiahAmount
 * @param {number} [pricePerPercent]
 * @returns {{ newState: object, addedPercent: number, cost: number, newGasoline: number }}
 */
export function refuelAmount(state, rupiahAmount, pricePerPercent = 500) {
  const currentGas = state?.gasoline ?? 100;
  const maxCanAdd = Math.max(0, 100 - currentGas);
  const percentFromMoney = Math.floor(rupiahAmount / pricePerPercent);
  const actualAdd = Math.min(maxCanAdd, percentFromMoney);
  const cost = actualAdd * pricePerPercent;
  const newGas = Math.min(100, Math.round(currentGas + actualAdd));

  const newState = {
    ...state,
    gasoline: newGas
  };

  emit(DOMAIN_EVENTS.FUEL_CHANGED, {
    gasoline: newGas,
    previousGasoline: currentGas,
    addedPercent: actualAdd,
    cost
  });

  return {
    newState,
    addedPercent: actualAdd,
    cost,
    newGasoline: newGas
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
    const oldGas = gas;
    gas = Math.max(0, gas - (ticks * perTick));

    if (gas !== oldGas) {
      emit(DOMAIN_EVENTS.FUEL_CHANGED, {
        gasoline: gas,
        previousGasoline: oldGas,
        drained: oldGas - gas
      });
    }
  }

  return {
    newGasoline: gas,
    newAccumulatorMs: totalMs,
    outOfFuel: gas === 0
  };
}
