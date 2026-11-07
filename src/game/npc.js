/**
 * npc.js — NPC Manager for Life Journey.
 * Spawns NPCs at layout positions, handles interaction zones and dialog triggers.
 */

export class NPCManager {
  /**
   * @param {Phaser.Scene} scene
   * @param {object[]} npcDefs - from layout.npcs
   */
  constructor(scene, npcDefs) {
    this.scene = scene;
    this.npcs = [];

    for (const def of npcDefs) {
      this._spawnNPC(def);
    }
  }

  _spawnNPC(def) {
    const scene = this.scene;
    const ts = 32;
    const x = def.x * ts + ts / 2;
    const y = def.y * ts + ts / 2;

    // NPC body (placeholder)
    const body = scene.add.rectangle(x, y, 16, 24, def.color ?? 0xC9A27A);
    body.setDepth(500 + y / 1000);

    // Name label
    const label = scene.add.text(x, y - 20, def.name ?? def.id ?? 'NPC', {
      font: '10px sans-serif',
      fill: '#FBF6EA',
      backgroundColor: '#121A2E',
      padding: { x: 2, y: 1 },
    });
    label.setOrigin(0.5, 1);
    label.setDepth(600);

    // Interaction zone (invisible circle)
    const zone = scene.add.circle(x, y, 48, 0x000000, 0);
    zone.setDepth(0);

    this.npcs.push({
      def,
      body,
      label,
      zone,
      x,
      y,
      inRange: false,
    });
  }

  /**
   * @param {number} time
   * @param {object} player - PlayerController
   */
  update(time, player) {
    if (!player) return;

    for (const npc of this.npcs) {
      const dx = player.x - npc.x;
      const dy = player.y - npc.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      const inRange = dist < 48;

      if (inRange !== npc.inRange) {
        npc.inRange = inRange;
        // Highlight on enter
        npc.body.setFillStyle(inRange ? 0xD9A441 : (npc.def.color ?? 0xC9A27A));

        if (inRange && npc.def.dialog) {
          // Dispatch dialog event
          document.dispatchEvent(new CustomEvent('lj:npcInteract', {
            detail: { npcId: npc.def.id, dialog: npc.def.dialog },
          }));
        }
      }
    }
  }
}
