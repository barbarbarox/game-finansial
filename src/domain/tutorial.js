/**
 * tutorial.js — Guided Tutorial and Story System (Rule 82).
 * Manages the mandatory first-time guided tutorial "Hari Pertama Bulan Baru" (T01–T20).
 */

import { DOMAIN_EVENTS, subscribe, emit } from './events.js';

export const TUTORIAL_MAP_GRAPH = {
  home: { town_hub: { x: 5, y: 18 } },
  town_hub: {
    home: { x: 6, y: 21 },
    school: { x: 10, y: 8 },
    minimarket: { x: 27, y: 7 },
    toko_kosmetik: { x: 35, y: 7 },
    spbu: { x: 36, y: 13 },
    game_center: { x: 30, y: 21 }
  },
  school: { town_hub: { x: 16, y: 19 } },
  minimarket: { town_hub: { x: 12, y: 16 } },
  toko_kosmetik: { town_hub: { x: 11, y: 14 } },
  spbu: { town_hub: { x: 12, y: 16 } },
  game_center: { town_hub: { x: 13, y: 16 } }
};

export const TARGET_COORDINATES = {
  home: {
    npc_ibu: { x: 17, y: 12, label: 'Ibu' },
    meja_makan: { x: 21, y: 15, label: 'Meja Makan' },
    celengan_ayam: { x: 7, y: 2.5, label: 'Celengan Ayam' },
    kasur_single: { x: 5, y: 3, label: 'Kasur Tidur' }
  },
  school: {
    meja_siswa_kursi: { x: 7, y: 4, label: 'Meja Kelas' },
    npc_penjual_kantin: { x: 20, y: 3, label: 'Kantin Sekolah' },
    meja_baca: { x: 6, y: 17, label: 'Meja Perpustakaan' },
    npc_budi: { x: 10, y: 14, label: 'Budi' }
  },
  minimarket: {
    npc_kasir_minimarket: { x: 13, y: 8, label: 'Kasir Mini Mart' }
  },
  toko_kosmetik: {
    npc_penjaga_kosmetik: { x: 11, y: 7, label: 'Mbak Maya (Kosmetik)' }
  },
  spbu: {
    npc_petugas_spbu: { x: 12, y: 8, label: 'Pak Doni (SPBU)' }
  },
  game_center: {
    arcade_a: { x: 10, y: 8, label: 'Mesin Arcade' }
  }
};

/**
 * Create initial tutorial state.
 * @param {object|null} saved
 * @param {boolean} isNewGame
 * @returns {object}
 */
export function createTutorialState(saved = null, isNewGame = false) {
  if (saved && typeof saved === 'object') {
    return {
      active: Boolean(saved.active),
      stepIndex: saved.stepIndex || 0,
      completedSteps: Array.isArray(saved.completedSteps) ? saved.completedSteps : [],
      completed: Boolean(saved.completed),
      pausedClock: saved.pausedClock !== false,
      stepStartTime: saved.stepStartTime || Date.now(),
      stepProgress: saved.stepProgress || {}
    };
  }

  // New Game defaults: tutorial active
  return {
    active: isNewGame,
    stepIndex: 0,
    completedSteps: [],
    completed: !isNewGame,
    pausedClock: isNewGame,
    stepStartTime: Date.now(),
    stepProgress: {}
  };
}

export class TutorialManager {
  /**
   * @param {object} store
   * @param {object} tutorialData
   * @param {object} [options]
   */
  constructor(store, tutorialData, options = {}) {
    this.store = store;
    this.data = tutorialData || { steps: [] };
    this.steps = this.data.steps || [];
    this.options = options;
    this.unsubscribers = [];
    this._moveStartPos = null;
    this._accumulatedTiles = 0;
  }

  /**
   * Initialize tutorial listeners and state.
   */
  init() {
    const state = this.store.getState();
    let tutState = state.tutorial;

    if (!tutState) {
      tutState = createTutorialState(null, true);
      this.store.setState({ tutorial: tutState });
    }

    if (!tutState.active || tutState.completed) {
      return;
    }

    this._setupListeners();
    this._syncCurrentStep();
  }

  destroy() {
    for (const unsub of this.unsubscribers) {
      if (typeof unsub === 'function') unsub();
    }
    this.unsubscribers = [];
  }

