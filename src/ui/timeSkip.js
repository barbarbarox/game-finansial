/**
 * timeSkip.js — Time-Skip Overlay for activities & transitions.
 * Complies with Rule 72 (Time System & Activities §5).
 */

let overlayContainer = null;

function ensureContainer() {
  if (!overlayContainer) {
    overlayContainer = document.createElement('div');
    overlayContainer.id = 'timeskip-overlay';
    overlayContainer.className = 'timeskip-overlay hidden';
    overlayContainer.setAttribute('role', 'dialog');
    overlayContainer.setAttribute('aria-modal', 'true');
    overlayContainer.setAttribute('aria-live', 'polite');
    document.body.appendChild(overlayContainer);
  }
  return overlayContainer;
}

/**
 * Show a clean, themed Time-Skip overlay while advancing game time.
 * @param {object} options
 * @param {string} options.title - Nama aktivitas (contoh: "Belajar di Kelas")
 * @param {number} options.minutes - Menit yang berlalu
 * @param {string} [options.costText] - Keterangan biaya jika ada (contoh: "-Rp15.000")
 * @param {string} [options.icon] - Path icon aktivitas
 * @param {function} [options.onComplete] - Callback saat overlay selesai
 * @param {number} [options.displayDurationMs=1000] - Durasi tampilan animasi overlay
 * @returns {Promise<void>}
 */
export function showTimeSkip(options) {
  const {
    title,
    minutes,
    costText = null,
    icon = 'assets/icons/icon_jam.png',
    onComplete = null,
    displayDurationMs = 900
  } = options;

  return new Promise((resolve) => {
    const container = ensureContainer();
    container.innerHTML = '';

    const card = document.createElement('div');
    card.className = 'timeskip-card';

    const iconImg = document.createElement('img');
    iconImg.src = icon;
    iconImg.alt = '';
    iconImg.className = 'timeskip-icon';

    const heading = document.createElement('h3');
    heading.className = 'timeskip-title';
    heading.textContent = title;

    const timeInfo = document.createElement('div');
    timeInfo.className = 'timeskip-time';
    timeInfo.textContent = `+${minutes} Menit Berlalu...`;

    card.appendChild(iconImg);
    card.appendChild(heading);
    card.appendChild(timeInfo);

    if (costText) {
      const costBadge = document.createElement('div');
      costBadge.className = 'timeskip-cost';
      costBadge.textContent = costText;
      card.appendChild(costBadge);
    }

    const progressBar = document.createElement('div');
    progressBar.className = 'timeskip-progress-bar';
    const progressFill = document.createElement('div');
    progressFill.className = 'timeskip-progress-fill';
    progressBar.appendChild(progressFill);
    card.appendChild(progressBar);

    container.appendChild(card);
    container.classList.remove('hidden');
    container.classList.add('visible');

    // Trigger CSS animation for fill
    requestAnimationFrame(() => {
      progressFill.style.width = '100%';
    });

    let completed = false;
    const finish = () => {
      if (completed) return;
      completed = true;
      container.classList.remove('visible');
      container.classList.add('hidden');
      if (onComplete) onComplete();
      resolve();
    };

    // Fast-skip on click/key
    const skipListener = (e) => {
      if (e.type === 'click' || e.key === ' ' || e.key === 'Enter' || e.key === 'Escape') {
        window.removeEventListener('keydown', skipListener);
        container.removeEventListener('click', skipListener);
        finish();
      }
    };
    window.addEventListener('keydown', skipListener);
    container.addEventListener('click', skipListener);

    setTimeout(() => {
      window.removeEventListener('keydown', skipListener);
      container.removeEventListener('click', skipListener);
      finish();
    }, displayDurationMs);
  });
}
