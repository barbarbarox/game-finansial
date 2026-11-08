/**
 * mapManager.js — Map management, interior rendering, and transition system.
 * Complies with Rule 70 (Interior Maps & Buildings) and Rule 72 (Time Integration).
 */

import { isLocationOpen, DEFAULT_OPENING_HOURS } from '../domain/clock.js';
import { createProceduralTiles } from '../assets-gen/groundTiles.js';

export class MapManager {
  /**
   * @param {Phaser.Scene} scene
   * @param {object} indexData - data/maps/index.json
   */
  constructor(scene, indexData) {
    this.scene = scene;
    this.indexData = indexData;
    this.currentMapId = null;
    this.currentLayout = null;
    this.furnitureObjects = [];
    this.colliders = [];
    this.isTransitioning = false;
  }

  /**
   * Initialize and load a map layout.
   * @param {string} mapId
   * @param {string|number[]} [spawnTarget='default']
   */
  async loadMap(mapId, spawnTarget = 'default') {
    this.currentMapId = mapId;
    const mapMeta = this.indexData.maps.find(m => m.id === mapId) || this.indexData.maps[0];

    // Fetch layout if not in Phaser cache
    let layout = this.scene.cache.json.get(`layout_${mapId}`);
    if (!layout) {
      try {
        const res = await fetch(mapMeta.file);
        layout = await res.json();
        this.scene.cache.json.add(`layout_${mapId}`, layout);
      } catch (err) {
        console.error(`[MapManager] Gagal memuat file peta: ${mapMeta.file}`, err);
        return;
      }
    }

    this.currentLayout = layout;
    this.renderCurrentMap();

    // Determine spawn position
    let spawnX = 5;
    let spawnY = 5;

    if (Array.isArray(spawnTarget) && spawnTarget.length >= 2) {
      spawnX = spawnTarget[0];
      spawnY = spawnTarget[1];
    } else if (typeof spawnTarget === 'string' && layout.world?.spawns?.[spawnTarget]) {
      const sp = layout.world.spawns[spawnTarget];
      spawnX = sp.x;
      spawnY = sp.y;
    } else if (layout.world?.spawns?.default) {
      spawnX = layout.world.spawns.default.x;
      spawnY = layout.world.spawns.default.y;
    } else if (layout.world?.spawn) {
      spawnX = layout.world.spawn.x;
      spawnY = layout.world.spawn.y;
    }

    // Position player
    const store = this.scene.game.registry.get('store');
    const savedPos = store?.getState()?.playerPos;

    if (spawnTarget === 'saved' && savedPos && savedPos.x && savedPos.y && this.scene._player) {
      this.scene._player.sprite.x = savedPos.x;
      this.scene._player.sprite.y = savedPos.y;
    } else {
      const tileSize = layout.world?.tileSize || 32;
      if (this.scene._player) {
        this.scene._player.sprite.x = (spawnX + 0.5) * tileSize;
        this.scene._player.sprite.y = (spawnY + 0.5) * tileSize;
      }
    }

    // Set camera bounds
    const mapW = (layout.world?.widthTiles || 40) * tileSize;
    const mapH = (layout.world?.heightTiles || 24) * tileSize;
    this.scene.cameras.main.setBounds(0, 0, mapW, mapH);
    if (this.scene._player) {
      this.scene.cameras.main.startFollow(this.scene._player.sprite, true, 0.1, 0.1);
    }

    // Update store state with currentMap
    if (store) {
      store.setState({ currentMap: mapId });
    }
  }

