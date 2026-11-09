/**
 * guidanceArrow.js — Floating World and Edge Directional Arrows (Rule 82 §4.2).
 * Shows an animated pixel arrow above targets or snapped to screen perimeter with distance.
 */

export class GuidanceArrowManager {
  /**
   * @param {Phaser.Scene} scene
   * @param {object} tutorialManager
   */
  constructor(scene, tutorialManager) {
    this.scene = scene;
    this.tutorialManager = tutorialManager;

    // World arrow container
    this.worldContainer = scene.add.container(0, 0);
    this.worldContainer.setDepth(2000);
    this.worldContainer.setVisible(false);

    // Create pixel arrow graphics (mustard triangle pointing down)
    const arrowGfx = scene.add.graphics();
    // Border
    arrowGfx.fillStyle(0x121A2E, 1);
    arrowGfx.beginPath();
    arrowGfx.moveTo(-14, -28);
    arrowGfx.lineTo(14, -28);
    arrowGfx.lineTo(0, -6);
    arrowGfx.closePath();
    arrowGfx.fillPath();

    // Fill
    arrowGfx.fillStyle(0xD9A441, 1);
    arrowGfx.beginPath();
    arrowGfx.moveTo(-10, -25);
    arrowGfx.lineTo(10, -25);
    arrowGfx.lineTo(0, -10);
    arrowGfx.closePath();
    arrowGfx.fillPath();

    this.worldContainer.add(arrowGfx);

    // Floating bounce tween
    this.scene.tweens.add({
      targets: arrowGfx,
      y: -8,
      duration: 500,
      yoyo: true,
      repeat: -1,
      ease: 'Sine.easeInOut'
    });

    // Edge UI indicator in DOM
    this._edgeEl = document.createElement('div');
    this._edgeEl.className = 'tutorial-edge-arrow hidden';
    this._edgeEl.innerHTML = `
      <span class="edge-arrow-icon">➤</span>
      <span class="edge-arrow-dist">0m</span>
    `;
    const uiContainer = document.getElementById('ui-container') || document.body;
    uiContainer.appendChild(this._edgeEl);
  }

  destroy() {
    if (this.worldContainer) {
      this.worldContainer.destroy();
    }
    if (this._edgeEl && this._edgeEl.parentNode) {
      this._edgeEl.parentNode.removeChild(this._edgeEl);
    }
  }

  /**
   * Called every frame in World.update
   * @param {string} currentMapId
   */
  update(currentMapId) {
    if (!this.tutorialManager) return;

    const targetInfo = this.tutorialManager.getTargetInfo(currentMapId);
    if (!targetInfo) {
      this.worldContainer.setVisible(false);
      this._edgeEl.classList.add('hidden');
      return;
    }

    const tx = targetInfo.x * 32 + 16;
    const ty = targetInfo.y * 32;

    this.worldContainer.setPosition(tx, ty);
    this.worldContainer.setVisible(true);

    // Check camera viewport visibility
    const cam = this.scene.cameras.main;
    const screenX = tx - cam.scrollX;
    const screenY = ty - cam.scrollY;

    const pad = 40;
    const inView = screenX >= pad && screenX <= (cam.width - pad) &&
                  screenY >= pad && screenY <= (cam.height - pad);

    const player = this.scene._player?.sprite;
    const distPx = player ? Math.hypot(tx - player.x, ty - player.y) : 0;
    const distMeters = Math.max(1, Math.round(distPx / 32));

    if (inView) {
      this._edgeEl.classList.add('hidden');
    } else {
      // Snap to screen perimeter
      this._edgeEl.classList.remove('hidden');

      const cx = cam.width / 2;
      const cy = cam.height / 2;
      const angle = Math.atan2(screenY - cy, screenX - cx);

      const margin = 48;
      const clampedX = Math.max(margin, Math.min(cam.width - margin, cx + Math.cos(angle) * (cx - margin)));
      const clampedY = Math.max(margin, Math.min(cam.height - margin, cy + Math.sin(angle) * (cy - margin)));

      this._edgeEl.style.left = `${clampedX}px`;
      this._edgeEl.style.top = `${clampedY}px`;

      const deg = (angle * 180 / Math.PI);
      const icon = this._edgeEl.querySelector('.edge-arrow-icon');
      if (icon) {
        icon.style.transform = `rotate(${deg}deg)`;
      }
      const distEl = this._edgeEl.querySelector('.edge-arrow-dist');
      if (distEl) {
        distEl.textContent = `${distMeters}m`;
      }
    }
  }
}

