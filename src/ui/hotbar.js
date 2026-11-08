/**
 * hotbar.js — Bottom-center 5-slot item hotbar + Backpack Button (Rule 80).
 * Anti-XSS: textContent only, no innerHTML.
 */

import { normalizeInventory, getBackpackCount } from '../domain/inventory.js';
import { showItemActionPopup } from './itemActionPopup.js';
import { openBackpack, initBackpackPanel } from './backpackPanel.js';
import { subscribe, DOMAIN_EVENTS } from '../domain/events.js';

export function createHotbar(container, store, onUseItem) {
  const hotbarEl = document.createElement('div');
  hotbarEl.id = 'hud-hotbar';
  hotbarEl.className = 'hud-hotbar-container';

  // Tooltip element
  const tooltipEl = document.createElement('div');
  tooltipEl.className = 'hotbar-tooltip';
  tooltipEl.style.display = 'none';
  document.body.appendChild(tooltipEl);

  let currentCatalog = {};
  let currentInventory = normalizeInventory(store?.getState?.()?.inventory);

  // 1. Five Hotbar Slots
  const slots = [];
  for (let i = 0; i < 5; i++) {
    const slot = document.createElement('button');
    slot.type = 'button';
    slot.className = 'hotbar-slot';
    slot.dataset.slotIndex = i;
    slot.setAttribute('aria-label', `Slot ${i + 1} Kosong`);

    // Key number indicator (1-5)
    const keyNum = document.createElement('span');
    keyNum.className = 'hotbar-slot-key';
    keyNum.textContent = String(i + 1);
    slot.appendChild(keyNum);

    // Item icon image
    const icon = document.createElement('img');
    icon.className = 'hotbar-slot-icon';
    icon.style.display = 'none';
    icon.alt = '';
    slot.appendChild(icon);

    // Quantity badge
    const badge = document.createElement('span');
    badge.className = 'hotbar-slot-badge';
    badge.style.display = 'none';
    badge.textContent = '1';
    slot.appendChild(badge);

    // Click handler -> Item action popup (Rule 80 §4)
    slot.addEventListener('click', () => {
      const slotData = currentInventory.hotbar[i];
      if (slotData && slotData.itemId) {
        showItemActionPopup(slot, 'hotbar', i, slotData, store, currentCatalog);
      }
    });

    // Tooltip handlers
    slot.addEventListener('mouseenter', (e) => showTooltip(e, i));
    slot.addEventListener('focus', (e) => showTooltip(e, i));
    slot.addEventListener('mouseleave', hideTooltip);
    slot.addEventListener('blur', hideTooltip);

    hotbarEl.appendChild(slot);
    slots.push({ slot, icon, badge, keyNum });
  }

  // 2. Backpack Button (Rule 80 §3)
  const backpackBtn = document.createElement('button');
  backpackBtn.type = 'button';
  backpackBtn.className = 'hotbar-backpack-btn';
  backpackBtn.id = 'hud-backpack-btn';
  backpackBtn.setAttribute('aria-label', 'Buka Ransel [B]');
  backpackBtn.title = 'Ransel Barang [B]';

  const bpKey = document.createElement('span');
  bpKey.className = 'hotbar-slot-key';
  bpKey.textContent = 'B';
  backpackBtn.appendChild(bpKey);

  const bpIcon = document.createElement('img');
  bpIcon.className = 'hotbar-slot-icon';
  bpIcon.src = 'assets/icons/icon_tas.png';
  bpIcon.alt = 'Ransel';
  backpackBtn.appendChild(bpIcon);

  const bpBadge = document.createElement('span');
  bpBadge.className = 'backpack-count-badge';
  bpBadge.id = 'hud-backpack-badge';
  bpBadge.style.display = 'none';
  bpBadge.textContent = '0';
  backpackBtn.appendChild(bpBadge);

  backpackBtn.addEventListener('click', () => {
    openBackpack();
  });

  hotbarEl.appendChild(backpackBtn);
  container.appendChild(hotbarEl);

  // Initialize Backpack modal panel
  if (store) {
    initBackpackPanel(store, currentCatalog);
  }

  // Global keydown listener for 1-5 hotkeys (Fast use) and B (Backpack)
  function onKeyDown(e) {
    const activeTag = document.activeElement?.tagName?.toLowerCase();
    if (activeTag === 'input' || activeTag === 'textarea') return;
    if (document.querySelector('.dialogue-panel:not([style*="display: none"])')) return;

    if (['1', '2', '3', '4', '5'].includes(e.key)) {
      const idx = parseInt(e.key, 10) - 1;
      if (idx >= 0 && idx < 5 && onUseItem) {
        onUseItem(idx);
      }
    }
  }

  window.addEventListener('keydown', onKeyDown);

  function showTooltip(e, slotIndex) {
    const itemData = currentInventory.hotbar[slotIndex];
    if (!itemData || !itemData.itemId || itemData.count <= 0) {
      hideTooltip();
      return;
    }

    const itemDef = currentCatalog[itemData.itemId] || {
      label: itemData.itemId,
      energy: 15,
      consumeMinutes: 3
    };

    tooltipEl.textContent = `${itemDef.label} (+${itemDef.energy} Energi, ${itemDef.consumeMinutes} mnt)`;
    tooltipEl.style.display = 'block';

    const rect = e.target.getBoundingClientRect();
    tooltipEl.style.left = `${rect.left + rect.width / 2}px`;
    tooltipEl.style.top = `${rect.top - 32}px`;
  }

  function hideTooltip() {
    tooltipEl.style.display = 'none';
  }

  function update(state, itemCatalog = {}) {
    currentCatalog = itemCatalog;
    const inv = normalizeInventory(state.inventory);
    currentInventory = inv;

    for (let i = 0; i < 5; i++) {
      const slotData = inv.hotbar[i];
      const { slot, icon, badge } = slots[i];

      if (slotData && slotData.itemId && slotData.count > 0) {
        const itemDef = itemCatalog[slotData.itemId] || {};
        const assetId = itemDef.iconAsset || `item_${slotData.itemId}`;
        icon.src = itemDef.icon || `assets/items/${assetId}.png`;
        icon.alt = itemDef.label || slotData.itemId;
        icon.style.display = 'block';

        badge.textContent = String(slotData.count);
        badge.style.display = slotData.count > 1 ? 'block' : 'none';
        slot.setAttribute('aria-label', `Slot ${i + 1}: ${itemDef.label || slotData.itemId} (${slotData.count})`);
        slot.classList.add('has-item');
      } else {
        icon.style.display = 'none';
        badge.style.display = 'none';
        slot.setAttribute('aria-label', `Slot ${i + 1} Kosong`);
        slot.classList.remove('has-item');
      }
    }

    // Update backpack badge count
    const bCount = getBackpackCount(inv);
    if (bCount > 0) {
      bpBadge.textContent = String(bCount);
      bpBadge.style.display = 'block';
    } else {
      bpBadge.style.display = 'none';
    }
  }

  // Subscribe to domain inventory events
  subscribe(DOMAIN_EVENTS.INVENTORY_CHANGED, (newInv) => {
    if (store) {
      update(store.getState(), currentCatalog);
    }
  });

  subscribe(DOMAIN_EVENTS.BACKPACK_CHANGED, ({ count }) => {
    if (count > 0) {
      bpBadge.textContent = String(count);
      bpBadge.style.display = 'block';
    } else {
      bpBadge.style.display = 'none';
    }
  });

  return {
    element: hotbarEl,
    update,
    setVisible(visible) {
      hotbarEl.style.display = visible ? 'flex' : 'none';
    },
    destroy() {
      window.removeEventListener('keydown', onKeyDown);
      hotbarEl.remove();
      tooltipEl.remove();
    }
  };
}
