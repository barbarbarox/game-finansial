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
    if (this._closestInRange) {
      this._openPanel(this._closestInRange.panelId, this._closestInRange.def);
    }
  }

  _openPanel(panelId, def) {
    if (!panelId) return;
    document.dispatchEvent(new CustomEvent('lj:openPanel', {
      detail: { panel: panelId, locationId: def.locationId, def },
    }));
  }
}
