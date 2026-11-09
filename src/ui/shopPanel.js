/**
 * shopPanel.js — Unified Shop & Vendor System for Life Journey (Rules 79 & 86).
 * Supports Kantin, Minimarket, Kafe Game Center, Toko Kosmetik, and SPBU.
 * Featuring:
 * - Vendor presence (192x256 scaled portraits, nameplates, dynamic speech bubbles)
 * - Multiple exit paths (Top-right X, Footer 'Selesai' button, Outside backdrop click, Esc key)
 * - Anti-XSS (textContent only, no innerHTML)
 */

import { getCash, addEntry, createExpenseEntry } from '../domain/ledger.js';
import { addItem, canAdd, normalizeInventory, getBackpackCount } from '../domain/inventory.js';
import { refuelPercent, refuelAmount, calculateFillCost } from '../domain/vehicle.js';
import { emit, DOMAIN_EVENTS } from '../domain/events.js';

let activeBackdrop = null;
let activeKeydownHandler = null;
let shopsCache = null;
let itemsCache = null;

const VENDOR_PROFILES = {
  kantin_sekolah: {
    name: 'Bu Sri',
    role: 'Penjual Kantin',
    portrait: 'assets/portraits/portrait_penjual_kantin.png',
    greeting: 'Halo! Mau jajan apa hari ini?',
    bought: 'Terima kasih sudah beli, selamat menikmati ya!',
    noCash: 'Waduh, uang saku kamu belum cukup nih.',
    bagFull: 'Wah, tas atau kantong kamu sudah penuh!'
  },
  minimarket: {
    name: 'Mbak Maya',
    role: 'Kasir Minimarket',
    portrait: 'assets/portraits/portrait_kasir_minimarket.png',
    greeting: 'Selamat datang di Minimarket! Ada yang bisa dibantu?',
    bought: 'Terima kasih sudah berbelanja di Minimarket!',
    noCash: 'Maaf, uangnya belum mencukupi untuk item ini.',
    bagFull: 'Ransel dan hotbar kamu sudah penuh nih!'
  },
  toko_kosmetik: {
    name: 'Kak Cindy',
    role: 'Penjaga Toko',
    portrait: 'assets/portraits/portrait_penjaga_kosmetik.png',
    greeting: 'Hai! Selamat datang di Toko Kosmetik. Silakan dipilih!',
    bought: 'Pilihan yang bagus! Semoga harimu menyenangkan!',
    noCash: 'Maaf ya, saldo kamu belum cukup untuk barang ini.',
    bagFull: 'Ranselmu sudah penuh, simpan dulu barangmu ya!'
  },
  game_center_kafe: {
    name: 'Kak Riko',
    role: 'Operator Game Center',
    portrait: 'assets/portraits/portrait_penjaga_game.png',
    greeting: 'Yo! Mau beli camilan atau minuman?',
    bought: 'Sip! Nikmati jajananmu ya!',
    noCash: 'Uangnya kurang nih bro, kumpulin lagi ya!',
    bagFull: 'Kantongmu sudah penuh bro!'
  },
  spbu: {
    name: 'Mas Doni',
    role: 'Petugas SPBU',
    portrait: 'assets/portraits/portrait_petugas_spbu.png',
    greeting: 'Mulai dari nol ya! Mau isi Pertalite berapa?',
    bought: 'Bensin sudah terisi. Hati-hati di jalan ya!',
    noCash: 'Uang kasnya belum cukup untuk nominal ini Mas/Mbak.',
    tankFull: 'Tangki motor sudah penuh 100%!'
  }
};

function getVendorProfile(shopId) {
  let id = shopId || '';
  if (id === 'kantin') id = 'kantin_sekolah';
  if (id === 'gamecenter' || id === 'game_center') id = 'game_center_kafe';
  if (id === 'kosmetik') id = 'toko_kosmetik';

  if (VENDOR_PROFILES[id]) return VENDOR_PROFILES[id];
  for (const key of Object.keys(VENDOR_PROFILES)) {
    if (id.includes(key) || key.includes(id)) return VENDOR_PROFILES[key];
  }
  return {
    name: 'Kasir Toko',
    role: 'Penjaga',
    portrait: 'assets/portraits/portrait_kasir_minimarket.png',
    greeting: 'Selamat datang! Silakan pilih belanjaan Anda.',
    bought: 'Terima kasih atas pembeliannya!',
    noCash: 'Saldo kas Anda tidak mencukupi.',
    bagFull: 'Kapasitas inventaris Anda sudah penuh!'
  };
}