  /**
   * Get current tutorial step definition.
   */
  getCurrentStep() {
    const tutState = this.store.getState()?.tutorial;
    if (!tutState || !tutState.active || tutState.completed) return null;
    return this.steps[tutState.stepIndex] || null;
  }

  /**
   * Check if clock should be paused.
   */
  isClockPaused() {
    const tut = this.store.getState()?.tutorial;
    return Boolean(tut && tut.active && !tut.completed && tut.pausedClock);
  }

  /**
   * Check if player can enter target building (Rule 82 §4.6 Soft-Lock).
   * @param {string} currentMap
   * @param {string} targetMap
   * @returns {{ allowed: boolean, reason?: string }}
   */
  canEnterBuilding(currentMap, targetMap) {
    const step = this.getCurrentStep();
    if (!step) return { allowed: true };

    // Always allow returning to town_hub or home
    if (targetMap === 'town_hub') return { allowed: true };

    const act = step.act;
    const targetMapRequired = step.target?.map || (step.complete?.map);

    // If step explicitly targets this map or current act matches
    if (targetMapRequired === targetMap) {
      return { allowed: true };
    }

    if (act === 'rumah' && targetMap === 'home') return { allowed: true };
    if (act === 'sekolah' && targetMap === 'school') return { allowed: true };
    if (act === 'kota') {
      // In town act, allow target building
      if (step.id === 'T14' && targetMap === 'minimarket') return { allowed: true };
      if (step.id === 'T15' && targetMap === 'toko_kosmetik') return { allowed: true };
      if (step.id === 'T17' && targetMap === 'spbu') return { allowed: true };
      if (step.id === 'T18' && targetMap === 'game_center') return { allowed: true };
    }
    if (act === 'penutup' && targetMap === 'home') return { allowed: true };

    return {
      allowed: false,
      reason: `Selesaikan misi: "${step.title}" terlebih dahulu!`
    };
  }

  /**
   * Get destination coordinates in world for guidance arrow.
   * @param {string} currentMapId
   * @returns {{ mapId: string, x: number, y: number, label: string }|null}
   */
  getTargetInfo(currentMapId) {
    const step = this.getCurrentStep();
    if (!step) return null;

    const target = step.target || {};
    if (target.type === 'none' || target.type === 'hud') {
      return null;
    }

    const targetMap = target.map || currentMapId;

    // 1. If target is on the current map
    if (targetMap === currentMapId) {
      const coords = TARGET_COORDINATES[currentMapId]?.[target.ref];
      if (coords) {
        return {
          mapId: currentMapId,
          x: coords.x,
          y: coords.y,
          label: coords.label || step.title
        };
      }
    }

    // 2. If target is on another map, point to the exit/door leading there
    const doors = TUTORIAL_MAP_GRAPH[currentMapId];
    if (doors) {
      // Direct door to target map
      if (doors[targetMap]) {
        return {
          mapId: currentMapId,
          x: doors[targetMap].x,
          y: doors[targetMap].y,
          label: `Menuju ${targetMap}`
        };
      }
      // If we are indoors, door to town_hub
      if (doors.town_hub) {
        return {
          mapId: currentMapId,
          x: doors.town_hub.x,
          y: doors.town_hub.y,
          label: 'Keluar ke Kota'
        };
      }
    }

    return null;
  }

  /**
   * Complete current step and advance to next.
   */
  advanceStep(reason = 'completed') {
    const state = this.store.getState();
    const tut = state.tutorial;
    if (!tut || !tut.active || tut.completed) return;

    const currentStep = this.steps[tut.stepIndex];
    if (!currentStep) return;

    const nextIndex = tut.stepIndex + 1;
    const isFinished = nextIndex >= this.steps.length;

    const completedSteps = [...tut.completedSteps, currentStep.id];
    const newTutState = {
      ...tut,
      stepIndex: nextIndex,
      completedSteps,
      completed: isFinished,
      active: !isFinished,
      pausedClock: !isFinished,
      stepStartTime: Date.now(),
      stepProgress: {}
    };

    this.store.setState({ tutorial: newTutState });

    // Emit event
    if (isFinished) {
      emit(DOMAIN_EVENTS.TUTORIAL_COMPLETED, { completedSteps });
      this._showTutorialFinishedModal();
    } else {
      emit(DOMAIN_EVENTS.TUTORIAL_STEP_CHANGED, {
        stepIndex: nextIndex,
        step: this.steps[nextIndex],
        prevStep: currentStep
      });
      this._syncCurrentStep();
    }
  }

