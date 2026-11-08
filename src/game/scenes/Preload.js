/**
 * Preload.js — Preload scene for Life Journey.
 * Loads all assets and configs, showing an animated loading bar.
 */

import { loadAssets, createPlaceholders } from '../assetLoader.js';

export class Preload extends Phaser.Scene {
  constructor() {
    super({ key: 'Preload' });
  }

  preload() {
    const { width, height } = this.scale;

    // Loading UI
    const barBg = this.add.rectangle(width / 2, height / 2, 400, 24, 0x1F2A44);
    barBg.setOrigin(0.5);

    const bar = this.add.rectangle(width / 2 - 200, height / 2, 0, 20, 0xD9A441);
    bar.setOrigin(0, 0.5);

    const loadText = this.add.text(width / 2, height / 2 - 28, 'Memuat aset Life Journey...', {
      font: '16px sans-serif',
      fill: '#F7EEDA',
    });
    loadText.setOrigin(0.5);

    this.load.on('progress', (value) => {
      bar.width = 400 * value;
    });

    this.load.on('complete', () => {
      loadText.setText('Selesai!');
      bar.width = 400;
    });

    // Load JSON data
    this.load.json('phase1config', 'data/phase1.config.json');
    this.load.json('eventsData', 'data/events.phase1.json');
    this.load.json('activitiesData', 'data/activities.phase1.json');
    this.load.json('mapsIndex', 'data/maps/index.json');
    this.load.json('townLayout', 'data/maps/town_hub.layout.json');
    this.load.json('layout_town_hub', 'data/maps/town_hub.layout.json');
    this.load.json('layout_home', 'data/maps/home.layout.json');
    this.load.json('layout_school', 'data/maps/school.layout.json');
    this.load.json('layout_minimarket', 'data/maps/minimarket.layout.json');
    this.load.json('layout_toko_kosmetik', 'data/maps/toko_kosmetik.layout.json');
    this.load.json('layout_spbu', 'data/maps/spbu.layout.json');
    this.load.json('layout_game_center', 'data/maps/game_center.layout.json');
    this.load.json('credits', 'assets/credits.json');
    this.load.json('palette', 'assets/palette.json');

    // Retrieve asset manifest loaded in Boot scene
    const manifest = this.cache.json.get('assetManifest');
    const assets = manifest?.assets || [];

    // Queue ready assets for loading
    loadAssets(this, assets);
  }

  create() {
    const manifest = this.cache.json.get('assetManifest');
    const assets = manifest?.assets || [];

    // Create canvas textures for any placeholder assets
    createPlaceholders(this, assets);

    // Short delay before transitioning to MainMenu
    this.time.delayedCall(200, () => {
      this.scene.start('MainMenu');
    });
  }
}