async function loadData() {
  if (!shopsCache) {
    try {
      const res = await fetch('data/shops.phase1.json');
      shopsCache = await res.json();
    } catch (e) {
      console.warn('[ShopPanel] Failed to load shops.phase1.json:', e);
      shopsCache = { shops: [] };
    }
  }
  if (!itemsCache) {
    try {
      const res = await fetch('data/items.phase1.json');
      itemsCache = await res.json();
    } catch (e) {
      console.warn('[ShopPanel] Failed to load items.phase1.json:', e);
      itemsCache = { items: [] };
    }
  }
  return { shops: shopsCache.shops || [], items: itemsCache.items || [] };
}

export function closeShopModal() {
  if (activeBackdrop) {
    activeBackdrop.remove();
    activeBackdrop = null;
  }
  if (activeKeydownHandler) {
    document.removeEventListener('keydown', activeKeydownHandler);
    activeKeydownHandler = null;
  }
}

/**
 * Open shop panel for a specific shopId or interactable.
 * @param {HTMLElement} container
 * @param {object} store
 * @param {string} shopId - e.g. 'kantin_sekolah', 'minimarket', 'spbu', 'game_center_kafe', 'toko_kosmetik'
 * @param {object} [options] - { categoryFilter, onClose }
 */
export async function createShopModal(container, store, shopId, options = {}) {
  closeShopModal();

  const { shops, items } = await loadData();
  const state = store.getState();

  // Map legacy / alternative IDs
  let targetShopId = shopId;
  if (shopId === 'kantin') targetShopId = 'kantin_sekolah';
  if (shopId === 'gamecenter' || shopId === 'game_center') targetShopId = 'game_center_kafe';
  if (shopId === 'kosmetik') targetShopId = 'toko_kosmetik';

  let shopDef = shops.find(s => s.id === targetShopId) || shops.find(s => s.sellAt === targetShopId);
  if (!shopDef) {
    shopDef = {
      id: targetShopId,
      label: targetShopId.toUpperCase(),
      modes: ['bungkus'],
      sellAt: targetShopId
    };
  }

  const vendor = getVendorProfile(targetShopId);
  const rupiah = new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 });

  // 1. Modal backdrop & panel
  activeBackdrop = document.createElement('div');
  activeBackdrop.className = 'lj-modal-backdrop';

  // Outside click closes modal (Rule 86 §2)
  activeBackdrop.addEventListener('click', (e) => {
    if (e.target === activeBackdrop) {
      closeShopModal();
      if (options.onClose) options.onClose();
    }
  });

  const modal = document.createElement('div');
  modal.className = 'lj-panel shop-modal-panel';
  modal.setAttribute('role', 'dialog');
  modal.setAttribute('aria-modal', 'true');
  modal.setAttribute('aria-label', shopDef.label);

  // 2. Header: Title + Close [X] Button (Rule 86 §2)
  const header = document.createElement('div');
  header.className = 'panel-header';

  const title = document.createElement('h2');
  title.className = 'panel-title';
  title.textContent = shopDef.label;

  const closeBtn = document.createElement('button');
  closeBtn.type = 'button';
  closeBtn.className = 'btn-close';
  closeBtn.textContent = '✕';
  closeBtn.setAttribute('aria-label', 'Tutup Katalog');
  closeBtn.addEventListener('click', () => {
    closeShopModal();
    if (options.onClose) options.onClose();
  });

  header.appendChild(title);
  header.appendChild(closeBtn);
  modal.appendChild(header);

  // 3. Body layout: 2 columns (Vendor Left + Content Right) (Rule 86 §3)
  const bodyLayout = document.createElement('div');
  bodyLayout.className = 'shop-body-layout';

  // --- Vendor Column (Left) ---
  const vendorCol = document.createElement('div');
  vendorCol.className = 'shop-vendor-col';

  const vendorNameplate = document.createElement('div');
  vendorNameplate.className = 'shop-vendor-nameplate';

  const vendorName = document.createElement('span');
  vendorName.className = 'shop-vendor-name';
  vendorName.textContent = vendor.name;

  const vendorRole = document.createElement('span');
  vendorRole.className = 'shop-vendor-role';
  vendorRole.textContent = vendor.role;

  vendorNameplate.appendChild(vendorName);
  vendorNameplate.appendChild(vendorRole);
  vendorCol.appendChild(vendorNameplate);

  const portraitWrap = document.createElement('div');
  portraitWrap.className = 'shop-vendor-portrait-wrap';

  const portraitImg = document.createElement('img');
  portraitImg.className = 'shop-vendor-portrait-img';
  portraitImg.src = vendor.portrait;
  portraitImg.alt = vendor.name;

  const portraitPlaceholder = document.createElement('div');
  portraitPlaceholder.className = 'shop-vendor-placeholder hidden';
  portraitPlaceholder.textContent = vendor.name;

  portraitImg.onerror = () => {
    console.warn(`[ShopPanel] Vendor portrait not found: ${vendor.portrait}`);
    portraitImg.classList.add('hidden');
    portraitPlaceholder.classList.remove('hidden');
  };

  portraitWrap.appendChild(portraitImg);
  portraitWrap.appendChild(portraitPlaceholder);
  vendorCol.appendChild(portraitWrap);

  const speechBubble = document.createElement('div');
  speechBubble.className = 'shop-vendor-speech';

  const speechText = document.createElement('p');
  speechText.className = 'shop-vendor-speech-text';
  speechText.textContent = vendor.greeting;
  speechBubble.appendChild(speechText);
  vendorCol.appendChild(speechBubble);

  function setVendorSpeech(msg) {
    if (speechText) {
      speechText.textContent = msg;
    }
  }

  bodyLayout.appendChild(vendorCol);

  // --- Content Column (Right) ---
  const contentCol = document.createElement('div');
  contentCol.className = 'shop-content-col';

  // Status Bar: Kas + Kapasitas Ransel
  const statusBar = document.createElement('div');
  statusBar.className = 'shop-status-bar';

  const cashBadge = document.createElement('span');
  cashBadge.className = 'shop-cash-badge';
  cashBadge.id = 'shop-cash-badge';
  cashBadge.textContent = rupiah.format(getCash(state.ledger));

  const invNorm = normalizeInventory(state.inventory);
  const capBadge = document.createElement('span');
  capBadge.className = 'backpack-capacity-badge';
  capBadge.id = 'shop-cap-badge';
  capBadge.textContent = `Hotbar ${invNorm.hotbar.filter(s => s).length}/5 · Ransel ${invNorm.backpack.filter(s => s).length}/20`;

  statusBar.appendChild(cashBadge);
  statusBar.appendChild(capBadge);
  contentCol.appendChild(statusBar);

  function updateStatusBadges() {
    const curState = store.getState();
    const curInv = normalizeInventory(curState.inventory);
    cashBadge.textContent = rupiah.format(getCash(curState.ledger));
    capBadge.textContent = `Hotbar ${curInv.hotbar.filter(s => s).length}/5 · Ransel ${curInv.backpack.filter(s => s).length}/20`;
  }

  // 4. Special Mode: SPBU Fuel Refuel
  if (shopDef.kind === 'fuel' || targetShopId === 'spbu') {
    renderFuelPanel(contentCol, store, shopDef, rupiah, setVendorSpeech, vendor, updateStatusBadges);
    bodyLayout.appendChild(contentCol);
    modal.appendChild(bodyLayout);

    // Footer with "Selesai" button (Rule 86 §2)
    const footer = document.createElement('div');
    footer.className = 'panel-footer shop-modal-footer';

    const doneBtn = document.createElement('button');
    doneBtn.type = 'button';
    doneBtn.className = 'shop-btn-done';
    doneBtn.textContent = 'Selesai';
    doneBtn.addEventListener('click', () => {
      closeShopModal();
      if (options.onClose) options.onClose();
    });
    footer.appendChild(doneBtn);
    modal.appendChild(footer);

    activeBackdrop.appendChild(modal);
    container.appendChild(activeBackdrop);

    // Esc closes modal
    activeKeydownHandler = (e) => {
      if (e.key === 'Escape') {
        closeShopModal();
        if (options.onClose) options.onClose();
      }
    };
    document.addEventListener('keydown', activeKeydownHandler);
    return;
  }

  // 5. Category Tabs
  const tabsContainer = document.createElement('div');
  tabsContainer.className = 'shop-tabs';

  const categories = ['Semua', 'Makanan', 'Minuman', 'Snack'];
  if (shopDef.goods && shopDef.goods.length > 0) {
    categories.push('Lainnya');
  }

  let activeTab = options.categoryFilter || 'Semua';
  if (activeTab === 'all') activeTab = 'Semua';

  const tabBtns = [];
  categories.forEach(cat => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = `shop-tab-btn ${cat.toLowerCase() === activeTab.toLowerCase() ? 'active' : ''}`;
    btn.textContent = cat;
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeTab = cat;
      renderItems();
    });
    tabBtns.push(btn);
    tabsContainer.appendChild(btn);
  });
  contentCol.appendChild(tabsContainer);

  // 6. Items list container
  const itemsContainer = document.createElement('div');
  itemsContainer.className = 'shop-items-container';
  contentCol.appendChild(itemsContainer);

  // Filter items matching shop
  const shopSellAt = shopDef.sellAt || targetShopId;
  const availableItems = items.filter(it => it.sellAt && it.sellAt.includes(shopSellAt));
  const availableGoods = shopDef.goods || [];

  function renderItems() {
    itemsContainer.innerHTML = '';
    const curState = store.getState();
    const curCash = getCash(curState.ledger);
    const curInv = normalizeInventory(curState.inventory);

    // Consumable food & drinks
    if (activeTab !== 'Lainnya') {
      const filtered = availableItems.filter(it => {
        if (activeTab === 'Semua') return true;
        return (it.type || '').toLowerCase() === activeTab.toLowerCase();
      });

      filtered.forEach(item => {
        const card = document.createElement('div');
        card.className = 'shop-item-card';

        const left = document.createElement('div');
        left.className = 'shop-item-left';

        const icon = document.createElement('img');
        icon.className = 'shop-item-icon';
        icon.src = item.icon || `assets/items/item_${item.id}.png`;
        icon.alt = item.label;

        const info = document.createElement('div');
        info.className = 'shop-item-info';

        const name = document.createElement('span');
        name.className = 'shop-item-name';
        name.textContent = item.label;

        const desc = document.createElement('span');
        desc.className = 'shop-item-desc';
        desc.textContent = `+${item.energy || 15} Energi · ${item.consumeMinutes || 3} mnt`;

        const price = document.createElement('span');
        price.className = 'shop-item-price';
        price.textContent = rupiah.format(item.price);

        info.appendChild(name);
        info.appendChild(desc);
        info.appendChild(price);
        left.appendChild(icon);
        left.appendChild(info);
        card.appendChild(left);

        // Right controls: Qty stepper + Mode select + Buy button
        const controls = document.createElement('div');
        controls.className = 'shop-item-controls';

        let qty = 1;
        const qtyBox = document.createElement('div');
        qtyBox.className = 'shop-qty-box';

        const minusBtn = document.createElement('button');
        minusBtn.type = 'button';
        minusBtn.className = 'shop-qty-btn';
        minusBtn.textContent = '-';

        const qtyText = document.createElement('span');
        qtyText.className = 'shop-qty-text';
        qtyText.textContent = '1';

        const plusBtn = document.createElement('button');
        plusBtn.type = 'button';
        plusBtn.className = 'shop-qty-btn';
        plusBtn.textContent = '+';

        minusBtn.addEventListener('click', () => {
          if (qty > 1) {
            qty--;
            qtyText.textContent = String(qty);
            updateBuyButton();
          }
        });
        plusBtn.addEventListener('click', () => {
          if (qty < 5) {
            qty++;
            qtyText.textContent = String(qty);
            updateBuyButton();
          }
        });

        qtyBox.appendChild(minusBtn);
        qtyBox.appendChild(qtyText);
        qtyBox.appendChild(plusBtn);
        controls.appendChild(qtyBox);

        // Mode select: Makan di tempat vs Bungkus
        let mode = 'bungkus';
        if (shopDef.modes && shopDef.modes.includes('makan_di_tempat')) {
          const modeSelect = document.createElement('select');
          modeSelect.className = 'shop-mode-select';
          
          const optBungkus = document.createElement('option');
          optBungkus.value = 'bungkus';
          optBungkus.textContent = 'Bungkus (Tas)';
          
          const optMakan = document.createElement('option');
          optMakan.value = 'makan_di_tempat';
          optMakan.textContent = 'Makan di tempat';

          modeSelect.appendChild(optBungkus);
          modeSelect.appendChild(optMakan);
          modeSelect.addEventListener('change', () => {
            mode = modeSelect.value;
            updateBuyButton();
          });
          controls.appendChild(modeSelect);
        }

        // Buy button
        const buyBtn = document.createElement('button');
        buyBtn.type = 'button';
        buyBtn.className = 'shop-buy-btn';
        buyBtn.textContent = 'Beli';

        function updateBuyButton() {
          const totalCost = item.price * qty;
          const freshCash = getCash(store.getState().ledger);
          const freshInv = store.getState().inventory;

          if (freshCash < totalCost) {
            buyBtn.disabled = true;
            buyBtn.title = 'Uang kas tidak mencukupi';
            return;
          }

          if (mode === 'bungkus') {
            const check = canAdd(freshInv, item.id, qty);
            if (!check.canAdd) {
              buyBtn.disabled = true;
              buyBtn.title = check.reason || 'Tas penuh';
              return;
            }
          }

          buyBtn.disabled = false;
          buyBtn.title = '';
        }

        buyBtn.addEventListener('click', () => {
          const totalCost = item.price * qty;
          const freshState = store.getState();
          const freshCash = getCash(freshState.ledger);

          if (freshCash < totalCost) {
            setVendorSpeech(vendor.noCash);
            alert('Uang kas tidak mencukupi!');
            return;
          }

          if (mode === 'bungkus') {
            const addCheck = canAdd(freshState.inventory, item.id, qty);
            if (!addCheck.canAdd) {
              setVendorSpeech(vendor.bagFull);
              alert(addCheck.reason || 'Tas penuh! Kapasitas hotbar dan ransel sudah mencapai batas maksimal.');
              return;
            }

            // ATOMIC TRANSACTION: Add expense to ledger and add item to inventory
            const clock = freshState.clock || {};
            const expEntry = createExpenseEntry(
              clock.day || 1,
              clock.month || 1,
              'jajan',
              totalCost,
              `Beli ${qty}x ${item.label}`,
              clock.timeOfDay || 480
            );
            const ledgerRes = addEntry(freshState.ledger, expEntry);
            if (ledgerRes.error) {
              alert(ledgerRes.error);
              return;
            }

            const invRes = addItem(freshState.inventory, item.id, qty);
            if (!invRes.success) {
              alert(invRes.reason || 'Gagal menambahkan item ke tas!');
              return;
            }

            store.setState({
              ledger: ledgerRes.ledger,
              inventory: invRes.inventory
            });

            emit(DOMAIN_EVENTS.ITEM_ACQUIRED, { itemId: item.id, count: qty });
            emit(DOMAIN_EVENTS.CASH_CHANGED, getCash(ledgerRes.ledger));
            emit(DOMAIN_EVENTS.INVENTORY_CHANGED, invRes.inventory);

            setVendorSpeech(vendor.bought);
            updateStatusBadges();
            renderItems();
          } else {
            // Makan di tempat: consume immediately
            const clock = freshState.clock || {};
            const expEntry = createExpenseEntry(
              clock.day || 1,
              clock.month || 1,
              'jajan',
              totalCost,
              `Makan di tempat: ${qty}x ${item.label}`,
              clock.timeOfDay || 480
            );
            const ledgerRes = addEntry(freshState.ledger, expEntry);
            if (ledgerRes.error) {
              alert(ledgerRes.error);
              return;
            }

            const curEnergy = freshState.energy?.current || 100;
            const energyAdd = (item.energy || 15) * qty;
            const newEnergy = Math.min(100, curEnergy + energyAdd);

            if (window.__LJ__?.advanceTime) {
              window.__LJ__.advanceTime((item.consumeMinutes || 3) * qty, `Makan ${item.label}`);
            }

            store.setState({
              ledger: ledgerRes.ledger,
              energy: {
                ...(freshState.energy || { max: 100, exhaustionCount: 0 }),
                current: newEnergy
              }
            });

            emit(DOMAIN_EVENTS.ENERGY_CHANGED, newEnergy);
            emit(DOMAIN_EVENTS.CASH_CHANGED, getCash(ledgerRes.ledger));

            setVendorSpeech(vendor.bought);
            updateStatusBadges();
            renderItems();
          }
        });

        updateBuyButton();
        controls.appendChild(buyBtn);
        card.appendChild(controls);
        itemsContainer.appendChild(card);
      });
    }

    // Goods / Activities / Non-consumables
    if (activeTab === 'Semua' || activeTab === 'Lainnya') {
      availableGoods.forEach(good => {
        const card = document.createElement('div');
        card.className = 'shop-item-card';

        const left = document.createElement('div');
        left.className = 'shop-item-left';

        const icon = document.createElement('img');
        icon.className = 'shop-item-icon';
        icon.src = good.icon || 'assets/items/item_buku.png';
        icon.alt = good.label;

        const info = document.createElement('div');
        info.className = 'shop-item-info';

        const name = document.createElement('span');
        name.className = 'shop-item-name';
        name.textContent = good.label;

        const desc = document.createElement('span');
        desc.className = 'shop-item-desc';
        desc.textContent = good.desc || good.category || '';

        const price = document.createElement('span');
        price.className = 'shop-item-price';
        price.textContent = rupiah.format(good.price);

        info.appendChild(name);
        info.appendChild(desc);
        info.appendChild(price);
        left.appendChild(icon);
        left.appendChild(info);
        card.appendChild(left);

        const buyBtn = document.createElement('button');
        buyBtn.type = 'button';
        buyBtn.className = 'shop-buy-btn';
        buyBtn.textContent = 'Beli';

        const freshCash = getCash(store.getState().ledger);
        if (freshCash < good.price) {
          buyBtn.disabled = true;
          buyBtn.title = 'Uang kas tidak mencukupi';
        }

        buyBtn.addEventListener('click', () => {
          const freshState = store.getState();
          const cash = getCash(freshState.ledger);
          if (cash < good.price) {
            setVendorSpeech(vendor.noCash);
            alert('Uang kas tidak mencukupi!');
            return;
          }

          const clock = freshState.clock || {};
          let cat = 'BEBAN_LAIN';
          if (good.category?.includes('Sekolah')) cat = 'BEBAN_SEKOLAH';
          else if (good.category?.includes('Komunikasi')) cat = 'BEBAN_KOMUNIKASI';
          else if (good.category?.includes('Perawatan')) cat = 'BEBAN_PERAWATAN_DIRI';

          const expEntry = createExpenseEntry(
            clock.day || 1,
            clock.month || 1,
            cat,
            good.price,
            `Beli ${good.label}`,
            clock.timeOfDay || 480
          );
          const ledgerRes = addEntry(freshState.ledger, expEntry);
          if (ledgerRes.error) {
            alert(ledgerRes.error);
            return;
          }

          const updates = { ledger: ledgerRes.ledger };
          if (good.setFlag) {
            updates.flags = { ...(freshState.flags || {}), [good.setFlag]: true };
          }

          if (window.__LJ__?.advanceTime) {
            window.__LJ__.advanceTime(good.minutes || 10, good.label);
          }

          store.setState(updates);
          emit(DOMAIN_EVENTS.CASH_CHANGED, getCash(ledgerRes.ledger));
          setVendorSpeech(vendor.bought);
          updateStatusBadges();
          renderItems();
        });

        card.appendChild(buyBtn);
        itemsContainer.appendChild(card);
      });
    }
  }

  renderItems();
  bodyLayout.appendChild(contentCol);
  modal.appendChild(bodyLayout);

  // 7. Footer with "Selesai" button (Rule 86 §2)
  const footer = document.createElement('div');
  footer.className = 'panel-footer shop-modal-footer';

  const doneBtn = document.createElement('button');
  doneBtn.type = 'button';
  doneBtn.className = 'shop-btn-done';
  doneBtn.textContent = 'Selesai';
  doneBtn.addEventListener('click', () => {
    closeShopModal();
    if (options.onClose) options.onClose();
  });
  footer.appendChild(doneBtn);
  modal.appendChild(footer);

  activeBackdrop.appendChild(modal);
  container.appendChild(activeBackdrop);

  // Esc closes
  activeKeydownHandler = (e) => {
    if (e.key === 'Escape') {
      closeShopModal();
      if (options.onClose) options.onClose();
    }
  };
  document.addEventListener('keydown', activeKeydownHandler);
}

