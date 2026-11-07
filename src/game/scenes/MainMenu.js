/**
 * MainMenu.js — Main menu scene for Life Journey.
 * Displays title, start/continue buttons, settings.
 * No innerHTML for dynamic data. Full keyboard navigation.
 */

import { hasValidSave } from '../../state/persistence.js';
import { isPlaceholder } from '../assetLoader.js';

export class MainMenu extends Phaser.Scene {
  constructor() {
    super({ key: 'MainMenu' });
    this._buttons = [];
    this._selectedIndex = 0;
  }

  create() {
    const { width, height } = this.scale;
    this._buttons = [];
    this._selectedIndex = 0;

    const meta = this.game.registry.get('meta') ?? { gameTitle: 'Life Journey', subtitle: '' };
    const config = this.cache.json.get('phase1config') ?? {};

    // Background
    if (!isPlaceholder('bg_mainmenu_town')) {
      this.add.image(width / 2, height / 2, 'bg_mainmenu_town').setOrigin(0.5);
    } else {
      // Procedural gradient background
      const bg = this.add.graphics();
      bg.fillGradientStyle(0x3D5236, 0x3D5236, 0x162038, 0x162038, 1);
      bg.fillRect(0, 0, width, height);

      // Simple decorative tiles to suggest a town
      const tileColor = 0x4A6B40;
      for (let tx = 0; tx < width; tx += 64) {
        for (let ty = height * 0.4; ty < height; ty += 32) {
          bg.fillStyle(tx % 128 === 0 ? 0x4A6B40 : 0x3D5236, 0.4);
          bg.fillRect(tx, ty, 60, 28);
        }
      }
    }

    // Logo area overlay
    this.add.rectangle(width / 2, height * 0.28, 500, 120, 0x121A2E, 0.75)
      .setOrigin(0.5);

    // Game title - using textContent equivalent (Phaser.GameObjects.Text, safe)
    const titleText = this.add.text(width / 2, height * 0.22, meta.gameTitle ?? 'Life Journey', {
      font: 'bold 48px sans-serif',
      fill: '#D9A441',
      stroke: '#121A2E',
      strokeThickness: 4,
    });
    titleText.setOrigin(0.5);

    const subtitleText = this.add.text(width / 2, height * 0.33, meta.subtitle ?? '', {
      font: '18px sans-serif',
      fill: '#FBF6EA',
    });
    subtitleText.setOrigin(0.5);

    // Version text
    const versionText = this.add.text(width - 8, height - 8, `v${meta.version ?? '0.1.0-prototype'}`, {
      font: '11px sans-serif',
      fill: '#B8A88A',
    });
    versionText.setOrigin(1, 1);

    // Panel for buttons
    const panelY = height * 0.55;
    this.add.rectangle(width / 2, panelY + 60, 280, 170, 0x121A2E, 0.8)
      .setOrigin(0.5);

    // Button definitions
    const hasSave = hasValidSave();
    const buttonDefs = [
      { label: 'Mulai Baru', action: () => this._startNew(), enabled: true },
      { label: 'Lanjutkan', action: () => this._continue(), enabled: hasSave },
      { label: 'Pengaturan', action: () => this._openSettings(), enabled: true },
    ];

    buttonDefs.forEach((def, i) => {
      this._addButton(width / 2, panelY + i * 50, def.label, def.action, def.enabled);
    });

    this._updateButtonHighlight();

    // Keyboard navigation
    this._cursors = this.input.keyboard.createCursorKeys();
    this._enterKey = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.ENTER);
    this._spaceKey = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.SPACE);

    this.input.keyboard.on('keydown-UP', () => this._moveCursor(-1));
    this.input.keyboard.on('keydown-DOWN', () => this._moveCursor(1));
    this.input.keyboard.on('keydown-ENTER', () => this._activateSelected());
    this.input.keyboard.on('keydown-SPACE', () => this._activateSelected());

    // Placeholder mode indicator
    const mode = this.add.text(8, height - 8, '[PLACEHOLDER MODE]', {
      font: '10px sans-serif',
      fill: '#9AA0AA',
    });
    mode.setOrigin(0, 1);
  }

  _addButton(x, y, label, action, enabled) {
    const bg = this.add.rectangle(x, y, 220, 40, enabled ? 0x34456B : 0x505860)
      .setOrigin(0.5)
      .setInteractive(enabled ? { useHandCursor: true } : {});

    const text = this.add.text(x, y, label, {
      font: `bold 16px sans-serif`,
      fill: enabled ? '#FBF6EA' : '#7A8090',
    });
    text.setOrigin(0.5);

    if (enabled) {
      bg.on('pointerover', () => {
        this._selectedIndex = this._buttons.length;
        this._updateButtonHighlight();
      });
      bg.on('pointerdown', () => {
        if (enabled) action();
      });
    }

    this._buttons.push({ bg, text, action, enabled, x, y });
  }

  _moveCursor(dir) {
    const enabled = this._buttons.filter(b => b.enabled);
    // Find next enabled
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
      btn.bg.setFillStyle(isSelected ? 0xD9A441 : 0x34456B);
      btn.text.setStyle({ fill: isSelected ? '#121A2E' : '#FBF6EA' });
    });
  }

  _activateSelected() {
    const btn = this._buttons[this._selectedIndex];
    if (btn?.enabled) btn.action();
  }

  _startNew() {
    this.scene.start('CharacterCreate');
  }

  _continue() {
    this.scene.start('World');
  }

  _openSettings() {
    // Show settings DOM panel
    const event = new CustomEvent('lj:openPanel', { detail: { panel: 'settings' } });
    document.dispatchEvent(event);
  }
}
