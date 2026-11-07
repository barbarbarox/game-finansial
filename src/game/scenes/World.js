/**
 * World.js — Main gameplay world scene for Life Journey.
 * Renders procedural ground, buildings, player, NPCs, and interactable doors.
 */

import { PlayerController } from '../player.js';
import { NPCManager } from '../npc.js';
import { InteractableManager } from '../interactables.js';
import { createHUD } from '../../ui/hud.js';
import { createCashbookModal } from '../../ui/cashbook.js';
import { createBudgetModal } from '../../ui/budgetPanel.js';
import { createShopModal } from '../../ui/shopPanel.js';
import { createDecisionModal } from '../../ui/decisionDialog.js';
import { createProceduralTiles } from '../../assets-gen/groundTiles.js';
import { saveGame } from '../../state/persistence.js';

export class World extends Phaser.Scene {
  constructor() {
    super({ key: 'World' });
    this._player = null;
    this._npcManager = null;
    this._interactables = null;
    this._hudElement = null;
    this._colliders = [];
    this._tileSize = 32;
    this._promptText = null;
    this._currentInteractable = null;
  }

  create() {
    const layout = this.cache.json.get('townLayout');
    const config = this.cache.json.get('phase1config') || {};
    const store = this.game.registry.get('store');

    this._tileSize = layout?.world?.tileSize || config?.tileSize || 32;
    const mapW = (layout?.world?.widthTiles || 40) * this._tileSize;
    const mapH = (layout?.world?.heightTiles || 24) * this._tileSize;

    // Generate procedural tile textures
    createProceduralTiles(this, this._tileSize);

    // Camera
    this.cameras.main.setBounds(0, 0, mapW, mapH);

    // 1. Draw ground layer
    this._drawGround(layout);

    // 2. Draw buildings
    this._drawBuildings(layout);

    // 3. Build colliders
    this._buildColliders(layout);

    // 4. Spawn Player
    const spawnX = (layout?.world?.spawn?.x || 6) * this._tileSize;
    const spawnY = (layout?.world?.spawn?.y || 18) * this._tileSize;
    this._player = new PlayerController(this, spawnX, spawnY, config);

    this.cameras.main.startFollow(this._player.sprite, true, 0.1, 0.1);

    // 5. Spawn NPCs
    this._npcManager = new NPCManager(this, layout?.npcs || []);

    // 6. Interactables (Doors, etc.)
    this._interactables = layout?.interactables || [];

    // Interaction prompt text
    this._promptText = this.add.text(0, 0, '', {
      font: 'bold 13px sans-serif',
      fill: '#D9A441',
      stroke: '#121A2E',
      strokeThickness: 3,
      backgroundColor: '#1F2A44',
      padding: { x: 8, y: 4 }
    }).setOrigin(0.5, 1.0).setDepth(2000).setVisible(false);

    // E key for interaction
    this.keyE = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.E);
    this.keySpace = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.SPACE);

    // 7. Mount DOM HUD
    const uiContainer = document.getElementById('ui-container') || document.body;
    if (store) {
      this._hudElement = createHUD(
        uiContainer,
        store,
        () => createCashbookModal(uiContainer, store),
        () => createBudgetModal(uiContainer, store, config)
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
      this._player.update(delta, this._colliders);
      this._checkInteractables();
    }
  }

  _drawGround(layout) {
    const ts = this._tileSize;
    const mapW = layout?.world?.widthTiles || 40;
    const mapH = layout?.world?.heightTiles || 24;

    // Base grass fill
    for (let tx = 0; tx < mapW; tx++) {
      for (let ty = 0; ty < mapH; ty++) {
        this.add.image(tx * ts, ty * ts, 'tile_rumput').setOrigin(0, 0).setDepth(0);
      }
    }

    // Specific zones from layout
    if (layout?.ground) {
      for (const zone of layout.ground) {
        const tex = `tile_${zone.type}`;
        if (this.textures.exists(tex)) {
          for (let x = zone.x; x < zone.x + zone.w; x++) {
            for (let y = zone.y; y < zone.y + zone.h; y++) {
              this.add.image(x * ts, y * ts, tex).setOrigin(0, 0).setDepth(1);
            }
          }
        }
      }
    }
  }

  _drawBuildings(layout) {
    const ts = this._tileSize;
    const objects = layout?.objects || [];

    for (const obj of objects) {
      const x = obj.x * ts;
      const y = obj.y * ts;
      const w = (obj.footprint?.w || 4) * ts;
      const h = (obj.footprint?.h || 3) * ts;

      if (this.textures.exists(obj.assetId)) {
        // Image asset exists: place with anchor at bottom center
        const img = this.add.image(x, y, obj.assetId);
        img.setOrigin(0.5, 1.0);
        img.setDepth(y);
      } else {
        // Labeled placeholder box
        const gfx = this.add.graphics();
        gfx.fillStyle(0x34456B, 1);
        gfx.fillRect(x - w / 2, y - h, w, h);
        gfx.lineStyle(2, 0xD9A441, 1);
        gfx.strokeRect(x - w / 2, y - h, w, h);
        gfx.setDepth(y);

        const lbl = this.add.text(x, y - h / 2, obj.id, {
          font: 'bold 11px sans-serif',
          fill: '#F7EEDA'
        }).setOrigin(0.5).setDepth(y + 1);
      }
    }
  }

  _buildColliders(layout) {
    const ts = this._tileSize;
    this._colliders = [];

    // Outer boundary walls
    const mapW = (layout?.world?.widthTiles || 40) * ts;
    const mapH = (layout?.world?.heightTiles || 24) * ts;
    this._colliders.push({ x: -ts, y: 0, w: ts, h: mapH });
    this._colliders.push({ x: mapW, y: 0, w: ts, h: mapH });
    this._colliders.push({ x: 0, y: -ts, w: mapW, h: ts });
    this._colliders.push({ x: 0, y: mapH, w: mapW, h: ts });

    // Object footprints as colliders
    if (layout?.objects) {
      for (const obj of layout.objects) {
        const x = obj.x * ts;
        const y = obj.y * ts;
        const fw = (obj.footprint?.w || 4) * ts;
        const fh = (obj.footprint?.h || 2) * ts;
        this._colliders.push({
          x: x - fw / 2,
          y: y - fh,
          w: fw,
          h: fh
        });
      }
    }
  }

  _checkInteractables() {
    const px = this._player.x;
    const py = this._player.y;
    const ts = this._tileSize;

    let nearby = null;
    for (const int of this._interactables) {
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
      this._promptText.setPosition(this._player.x, this._player.y - 70);
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

    if (int.locationId) {
      createShopModal(uiContainer, store, int.locationId, config, null);
    }
  }

  _setupDebug(config) {
    const params = new URLSearchParams(window.location.search);
    if (params.get('debug') === '1' || config?.debugEnabled === true) {
      window.__LJ__ = {
        scene: this,
        getStore: () => this.game.registry.get('store'),
        getLedger: () => this.game.registry.get('store')?.getState()?.ledger,
        getPlayer: () => this._player,
        teleportTo: (tx, ty) => {
          if (this._player) {
            this._player.sprite.x = tx * this._tileSize;
            this._player.sprite.y = ty * this._tileSize;
          }
        }
      };
      console.info('[Debug] window.__LJ__ aktif');
    }
  }
}
