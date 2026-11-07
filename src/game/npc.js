/**
 * npc.js — NPC Manager for Life Journey.
 * Spawns NPCs at layout positions, handles proximity detection,
 * floating interaction prompts, and triggers the NPC interaction choices dialog.
 */

import { createNPCDialog, closeNPCDialog, isNPCDialogOpen } from '../ui/npcDialog.js';

export class NPCManager {
  /**
   * @param {Phaser.Scene} scene
   * @param {object[]} npcDefs - from layout.npcs
   */
  constructor(scene, npcDefs) {
    this.scene = scene;
    this.npcs = [];
    this.activeNpc = null;

    for (const def of npcDefs) {
      this._spawnNPC(def);
    }
  }

  _spawnNPC(def) {
    const scene = this.scene;
    const ts = 32;
    const x = def.x * ts + ts / 2;
    const y = def.y * ts + ts / 2;

    // Shadow under NPC
    const shadow = scene.add.ellipse(x, y + 14, 20, 8, 0x121A2E, 0.5);
    shadow.setDepth(490);

    // NPC Sprite or Figure Container
    let body;
    if (scene.textures.exists(def.assetId)) {
      body = scene.add.sprite(x, y + 4, def.assetId, 0);
      body.setOrigin(0.5, 0.95);
      body.setDepth(500 + y / 1000);
    } else {
      body = scene.add.container(x, y);
      body.setDepth(500 + y / 1000);
      const torso = scene.add.rectangle(0, 0, 18, 26, def.color ?? 0xC9A27A);
      const head = scene.add.circle(0, -18, 8, def.color ?? 0xC9A27A);
      const outline = scene.add.rectangle(0, 0, 20, 28);
      outline.setStrokeStyle(1, 0x121A2E);
      body.add([torso, head, outline]);
    }

    // Name label
    const displayName = def.name || def.id || 'NPC';
    const label = scene.add.text(x, y - 36, displayName, {
      font: 'bold 11px sans-serif',
      fill: '#FBF6EA',
      backgroundColor: '#121A2E',
      padding: { x: 4, y: 2 },
    });
    label.setOrigin(0.5, 1);
    label.setDepth(600);

    // Floating interaction prompt bubble
    const promptBubble = scene.add.container(x, y - 56);
    promptBubble.setDepth(1500);
    promptBubble.setVisible(false);

    const promptBg = scene.add.rectangle(0, 0, 96, 20, 0x1F2A44, 0.95);
    promptBg.setStrokeStyle(1, 0xD9A441);
    const promptText = scene.add.text(0, 0, '💬 [E] Bicara', {
      font: 'bold 10px sans-serif',
      fill: '#D9A441',
    }).setOrigin(0.5);
    promptBubble.add([promptBg, promptText]);

    // Subtle floating tween for prompt
    scene.tweens.add({
      targets: promptBubble,
      y: y - 60,
      duration: 600,
      yoyo: true,
      repeat: -1,
      ease: 'Sine.easeInOut'
    });

    this.npcs.push({
      def,
      body,
      shadow,
      label,
      promptBubble,
      x,
      y,
      inRange: false,
      autoOpened: false,
    });
  }

  /**
   * Called every frame in World.update
   * @param {number} time
   * @param {object} player - PlayerController
   */
  update(time, player) {
    if (!player) return;

    const px = player.x;
    const py = player.y;
    const uiContainer = document.getElementById('ui-container') || document.body;

    for (const npc of this.npcs) {
      const dx = px - npc.x;
      const dy = py - npc.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      const inRange = dist < 54;

      if (inRange) {
        if (!npc.inRange) {
          npc.inRange = true;
          npc.promptBubble.setVisible(true);

          // Pilihan interaksi otomatis muncul saat pemain mendekat
          if (!npc.autoOpened && !isNPCDialogOpen()) {
            this.openDialog(npc, uiContainer);
            npc.autoOpened = true;
          }
        }

        // Jika tombol E atau Space ditekan saat berada di dekat NPC
        if (this.scene.keyE && (Phaser.Input.Keyboard.JustDown(this.scene.keyE) || Phaser.Input.Keyboard.JustDown(this.scene.keySpace))) {
          this.openDialog(npc, uiContainer);
        }
      } else {
        if (npc.inRange) {
          npc.inRange = false;
          npc.promptBubble.setVisible(false);
          npc.autoOpened = false;

          // Jika pemain menjauh (dist > 72), tutup dialog otomatis bila aktif untuk NPC ini
          if (this.activeNpc === npc) {
            closeNPCDialog();
            this.activeNpc = null;
          }
        }
      }
    }
  }

  openDialog(npc, container) {
    this.activeNpc = npc;
    createNPCDialog(
      container,
      npc.def,
      (choiceId) => {
        // Choice selected
      },
      () => {
        // Closed
        this.activeNpc = null;
      }
    );
  }
}
