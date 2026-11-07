/**
 * groundTiles.js — Procedural ground tile generator according to Rule 20 Section 7.
 * Generates runtime canvas textures for: rumput, jalan, trotoar, tanah/halaman.
 * strictly using colors from palette.json.
 */

export function createProceduralTiles(scene, tileSize = 32) {
  // 1. Rumput (Grass)
  const grassCanvas = document.createElement('canvas');
  grassCanvas.width = tileSize;
  grassCanvas.height = tileSize;
  const gctx = grassCanvas.getContext('2d');
  gctx.fillStyle = '#6F9262'; // green-600
  gctx.fillRect(0, 0, tileSize, tileSize);
  gctx.fillStyle = '#A5BE93'; // green-400 flecks
  gctx.fillRect(4, 4, 2, 2);
  gctx.fillRect(18, 12, 2, 2);
  gctx.fillRect(10, 24, 2, 2);
  gctx.fillStyle = '#44603F'; // green-800 shade
  gctx.fillRect(6, 6, 2, 2);
  gctx.fillRect(20, 14, 2, 2);
  scene.textures.addCanvas('tile_rumput', grassCanvas);

  // 2. Jalan (Road)
  const roadCanvas = document.createElement('canvas');
  roadCanvas.width = tileSize;
  roadCanvas.height = tileSize;
  const rctx = roadCanvas.getContext('2d');
  rctx.fillStyle = '#28344F'; // dark asphalt tone
  rctx.fillRect(0, 0, tileSize, tileSize);
  rctx.fillStyle = '#D9A441'; // yellow road mark in center
  rctx.fillRect(14, 15, 4, 2);
  scene.textures.addCanvas('tile_jalan', roadCanvas);

  // 3. Trotoar (Sidewalk / Paving)
  const sidewalkCanvas = document.createElement('canvas');
  sidewalkCanvas.width = tileSize;
  sidewalkCanvas.height = tileSize;
  const sctx = sidewalkCanvas.getContext('2d');
  sctx.fillStyle = '#C9A27A'; // brown-300 light stone
  sctx.fillRect(0, 0, tileSize, tileSize);
  sctx.strokeStyle = '#9A6F4C'; // stone borders
  sctx.strokeRect(0.5, 0.5, tileSize - 1, tileSize - 1);
  scene.textures.addCanvas('tile_trotoar', sidewalkCanvas);

  // 4. Halaman / Tanah (Yard / Dirt)
  const yardCanvas = document.createElement('canvas');
  yardCanvas.width = tileSize;
  yardCanvas.height = tileSize;
  const yctx = yardCanvas.getContext('2d');
  yctx.fillStyle = '#E9D8B4'; // cream-300
  yctx.fillRect(0, 0, tileSize, tileSize);
  yctx.fillStyle = '#C9A27A';
  yctx.fillRect(8, 8, 3, 3);
  yctx.fillRect(22, 16, 2, 2);
  scene.textures.addCanvas('tile_halaman', yardCanvas);
}
