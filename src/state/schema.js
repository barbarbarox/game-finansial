/**
 * schema.js — Save-game schema definition and validation.
 * Protects against tampered/corrupt LocalStorage data.
 * Complies with Rule 50 (Security) and Rule 72 (Time System v2).
 */

export const SCHEMA_VERSION = 3;

/**
 * Whitelist of allowed top-level keys and their types.
 */
export const SAVE_SCHEMA = {
  schemaVersion: { type: 'number', required: true },
  playerName: { type: 'string', required: false, maxLen: 20 },
  fatherName: { type: 'string', required: false, maxLen: 20 },
  motherName: { type: 'string', required: false, maxLen: 20 },
  gender: { type: 'string', required: false, enum: ['m', 'f'] },
  character: { type: 'object', required: false },
  ledger: { type: 'object', required: true },
  clock: { type: 'object', required: true },
  budget: { type: 'object', required: false },
  missions: { type: 'array', required: false },
  gasoline: { type: 'number', required: false, min: 0, max: 100 },
  energy: { type: 'object', required: false },
  inventory: { type: 'array', required: false },
  vehicle: { type: 'object', required: false },
  eventEngine: { type: 'object', required: false },
  flags: { type: 'object', required: false },
  seed: { type: 'number', required: false },
  eventsResolved: { type: 'number', required: false, min: 0 },
  savingsEver: { type: 'boolean', required: false },
  budgetSet: { type: 'boolean', required: false },
  month1NoBroke: { type: 'boolean', required: false },
  currentMap: { type: 'string', required: false },
  playerPos: { type: 'object', required: false },
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

  // Check schema version
  if (typeof data.schemaVersion !== 'number' || data.schemaVersion < 1) {
    errors.push('schemaVersion tidak valid.');
  }

  // Ensure character info exists either in character object or top-level fields
  const hasCharName = (typeof data.playerName === 'string' && data.playerName.length > 0) ||
                      (data.character && typeof data.character.name === 'string');
  if (!hasCharName) {
    errors.push('Nama karakter tidak ditemukan.');
  }

  const hasGender = (typeof data.gender === 'string') ||
                    (data.character && typeof data.character.gender === 'string');
  if (!hasGender) {
    errors.push('Gender karakter tidak ditemukan.');
  }

  // Validate each known field
  for (const [key, def] of Object.entries(SAVE_SCHEMA)) {
    const value = data[key];

    if (value === undefined || value === null) {
      if (def.required) {
        errors.push(`Field wajib hilang: ${key}`);
      }
      continue;
    }

    // Type check
    const actualType = Array.isArray(value) ? 'array' : typeof value;
    if (actualType !== def.type) {
      errors.push(`Field ${key} bertipe ${actualType}, diharapkan ${def.type}`);
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
 * Migrate save data to current schema version (v2).
 * Returns a clean, whitelisted copy of the data.
 * @param {object} data
 * @returns {object} migrated data
 */
export function migrateSave(data) {
  const clean = Object.create(null);

  // Copy only whitelisted fields
  for (const key of Object.keys(SAVE_SCHEMA)) {
    if (FORBIDDEN_KEYS.has(key)) continue;
    if (key in data) {
      clean[key] = data[key];
    }
  }

  clean.schemaVersion = SCHEMA_VERSION;

  // Defaults
  clean.eventsResolved = clean.eventsResolved ?? 0;
  clean.savingsEver = clean.savingsEver ?? false;
  clean.budgetSet = clean.budgetSet ?? false;
  clean.month1NoBroke = clean.month1NoBroke ?? false;
  clean.flags = clean.flags ?? {};
  clean.gasoline = clean.gasoline ?? 100;
  clean.missions = clean.missions ?? [];
  clean.budget = clean.budget ?? {};
  clean.currentMap = clean.currentMap ?? 'home';

  // Energy & Inventory (Rule 74, Save v3)
  clean.energy = clean.energy ? {
    current: Math.max(0, Math.min(clean.energy.max ?? 100, Math.round(clean.energy.current ?? 100))),
    max: clean.energy.max ?? 100,
    exhaustionCount: clean.energy.exhaustionCount ?? 0
  } : {
    current: 100,
    max: 100,
    exhaustionCount: 0
  };

  clean.inventory = Array.isArray(clean.inventory) ? clean.inventory : [
    { slotIndex: 0, itemId: null, count: 0 },
    { slotIndex: 1, itemId: null, count: 0 },
    { slotIndex: 2, itemId: null, count: 0 },
    { slotIndex: 3, itemId: null, count: 0 },
    { slotIndex: 4, itemId: null, count: 0 }
  ];

  // Standardize character
  if (!clean.character && clean.playerName) {
    clean.character = {
      name: clean.playerName,
      gender: clean.gender || 'm',
      fatherName: clean.fatherName || 'Ayah',
      motherName: clean.motherName || 'Ibu'
    };
  }

  // Standardize clock for v2 (gameMinutes)
  if (clean.clock) {
    const day = clean.clock.day ?? 1;
    const timeOfDay = clean.clock.timeOfDay ?? (clean.clock.gameMinutes ? clean.clock.gameMinutes % 1440 : 360);
    const gameMinutes = clean.clock.gameMinutes ?? (((day - 1) * 1440) + timeOfDay);

    clean.clock = {
      ...clean.clock,
      day,
      month: clean.clock.month ?? 1,
      year: clean.clock.year ?? 1,
      timeOfDay,
      gameMinutes,
      accumulatedMs: clean.clock.accumulatedMs ?? 0,
      totalDays: clean.clock.totalDays ?? (day - 1),
      paused: false,
      finished: Boolean(clean.clock.finished)
    };
  }

  return clean;
}
