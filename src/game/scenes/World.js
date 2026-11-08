/**
 * World.js — Main gameplay world scene for Life Journey.
 *
 * ARCHITECTURE (v2):
 * World.js only bootstraps the Phaser scene (player, camera, HUD, lighting).
 * ALL map rendering (ground, walls, buildings, furniture, NPCs) is exclusively
 * handled by MapManager.  World.js keeps NO parallel drawing code for maps.
 * This prevents the interior-over-exterior bleed that occurred before.
 */

import { PlayerController } from '../player.js';
import { NPCManager } from '../npc.js';
import { createHUD } from '../../ui/hud.js';
import { createCashbookModal } from '../../ui/cashbook.js';
import { createBudgetModal } from '../../ui/budgetPanel.js';
import { createShopModal } from '../../ui/shopPanel.js';
import { createSettingsModal } from '../../ui/settings.js';
import { createCreditsModal } from '../../ui/credits.js';
import { createProceduralTiles } from '../../assets-gen/groundTiles.js';
import { saveGame } from '../../state/persistence.js';
import { addEntry, createAllowanceEntry } from '../../domain/ledger.js';
import { advanceTime, isLocationOpen, formatClock, getTimeUntilWakeup, DEFAULT_OPENING_HOURS } from '../../domain/clock.js';
import { MapManager } from '../mapManager.js';
import { showTimeSkip } from '../../ui/timeSkip.js';
import { startDialogue, chooseOption, getDialogueState, closeDialogue } from '../../ui/dialogueBox.js';

export class World extends Phaser.Scene {
  constructor() {
    super({ key: 'World' });
    this._player = null;
    this._npcManager = null;
    this._interactables = [];
    this._hudElement = null;
    this._tileSize = 32;
    this._promptText = null;
    this._currentInteractable = null;
    this._clockTimerMs = 0;
    this._mapManager = null;
    this._feedbackUntil = 0;
  }

