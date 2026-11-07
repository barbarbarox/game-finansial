/**
 * npcDialog.js — Dialog Interaksi NPC untuk Life Journey
 * Mengimplementasikan sistem dialog interaktif saat player mendekat ke NPC:
 * - Menampilkan nama & inisial avatar NPC
 * - Balon teks pesan dari NPC
 * - Opsi respon/pilihan interaksi dari pemain
 * - Reaksi dinamis berdasarkan balasan pilihan (choice.reply)
 * - Anti-XSS: textContent only.
 */

let activeDialogBackdrop = null;

export function isNPCDialogOpen() {
  return activeDialogBackdrop !== null;
}

export function closeNPCDialog() {
  if (activeDialogBackdrop) {
    activeDialogBackdrop.remove();
    activeDialogBackdrop = null;
  }
}

/**
 * @param {HTMLElement} container
 * @param {object} npcData - { id, name, role, dialog, choices }
 * @param {function} onChoiceSelect - callback(choiceId)
 * @param {function} onClose - callback()
 */
export function createNPCDialog(container, npcData, onChoiceSelect, onClose) {
  // Tutup dialog lama bila masih ada
  closeNPCDialog();

  const backdrop = document.createElement('div');
  backdrop.className = 'lj-npc-dialog-backdrop';
  activeDialogBackdrop = backdrop;

  const dialog = document.createElement('div');
  dialog.className = 'lj-npc-dialog';
  dialog.setAttribute('role', 'dialog');
  dialog.setAttribute('aria-modal', 'true');
  dialog.setAttribute('aria-label', `Dialog dengan ${npcData.name || 'NPC'}`);

  // Header: Avatar + Nama + Role
  const header = document.createElement('div');
  header.className = 'npc-dialog-header';

  const avatar = document.createElement('div');
  avatar.className = 'npc-avatar';
  const initial = (npcData.name || 'N').charAt(0).toUpperCase();
  avatar.textContent = initial;

  const meta = document.createElement('div');
  meta.className = 'npc-meta';
  const nameEl = document.createElement('div');
  nameEl.className = 'npc-name';
  nameEl.textContent = npcData.name || 'Warga';
  const titleEl = document.createElement('div');
  titleEl.className = 'npc-title';
  titleEl.textContent = npcData.role || 'Penduduk Kota';
  meta.appendChild(nameEl);
  meta.appendChild(titleEl);

  const closeBtn = document.createElement('button');
  closeBtn.type = 'button';
  closeBtn.className = 'btn-close';
  closeBtn.textContent = '✕';
  closeBtn.setAttribute('aria-label', 'Tutup Dialog');
  closeBtn.addEventListener('click', () => {
    closeNPCDialog();
    if (onClose) onClose();
  });

  header.appendChild(avatar);
  header.appendChild(meta);
  header.appendChild(closeBtn);

  // Body: Pesan NPC
  const body = document.createElement('div');
  body.className = 'npc-dialog-body';
  body.textContent = npcData.dialog || 'Halo! Semoga harimu menyenangkan.';

  // Choices: Pilihan respon pemain
  const choicesContainer = document.createElement('div');
  choicesContainer.className = 'npc-choices';

  const choices = (npcData.choices && npcData.choices.length > 0) ? npcData.choices : [
    { id: 'greet', label: '👋 "Halo, senang bertemu!"', reply: 'Senang bertemu denganmu juga! Tetap semangat menjalani hari ini.' },
    { id: 'advice', label: '💡 "Ada nasihat keuangan untuk hari ini?"', reply: 'Selalu sisihkan uang saku ke tabungan di awal, bukan menunggu sisa di akhir bulan!' },
    { id: 'bye', label: '🚶 "Saya harus jalan dulu."', reply: 'Hati-hati di jalan ya! Sampai jumpa lagi.' }
  ];

  choices.forEach(choice => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'npc-choice-btn';

    const lbl = document.createElement('span');
    lbl.textContent = choice.label;

    const arrow = document.createElement('span');
    arrow.textContent = '➔';
    arrow.style.color = 'var(--color-accent)';

    btn.appendChild(lbl);
    btn.appendChild(arrow);

    btn.addEventListener('click', () => {
      // Tampilkan balasan NPC
      if (choice.reply) {
        body.textContent = choice.reply;
      } else {
        handleChoiceResponse(body, choice.id, npcData);
      }

      if (onChoiceSelect) onChoiceSelect(choice.id);

      // Event global
      document.dispatchEvent(new CustomEvent('lj:npcChoice', {
        detail: { npcId: npcData.id, choiceId: choice.id }
      }));

      // Jika pilihan adalah pamit/bye/tutup, tutup dialog setelah delay singkat
      if (choice.id === 'bye' || choice.id === 'close') {
        setTimeout(() => {
          closeNPCDialog();
          if (onClose) onClose();
        }, 700);
      }
    });

    choicesContainer.appendChild(btn);
  });

  dialog.appendChild(header);
  dialog.appendChild(body);
  dialog.appendChild(choicesContainer);
  backdrop.appendChild(dialog);
  container.appendChild(backdrop);

  // Keyboard shortcut [Esc] untuk menutup
  const handleKeydown = (e) => {
    if (e.key === 'Escape') {
      closeNPCDialog();
      if (onClose) onClose();
      window.removeEventListener('keydown', handleKeydown);
    }
  };
  window.addEventListener('keydown', handleKeydown);

  return backdrop;
}

function handleChoiceResponse(bodyElement, choiceId, npcData) {
  if (choiceId === 'greet') {
    bodyElement.textContent = `Senang bertemu denganmu juga! Tetap semangat ya.`;
  } else if (choiceId === 'advice') {
    const tips = [
      'Selalu sisihkan uang saku ke tabungan di awal, bukan sisa belanja di akhir.',
      'Periksa buku kasmu tiap malam untuk tahu ke mana uangmu mengalir.',
      'Bedakan antara kebutuhan pokok (makan, bensin) dengan hiburan/keinginan semata.',
      'Isi bensin sebelum kritis agar tidak menghambat perjalananmu!'
    ];
    const picked = tips[Math.floor(Math.random() * tips.length)];
    bodyElement.textContent = `💡 Tips dari ${npcData.name || 'Warga'}: "${picked}"`;
  } else if (choiceId === 'bye') {
    bodyElement.textContent = `Sampai jumpa lagi! Hati-hati di jalan.`;
  }
}
