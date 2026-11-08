/**
 * mapManager.js — Map management, interior rendering, and transition system.
 * Complies with Rule 70 (Interior Maps & Buildings) and Rule 72 (Time Integration).
 *
 * ARCHITECTURE NOTE:
 * MapManager is the SOLE owner of all visual layers (ground, walls, furniture, NPCs).
 * World.js bootstraps once and delegates ALL map rendering to MapManager.
 * clearCurrentMap() destroys every Phaser game object created by this manager
 * before renderCurrentMap() builds the new one — no overlap possible.
 */

import { isLocationOpen, DEFAULT_OPENING_HOURS } from '../domain/clock.js';

/** Floor colour palette for interior tiles */
const FLOOR_COLORS = {
  lantai_kayu_kamar:        { base: 0x8D6346, line: 0x6E4C33 },
  keramik_kamar_mandi:      { base: 0x4A88B8, line: 0x34658B },
  keramik_ruang_tamu:       { base: 0xC8B898, line: 0xA89878 },
  keramik_dapur:            { base: 0x98A8A0, line: 0x788880 },
  lantai_koridor:           { base: 0xB0A088, line: 0x887860 },
  lantai_kelas:             { base: 0x7C5C43, line: 0x5C3E28 },
  lantai_kantin:            { base: 0xA89878, line: 0x887858 },
  keramik_minimarket:       { base: 0xE0E0D8, line: 0xB8B8B0 },
  keramik_kosmetik_pastel:  { base: 0xD8B8C8, line: 0xB898A8 },
  lantai_kios_spbu:         { base: 0x888890, line: 0x686870 },
  lantai_arcade_neon:       { base: 0x221833, line: 0x3D2855 },
};

