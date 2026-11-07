/**
 * MainMenu.js — Main menu scene for Life Journey.
 * Fitur:
 * - Visual retro RPG estetis dengan latar kota, bangunan sekolah & rumah, serta karakter SMA.
 * - Tombol Mulai Baru, Lanjutkan, dan Pengaturan yang responsif dan interaktif.
 * - Keyboard navigation (Up/Down/Enter/Space) dan pointer hover/click tanpa bug hitArea.
 * - Anti-XSS & Offline-first.
 */

import { hasValidSave, loadGame } from '../../state/persistence.js';
import { createStore } from '../../state/store.js';

export class MainMenu extends Phaser.Scene {
  constructor() {
    super({ key: 'MainMenu' });
    this._buttons = [];
    this._selectedIndex = 0;
    this._cursor = null;
  }

  create() {
    const { width, height } = this.scale;
    this._buttons = [];
    this._selectedIndex = 0;

    const meta = this.cache.json.get('meta') || {
      gameTitle: 'Life Journey',
      subtitle: 'Simulasi Kehidupan Finansial Siswa SMA',
      version: '0.1.0-prototype'
    };

    // 1. LATAR BELAKANG KOTA ESTETIS (Sky, Road, Buildings, Props, Characters)
    this._createScenicBackground(width, height);

    // 2. HEADER BANNER TITLE CARD
    this._createTitleBanner(width, height, meta);

    // 3. PANEL TOMBOL MENU UTAMA
    this._createMenuPanel(width, height);

    // 4. FOOTER VERSION
    const versionText = this.add.text(width - 16, height - 14, `v${meta.version || '0.1.0-prototype'} · Life Journey`, {
      font: '11px sans-serif',
      fill: '#B8A88A',
    }).setOrigin(1, 1).setDepth(20);

    // 5. KEYBOARD NAVIGATION
    this.input.keyboard.on('keydown-UP', () => this._moveCursor(-1));
    this.input.keyboard.on('keydown-W', () => this._moveCursor(-1));
    this.input.keyboard.on('keydown-DOWN', () => this._moveCursor(1));
    this.input.keyboard.on('keydown-S', () => this._moveCursor(1));
    this.input.keyboard.on('keydown-ENTER', () => this._activateSelected());
    this.input.keyboard.on('keydown-SPACE', () => this._activateSelected());
  }

