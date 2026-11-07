/**
 * hud.js — HUD DOM overlay untuk Life Journey
 * Mengimplementasikan UI Design Rules (docs/UI-DESIGN-RULES.md):
 * - Status finansial (Kas, Tabungan) tanpa emote/emoji
 * - Status bensin dengan visual bar persentase
 * - Status waktu & misi aktif
 * - Tombol navigasi Buku Kas, Anggaran, & Pengaturan (bersih tanpa emote)
 * Anti-XSS: textContent only, no innerHTML.
 */

import { getCash, getSavings } from '../domain/ledger.js';

export function createHUD(container, store, onOpenCashbook, onOpenBudget, onOpenSettings) {
  const hudElement = document.createElement('header');
  hudElement.className = 'lj-hud';
  hudElement.setAttribute('role', 'region');
  hudElement.setAttribute('aria-label', 'Status Permainan');

  // ================= KIRI: STATUS PLAYER & FINANSIAL =================
  const statsGroup = document.createElement('div');
  statsGroup.className = 'hud-group hud-stats';

  // Kas Badge
  const cashBadge = document.createElement('div');
  cashBadge.className = 'hud-badge cash-badge';
  const cashTag = document.createElement('span');
  cashTag.className = 'hud-tag tag-cash';
  cashTag.textContent = 'KAS';
  const cashValue = document.createElement('span');
  cashValue.className = 'hud-val hud-val-cash';
  cashValue.textContent = 'Rp0';
  cashBadge.appendChild(cashTag);
  cashBadge.appendChild(cashValue);

  // Tabungan Badge
  const savingsBadge = document.createElement('div');
  savingsBadge.className = 'hud-badge savings-badge';
  const savingsTag = document.createElement('span');
  savingsTag.className = 'hud-tag tag-savings';
  savingsTag.textContent = 'TABUNGAN';
  const savingsValue = document.createElement('span');
  savingsValue.className = 'hud-val hud-val-savings';
  savingsValue.textContent = 'Rp0';
  savingsBadge.appendChild(savingsTag);
  savingsBadge.appendChild(savingsValue);

  // Bensin Badge dengan Visual Bar
  const gasBadge = document.createElement('div');
  gasBadge.className = 'hud-badge gas-badge';
  const gasTag = document.createElement('span');
  gasTag.className = 'hud-tag tag-gas';
  gasTag.textContent = 'BENSIN';
  const gasContainer = document.createElement('div');
  gasContainer.className = 'hud-gas-container';
  const gasBar = document.createElement('div');
  gasBar.className = 'hud-gas-bar';
  const gasFill = document.createElement('div');
  gasFill.className = 'hud-gas-fill';
  gasBar.appendChild(gasFill);
  gasContainer.appendChild(gasBar);
  const gasValue = document.createElement('span');
  gasValue.className = 'hud-val hud-val-gas';
  gasValue.textContent = '100%';
  gasBadge.appendChild(gasTag);
  gasBadge.appendChild(gasContainer);
  gasBadge.appendChild(gasValue);

  statsGroup.appendChild(cashBadge);
  statsGroup.appendChild(savingsBadge);
  statsGroup.appendChild(gasBadge);

  // ================= TENGAH: WAKTU & MISI =================
  const centerGroup = document.createElement('div');
  centerGroup.className = 'hud-group hud-center';

  // Clock
  const clockBadge = document.createElement('div');
  clockBadge.className = 'hud-badge clock-badge';
  const clockTag = document.createElement('span');
  clockTag.className = 'hud-tag tag-clock';
  clockTag.textContent = 'WAKTU';
  const clockText = document.createElement('span');
  clockText.className = 'hud-val hud-val-clock';
  clockText.textContent = 'Bulan 1 · Hari 1';
  clockBadge.appendChild(clockTag);
  clockBadge.appendChild(clockText);

  // Misi
  const missionBadge = document.createElement('div');
  missionBadge.className = 'hud-badge mission-badge';
  const missionTag = document.createElement('span');
  missionTag.className = 'hud-tag tag-mission';
  missionTag.textContent = 'MISI';
  const missionTitle = document.createElement('span');
  missionTitle.className = 'hud-val-mission';
  missionTitle.textContent = '...';
  missionBadge.appendChild(missionTag);
  missionBadge.appendChild(missionTitle);

  centerGroup.appendChild(clockBadge);
  centerGroup.appendChild(missionBadge);

  // ================= KANAN: TOMBOL NAVIGASI & MENU (TANPA EMOTE) =================
  const navGroup = document.createElement('div');
  navGroup.className = 'hud-group hud-nav';

  const cashbookBtn = document.createElement('button');
  cashbookBtn.type = 'button';
  cashbookBtn.className = 'lj-btn secondary btn-sm hud-btn';
  cashbookBtn.textContent = 'Buku Kas';
  cashbookBtn.addEventListener('click', onOpenCashbook);

  const budgetBtn = document.createElement('button');
  budgetBtn.type = 'button';
  budgetBtn.className = 'lj-btn secondary btn-sm hud-btn';
  budgetBtn.textContent = 'Anggaran';
  budgetBtn.addEventListener('click', onOpenBudget);

  const settingsBtn = document.createElement('button');
  settingsBtn.type = 'button';
  settingsBtn.className = 'lj-btn secondary btn-sm hud-btn';
  settingsBtn.textContent = 'Pengaturan';
  if (onOpenSettings) {
    settingsBtn.addEventListener('click', onOpenSettings);
  }

  navGroup.appendChild(cashbookBtn);
  navGroup.appendChild(budgetBtn);
  navGroup.appendChild(settingsBtn);

  hudElement.appendChild(statsGroup);
  hudElement.appendChild(centerGroup);
  hudElement.appendChild(navGroup);
  container.appendChild(hudElement);

  const rupiahFormatter = new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    maximumFractionDigits: 0
  });

  function updateUI(state) {
    if (!state) return;
    const cash = getCash(state.ledger);
    const savings = getSavings(state.ledger);
    cashValue.textContent = rupiahFormatter.format(cash);
    savingsValue.textContent = rupiahFormatter.format(savings);

    const gasPercent = Math.max(0, Math.min(100, Math.round(state.gasoline ?? 100)));
    gasValue.textContent = `${gasPercent}%`;
    gasFill.style.width = `${gasPercent}%`;
    gasFill.className = 'hud-gas-fill';
    if (gasPercent < 30) {
      gasFill.classList.add('danger');
    } else if (gasPercent < 60) {
      gasFill.classList.add('warning');
    }

    clockText.textContent = `Bulan ${state.clock?.month || 1} · Hari ${state.clock?.day || 1}`;

    const activeM = state.missions?.find(m => !m.completed);
    missionTitle.textContent = activeM ? activeM.title : 'Semua Selesai';
  }

  // Initial render
  if (store) {
    updateUI(store.getState());
    store.subscribe(updateUI);
  }

  return hudElement;
}
