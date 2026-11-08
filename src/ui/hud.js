/**
 * hud.js — HUD DOM overlay untuk Life Journey
 * Mengimplementasikan gaya Status Dashboard Harvest Moon sesuai referensi gambar:
 * - Tab hari di atas (RABU, SENIN, dst.)
 * - Kotak dial langit dinamis dengan marker matahari/bulan di kiri
 * - Kolom informasi inset: Tanggal, Jam Digital, Kas, dan Tabungan
 * - Bar Bensin/Energi visual persentase langsung di bawah kotak
 * - Tombol navigasi Buku Kas, Anggaran, & Pengaturan di sisi kanan atas
 * Anti-XSS: textContent only, no innerHTML.
 */

import { getCash, getSavings } from '../domain/ledger.js';

function makeIcon(src, alt = '') {
  const img = document.createElement('img');
  img.className = 'hm-icon-img';
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

  // ================= 1. HARVEST MOON STATUS DASHBOARD (KIRI ATAS) =================
  const statusWidget = document.createElement('div');
  statusWidget.className = 'hm-status-widget';
  statusWidget.setAttribute('role', 'status');

  // Tab Hari di bagian atas (seperti tab 'Rabu' di referensi)
  const dayTab = document.createElement('div');
  dayTab.className = 'hm-day-tab';
  const dayPill = document.createElement('span');
  dayPill.className = 'hm-day-text';
  dayPill.textContent = 'SENIN';
  dayTab.appendChild(dayPill);
  statusWidget.appendChild(dayTab);

  // Main Box (kotak oranye/kayu)
  const mainBox = document.createElement('div');
  mainBox.className = 'hm-main-box';

  // Kolom Kiri: Dial Langit / Waktu (Sky Dial Box)
  const skyBox = document.createElement('div');
  skyBox.className = 'hm-sky-box sky-pagi';
  const skyMarker = document.createElement('span');
  skyMarker.className = 'hm-sky-marker';
  skyMarker.textContent = '☀️';
  const skyArrow = document.createElement('div');
  skyArrow.className = 'hm-sky-arrow';
  skyArrow.textContent = '▲';
  skyBox.appendChild(skyMarker);
  skyBox.appendChild(skyArrow);
  mainBox.appendChild(skyBox);

  // Kolom Kanan: 4 Kotak Inset (Tanggal, Jam, Kas, Tabungan)
  const infoCol = document.createElement('div');
  infoCol.className = 'hm-info-column';

  // Row 1: Tanggal (misal: "Hari 1 · Bln 1")
  const dateBox = document.createElement('div');
  dateBox.className = 'hm-inset-box hm-date-box';
  const dateText = document.createElement('span');
  dateText.className = 'hm-date-text';
  dateText.textContent = 'Hari 1 · Bln 1';
  dateBox.appendChild(dateText);
  infoCol.appendChild(dateBox);

  // Row 2: Jam Digital (Icon Jam + HH:MM + Tag Periode)
  const timeBox = document.createElement('div');
  timeBox.className = 'hm-inset-box hm-time-box';
  const timeIcon = makeIcon('assets/icons/icon_jam.png', 'Jam');
  const digitalVal = document.createElement('span');
  digitalVal.className = 'hm-time-text hud-val-clock'; // preserves selector for tests
  digitalVal.textContent = '08:00';
  const periodBadge = document.createElement('span');
  periodBadge.className = 'hm-period-badge';
  periodBadge.textContent = 'PAGI';
  timeBox.appendChild(timeIcon);
  timeBox.appendChild(digitalVal);
  timeBox.appendChild(periodBadge);
  infoCol.appendChild(timeBox);

  // Row 3: Kas (Icon Koin + Jumlah Kas)
  const cashBox = document.createElement('div');
  cashBox.className = 'hm-inset-box hm-cash-box';
  const cashIcon = makeIcon('assets/icons/icon_coin.png', 'Kas');
  const cashVal = document.createElement('span');
  cashVal.className = 'hm-cash-text hud-val-cash'; // preserves selector for tests
  cashVal.textContent = 'Rp1.000.000';
  cashBox.appendChild(cashIcon);
  cashBox.appendChild(cashVal);
  infoCol.appendChild(cashBox);

  // Row 4: Tabungan (Icon Celengan + Jumlah Tabungan)
  const savingsBox = document.createElement('div');
  savingsBox.className = 'hm-inset-box hm-savings-box';
  const savingsIcon = makeIcon('assets/icons/icon_celengan.png', 'Tabungan');
  const savingsVal = document.createElement('span');
  savingsVal.className = 'hm-savings-text hud-val-savings'; // preserves selector for tests
  savingsVal.textContent = 'Rp0';
  savingsBox.appendChild(savingsIcon);
  savingsBox.appendChild(savingsVal);
  infoCol.appendChild(savingsBox);

  mainBox.appendChild(infoCol);
  statusWidget.appendChild(mainBox);

  // Bagian Bawah: Bar Bensin / Energi (Visual Bar Hijau 100%)
  const fuelContainer = document.createElement('div');
  fuelContainer.className = 'hm-fuel-bar-container';
  const fuelIcon = makeIcon('assets/icons/icon_bensin.png', 'Bensin');
  fuelIcon.className = 'hm-fuel-icon';
  const fuelTrack = document.createElement('div');
  fuelTrack.className = 'hm-fuel-track';
  const fuelFill = document.createElement('div');
  fuelFill.className = 'hm-fuel-fill';
  fuelFill.style.width = '100%';
  const fuelText = document.createElement('span');
  fuelText.className = 'hm-fuel-text hud-val-gas'; // preserves selector for tests
  fuelText.textContent = '100%';
  fuelFill.appendChild(fuelText);
  fuelTrack.appendChild(fuelFill);
  fuelContainer.appendChild(fuelIcon);
  fuelContainer.appendChild(fuelTrack);
  statusWidget.appendChild(fuelContainer);

  hudElement.appendChild(statusWidget);

  // ================= 2. MISI AKTIF (TENGAH ATAS) =================
  const missionBadge = document.createElement('div');
  missionBadge.className = 'hud-mission-badge';
  const missionIcon = document.createElement('img');
  missionIcon.className = 'hm-icon-img';
  missionIcon.src = 'assets/icons/icon_misi.png';
  missionIcon.alt = 'Misi';
  const missionTag = document.createElement('span');
  missionTag.className = 'hud-tag tag-mission';
  missionTag.textContent = 'MISI';
  const missionTitle = document.createElement('span');
  missionTitle.className = 'hud-val-mission';
  missionTitle.textContent = '...';
  missionBadge.appendChild(missionIcon);
  missionBadge.appendChild(missionTag);
  missionBadge.appendChild(missionTitle);
  hudElement.appendChild(missionBadge);

  // ================= 3. TOMBOL NAVIGASI & MENU (KANAN ATAS) =================
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
  hudElement.appendChild(navGroup);

  container.appendChild(hudElement);

  const rupiahFormatter = new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    maximumFractionDigits: 0
  });

  const DAY_NAMES = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'];

  function updateUI(state) {
    if (!state) return;

    // Financial updates
    const cash = getCash(state.ledger);
    const savings = getSavings(state.ledger);
    cashVal.textContent = rupiahFormatter.format(cash);
    savingsVal.textContent = rupiahFormatter.format(savings);

    // Fuel bar updates
    const gasPercent = Math.max(0, Math.min(100, Math.round(state.gasoline ?? 100)));
    fuelText.textContent = `${gasPercent}%`;
    fuelFill.style.width = `${gasPercent}%`;
    fuelFill.className = 'hm-fuel-fill';
    if (gasPercent < 30) {
      fuelFill.classList.add('danger');
    } else if (gasPercent < 60) {
      fuelFill.classList.add('warning');
    }

    // Time & Calendar updates
    const clock = state.clock || {};
    const day = clock.day || 1;
    const month = clock.month || 1;
    const totalMin = (clock.gameMinutes !== undefined) ? (clock.gameMinutes % 1440) : (clock.timeOfDay ?? (6 * 60));

    const hours = Math.floor(totalMin / 60) % 24;
    const mins = Math.floor(totalMin % 60);
    const hh = String(hours).padStart(2, '0');
    const mm = String(mins).padStart(2, '0');

    const dayName = DAY_NAMES[(day - 1) % 7] || 'Senin';
    dayPill.textContent = dayName.toUpperCase();
    dateText.textContent = `Hari ${day} · Bln ${month}`;
    digitalVal.textContent = `${hh}:${mm}`;

    // Period of day & sky theme (Rule 72 §2: Pagi 06-12, Siang 12-17, Sore 17-19, Malam 19-06)
    let period = 'PAGI';
    let skyClass = 'sky-pagi';
    let markerEmoji = '🌅';

    if (hours >= 6 && hours < 12) {
      period = 'PAGI';
      skyClass = 'sky-pagi';
      markerEmoji = '🌅';
    } else if (hours >= 12 && hours < 17) {
      period = 'SIANG';
      skyClass = 'sky-siang';
      markerEmoji = '☀️';
    } else if (hours >= 17 && hours < 19) {
      period = 'SORE';
      skyClass = 'sky-sore';
      markerEmoji = '🌇';
    } else {
      period = 'MALAM';
      skyClass = 'sky-malam';
      markerEmoji = '🌙';
    }

    periodBadge.textContent = period;
    skyBox.className = `hm-sky-box ${skyClass}`;
    skyMarker.textContent = markerEmoji;

    // Arrow positioning based on time of day (0 to 1440 minutes)
    const progressFraction = Math.max(0, Math.min(1, totalMin / 1440));
    const arrowOffsetPx = Math.round((progressFraction - 0.5) * 28);
    skyArrow.style.transform = `translateX(${arrowOffsetPx}px)`;

    // Active mission title
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
