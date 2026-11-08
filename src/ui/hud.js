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

function makeIcon(src, alt = '') {
  const img = document.createElement('img');
  img.className = 'hud-icon-img';
  img.src = src;
  img.alt = alt;
  return img;
}

function makeBtnIcon(src) {
  const img = document.createElement('img');
  img.className = 'btn-icon-img';
  img.src = src;
  img.alt = '';
  return img;
}

export function createHUD(container, store, onOpenCashbook, onOpenBudget, onOpenSettings) {
  const hudElement = document.createElement('header');
  hudElement.className = 'lj-hud';
  hudElement.setAttribute('role', 'region');
  hudElement.setAttribute('aria-label', 'Status Permainan');

  // ================= KIRI: STATUS PLAYER & FINANSIAL =================
  const statsGroup = document.createElement('div');
  statsGroup.className = 'hud-group hud-stats';

  // Kas Badge (Icon Koin Pixel Art)
  const cashBadge = document.createElement('div');
  cashBadge.className = 'hud-badge cash-badge';
  const cashTag = document.createElement('span');
  cashTag.className = 'hud-tag tag-cash';
  cashTag.textContent = 'KAS';
  const cashValue = document.createElement('span');
  cashValue.className = 'hud-val hud-val-cash';
  cashValue.textContent = 'Rp0';
  cashBadge.appendChild(makeIcon('assets/icons/icon_coin.png', 'Kas'));
  cashBadge.appendChild(cashTag);
  cashBadge.appendChild(cashValue);

  // Tabungan Badge (Icon Celengan Ayam Pixel Art)
  const savingsBadge = document.createElement('div');
  savingsBadge.className = 'hud-badge savings-badge';
  const savingsTag = document.createElement('span');
  savingsTag.className = 'hud-tag tag-savings';
  savingsTag.textContent = 'TABUNGAN';
  const savingsValue = document.createElement('span');
  savingsValue.className = 'hud-val hud-val-savings';
  savingsValue.textContent = 'Rp0';
  savingsBadge.appendChild(makeIcon('assets/icons/icon_celengan.png', 'Tabungan'));
  savingsBadge.appendChild(savingsTag);
  savingsBadge.appendChild(savingsValue);

  // Bensin Badge dengan Visual Bar (Icon Pompa Bensin Pixel Art)
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
  gasBadge.appendChild(makeIcon('assets/icons/icon_bensin.png', 'Bensin'));
  gasBadge.appendChild(gasTag);
  gasBadge.appendChild(gasContainer);
  gasBadge.appendChild(gasValue);

  statsGroup.appendChild(cashBadge);
  statsGroup.appendChild(savingsBadge);
  statsGroup.appendChild(gasBadge);

  // ================= TENGAH: WAKTU & MISI =================
  const centerGroup = document.createElement('div');
  centerGroup.className = 'hud-group hud-center';

  // --- HARVEST MOON-INSPIRED TIME WIDGET & BAR WAKTU ---
  const timeWidget = document.createElement('div');
  timeWidget.className = 'hud-time-widget';
  timeWidget.setAttribute('role', 'status');
  timeWidget.setAttribute('aria-label', 'Status Waktu & Siklus Hari');

  // 1. Sky Dial Box (Kiri: Langit dinamis + Marker Matahari/Bulan yang bergerak)
  const skyBox = document.createElement('div');
  skyBox.className = 'time-sky-box sky-pagi';
  const skyMarker = document.createElement('span');
  skyMarker.className = 'time-sky-marker';
  skyMarker.textContent = '☀️';
  skyBox.appendChild(skyMarker);

  // 2. Info Stack (Kanan: Hari, Tanggal, Jam Digital, dan Bar Waktu)
  const infoStack = document.createElement('div');
  infoStack.className = 'time-info-stack';

  // Row Atas: Tab Hari (e.g. RABU) + Tanggal
  const rowTop = document.createElement('div');
  rowTop.className = 'time-row-top';
  const dayPill = document.createElement('span');
  dayPill.className = 'time-day-pill';
  dayPill.textContent = 'SENIN';
  const dateText = document.createElement('span');
  dateText.className = 'time-date-text';
  dateText.textContent = 'Hari 1 · Bln 1';
  rowTop.appendChild(dayPill);
  rowTop.appendChild(dateText);

  // Row Bawah: Jam Digital + Bar Waktu Visual + Tag Periode
  const rowBottom = document.createElement('div');
  rowBottom.className = 'time-row-bottom';

  const digitalBox = document.createElement('div');
  digitalBox.className = 'time-digital-box';
  const clockIcon = makeBtnIcon('assets/icons/icon_jam.png');
  const digitalVal = document.createElement('span');
  digitalVal.className = 'time-digital-val hud-val-clock'; // preserves class for automated tests
  digitalVal.textContent = '08:00';
  const periodTag = document.createElement('span');
  periodTag.className = 'time-period-tag';
  periodTag.textContent = 'PAGI';
  digitalBox.appendChild(clockIcon);
  digitalBox.appendChild(digitalVal);
  digitalBox.appendChild(periodTag);

  // Bar Waktu Visual (Track & Fill yang bergerak seiring waktu berjalan)
  const timeBarTrack = document.createElement('div');
  timeBarTrack.className = 'time-bar-track';
  timeBarTrack.title = 'Siklus Perjalanan Waktu Hari Ini (24 Jam)';
  const timeBarFill = document.createElement('div');
  timeBarFill.className = 'time-bar-fill';
  timeBarFill.style.width = '33%';
  timeBarTrack.appendChild(timeBarFill);

  rowBottom.appendChild(digitalBox);
  rowBottom.appendChild(timeBarTrack);

  infoStack.appendChild(rowTop);
  infoStack.appendChild(rowBottom);

  timeWidget.appendChild(skyBox);
  timeWidget.appendChild(infoStack);

  // Misi (Icon Bendera Misi Pixel Art)
  const missionBadge = document.createElement('div');
  missionBadge.className = 'hud-badge mission-badge';
  const missionTag = document.createElement('span');
  missionTag.className = 'hud-tag tag-mission';
  missionTag.textContent = 'MISI';
  const missionTitle = document.createElement('span');
  missionTitle.className = 'hud-val-mission';
  missionTitle.textContent = '...';
  missionBadge.appendChild(makeIcon('assets/icons/icon_misi.png', 'Misi'));
  missionBadge.appendChild(missionTag);
  missionBadge.appendChild(missionTitle);

  centerGroup.appendChild(timeWidget);
  centerGroup.appendChild(missionBadge);

  // ================= KANAN: TOMBOL NAVIGASI & MENU (DENGAN IKON PIXEL ART, TANPA EMOTE) =================
  const navGroup = document.createElement('div');
  navGroup.className = 'hud-group hud-nav';

  const cashbookBtn = document.createElement('button');
  cashbookBtn.type = 'button';
  cashbookBtn.className = 'lj-btn secondary btn-sm hud-btn';
  cashbookBtn.appendChild(makeBtnIcon('assets/icons/icon_buku.png'));
  const cbLabel = document.createElement('span');
  cbLabel.textContent = 'Buku Kas';
  cashbookBtn.appendChild(cbLabel);
  cashbookBtn.addEventListener('click', onOpenCashbook);

  const budgetBtn = document.createElement('button');
  budgetBtn.type = 'button';
  budgetBtn.className = 'lj-btn secondary btn-sm hud-btn';
  budgetBtn.appendChild(makeBtnIcon('assets/icons/icon_wallet.png'));
  const bgLabel = document.createElement('span');
  bgLabel.textContent = 'Anggaran';
  budgetBtn.appendChild(bgLabel);
  budgetBtn.addEventListener('click', onOpenBudget);

  const settingsBtn = document.createElement('button');
  settingsBtn.type = 'button';
  settingsBtn.className = 'lj-btn secondary btn-sm hud-btn';
  settingsBtn.appendChild(makeBtnIcon('assets/icons/icon_gamepad.png'));
  const stLabel = document.createElement('span');
  stLabel.textContent = 'Pengaturan';
  settingsBtn.appendChild(stLabel);
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

    // --- UPDATE STATUS WAKTU & BAR WAKTU HARVEST MOON STYLE ---
    const clock = state.clock || {};
    const day = clock.day || 1;
    const month = clock.month || 1;
    const totalMin = clock.timeOfDay ?? (8 * 60);

    const hours = Math.floor(totalMin / 60) % 24;
    const mins = Math.floor(totalMin % 60);
    const hh = String(hours).padStart(2, '0');
    const mm = String(mins).padStart(2, '0');

    const DAY_NAMES = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'];
    const dayName = DAY_NAMES[(day - 1) % 7] || 'Senin';

    dayPill.textContent = dayName.toUpperCase();
    dateText.textContent = `Hari ${day} · Bln ${month}`;
    digitalVal.textContent = `${hh}:${mm}`;

    // Period & Sky themes
    let period = 'PAGI';
    let skyClass = 'sky-pagi';
    let markerEmoji = '☀️';

    if (hours >= 6 && hours < 11) {
      period = 'PAGI';
      skyClass = 'sky-pagi';
      markerEmoji = '🌅';
    } else if (hours >= 11 && hours < 15) {
      period = 'SIANG';
      skyClass = 'sky-siang';
      markerEmoji = '☀️';
    } else if (hours >= 15 && hours < 18) {
      period = 'SORE';
      skyClass = 'sky-sore';
      markerEmoji = '🌇';
    } else {
      period = 'MALAM';
      skyClass = 'sky-malam';
      markerEmoji = '🌙';
    }

    periodTag.textContent = period;
    skyBox.className = `time-sky-box ${skyClass}`;
    skyMarker.textContent = markerEmoji;

    // Persentase Bar Waktu (00:00 - 24:00 = 0% - 100%)
    const dayPercent = Math.max(0, Math.min(100, (totalMin / 1440) * 100));
    timeBarFill.style.width = `${dayPercent.toFixed(1)}%`;

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
