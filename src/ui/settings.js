/**
 * settings.js — Menu Pengaturan & Catatan Privasi
 * Anti-XSS: textContent only.
 */

import { resetSave } from '../state/persistence.js';

export function createSettingsModal(container, onClose, onOpenCredits) {
  const backdrop = document.createElement('div');
  backdrop.className = 'lj-modal-backdrop';

  const modal = document.createElement('div');
  modal.className = 'lj-panel settings-panel';
  modal.setAttribute('role', 'dialog');
  modal.setAttribute('aria-modal', 'true');

  const header = document.createElement('div');
  header.className = 'panel-header';
  const title = document.createElement('h2');
  title.className = 'panel-title';
  title.textContent = 'Pengaturan Permainan';
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

  const body = document.createElement('div');
  body.className = 'settings-body';

  // Privacy notice
  const privacyTitle = document.createElement('h3');
  privacyTitle.textContent = 'Catatan Privasi';
  const privacyText = document.createElement('p');
  privacyText.textContent = 'Seluruh data permainan (nama karakter, pilihan, riwayat keuangan) disimpan sepenuhnya secara lokal di browser Anda (LocalStorage) dan tidak pernah dikirimkan ke server eksternal.';

  body.appendChild(privacyTitle);
  body.appendChild(privacyText);

  // Actions
  const btnGroup = document.createElement('div');
  btnGroup.className = 'settings-actions';

  const creditsBtn = document.createElement('button');
  creditsBtn.type = 'button';
  creditsBtn.className = 'btn btn-secondary';
  creditsBtn.textContent = 'Kredit & Lisensi';
  creditsBtn.addEventListener('click', () => {
    backdrop.remove();
    if (onOpenCredits) onOpenCredits();
  });

  const resetBtn = document.createElement('button');
  resetBtn.type = 'button';
  resetBtn.className = 'btn btn-negative';
  resetBtn.textContent = 'Hapus Progres (Reset)';
  resetBtn.addEventListener('click', () => {
    if (confirm('Apakah Anda yakin ingin menghapus semua progres permainan? Tindakan ini tidak dapat dibatalkan.')) {
      resetSave();
      window.location.reload();
    }
  });

  btnGroup.appendChild(creditsBtn);
  btnGroup.appendChild(resetBtn);
  body.appendChild(btnGroup);

  modal.appendChild(body);
  backdrop.appendChild(modal);
  container.appendChild(backdrop);
}

