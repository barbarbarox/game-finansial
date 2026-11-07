/**
 * MainMenu.js — Main menu scene for Life Journey.
 * Displays title, start/continue buttons, settings.
 * No innerHTML for dynamic data. Full keyboard navigation.
 */

import { hasValidSave, loadGame } from '../../state/persistence.js';
import { createStore } from '../../state/store.js';
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

    const meta = this.cache.json.get('meta') || { gameTitle: 'Life Journey', subtitle: 'Simulasi Kehidupan Finansial SMA', version: '0.1.0-prototype' };

    // Background
    if (this.textures.exists('bg_mainmenu_town') && !isPlaceholder('bg_mainmenu_town')) {
      this.add.image(width / 2, height / 2, 'bg_mainmenu_town').setOrigin(0.5);
    } else {
      const bg = this.add.graphics();
      bg.fillGradientStyle(0x3D5236, 0x3D5236, 0x162038, 0x162038, 1);
      bg.fillRect(0, 0, width, height);

      for (let tx = 0; tx < width; tx += 64) {
        for (let ty = height * 0.4; ty < height; ty += 32) {
          bg.fillStyle(tx % 128 === 0 ? 0x4A6B40 : 0x3D5236, 0.4);
          bg.fillRect(tx, ty, 60, 28);
        }
      }
    }

    // Logo area overlay
    this.add.rectangle(width / 2, height * 0.28, 560, 130, 0x121A2E, 0.85).setOrigin(0.5);

    const titleText = this.add.text(width / 2, height * 0.22, meta.gameTitle || 'Life Journey', {
      font: 'bold 44px sans-serif',
      fill: '#D9A441',
      stroke: '#121A2E',
      strokeThickness: 4,
    });
    titleText.setOrigin(0.5);

    const subtitleText = this.add.text(width / 2, height * 0.33, meta.subtitle || 'Simulasi Kehidupan Finansial SMA', {
      font: '16px sans-serif',
      fill: '#F7EEDA',
    });
    subtitleText.setOrigin(0.5);

    const versionText = this.add.text(width - 12, height - 12, `v${meta.version || '0.1.0-prototype'}`, {
      font: '11px sans-serif',
      fill: '#B8A88A',
    });
    versionText.setOrigin(1, 1);

    // Panel for buttons
    const panelY = height * 0.58;
    this.add.rectangle(width / 2, panelY + 45, 280, 160, 0x121A2E, 0.85).setOrigin(0.5);

    const hasSave = hasValidSave();
    const buttonDefs = [
      { label: 'Mulai Baru', action: () => this._startNew(), enabled: true },
      { label: 'Lanjutkan', action: () => this._continue(), enabled: hasSave },
      { label: 'Pengaturan', action: () => this._openSettings(), enabled: true },
    ];

    buttonDefs.forEach((def, i) => {
      this._addButton(width / 2, panelY + i * 48, def.label, def.action, def.enabled);
    });

    this._updateButtonHighlight();

    // Keyboard navigation
    this.input.keyboard.on('keydown-UP', () => this._moveCursor(-1));
    this.input.keyboard.on('keydown-DOWN', () => this._moveCursor(1));
    this.input.keyboard.on('keydown-ENTER', () => this._activateSelected());
    this.input.keyboard.on('keydown-SPACE', () => this._activateSelected());
  }

  _addButton(x, y, label, action, enabled) {
    const bg = this.add.rectangle(x, y, 220, 38, enabled ? 0x34456B : 0x505860)
      .setOrigin(0.5)
      .setInteractive(enabled ? { useHandCursor: true } : {});

    const text = this.add.text(x, y, label, {
      font: 'bold 15px sans-serif',
      fill: enabled ? '#F7EEDA' : '#7A8090',
    });
    text.setOrigin(0.5);

    if (enabled) {
      bg.on('pointerover', () => {
        this._selectedIndex = this._buttons.findIndex(b => b.bg === bg);
        this._updateButtonHighlight();
      });
      bg.on('pointerdown', () => {
        action();
      });
    }

    this._buttons.push({ bg, text, action, enabled });
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
      btn.bg.setFillStyle(isSelected ? 0xD9A441 : 0x34456B);
      btn.text.setStyle({ fill: isSelected ? '#121A2E' : '#F7EEDA' });
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
