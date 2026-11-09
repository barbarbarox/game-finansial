/**
 * inventory.js — Inventory domain logic for Life Journey V5 (Rule 80).
 * Implements 5-slot hotbar + 20-slot backpack with auto-overflow and auto-refill.
 * Pure functions with zero DOM or Phaser dependencies.
 */

import { emit, DOMAIN_EVENTS } from './events.js';

export const INVENTORY_CONFIG = {
  hotbarSlots: 5,
  backpackSlots: 20,
  stackMax: 5
};

/**
 * Normalise any inventory data structure (v3 array or v4 object) into standard { hotbar, backpack }.
 * @param {any} raw
 * @returns {{ hotbar: Array<{itemId: string, count: number}|null>, backpack: Array<{itemId: string, count: number}|null> }}
 */
export function normalizeInventory(raw) {
  const hotbar = Array(INVENTORY_CONFIG.hotbarSlots).fill(null);
  const backpack = Array(INVENTORY_CONFIG.backpackSlots).fill(null);

  if (!raw) return { hotbar, backpack };

  if (Array.isArray(raw)) {
    // Legacy v3 flat array migration (first 5 -> hotbar, remaining -> backpack)
    let bIdx = 0;
    for (let i = 0; i < raw.length; i++) {
      const item = raw[i];
      if (!item || !item.itemId || item.count <= 0) continue;
      const slot = { itemId: item.itemId, count: Math.min(INVENTORY_CONFIG.stackMax, item.count) };
      if (i < INVENTORY_CONFIG.hotbarSlots) {
        hotbar[i] = slot;
      } else if (bIdx < INVENTORY_CONFIG.backpackSlots) {
        backpack[bIdx++] = slot;
      }
    }
    return autoRefill({ hotbar, backpack });
  }

  if (typeof raw === 'object') {
    const rawHotbar = Array.isArray(raw.hotbar) ? raw.hotbar : [];
    const rawBackpack = Array.isArray(raw.backpack) ? raw.backpack : [];

    for (let i = 0; i < INVENTORY_CONFIG.hotbarSlots; i++) {
      const item = rawHotbar[i];
      if (item && item.itemId && item.count > 0) {
        hotbar[i] = { itemId: item.itemId, count: Math.min(INVENTORY_CONFIG.stackMax, item.count) };
      }
    }
    for (let i = 0; i < INVENTORY_CONFIG.backpackSlots; i++) {
      const item = rawBackpack[i];
      if (item && item.itemId && item.count > 0) {
        backpack[i] = { itemId: item.itemId, count: Math.min(INVENTORY_CONFIG.stackMax, item.count) };
      }
    }
    return autoRefill({ hotbar, backpack });
  }

  return { hotbar, backpack };
}

/**
 * Create initial empty inventory.
 * @returns {{ hotbar: Array, backpack: Array }}
 */
export function createInventory() {
  return {
    hotbar: Array(INVENTORY_CONFIG.hotbarSlots).fill(null),
    backpack: Array(INVENTORY_CONFIG.backpackSlots).fill(null)
  };
}

/**
 * Count total items stored in backpack.
 * @param {object} inventory
 * @returns {number}
 */
export function getBackpackCount(inventory) {
  const norm = normalizeInventory(inventory);
  return norm.backpack.reduce((sum, slot) => sum + (slot ? slot.count : 0), 0);
}

/**
 * Check if count items can fit in inventory (all-or-nothing check).
 * @param {object} inventory
 * @param {string} itemId
 * @param {number} [count=1]
 * @param {number} [stackMax=5]
 * @returns {{ canAdd: boolean, reason: string|null }}
 */
export function canAdd(inventory, itemId, count = 1, stackMax = INVENTORY_CONFIG.stackMax) {
  if (!itemId || count <= 0) {
    return { canAdd: false, reason: 'Item atau jumlah tidak valid' };
  }

  const norm = normalizeInventory(inventory);
  let needed = count;

  // 1. Check space in hotbar matching stacks
  for (const slot of norm.hotbar) {
    if (slot && slot.itemId === itemId && slot.count < stackMax) {
      needed -= (stackMax - slot.count);
      if (needed <= 0) return { canAdd: true, reason: null };
    }
  }

  // 2. Check empty hotbar slots
  for (const slot of norm.hotbar) {
    if (!slot) {
      needed -= stackMax;
      if (needed <= 0) return { canAdd: true, reason: null };
    }
  }

  // 3. Check space in backpack matching stacks
  for (const slot of norm.backpack) {
    if (slot && slot.itemId === itemId && slot.count < stackMax) {
      needed -= (stackMax - slot.count);
      if (needed <= 0) return { canAdd: true, reason: null };
    }
  }

  // 4. Check empty backpack slots
  for (const slot of norm.backpack) {
    if (!slot) {
      needed -= stackMax;
      if (needed <= 0) return { canAdd: true, reason: null };
    }
  }

  return {
    canAdd: false,
    reason: 'Tas penuh! Kapasitas hotbar dan ransel sudah mencapai batas maksimal (25 slot).'
  };
}

