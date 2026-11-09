# Laporan Pengujian Hijau: B13 (Sprite NPC Budi Bergaya Kartun/Chibi)

- **Status:** PASS (HIJAU)
- **Komponen:** `src/game/npc.js`, `src/game/scenes/Preload.js`, `data/maps/school.layout.json`, `data/maps/town_hub.layout.json`, `assets/npcs/npc_budi_v6.png`, `tools/test_j5_green.py`
- **Tangkapan Layar:**
  - SEBELUM (RED): `docs/regression/b13_sprite_budi_kartun_red.png`
  - SESUDAH (GREEN): `docs/regression/b13_sprite_budi_kartun_green.png`
- **Akar Masalah:**
  Sprite NPC Budi sebelumnya menggunakan gaya ilustrasi kartun / chibi dengan kepala besar bergaris halus (bukan pixel art), yang tidak konsisten dengan sprite karakter pemain dan NPC lain yang berestetika pixel art retro.
- **Perbaikan yang Diterapkan:**
  1. Dibuat sprite pixel art baru `npc_budi_v6.png` (32x64) dan spritesheet `npc_sheet_budi_v6.png` (96x64 3-views) dengan proporsi tubuh remaja realistis, palet warna seragam sekolah SMA, dan ukuran pixel grid 2.0x identik dengan karakter pemain.
  2. Mendaftarkan `npc_budi_v6` pada `assets/asset-manifest.json` dan memuatnya di `Preload.js`.
  3. Memperbarui `src/game/npc.js` agar memprioritaskan `def.assetId` dan `npc_budi_v6` untuk def ID `npc_budi` atau `npc_teman`.
  4. Mengatur `assetId: "npc_budi_v6"` di `school.layout.json` dan `town_hub.layout.json`.
- **Hasil Verifikasi:**
  Pengujian runtime via CDP membuktikan NPC Budi di lorong sekolah berhasil merender sprite `npc_budi_v6` dengan gaya pixel art proporsional yang menyatu sempurna dengan visual pemain.

