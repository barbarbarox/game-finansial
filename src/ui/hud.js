/**
 * hud.js — HUD DOM overlay
 * Displays cash, gasoline, active mission, clock, and action buttons.
 * Strictly adheres to Rule 50: uses textContent, no innerHTML for dynamic data.
 */

import { getCash, getSavings } from '../domain/ledger.js';

export function createHUD(container, store, onOpenCashbook, onOpenBudget) {
  const hudElement = document.createElement('header');
  hudElement.className = 'lj-hud';
  hudElement.setAttribute('role', 'region');
  hudElement.setAttribute('aria-label', 'Status Permainan');

  // Top Left: Financial Summary
  const statsGroup = document.createElement('div');
  statsGroup.className = 'hud-group hud-stats';

  const cashBadge = document.createElement('div');
  cashBadge.className = 'hud-badge cash-badge';
  const cashLabel = document.createElement('span');
  cashLabel.className = 'hud-label';
  cashLabel.textContent = 'Kas: ';
  const cashValue = document.createElement('strong');
  cashValue.className = 'hud-val-cash';
  cashValue.textContent = 'Rp0';
  cashBadge.appendChild(cashLabel);
  cashBadge.appendChild(cashValue);

  const savingsBadge = document.createElement('div');
  savingsBadge.className = 'hud-badge savings-badge';
  const savingsLabel = document.createElement('span');
  savingsLabel.className = 'hud-label';
  savingsLabel.textContent = 'Tabungan: ';
  const savingsValue = document.createElement('strong');
  savingsValue.className = 'hud-val-savings';
  savingsValue.textContent = 'Rp0';
  savingsBadge.appendChild(savingsLabel);
  savingsBadge.appendChild(savingsValue);

  const gasBadge = document.createElement('div');
  gasBadge.className = 'hud-badge gas-badge';
  const gasLabel = document.createElement('span');
  gasLabel.className = 'hud-label';
  gasLabel.textContent = 'Bensin: ';
  const gasValue = document.createElement('strong');
  gasValue.className = 'hud-val-gas';
  gasValue.textContent = '100%';
  gasBadge.appendChild(gasLabel);
  gasBadge.appendChild(gasValue);

  statsGroup.appendChild(cashBadge);
  statsGroup.appendChild(savingsBadge);
  statsGroup.appendChild(gasBadge);

  // Center: Clock & Mission
  const centerGroup = document.createElement('div');
  centerGroup.className = 'hud-group hud-center';

  const clockBadge = document.createElement('div');
  clockBadge.className = 'hud-badge clock-badge';
  const clockText = document.createElement('span');
  clockText.className = 'hud-val-clock';
  clockText.textContent = 'Bulan 1 · Hari 1';
  clockBadge.appendChild(clockText);

  const missionBadge = document.createElement('div');
  missionBadge.className = 'hud-badge mission-badge';
  const missionTitle = document.createElement('span');
  missionTitle.className = 'hud-val-mission';
  missionTitle.textContent = 'Misi: Terima Uang Saku';
  missionBadge.appendChild(missionTitle);

  centerGroup.appendChild(clockBadge);
  centerGroup.appendChild(missionBadge);

  // Right: Navigation Buttons
  const navGroup = document.createElement('div');
  navGroup.className = 'hud-group hud-nav';

  const cashbookBtn = document.createElement('button');
  cashbookBtn.type = 'button';
  cashbookBtn.className = 'btn btn-secondary';
  cashbookBtn.textContent = 'Buku Kas';
  cashbookBtn.addEventListener('click', onOpenCashbook);

  const budgetBtn = document.createElement('button');
  budgetBtn.type = 'button';
  budgetBtn.className = 'btn btn-secondary';
  budgetBtn.textContent = 'Anggaran';
  budgetBtn.addEventListener('click', onOpenBudget);

  navGroup.appendChild(cashbookBtn);
  navGroup.appendChild(budgetBtn);

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
    gasValue.textContent = `${Math.max(0, Math.round(state.gasoline || 0))}%`;
    clockText.textContent = `Bulan ${state.clock?.month || 1} · Hari ${state.clock?.day || 1}`;

    const activeM = state.missions?.find(m => !m.completed);
    missionTitle.textContent = activeM ? `Misi: ${activeM.title}` : 'Semua Misi Selesai!';
  }

  // Initial render
  if (store) {
    updateUI(store.getState());
    store.subscribe(updateUI);
  }

  return hudElement;
}