  /**
   * Transition to another map with 200ms fade.
   * @param {string} targetMapId
   * @param {string|number[]} [spawnTarget='default']
   * @param {string} [openingHoursId]
   */
  transitionTo(targetMapId, targetSpawn = 'default', openingHoursId = null) {
    if (this.isTransitioning) return;

    // Check opening hours if target is an interior with schedule
    const store = this.scene.game.registry.get('store');
    const clock = store?.getState()?.clock || {};
    const checkId = openingHoursId || (targetMapId === 'home' ? 'home' : targetMapId);

    if (targetMapId !== 'town_hub' && DEFAULT_OPENING_HOURS[checkId]) {
      const status = isLocationOpen(checkId, clock);
      if (!status.open) {
        // Show door closed feedback
        if (this.scene._promptText) {
          this.scene._promptText.setText(`[TUTUP] ${status.reason}`);
          this.scene._promptText.setVisible(true);
          setTimeout(() => {
            if (this.scene._promptText) this.scene._promptText.setVisible(false);
          }, 2500);
        }
        return;
      }
    }

    this.isTransitioning = true;

    // Use setTimeout instead of scene.time.delayedCall to ensure it fires even
    // when Phaser's game loop is throttled (e.g., headless testing).
    try {
      this.scene.cameras.main.fadeOut(200, 10, 15, 26);
    } catch (_) { /* camera may not be ready */ }

    // Failsafe: always clear isTransitioning after 3 seconds max
    const failsafeTimer = setTimeout(() => {
      this.isTransitioning = false;
    }, 3000);

    setTimeout(async () => {
      // Clear previous map objects
      this.clearCurrentMap();

      try {
        await this.loadMap(targetMapId, targetSpawn);
      } catch (err) {
        console.error('[MapManager] Error loading map during transition:', err);
      }

      try {
        this.scene.cameras.main.fadeIn(200, 10, 15, 26);
      } catch (_) { /* ignore */ }

      setTimeout(() => {
        clearTimeout(failsafeTimer);
        this.isTransitioning = false;
      }, 250);
    }, 200);
  }

  /**
   * Clear old map objects, furniture, and colliders.
   */
  clearCurrentMap() {
    for (const c of this.colliders) {
      if (c && c.destroy) c.destroy();
    }
    this.colliders = [];

    for (const f of this.furnitureObjects) {
      if (f && f.destroy) f.destroy();
    }
    this.furnitureObjects = [];

    if (this._groundLayer && this._groundLayer.destroy) {
      this._groundLayer.destroy();
    }
  }

