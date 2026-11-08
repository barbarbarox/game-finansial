/**
 * shopPanel.js — Panel interaktif lokasi & toko.
 * Menampilkan item belanja, celengan (di rumah), pengisian bensin, dll.
 * Anti-XSS: textContent only.
 */

import { getCash, addEntry, createExpenseEntry, createSavingsDepositEntry, createSavingsWithdrawEntry } from '../domain/ledger.js';

export function createShopModal(container, store, locationId, config, onClose) {
  const backdrop = document.createElement('div');
  backdrop.className = 'lj-modal-backdrop';

  const modal = document.createElement('div');
  modal.className = 'lj-panel shop-panel';
  modal.setAttribute('role', 'dialog');
  modal.setAttribute('aria-modal', 'true');

  const locInfo = config.locations[locationId] || { name: 'Lokasi' };

  // Header
  const header = document.createElement('div');
  header.className = 'panel-header';
  const title = document.createElement('h2');
  title.className = 'panel-title';
  title.textContent = locInfo.name;
  const closeBtn = document.createElement('button');
  closeBtn.type = 'button';
  closeBtn.className = 'btn-close';
  closeBtn.textContent = '✕';
  closeBtn.addEventListener('click', () => {
    backdrop.remove();
    if (onClose) onClose();
  });
  header.appendChild(title);
  header.appendChild(closeBtn);
  modal.appendChild(header);

  const rupiah = new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 });

  // Body content based on location
  const body = document.createElement('div');
  body.className = 'shop-body';

  if (locationId === 'rumah') {
    // Celengan & Istirahat (Tidur)
    const celenganSection = document.createElement('div');
    celenganSection.className = 'shop-section';
    const sTitle = document.createElement('h3');
    sTitle.textContent = 'Celengan Ayam (Tabungan)';
    celenganSection.appendChild(sTitle);

    const amountInput = document.createElement('input');
    amountInput.type = 'number';
    amountInput.min = '10000';
    amountInput.step = '10000';
    amountInput.value = '10000';
    amountInput.className = 'input-field';

    const btnGroup = document.createElement('div');
    btnGroup.className = 'btn-group';

    const depositBtn = document.createElement('button');
    depositBtn.className = 'btn btn-primary';
    depositBtn.textContent = 'Nabung (+10.000)';
    depositBtn.addEventListener('click', () => {
      const state = store.getState();
      const amt = parseInt(amountInput.value, 10) || 10000;
      if (getCash(state.ledger) < amt) {
        alert('Kas pribadi tidak mencukupi untuk menabung sejumlah ini!');
        return;
      }
      const entry = createSavingsDepositEntry(state.clock.day, state.clock.month, amt);
      const res = addEntry(state.ledger, entry);
      if (!res.error) {
        store.setState({ ledger: res.ledger });
      }
    });

    const withdrawBtn = document.createElement('button');
    withdrawBtn.className = 'btn btn-secondary';
    withdrawBtn.textContent = 'Tarik Tabungan';
    withdrawBtn.addEventListener('click', () => {
      const state = store.getState();
      const amt = parseInt(amountInput.value, 10) || 10000;
      const entry = createSavingsWithdrawEntry(state.clock.day, state.clock.month, amt);
      const res = addEntry(state.ledger, entry);
      if (res.error) {
        alert(res.error);
      } else {
        store.setState({ ledger: res.ledger });
      }
    });

    btnGroup.appendChild(depositBtn);
    btnGroup.appendChild(withdrawBtn);
    celenganSection.appendChild(amountInput);
    celenganSection.appendChild(btnGroup);
    body.appendChild(celenganSection);

    // Tidur / istirahat (lompat hari)
    const sleepSection = document.createElement('div');
    sleepSection.className = 'shop-section';
    const sleepBtn = document.createElement('button');
    sleepBtn.className = 'btn btn-tertiary';
    sleepBtn.textContent = 'Tidur (Lanjut ke Hari Berikutnya)';
    sleepBtn.addEventListener('click', () => {
      const state = store.getState();
      let nextDay = state.clock.day + 1;
      let nextMonth = state.clock.month;
      if (nextDay > config.monthDays) {
        nextDay = 1;
        nextMonth += 1;
      }
      store.setState({
        clock: { ...state.clock, day: nextDay, month: nextMonth },
        gasoline: Math.max(0, state.gasoline - config.gasolineDrainPerDay)
      });
      backdrop.remove();
      if (onClose) onClose();
    });
    sleepSection.appendChild(sleepBtn);
    body.appendChild(sleepSection);

  } else {
    // Normal Shop items
    const items = config.shopItems[locationId] || [];
    const list = document.createElement('div');
    list.className = 'shop-item-list';

    items.forEach(item => {
      const card = document.createElement('div');
      card.className = 'shop-item-card';

      const details = document.createElement('div');
      details.className = 'shop-item-details';
      const name = document.createElement('strong');
      name.className = 'shop-item-name';
      name.textContent = item.name;
      const price = document.createElement('span');
      price.className = 'shop-item-price';
      price.textContent = rupiah.format(item.price);
      details.appendChild(name);
      details.appendChild(price);

      const buyBtn = document.createElement('button');
      buyBtn.className = 'btn btn-primary';
      buyBtn.textContent = 'Beli';
      buyBtn.addEventListener('click', () => {
        const state = store.getState();
        if (getCash(state.ledger) < item.price) {
          alert('Uang kas kamu tidak cukup!');
          return;
        }

        const entry = createExpenseEntry(
          state.clock.day,
          state.clock.month,
          item.categoryId,
          item.price,
          item.name
        );
        const res = addEntry(state.ledger, entry);
        if (!res.error) {
          const updates = { ledger: res.ledger };
          if (locationId === 'spbu') {
            updates.gasoline = Math.min(100, (state.gasoline || 0) + config.gasolineFillAmount);
          }
          store.setState(updates);

          // Rule 72 §3 & Rule 70: Purchases advance time
          let duration = 15;
          if (locationId === 'kantin') {
            duration = item.id === 'makan_siang' ? 20 : 10;
          } else if (locationId === 'spbu') {
            duration = 10;
          } else if (locationId === 'kosmetik') {
            duration = 20;
          } else if (locationId === 'gamecenter') {
            duration = item.id === 'nonton' ? 120 : (item.id === 'nongkrong' ? 90 : 60);
          }
          if (window.__LJ__?.advanceTime) {
            window.__LJ__.advanceTime(duration, `beli_${item.id}`);
          }
        }
      });

      card.appendChild(details);
      card.appendChild(buyBtn);
      list.appendChild(card);
    });

    body.appendChild(list);
  }

  modal.appendChild(body);
  backdrop.appendChild(modal);
  container.appendChild(backdrop);
}