/**
 * Add items into inventory with overflow to backpack and event emissions.
 * @param {object} inventory
 * @param {string} itemId
 * @param {number} [count=1]
 * @param {number} [stackMax=5]
 * @returns {{ ok: boolean, inventory: object, reason: string|null }}
 */
export function addItem(inventory, itemId, count = 1, stackMax = INVENTORY_CONFIG.stackMax) {
  const check = canAdd(inventory, itemId, count, stackMax);
  if (!check.canAdd) {
    return { ok: false, success: false, inventory, reason: check.reason };
  }

  const norm = normalizeInventory(inventory);
  const hotbar = norm.hotbar.map(s => (s ? { ...s } : null));
  const backpack = norm.backpack.map(s => (s ? { ...s } : null));
  let remaining = count;

  // Step 1: Add to existing hotbar stacks of same item
  for (let i = 0; i < hotbar.length && remaining > 0; i++) {
    if (hotbar[i] && hotbar[i].itemId === itemId && hotbar[i].count < stackMax) {
      const space = stackMax - hotbar[i].count;
      const add = Math.min(remaining, space);
      hotbar[i].count += add;
      remaining -= add;
    }
  }

  // Step 2: Add to empty hotbar slots
  for (let i = 0; i < hotbar.length && remaining > 0; i++) {
    if (!hotbar[i]) {
      const add = Math.min(remaining, stackMax);
      hotbar[i] = { itemId, count: add };
      remaining -= add;
    }
  }

  // Step 3: Add to existing backpack stacks of same item
  for (let i = 0; i < backpack.length && remaining > 0; i++) {
    if (backpack[i] && backpack[i].itemId === itemId && backpack[i].count < stackMax) {
      const space = stackMax - backpack[i].count;
      const add = Math.min(remaining, space);
      backpack[i].count += add;
      remaining -= add;
    }
  }

  // Step 4: Add to empty backpack slots
  for (let i = 0; i < backpack.length && remaining > 0; i++) {
    if (!backpack[i]) {
      const add = Math.min(remaining, stackMax);
      backpack[i] = { itemId, count: add };
      remaining -= add;
    }
  }

  const result = autoRefill({ hotbar, backpack });

  emit(DOMAIN_EVENTS.INVENTORY_CHANGED, result);
  emit(DOMAIN_EVENTS.BACKPACK_CHANGED, {
    backpack: result.backpack,
    count: getBackpackCount(result)
  });

  return { ok: true, success: true, inventory: result, reason: null };
}

/**
 * Automatically refills empty hotbar slots from backpack.
 * Enforces invariant: If there is an empty hotbar slot, backpack must be empty.
 * Priority: same item as preferredItemId if provided, else first occupied backpack slot.
 * @param {{ hotbar: Array, backpack: Array }} inv
 * @param {string|null} [preferredItemId=null]
 * @param {number} [stackMax=5]
 * @returns {{ hotbar: Array, backpack: Array }}
 */
export function autoRefill(inv, preferredItemId = null, stackMax = INVENTORY_CONFIG.stackMax) {
  const hotbar = (inv.hotbar || []).map(s => (s ? { ...s } : null));
  const backpack = (inv.backpack || []).map(s => (s ? { ...s } : null));

  while (true) {
    const emptySlotIdx = hotbar.findIndex(s => s === null);
    if (emptySlotIdx === -1) break; // Hotbar is full

    // Find donor slot in backpack
    let donorIdx = -1;
    if (preferredItemId) {
      donorIdx = backpack.findIndex(s => s && s.itemId === preferredItemId);
    }
    if (donorIdx === -1) {
      donorIdx = backpack.findIndex(s => s !== null && s.count > 0);
    }
    if (donorIdx === -1) break; // Backpack is completely empty

    // Move donor stack to hotbar
    hotbar[emptySlotIdx] = { ...backpack[donorIdx] };
    backpack[donorIdx] = null;
  }

  return { hotbar, backpack };
}

