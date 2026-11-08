/**
 * hotbar.js — Bottom-center 5-slot item hotbar (Rule 74 §3).
 * Follows design in docs/reference/hotbar-reference.png and preserves user UI.
 */

export function createHotbar(container, store, onUseItem) {
  const hotbarEl = document.createElement('div');
  hotbarEl.id = 'hud-hotbar';
  hotbarEl.className = 'hud-hotbar-container';

  // Tooltip element
  const tooltipEl = document.createElement('div');
  tooltipEl.className = 'hotbar-tooltip';
  tooltipEl.style.display = 'none';
  document.body.appendChild(tooltipEl);

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

    // Click handler
    slot.addEventListener('click', () => {
      if (onUseItem) onUseItem(i);
    });

    // Tooltip handlers
    slot.addEventListener('mouseenter', (e) => showTooltip(e, i));
    slot.addEventListener('focus', (e) => showTooltip(e, i));
    slot.addEventListener('mouseleave', hideTooltip);
    slot.addEventListener('blur', hideTooltip);

    hotbarEl.appendChild(slot);
    slots.push({ slot, icon, badge, keyNum });
  }

  container.appendChild(hotbarEl);

  // Global keydown listener for 1-5 hotkeys
  function onKeyDown(e) {
    // Ignore if typing in an input/textarea or if dialog modal is open
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

  let currentCatalog = {};
  let currentInventory = [];

  function showTooltip(e, slotIndex) {
    const itemData = currentInventory[slotIndex];
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
    const inv = state.inventory || [];
    currentInventory = inv;

    for (let i = 0; i < 5; i++) {
      const slotData = inv[i];
      const { slot, icon, badge } = slots[i];

      if (slotData && slotData.itemId && slotData.count > 0) {
        const itemDef = itemCatalog[slotData.itemId] || {};
        const assetId = itemDef.iconAsset || `item_${slotData.itemId}`;
        icon.src = `assets/items/${assetId}.png`;
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
  }

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

