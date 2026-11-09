/**
 * settings.js — Menu Pengaturan & Pause Permainan
 * Menyediakan aksi Simpan Permainan, Keluar ke Menu Utama, Pengaturan Audio/Tampilan,
 * Petunjuk Singkat, Kredit, dan Reset Data.
 * Anti-XSS: textContent only.
 */

import { resetSave, saveGame } from '../state/persistence.js';

export function createSettingsModal(container, onClose, onOpenCredits, onExitToMainMenu, store) {
  const backdrop = document.createElement('div');
  backdrop.className = 'lj-modal-backdrop';

  const modal = document.createElement('div');
  modal.className = 'lj-panel settings-panel';
  modal.setAttribute('role', 'dialog');
  modal.setAttribute('aria-modal', 'true');
  modal.setAttribute('aria-label', 'Pengaturan Permainan');

  // Header
  const header = document.createElement('div');
  header.className = 'panel-header';
  const title = document.createElement('h2');
  title.className = 'panel-title';
  title.textContent = 'Menu & Pengaturan';
  const closeBtn = document.createElement('button');
  closeBtn.type = 'button';
  closeBtn.className = 'btn-close';
  closeBtn.textContent = '✕';
  closeBtn.setAttribute('aria-label', 'Tutup Pengaturan');
  closeBtn.addEventListener('click', () => {
    backdrop.remove();
    if (onClose) onClose();
  });
  header.appendChild(title);
  header.appendChild(closeBtn);
  modal.appendChild(header);

  const body = document.createElement('div');
  body.className = 'settings-body';

  // Feedback status label
  const statusToast = document.createElement('div');
  statusToast.className = 'settings-toast';
  statusToast.style.display = 'none';
  body.appendChild(statusToast);

  // Section 1: Manajemen Permainan (Simpan & Keluar)
  const saveSection = document.createElement('div');
  saveSection.className = 'settings-section';
  const s1Title = document.createElement('h3');
  s1Title.textContent = 'Progres Permainan';
  saveSection.appendChild(s1Title);

  const saveGroup = document.createElement('div');
  saveGroup.className = 'btn-group';

  const saveBtn = document.createElement('button');
  saveBtn.type = 'button';
  saveBtn.className = 'btn btn-primary';
  saveBtn.textContent = 'Simpan Permainan';
  if (store) {
    saveBtn.addEventListener('click', () => {
      saveGame(store.getState());
      statusToast.textContent = '✓ Progres permainan berhasil disimpan!';
      statusToast.className = 'settings-toast success';
      statusToast.style.display = 'block';
      setTimeout(() => { statusToast.style.display = 'none'; }, 2500);
    });
  } else {
    saveBtn.disabled = true;
    saveBtn.style.opacity = '0.5';
    saveBtn.title = 'Hanya dapat disimpan saat dalam sesi permainan aktif';
  }

  const exitBtn = document.createElement('button');
  exitBtn.type = 'button';
  exitBtn.className = 'btn btn-secondary';
  exitBtn.textContent = 'Keluar ke Menu Utama';
  if (store) {
    exitBtn.addEventListener('click', () => {
      saveGame(store.getState());
      backdrop.remove();
      if (onExitToMainMenu) {
        onExitToMainMenu();
      } else {
        window.location.reload();
      }
    });
  } else {
    exitBtn.style.display = 'none';
  }

  saveGroup.appendChild(saveBtn);
  if (store) {
    saveGroup.appendChild(exitBtn);
  }
  saveSection.appendChild(saveGroup);

  if (!store) {
    const infoNote = document.createElement('p');
    infoNote.style.fontSize = '11px';
    infoNote.style.color = 'var(--color-text-muted)';
    infoNote.style.marginTop = '6px';
    infoNote.textContent = 'Mode Menu Utama: Mulai atau lanjutkan permainan untuk menyimpan progres.';
    saveSection.appendChild(infoNote);
  }

  body.appendChild(saveSection);

  // Section 2: Pengaturan Audio & Tampilan (Statis & Interaktif)
  const audioSection = document.createElement('div');
  audioSection.className = 'settings-section';
  const s2Title = document.createElement('h3');
  s2Title.textContent = 'Audio & Tampilan';
  audioSection.appendChild(s2Title);

  const audioGrid = document.createElement('div');
  audioGrid.className = 'settings-options-grid';

  function createToggleRow(labelTxt, defaultActive = true) {
    const row = document.createElement('div');
    row.className = 'settings-row';
    const lbl = document.createElement('span');
    lbl.textContent = labelTxt;
    const tBtn = document.createElement('button');
    tBtn.type = 'button';
    tBtn.className = 'btn btn-sm ' + (defaultActive ? 'btn-secondary' : 'btn-tertiary');
    tBtn.textContent = defaultActive ? 'Aktif' : 'Nonaktif';
    tBtn.addEventListener('click', () => {
      const isNowActive = tBtn.textContent === 'Nonaktif';
      tBtn.textContent = isNowActive ? 'Aktif' : 'Nonaktif';
      tBtn.className = 'btn btn-sm ' + (isNowActive ? 'btn-secondary' : 'btn-tertiary');
    });
    row.appendChild(lbl);
    row.appendChild(tBtn);
    return row;
  }

  audioGrid.appendChild(createToggleRow('Musik Latar (BGM):', true));
  audioGrid.appendChild(createToggleRow('Efek Suara (SFX):', true));
  audioGrid.appendChild(createToggleRow('Animasi Karakter:', true));

  // --- Dark / Light Mode Toggle (interactive, persisted) ---
  const themeRow = document.createElement('div');
  themeRow.className = 'settings-row';
  const themeLbl = document.createElement('span');
  themeLbl.className = 'settings-row-label';
  themeLbl.textContent = 'Tema Tampilan:';

  const themeBtn = document.createElement('button');
  themeBtn.type = 'button';
  themeBtn.className = 'btn btn-sm btn-secondary';
  const isLightNow = document.body.classList.contains('lj-light');
  themeBtn.textContent = isLightNow ? 'Terang (aktif)' : 'Gelap (aktif)';

  themeBtn.addEventListener('click', () => {
    const willLight = !document.body.classList.contains('lj-light');
    document.body.classList.toggle('lj-light', willLight);
    try { localStorage.setItem('lj_theme', willLight ? 'light' : 'dark'); } catch(_) {}
    themeBtn.textContent = willLight ? 'Terang (aktif)' : 'Gelap (aktif)';
  });

  themeRow.appendChild(themeLbl);
  themeRow.appendChild(themeBtn);
  audioGrid.appendChild(themeRow);

  audioSection.appendChild(audioGrid);
  body.appendChild(audioSection);

  // Section 2b: Tutorial & Bantuan (Rule 82)
  if (store) {
    const tutSection = document.createElement('div');
    tutSection.className = 'settings-section';
    const tutTitle = document.createElement('h3');
    tutTitle.textContent = 'Tutorial & Panduan';
    tutSection.appendChild(tutTitle);

    const tutRow = document.createElement('div');
    tutRow.className = 'settings-row';
    const tutLbl = document.createElement('span');
    tutLbl.textContent = 'Mulai Ulang Tutorial:';
    const tutBtn = document.createElement('button');
    tutBtn.type = 'button';
    tutBtn.className = 'btn btn-sm btn-secondary';
    tutBtn.textContent = 'Ulangi Tutorial';
    tutBtn.addEventListener('click', () => {
      store.setState({
        tutorial: {
          active: true,
          stepIndex: 0,
          completedSteps: [],
          completed: false,
          pausedClock: true,
          stepStartTime: Date.now(),
          stepProgress: {}
        }
      });
      statusToast.textContent = '✓ Tutorial dimulai ulang!';
      statusToast.className = 'settings-toast success';
      statusToast.style.display = 'block';
      setTimeout(() => { statusToast.style.display = 'none'; }, 2500);
    });
    tutRow.appendChild(tutLbl);
    tutRow.appendChild(tutBtn);
    tutSection.appendChild(tutRow);
    body.appendChild(tutSection);
  }

  // Section 3: Petunjuk & Panduan Singkat
  const guideSection = document.createElement('div');
  guideSection.className = 'settings-section';
  const s3Title = document.createElement('h3');
  s3Title.textContent = 'Petunjuk Singkat Permainan';
  guideSection.appendChild(s3Title);

  const guideList = document.createElement('ul');
  guideList.className = 'settings-guide-list';
  const guides = [
    'Uang saku bulanan sebesar Rp300.000 cair setiap tanggal 1.',
    'Selalu sisihkan minimal 20% uang saku ke Celengan di Rumah sebelum berbelanja.',
    'Pantau persentase bensin di HUD; isi ulang di SPBU sebelum mencapai level kritis.',
    'Gunakan Buku Kas untuk memeriksa riwayat debet/kredit pengeluaranmu.',
    'Dekati NPC di sekitar kota untuk meminta nasihat atau berinteraksi.'
  ];
  guides.forEach(g => {
    const li = document.createElement('li');
    li.textContent = g;
    guideList.appendChild(li);
  });
  guideSection.appendChild(guideList);
  body.appendChild(guideSection);

  // Section 4: Kredit & Reset Data
  const bottomActions = document.createElement('div');
  bottomActions.className = 'settings-actions';

  const creditsBtn = document.createElement('button');
  creditsBtn.type = 'button';
  creditsBtn.className = 'btn btn-tertiary';
  creditsBtn.textContent = 'Kredit & Lisensi Aset';
  creditsBtn.addEventListener('click', () => {
    backdrop.remove();
    if (onOpenCredits) onOpenCredits();
  });

  const resetBtn = document.createElement('button');
  resetBtn.type = 'button';
  resetBtn.className = 'btn btn-negative';
  resetBtn.textContent = 'Hapus Progres (Mulai Ulang)';
  resetBtn.addEventListener('click', () => {
    if (confirm('Apakah Anda yakin ingin menghapus seluruh progres permainan dan mulai dari awal?')) {
      resetSave();
      window.location.reload();
    }
  });

  bottomActions.appendChild(creditsBtn);
  bottomActions.appendChild(resetBtn);
  body.appendChild(bottomActions);

  modal.appendChild(body);
  backdrop.appendChild(modal);
  container.appendChild(backdrop);

  // Klik backdrop untuk menutup modal
  backdrop.addEventListener('click', (e) => {
    if (e.target === backdrop) {
      backdrop.remove();
      if (onClose) onClose();
      window.removeEventListener('keydown', handleKeydown);
    }
  });

  // Keyboard shortcut [Esc] untuk menutup
  const handleKeydown = (e) => {
    if (e.key === 'Escape') {
      backdrop.remove();
      if (onClose) onClose();
      window.removeEventListener('keydown', handleKeydown);
    }
  };
  window.addEventListener('keydown', handleKeydown);

  return backdrop;
}
