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
    this.load.json('itemsData', 'data/items.phase1.json');
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

    // Home Furniture (Living Room, Kitchen, Bedrooms, Bathroom)
    this.load.image('furn_kasur_besar', 'assets/furniture/home/furn_kasur_besar.png');
    this.load.image('furn_lemari_besar', 'assets/furniture/home/furn_lemari_besar.png');
    this.load.image('furn_meja_rias', 'assets/furniture/home/furn_meja_rias.png');
    this.load.image('furn_kipas_berdiri', 'assets/furniture/home/furn_kipas_berdiri.png');
    this.load.image('furn_sofa_3dudukan', 'assets/furniture/home/furn_sofa_3dudukan.png');
    this.load.image('furn_sofa_single', 'assets/furniture/home/furn_sofa_single.png');
    this.load.image('furn_meja_tamu', 'assets/furniture/home/furn_meja_tamu.png');
    this.load.image('furn_tv_dan_rak', 'assets/furniture/home/furn_tv_dan_rak.png');
    this.load.image('furn_rak_pajangan', 'assets/furniture/home/furn_rak_pajangan.png');
    this.load.image('furn_karpet_tamu', 'assets/furniture/home/furn_karpet_tamu.png');
    this.load.image('furn_kompor_counter', 'assets/furniture/home/furn_kompor_counter.png');
    this.load.image('furn_kulkas', 'assets/furniture/home/furn_kulkas.png');
    this.load.image('furn_meja_makan', 'assets/furniture/home/furn_meja_makan.png');
    this.load.image('furn_kursi_makan', 'assets/furniture/home/furn_kursi_makan.png');
    this.load.image('furn_rak_piring', 'assets/furniture/home/furn_rak_piring.png');
    this.load.image('furn_wastafel_dapur', 'assets/furniture/home/furn_wastafel_dapur.png');
    this.load.image('furn_bak_mandi', 'assets/furniture/home/furn_bak_mandi.png');
    this.load.image('furn_toilet', 'assets/furniture/home/furn_toilet.png');
    this.load.image('furn_wastafel_cermin', 'assets/furniture/home/furn_wastafel_cermin.png');
    this.load.image('furn_rak_handuk', 'assets/furniture/home/furn_rak_handuk.png');
    this.load.image('furn_ember', 'assets/furniture/home/furn_ember.png');
    this.load.image('furn_pintu_kamar', 'assets/furniture/home/furn_pintu_kamar.png');
    this.load.image('furn_pintu_depan', 'assets/furniture/home/furn_pintu_depan.png');
    this.load.image('furn_jendela', 'assets/furniture/home/furn_jendela.png');
    this.load.image('furn_jam_dinding', 'assets/furniture/home/furn_jam_dinding.png');
    this.load.image('furn_bingkai_kosong', 'assets/furniture/home/furn_bingkai_kosong.png');

    // School Furniture
    this.load.image('furn_meja_siswa_kursi', 'assets/furniture/school/furn_meja_siswa_kursi.png');
    this.load.image('furn_meja_guru', 'assets/furniture/school/furn_meja_guru.png');
    this.load.image('furn_papan_tulis', 'assets/furniture/school/furn_papan_tulis.png');
    this.load.image('furn_lemari_kelas', 'assets/furniture/school/furn_lemari_kelas.png');
    this.load.image('furn_tempat_sampah_kelas', 'assets/furniture/school/furn_tempat_sampah_kelas.png');
    this.load.image('furn_counter_kantin', 'assets/furniture/school/furn_counter_kantin.png');
    this.load.image('furn_meja_kantin', 'assets/furniture/school/furn_meja_kantin.png');
    this.load.image('furn_bangku_kantin', 'assets/furniture/school/furn_bangku_kantin.png');
    this.load.image('furn_kulkas_minuman', 'assets/furniture/school/furn_kulkas_minuman.png');
    this.load.image('furn_dispenser_galon', 'assets/furniture/school/furn_dispenser_galon.png');
    this.load.image('furn_rak_snack', 'assets/furniture/school/furn_rak_snack.png');
    this.load.image('furn_rak_buku_perpus', 'assets/furniture/school/furn_rak_buku_perpus.png');
    this.load.image('furn_meja_baca', 'assets/furniture/school/furn_meja_baca.png');
    this.load.image('furn_bangku_tunggu', 'assets/furniture/school/furn_bangku_tunggu.png');
    this.load.image('furn_papan_pengumuman', 'assets/furniture/school/furn_papan_pengumuman.png');
    this.load.image('furn_vas_tanaman', 'assets/furniture/school/furn_vas_tanaman.png');
    this.load.image('furn_poster_kosong', 'assets/furniture/school/furn_poster_kosong.png');

    // Minimarket Furniture
    this.load.image('furn_kasir_counter', 'assets/furniture/minimarket/furn_kasir_counter.png');
    this.load.image('furn_rak_gondola', 'assets/furniture/minimarket/furn_rak_gondola.png');
    this.load.image('furn_kulkas_minuman_besar', 'assets/furniture/minimarket/furn_kulkas_minuman_besar.png');
    this.load.image('furn_rak_alat_tulis', 'assets/furniture/minimarket/furn_rak_alat_tulis.png');
    this.load.image('furn_mesin_fotokopi', 'assets/furniture/minimarket/furn_mesin_fotokopi.png');
    this.load.image('furn_keranjang_belanja', 'assets/furniture/minimarket/furn_keranjang_belanja.png');

    // Cosmetics Furniture
    this.load.image('furn_etalase_kaca', 'assets/furniture/kosmetik/furn_etalase_kaca.png');
    this.load.image('furn_kasir_kecil', 'assets/furniture/kosmetik/furn_kasir_kecil.png');
    this.load.image('furn_meja_cermin', 'assets/furniture/kosmetik/furn_meja_cermin.png');
    this.load.image('furn_rak_dinding_kosmetik', 'assets/furniture/kosmetik/furn_rak_dinding_kosmetik.png');
    this.load.image('furn_kursi_tunggu', 'assets/furniture/kosmetik/furn_kursi_tunggu.png');

    // SPBU Furniture
    this.load.image('furn_dispenser_bbm', 'assets/furniture/spbu/furn_dispenser_bbm.png');
    this.load.image('furn_kiosk_spbu', 'assets/furniture/spbu/furn_kiosk_spbu.png');
    this.load.image('furn_rak_oli', 'assets/furniture/spbu/furn_rak_oli.png');
    this.load.image('furn_bangku_spbu', 'assets/furniture/spbu/furn_bangku_spbu.png');

    // Game Center Furniture
    this.load.image('furn_arcade_a', 'assets/furniture/game_center/furn_arcade_a.png');
    this.load.image('furn_arcade_b', 'assets/furniture/game_center/furn_arcade_b.png');
    this.load.image('furn_counter_kafe', 'assets/furniture/game_center/furn_counter_kafe.png');
    this.load.image('furn_meja_kafe', 'assets/furniture/game_center/furn_meja_kafe.png');
    this.load.image('furn_kursi_kafe', 'assets/furniture/game_center/furn_kursi_kafe.png');
    this.load.image('furn_tv_besar', 'assets/furniture/game_center/furn_tv_besar.png');

    // 16 Consumable Item Icons (AI-Generated Pixel Art)
    this.load.image('item_air_mineral', 'assets/items/item_air_mineral.png');
    this.load.image('item_teh_kemasan', 'assets/items/item_teh_kemasan.png');
    this.load.image('item_jus_kotak', 'assets/items/item_jus_kotak.png');
    this.load.image('item_susu_kotak', 'assets/items/item_susu_kotak.png');
    this.load.image('item_isotonik', 'assets/items/item_isotonik.png');
    this.load.image('item_pisang', 'assets/items/item_pisang.png');
    this.load.image('item_roti_isi', 'assets/items/item_roti_isi.png');
    this.load.image('item_keripik', 'assets/items/item_keripik.png');
    this.load.image('item_coklat_batang', 'assets/items/item_coklat_batang.png');
    this.load.image('item_gorengan', 'assets/items/item_gorengan.png');
    this.load.image('item_mie_cup', 'assets/items/item_mie_cup.png');
    this.load.image('item_es_teh', 'assets/items/item_es_teh.png');
    this.load.image('item_nasi_kuning', 'assets/items/item_nasi_kuning.png');
    this.load.image('item_nasi_goreng', 'assets/items/item_nasi_goreng.png');
    this.load.image('item_mie_goreng', 'assets/items/item_mie_goreng.png');
    this.load.image('item_bakso', 'assets/items/item_bakso.png');

    this.load.image('portrait_player_m', 'assets/portraits/portrait_player_m.png');
    this.load.image('portrait_player_f', 'assets/portraits/portrait_player_f.png');
    this.load.spritesheet('char_rider_m', 'assets/characters/char_rider_m.png', { frameWidth: 48, frameHeight: 64 });
    this.load.spritesheet('char_rider_f', 'assets/characters/char_rider_f.png', { frameWidth: 48, frameHeight: 64 });
    this.load.image('icon_motor', 'assets/icons/icon_motor.png');
    this.load.image('prop_motor_parkir', 'assets/furniture/props/prop_motor_parkir.png');

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

    // Short delay before transitioning
    this.time.delayedCall(200, () => {
      const urlParams = new URLSearchParams(window.location.search);
      const targetScene = urlParams.get('scene');
      const targetMap = urlParams.get('map') || 'home';
      const targetSpawn = urlParams.get('spawn') || 'default';

      if (targetScene === 'World') {
        this.scene.start('World', { mapId: targetMap, spawnTarget: targetSpawn });
      } else {
        this.scene.start('MainMenu');
      }
    });
  }
}