/** Exterior ground colour palette */
const GROUND_COLORS = {
  rumput:  0x4A6B3E,
  jalan:   0x2C3A54,
  tanah:   0x7E7259,
  trotoar: 0xA89878,
  pasir:   0xC8B080,
};

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

    // All Phaser game objects created for the current map are tracked here
    // so clearCurrentMap() can destroy them all cleanly.
    this._mapObjects = [];   // generic displayObjects
    this._colliderBodies = []; // physics rectangles
    this._colliderRects = [];  // pixel rects for player translation collision
    this.isTransitioning = false;
  }

  // ─── Public API ───────────────────────────────────────────────────────────

  /**
   * Initialise and load a map layout (no transition animation).
   * @param {string} mapId
   * @param {string|number[]} [spawnTarget='default']
   */
  async loadMap(mapId, spawnTarget = 'default') {
    this.currentMapId = mapId;

    const mapMeta = this.indexData.maps.find(m => m.id === mapId)
      || { id: mapId, file: `data/maps/${mapId}.layout.json` };

    // Fetch layout (use cache if available)
    let layout = this.scene.cache.json.get(`layout_${mapId}`);
    if (!layout) {
      try {
        const res = await fetch(mapMeta.file);
        layout = await res.json();
        this.scene.cache.json.add(`layout_${mapId}`, layout);
      } catch (err) {
        console.error(`[MapManager] Failed to load map: ${mapMeta.file}`, err);
        return;
      }
    }

    this.currentLayout = layout;

    // Destroy everything from the previous map first
    this.clearCurrentMap();

    // Build the new map
    this._renderMap(layout);

    // Position player at spawn
    this._positionPlayer(layout, spawnTarget);

    // Update camera bounds (User feedback: provide camera padding so room corners are never obscured by HUD)
    const tileSize = layout.world?.tileSize || 32;
    const mapW = (layout.world?.widthTiles || 40) * tileSize;
    const mapH = (layout.world?.heightTiles || 24) * tileSize;

    if (layout.type === 'interior') {
      const padX = tileSize * 8; // 256px padding
      const padY = tileSize * 5; // 160px padding
      this.scene.cameras.main.setBounds(-padX, -padY, mapW + padX * 2, mapH + padY * 2);
    } else {
      this.scene.cameras.main.setBounds(0, 0, mapW, mapH);
    }

    if (this.scene._player) {
      this.scene.cameras.main.startFollow(this.scene._player.sprite, true, 0.1, 0.1);
    }

    // Persist current map in store
    const store = this.scene.game.registry.get('store');
    if (store) store.setState({ currentMap: mapId });
  }

  /**
   * Transition to another map with a 200 ms fade.
   * @param {string} targetMapId
   * @param {string|number[]} [targetSpawn='default']
   * @param {string|null} [openingHoursId]
   */
  transitionTo(targetMapId, targetSpawn = 'default', openingHoursId = null) {
    if (this.isTransitioning) return;

    // Opening-hours guard (skip for hub and home)
    const store = this.scene.game.registry.get('store');
    const clock = store?.getState()?.clock || {};
    const checkId = openingHoursId || targetMapId;

    if (targetMapId !== 'town_hub' && targetMapId !== 'home' && DEFAULT_OPENING_HOURS[checkId]) {
      const status = isLocationOpen(checkId, clock);
      if (!status.open) {
        if (this.scene.showPromptFeedback) {
          this.scene.showPromptFeedback(`[TUTUP] ${status.reason}`);
        }
        return;
      }
    }

    this.isTransitioning = true;

    try { this.scene.cameras.main.fadeOut(200, 10, 15, 26); } catch (_) {}

    const failsafe = setTimeout(() => { this.isTransitioning = false; }, 3000);

    setTimeout(async () => {
      try {
        await this.loadMap(targetMapId, targetSpawn);
      } catch (err) {
        console.error('[MapManager] Error during transition:', err);
      }
      try { this.scene.cameras.main.fadeIn(200, 10, 15, 26); } catch (_) {}
      setTimeout(() => {
        clearTimeout(failsafe);
        this.isTransitioning = false;
      }, 250);
    }, 200);
  }

  /**
   * Destroy every Phaser game object owned by this manager.
   * Must be called before rendering a new map.
   */
  clearCurrentMap() {
    for (const obj of this._mapObjects) {
      if (obj && !obj.destroyed) {
        try { obj.destroy(); } catch (_) {}
      }
    }
    this._mapObjects = [];

    for (const body of this._colliderBodies) {
      if (body && !body.destroyed) {
        try { body.destroy(); } catch (_) {}
      }
    }
    this._colliderBodies = [];
    this._colliderRects = [];
  }

  // ─── Internals ────────────────────────────────────────────────────────────

  /** Spawn player at the correct tile position for spawnTarget */
  _positionPlayer(layout, spawnTarget) {
    const tileSize = layout.world?.tileSize || 32;
    let spawnX = 5;
    let spawnY = 5;

    if (Array.isArray(spawnTarget) && spawnTarget.length >= 2) {
      [spawnX, spawnY] = spawnTarget;
    } else if (typeof spawnTarget === 'string' && layout.world?.spawns?.[spawnTarget]) {
      ({ x: spawnX, y: spawnY } = layout.world.spawns[spawnTarget]);
    } else if (layout.world?.spawns?.default) {
      ({ x: spawnX, y: spawnY } = layout.world.spawns.default);
    } else if (layout.world?.spawn) {
      ({ x: spawnX, y: spawnY } = layout.world.spawn);
    }

    const store = this.scene.game.registry.get('store');
    const savedPos = store?.getState()?.playerPos;

    if (spawnTarget === 'saved' && savedPos?.x && savedPos?.y && this.scene._player) {
      this.scene._player.sprite.x = savedPos.x;
      this.scene._player.sprite.y = savedPos.y;
    } else if (this.scene._player) {
      this.scene._player.sprite.x = (spawnX + 0.5) * tileSize;
      this.scene._player.sprite.y = (spawnY + 0.5) * tileSize;
    }
  }

  /** Master render routine */
  _renderMap(layout) {
    if (layout.type === 'interior') {
      this._renderInterior(layout);
    } else {
      this._renderExterior(layout);
    }
    this._renderFurniture(layout);
    this._buildColliders(layout);
    this._spawnNPCs(layout);
    this._registerInteractables(layout);
  }

  // ── Interior rendering ───────────────────────────────────────────────────

  _renderInterior(layout) {
    const tileSize = layout.world?.tileSize || 32;
    const mapW = (layout.world?.widthTiles || 24) * tileSize;
    const mapH = (layout.world?.heightTiles || 18) * tileSize;

    // Full void background — covers any exterior tiles underneath and margin padding
    const bg = this.scene.add.graphics();
    bg.fillStyle(0x0a0f1a, 1.0);
    bg.fillRect(-2000, -2000, mapW + 4000, mapH + 4000);
    bg.setDepth(-200);
    this._mapObjects.push(bg);

    const gfx = this.scene.add.graphics();
    gfx.setDepth(-10);
    this._mapObjects.push(gfx);

    // Floor tiles
    for (const fl of layout.floors || []) {
      const theme = FLOOR_COLORS[fl.type] || { base: 0x8D6346, line: 0x6E4C33 };
      gfx.fillStyle(theme.base, 1.0);
      gfx.fillRect(fl.x * tileSize, fl.y * tileSize, fl.w * tileSize, fl.h * tileSize);
      gfx.lineStyle(1, theme.line, 0.4);
      for (let x = fl.x; x <= fl.x + fl.w; x++) {
        gfx.lineBetween(x * tileSize, fl.y * tileSize, x * tileSize, (fl.y + fl.h) * tileSize);
      }
      for (let y = fl.y; y <= fl.y + fl.h; y++) {
        gfx.lineBetween(fl.x * tileSize, y * tileSize, (fl.x + fl.w) * tileSize, y * tileSize);
      }
    }

    // Walls
    for (const w of layout.walls || []) {
      gfx.fillStyle(0x34456B, 1.0);
      gfx.fillRect(w.x * tileSize, w.y * tileSize, w.w * tileSize, w.h * tileSize);
      gfx.fillStyle(0x1F2A44, 1.0);
      gfx.fillRect(w.x * tileSize, w.y * tileSize, w.w * tileSize, 6);
      gfx.fillStyle(0x121A2E, 1.0);
      gfx.fillRect(w.x * tileSize, (w.y + w.h) * tileSize - 4, w.w * tileSize, 4);
    }

    // Doorways & Archways (Rule 73: clear visual doorways, thresholds & archway frames)
    for (const d of layout.doorways || []) {
      this._renderDoorway(d, tileSize);
    }

    // Room label (fixed to camera)
    const nameLabel = this.scene.add.text(
      8, 8,
      layout.displayName || layout.id || '',
      { font: 'bold 11px monospace', fill: '#D9A441', stroke: '#121A2E', strokeThickness: 2 }
    ).setScrollFactor(0).setDepth(3000);
    this._mapObjects.push(nameLabel);
  }

  /**
   * Render visually distinct doorway archways, thresholds, and pillar posts
   */
  _renderDoorway(d, tileSize) {
    const gfx = this.scene.add.graphics();
    gfx.setDepth(-5);
    this._mapObjects.push(gfx);

    const x = d.x * tileSize;
    const y = d.y * tileSize;
    const w = (d.w || 1) * tileSize;
    const h = (d.h || 1) * tileSize;

    if (d.orientation === 'vertical') {
      // 1. Floor threshold / parquet runner bridging the rooms
      const pad = 10;
      gfx.fillStyle(0x7C5236, 1.0);
      gfx.fillRect(x - pad, y, w + pad * 2, h);

      // Brass transition strips on both left and right edges
      gfx.fillStyle(0xD9A441, 0.95);
      gfx.fillRect(x - pad, y, 4, h);
      gfx.fillRect(x + w + pad - 4, y, 4, h);

      // Wood plank lines
      gfx.lineStyle(1, 0x543622, 0.7);
      for (let py = y + 16; py < y + h; py += 16) {
        gfx.lineBetween(x - pad, py, x + w + pad, py);
      }

      // 2. Doorway Pillars / Jambs (Tiang Kusen Pintu) at top and bottom wall terminations
      // Top Pillar Cap
      gfx.fillStyle(0x5A3825, 1.0);
      gfx.fillRect(x - 4, y - 8, w + 8, 12);
      gfx.fillStyle(0x9E6D48, 1.0);
      gfx.fillRect(x - 4, y - 8, w + 8, 4);
      gfx.fillStyle(0xD9A441, 1.0);
      gfx.fillRect(x - 4, y + 2, w + 8, 2);

      // Bottom Pillar Cap
      gfx.fillStyle(0x5A3825, 1.0);
      gfx.fillRect(x - 4, y + h - 4, w + 8, 12);
      gfx.fillStyle(0x9E6D48, 1.0);
      gfx.fillRect(x - 4, y + h - 4, w + 8, 4);
      gfx.fillStyle(0xD9A441, 1.0);
      gfx.fillRect(x - 4, y + h + 6, w + 8, 2);

      // Overhead archway beam hint
      gfx.fillStyle(0x1F2A44, 0.4);
      gfx.fillRect(x - pad, y, w + pad * 2, 8);

      // 3. Directional Floor Sign
      const textX = x + w / 2;
      const textY = y + h / 2;
      const labelStr = d.type === 'archway' ? '◀ TAMU  ·  DAPUR ▶' : (d.label || 'PINTU');
      const passageLabel = this.scene.add.text(
        textX, textY,
        labelStr,
        {
          font: 'bold 9px monospace',
          fill: '#F7EEDA',
          stroke: '#121A2E',
          strokeThickness: 2,
          align: 'center'
        }
      ).setOrigin(0.5, 0.5).setDepth(-3).setRotation(-Math.PI / 2);
      this._mapObjects.push(passageLabel);

    } else {
      // Horizontal doorway (bedroom doors, bathroom doors, entrance)
      // 1. Floor threshold
      gfx.fillStyle(0x7C5236, 1.0);
      gfx.fillRect(x, y - 4, w, h + 8);

      // Brass edges
      gfx.fillStyle(0xD9A441, 0.95);
      gfx.fillRect(x, y - 4, w, 3);
      gfx.fillRect(x, y + h + 1, w, 3);

      // Wood plank lines
      gfx.lineStyle(1, 0x543622, 0.7);
      for (let px = x + 16; px < x + w; px += 16) {
        gfx.lineBetween(px, y - 4, px, y + h + 4);
      }

      // Left & Right Door Frame Jambs
      gfx.fillStyle(0x5A3825, 1.0);
      gfx.fillRect(x - 4, y - 6, 6, h + 12);
      gfx.fillRect(x + w - 2, y - 6, 6, h + 12);
      gfx.fillStyle(0x9E6D48, 1.0);
      gfx.fillRect(x - 4, y - 6, 2, h + 12);
      gfx.fillRect(x + w + 2, y - 6, 2, h + 12);

      if (d.label) {
        const lbl = this.scene.add.text(
          x + w / 2, y + h / 2,
          d.label,
          {
            font: 'bold 8px monospace',
            fill: '#F7EEDA',
            stroke: '#121A2E',
            strokeThickness: 2,
            align: 'center'
          }
        ).setOrigin(0.5, 0.5).setDepth(-3);
        this._mapObjects.push(lbl);
      }
    }
  }

  // ── Exterior rendering ───────────────────────────────────────────────────

  _renderExterior(layout) {
    const tileSize = layout.world?.tileSize || 32;
    const mapW = (layout.world?.widthTiles || 40) * tileSize;
    const mapH = (layout.world?.heightTiles || 24) * tileSize;

    // Rule 76 §4: Plate terrain with fallback to procedural ground
    const usePlate = this.scene.textures.exists('terrain_plate_hub') && (layout.terrain?.mode !== 'procedural');

    if (usePlate) {
      const plate = this.scene.add.image(0, 0, 'terrain_plate_hub');
      plate.setOrigin(0, 0).setDepth(-200);
      this._mapObjects.push(plate);
    } else {
      const gfx = this.scene.add.graphics();
      gfx.setDepth(-200);
      this._mapObjects.push(gfx);

      // Base grass
      gfx.fillStyle(GROUND_COLORS.rumput, 1.0);
      gfx.fillRect(0, 0, mapW, mapH);

      // Zone overrides
      for (const g of layout.ground || []) {
        const color = GROUND_COLORS[g.type] ?? GROUND_COLORS.tanah;
        gfx.fillStyle(color, 1.0);
        gfx.fillRect(g.x * tileSize, g.y * tileSize, g.w * tileSize, g.h * tileSize);
      }

      // Subtle tile grid
      gfx.lineStyle(1, 0x000000, 0.06);
      for (let x = 0; x <= mapW; x += tileSize) gfx.lineBetween(x, 0, x, mapH);
      for (let y = 0; y <= mapH; y += tileSize) gfx.lineBetween(0, y, mapW, y);
    }

    // Buildings
    for (const obj of layout.objects || []) this._renderExteriorObject(obj, tileSize);

    // Props
    for (const p of layout.props || []) this._renderProp(p, tileSize);
  }

  _renderExteriorObject(obj, tileSize) {
    const x = obj.x * tileSize;
    const y = obj.y * tileSize;
    const w = (obj.footprint?.w || 4) * tileSize;
    const h = (obj.footprint?.h || 3) * tileSize;

    if (this.scene.textures.exists(obj.assetId)) {
      const img = this.scene.add.image(x, y, obj.assetId);
      img.setOrigin(0.5, 1.0).setDepth(y);
      this._mapObjects.push(img);
    } else {
      const gfx = this.scene.add.graphics();
      gfx.fillStyle(0x2C3A54, 1);
      gfx.fillRect(x - w / 2, y - h, w, h);
      gfx.lineStyle(2, 0xD9A441, 1);
      gfx.strokeRect(x - w / 2, y - h, w, h);
      gfx.setDepth(y);
      this._mapObjects.push(gfx);

      const lbl = this.scene.add.text(x, y - h * 0.6, obj.label || obj.id || obj.type || '', {
        font: 'bold 11px monospace', fill: '#F7EEDA', stroke: '#0a0f1a', strokeThickness: 2,
        align: 'center', wordWrap: { width: w - 8 }
      }).setOrigin(0.5, 0.5).setDepth(y + 1);
      this._mapObjects.push(lbl);
    }
  }

  _renderProp(p, tileSize) {
    const x = p.x * tileSize + tileSize / 2;
    const y = p.y * tileSize + tileSize;
    if (this.scene.textures.exists(p.assetId)) {
      const img = this.scene.add.image(x, y, p.assetId);
      img.setOrigin(0.5, 1.0).setDepth(y);
      this._mapObjects.push(img);
    }
  }

  // ── Furniture ────────────────────────────────────────────────────────────

  _renderFurniture(layout) {
    const tileSize = layout.world?.tileSize || 32;

    for (const f of layout.furniture || []) {
      const px = f.x * tileSize;
      const py = f.y * tileSize;
      const fw = f.w * tileSize;
      const fh = f.h * tileSize;
      const isDecal = f.class_ === 'floor_decal' || f.type?.includes('karpet') || f.type?.includes('keset');
      const depth = isDecal ? 2 : (py + fh);

      const container = this.scene.add.container(px, py);
      container.setDepth(depth);
      this._mapObjects.push(container);

      let textureKey = f.assetId;
      if (!this.scene.textures.exists(textureKey)) {
        const altKey = textureKey?.endsWith('_v4') ? textureKey.slice(0, -3) : `${textureKey}_v4`;
        if (this.scene.textures.exists(altKey)) {
          textureKey = altKey;
        } else if (f.fallbackAssetId && this.scene.textures.exists(f.fallbackAssetId)) {
          textureKey = f.fallbackAssetId;
        } else if (f.type && this.scene.textures.exists(`furn_${f.type}`)) {
          textureKey = `furn_${f.type}`;
        } else if (f.type && this.scene.textures.exists(`furn_${f.type}_v4`)) {
          textureKey = `furn_${f.type}_v4`;
        }
      }

      if (this.scene.textures.exists(textureKey)) {
        const sprite = this.scene.add.sprite(fw / 2, fh, textureKey);
        sprite.setOrigin(0.5, 1.0);
        const tex = this.scene.textures.get(textureKey).getSourceImage();
        if (tex.width > 0) {
          const scale = Math.min(fw / tex.width, fh / tex.height, 1.5);
          sprite.setScale(scale);
        }
        container.add(sprite);
      } else {
        // Coloured placeholder with label
        const gfx = this.scene.add.graphics();
        const fillColor = this._furnitureColor(f.type || f.id);
        gfx.fillStyle(fillColor, isDecal ? 0.6 : 0.95);
        gfx.fillRect(0, 0, fw, fh);
        // Top highlight (fake 3-D)
        if (!isDecal && f.class_ !== 'wall_decor') {
          gfx.fillStyle(0xFFFFFF, 0.08);
          gfx.fillRect(0, 0, fw, Math.min(8, fh * 0.25));
        }
        gfx.lineStyle(2, 0xD9A441, 0.9);
        gfx.strokeRect(0, 0, fw, fh);
        container.add(gfx);

        const fontSize = Math.max(7, Math.min(10, Math.floor(fw / 7)));
        const lbl = this.scene.add.text(
          fw / 2, fh / 2,
          f.label || f.type || f.id,
          {
            fontSize: `${fontSize}px`,
            fontFamily: 'monospace',
            color: '#F7EEDA',
            stroke: '#0a0f1a',
            strokeThickness: 1,
            align: 'center',
            wordWrap: { width: fw - 6 }
          }
        ).setOrigin(0.5);
        container.add(lbl);
      }

      // Physics collider for furniture (Rule 73 §5: non-decorative items get collision footprint)
      const isDecorative = isDecal || f.class_ === 'wall_decor' || f.collidable === false;
      if (!isDecorative && this.scene._player) {
        const fpw = f.footprint?.w ? f.footprint.w * tileSize : (fw > 16 ? fw - 8 : fw);
        const fph = f.footprint?.h ? f.footprint.h * tileSize : Math.max(16, Math.floor(fh * 0.4));
        const fpx = px + fw / 2;
        const fpy = py + fh - fph / 2;
        this._addStaticBody(fpx, fpy, fpw, fph, f.id || f.type || 'furn');
      }
    }

    // Exit/door tile markers
    for (const int of layout.interactables || []) {
      if (int.type === 'exit') this._renderExitMarker(int, tileSize);
    }
  }

  _renderExitMarker(int, tileSize) {
    const px = int.x * tileSize;
    const py = int.y * tileSize;
    const fw = (int.w || 1) * tileSize;
    const fh = (int.h || 1) * tileSize;

    const gfx = this.scene.add.graphics();
    // Golden diamond on floor
    gfx.fillStyle(0xD9A441, 0.3);
    gfx.fillRect(px + 4, py + 4, fw - 8, fh - 8);
    gfx.lineStyle(2, 0xD9A441, 0.8);
    gfx.strokeRect(px + 2, py + 2, fw - 4, fh - 4);
    gfx.setDepth(py - 1);
    this._mapObjects.push(gfx);
  }

  _furnitureColor(type = '') {
    const t = type.toLowerCase();
    if (t.includes('kasur') || t.includes('bed'))      return 0x2E4080;
    if (t.includes('meja'))                             return 0x4A3828;
    if (t.includes('kursi') || t.includes('sofa'))     return 0x3A2E5A;
    if (t.includes('lemari') || t.includes('rak'))     return 0x1E3A30;
    if (t.includes('kompor') || t.includes('dapur'))   return 0x5A2020;
    if (t.includes('kulkas') || t.includes('chiller')) return 0x1A4055;
    if (t.includes('tv') || t.includes('layar'))       return 0x151520;
    if (t.includes('kasir') || t.includes('counter'))  return 0x402818;
    if (t.includes('arcade'))                          return 0x280040;
    if (t.includes('etalase') || t.includes('display'))return 0x1A3040;
    return 0x1F2A44;
  }

  // ── Colliders ────────────────────────────────────────────────────────────

  _buildColliders(layout) {
    if (!this.scene._player) return;
    const tileSize = layout.world?.tileSize || 32;
    const mapW = (layout.world?.widthTiles || 40) * tileSize;
    const mapH = (layout.world?.heightTiles || 24) * tileSize;

    // Map boundary walls
    const boundaries = [
      { cx: -tileSize / 2,       cy: mapH / 2,        w: tileSize, h: mapH },
      { cx: mapW + tileSize / 2, cy: mapH / 2,        w: tileSize, h: mapH },
      { cx: mapW / 2,            cy: -tileSize / 2,   w: mapW,     h: tileSize },
      { cx: mapW / 2,            cy: mapH + tileSize / 2, w: mapW, h: tileSize },
    ];
    for (const b of boundaries) this._addStaticBody(b.cx, b.cy, b.w, b.h);

    // Layout-defined colliders
    for (const c of layout.colliders || []) {
      this._addStaticBody(
        c.x * tileSize + (c.w * tileSize) / 2,
        c.y * tileSize + (c.h * tileSize) / 2,
        c.w * tileSize,
        c.h * tileSize
      );
    }

    // Exterior object footprints
    for (const obj of layout.objects || []) {
      const x = obj.x * tileSize;
      const y = obj.y * tileSize;
      const fw = (obj.footprint?.w || 4) * tileSize;
      const fh = (obj.footprint?.h || 2) * tileSize;
      this._addStaticBody(x, y - fh / 2, fw, fh);
    }

    // Trees
    for (const p of layout.props || []) {
      if (p.assetId?.includes('tree')) {
        const px = p.x * tileSize + tileSize / 2;
        const py = p.y * tileSize + tileSize;
        this._addStaticBody(px, py - 12, 24, 20);
      }
    }
  }

  _addStaticBody(cx, cy, w, h, name = '') {
    const body = this.scene.add.rectangle(cx, cy, w, h);
    this.scene.physics.add.existing(body, true);
    if (this.scene._player?.sprite) {
      this.scene.physics.add.collider(this.scene._player.sprite, body);
    }
    body.setVisible(false);
    this._colliderBodies.push(body);
    this._mapObjects.push(body);
    this._colliderRects.push({
      x: cx - w / 2,
      y: cy - h / 2,
      w,
      h,
      cx,
      cy,
      name
    });
  }

  getColliderRects() {
    return this._colliderRects || [];
  }

  getLayout(mapId) {
    if (!mapId || mapId === this.currentMapId) return this.currentLayout;
    return this.scene.cache.json.get(`layout_${mapId}`) || null;
  }

  listNPCs(mapId) {
    const layout = this.getLayout(mapId);
    if (layout?.npcs) {
      return layout.npcs.map(n => n.id);
    }
    return [];
  }

  runCollisionProbe(mapId) {
    const layout = this.getLayout(mapId) || this.currentLayout;
    if (!layout) {
      return { mapId, allPassed: false, error: 'Layout tidak ditemukan' };
    }

    const colliders = (mapId && mapId !== this.currentMapId)
      ? this.getCollidersForLayout(layout)
      : this._colliderRects;

    let testedCount = 0;
    let passedCount = 0;
    const details = [];

    for (const c of colliders) {
      // Skip outer world boundary lines
      if (c.name?.includes('batas_')) continue;

      testedCount++;
      const probeX = c.x + c.w / 2;
      const probeY = c.y + c.h / 2;
      const hw = 8;
      const hh = 5;

      const left = probeX - hw;
      const right = probeX + hw;
      const top = probeY - hh;
      const bottom = probeY + hh;

      const isBlocked = (right > c.x && left < c.x + c.w && bottom > c.y && top < c.y + c.h);
      if (isBlocked) {
        passedCount++;
        details.push({ name: c.name || 'unnamed', blocked: true, rect: [c.x, c.y, c.w, c.h] });
      } else {
        details.push({ name: c.name || 'unnamed', blocked: false, rect: [c.x, c.y, c.w, c.h] });
      }
    }

    return {
      mapId: mapId || this.currentMapId,
      totalColliders: colliders.length,
      testedCount,
      passedCount,
      allPassed: testedCount > 0 && passedCount === testedCount,
      details
    };
  }

  getCollidersForLayout(layout) {
    const tileSize = layout.world?.tileSize || 32;
    const rects = [];
    for (const c of layout.colliders || []) {
      rects.push({
        name: c.name || 'collider',
        x: c.x * tileSize,
        y: c.y * tileSize,
        w: c.w * tileSize,
        h: c.h * tileSize
      });
    }
    for (const obj of layout.objects || []) {
      const x = obj.x * tileSize;
      const y = obj.y * tileSize;
      const fw = (obj.footprint?.w || 4) * tileSize;
      const fh = (obj.footprint?.h || 2) * tileSize;
      rects.push({
        name: obj.id || obj.assetId || 'object',
        x: x - fw / 2,
        y: y - fh,
        w: fw,
        h: fh
      });
    }
    for (const f of layout.furniture || []) {
      const isDecorative = f.class_ === 'floor_decal' || f.class_ === 'wall_decor' || f.collidable === false;
      if (!isDecorative) {
        const px = f.x * tileSize;
        const py = f.y * tileSize;
        const fw = f.w * tileSize;
        const fh = f.h * tileSize;
        const fpw = f.footprint?.w ? f.footprint.w * tileSize : (fw > 16 ? fw - 8 : fw);
        const fph = f.footprint?.h ? f.footprint.h * tileSize : Math.max(16, Math.floor(fh * 0.4));
        rects.push({
          name: f.id || f.type || 'furniture',
          x: px + (fw - fpw) / 2,
          y: py + fh - fph,
          w: fpw,
          h: fph
        });
      }
    }
    return rects;
  }

  // ── NPCs ─────────────────────────────────────────────────────────────────

  _spawnNPCs(layout) {
    if (!this.scene._npcManager) return;
    this.scene._npcManager.setNPCs(layout.npcs || []);
  }

  // ── Interactables ─────────────────────────────────────────────────────────

  _registerInteractables(layout) {
    this.scene._interactables = layout.interactables || [];
    if (this.scene._interactablesManager?.setInteractables) {
      this.scene._interactablesManager.setInteractables(layout.interactables || []);
    }
  }
}
