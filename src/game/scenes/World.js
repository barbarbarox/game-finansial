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
import { createShopModal, closeShopModal } from '../../ui/shopPanel.js';
import { createSettingsModal } from '../../ui/settings.js';
import { createCreditsModal } from '../../ui/credits.js';
import { createProceduralTiles } from '../../assets-gen/groundTiles.js';
import { saveGame } from '../../state/persistence.js';
import { addEntry, createAllowanceEntry, createSavingsDepositEntry, getCash } from '../../domain/ledger.js';
import { advanceTime, isLocationOpen, formatClock, getTimeUntilWakeup, DEFAULT_OPENING_HOURS } from '../../domain/clock.js';
import { MapManager } from '../mapManager.js';
import { showTimeSkip } from '../../ui/timeSkip.js';
import { startDialogue, chooseOption, getDialogueState, closeDialogue } from '../../ui/dialogueBox.js';
import { MissionFxManager } from '../effects/missionFx.js';
import { createHotbar } from '../../ui/hotbar.js';
import { changeEnergy, calculateActivityDrain, canPerformActivity, DEFAULT_ENERGY_CONFIG } from '../../domain/energy.js';
import { useItem, createInventory, addItem as domainAddItem } from '../../domain/inventory.js';
import { ITEMS_MAP } from '../../domain/itemsCatalog.js';
import { canMountVehicle } from '../../domain/vehicle.js';
import { NavigationGrid } from '../navigationGrid.js';
import { findBestInteractionTarget } from '../interactionTarget.js';
import { emit, subscribe, DOMAIN_EVENTS } from '../../domain/events.js';
import { TutorialManager, createTutorialState } from '../../domain/tutorial.js';
import { GuidanceArrowManager } from '../effects/guidanceArrow.js';
import { TutorialBanner } from '../../ui/tutorialBanner.js';

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
    this._tutorialManager = null;
    this._guidanceArrow = null;
    this._tutorialBanner = null;
    this._clockTimerMs = 0;
    this._mapManager = null;
    this._missionFx = null;
    this._feedbackUntil = 0;
    this._hotbar = null;
    this._passiveMinuteAccumulator = 0;
    this._parkedMotorProp = null;
    this.keyV = null;
    this.keyEsc = null;
    this._navGrid = null;
    this._initData = null;
  }

  init(data) {
    this._initData = data || {};
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
    this.keyV = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.V);
    this.keyEsc = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.ESC);
    this.keyTab = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.TAB);

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
    this._missionFx = new MissionFxManager(this);

    // Load initial map: query param / init data first, then saved map, then 'home'
    const savedMap = store?.getState()?.currentMap;
    const savedPos  = store?.getState()?.playerPos;
    const startMap  = this._initData?.mapId || savedMap || 'home';
    const startSpawn = this._initData?.spawnTarget || ((savedMap && savedPos) ? 'saved' : 'default');
    this._mapManager.loadMap(startMap, startSpawn);

    // 7. Mount DOM HUD
    const uiContainer = document.getElementById('ui-container') || document.body;
    if (store) {
      this._hudElement = createHUD(
        uiContainer,
        store,
        () => createCashbookModal(uiContainer, store),
        () => createBudgetModal(uiContainer, store, config),
        () => createSettingsModal(uiContainer, null, () => createCreditsModal(uiContainer), () => this._exitToMainMenu(), store),
        () => this._toggleVehicle()
      );

      // 8. Mount DOM Hotbar (Rule 74 §3)
      this._hotbar = createHotbar(uiContainer, store, (slotIndex) => this._useHotbarItem(slotIndex));
      if (this._hotbar) {
        this._hotbar.update(store.getState(), ITEMS_MAP);
        store.subscribe((st) => {
          if (this._hotbar && st) {
            this._hotbar.update(st, ITEMS_MAP);
          }
        });
      }

      // Auto-save on state change & check mission completion (Rule 77)
      let prevMissions = store.getState()?.missions || [];
      store.subscribe((st) => {
        if (st) {
          saveGame(st);
          if (st.missions && this._missionFx) {
            for (const m of st.missions) {
              if (m.completed) {
                const prev = prevMissions.find(pm => pm.id === m.id);
                if (!prev || !prev.completed) {
                  this._missionFx.trigger(m.id, m.title);
                }
              }
            }
            prevMissions = st.missions;
          }
        }
      });

      // 10. Tutorial System (Rule 82)
      const tutData = this.cache.json.get('tutorialPhase1') || {};
      this._tutorialManager = new TutorialManager(store, tutData);
      this._tutorialManager.init();
      this._guidanceArrow = new GuidanceArrowManager(this, this._tutorialManager);
      this._tutorialBanner = new TutorialBanner(store, this._tutorialManager);

      // Trigger mission complete FX on tutorial step change
      subscribe(DOMAIN_EVENTS.TUTORIAL_STEP_CHANGED, (payload) => {
        if (payload?.prevStep && this._missionFx) {
          this._missionFx.trigger(payload.prevStep.id, payload.prevStep.title);
        }
      });
    }

    // 9. Click-to-Move Pathfinding & Interaction (Gate H5)
    this._initNavGrid();
    this.input.on('pointerdown', (pointer) => {
      if (pointer.button !== 0) return;
      this._handleClickToMove(pointer);
    });

    // Debug hook
    this._setupDebug(config);
  }

  update(time, delta) {
    if (this._isExhaustionSequenceRunning) return;
    if (this._player) {
      if (this.keyV && Phaser.Input.Keyboard.JustDown(this.keyV)) {
        this._toggleVehicle();
      }
      if (this.keyEsc && Phaser.Input.Keyboard.JustDown(this.keyEsc)) {
        this._player.clearPath();
      }
      const colliders = this._mapManager ? this._mapManager.getColliderRects() : [];
      this._player.update(delta, colliders);
      if (this._player.moving && this._player.sprite) {
        emit(DOMAIN_EVENTS.PLAYER_MOVED, { x: this._player.sprite.x, y: this._player.sprite.y });
      }
      this._checkInteractables();
      if (this._npcManager) {
        this._npcManager.update(time, this._player);
      }
      if (this._guidanceArrow) {
        this._guidanceArrow.update(this._mapManager?.currentMapId || 'home');
      }
      this._updateGameClock(delta);
    }
  }

  _updateGameClock(delta) {
    if (this._tutorialManager?.isClockPaused()) {
      this._clockTimerMs = 0;
      return;
    }
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
      this._updateEnergyDrain(minutesToAdvance, 'tick');
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

  _useHotbarItem(slotIndex) {
    if (document.querySelector('.dialogue-panel:not([style*="display: none"])')) return;

    const store = this.game.registry.get('store');
    if (!store) return;
    const state = store.getState();
    const inventory = state.inventory || createInventory(5);
    const energyState = state.energy || { current: 100, max: 100 };

    const res = useItem(inventory, slotIndex, ITEMS_MAP, energyState);
    if (!res.ok) {
      if (res.reason) {
        this.showPromptFeedback(res.reason, 2000);
      }
      return;
    }

    const nextEnergy = changeEnergy(energyState, res.item.energy);
    store.setState({
      inventory: res.inventory,
      energy: nextEnergy.state
    });

    const minutes = res.item.consumeMinutes || 3;
    if (window.__LJ__?.advanceTime) {
      window.__LJ__.advanceTime(minutes, `consume_${res.item.id}`);
    }

    if (this._player?.sprite) {
      const fx = this.add.text(this._player.sprite.x, this._player.sprite.y - 28, `+${res.item.energy} Energi`, {
        fontFamily: 'monospace',
        fontSize: '13px',
        fontStyle: 'bold',
        color: '#85E37D',
        stroke: '#0A0F1A',
        strokeThickness: 3
      }).setOrigin(0.5).setDepth(9999);

      this.tweens.add({
        targets: fx,
        y: fx.y - 20,
        alpha: 0,
        duration: 900,
        ease: 'Power1',
        onComplete: () => fx.destroy()
      });
    }

    this.showPromptFeedback(`Mengonsumsi ${res.item.label} (+${res.item.energy} Energi)`);
  }

  _showEnergy50Toast() {
    this.showPromptFeedback('Energi kamu di bawah 50%, silakan makan untuk menambahnya.', 3500);
    const track = document.querySelector('.hm-energy-track');
    if (track) {
      track.classList.add('pulse-warn');
      setTimeout(() => track.classList.remove('pulse-warn'), 1500);
    }

    const toast = document.createElement('div');
    toast.className = 'energy-warn-toast';
    toast.style.position = 'fixed';
    toast.style.top = '72px';
    toast.style.left = '50%';
    toast.style.transform = 'translateX(-50%)';
    toast.style.backgroundColor = '#D9A441';
    toast.style.color = '#0A0F1A';
    toast.style.padding = '8px 18px';
    toast.style.borderRadius = '6px';
    toast.style.fontFamily = 'monospace';
    toast.style.fontWeight = 'bold';
    toast.style.fontSize = '13px';
    toast.style.zIndex = '9999';
    toast.style.boxShadow = '0 4px 16px rgba(0,0,0,0.6)';
    toast.style.border = '1px solid #FFE7A0';
    toast.textContent = 'Energi kamu di bawah 50%, silakan makan untuk menambahnya.';
    document.body.appendChild(toast);
    setTimeout(() => {
      toast.style.transition = 'opacity 0.4s ease';
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 400);
    }, 3200);
  }

  _triggerExhaustionSequence() {
    if (this._isExhaustionSequenceRunning) return;
    this._isExhaustionSequenceRunning = true;

    const store = this.game.registry.get('store');
    const state = store ? store.getState() : {};
    const clock = state.clock || {};

    // 1. If mounted on motor, auto-dismount and park motor in town_hub
    if (this._player?.isMounted) {
      this._player.dismount();
      if (store) {
        store.setState({
          vehicle: {
            mounted: false,
            parked: { mapId: 'town_hub', x: 19 * 32, y: 15 * 32 }
          }
        });
      }
      this._removeParkedMotor();
    }

    // 2. Blackout overlay with text "Kamu kelelahan dan tertidur…"
    const overlay = document.createElement('div');
    overlay.className = 'exhaustion-blackout-overlay';
    overlay.style.position = 'fixed';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.width = '100vw';
    overlay.style.height = '100vh';
    overlay.style.backgroundColor = '#000000';
    overlay.style.zIndex = '99999';
    overlay.style.display = 'flex';
    overlay.style.alignItems = 'center';
    overlay.style.justifyContent = 'center';
    overlay.style.color = '#F7EEDA';
    overlay.style.fontSize = '20px';
    overlay.style.fontFamily = 'monospace';
    overlay.style.opacity = '0';
    overlay.style.transition = 'opacity 0.6s ease';
    overlay.textContent = 'Kamu kelelahan dan tertidur…';
    document.body.appendChild(overlay);

    requestAnimationFrame(() => {
      overlay.style.opacity = '1';
    });

    setTimeout(async () => {
      // 3. Advance time to next day 10:00 (minute 600)
      const curState = store.getState();
      const curClock = curState.clock || {};
      const currentMinuteOfDay = curClock.timeOfDay ?? (curClock.gameMinutes ? curClock.gameMinutes % 1440 : 360);
      const minutesToMidnight = 1440 - currentMinuteOfDay;
      const minutesTo10AM = minutesToMidnight + 600; // 10:00 = 600 mins

      if (window.__LJ__?.advanceTime) {
        window.__LJ__.advanceTime(minutesTo10AM, 'exhaustion_wake');
      }
      this._clockTimerMs = 0;

      // 4. Record attendanceMissed++ & reset energy to 50%
      const postState = store.getState();
      const updatedSchool = {
        ...(postState.school || {}),
        attendanceMissed: (postState.school?.attendanceMissed || 0) + 1
      };

      store.setState({
        school: updatedSchool,
        energy: {
          current: 50,
          max: postState.energy?.max || 100,
          exhaustionCount: (postState.energy?.exhaustionCount || 0) + 1,
          warn50Triggered: false,
          warn25Triggered: false
        }
      });

      emit(DOMAIN_EVENTS.ENERGY_CHANGED, 50);

      // 5. Load home map at bed position (x=5, y=5)
      await this._mapManager.loadMap('home', 'default');
      if (this._player) {
        this._player.sprite.x = 5 * 32;
        this._player.sprite.y = 5 * 32;
        this._player.facing = 'down';
      }

      // 6. Fade out blackout overlay
      setTimeout(() => {
        overlay.style.opacity = '0';
        setTimeout(() => {
          overlay.remove();
          this._isExhaustionSequenceRunning = false;
          this.showPromptFeedback('Kamu bangun kesiangan karena kelelahan.', 3500);
        }, 600);
      }, 800);
    }, 1200);
  }

  _updateEnergyDrain(minutes, reason) {
    const store = this.game.registry.get('store');
    if (!store) return;
    const state = store.getState();
    const energyState = state.energy || { current: 100, max: 100, exhaustionCount: 0 };

    // Recovery reasons
    if (reason === 'sleep' || reason === 'tidur_malam' || reason === 'tidur') {
      const rec = Math.round((DEFAULT_ENERGY_CONFIG.sleepRecoveryPerHour * minutes) / 60);
      const res = changeEnergy(energyState, Math.max(rec, 50));
      store.setState({ energy: res.state });
      emit(DOMAIN_EVENTS.ENERGY_CHANGED, res.state.current);
      return;
    }

    if (reason === 'makan_rumah') {
      const res = changeEnergy(energyState, 40);
      store.setState({ energy: res.state });
      emit(DOMAIN_EVENTS.ENERGY_CHANGED, res.state.current);
      return;
    }

    if (reason === 'istirahat') {
      const rec = Math.round((DEFAULT_ENERGY_CONFIG.restRecoveryPerHour * minutes) / 60);
      const res = changeEnergy(energyState, rec);
      store.setState({ energy: res.state });
      emit(DOMAIN_EVENTS.ENERGY_CHANGED, res.state.current);
      return;
    }

    if (reason === 'exhaustion_wake') {
      return;
    }

    // Activity drain (Rule 83)
    const drain = calculateActivityDrain(reason, minutes);
    if (drain > 0) {
      const res = changeEnergy(energyState, -drain);
      store.setState({ energy: res.state });
      emit(DOMAIN_EVENTS.ENERGY_CHANGED, res.state.current);

      if (res.nowExhausted) {
        this._triggerExhaustionSequence();
        return;
      }

      if (res.showWarn50) {
        this._showEnergy50Toast();
      } else if (res.showWarn25) {
        this.showPromptFeedback('Energi kamu hampir habis!', 2500);
      }
      return;
    }

    // Normal tick passive drain (1.5 per game hour -> 1 per 40 game minutes)
    if (reason === 'tick') {
      this._passiveMinuteAccumulator = (this._passiveMinuteAccumulator || 0) + minutes;
      if (this._passiveMinuteAccumulator >= 40) {
        const pDrain = Math.floor(this._passiveMinuteAccumulator / 40);
        this._passiveMinuteAccumulator %= 40;
        const res = changeEnergy(energyState, -pDrain);
        store.setState({ energy: res.state });
        emit(DOMAIN_EVENTS.ENERGY_CHANGED, res.state.current);

        if (res.nowExhausted) {
          this._triggerExhaustionSequence();
          return;
        }

        if (res.showWarn50) {
          this._showEnergy50Toast();
        } else if (res.showWarn25) {
          this.showPromptFeedback('Energi kamu hampir habis!', 2500);
        }
      }
    }
  }

  _toggleVehicle() {
    if (document.querySelector('.dialogue-panel:not([style*="display: none"])')) return;
    if (this._mapManager?.isTransitioning) return;
    if (!this._player) return;

    const store = this.game.registry.get('store');
    const state = store?.getState() || {};
    const config = this.cache.json.get('phase1config') || {};

    if (this._player.isMounted) {
      this._player.dismount(null, () => {
        const currentMap = this._mapManager?.currentMapId || 'town_hub';
        if (currentMap === 'town_hub') {
          const spawnX = this._player.x + (this._player.facing === 'left' ? 24 : -24);
          this._spawnParkedMotor(spawnX, this._player.y, 'town_hub');
        } else {
          this._removeParkedMotor();
          if (store) {
            store.setState({ vehicle: { mounted: false, parked: null } });
          }
        }
        this.showPromptFeedback('Turun dari motor');
      });
    } else {
      const check = canMountVehicle(state, this._mapManager?.currentMapId || 'home', config.vehicle);
      if (!check.canMount) {
        this.showPromptFeedback(check.reason, 3000);
        return;
      }

      this._player.mount(() => {
        this._removeParkedMotor();
        if (store) {
          store.setState({ vehicle: { mounted: true, parked: null } });
        }
        this.showPromptFeedback('Menaiki motor [Kecepatan 1.8x]');
      });
    }
  }

  _syncParkedMotor() {
    this._removeParkedMotor();
    const store = this.game.registry.get('store');
    const parked = store?.getState()?.vehicle?.parked;
    const currentMapId = this._mapManager?.currentMapId;
    if (parked && parked.mapId === currentMapId && this.textures.exists('prop_motor_parkir')) {
      this._parkedMotorProp = this.add.sprite(parked.x, parked.y, 'prop_motor_parkir');
      this._parkedMotorProp.setOrigin(0.5, 1.0);
      this._parkedMotorProp.setDepth(parked.y);
    }
  }

  _spawnParkedMotor(x, y, mapId = null) {
    this._removeParkedMotor();
    const targetMap = mapId || this._mapManager?.currentMapId || 'town_hub';
    const store = this.game.registry.get('store');
    if (store) {
      store.setState({
        vehicle: {
          mounted: false,
          parked: { mapId: targetMap, x: Math.round(x), y: Math.round(y) }
        }
      });
    }
    if (this._mapManager?.currentMapId === targetMap && this.textures.exists('prop_motor_parkir')) {
      this._parkedMotorProp = this.add.sprite(x, y, 'prop_motor_parkir');
      this._parkedMotorProp.setOrigin(0.5, 1.0);
      this._parkedMotorProp.setDepth(y);
    }
  }

  _removeParkedMotor() {
    if (this._parkedMotorProp) {
      try { this._parkedMotorProp.destroy(); } catch (_) {}
      this._parkedMotorProp = null;
    }
  }

  _checkInteractables() {
    if (this._feedbackUntil && Date.now() < this._feedbackUntil) {
      return;
    }

    const px = this._player.x;
    const py = this._player.y;
    const facing = this._player.facing || 'down';
    const camW = this.cameras.main.width || 960;
    const camH = this.cameras.main.height || 540;

    const npcs = this._mapManager?.currentLayout?.npcs || (this._mapManager ? this._mapManager.getLayout(this._mapManager.currentMapId)?.npcs : []) || [];
    const store = this.game.registry.get('store');
    const tutorial = store?.getState()?.tutorial;
    const activeTargetId = tutorial?.active ? tutorial.targetId : null;

    const best = findBestInteractionTarget(
      { x: px, y: py, facing },
      this._interactables || [],
      npcs || [],
      activeTargetId
    );

    if (best) {
      this._currentInteractable = best.target;
      this._currentCandidateMeta = best;

      // Position prompt at bottom-center of screen
      this._promptText.setPosition(camW / 2, camH - 20);
      this._promptText.setText(best.prompt || 'Tekan [E]');
      this._promptText.setVisible(true);

      if (Phaser.Input.Keyboard.JustDown(this.keyE) || Phaser.Input.Keyboard.JustDown(this.keySpace)) {
        if (best.entityType === 'npc') {
          const npc = best.target;
          if (npc.dialogId) {
            startDialogue(npc.dialogId, npc.id);
          }
        } else {
          this._openInteraction(best.target);
        }
      }
    } else {
      this._currentInteractable = null;
      this._currentCandidateMeta = null;
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
        if (this._tutorialManager) {
          const check = this._tutorialManager.canEnterBuilding(this._mapManager.currentMapId, int.targetMap);
          if (!check.allowed) {
            this.showPromptFeedback(check.reason, 3000);
            return;
          }
        }
        // Auto-dismount and park motor outside when entering building (Rule 75 §1 & §6)
        if (this._player?.isMounted) {
          this._player.dismount('Motor diparkir di depan pintu');
          const parkX = Math.round(this._player.x);
          const parkY = Math.round(this._player.y);
          const fromMap = this._mapManager?.currentMapId || 'town_hub';
          if (store) {
            store.setState({
              vehicle: {
                mounted: false,
                parked: { mapId: fromMap, x: parkX, y: parkY }
              }
            });
          }
          this._removeParkedMotor();
        }
        this._mapManager.transitionTo(int.targetMap, int.targetSpawn, int.openingHoursId);
        return;
      }
    }

    // 2. Sleep in bed (Rule 72 §4 & Rule 74 §1)
    if (int.action === 'sleep' || int.activityId === 'tidur_malam' || int.activityId === 'tidur') {
      const clock = store?.getState()?.clock || {};
      const diff = getTimeUntilWakeup(clock);
      showTimeSkip({
        title: 'Tidur di Kamar',
        minutes: diff,
        costText: 'Energi Pulih 100%',
        onComplete: () => {
          if (window.__LJ__) window.__LJ__.advanceTime(diff, 'sleep');
          if (store) {
            const st = store.getState();
            store.setState({
              gasoline: 100,
              energy: { current: 100, max: 100, exhaustionCount: st?.energy?.exhaustionCount || 0 }
            });
          }
          emit(DOMAIN_EVENTS.ACTIVITY_COMPLETED, { activityId: 'tidur', action: 'sleep' });
        }
      });
      return;
    }

    // 2b. Makan di rumah (Rule 74 §1: makan_rumah +40 Energi, 20 menit, gratis)
    if (int.activityId === 'makan_rumah' || int.action === 'eat_home') {
      showTimeSkip({
        title: 'Makan di Dapur Ibu',
        minutes: 20,
        costText: '+40 Energi (Gratis)',
        onComplete: () => {
          if (window.__LJ__) window.__LJ__.advanceTime(20, 'makan_rumah');
          this.showPromptFeedback('Makan masakan Ibu yang lezat (+40 Energi)');
          emit(DOMAIN_EVENTS.ACTIVITY_COMPLETED, { activityId: 'makan_rumah', action: 'eat_home' });
        }
      });
      return;
    }

    // 2c. Celengan Ayam (Rule 82 T06)
    if (int.activityId === 'celengan_ayam' || int.action === 'deposit_savings') {
      const state = store?.getState();
      const currentCash = getCash(state?.ledger);
      if (currentCash < 100000) {
        this.showPromptFeedback('Uang kas kamu kurang dari Rp100.000 untuk ditabung.');
        return;
      }
      const clock = state?.clock || {};
      const depositEntry = createSavingsDepositEntry(clock.day || 1, clock.month || 1, 100000, clock.timeOfDay || 480);
      const res = addEntry(state.ledger, depositEntry);
      if (res.error) {
        this.showPromptFeedback(res.error);
        return;
      }
      store.setState({ ledger: res.ledger, savingsEver: true });
      emit(DOMAIN_EVENTS.CASH_CHANGED, getCash(res.ledger));
      emit(DOMAIN_EVENTS.SAVINGS_DEPOSITED, { amount: 100000 });
      this.showPromptFeedback('Menyisihkan Rp100.000 ke Celengan Ayam!');
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
        if (int.activityId === 'pelajaran_sekolah') {
          const tutStep = this._tutorialManager?.getCurrentStep();
          if (tutStep?.id === 'T09') {
            actMinutes = 180; // Sesi 1: 07:00 -> 10:00
          } else if (tutStep?.id === 'T12') {
            actMinutes = 240; // Sesi 2: 10:30 -> 14:30
          } else {
            actMinutes = 120;
          }
        } else {
          actMinutes = int.activityId === 'main_game' ? 60 : (int.activityId === 'baca_buku' ? 60 : 30);
        }
      }

      // Check energy (Rule 74 §1: disable heavy activities if exhausted or insufficient)
      const st = store?.getState();
      const check = canPerformActivity(st?.energy, int.activityId, actMinutes);
      if (!check.canPerform) {
        this.showPromptFeedback(check.reason, 3500);
        return;
      }

      showTimeSkip({
        title: int.prompt.replace(/^Tekan \[E\]\s*/, ''),
        minutes: actMinutes,
        onComplete: () => {
          if (window.__LJ__) window.__LJ__.advanceTime(actMinutes, int.activityId);
          emit(DOMAIN_EVENTS.ACTIVITY_COMPLETED, { activityId: int.activityId, action: int.action });
        }
      });
      return;
    }

    // 4. Shop / Vendor / Savings Modal (Rule 79)
    if (int.action === 'savings' || int.type === 'savings') {
      createShopModal(uiContainer, store, 'rumah');
      return;
    }

    if (int.action === 'refuel' || int.activityId === 'isi_bensin') {
      createShopModal(uiContainer, store, 'spbu');
      return;
    }

    const shopId = int.shopId || (int.type === 'shop' ? int.panel || int.id : null) || int.locationId;
    if (shopId) {
      if (int.openingHoursId || DEFAULT_OPENING_HOURS[shopId]) {
        const checkId = int.openingHoursId || shopId;
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
      const canonicalShopId = shopId === 'kantin' ? 'kantin_sekolah'
        : (shopId === 'gamecenter' ? 'game_center_kafe'
        : (shopId === 'kosmetik' ? 'toko_kosmetik' : shopId));
      createShopModal(uiContainer, store, canonicalShopId, { categoryFilter: int.categoryFilter || null });
      return;
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
    if (this._hotbar) {
      this._hotbar.destroy();
      this._hotbar = null;
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
      getCash: () => getCash(this.game.registry.get('store')?.getState()?.ledger),
      grantAllowance: () => {
        const s = this.game.registry.get('store');
        if (!s) return null;
        const st = s.getState();
        const clock = st.clock || {};
        const entry = createAllowanceEntry(clock.day || 1, clock.month || 1, clock.timeOfDay || 360);
        const res = addEntry(st.ledger, entry);
        if (!res.error) {
          const missions = (st.missions || []).map(m => m.id === 'M1' ? { ...m, completed: true } : m);
          s.setState({ ledger: res.ledger, missions });
          emit(DOMAIN_EVENTS.ALLOWANCE_GRANTED, { amount: 1000000 });
          emit(DOMAIN_EVENTS.CASH_CHANGED, getCash(res.ledger));
          return res.ledger;
        }
        return null;
      },
      chooseOption: (i) => chooseOption(i),
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
        this._updateEnergyDrain(minutes, reason);
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
      getEnergy: () => this.game.registry.get('store')?.getState()?.energy,
      setEnergy: (val) => {
        const s = this.game.registry.get('store');
        if (s) {
          const cur = s.getState()?.energy?.current ?? 100;
          const nextState = changeEnergy(s.getState()?.energy || { current: 100, max: 100 }, val - cur).state;
          s.setState({ energy: nextState });
          emit(DOMAIN_EVENTS.ENERGY_CHANGED, nextState);
        }
      },
      getInventory: () => this.game.registry.get('store')?.getState()?.inventory,
      addItem: (itemId, count = 1) => {
        const s = this.game.registry.get('store');
        if (!s) return null;
        const inv = s.getState()?.inventory || createInventory(5);
        const res = domainAddItem(inv, itemId, count);
        if (res.ok) {
          s.setState({ inventory: res.inventory });
        }
        return res;
      },
      useHotbarItem: (idx) => this._useHotbarItem(idx),
      openShop: (locId) => {
        const uiContainer = document.getElementById('ui-container') || document.body;
        return createShopModal(uiContainer, this.game.registry.get('store'), locId);
      },
      closeShop: () => closeShopModal(),
      toggleVehicle: () => this._toggleVehicle(),
      isMounted: () => Boolean(this._player?.isMounted),
      measureSpeed: () => this._player ? this._player.measureSpeed() : 0,
      getGasoline: () => this.game.registry.get('store')?.getState()?.gasoline,
      setGasoline: (val) => this.game.registry.get('store')?.setState({ gasoline: Math.max(0, Math.min(100, val)) }),
      getParkedMotor: () => this.game.registry.get('store')?.getState()?.vehicle?.parked,
      simulateMovingFuel: (deltaMs) => {
        if (this._player) {
          this._player.isMounted = true;
          this._player.moving = true;
          this._player._drainGasoline(deltaMs);
        }
      },
      startDialogue: (id, npcId, onClose) => startDialogue(id, npcId, onClose),
      choose: (i) => chooseOption(i),
      getDialogueState: () => getDialogueState(),
      closeDialogue: () => closeDialogue(),
      completeMission: (id, title) => this._missionFx ? this._missionFx.trigger(id, title) : false,
      listNPCs: (mapId) => this._mapManager ? this._mapManager.listNPCs(mapId) : [],
      collisionProbe: (mapId) => this._mapManager ? this._mapManager.runCollisionProbe(mapId) : { allPassed: false },
      getNavGrid: () => this._navGrid
    };
    console.info('[Debug] window.__LJ__ aktif dengan time system, map & dialogue controls');
  }

  _initNavGrid() {
    if (!this._mapManager) return;
    const colliders = this._mapManager.getColliderRects();
    const layout = this._mapManager.currentLayout;
    const ts = this._tileSize || 32;
    const mapW = (layout?.world?.widthTiles || layout?.width || 30) * ts;
    const mapH = (layout?.world?.heightTiles || layout?.height || 24) * ts;
    this._navGrid = new NavigationGrid(mapW, mapH, colliders, 16);
  }

  _handleClickToMove(pointer) {
    if (!this._player || !this._navGrid) return;

    // Ignore clicks on DOM UI overlays!
    const clientX = pointer.event.clientX;
    const clientY = pointer.event.clientY;
    const domEl = document.elementFromPoint(clientX, clientY);
    if (domEl) {
      if (domEl.closest('#ui-container > *') ||
          domEl.closest('.lj-panel') ||
          domEl.closest('.lj-modal-backdrop') ||
          domEl.closest('.hud-container') ||
          domEl.closest('.hud-hotbar-container') ||
          domEl.closest('.dialogue-panel') ||
          domEl.closest('.dialogue-overlay') ||
          domEl.closest('.time-skip-backdrop') ||
          domEl.closest('.shop-modal-panel') ||
          domEl.closest('.backpack-modal-panel') ||
          domEl.closest('.item-action-popup')) {
        return; // Clicked on UI, do not move player!
      }
    }

    // Convert screen coordinates to world coordinates taking camera zoom & scroll into account
    const wp = this.cameras.main.getWorldPoint(pointer.x, pointer.y);

    // Check if target is an interactable or NPC
    const targetObj = this._findClickableAt(wp.x, wp.y);

    let destX = wp.x;
    let destY = wp.y;

    if (targetObj) {
      if (targetObj.targetX !== undefined && targetObj.targetY !== undefined) {
        destX = targetObj.targetX;
        destY = targetObj.targetY;
      }
    }

    const path = this._navGrid.findPath(this._player.sprite.x, this._player.sprite.y, destX, destY);
    if (path && path.length > 0) {
      this._player.setPath(path, targetObj);
    }
  }

  _findClickableAt(wx, wy) {
    const ts = this._tileSize || 32;

    // 1. Check NPCs
    if (this._npcManager && this._npcManager.npcs) {
      for (const npc of this._npcManager.npcs) {
        const dist = Math.hypot(wx - npc.x, wy - npc.y);
        if (dist < 32) {
          return {
            type: 'npc',
            npc: npc,
            targetX: npc.x,
            targetY: npc.y
          };
        }
      }
    }

    // 2. Check interactables (bed, counter, door, etc.)
    for (const int of (this._interactables || [])) {
      const rx0 = (int.x || 0) * ts;
      const ry0 = (int.y || 0) * ts;
      const rx1 = rx0 + (int.w || 1) * ts;
      const ry1 = ry0 + (int.h || 1) * ts;

      if (wx >= rx0 - 16 && wx <= rx1 + 16 && wy >= ry0 - 16 && wy <= ry1 + 16) {
        const closestX = Math.max(rx0, Math.min(wx, rx1));
        const closestY = Math.max(ry0, Math.min(wy, ry1));
        return {
          type: 'interactable',
          interactable: int,
          targetX: closestX,
          targetY: closestY
        };
      }
    }

    return null;
  }

  _onArrivalAtTarget(target) {
    if (!target) return;

    if (target.type === 'npc' && target.npc) {
      const uiContainer = document.getElementById('ui-container') || document.body;
      if (this._npcManager) {
        this._npcManager.openDialog(target.npc, uiContainer);
      }
      return;
    }

    if (target.type === 'interactable' && target.interactable) {
      this._openInteraction(target.interactable);
      return;
    }
  }
}
