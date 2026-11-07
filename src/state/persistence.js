/**
 * persistence.js — LocalStorage save/load with schema validation.
 * Wraps all access in try/catch. Enforces 512KB size limit.
 */

import { validateSave, migrateSave, SCHEMA_VERSION } from './schema.js';

const SAVE_KEY = 'life_journey_save_v1';
const MAX_SAVE_SIZE = 524288; // 512 KB

/**
 * Save game state to LocalStorage.
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

    localStorage.setItem(SAVE_KEY, json);
    return { success: true };
  } catch (err) {
    console.warn('[persistence] saveGame error:', err);
    return { success: false, error: err.message ?? 'Gagal menyimpan.' };
  }
}

/**
 * Load game state from LocalStorage.
 * @returns {{ success: boolean, state?: object, error?: string }}
 */
export function loadGame() {
  try {
    const raw = localStorage.getItem(SAVE_KEY);
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
 * Delete the save data.
 * @returns {{ success: boolean, error?: string }}
 */
export function resetSave() {
  try {
    localStorage.removeItem(SAVE_KEY);
    return { success: true };
  } catch (err) {
    console.warn('[persistence] resetSave error:', err);
    return { success: false, error: err.message ?? 'Gagal menghapus save.' };
  }
}
