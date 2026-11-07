/**
 * main.js — Game entry point for Life Journey
 * Sets up Phaser 3 with pixelArt: true, logical resolution 960x540.
 */

import { Boot } from './scenes/Boot.js';
import { Preload } from './scenes/Preload.js';
import { MainMenu } from './scenes/MainMenu.js';
import { CharacterCreate } from './scenes/CharacterCreate.js';
import { World } from './scenes/World.js';
import { createSettingsModal } from '../ui/settings.js';
import { createCreditsModal } from '../ui/credits.js';

function initGame() {
  if (window.__GAME__) return;

  const config = {
    type: Phaser.AUTO,
    parent: 'game-container',
    width: 960,
    height: 540,
    pixelArt: true,
    antialias: false,
    roundPixels: true,
    scale: {
      mode: Phaser.Scale.FIT,
      autoCenter: Phaser.Scale.CENTER_BOTH,
    },
    physics: {
      default: 'arcade',
      arcade: {
        gravity: { y: 0 },
        debug: false,
      },
    },
    scene: [Boot, Preload, MainMenu, CharacterCreate, World],
  };

  const game = new Phaser.Game(config);
  window.__GAME__ = game;

  // Global UI event listener for DOM overlays
  document.addEventListener('lj:openPanel', (e) => {
    const panelName = e.detail?.panel;
    const uiContainer = document.getElementById('ui-container') || document.body;

    if (panelName === 'settings') {
      createSettingsModal(uiContainer, null, () => {
        createCreditsModal(uiContainer, null);
      });
    } else if (panelName === 'credits') {
      createCreditsModal(uiContainer, null);
    }
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initGame);
} else {
  initGame();
}
