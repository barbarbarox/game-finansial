/**
 * npc.js — NPC Manager for Life Journey.
 * Spawns NPCs at layout positions, handles proximity detection,
 * floating interaction prompts, and triggers the NPC interaction choices dialog.
 */

import { createNPCDialog, closeNPCDialog, isNPCDialogOpen } from '../ui/npcDialog.js';
import { startDialogue, closeDialogue } from '../ui/dialogueBox.js';

export class NPCManager {
  /**
   * @param {Phaser.Scene} scene
   * @param {object[]} npcDefs - from layout.npcs
   */
  constructor(scene, npcDefs) {
    this.scene = scene;
    this.npcs = [];
    this.activeNpc = null;

    for (const def of (npcDefs || [])) {
      this._spawnNPC(def);
    }
  }

  setNPCs(npcDefs) {
    for (const npc of this.npcs) {
      if (npc.shadow && npc.shadow.destroy) npc.shadow.destroy();
      if (npc.body && npc.body.destroy) npc.body.destroy();
      if (npc.label && npc.label.destroy) npc.label.destroy();
      if (npc.bubble && npc.bubble.destroy) npc.bubble.destroy();
    }
    this.npcs = [];
    this.activeNpc = null;

    for (const def of (npcDefs || [])) {
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
    let textureKey = null;
    let frame = def.frame ?? 0;

    // 0. Explicit assetId match (highest priority, e.g. npc_budi_v6)
    if (def.assetId && scene.textures.exists(def.assetId)) {
      textureKey = def.assetId;
      if (def.assetId === 'npc_sheet_family') {
        frame = def.id === 'npc_ayah' ? 1 : 0;
      } else if (def.assetId === 'npc_sheet_friends') {
        frame = def.id === 'npc_siti' ? 1 : 0;
      } else if (def.assetId === 'npc_sheet_vendors') {
        if (def.id === 'npc_kasir_minimarket' || def.id === 'npc_kasir') frame = 1;
        else if (def.id === 'npc_cindy' || def.id === 'npc_penjaga_kosmetik') frame = 2;
        else if (def.id === 'npc_doni' || def.id === 'npc_petugas_spbu' || def.id === 'npc_pak_anto') frame = 3;
        else if (def.id === 'npc_riko' || def.id === 'npc_penjaga_game') frame = 4;
        else frame = 0;
      }
    } else if ((def.id === 'npc_budi' || def.id === 'npc_teman') && scene.textures.exists('npc_budi_v6')) {
      textureKey = 'npc_budi_v6';
    } else if (scene.textures.exists(def.id)) {
      textureKey = def.id;
      frame = 0;
    } else if (def.id === 'npc_ibu' && scene.textures.exists('npc_ibu')) {
      textureKey = 'npc_ibu';
    } else if (def.id === 'npc_ayah' && scene.textures.exists('npc_ayah')) {
      textureKey = 'npc_ayah';
    } else if ((def.id === 'npc_budi' || def.id === 'npc_teman') && scene.textures.exists('npc_budi')) {
      textureKey = 'npc_budi';
    } else if (def.id === 'npc_siti' && scene.textures.exists('npc_siti')) {
      textureKey = 'npc_siti';
    } else if ((def.id === 'npc_kantin' || def.id === 'npc_penjual') && scene.textures.exists('npc_penjual_kantin')) {
      textureKey = 'npc_penjual_kantin';
    } else if ((def.id === 'npc_kasir_minimarket' || def.id === 'npc_kasir') && scene.textures.exists('npc_kasir_minimarket')) {
      textureKey = 'npc_kasir_minimarket';
    } else if ((def.id === 'npc_cindy' || def.id === 'npc_penjaga_kosmetik') && scene.textures.exists('npc_penjaga_kosmetik')) {
      textureKey = 'npc_penjaga_kosmetik';
    } else if ((def.id === 'npc_doni' || def.id === 'npc_petugas_spbu' || def.id === 'npc_pak_anto') && scene.textures.exists('npc_petugas_spbu')) {
      textureKey = 'npc_petugas_spbu';
    } else if ((def.id === 'npc_riko' || def.id === 'npc_penjaga_game') && scene.textures.exists('npc_penjaga_game')) {
      textureKey = 'npc_penjaga_game';
    } else if (def.assetId && scene.textures.exists(def.assetId)) {
      textureKey = def.assetId;
      if (def.assetId === 'npc_sheet_family') {
        frame = def.id === 'npc_ayah' ? 1 : 0;
      } else if (def.assetId === 'npc_sheet_friends') {
        frame = def.id === 'npc_siti' ? 1 : 0;
      } else if (def.assetId === 'npc_sheet_vendors') {
        if (def.id === 'npc_kasir_minimarket' || def.id === 'npc_kasir') frame = 1;
        else if (def.id === 'npc_cindy' || def.id === 'npc_penjaga_kosmetik') frame = 2;
        else if (def.id === 'npc_doni' || def.id === 'npc_petugas_spbu' || def.id === 'npc_pak_anto') frame = 3;
        else if (def.id === 'npc_riko' || def.id === 'npc_penjaga_game') frame = 4;
        else frame = 0;
      }
    }

    if (textureKey) {
      body = scene.add.sprite(x, y + 4, textureKey, frame);
      body.setOrigin(0.5, 0.95);
      body.setDepth(y + 14);
    } else {
      body = scene.add.container(x, y);
      body.setDepth(y + 14);
      const torso = scene.add.rectangle(0, 0, 18, 26, def.color ?? 0xC9A27A);
      const head = scene.add.circle(0, -18, 8, def.color ?? 0xC9A27A);
      const outline = scene.add.rectangle(0, 0, 20, 28);
      outline.setStrokeStyle(1, 0x121A2E);
      body.add([torso, head, outline]);
    }

    // Name label — Diletakkan di atas kepala karakter (Rule 73 §6: validasi bentrok nama pemain vs NPC)
    const store = scene.game.registry.get('store');
    const playerName = store?.getState()?.character?.name;
    let displayName = def.name || def.id || 'NPC';
    if (playerName && displayName.trim().toLowerCase() === playerName.trim().toLowerCase()) {
      displayName = def.altName || `${displayName} (NPC)`;
    }

    const label = scene.add.text(x, y - 64, displayName, {
      font: 'bold 10px sans-serif',
      fill: '#FBF6EA',
      backgroundColor: '#121A2E',
      padding: { x: 5, y: 2 },
    });
    label.setOrigin(0.5, 1);
    label.setDepth(600);

    // Floating interaction prompt bubble — Melayang di atas label nama (y - 88)
    const promptBubble = scene.add.container(x, y - 88);
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
      y: y - 92,
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
        }

        // Buka dialog HANYA jika pemain menekan tombol interaksi [E] atau [Space]
        const keyEDown = this.scene.keyE && Phaser.Input.Keyboard.JustDown(this.scene.keyE);
        const keySpaceDown = this.scene.keySpace && Phaser.Input.Keyboard.JustDown(this.scene.keySpace);

        if ((keyEDown || keySpaceDown) && !isNPCDialogOpen()) {
          this.openDialog(npc, uiContainer);
        }
      } else {
        if (npc.inRange) {
          npc.inRange = false;
          npc.promptBubble.setVisible(false);

          // Jika pemain menjauh (keluar dari jangkauan), tutup dialog otomatis bila aktif untuk NPC ini
          if (this.activeNpc === npc) {
            closeNPCDialog();
            this.activeNpc = null;
          }
        }
      }
    }
  }

  _resolveDialogId(npcDef) {
    if (npcDef.dialogId) return npcDef.dialogId;
    const id = npcDef.id;
    if (id === 'npc_ibu') return 'dia_ibu_home';
    if (id === 'npc_ayah') return 'dia_ayah_home';
    if (id === 'npc_budi' || id === 'npc_teman') return 'dia_budi_school';
    if (id === 'npc_sri' || id === 'npc_kantin' || id === 'npc_penjual') return 'dia_sri_kantin';
    if (id === 'npc_kasir_mini' || id === 'npc_kasir_minimarket' || id === 'npc_kasir') return 'dia_maya_minimarket';
    if (id === 'npc_mbak_maya' || id === 'npc_cindy' || id === 'npc_penjaga_kosmetik') return 'dia_cindy_kosmetik';
    if (id === 'npc_bang_dodi' || id === 'npc_doni' || id === 'npc_petugas_spbu') return 'dia_doni_spbu';
    if (id === 'npc_pak_anto') return 'dia_pak_anto_hub';
    if (id === 'npc_operator_game' || id === 'npc_riko' || id === 'npc_penjaga_game') return 'dia_riko_game';
    return null;
  }

  openDialog(npc, container) {
    this.activeNpc = npc;

    // Use Rule 71 Dialogue Box with Character Portraits for all NPCs
    const dialogId = this._resolveDialogId(npc.def);
    if (dialogId) {
      startDialogue(dialogId, npc.def.id, () => {
        this.activeNpc = null;
      });
      return;
    }

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