  /**
   * Skip current step (anti-macet button).
   */
  skipCurrentStep() {
    this.advanceStep('skipped');
  }

  // ── Internal Listeners ────────────────────────────────────────────────────

  _setupListeners() {
    this.unsubscribers.push(
      subscribe(DOMAIN_EVENTS.PLAYER_MOVED, (payload) => this._onPlayerMoved(payload)),
      subscribe(DOMAIN_EVENTS.DIALOGUE_OPENED, (payload) => this._onDialogueOpened(payload)),
      subscribe(DOMAIN_EVENTS.ALLOWANCE_GRANTED, (payload) => this._onAllowanceGranted(payload)),
      subscribe(DOMAIN_EVENTS.ACTIVITY_COMPLETED, (payload) => this._onActivityCompleted(payload)),
      subscribe(DOMAIN_EVENTS.BUDGET_SET, (payload) => this._onBudgetSet(payload)),
      subscribe(DOMAIN_EVENTS.SAVINGS_DEPOSITED, (payload) => this._onSavingsDeposited(payload)),
      subscribe(DOMAIN_EVENTS.MAP_CHANGED, (payload) => this._onMapChanged(payload)),
      subscribe(DOMAIN_EVENTS.PURCHASE_COMPLETED, (payload) => this._onPurchaseCompleted(payload)),
      subscribe(DOMAIN_EVENTS.ITEM_USED, (payload) => this._onItemUsed(payload)),
      subscribe(DOMAIN_EVENTS.VEHICLE_MOUNTED, (payload) => this._onVehicleMounted(payload)),
      subscribe(DOMAIN_EVENTS.REFUELED, (payload) => this._onRefueled(payload)),
      subscribe(DOMAIN_EVENTS.BACKPACK_OPENED, (payload) => this._onBackpackOpened(payload))
    );
  }

  _syncCurrentStep() {
    const step = this.getCurrentStep();
    if (!step) return;

    this._moveStartPos = null;
    this._accumulatedTiles = 0;

    // Check T19 auto-complete if energy already >= 50%
    if (step.id === 'T19') {
      const energy = this.store.getState()?.energy;
      const curEnergy = typeof energy === 'object' ? energy.current : Number(energy || 100);
      if (curEnergy >= 50) {
        setTimeout(() => this.advanceStep('energy_sufficient'), 500);
      }
    }
  }

  _onPlayerMoved(payload) {
    const step = this.getCurrentStep();
    if (!step || step.id !== 'T01') return;

    const { x, y } = payload || {};
    if (x === undefined || y === undefined) return;

    if (!this._moveStartPos) {
      this._moveStartPos = { x, y };
      return;
    }

    const dx = Math.abs(x - this._moveStartPos.x) / 32;
    const dy = Math.abs(y - this._moveStartPos.y) / 32;
    const dist = Math.sqrt(dx * dx + dy * dy);

    if (dist >= (step.complete?.minDistanceTiles || 3)) {
      this.advanceStep();
    }
  }

  _onDialogueOpened(payload) {
    const step = this.getCurrentStep();
    if (!step || step.id !== 'T02') return;

    if (payload?.npcId === 'npc_ibu' || payload?.dialogueId?.includes('ibu')) {
      this.advanceStep();
    }
  }

  _onAllowanceGranted(payload) {
    const step = this.getCurrentStep();
    if (!step || step.id !== 'T03') return;
    this.advanceStep();
  }

  _onActivityCompleted(payload) {
    const step = this.getCurrentStep();
    if (!step) return;

    const actId = payload?.activityId;

    if (step.id === 'T04' && (actId === 'makan_rumah' || actId === 'makan')) {
      this.advanceStep();
    } else if (step.id === 'T09' && (actId === 'pelajaran_sekolah' || actId === 'ikut_pelajaran_sesi1')) {
      this.advanceStep();
    } else if (step.id === 'T12' && (actId === 'pelajaran_sekolah' || actId === 'ikut_pelajaran_sesi2')) {
      this.advanceStep();
    } else if (step.id === 'T13' && (actId === 'baca_perpustakaan' || actId === 'baca_buku')) {
      this.advanceStep();
    } else if (step.id === 'T18' && (actId === 'main_game' || actId === 'game_arcade')) {
      this.advanceStep();
    } else if (step.id === 'T20' && (actId === 'tidur' || actId === 'sleep')) {
      this.advanceStep();
    }
  }

