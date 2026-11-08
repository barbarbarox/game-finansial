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

    // Load E4 furniture and portraits
    this.load.image('furn_kasur_single', 'assets/furniture/kamar_pemain/furn_kasur_single.png');
    this.load.image('furn_meja_belajar', 'assets/furniture/kamar_pemain/furn_meja_belajar.png');
    this.load.image('furn_kursi_belajar', 'assets/furniture/kamar_pemain/furn_kursi_belajar.png');
    this.load.image('furn_lemari_pakaian', 'assets/furniture/kamar_pemain/furn_lemari_pakaian.png');
    this.load.image('furn_rak_buku', 'assets/furniture/kamar_pemain/furn_rak_buku.png');
    this.load.image('furn_nakas_lampu', 'assets/furniture/kamar_pemain/furn_nakas_lampu.png');
    this.load.image('portrait_player_m', 'assets/portraits/portrait_player_m.png');
    this.load.image('portrait_player_f', 'assets/portraits/portrait_player_f.png');

    // Individual NPC Sprites
    this.load.image('npc_ibu', 'assets/npcs/npc_ibu.png');
    this.load.image('npc_ayah', 'assets/npcs/npc_ayah.png');
    this.load.image('npc_budi', 'assets/npcs/npc_budi.png');
    this.load.image('npc_siti', 'assets/npcs/npc_siti.png');
    this.load.image('npc_penjual_kantin', 'assets/npcs/npc_penjual_kantin.png');
    this.load.image('npc_kasir_minimarket', 'assets/npcs/npc_kasir_minimarket.png');
    this.load.image('npc_penjaga_kosmetik', 'assets/npcs/npc_penjaga_kosmetik.png');
    this.load.image('npc_petugas_spbu', 'assets/npcs/npc_petugas_spbu.png');
    this.load.image('npc_penjaga_game', 'assets/npcs/npc_penjaga_game.png');

    // Dialogue Portraits
    this.load.image('portrait_ibu', 'assets/portraits/portrait_ibu.png');
    this.load.image('portrait_ayah', 'assets/portraits/portrait_ayah.png');
    this.load.image('portrait_teman_l', 'assets/portraits/portrait_teman_l.png');
    this.load.image('portrait_teman_p', 'assets/portraits/portrait_teman_p.png');
    this.load.image('portrait_penjual_kantin', 'assets/portraits/portrait_penjual_kantin.png');
    this.load.image('portrait_kasir_minimarket', 'assets/portraits/portrait_kasir_minimarket.png');
    this.load.image('portrait_penjaga_kosmetik', 'assets/portraits/portrait_penjaga_kosmetik.png');
    this.load.image('portrait_petugas_spbu', 'assets/portraits/portrait_petugas_spbu.png');
    this.load.image('portrait_penjaga_game', 'assets/portraits/portrait_penjaga_game.png');

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