function renderFuelPanel(contentCol, store, shopDef, rupiah, setVendorSpeech, vendor, updateStatusBadges) {
  const container = document.createElement('div');
  container.className = 'shop-items-container';

  const infoNotice = document.createElement('div');
  infoNotice.style.padding = '8px 12px';
  infoNotice.style.background = 'rgba(217, 164, 65, 0.15)';
  infoNotice.style.border = '1px solid #D9A441';
  infoNotice.style.borderRadius = '6px';
  infoNotice.style.fontSize = '12px';
  infoNotice.style.color = '#F7EEDA';
  infoNotice.style.marginBottom = '12px';
  infoNotice.textContent = 'Pilih nominal pengisian bahan bakar motor Anda (Pertalite).';
  container.appendChild(infoNotice);

  const presetsGrid = document.createElement('div');
  presetsGrid.className = 'shop-fuel-presets';

  const presets = [
    { label: 'Pertalite Rp10.000', amount: 10000, percent: 20 },
    { label: 'Pertalite Rp20.000', amount: 20000, percent: 40 },
    { label: 'Pertalite Rp30.000', amount: 30000, percent: 60 },
    { label: 'Isi Penuh Tangki (100%)', isFull: true }
  ];

  presets.forEach(p => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'shop-fuel-btn';

    const state = store.getState();
    const curGas = state.gasoline ?? 100;
    const pricePerPercent = shopDef.fuel?.pricePerPercent || 500;

    let cost = p.amount;
    let percentText = `+${p.percent}%`;
    if (p.isFull) {
      cost = calculateFillCost(curGas, pricePerPercent);
      percentText = `Isi hingga 100% (+${100 - curGas}%)`;
    }

    const titleSpan = document.createElement('span');
    titleSpan.textContent = p.label;
    const priceSpan = document.createElement('span');
    priceSpan.className = 'shop-fuel-btn-price';
    priceSpan.textContent = `${rupiah.format(cost)} (${percentText})`;

    btn.appendChild(titleSpan);
    btn.appendChild(priceSpan);

    if (curGas >= 100) {
      btn.disabled = true;
      btn.title = 'Tangki sudah penuh 100%!';
    } else if (getCash(state.ledger) < cost) {
      btn.disabled = true;
      btn.title = 'Uang kas tidak mencukupi';
    }

    btn.addEventListener('click', () => {
      const freshState = store.getState();
      const freshGas = freshState.gasoline ?? 100;
      if (freshGas >= 100) {
        setVendorSpeech(vendor.tankFull);
        alert('Tangki bensin sudah penuh 100%!');
        return;
      }

      const freshCash = getCash(freshState.ledger);
      if (freshCash < cost) {
        setVendorSpeech(vendor.noCash);
        alert('Uang kas tidak mencukupi!');
        return;
      }

      let res;
      if (p.isFull) {
        res = refuelPercent(freshState, 100 - freshGas, pricePerPercent);
      } else {
        res = refuelAmount(freshState, p.amount, pricePerPercent);
      }

      if (res && res.cost > 0) {
        const clock = freshState.clock || {};
        const expEntry = createExpenseEntry(
          clock.day || 1,
          clock.month || 1,
          'transportasi',
          res.cost,
          `Isi bensin di SPBU (+${res.addedPercent}%)`,
          clock.timeOfDay || 480
        );
        const ledgerRes = addEntry(freshState.ledger, expEntry);
        if (ledgerRes.error) {
          alert(ledgerRes.error);
          return;
        }

        if (window.__LJ__?.advanceTime) {
          window.__LJ__.advanceTime(10, 'Isi bensin motor');
        }

        store.setState({
          ledger: ledgerRes.ledger,
          gasoline: res.newGasoline
        });

        emit(DOMAIN_EVENTS.FUEL_CHANGED, { gasoline: res.newGasoline, percent: res.newGasoline });
        emit(DOMAIN_EVENTS.CASH_CHANGED, getCash(ledgerRes.ledger));

        setVendorSpeech(vendor.bought);
        updateStatusBadges();
        closeShopModal();
      }
    });

    presetsGrid.appendChild(btn);
  });

  container.appendChild(presetsGrid);
  contentCol.appendChild(container);
}

// Global listener for 'lj:openShop' custom event
document.addEventListener('lj:openShop', (e) => {
  const shopId = e.detail?.shopId || 'kantin_sekolah';
  const filter = e.detail?.category || null;
  const store = window.__LJ__?.getStore?.();
  if (store) {
    createShopModal(document.body, store, shopId, { categoryFilter: filter });
  }
});
