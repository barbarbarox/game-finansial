/**
 * Boot.js — Boot scene for Life Journey.
 * Checks LocalStorage availability and preloads meta + manifest so Preload scene can queue assets.
 */

export class Boot extends Phaser.Scene {
  constructor() {
    super({ key: 'Boot' });
  }

  preload() {
    // Load meta.json and assetManifest early so Preload scene has them
    this.load.json('meta', 'data/meta.json');
    this.load.json('assetManifest', 'assets/asset-manifest.json');
  }

  create() {
    let storageOk = false;
    try {
      const testKey = '__lj_test__';
      localStorage.setItem(testKey, '1');
      localStorage.removeItem(testKey);
      storageOk = true;
    } catch (e) {
      console.warn('[Boot] LocalStorage tidak tersedia:', e);
    }

    this.game.registry.set('storageOk', storageOk);
    this.scene.start('Preload');
  }
}
