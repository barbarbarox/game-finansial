/**
 * schema.js — Save-game schema definition and validation.
 * Protects against tampered/corrupt LocalStorage data.
 */

export const SCHEMA_VERSION = 1;

/**
 * Whitelist of allowed top-level keys and their types.
 * type: 'string' | 'number' | 'boolean' | 'object' | 'array'
 */
export const SAVE_SCHEMA = {
  schemaVersion: { type: 'number', required: true },
  playerName: { type: 'string', required: true, maxLen: 20 },
  fatherName: { type: 'string', required: false, maxLen: 20 },
  motherName: { type: 'string', required: false, maxLen: 20 },
  gender: { type: 'string', required: true, enum: ['m', 'f'] },
  ledger: { type: 'object', required: true },
  clock: { type: 'object', required: true },
  budget: { type: 'object', required: true },
  missions: { type: 'array', required: true },
  gasoline: { type: 'number', required: true, min: 0, max: 100 },
  eventEngine: { type: 'object', required: false },
  flags: { type: 'object', required: false },
  eventsResolved: { type: 'number', required: false, min: 0 },
  savingsEver: { type: 'boolean', required: false },
  budgetSet: { type: 'boolean', required: false },
  month1NoBroke: { type: 'boolean', required: false },
};

/** Dangerous prototype-pollution keys */
const FORBIDDEN_KEYS = new Set(['__proto__', 'constructor', 'prototype']);

/**
 * Validate a saved game object against the schema.
 * @param {*} data
 * @returns {{ valid: boolean, errors: string[] }}
 */
export function validateSave(data) {
  const errors = [];

  if (data === null || typeof data !== 'object' || Array.isArray(data)) {
    return { valid: false, errors: ['Save data harus berupa object.'] };
  }

  // Check for forbidden keys (prototype pollution)
  for (const key of Object.keys(data)) {
    if (FORBIDDEN_KEYS.has(key)) {
      errors.push(`Kunci terlarang ditemukan: ${key}`);
    }
  }

  // Check schema version first
  if (typeof data.schemaVersion !== 'number') {
    errors.push('schemaVersion tidak valid.');
  }

  // Validate each known field
  for (const [key, def] of Object.entries(SAVE_SCHEMA)) {
    const value = data[key];

    if (value === undefined || value === null) {
      if (def.required) {
        errors.push(`Field wajib tidak ada: ${key}`);
      }
      continue;
    }

    // Type check
    if (def.type === 'array') {
      if (!Array.isArray(value)) {
        errors.push(`Field ${key} harus berupa array.`);
      }
    } else if (typeof value !== def.type) {
      errors.push(`Field ${key} harus bertipe ${def.type}, ditemukan ${typeof value}.`);
      continue;
    }

    // String constraints
    if (def.type === 'string') {
      if (def.maxLen && value.length > def.maxLen) {
        errors.push(`Field ${key} terlalu panjang (maks ${def.maxLen}).`);
      }
      if (def.enum && !def.enum.includes(value)) {
        errors.push(`Field ${key} harus salah satu dari: ${def.enum.join(', ')}.`);
      }
    }

    // Number constraints
    if (def.type === 'number') {
      if (def.min !== undefined && value < def.min) {
        errors.push(`Field ${key} harus >= ${def.min}.`);
      }
      if (def.max !== undefined && value > def.max) {
        errors.push(`Field ${key} harus <= ${def.max}.`);
      }
      if (!Number.isFinite(value)) {
        errors.push(`Field ${key} harus bilangan finite.`);
      }
    }
  }

  return { valid: errors.length === 0, errors };
}

/**
 * Migrate save data to current schema version.
 * Returns a clean, whitelisted copy of the data.
 * @param {object} data
 * @returns {object} migrated data
 */
export function migrateSave(data) {
  // Create clean object (no prototype pollution)
  const clean = Object.create(null);

  // Copy only whitelisted fields
  for (const key of Object.keys(SAVE_SCHEMA)) {
    if (FORBIDDEN_KEYS.has(key)) continue;
    if (key in data) {
      clean[key] = data[key];
    }
  }

  // Set current schema version
  clean.schemaVersion = SCHEMA_VERSION;

  // Migration: v0 → v1 (add missing fields with defaults)
  clean.eventsResolved = clean.eventsResolved ?? 0;
  clean.savingsEver = clean.savingsEver ?? false;
  clean.budgetSet = clean.budgetSet ?? false;
  clean.month1NoBroke = clean.month1NoBroke ?? false;
  clean.flags = clean.flags ?? {};
  clean.gasoline = clean.gasoline ?? 100;

  return clean;
}