  _createScenicBackground(width, height) {
    // Sky gradient (Midnight navy -> Warm dusk horizon)
    const sky = this.add.graphics();
    sky.fillGradientStyle(0x0F172A, 0x0F172A, 0x2A1F36, 0x382D42, 1);
    sky.fillRect(0, 0, width, height);

    // Ambient stars in sky
    const stars = this.add.graphics();
    stars.fillStyle(0xF7EEDA, 0.4);
    const starCoords = [
      [60, 40], [140, 70], [240, 30], [350, 60], [620, 45],
      [730, 80], [840, 35], [910, 65], [180, 110], [800, 120]
    ];
    for (const [sx, sy] of starCoords) {
      stars.fillRect(sx, sy, 2, 2);
    }

    // Ground: Sidewalk curb & Road asphalt
    const ground = this.add.graphics();
    // Sidewalk layer (y: 400 - 450)
    ground.fillStyle(0x28344F, 1);
    ground.fillRect(0, 400, width, 50);
    ground.fillStyle(0x34456B, 1);
    ground.fillRect(0, 400, width, 3); // Curb line

    // Road layer (y: 450 - 540)
    ground.fillStyle(0x162038, 1);
    ground.fillRect(0, 450, width, 90);
    // Road dashed stripes
    ground.fillStyle(0xD9A441, 0.7);
    for (let rx = 20; rx < width; rx += 60) {
      ground.fillRect(rx, 492, 36, 4);
    }

    // Background Buildings
    const groundY = 405;

    // Sekolah di sisi kiri
    if (this.textures.exists('bld_sekolah')) {
      const bldSekolah = this.add.image(130, groundY, 'bld_sekolah')
        .setOrigin(0.5, 1.0)
        .setScale(0.82)
        .setAlpha(0.9)
        .setDepth(2);
    }

    // Rumah Pemain di sisi kanan
    if (this.textures.exists('bld_rumah_pemain')) {
      const bldRumah = this.add.image(835, groundY, 'bld_rumah_pemain')
        .setOrigin(0.5, 1.0)
        .setScale(0.85)
        .setAlpha(0.9)
        .setDepth(2);
    }

    // Pepohonan dekoratif
    if (this.textures.exists('prop_tree_large')) {
      this.add.image(285, groundY, 'prop_tree_large').setOrigin(0.5, 1.0).setDepth(3);
      this.add.image(690, groundY, 'prop_tree_large').setOrigin(0.5, 1.0).setDepth(3);
    }
    if (this.textures.exists('prop_tree_small')) {
      this.add.image(35, groundY, 'prop_tree_small').setOrigin(0.5, 1.0).setDepth(3);
      this.add.image(925, groundY, 'prop_tree_small').setOrigin(0.5, 1.0).setDepth(3);
    }

    // Lampu jalan dengan pendaran cahaya hangat
    if (this.textures.exists('prop_street_lamp')) {
      const lampLeft = this.add.image(45, groundY, 'prop_street_lamp').setOrigin(0.5, 1.0).setDepth(4);
      const lampRight = this.add.image(915, groundY, 'prop_street_lamp').setOrigin(0.5, 1.0).setDepth(4);

      // Light glow
      const glow = this.add.graphics().setDepth(3);
      glow.fillStyle(0xFDF6B2, 0.12);
      glow.fillCircle(45, groundY - 45, 36);
      glow.fillCircle(915, groundY - 45, 36);
    }

    // Karakter Siswa SMA (Budi & Siswi) berdiri di trotoar
    if (this.textures.exists('char_player_m_casual')) {
      const charM = this.add.sprite(220, groundY + 24, 'char_player_m_casual', 0)
        .setOrigin(0.5, 1.0)
        .setScale(1.25)
        .setDepth(5);

      // Subtle breathing idle animation
      this.tweens.add({
        targets: charM,
        y: groundY + 21,
        duration: 1200,
        yoyo: true,
        repeat: -1,
        ease: 'Sine.easeInOut'
      });
    }

    if (this.textures.exists('char_player_f_casual')) {
      const charF = this.add.sprite(750, groundY + 24, 'char_player_f_casual', 0)
        .setOrigin(0.5, 1.0)
        .setScale(1.25)
        .setDepth(5);

      this.tweens.add({
        targets: charF,
        y: groundY + 21,
        duration: 1300,
        yoyo: true,
        repeat: -1,
        ease: 'Sine.easeInOut',
        delay: 200
      });
    }
  }

  _createTitleBanner(width, height, meta) {
    const bannerX = width / 2;
    const bannerY = 82;
    const bannerW = 540;
    const bannerH = 100;

    // Outer card
    const bannerBg = this.add.rectangle(bannerX, bannerY, bannerW, bannerH, 0x121A2E, 0.94)
      .setOrigin(0.5)
      .setStrokeStyle(2, 0xD9A441, 1)
      .setDepth(10);

    // Top Category Tag
    const tag = this.add.text(bannerX, bannerY - 32, 'SIMULASI LITERASI FINANSIAL SISWA SMA', {
      font: 'bold 11px sans-serif',
      fill: '#D9A441',
      letterSpacing: 1
    }).setOrigin(0.5).setDepth(11);

    // Main Title
    const titleText = this.add.text(bannerX, bannerY - 4, meta.gameTitle || 'Life Journey', {
      font: 'bold 36px sans-serif',
      fill: '#F7EEDA',
      stroke: '#121A2E',
      strokeThickness: 5,
    }).setOrigin(0.5).setDepth(11);

    // Subtitle
    const subtitleText = this.add.text(bannerX, bannerY + 28, 'Rencanakan · Belanja Bijak · Tabung Masa Depan', {
      font: '13px sans-serif',
      fill: '#B8A88A',
    }).setOrigin(0.5).setDepth(11);
  }