/**
 * Use an item from hotbar or backpack.
 * @param {object} inventory
 * @param {'hotbar'|'backpack'} location
 * @param {number} slotIndex
 * @param {object} [itemCatalog]
 * @param {object} [energyState]
 * @returns {{ ok: boolean, inventory: object, item: object|null, reason: string|null }}
 */
export function useItem(inventory, location, slotIndex, itemCatalog = {}, energyState = null) {
  const norm = normalizeInventory(inventory);
  const targetArray = location === 'backpack' ? norm.backpack : norm.hotbar;

  if (slotIndex < 0 || slotIndex >= targetArray.length) {
    return { ok: false, inventory: norm, item: null, reason: 'Slot tidak valid' };
  }

  const slot = targetArray[slotIndex];
  if (!slot || !slot.itemId || slot.count <= 0) {
    return { ok: false, inventory: norm, item: null, reason: 'Slot kosong' };
  }

  const itemDef = itemCatalog[slot.itemId] || {
    id: slot.itemId,
    label: slot.itemId,
    energy: 15,
    consumeMinutes: 3
  };

  if (energyState && energyState.current >= 95 && itemDef.energy > 0) {
    return {
      ok: false,
      inventory: norm,
      item: itemDef,
      reason: 'Energimu masih sangat penuh (>= 95%)! Simpan untuk nanti.'
    };
  }

  const usedItemId = slot.itemId;
  slot.count -= 1;
  if (slot.count <= 0) {
    targetArray[slotIndex] = null;
  }

  const result = autoRefill(norm, usedItemId);

  emit(DOMAIN_EVENTS.INVENTORY_CHANGED, result);
  emit(DOMAIN_EVENTS.BACKPACK_CHANGED, {
    backpack: result.backpack,
    count: getBackpackCount(result)
  });

  return {
    ok: true,
    inventory: result,
    item: itemDef,
    reason: null
  };
}

/**
 * Discard (buang) an item from slot without refund.
 * @param {object} inventory
 * @param {'hotbar'|'backpack'} location
 * @param {number} slotIndex
 * @param {number} [count=1]
 * @returns {{ ok: boolean, inventory: object, discardedItem: string|null }}
 */
export function discardItem(inventory, location, slotIndex, count = 1) {
  const norm = normalizeInventory(inventory);
  const targetArray = location === 'backpack' ? norm.backpack : norm.hotbar;

  if (slotIndex < 0 || slotIndex >= targetArray.length) {
    return { ok: false, inventory: norm, discardedItem: null };
  }

  const slot = targetArray[slotIndex];
  if (!slot || !slot.itemId || slot.count <= 0) {
    return { ok: false, inventory: norm, discardedItem: null };
  }

  const discardedItem = slot.itemId;
  slot.count -= count;
  if (slot.count <= 0) {
    targetArray[slotIndex] = null;
  }

  const result = autoRefill(norm, discardedItem);

  emit(DOMAIN_EVENTS.INVENTORY_CHANGED, result);
  emit(DOMAIN_EVENTS.BACKPACK_CHANGED, {
    backpack: result.backpack,
    count: getBackpackCount(result)
  });

  return {
    ok: true,
    inventory: result,
    discardedItem
  };
}

/**
 * Move or swap an item between slots.
 * @param {object} inventory
 * @param {'hotbar'|'backpack'} fromLocation
 * @param {number} fromIndex
 * @param {'hotbar'|'backpack'} toLocation
 * @param {number} toIndex
 * @returns {{ ok: boolean, inventory: object }}
 */
export function moveItem(inventory, fromLocation, fromIndex, toLocation, toIndex) {
  const norm = normalizeInventory(inventory);
  const fromArr = fromLocation === 'backpack' ? norm.backpack : norm.hotbar;
  const toArr = toLocation === 'backpack' ? norm.backpack : norm.hotbar;

  if (fromIndex < 0 || fromIndex >= fromArr.length || toIndex < 0 || toIndex >= toArr.length) {
    return { ok: false, inventory: norm };
  }

  const temp = fromArr[fromIndex];
  fromArr[fromIndex] = toArr[toIndex];
  toArr[toIndex] = temp;

  const result = autoRefill(norm);

  emit(DOMAIN_EVENTS.INVENTORY_CHANGED, result);
  emit(DOMAIN_EVENTS.BACKPACK_CHANGED, {
    backpack: result.backpack,
    count: getBackpackCount(result)
  });

  return { ok: true, inventory: result };
}
