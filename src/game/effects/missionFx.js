/**
 * missionFx.js — Procedural Mission Complete Visual Effects.
 * Complies with Rule 77 (Penanda Misi Selesai dan Efek Visual Prosedural):
 * - Flash cream tint on character (0-80 ms)
 * - Two expanding pixel rings from feet (0-900 ms, mustard -> cream)
 * - 12 pixel stars floating up with jitter (0-900 ms)
 * - Floating text "MISI SELESAI!" + mission title (200-1200 ms, mustard with navy outline)
 * - Idempotent, max queue 3, supports prefers-reduced-motion
 */

export class MissionFxManager {
  /**
   * @param {Phaser.Scene} scene
   */
  constructor(scene) {
    this.scene = scene;
    this.queue = [];
    this.isPlaying = false;
    this.completedMissions = new Set();
  }

  /**
   * Trigger mission complete effect (idempotent).
   * @param {string} missionId
   * @param {string} missionTitle
   * @returns {boolean} true if triggered, false if already completed or queue full
   */
  trigger(missionId, missionTitle = 'Misi Selesai') {
    if (this.completedMissions.has(missionId)) {
      return false;
    }
    this.completedMissions.add(missionId);

    if (this.queue.length >= 3) {
      return false;
    }

    this.queue.push({ id: missionId, title: missionTitle });
    if (!this.isPlaying) {
      this._playNext();
    }
    return true;
  }

  _playNext() {
    if (this.queue.length === 0) {
      this.isPlaying = false;
      return;
    }

    this.isPlaying = true;
    const { id, title } = this.queue.shift();

    // Trigger DOM HUD mission checkmark / shine animation if HUD exists
    this._triggerHudBannerEffect(id, title);

    const player = this.scene._player;
    if (!player || !player.sprite) {
      // If player not ready, finish after delay
      this.scene.time.delayedCall(1200, () => this._playNext());
      return;
    }

    const reducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const px = player.sprite.x;
    const py = player.sprite.y;

    // 1. Flash tint (0 - 80 ms)
    if (!reducedMotion) {
      player.sprite.setTint(0xF7EEDA);
      this.scene.time.delayedCall(80, () => {
        if (player.sprite) player.sprite.clearTint();
      });
    }

    // 2. Rings & Stars (0 - 900 ms)
    if (!reducedMotion) {
      this._spawnPixelRings(px, py);
      this._spawnPixelStars(px, py);
    }

    // 3. Floating Text (200 - 1200 ms)
    this.scene.time.delayedCall(200, () => {
      this._spawnFloatingText(px, py - 40, title);
    });

    // Complete queue step after 1200 ms
    this.scene.time.delayedCall(1200, () => {
      this._playNext();
    });
  }

  _spawnPixelRings(x, y) {
    // Ring 1 (starts immediately)
    this._createSingleRing(x, y, 0, 0xD9A441);
    // Ring 2 (starts at 150 ms)
    this.scene.time.delayedCall(150, () => {
      this._createSingleRing(x, y, 0, 0xF7EEDA);
    });
  }

  _createSingleRing(x, y, initialRadius, color) {
    const ring = this.scene.add.graphics();
    ring.setDepth(6000);

    const state = { radius: initialRadius, alpha: 1.0 };
    this.scene.tweens.add({
      targets: state,
      radius: 36,
      alpha: 0,
      duration: 750,
      ease: 'Cubic.easeOut',
      onUpdate: () => {
        ring.clear();
        ring.lineStyle(3, color, state.alpha);
        // Chunky pixel ring (diamond/square)
        ring.strokeRect(x - state.radius, y - state.radius * 0.5, state.radius * 2, state.radius);
      },
      onComplete: () => {
        ring.destroy();
      }
    });
  }

  _spawnPixelStars(x, y) {
    const starCount = 12;
    const colors = [0xD9A441, 0xF7EEDA, 0xC9A27A];

    for (let i = 0; i < starCount; i++) {
      const delay = Math.random() * 200;
      const size = Math.random() > 0.5 ? 6 : 4;
      const col = colors[Math.floor(Math.random() * colors.length)];
      const targetX = x + (Math.random() * 40 - 20);
      const targetY = y - 20 - Math.random() * 40;

      this.scene.time.delayedCall(delay, () => {
        const star = this.scene.add.rectangle(x + (Math.random() * 16 - 8), y, size, size, col);
        star.setDepth(6001);

        this.scene.tweens.add({
          targets: star,
          x: targetX,
          y: targetY,
          alpha: { from: 1.0, to: 0 },
          scale: { from: 1.0, to: 0.3 },
          duration: 650,
          ease: 'Quad.easeOut',
          onComplete: () => star.destroy()
        });
      });
    }
  }

  _spawnFloatingText(x, y, title) {
    const container = this.scene.add.container(x, y);
    container.setDepth(6002);

    const titleText = this.scene.add.text(0, -14, 'MISI SELESAI!', {
      fontFamily: 'monospace',
      fontSize: '14px',
      fontStyle: 'bold',
      color: '#D9A441',
      stroke: '#1F2A44',
      strokeThickness: 3,
      align: 'center'
    }).setOrigin(0.5);

    const descText = this.scene.add.text(0, 4, title, {
      fontFamily: 'sans-serif',
      fontSize: '11px',
      fontStyle: 'bold',
      color: '#F7EEDA',
      stroke: '#121A2E',
      strokeThickness: 2,
      align: 'center'
    }).setOrigin(0.5);

    container.add([titleText, descText]);

    this.scene.tweens.add({
      targets: container,
      y: y - 28,
      alpha: { from: 1.0, to: 0 },
      duration: 1000,
      ease: 'Cubic.easeOut',
      onComplete: () => container.destroy()
    });
  }

  _triggerHudBannerEffect(id, title) {
    const badge = document.querySelector('.hud-mission-badge');
    const titleEl = document.querySelector('.hud-val-mission');
    if (!badge || !titleEl) return;

    badge.classList.add('mission-complete-anim');
    const oldText = titleEl.textContent;
    titleEl.textContent = `✓ ${title || oldText}`;

    setTimeout(() => {
      badge.classList.remove('mission-complete-anim');
    }, 1500);
  }
}
