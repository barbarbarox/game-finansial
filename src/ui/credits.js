/**
 * credits.js — Layar Kredit & Lisensi
 * Anti-XSS: textContent only.
 */

export function createCreditsModal(container, onClose) {
  const backdrop = document.createElement('div');
  backdrop.className = 'lj-modal-backdrop';

  const modal = document.createElement('div');
  modal.className = 'lj-panel credits-panel';
  modal.setAttribute('role', 'dialog');
  modal.setAttribute('aria-modal', 'true');

  const header = document.createElement('div');
  header.className = 'panel-header';
  const title = document.createElement('h2');
  title.className = 'panel-title';
  title.textContent = 'Kredit & Atribusi Lisensi';
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
  body.className = 'credits-body';

  fetch('assets/credits.json')
    .then(r => r.json())
    .then(data => {
      const pIntro = document.createElement('p');
      pIntro.textContent = `${data.project} (v${data.version})`;
      body.appendChild(pIntro);

      const hLib = document.createElement('h3');
      hLib.textContent = 'Pustaka & Engine';
      body.appendChild(hLib);

      const ul = document.createElement('ul');
      data.libraries.forEach(lib => {
        const li = document.createElement('li');
        li.textContent = `${lib.name} v${lib.version} — Lisensi ${lib.license} (${lib.url})`;
        ul.appendChild(li);
      });
      body.appendChild(ul);

      const hArt = document.createElement('h3');
      hArt.textContent = 'Aset Visual & Gaya';
      body.appendChild(hArt);

      const pArt = document.createElement('p');
      pArt.textContent = `${data.art.style} · Dihasilkan via ${data.art.generator} melalui ${data.art.pipeline}.`;
      body.appendChild(pArt);
    })
    .catch(() => {
      const err = document.createElement('p');
      err.textContent = 'Gagal memuat informasi kredit.';
      body.appendChild(err);
    });

  modal.appendChild(body);
  backdrop.appendChild(modal);
  container.appendChild(backdrop);
}
