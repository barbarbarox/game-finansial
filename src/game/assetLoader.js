/**
 * assetLoader.js — Asset loader for Life Journey.
 * Reads asset-manifest.json and registers assets with Phaser.
 * Falls back to labeled canvas placeholders for missing/placeholder assets.
 */

const registry = new Map();

/**
 * Create a canvas placeholder texture.
 */
function createPlaceholderTexture(scene, key, width, height, label, bgColor = '#34456B') {
  if (scene.textures.exists(key)) return;

  const canvas = document.createElement('canvas');
  canvas.width = Math.max(32, width);
  canvas.height = Math.max(32, height);
  const ctx = canvas.getContext('2d');

  // Background
  ctx.fillStyle = bgColor;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Border
  ctx.strokeStyle = '#D9A441';
  ctx.lineWidth = 2;
  ctx.strokeRect(1, 1, canvas.width - 2, canvas.height - 2);

  // Label text
  ctx.fillStyle = '#F7EEDA';
  ctx.font = `bold ${Math.max(9, Math.min(13, canvas.width / 10))}px sans-serif`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(label, canvas.width / 2, canvas.height / 2, canvas.width - 6);

  scene.textures.addCanvas(key, canvas);
}

/**
 * Load all assets listed in the manifest into the given Phaser scene.
 * Call this during Preload.preload().
 */
export function loadAssets(scene, manifest) {
  for (const entry of manifest) {
    const key = entry.id;
    const isReady = entry.status === 'ready';

    registry.set(key, { key, isPlaceholder: !isReady });

    if (isReady && entry.file) {
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
 * Create placeholder textures for assets not yet ready.
 */
export function createPlaceholders(scene, manifest) {
  for (const entry of manifest) {
    const key = entry.id;
    if (entry.status !== 'ready') {
      const w = entry.frameWidth || entry.width || 64;
      const h = entry.frameHeight || entry.height || 64;
      createPlaceholderTexture(scene, key, w, h, key);
    }
  }
}

export function getAssetKey(id) {
  return registry.get(id)?.key || id;
}

export function isPlaceholder(id) {
  return registry.get(id)?.isPlaceholder ?? true;
}