  /**
   * Render current map (floors, walls, furniture, colliders).
   */
  renderCurrentMap() {
    const layout = this.currentLayout;
    if (!layout) return;

    const tileSize = layout.world?.tileSize || 32;
    const mapW = (layout.world?.widthTiles || 40) * tileSize;
    const mapH = (layout.world?.heightTiles || 24) * tileSize;

    // 1. Render Ground / Floor
    const gfx = this.scene.add.graphics();
    gfx.setDepth(-10);

    if (layout.type === 'interior') {
      // Background void for interior
      gfx.fillStyle(0x0a0f1a, 1.0);
      gfx.fillRect(0, 0, mapW, mapH);

      // Render floors
      const floorColors = {
        lantai_kayu_kamar: { base: 0x8D6346, line: 0x6E4C33 },
        keramik_kamar_mandi: { base: 0x4A88B8, line: 0x34658B },
        keramik_ruang_tamu: { base: 0xC8B898, line: 0xA89878 },
        keramik_dapur: { base: 0x98A8A0, line: 0x788880 },
        lantai_koridor: { base: 0xB0A088, line: 0x887860 },
        lantai_kelas: { base: 0x7C5C43, line: 0x5C3E28 },
        lantai_kantin: { base: 0xA89878, line: 0x887858 },
        keramik_minimarket: { base: 0xE0E0D8, line: 0xB8B8B0 },
        keramik_kosmetik_pastel: { base: 0xD8B8C8, line: 0xB898A8 },
        lantai_kios_spbu: { base: 0x888890, line: 0x686870 },
        lantai_arcade_neon: { base: 0x221833, line: 0x3D2855 }
      };

      for (const fl of (layout.floors || [])) {
        const theme = floorColors[fl.type] || { base: 0x8D6346, line: 0x6E4C33 };
        gfx.fillStyle(theme.base, 1.0);
        gfx.fillRect(fl.x * tileSize, fl.y * tileSize, fl.w * tileSize, fl.h * tileSize);

        // Grid lines for tile effect
        gfx.lineStyle(1, theme.line, 0.4);
        for (let x = fl.x; x <= fl.x + fl.w; x++) {
          gfx.lineBetween(x * tileSize, fl.y * tileSize, x * tileSize, (fl.y + fl.h) * tileSize);
        }
        for (let y = fl.y; y <= fl.y + fl.h; y++) {
          gfx.lineBetween(fl.x * tileSize, y * tileSize, (fl.x + fl.w) * tileSize, y * tileSize);
        }
      }

      // Render walls
      for (const w of (layout.walls || [])) {
        // Wall base
        gfx.fillStyle(0x34456B, 1.0);
        gfx.fillRect(w.x * tileSize, w.y * tileSize, w.w * tileSize, w.h * tileSize);

        // Upper cornice
        gfx.fillStyle(0x1F2A44, 1.0);
        gfx.fillRect(w.x * tileSize, w.y * tileSize, w.w * tileSize, 6);

        // Baseboard
        gfx.fillStyle(0x121A2E, 1.0);
        gfx.fillRect(w.x * tileSize, (w.y + w.h) * tileSize - 4, w.w * tileSize, 4);
      }
    } else {
      // Exterior town hub ground rendering
      for (const g of (layout.ground || [])) {
        const color = g.type === 'rumput' ? 0x4A6B3E : (g.type === 'jalan' ? 0x2C3A54 : 0x7E7259);
        gfx.fillStyle(color, 1.0);
        gfx.fillRect(g.x * tileSize, g.y * tileSize, g.w * tileSize, g.h * tileSize);
      }
    }

    this._groundLayer = gfx;

    // 2. Render Furniture (pixel art sprites if available, or labeled placeholders)
    const furniture = layout.furniture || [];
    for (const f of furniture) {
      const container = this.scene.add.container(f.x * tileSize, f.y * tileSize);
      container.setDepth(f.y + f.h);

      const textureKey = f.assetId || `furn_${f.type}`;
      if (this.scene.textures.exists(textureKey)) {
        const sprite = this.scene.add.sprite(
          (f.w * tileSize) / 2,
          f.h * tileSize,
          textureKey
        );
        sprite.setOrigin(0.5, 1.0);
        container.add(sprite);
      } else {
        const fGfx = this.scene.add.graphics();
        // 3/4 box perspective
        fGfx.fillStyle(0x1F2A44, 0.95);
        fGfx.fillRect(0, 0, f.w * tileSize, f.h * tileSize);
        fGfx.lineStyle(2, 0xD9A441, 1.0);
        fGfx.strokeRect(0, 0, f.w * tileSize, f.h * tileSize);

        // Label
        const label = this.scene.add.text(
          (f.w * tileSize) / 2,
          (f.h * tileSize) / 2,
          f.label || f.type,
          {
            fontSize: '9px',
            fontFamily: 'monospace',
            color: '#F7EEDA',
            align: 'center',
            wordWrap: { width: f.w * tileSize - 4 }
          }
        ).setOrigin(0.5);

        container.add(fGfx);
        container.add(label);
      }
      this.furnitureObjects.push(container);

      // Collider for furniture
      if (f.collidable && this.scene._player) {
        const body = this.scene.add.rectangle(
          f.x * tileSize + (f.w * tileSize) / 2,
          f.y * tileSize + (f.h * tileSize) / 2,
          f.w * tileSize,
          f.h * tileSize
        );
        this.scene.physics.add.existing(body, true);
        this.scene.physics.add.collider(this.scene._player.sprite, body);
        this.colliders.push(body);
      }
    }

    // 3. Static Map Colliders
    for (const c of (layout.colliders || [])) {
      if (this.scene._player) {
        const body = this.scene.add.rectangle(
          c.x * tileSize + (c.w * tileSize) / 2,
          c.y * tileSize + (c.h * tileSize) / 2,
          c.w * tileSize,
          c.h * tileSize
        );
        this.scene.physics.add.existing(body, true);
        this.scene.physics.add.collider(this.scene._player.sprite, body);
        this.colliders.push(body);
      }
    }

    // 4. Update interactables and NPCs in World scene
    if (layout.interactables) {
      this.scene._interactables = layout.interactables;
      if (this.scene._interactablesManager?.setInteractables) {
        this.scene._interactablesManager.setInteractables(layout.interactables);
      }
    }
    if (this.scene._npcManager && layout.npcs) {
      this.scene._npcManager.setNPCs(layout.npcs);
    }
  }
}
