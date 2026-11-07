/**
 * assetLoader.js — Asset loader for Life Journey.
 * Reads asset-manifest.json and registers assets with Phaser.
 * Falls back to labeled canvas placeholders for missing/placeholder assets.
 */

/** Map of assetId → { key, isPlaceholder } */
const registry = new Map();

/**
 * Create a canvas placeholder texture.
 * @param {Phaser.Scene} scene
 * @param {string} key
 * @param {number} width
 * @param {number} height
 * @param {string} label
 * @param {string} [bgColor='#9AA0AA']
 */
function createPlaceholderTexture(scene, key, width, height, label, bgColor = '#9AA0AA') {
  if (scene.textures.exists(key)) return;

  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');

  // Background
  ctx.fillStyle = bgColor;
  ctx.fillRect(0, 0, width, height);

  // Border
  ctx.strokeStyle = '#5E3F2A';
  ctx.lineWidth = 2;
  ctx.strokeRect(1, 1, width - 2, height - 2);

  // Cross-hatch pattern
  ctx.strokeStyle = 'rgba(94,63,42,0.2)';
  ctx.lineWidth = 1;
  for (let x = 0; x < width; x += 16) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, height);
    ctx.stroke();
  }
  for (let y = 0; y < height; y += 16) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(width, y);
    ctx.stroke();
  }

  // Label text
  ctx.fillStyle = '#1F2A44';
  ctx.font = `bold ${Math.max(8, Math.min(14, width / 8))}px sans-serif`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  const lines = label.split('\n');
  const lineH = Math.max(10, Math.min(16, width / 7));
  lines.forEach((line, i) => {
    ctx.fillText(line, width / 2, height / 2 + (i - (lines.length - 1) / 2) * lineH, width - 8);
  });

  scene.textures.addCanvas(key, canvas);
}

/**
 * Load all assets listed in the manifest into the given Phaser scene.
 * Call this during Preload.preload().
 * @param {Phaser.Scene} scene
 * @param {object[]} manifest - parsed asset-manifest.json `.assets` array
 */
export function loadAssets(scene, manifest) {
  for (const entry of manifest) {
    const key = entry.id;
    const isPlaceholder = entry.status !== 'ready';

    registry.set(key, { key, isPlaceholder });

    if (isPlaceholder) {
      // Will be created as canvas texture after scene is ready
      scene.load.once('complete', () => {
        const w = entry.frameWidth ?? entry.width ?? 64;
        const h = entry.frameHeight ?? entry.height ?? 64;
        createPlaceholderTexture(scene, key, w, h, key);
        if (entry.type === 'spritesheet') {
          // For spritesheets, we need a valid texture
          // Placeholder canvas already registered; Phaser will use it
        }
      });
    } else {
      // Load real file
      if (entry.type === 'spritesheet') {
        scene.load.spritesheet(key, entry.file, {
          frameWidth: entry.frameWidth,
          frameHeight: entry.frameHeight,
        });
      } else {
        scene.load.image(key, entry.file);
      }
    }
  }
}

/**
 * Create placeholder textures immediately (for use after scene ready).
 * @param {Phaser.Scene} scene
 * @param {object[]} manifest
 */
export function createPlaceholders(scene, manifest) {
  for (const entry of manifest) {
    if (entry.status !== 'ready') {
      const key = entry.id;
      const w = entry.frameWidth ?? entry.width ?? 64;
      const h = entry.frameHeight ?? entry.height ?? 64;
      createPlaceholderTexture(scene, key, w, h, key);
    }
  }
}

/**
 * Get the registered Phaser texture key for an asset id.
 * @param {string} id
 * @returns {string}
 */
export function getAssetKey(id) {
  return registry.get(id)?.key ?? id;
}

/**
 * Check if an asset is currently a placeholder.
 * @param {string} id
 * @returns {boolean}
 */
export function isPlaceholder(id) {
  return registry.get(id)?.isPlaceholder ?? true;
}