  _onBudgetSet(payload) {
    const step = this.getCurrentStep();
    if (!step || step.id !== 'T05') return;
    this.advanceStep();
  }

  _onSavingsDeposited(payload) {
    const step = this.getCurrentStep();
    if (!step || step.id !== 'T06') return;
    const min = step.complete?.minAmount || 100000;
    if ((payload?.amount || 100000) >= min) {
      this.advanceStep();
    }
  }

  _onMapChanged(payload) {
    const step = this.getCurrentStep();
    if (!step) return;

    const map = payload?.mapId;
    if (step.id === 'T07' && map === 'town_hub') {
      this.advanceStep();
    } else if (step.id === 'T08' && map === 'school') {
      this.advanceStep();
    }
  }

  _onPurchaseCompleted(payload) {
    const step = this.getCurrentStep();
    if (!step) return;

    const shop = payload?.shopId;

    if (step.id === 'T10' && (shop?.includes('kantin'))) {
      this.advanceStep();
    } else if (step.id === 'T14' && (shop?.includes('minimarket'))) {
      const tut = this.store.getState()?.tutorial || {};
      const prog = tut.stepProgress || {};
      prog.purchased = true;
      this.store.setState({ tutorial: { ...tut, stepProgress: prog } });
      if (prog.backpackOpened) this.advanceStep();
    } else if (step.id === 'T15' && (shop?.includes('kosmetik'))) {
      this.advanceStep();
    }
  }

  _onBackpackOpened() {
    const step = this.getCurrentStep();
    if (!step || step.id !== 'T14') return;

    const tut = this.store.getState()?.tutorial || {};
    const prog = tut.stepProgress || {};
    prog.backpackOpened = true;
    this.store.setState({ tutorial: { ...tut, stepProgress: prog } });
    if (prog.purchased) this.advanceStep();
  }

  _onItemUsed(payload) {
    const step = this.getCurrentStep();
    if (!step) return;

    if (step.id === 'T11' || step.id === 'T19') {
      this.advanceStep();
    }
  }

  _onVehicleMounted() {
    const step = this.getCurrentStep();
    if (!step || step.id !== 'T16') return;
    this.advanceStep();
  }

  _onRefueled(payload) {
    const step = this.getCurrentStep();
    if (!step || step.id !== 'T17') return;
    this.advanceStep();
  }

  _showTutorialFinishedModal() {
    const uiContainer = document.getElementById('ui-container') || document.body;
    const modal = document.createElement('div');
    modal.className = 'lj-modal-backdrop tutorial-finish-modal';
    modal.innerHTML = `
      <div class="lj-modal-dialog" style="max-width: 480px; text-align: center; background: #1F2A44; border: 2px solid #D9A441; border-radius: 8px; padding: 24px; color: #F7EEDA; box-shadow: 0 12px 36px rgba(0,0,0,0.8);">
        <h2 style="color: #D9A441; font-size: 20px; margin-bottom: 12px;">🎉 Tutorial Hari Pertama Selesai!</h2>
        <p style="font-size: 14px; line-height: 1.5; margin-bottom: 16px;">
          Hebat! Kamu telah mempelajari semua dasar kehidupan finansial: menerima uang saku, menyusun anggaran, menabung, mengelola energi, belanja bijak, dan bermotor.
        </p>
        <p style="font-size: 13px; color: #9FB3C8; margin-bottom: 20px;">
          Mulai sekarang, jam permainan berjalan penuh secara real-time. Nikmati petualanganmu di Life Journey!
        </p>
        <button type="button" class="lj-btn primary" id="btn-finish-tutorial" style="padding: 10px 24px; font-weight: bold;">Mulai Permainan Bebas</button>
      </div>
    `;
    uiContainer.appendChild(modal);

    const btn = modal.querySelector('#btn-finish-tutorial');
    if (btn) {
      btn.addEventListener('click', () => {
        modal.remove();
      });
    }
  }
}

