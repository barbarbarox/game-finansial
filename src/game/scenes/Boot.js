/**
 * Boot.js — Boot scene for Life Journey.
 * Checks LocalStorage availability, then starts Preload.
 */

export class Boot extends Phaser.Scene {
  constructor() {
    super({ key: 'Boot' });
  }

  preload() {
    // Load meta.json for game title
    this.load.json('meta', 'data/meta.json');
  }

  create() {
    // Check LocalStorage
    let storageOk = false;
    try {
      const testKey = '__lj_test__';
      localStorage.setItem(testKey, '1');
      localStorage.removeItem(testKey);
      storageOk = true;
    } catch (e) {
      console.warn('[Boot] LocalStorage tidak tersedia:', e);
    }

    if (!storageOk) {
      // Show warning but continue
      const { width, height } = this.scale;
      this.add.rectangle(width / 2, height / 2, width, 60, 0xC0654A)
        .setOrigin(0.5);
      const warn = this.add.text(width / 2, height / 2,
        'Peringatan: Penyimpanan tidak tersedia. Progres tidak akan disimpan.',
        { font: '14px sans-serif', fill: '#FBF6EA' }
      );
      warn.setOrigin(0.5);
    }

    this.game.registry.set('storageOk', storageOk);

    // Brief delay then start Preload
    this.time.delayedCall(200, () => {
      this.scene.start('Preload');
    });
  }
}
