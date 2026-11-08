/**
 * inventory.js — Inventory and item domain logic for Life Journey (Rule 74).
 * Pure functions without DOM or Phaser dependencies.
 */

export const DEFAULT_INVENTORY_CONFIG = {
  slots: 5,
  stackMax: 5
};

/**
 * Create initial empty inventory.
 * @param {number} slots
 * @param {Array<{itemId: string, count: number}>} [initialItems]
 * @returns {Array<{slotIndex: number, itemId: string|null, count: number}>}
 */
export function createInventory(slots = 5, initialItems = []) {
  const inv = [];
  for (let i = 0; i < slots; i++) {
    const init = initialItems[i];
    if (init && init.itemId) {
      inv.push({
        slotIndex: i,
        itemId: init.itemId,
        count: Math.min(5, Math.max(1, init.count || 1))
      });
    } else {
      inv.push({
        slotIndex: i,
        itemId: null,
        count: 0
      });
    }
  }
  return inv;
}

/**
 * Add an item to the inventory.
 * @param {Array} inventory
 * @param {string} itemId
 * @param {number} [count=1]
 * @param {number} [stackMax=5]
 * @returns {{ ok: boolean, inventory: Array, reason: string|null, slotIndex: number|null }}
 */
export function addItem(inventory, itemId, count = 1, stackMax = 5) {
  if (!itemId || count <= 0) {
    return { ok: false, inventory, reason: 'Item tidak valid', slotIndex: null };
  }

  const next = inventory.map(s => ({ ...s }));

  // 1. Try to stack into an existing slot with same itemId and room
  for (let i = 0; i < next.length; i++) {
    if (next[i].itemId === itemId && next[i].count < stackMax) {
      const canAdd = Math.min(count, stackMax - next[i].count);
      next[i].count += canAdd;
      const remaining = count - canAdd;
      if (remaining <= 0) {
        return { ok: true, inventory: next, reason: null, slotIndex: i };
      }
      // If remaining > 0, continue looking for empty slot
      count = remaining;
    }
  }

  // 2. Find first empty slot
  for (let i = 0; i < next.length; i++) {
    if (!next[i].itemId || next[i].count <= 0) {
      next[i].itemId = itemId;
      next[i].count = Math.min(count, stackMax);
      return { ok: true, inventory: next, reason: null, slotIndex: i };
    }
  }

  // 3. Tas penuh
  return { ok: false, inventory, reason: 'Tas penuh! Gunakan atau buang item terlebih dahulu.', slotIndex: null };
}

/**
 * Remove an item from a specific slot.
 * @param {Array} inventory
 * @param {number} slotIndex
 * @param {number} [count=1]
 * @returns {{ ok: boolean, inventory: Array, removedItem: string|null }}
 */
export function removeItem(inventory, slotIndex, count = 1) {
  if (slotIndex < 0 || slotIndex >= inventory.length) {
    return { ok: false, inventory, removedItem: null };
  }

  const next = inventory.map(s => ({ ...s }));
  const slot = next[slotIndex];
  if (!slot.itemId || slot.count <= 0) {
    return { ok: false, inventory, removedItem: null };
  }

  const removedItem = slot.itemId;
  slot.count -= count;
  if (slot.count <= 0) {
    slot.itemId = null;
    slot.count = 0;
  }

  return { ok: true, inventory: next, removedItem };
}

/**
 * Use an item from a slot.
 * @param {Array} inventory
 * @param {number} slotIndex
 * @param {object} itemCatalog - map of itemId -> item definition
 * @param {object} [energyState]
 * @returns {{ ok: boolean, inventory: Array, item: object|null, reason: string|null }}
 */
export function useItem(inventory, slotIndex, itemCatalog = {}, energyState = null) {
  if (slotIndex < 0 || slotIndex >= inventory.length) {
    return { ok: false, inventory, item: null, reason: 'Slot tidak valid' };
  }

  const slot = inventory[slotIndex];
  if (!slot.itemId || slot.count <= 0) {
    return { ok: false, inventory, item: null, reason: 'Slot kosong' };
  }

  const itemDef = itemCatalog[slot.itemId] || {
    id: slot.itemId,
    label: slot.itemId,
    energy: 15,
    consumeMinutes: 3
  };

  // If energy >= 95 and item gives energy only, warn and don't consume
  if (energyState && energyState.current >= 95 && itemDef.energy > 0) {
    return {
      ok: false,
      inventory,
      item: itemDef,
      reason: 'Energimu masih sangat penuh! Simpan makanan/minuman ini untuk nanti.'
    };
  }

  const res = removeItem(inventory, slotIndex, 1);
  return {
    ok: true,
    inventory: res.inventory,
    item: itemDef,
    reason: null
  };
}