  _createMenuPanel(width, height) {
    const panelX = width / 2;
    const panelY = 300;
    const panelW = 360;
    const panelH = 250;

    // Background Card
    const panelBg = this.add.rectangle(panelX, panelY, panelW, panelH, 0x121A2E, 0.95)
      .setOrigin(0.5)
      .setStrokeStyle(2, 0x34456B, 1)
      .setDepth(10);

    // Panel Top Decorative Line
    const decoLine = this.add.rectangle(panelX, panelY - panelH / 2 + 18, panelW - 40, 1, 0x34456B, 1)
      .setOrigin(0.5)
      .setDepth(11);

    const panelLabel = this.add.text(panelX, panelY - panelH / 2 + 10, 'PILIH MENU', {
      font: 'bold 10px sans-serif',
      fill: '#D9A441',
      backgroundColor: '#121A2E',
      padding: { x: 8, y: 0 }
    }).setOrigin(0.5).setDepth(12);

    // Check save state
    const hasSave = hasValidSave();
    let saveInfoText = '(Belum ada data tersimpan)';
    if (hasSave) {
      const saved = loadGame();
      if (saved.success && saved.state?.clock) {
        saveInfoText = `Tersimpan: Bulan ${saved.state.clock.month || 1} · Hari ${saved.state.clock.day || 1}`;
      } else {
        saveInfoText = 'Tersedia data simpanan';
      }
    }

    const buttonDefs = [
      {
        id: 'new',
        label: 'Mulai Petualangan Baru',
        sublabel: 'Buat karakter & mulai bulan 1',
        action: () => this._startNew(),
        enabled: true,
        primary: true,
      },
      {
        id: 'continue',
        label: 'Lanjutkan Permainan',
        sublabel: saveInfoText,
        action: () => this._continue(),
        enabled: hasSave,
        primary: false,
      },
      {
        id: 'settings',
        label: 'Pengaturan & Bantuan',
        sublabel: 'Audio, petunjuk singkat, & kredit',
        action: () => this._openSettings(),
        enabled: true,
        primary: false,
      },
    ];

    const startY = panelY - 55;
    const btnGap = 64;

    buttonDefs.forEach((def, i) => {
      this._addButton(panelX, startY + i * btnGap, def, i);
    });

    // Cursor Indicator (Animated Arrow)
    this._cursor = this.add.text(panelX - 170, startY, '►', {
      font: 'bold 18px sans-serif',
      fill: '#D9A441'
    }).setOrigin(0.5).setDepth(15);

    // Gentle cursor bounce tween
    this.tweens.add({
      targets: this._cursor,
      x: panelX - 164,
      duration: 450,
      yoyo: true,
      repeat: -1,
      ease: 'Sine.easeInOut'
    });

    this._updateButtonHighlight();
  }

