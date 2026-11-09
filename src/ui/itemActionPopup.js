/**
 * itemActionPopup.js — Item Action Popup (Rule 80 §4).
 * Provides Gunakan, Pindahkan, Buang with confirmation.
 * Anti-XSS: textContent only, no innerHTML.
 */

import { useItem, moveItem, discardItem, normalizeInventory } from '../domain/inventory.js';
import { emit, DOMAIN_EVENTS } from '../domain/events.js';

let popupEl = null;

export function hideItemActionPopup() {
  if (popupEl) {
    popupEl.remove();
    popupEl = null;
  }
}

/**
 * Show popup anchored to target slot element.
 * @param {HTMLElement} anchorEl
 * @param {'hotbar'|'backpack'} location
 * @param {number} slotIndex
 * @param {object} slotData - { itemId, count }
 * @param {object} store
 * @param {object} itemCatalog
 */
export function showItemActionPopup(anchorEl, location, slotIndex, slotData, store, itemCatalog = {}) {
  hideItemActionPopup();
  if (!anchorEl || !slotData || !slotData.itemId) return;

  const state = store.getState();
  const itemDef = itemCatalog[slotData.itemId] || {
    id: slotData.itemId,
    label: slotData.itemId,
    price: 10000,
    energy: 15,
    consumeMinutes: 3
  };

  popupEl = document.createElement('div');
  popupEl.className = 'item-action-popup';
  popupEl.setAttribute('role', 'menu');

  // 1. Header: Icon + Name
  const header = document.createElement('div');
  header.className = 'item-action-header';

  const icon = document.createElement('img');
  icon.className = 'item-action-icon';
  icon.src = itemDef.icon || `assets/items/item_${slotData.itemId}.png`;
  icon.alt = '';

  const titleWrap = document.createElement('div');
  const title = document.createElement('div');
  title.className = 'item-action-title';
  title.textContent = `${itemDef.label || slotData.itemId} (x${slotData.count})`;

  const info = document.createElement('div');
  info.className = 'item-action-info';
  info.textContent = `+${itemDef.energy || 15} Energi · ${itemDef.consumeMinutes || 3} mnt`;

  titleWrap.appendChild(title);
  titleWrap.appendChild(info);
  header.appendChild(icon);
  header.appendChild(titleWrap);
  popupEl.appendChild(header);

  // 2. Action Buttons
  const btnsWrap = document.createElement('div');
  btnsWrap.className = 'item-action-btns';

  // --- Gunakan ---
  const useBtn = document.createElement('button');
  useBtn.type = 'button';
  useBtn.className = 'item-action-btn btn-use';
  useBtn.textContent = 'Gunakan';

  const energyState = state.energy || { current: 100, max: 100 };
  const energyCur = energyState.current ?? 100;
  if (energyCur >= 95 && (itemDef.energy || 0) > 0) {
    useBtn.disabled = true;
    useBtn.title = 'Energimu masih sangat penuh (>= 95%)!';
  }

  useBtn.addEventListener('click', () => {
    const res = useItem(state.inventory, location, slotIndex, itemCatalog, energyState);
    if (res.ok) {
      // Update energy
      const newEnergy = Math.min(energyState.max || 100, energyCur + (itemDef.energy || 15));
      const updatedEnergyState = { ...energyState, current: newEnergy };
      
      // Advance time
      const minutes = itemDef.consumeMinutes || 3;
      if (window.__LJ__?.advanceTime) {
        window.__LJ__.advanceTime(minutes, `Konsumsi ${itemDef.label}`);
      }

      store.setState({
        inventory: res.inventory,
        energy: updatedEnergyState
      });

      emit(DOMAIN_EVENTS.ENERGY_CHANGED, updatedEnergyState);
      emit(DOMAIN_EVENTS.ITEM_USED, { item: itemDef });

      // Toast feedback
      showFloatingToast(`+${itemDef.energy || 15} Energi`);
    }
    hideItemActionPopup();
  });
  btnsWrap.appendChild(useBtn);

  // --- Pindahkan ---
  const moveBtn = document.createElement('button');
  moveBtn.type = 'button';
  moveBtn.className = 'item-action-btn btn-move';
  const targetLocName = location === 'hotbar' ? 'Ransel' : 'Hotbar';
  moveBtn.textContent = `Pindahkan ke ${targetLocName}`;

  moveBtn.addEventListener('click', () => {
    const norm = normalizeInventory(state.inventory);
    const targetArr = location === 'hotbar' ? norm.backpack : norm.hotbar;
    const targetLoc = location === 'hotbar' ? 'backpack' : 'hotbar';
    let targetIdx = targetArr.findIndex(s => s === null);
    if (targetIdx === -1) targetIdx = 0; // Swap with first slot if full

    const res = moveItem(state.inventory, location, slotIndex, targetLoc, targetIdx);
    if (res.ok) {
      store.setState({ inventory: res.inventory });
    }
    hideItemActionPopup();
  });
  btnsWrap.appendChild(moveBtn);

  // --- Buang ---
  const discardBtn = document.createElement('button');
  discardBtn.type = 'button';
  discardBtn.className = 'item-action-btn btn-discard';
  discardBtn.textContent = 'Buang';

  discardBtn.addEventListener('click', () => {
    const priceText = itemDef.price ? `(Rp${itemDef.price.toLocaleString('id-ID')})` : '';
    const confirmMsg = `Membuang makanan = membuang uang ${priceText}. Yakin ingin membuang 1 ${itemDef.label || slotData.itemId}?`;
    
    // We can use confirm() or an inline confirmation
    if (window.confirm(confirmMsg)) {
      const res = discardItem(state.inventory, location, slotIndex, 1);
      if (res.ok) {
        store.setState({ inventory: res.inventory });
        showFloatingToast(`Membuang 1 ${itemDef.label}`);
      }
    }
    hideItemActionPopup();
  });
  btnsWrap.appendChild(discardBtn);

  popupEl.appendChild(btnsWrap);
  document.body.appendChild(popupEl);

  // Position popup anchored to slot
  const rect = anchorEl.getBoundingClientRect();
  const popRect = popupEl.getBoundingClientRect();
  let top = rect.top - popRect.height - 8;
  if (top < 10) top = rect.bottom + 8;
  let left = rect.left + (rect.width - popRect.width) / 2;
  if (left < 10) left = 10;
  if (left + popRect.width > window.innerWidth - 10) {
    left = window.innerWidth - popRect.width - 10;
  }

  popupEl.style.top = `${top}px`;
  popupEl.style.left = `${left}px`;

  // Auto-close on click outside
  const onDocumentClick = (e) => {
    if (popupEl && !popupEl.contains(e.target) && !anchorEl.contains(e.target)) {
      hideItemActionPopup();
      document.removeEventListener('pointerdown', onDocumentClick);
    }
  };
  setTimeout(() => {
    document.addEventListener('pointerdown', onDocumentClick);
  }, 10);
}

function showFloatingToast(text) {
  const toast = document.createElement('div');
  toast.className = 'hotbar-tooltip';
  toast.style.position = 'fixed';
  toast.style.bottom = '80px';
  toast.style.left = '50%';
  toast.style.transform = 'translateX(-50%)';
  toast.style.color = '#A5BE93';
  toast.textContent = text;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 1800);
}

