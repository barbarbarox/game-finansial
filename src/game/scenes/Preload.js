/**
 * Preload.js — Preload scene for Life Journey.
 * Loads all assets and shows a loading bar.
 */

import { loadAssets, createPlaceholders } from '../assetLoader.js';

export class Preload extends Phaser.Scene {
  constructor() {
    super({ key: 'Preload' });
  }

  preload() {
    const { width, height } = this.scale;

    // Loading bar background
    const barBg = this.add.rectangle(width / 2, height / 2, 400, 24, 0x34456B);
    barBg.setOrigin(0.5);

    // Loading bar fill
    const bar = this.add.rectangle(width / 2 - 200, height / 2, 0, 20, 0xD9A441);
    bar.setOrigin(0, 0.5);

    // Loading text
    const loadText = this.add.text(width / 2, height / 2 - 24, 'Memuat...', {
      font: '16px sans-serif',
      fill: '#FBF6EA',
    });
    loadText.setOrigin(0.5);

    // Update bar on progress
    this.load.on('progress', (value) => {
      bar.width = 400 * value;
    });

    this.load.on('complete', () => {
      loadText.setText('Selesai!');
      bar.width = 400;
    });

    // Load JSON configs
    this.load.json('phase1config', 'data/phase1.config.json');
    this.load.json('eventsData', 'data/events.phase1.json');
    this.load.json('assetManifest', 'assets/asset-manifest.json');
    this.load.json('townLayout', 'data/maps/town_hub.layout.json');
    this.load.json('credits', 'assets/credits.json');
    this.load.json('palette', 'assets/palette.json');
  }

  create() {
    const manifest = this.cache.json.get('assetManifest');
    const assets = manifest?.assets ?? [];

    // Create placeholder textures for all placeholder assets
    createPlaceholders(this, assets);

    // Load any ready assets (spritesheet setup, etc.)
    // For now all are placeholder; we still register them
    for (const entry of assets) {
      if (entry.status === 'ready') {
        // Would be loaded in preload, placeholder already handled
      }
    }

    // Short delay then go to MainMenu
    this.time.delayedCall(300, () => {
      this.scene.start('MainMenu');
    });
  }
}
