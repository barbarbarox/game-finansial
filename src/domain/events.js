/**
 * events.js — Typed Domain Events for Life Journey (Rule 78 §4).
 * Pure pub/sub event bus with zero DOM or Phaser dependencies.
 */

const subscribers = new Map();

export const DOMAIN_EVENTS = {
  FUEL_CHANGED: 'fuelChanged',
  CASH_CHANGED: 'cashChanged',
  SAVINGS_CHANGED: 'savingsChanged',
  ENERGY_CHANGED: 'energyChanged',
  INVENTORY_CHANGED: 'inventoryChanged',
  BACKPACK_CHANGED: 'backpackChanged',
  MAP_CHANGED: 'mapChanged',
  MISSION_CHANGED: 'missionChanged',
  TIME_CHANGED: 'timeChanged',
  // Tutorial & Interaction Events (Rule 82)
  PLAYER_MOVED: 'playerMoved',
  DIALOGUE_OPENED: 'dialogueOpened',
  ALLOWANCE_GRANTED: 'allowanceGranted',
  ACTIVITY_COMPLETED: 'activityCompleted',
  BUDGET_SET: 'budgetSet',
  SAVINGS_DEPOSITED: 'savingsDeposited',
  PURCHASE_COMPLETED: 'purchaseCompleted',
  ITEM_USED: 'itemUsed',
  VEHICLE_MOUNTED: 'vehicleMounted',
  REFUELED: 'refueled',
  BACKPACK_OPENED: 'backpackOpened',
  TUTORIAL_STEP_CHANGED: 'tutorialStepChanged',
  TUTORIAL_COMPLETED: 'tutorialCompleted'
};

/**
 * Subscribe to a domain event.
 * @param {string} eventType - from DOMAIN_EVENTS or custom string
 * @param {Function} handler - callback(payload)
 * @returns {Function} unsubscribe function
 */
export function subscribe(eventType, handler) {
  if (typeof handler !== 'function') {
    throw new TypeError(`Handler for ${eventType} must be a function`);
  }
  if (!subscribers.has(eventType)) {
    subscribers.set(eventType, new Set());
  }
  const handlers = subscribers.get(eventType);
  handlers.add(handler);

  return function unsubscribe() {
    handlers.delete(handler);
    if (handlers.size === 0) {
      subscribers.delete(eventType);
    }
  };
}

/**
 * Emit a typed domain event with payload.
 * @param {string} eventType
 * @param {any} payload
 */
export function emit(eventType, payload) {
  if (!subscribers.has(eventType)) return;
  const handlers = subscribers.get(eventType);
  for (const handler of Array.from(handlers)) {
    try {
      handler(payload);
    } catch (err) {
      console.error(`[DomainEvents] Error in handler for ${eventType}:`, err);
    }
  }
}

/**
 * Count active subscribers for an event type (for audit and tests).
 * @param {string} eventType
 * @returns {number}
 */
export function getSubscribersCount(eventType) {
  return subscribers.has(eventType) ? subscribers.get(eventType).size : 0;
}

/**
 * Get all registered event types that have at least 1 subscriber.
 * @returns {string[]}
 */
export function getRegisteredEventTypes() {
  return Array.from(subscribers.keys());
}

/**
 * Clear all subscribers (useful between test runs).
 */
export function clearSubscribers() {
  subscribers.clear();
}