  _addButton(x, y, def, index) {
    const btnW = 310;
    const btnH = 50;
    const enabled = def.enabled;

    // Background Card
    let bgColor = enabled ? (def.primary ? 0x2A3654 : 0x1F2A44) : 0x161E2E;
    let strokeColor = enabled ? (def.primary ? 0xD9A441 : 0x34456B) : 0x26334D;

    const bg = this.add.rectangle(x, y, btnW, btnH, bgColor)
      .setOrigin(0.5)
      .setStrokeStyle(enabled ? (def.primary ? 2 : 1) : 1, strokeColor, 1)
      .setDepth(11);

    // Primary Tag / Action Indicator
    const prefix = enabled ? '▶  ' : '   ';

    // Main Text
    const text = this.add.text(x - btnW / 2 + 18, y - 9, `${prefix}${def.label}`, {
      font: 'bold 14px sans-serif',
      fill: enabled ? (def.primary ? '#D9A441' : '#F7EEDA') : '#64748B',
    }).setOrigin(0, 0.5).setDepth(12);

    // Subtitle Text
    const subtext = this.add.text(x - btnW / 2 + 18, y + 11, def.sublabel, {
      font: '10px sans-serif',
      fill: enabled ? '#B8A88A' : '#475569',
    }).setOrigin(0, 0.5).setDepth(12);

    // Invisible Hit Zone covering the full button
    const hitZone = this.add.rectangle(x, y, btnW, btnH, 0x000000, 0)
      .setOrigin(0.5)
      .setDepth(14);

    if (enabled) {
      hitZone.setInteractive({ useHandCursor: true });

      hitZone.on('pointerover', () => {
        this._selectedIndex = index;
        this._updateButtonHighlight();
      });

      hitZone.on('pointerdown', () => {
        this._clickFeedback(bg, () => def.action());
      });
    }

    this._buttons.push({
      bg,
      text,
      subtext,
      hitZone,
      def,
      enabled,
      x,
      y
    });
  }

  _clickFeedback(bg, callback) {
    // Quick punch animation on click
    this.tweens.add({
      targets: bg,
      scaleX: 0.98,
      scaleY: 0.96,
      duration: 60,
      yoyo: true,
      onComplete: () => {
        if (callback) callback();
      }
    });
  }

  _moveCursor(dir) {
    let idx = this._selectedIndex + dir;
    while (idx >= 0 && idx < this._buttons.length && !this._buttons[idx].enabled) {
      idx += dir;
    }
    if (idx >= 0 && idx < this._buttons.length && this._buttons[idx].enabled) {
      this._selectedIndex = idx;
      this._updateButtonHighlight();
    }
  }

  _updateButtonHighlight() {
    this._buttons.forEach((btn, i) => {
      if (!btn.enabled) return;
      const isSelected = i === this._selectedIndex;

      if (isSelected) {
        btn.bg.setFillStyle(0xD9A441, 1);
        btn.bg.setStrokeStyle(2, 0xF7EEDA, 1);
        btn.text.setStyle({ fill: '#121A2E' });
        btn.subtext.setStyle({ fill: '#2A1F1A' });
      } else {
        const bgCol = btn.def.primary ? 0x2A3654 : 0x1F2A44;
        const strCol = btn.def.primary ? 0xD9A441 : 0x34456B;
        btn.bg.setFillStyle(bgCol, 1);
        btn.bg.setStrokeStyle(btn.def.primary ? 2 : 1, strCol, 1);
        btn.text.setStyle({ fill: btn.def.primary ? '#D9A441' : '#F7EEDA' });
        btn.subtext.setStyle({ fill: '#B8A88A' });
      }
    });

    // Move cursor arrow to selected button
    const selBtn = this._buttons[this._selectedIndex];
    if (selBtn && this._cursor) {
      this.tweens.add({
        targets: this._cursor,
        y: selBtn.y,
        duration: 100,
        ease: 'Cubic.easeOut'
      });
    }
  }

  _activateSelected() {
    const btn = this._buttons[this._selectedIndex];
    if (btn?.enabled) {
      this._clickFeedback(btn.bg, () => btn.def.action());
    }
  }

  _startNew() {
    this.scene.start('CharacterCreate');
  }

  _continue() {
    const loaded = loadGame();
    if (loaded.success && loaded.state) {
      const store = createStore(loaded.state);
      this.game.registry.set('store', store);
      this.scene.start('World');
    }
  }

  _openSettings() {
    document.dispatchEvent(new CustomEvent('lj:openPanel', { detail: { panel: 'settings' } }));
  }
}
