/**
 * CharacterCreate.js — Scene for character creation.
 * Opens DOM character creation modal. Once done, initializes store and starts World scene.
 */

import { createCharacterModal } from '../../ui/characterCreate.js';
import { createStore } from '../../state/store.js';
import { createLedger, createAllowanceEntry, addEntry } from '../../domain/ledger.js';
import { saveGame } from '../../state/persistence.js';

export class CharacterCreate extends Phaser.Scene {
  constructor() {
    super({ key: 'CharacterCreate' });
  }

  create() {
    const config = this.cache.json.get('phase1config') || {};
    const container = document.getElementById('ui-container') || document.body;

    createCharacterModal(container, (charData) => {
      let ledger = createLedger();
      // Allowance will be granted by Ibu during Day 1 morning dialogue (E6 flow)

      const initialMissions = [
        { id: 'M1', title: 'Terima Uang Saku dari Ibu', completed: false },
        { id: 'M2', title: 'Susun Anggaran Bulan Ini', completed: false },
        { id: 'M3', title: 'Isi Bensin Sebelum 20%', completed: false },
        { id: 'M4', title: 'Tabung Minimal Rp100.000 Bulan Ini', completed: false },
        { id: 'M5', title: 'Hadapi Satu Ajakan Teman', completed: false },
        { id: 'M6', title: 'Pertahankan Kas > Rp0 Sampai Akhir Bulan', completed: false },
        { id: 'M7', title: 'Tinjau Ringkasan Akhir Bulan', completed: false },
      ];

      const gameState = {
        schemaVersion: 3,
        character: charData,
        currentMap: 'home',
        clock: {
          gameMinutes: 360, // 06:00
          day: 1,
          month: 1,
          year: 1,
          timeOfDay: 360,
          totalDays: 0,
          paused: false,
          finished: false
        },
        ledger: ledger,
        gasoline: 60, // Rule 82 §5: Initial fuel 60% for SPBU tutorial
        energy: {
          current: 100,
          max: 100,
          exhaustionCount: 0
        },
        inventory: [
          { slotIndex: 0, itemId: null, count: 0 },
          { slotIndex: 1, itemId: null, count: 0 },
          { slotIndex: 2, itemId: null, count: 0 },
          { slotIndex: 3, itemId: null, count: 0 },
          { slotIndex: 4, itemId: null, count: 0 }
        ],
        budget: {},
        missions: initialMissions,
        tutorial: {
          active: true,
          stepIndex: 0,
          completedSteps: [],
          completed: false,
          pausedClock: true,
          stepStartTime: Date.now(),
          stepProgress: {}
        },
        flags: {},
        seed: 12345
      };

      // Save initial state
      saveGame(gameState);

      // Create store and register in Phaser
      const store = createStore(gameState);
      this.game.registry.set('store', store);

      // Transition to World scene
      this.scene.start('World');
    });
  }
}
