/**
 * backpackPanel.js — 20-Slot Backpack Modal Panel (Rule 80 §3).
 * Anti-XSS: textContent only, no innerHTML.
 */

import { subscribe, emit, DOMAIN_EVENTS } from '../domain/events.js';
import { normalizeInventory, useItem, moveItem, discardItem, getBackpackCount } from '../domain/inventory.js';
import { showItemActionPopup, hideItemActionPopup } from './itemActionPopup.js';

let modalOverlay = null;
let currentStore = null;
let currentCatalog = {};
let isOpen = false;

export function initBackpackPanel(store, itemCatalog = {}) {
  currentStore = store;
  currentCatalog = itemCatalog;

  subscribe(DOMAIN_EVENTS.INVENTORY_CHANGED, (inv) => {
    if (isOpen) renderGrid();
  });

  subscribe(DOMAIN_EVENTS.BACKPACK_CHANGED, () => {
    if (isOpen) renderGrid();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isOpen) {
      closeBackpack();
    } else if ((e.key === 'b' || e.key === 'B') && !isOpen) {
      const activeTag = document.activeElement?.tagName?.toLowerCase();
      if (activeTag !== 'input' && activeTag !== 'textarea') {
        openBackpack();
      }
    }
  });
}

export function openBackpack() {
  if (isOpen) return;
  isOpen = true;

  if (!modalOverlay) {
    createDOM();
  }
  modalOverlay.style.display = 'flex';
  renderGrid();
}

export function closeBackpack() {
  if (!isOpen) return;
  isOpen = false;
  hideItemActionPopup();
  if (modalOverlay) {
    modalOverlay.style.display = 'none';
  }
}

export function toggleBackpack() {
  if (isOpen) closeBackpack();
  else openBackpack();
}

function createDOM() {
  modalOverlay = document.createElement('div');
  modalOverlay.className = 'backpack-modal-overlay';
  modalOverlay.style.display = 'none';

  const panel = document.createElement('div');
  panel.className = 'backpack-modal-panel';
  panel.setAttribute('role', 'dialog');
  panel.setAttribute('aria-modal', 'true');
  panel.setAttribute('aria-label', 'Ransel Pemain');

  // Header
  const header = document.createElement('div');
  header.className = 'backpack-header';

  const title = document.createElement('div');
  title.className = 'backpack-title';
  const icon = document.createElement('img');
  icon.src = 'assets/icons/icon_tas.png';
  icon.alt = '';
  icon.style.width = '20px';
  icon.style.height = '20px';
  const titleText = document.createElement('span');
  titleText.textContent = 'Ransel Barang';
  title.appendChild(icon);
  title.appendChild(titleText);

  const badge = document.createElement('div');
  badge.className = 'backpack-capacity-badge';
  badge.id = 'backpack-capacity-badge';
  badge.textContent = 'Hotbar 0/5 · Ransel 0/20';

  header.appendChild(title);
  header.appendChild(badge);
  panel.appendChild(header);

  // 5x4 Grid
  const grid = document.createElement('div');
  grid.className = 'backpack-grid';
  grid.id = 'backpack-grid';
  panel.appendChild(grid);

  // Close Button
  const closeBtn = document.createElement('button');
  closeBtn.type = 'button';
  closeBtn.className = 'backpack-close-btn';
  closeBtn.textContent = 'Tutup [Esc]';
  closeBtn.addEventListener('click', closeBackpack);
  panel.appendChild(closeBtn);

  modalOverlay.appendChild(panel);
  modalOverlay.addEventListener('click', (e) => {
    if (e.target === modalOverlay) closeBackpack();
  });

  document.body.appendChild(modalOverlay);
}

function renderGrid() {
  if (!modalOverlay || !currentStore) return;
  const state = currentStore.getState();
  const inv = normalizeInventory(state.inventory);
  const grid = document.getElementById('backpack-grid');
  const badge = document.getElementById('backpack-capacity-badge');
  if (!grid) return;

  grid.innerHTML = '';

  const hotbarCount = inv.hotbar.filter(s => s && s.itemId).length;
  const backpackCount = inv.backpack.filter(s => s && s.itemId).length;
  if (badge) {
    badge.textContent = `Hotbar ${hotbarCount}/5 · Ransel ${backpackCount}/20`;
  }

  inv.backpack.forEach((slot, idx) => {
    const slotEl = document.createElement('button');
    slotEl.type = 'button';
    slotEl.className = `backpack-slot ${slot && slot.itemId ? 'has-item' : 'empty'}`;
    slotEl.dataset.slotIndex = idx;
    slotEl.setAttribute('aria-label', slot && slot.itemId ? `Slot Ransel ${idx + 1}: ${slot.itemId}` : `Slot Ransel ${idx + 1} Kosong`);

    if (slot && slot.itemId) {
      const img = document.createElement('img');
      img.className = 'hotbar-slot-icon';
      img.src = `assets/items/item_${slot.itemId}.png`;
      img.alt = slot.itemId;
      slotEl.appendChild(img);

      if (slot.count > 1) {
        const countSpan = document.createElement('span');
        countSpan.className = 'hotbar-slot-badge';
        countSpan.textContent = String(slot.count);
        slotEl.appendChild(countSpan);
      }

      slotEl.addEventListener('click', (e) => {
        showItemActionPopup(slotEl, 'backpack', idx, slot, currentStore, currentCatalog);
      });
    }

    grid.appendChild(slotEl);
  });
}

