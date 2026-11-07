/**
 * eventEngine.js — Event system with seedable RNG for Life Journey.
 * Uses xorshift32 for deterministic pseudo-randomness.
 */

/**
 * xorshift32 PRNG — fast, seedable, good distribution.
 * @param {number} seed - 32-bit integer seed
 * @returns {{ next: () => number, state: number }}
 */
function createRNG(seed) {
  let state = (seed >>> 0) || 1; // ensure non-zero
  return {
    next() {
      state ^= state << 13;
      state ^= state >>> 17;
      state ^= state << 5;
      state = state >>> 0;
      return state / 0xFFFFFFFF; // [0, 1)
    },
    get state() { return state; },
  };
}

/**
 * Create an event engine.
 * @param {object} eventsData - parsed events.phase1.json
 * @param {number} seed - RNG seed
 * @returns {object} engine
 */
export function createEventEngine(eventsData, seed) {
  const events = (eventsData.events ?? []).map(e => ({ ...e }));
  const rng = createRNG(seed);
  const consumed = new Set(); // non-repeatable events that fired

  return {
    events,
    rng,
    consumed,
    version: eventsData.version ?? 1,
  };
}

/**
 * Pick a random event that matches current game state.
 * @param {object} engine
 * @param {object} state - current game state (cash, gasoline, etc.)
 * @param {number} currentDay
 * @param {number} currentMonth
 * @returns {object|null} event or null
 */
export function pickEvent(engine, state, currentDay, currentMonth) {
  const { events, rng, consumed } = engine;

  // Normalize day to [1..30] within the phase
  const totalDayInPhase = (currentMonth - 1) * 30 + currentDay;

  const eligible = events.filter(ev => {
    // Skip consumed non-repeatable
    if (!ev.repeatable && consumed.has(ev.id)) return false;

    // Day window (across the whole phase)
    const minDay = ev.triggerWindow?.dayMin ?? 1;
    const maxDay = ev.triggerWindow?.dayMax ?? 60;
    if (totalDayInPhase < minDay || totalDayInPhase > maxDay) return false;

    // Conditions
    const cond = ev.conditions ?? {};
    if (cond.minCash !== undefined && state.cash < cond.minCash) return false;
    if (cond.maxCash !== undefined && state.cash > cond.maxCash) return false;
    if (cond.gasolineMax !== undefined && state.gasoline > cond.gasolineMax) return false;
    if (cond.gasolineMin !== undefined && state.gasoline < cond.gasolineMin) return false;

    return true;
  });

  if (eligible.length === 0) return null;

  // Weighted random selection
  const totalWeight = eligible.reduce((s, ev) => s + (ev.weight ?? 1), 0);
  let pick = rng.next() * totalWeight;
  for (const ev of eligible) {
    pick -= ev.weight ?? 1;
    if (pick <= 0) return ev;
  }
  return eligible[eligible.length - 1];
}

/**
 * Mark an event as consumed (prevent repeat for non-repeatable).
 * @param {object} engine
 * @param {string} eventId
 * @returns {object} new engine
 */
export function consumeEvent(engine, eventId) {
  const newConsumed = new Set(engine.consumed);
  newConsumed.add(eventId);
  return { ...engine, consumed: newConsumed };
}

/**
 * Serialize engine state for save/load.
 * @param {object} engine
 * @returns {object}
 */
export function serializeEngine(engine) {
  return {
    rngState: engine.rng.state,
    consumed: Array.from(engine.consumed),
  };
}

/**
 * Restore engine from serialized state.
 * @param {object} eventsData
 * @param {object} saved - output of serializeEngine
 * @returns {object} engine
 */
export function deserializeEngine(eventsData, saved) {
  const engine = createEventEngine(eventsData, saved.rngState ?? 1);
  engine.consumed = new Set(saved.consumed ?? []);
  return engine;
}
