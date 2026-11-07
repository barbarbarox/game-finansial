/**
 * store.js — Simple pub-sub state store for Life Journey.
 * No external dependencies. Pure JS.
 */

/**
 * Create a new store.
 * @param {object} initialState
 * @returns {object} store
 */
export function createStore(initialState) {
  let state = { ...initialState };
  const listeners = new Set();
  const eventListeners = new Map();

  return {
    /** Get current state (read-only snapshot) */
    getState() {
      return Object.freeze({ ...state });
    },

    /**
     * Merge partial state update and notify subscribers.
     * @param {object} partial
     */
    setState(partial) {
      state = { ...state, ...partial };
      for (const listener of listeners) {
        listener(state);
      }
    },

    /**
     * Subscribe to any state change.
     * @param {Function} listener - called with new state
     * @returns {Function} unsubscribe function
     */
    subscribe(listener) {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },

    /**
     * Dispatch a named event with optional payload.
     * @param {string} eventType
     * @param {*} payload
     */
    dispatch(eventType, payload) {
      const handlers = eventListeners.get(eventType) ?? [];
      for (const handler of handlers) {
        handler(payload, state);
      }
    },

    /**
     * Register a handler for a specific event type.
     * @param {string} eventType
     * @param {Function} handler - (payload, state) => void
     * @returns {Function} unregister function
     */
    on(eventType, handler) {
      if (!eventListeners.has(eventType)) {
        eventListeners.set(eventType, new Set());
      }
      eventListeners.get(eventType).add(handler);
      return () => eventListeners.get(eventType)?.delete(handler);
    },
  };
}
