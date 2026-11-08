// tests/inventory_property_test.mjs — 500 Random Operations Property Test (Rule 80 §2)
import { createInventory, addItem, useItem, moveItem, discardItem, canAdd, normalizeInventory, getBackpackCount } from '../src/domain/inventory.js';

const ITEM_TYPES = ['nasi_kuning', 'bakso', 'es_teh', 'air_mineral', 'gorengan', 'mie_goreng', 'roti_isi'];

function countAll(inv) {
  let total = 0;
  for (const s of inv.hotbar) {
    if (s && s.count > 0) total += s.count;
  }
  for (const s of inv.backpack) {
    if (s && s.count > 0) total += s.count;
  }
  return total;
}

function verifyInvariants(inv, opName) {
  // 1. Array lengths
  if (inv.hotbar.length !== 5) {
    throw new Error(`[${opName}] Hotbar length is ${inv.hotbar.length}, expected 5`);
  }
  if (inv.backpack.length !== 20) {
    throw new Error(`[${opName}] Backpack length is ${inv.backpack.length}, expected 20`);
  }

  // 2. Stack counts
  for (let i = 0; i < 5; i++) {
    const s = inv.hotbar[i];
    if (s) {
      if (s.count < 1 || s.count > 5) throw new Error(`[${opName}] Invalid hotbar stack count: ${s.count}`);
      if (!s.itemId) throw new Error(`[${opName}] Hotbar slot has count but null itemId`);
    }
  }
  for (let i = 0; i < 20; i++) {
    const s = inv.backpack[i];
    if (s) {
      if (s.count < 1 || s.count > 5) throw new Error(`[${opName}] Invalid backpack stack count: ${s.count}`);
      if (!s.itemId) throw new Error(`[${opName}] Backpack slot has count but null itemId`);
    }
  }

  // 3. CRITICAL INVARIANT: If any slot in hotbar is empty, backpack MUST be empty
  const hasEmptyHotbarSlot = inv.hotbar.some(s => s === null);
  const backpackHasItems = inv.backpack.some(s => s !== null && s.count > 0);
  if (hasEmptyHotbarSlot && backpackHasItems) {
    throw new Error(`[${opName}] INVARIANT VIOLATED! Hotbar has empty slots but backpack contains items!\nHotbar: ${JSON.stringify(inv.hotbar)}\nBackpack: ${JSON.stringify(inv.backpack)}`);
  }
}

console.log('--- STARTING 500 INVENTORY PROPERTY INVARIANT TESTS ---');
let inv = createInventory();
let opCounts = { add: 0, use: 0, move: 0, discard: 0, rejected: 0 };

for (let step = 1; step <= 500; step++) {
  const op = Math.random();
  const prevCount = countAll(inv);

  if (op < 0.45) {
    // Add item (1 to 4 qty)
    const itemId = ITEM_TYPES[Math.floor(Math.random() * ITEM_TYPES.length)];
    const qty = 1 + Math.floor(Math.random() * 4);
    const check = canAdd(inv, itemId, qty);
    const res = addItem(inv, itemId, qty);
    if (res.ok) {
      opCounts.add++;
      inv = res.inventory;
      const newCount = countAll(inv);
      if (newCount !== prevCount + qty) {
        throw new Error(`Conservation failed on add! Expected ${prevCount + qty}, got ${newCount}`);
      }
    } else {
      opCounts.rejected++;
      if (check.canAdd) {
        throw new Error(`canAdd returned true but addItem failed: ${res.reason}`);
      }
    }
  } else if (op < 0.70) {
    // Use item
    const inBackpack = Math.random() < 0.3;
    const loc = inBackpack ? 'backpack' : 'hotbar';
    const slots = inBackpack ? inv.backpack : inv.hotbar;
    const occupied = slots.map((s, idx) => (s ? idx : -1)).filter(idx => idx !== -1);
    if (occupied.length > 0) {
      const idx = occupied[Math.floor(Math.random() * occupied.length)];
      const res = useItem(inv, loc, idx);
      if (res.ok) {
        opCounts.use++;
        inv = res.inventory;
        const newCount = countAll(inv);
        if (newCount !== prevCount - 1) {
          throw new Error(`Conservation failed on use! Expected ${prevCount - 1}, got ${newCount}`);
        }
      }
    }
  } else if (op < 0.85) {
    // Move item
    const fromLoc = Math.random() < 0.5 ? 'hotbar' : 'backpack';
    const toLoc = Math.random() < 0.5 ? 'hotbar' : 'backpack';
    const fromArr = fromLoc === 'hotbar' ? inv.hotbar : inv.backpack;
    const toArr = toLoc === 'hotbar' ? inv.hotbar : inv.backpack;
    const fromIdx = Math.floor(Math.random() * fromArr.length);
    const toIdx = Math.floor(Math.random() * toArr.length);
    const res = moveItem(inv, fromLoc, fromIdx, toLoc, toIdx);
    if (res.ok) {
      opCounts.move++;
      inv = res.inventory;
      const newCount = countAll(inv);
      if (newCount !== prevCount) {
        throw new Error(`Conservation failed on move! Expected ${prevCount}, got ${newCount}`);
      }
    }
  } else {
    // Discard item
    const inBackpack = Math.random() < 0.3;
    const loc = inBackpack ? 'backpack' : 'hotbar';
    const slots = inBackpack ? inv.backpack : inv.hotbar;
    const occupied = slots.map((s, idx) => (s ? idx : -1)).filter(idx => idx !== -1);
    if (occupied.length > 0) {
      const idx = occupied[Math.floor(Math.random() * occupied.length)];
      const res = discardItem(inv, loc, idx, 1);
      if (res.ok) {
        opCounts.discard++;
        inv = res.inventory;
        const newCount = countAll(inv);
        if (newCount !== prevCount - 1) {
          throw new Error(`Conservation failed on discard! Expected ${prevCount - 1}, got ${newCount}`);
        }
      }
    }
  }

  verifyInvariants(inv, `Step ${step}`);
}

console.log(`✅ 500 OPERATIONS PASSED!
Summary:
 - Adds: ${opCounts.add}
 - Uses: ${opCounts.use}
 - Moves: ${opCounts.move}
 - Discards: ${opCounts.discard}
 - Full/Rejected Adds: ${opCounts.rejected}
 - Total Invariant Checks: 500 (100% PASS)`);

