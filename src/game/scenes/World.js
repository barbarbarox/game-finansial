/**
 * World.js — World/Map scene for Life Journey.
 * Top-down 40×24 tile map with player movement, collision, NPCs, and interactables.
 */

import { PlayerController } from '../player.js';
import { NPCManager } from '../npc.js';
import { InteractableManager } from '../interactables.js';
import { HUD } from '../../ui/hud.js';

export class World extends Phaser.Scene {
  constructor() {
    super({ key: 'World' });
    this._player = null;
    this._npcManager = null;
    this._interactables = null;
    this._hud = null;
    this._colliders = [];
    this._tileSize = 32;
  }

  create() {
    const layout = this.cache.json.get('townLayout');
    const config = this.cache.json.get('phase1config');
    const store = this.game.registry.get('store');

    this._tileSize = layout?.world?.tileSize ?? config?.tileSize ?? 32;
    const mapW = (layout?.world?.widthTiles ?? 40) * this._tileSize;
    const mapH = (layout?.world?.heightTiles ?? 24) * this._tileSize;

    // Camera bounds
    this.cameras.main.setBounds(0, 0, mapW, mapH);

    // Draw ground layer
    this._drawGround(layout);

    // Draw buildings
    this._drawBuildings(layout);

    // Colliders
    this._buildColliders(layout);

    // Player
    const spawnX = (layout?.world?.spawnX ?? 20) * this._tileSize;
    const spawnY = (layout?.world?.spawnY ?? 12) * this._tileSize;
    this._player = new PlayerController(this, spawnX, spawnY, config);

    // Camera follows player
    this.cameras.main.startFollow(this._player.sprite, true, 0.1, 0.1);

    // NPCs
    this._npcManager = new NPCManager(this, layout?.npcs ?? []);

    // Interactables
    this._interactables = new InteractableManager(this, layout?.interactables ?? [], store);

    // HUD
    this._hud = new HUD(store, config);
    this._hud.show();

    // Debug hook (only if ?debug=1 and config.debugEnabled)
    this._setupDebug(config);

    // Dispatch world-ready event
    document.dispatchEvent(new CustomEvent('lj:worldReady'));
  }

  update(time, delta) {
    if (this._player) {
      this._player.update(delta, this._colliders);
    }
    if (this._npcManager) {
      this._npcManager.update(time, this._player);
    }
    if (this._interactables) {
      this._interactables.update(this._player);
    }
  }

  _drawGround(layout) {
    const gfx = this.add.graphics();
    const ts = this._tileSize;

    // Default ground: grass
    const mapW = (layout?.world?.widthTiles ?? 40);
    const mapH = (layout?.world?.heightTiles ?? 24);

    for (let tx = 0; tx < mapW; tx++) {
      for (let ty = 0; ty < mapH; ty++) {
        const isRoad = (tx >= 18 && tx <= 22) || (ty >= 11 && ty <= 13);
        const isSidewalk = (tx === 17 || tx === 23) || (ty === 10 || ty === 14);
        let color = 0x4A6B40; // grass
        if (isRoad) color = 0x505860; // road (grey)
        if (isSidewalk) color = 0xB8A88A; // sidewalk (beige)

        gfx.fillStyle(color, 1);
        gfx.fillRect(tx * ts, ty * ts, ts - 1, ts - 1);
      }
    }

    // Ground layer tile data from layout
    if (layout?.ground) {
      for (const tile of layout.ground) {
        gfx.fillStyle(tile.color ?? 0x4A6B40, 1);
        gfx.fillRect(tile.x * ts, tile.y * ts, ts - 1, ts - 1);
      }
    }
  }

  _drawBuildings(layout) {
    const ts = this._tileSize;
    const objects = layout?.objects ?? [];

    for (const obj of objects) {
      const x = obj.x * ts;
      const y = obj.y * ts;
      const w = (obj.w ?? 4) * ts;
      const h = (obj.h ?? 3) * ts;

      // Draw building placeholder
      const gfx = this.add.graphics();
      gfx.fillStyle(0xC9A27A, 1);
      gfx.fillRect(x, y, w, h);
      gfx.lineStyle(2, 0x5E3F2A, 1);
      gfx.strokeRect(x, y, w, h);

      // Roof
      gfx.fillStyle(0xC0654A, 1);
      gfx.fillRect(x, y, w, h * 0.3);

      // Door
      const doorW = ts;
      const doorH = ts * 0.75;
      const doorX = x + w / 2 - doorW / 2;
      const doorY = y + h - doorH;
      gfx.fillStyle(0x5E3F2A, 1);
      gfx.fillRect(doorX, doorY, doorW, doorH);

      // Label
      const label = this.add.text(x + w / 2, y + h / 2, obj.name ?? obj.id ?? '', {
        font: '10px sans-serif',
        fill: '#1F2A44',
      });
      label.setOrigin(0.5);
      label.setDepth(10);

      // Add building to scene at correct depth
      gfx.setDepth(y + h); // depth sorting by bottom edge
    }
  }

  _buildColliders(layout) {
    const ts = this._tileSize;
    this._colliders = [];

    // Colliders from layout
    if (layout?.colliders) {
      for (const c of layout.colliders) {
        this._colliders.push({
          x: c.x * ts,
          y: c.y * ts,
          w: c.w * ts,
          h: c.h * ts,
        });
      }
    }

    // Buildings act as colliders
    if (layout?.objects) {
      for (const obj of layout.objects) {
        const x = obj.x * ts;
        const y = obj.y * ts;
        const w = (obj.w ?? 4) * ts;
        const h = (obj.h ?? 3) * ts;
        // Footprint is bottom 40% (walkable below door)
        this._colliders.push({ x, y, w, h: h * 0.6 });
      }
    }

    // Map bounds
    const mapW = (layout?.world?.widthTiles ?? 40) * ts;
    const mapH = (layout?.world?.heightTiles ?? 24) * ts;
    this._colliders.push({ x: -ts, y: 0, w: ts, h: mapH });       // left wall
    this._colliders.push({ x: mapW, y: 0, w: ts, h: mapH });      // right wall
    this._colliders.push({ x: 0, y: -ts, w: mapW, h: ts });       // top wall
    this._colliders.push({ x: 0, y: mapH, w: mapW, h: ts });      // bottom wall
  }

  _setupDebug(config) {
    const params = new URLSearchParams(window.location.search);
    if (params.get('debug') === '1' && config?.debugEnabled === true) {
      window.__LJ__ = {
        scene: this,
        getStore: () => this.game.registry.get('store'),
        getLedger: () => this.game.registry.get('store')?.getState()?.ledger,
        getPlayer: () => this._player,
      };
      console.info('[Debug] window.__LJ__ aktif');
    }
  }
}
