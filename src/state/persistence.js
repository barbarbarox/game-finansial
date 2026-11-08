/**
 * persistence.js — LocalStorage save/load with schema validation.
 * Supports lj_save_v2 with auto-migration from legacy saves.
 * Wraps all access in try/catch. Enforces 512KB size limit.
 */

import { validateSave, migrateSave, SCHEMA_VERSION } from './schema.js';

export const SAVE_KEY_V3 = 'lj_save_v3';
export const SAVE_KEY_V2 = 'lj_save_v2';
export const LEGACY_SAVE_KEYS = ['lj_save_v2', 'life_journey_save_v1', 'lj_save_v1'];
const MAX_SAVE_SIZE = 524288; // 512 KB

/**
 * Save game state to LocalStorage (v3).
 * @param {object} state - game state to persist
 * @returns {{ success: boolean, error?: string }}
 */
export function saveGame(state) {
  try {
    const data = { ...state, schemaVersion: SCHEMA_VERSION };
    const json = JSON.stringify(data);

    if (json.length > MAX_SAVE_SIZE) {
      return { success: false, error: `Data save terlalu besar (${json.length} > ${MAX_SAVE_SIZE} bytes)` };
    }

    localStorage.setItem(SAVE_KEY_V3, json);
    return { success: true };
  } catch (err) {
    console.warn('[persistence] saveGame error:', err);
    return { success: false, error: err.message ?? 'Gagal menyimpan.' };
  }
}

/**
 * Load game state from LocalStorage.
 * Checks v3 first, falls back to legacy v2/v1 keys and auto-migrates.
 * @returns {{ success: boolean, state?: object, error?: string }}
 */
export function loadGame() {
  try {
    let raw = localStorage.getItem(SAVE_KEY_V3);
    let fromLegacy = false;

    if (!raw) {
      for (const legacyKey of LEGACY_SAVE_KEYS) {
        raw = localStorage.getItem(legacyKey);
        if (raw) {
          fromLegacy = true;
          break;
        }
      }
    }

    if (!raw) {
      return { success: false, error: 'Tidak ada save yang ditemukan.' };
    }

    let parsed;
    try {
      parsed = JSON.parse(raw);
    } catch (parseErr) {
      return { success: false, error: 'Data save rusak (JSON tidak valid).' };
    }

    const { valid, errors } = validateSave(parsed);
    if (!valid) {
      console.warn('[persistence] Validasi save gagal:', errors);
      return { success: false, error: 'Data save tidak valid: ' + errors.join('; ') };
    }

    const migrated = migrateSave(parsed);

    // If loaded from legacy v1, persist migrated v2 format
    if (fromLegacy) {
      saveGame(migrated);
    }

    return { success: true, state: migrated };
  } catch (err) {
    console.warn('[persistence] loadGame error:', err);
    return { success: false, error: err.message ?? 'Gagal memuat save.' };
  }
}

/**
 * Check if a valid save exists.
 * @returns {boolean}
 */
export function hasValidSave() {
  const result = loadGame();
  return result.success;
}

/**
 * Delete the save data across v2 and legacy keys.
 * @returns {{ success: boolean, error?: string }}
 */
export function resetSave() {
  try {
    localStorage.removeItem(SAVE_KEY_V3);
    localStorage.removeItem(SAVE_KEY_V2);
    for (const legacyKey of LEGACY_SAVE_KEYS) {
      localStorage.removeItem(legacyKey);
    }
    return { success: true };
  } catch (err) {
    console.warn('[persistence] resetSave error:', err);
    return { success: false, error: err.message ?? 'Gagal menghapus save.' };
  }
}
