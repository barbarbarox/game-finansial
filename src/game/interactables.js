/**
 * interactables.js — Interactable objects (doors, signs) for Life Journey.
 * Detects player proximity and opens the appropriate panel.
 */

export class InteractableManager {
  /**
   * @param {Phaser.Scene} scene
   * @param {object[]} interactableDefs - from layout.interactables
   * @param {object|null} store - pub-sub store
   */
  constructor(scene, interactableDefs, store) {
    this.scene = scene;
    this.store = store;
    this.interactables = [];
    this._activePanel = null;

    for (const def of interactableDefs) {
      this._register(def);
    }

    // Also listen for E key
    scene.input.keyboard.on('keydown-E', () => {
      this._tryInteract();
    });
    scene.input.keyboard.on('keydown-F', () => {
      this._tryInteract();
    });
  }

  _register(def) {
    const ts = 32;
    const x = def.x * ts;
    const y = def.y * ts;
    const r = def.radius ?? ts;

    // Visual indicator (door marker)
    const marker = this.scene.add.triangle(x, y, 0, -8, 8, 8, -8, 8, 0xD9A441, 0.8);
    marker.setDepth(1000);
    marker.setVisible(false);

    this.interactables.push({
      def,
      x: x + ts / 2,
      y: y + ts / 2,
      radius: r,
      marker,
      inRange: false,
      panelId: def.panelId ?? def.locationId,
    });
  }

  /**
   * @param {object} player - PlayerController
   */
  update(player) {
    if (!player) return;

    let closestInRange = null;
    let minDist = Infinity;

    for (const item of this.interactables) {
      const dx = player.x - item.x;
      const dy = player.y - item.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      const inRange = dist < item.radius;

      item.marker.setVisible(inRange);

      if (inRange && dist < minDist) {
        minDist = dist;
        closestInRange = item;
      }

      item.inRange = inRange;
    }

    this._closestInRange = closestInRange;
  }

  _tryInteract() {
    if (!this._closestInRange) return;
    const def = this._closestInRange.def;

    // 1. Door / Exit transition
    if (def.type === 'door' || def.type === 'exit') {
      if (def.targetMap && this.scene._mapManager) {
        this.scene._mapManager.transitionTo(def.targetMap, def.targetSpawn, def.openingHoursId);
        return;
      }
    }

    // 2. Activity trigger (Time-Skip)
    if (def.type === 'activity') {
      document.dispatchEvent(new CustomEvent('lj:runActivity', {
        detail: { activityId: def.activityId, def }
      }));
      return;
    }

    // 3. Shop or other panel
    this._openPanel(this._closestInRange.panelId, def);
  }

  setInteractables(interactableDefs) {
    for (const item of this.interactables) {
      if (item.marker && item.marker.destroy) {
        item.marker.destroy();
      }
    }
    this.interactables = [];
    this._closestInRange = null;

    for (const def of (interactableDefs || [])) {
      this._register(def);
    }
  }

  _openPanel(panelId, def) {
    if (!panelId) return;
    document.dispatchEvent(new CustomEvent('lj:openPanel', {
      detail: { panel: panelId, locationId: def.locationId, def },
    }));
  }
}