  create() {
    const config = this.cache.json.get('phase1config') || {};
    const store = this.game.registry.get('store');

    this._tileSize = config?.tileSize || 32;

    // Generate procedural tile textures once
    createProceduralTiles(this, this._tileSize);

    // Initial camera size (will be updated when map loads)
    this.cameras.main.setBounds(0, 0, 1280, 768);

    // 1. Spawn Player at a temporary position (MapManager will reposition on load)
    const tmpX = 6 * this._tileSize;
    const tmpY = 10 * this._tileSize;
    this._player = new PlayerController(this, tmpX, tmpY, config);
    this.cameras.main.startFollow(this._player.sprite, true, 0.1, 0.1);

    // 2. NPC Manager (empty until map loads)
    this._npcManager = new NPCManager(this, []);

    // 3. Interaction prompt text (fixed to camera)
    this._promptText = this.add.text(0, 0, '', {
      font: 'bold 13px sans-serif',
      fill: '#D9A441',
      stroke: '#121A2E',
      strokeThickness: 3,
      backgroundColor: '#1F2A44',
      padding: { x: 8, y: 4 }
    }).setOrigin(0.5, 1.0).setDepth(2000).setScrollFactor(0).setVisible(false);

    // 4. Keyboard input
    this.keyE = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.E);
    this.keySpace = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.SPACE);

    // 5. Ambient Day-Night Lighting Overlay
    const viewW = this.cameras.main.width || 960;
    const viewH = this.cameras.main.height || 540;
    this._ambientLight = this.add.rectangle(0, 0, viewW, viewH, 0x000000, 0);
    this._ambientLight.setOrigin(0, 0).setScrollFactor(0).setDepth(4500);
    const initialTime = store?.getState()?.clock?.timeOfDay ?? (8 * 60);
    this._updateAmbientLight(initialTime);

    // 6. Initialize MapManager — this is the ONLY thing that draws maps
    const mapsIndex = this.cache.json.get('mapsIndex') || {
      maps: [
        { id: 'town_hub',      file: 'data/maps/town_hub.layout.json' },
        { id: 'home',          file: 'data/maps/home.layout.json' },
        { id: 'school',        file: 'data/maps/school.layout.json' },
        { id: 'minimarket',    file: 'data/maps/minimarket.layout.json' },
        { id: 'toko_kosmetik', file: 'data/maps/toko_kosmetik.layout.json' },
        { id: 'spbu',          file: 'data/maps/spbu.layout.json' },
        { id: 'game_center',   file: 'data/maps/game_center.layout.json' }
      ]
    };
    this._mapManager = new MapManager(this, mapsIndex);

    // Load initial map: saved map first, then 'home' for new game, then town_hub
    const savedMap = store?.getState()?.currentMap;
    const savedPos  = store?.getState()?.playerPos;
    const startMap  = savedMap || 'home';
    const startSpawn = (savedMap && savedPos) ? 'saved' : 'default';
    this._mapManager.loadMap(startMap, startSpawn);

    // 7. Mount DOM HUD
    const uiContainer = document.getElementById('ui-container') || document.body;
    if (store) {
      this._hudElement = createHUD(
        uiContainer,
        store,
        () => createCashbookModal(uiContainer, store),
        () => createBudgetModal(uiContainer, store, config),
        () => createSettingsModal(uiContainer, null, () => createCreditsModal(uiContainer), () => this._exitToMainMenu(), store)
      );

      // Auto-save on state change
      store.subscribe((st) => {
        if (st) saveGame(st);
      });
    }

    // Debug hook
    this._setupDebug(config);
  }

  update(time, delta) {
    if (this._player) {
      this._player.update(delta, []);    // colliders managed by MapManager
      this._checkInteractables();
      if (this._npcManager) {
        this._npcManager.update(time, this._player);
      }
      this._updateGameClock(delta);
    }
  }

  _updateGameClock(delta) {
    this._clockTimerMs += delta;

    // 1000ms real time = 1 menit game (1 real second = 1 game min)
    if (this._clockTimerMs >= 1000) {
      const minutesToAdvance = Math.floor(this._clockTimerMs / 1000);
      this._clockTimerMs %= 1000;

      const store = this.game.registry.get('store');
      if (!store) return;
      const state = store.getState();
      if (!state || !state.clock) return;

      const { clock: newClock, events } = advanceTime(state.clock, minutesToAdvance, 'tick');
      let ledger = state.ledger;

      for (const ev of events) {
        if (ev.type === 'allowance_due') {
          if (ledger) {
            const allowanceEntry = createAllowanceEntry(newClock.day, newClock.month, newClock.timeOfDay);
            const res = addEntry(ledger, allowanceEntry);
            if (res.ok) ledger = res.ledger;
          }
        }
      }

      store.setState({
        clock: newClock,
        ledger
      });

      this._updateAmbientLight(newClock.timeOfDay);
    }
  }

  _updateAmbientLight(timeOfDay) {
    if (!this._ambientLight) return;
    const hours = (timeOfDay / 60) % 24;

    // Transisi pencahayaan dunia game sesuai waktu:
    // Pagi (07:00 - 15:30): Cahaya siang bersih (alpha 0)
    // Sore (15:30 - 18:00): Senja jingga/keemasan hangat
    // Malam (18:00 - 21:00): Biru malam temaram
    // Dini Hari (21:00 - 05:00): Biru gelap malam pekat
    // Fajar (05:00 - 07:00): Semburat keemasan fajar
    if (hours >= 7 && hours < 15.5) {
      this._ambientLight.setFillStyle(0x000000, 0);
    } else if (hours >= 15.5 && hours < 18) {
      const t = (hours - 15.5) / 2.5;
      this._ambientLight.setFillStyle(0xD86A28, 0.04 + t * 0.16);
    } else if (hours >= 18 && hours < 21) {
      const t = (hours - 18) / 3;
      this._ambientLight.setFillStyle(0x0E1832, 0.18 + t * 0.22);
    } else if (hours >= 21 || hours < 5) {
      this._ambientLight.setFillStyle(0x081024, 0.40);
    } else {
      const t = (hours - 5) / 2;
      this._ambientLight.setFillStyle(0xC88040, 0.22 * (1 - t));
    }
  }

  showPromptFeedback(text, durationMs = 2500) {
    if (this._promptText) {
      this._promptText.setText(text);
      const camW = this.cameras.main.width || 960;
      const camH = this.cameras.main.height || 540;
      this._promptText.setPosition(camW / 2, camH - 20);
      this._promptText.setVisible(true);
      this._feedbackUntil = Date.now() + durationMs;
      setTimeout(() => {
        if (Date.now() >= this._feedbackUntil && this._promptText) {
          this._promptText.setVisible(false);
        }
      }, durationMs);
    }
  }

  _checkInteractables() {
    if (this._feedbackUntil && Date.now() < this._feedbackUntil) {
      return;
    }

    const px = this._player.x;
    const py = this._player.y;
    const ts = this._tileSize;
    const camW = this.cameras.main.width || 960;
    const camH = this.cameras.main.height || 540;

    let nearby = null;
    for (const int of (this._interactables || [])) {
      const ix = (int.x || 0) * ts;
      const iy = (int.y || 0) * ts;
      const dist = Phaser.Math.Distance.Between(px, py, ix, iy);
      if (dist < 50) {
        nearby = int;
        break;
      }
    }

    if (nearby) {
      this._currentInteractable = nearby;
      // Prompt sits at bottom-center of screen (scrollFactor=0 text)
      this._promptText.setPosition(camW / 2, camH - 20);
      this._promptText.setText(nearby.prompt || 'Tekan [E]');
      this._promptText.setVisible(true);

      if (Phaser.Input.Keyboard.JustDown(this.keyE) || Phaser.Input.Keyboard.JustDown(this.keySpace)) {
        this._openInteraction(nearby);
      }
    } else {
      this._currentInteractable = null;
      this._promptText.setVisible(false);
    }
  }

  _openInteraction(int) {
    const uiContainer = document.getElementById('ui-container') || document.body;
    const store = this.game.registry.get('store');
    const config = this.cache.json.get('phase1config') || {};

    // 1. Door / Exit transition
    if (int.type === 'door' || int.type === 'exit') {
      if (int.targetMap && this._mapManager) {
        this._mapManager.transitionTo(int.targetMap, int.targetSpawn, int.openingHoursId);
        return;
      }
    }

    // 2. Sleep in bed (Rule 72 §4)
    if (int.action === 'sleep' || int.activityId === 'tidur_malam') {
      const clock = store?.getState()?.clock || {};
      const diff = getTimeUntilWakeup(clock);
      showTimeSkip({
        title: 'Tidur di Kamar',
        minutes: diff,
        costText: 'Energi Pulih 100%',
        onComplete: () => {
          if (window.__LJ__) window.__LJ__.advanceTime(diff, 'sleep');
          if (store) store.setState({ gasoline: 100 });
        }
      });
      return;
    }

    // 3. Other activities (study, watch tv, etc.)
    if (int.type === 'activity') {
      // Look up duration from activities catalog
      const activitiesCatalog = this.cache.json.get('activitiesData')?.activities || [];
      const actEntry = activitiesCatalog.find(a => a.id === int.activityId);
      let actMinutes;
      if (actEntry) {
        if (typeof actEntry.duration === 'number') {
          actMinutes = actEntry.duration;
        } else if (Array.isArray(actEntry.durationOptions)) {
          // Default to minimum duration
          actMinutes = actEntry.durationOptions[0];
        } else if (actEntry.duration === 'until_1430') {
          // School lesson: advance to 14:30
          const clock = store?.getState()?.clock || {};
          const currentMin = (clock.gameMinutes ?? (clock.timeOfDay ?? 360)) % 1440;
          actMinutes = Math.max(1, 870 - currentMin); // 14:30 = 870 mins
        } else {
          actMinutes = 30; // safe fallback
        }
      } else {
        // Fallback: hardcoded for known types
        actMinutes = int.activityId === 'pelajaran_sekolah' ? 120 : (int.activityId === 'main_game' ? 60 : 30);
      }

      showTimeSkip({
        title: int.prompt.replace(/^Tekan \[E\]\s*/, ''),
        minutes: actMinutes,
        onComplete: () => {
          if (window.__LJ__) window.__LJ__.advanceTime(actMinutes, int.activityId);
        }
      });
      return;
    }

    // 4. Savings / Shop / Panel
    if (int.action === 'savings' || int.type === 'savings') {
      createShopModal(uiContainer, store, 'rumah', config, null);
      return;
    }

    if (int.locationId) {
      if (int.openingHoursId || DEFAULT_OPENING_HOURS[int.locationId]) {
        const checkId = int.openingHoursId || int.locationId;
        const clock = store?.getState()?.clock || {};
        const status = isLocationOpen(checkId, clock);
        if (!status.open) {
          if (this._promptText) {
            this._promptText.setText(`[TUTUP] ${status.reason}`);
            this._promptText.setVisible(true);
            setTimeout(() => {
              if (this._promptText) this._promptText.setVisible(false);
            }, 2500);
          }
          return;
        }
      }
      createShopModal(uiContainer, store, int.locationId, config, null);
    }
  }

  _exitToMainMenu() {
    const store = this.game.registry.get('store');
    if (store && this._player?.sprite) {
      const st = store.getState();
      saveGame({
        ...st,
        playerPos: { x: Math.round(this._player.sprite.x), y: Math.round(this._player.sprite.y) }
      });
    }
    if (this._hudElement) {
      this._hudElement.remove();
      this._hudElement = null;
    }
    const uiContainer = document.getElementById('ui-container');
    if (uiContainer) {
      uiContainer.replaceChildren();
    }
    this.scene.stop('World');
    this.scene.start('MainMenu');
  }

  _setupDebug(config) {
    window.__LJ__ = {
      scene: this,
      getStore: () => this.game.registry.get('store'),
      getState: () => this.game.registry.get('store')?.getState(),
      getLedger: () => this.game.registry.get('store')?.getState()?.ledger,
      getPlayer: () => this._player,
      getMapManager: () => this._mapManager,
      teleportTo: (tx, ty) => {
        if (this._player) {
          this._player.sprite.x = tx * this._tileSize;
          this._player.sprite.y = ty * this._tileSize;
        }
      },
      teleportToMap: (mapId, spawn) => {
        if (this._mapManager) {
          this._mapManager.loadMap(mapId, spawn || 'default');
        }
      },
      listInteractables: () => this._interactables,
      interact: (id) => {
        const item = this._interactables?.find(i => i.id === id);
        if (item) this._openInteraction(item);
      },
      advanceTime: (minutes, reason = 'debug') => {
        const store = this.game.registry.get('store');
        if (!store) return null;
        const state = store.getState();
        if (!state || !state.clock) return null;

        const { clock: newClock, events } = advanceTime(state.clock, minutes, reason);
        let ledger = state.ledger;
        for (const ev of events) {
          if (ev.type === 'allowance_due') {
            if (ledger) {
              const allowanceEntry = createAllowanceEntry(newClock.day, newClock.month, newClock.timeOfDay);
              const res = addEntry(ledger, allowanceEntry);
              if (res.ok) ledger = res.ledger;
            }
          }
        }
        store.setState({ clock: newClock, ledger });
        this._updateAmbientLight(newClock.timeOfDay);
        return { clock: newClock, events };
      },
      getTime: () => {
        const store = this.game.registry.get('store');
        return formatClock(store?.getState()?.clock || {});
      },
      isLocationOpen: (locId) => {
        const store = this.game.registry.get('store');
        return isLocationOpen(locId, store?.getState()?.clock || {});
      },
      startDialogue: (id, npcId, onClose) => startDialogue(id, npcId, onClose),
      choose: (i) => chooseOption(i),
      getDialogueState: () => getDialogueState(),
      closeDialogue: () => closeDialogue()
    };
    console.info('[Debug] window.__LJ__ aktif dengan time system, map & dialogue controls');
  }
}
