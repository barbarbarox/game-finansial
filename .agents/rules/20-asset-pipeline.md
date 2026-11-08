---
trigger: model_decision
description: "Terapkan setiap kali memuat, menamai, mendaftarkan, atau merujuk gambar, sprite, peta layout, font, ikon, audio; atau saat menyentuh folder assets/, data/maps/, asset-manifest.json."
---

# 20 · Pipeline Aset (struktur, penamaan, manifest, peta)

Proses pembuatan/perbaikan aset ada di `60-asset-generation-qa.md`. File ini mengatur **di mana dan bagaimana aset dipakai**.

## 1. Prinsip
- `assets/asset-manifest.json` = satu-satunya sumber kebenaran ukuran, frame, anchor, footprint, status, dan sumber. Tidak ada tebakan ukuran dari gambar.
- Hanya satu loader (`src/game/assetLoader.js`) yang membaca manifest dan mendaftarkan aset ke Phaser dan DOM.
- Aset belum ada / gagal QA → loader memakai **placeholder berlabel** (mode debug) + peringatan konsol. Mengganti placeholder dengan aset final = taruh file + ubah `status` di manifest, tanpa ubah kode.

## 2. Folder
`assets/` → `characters/`, `npcs/`, `portraits/`, `buildings/`, `furniture/`, `props/`, `backgrounds/` (key art, panel lokasi), `icons/`, `fonts/`, `audio/` (opsional), `_raw/` (keluaran mentah generator, tidak dimuat runtime), `_rejected/` (gagal QA, untuk analisis), `palette.json`.
Lainnya: `data/maps/town_hub.layout.json`, `data/asset-briefs.json`, `tools/`.

## 3. Penamaan (snake_case)
`char_player_m_casual.png`, `char_player_f_casual.png`, `npc_ibu.png`, `bld_minimarket.png`, `prop_pohon_mangga.png`, `bg_panel_kantin.png`, `bg_mainmenu_town.png`, `icon_coin.png`, `logo_emblem.png`. Pola: `<kategori>_<nama>[_<varian>].png`.

## 4. Spesifikasi teknis
- PNG 32-bit transparan, tanpa anti-aliasing (alpha hanya 0 atau 255), tanpa metadata, warna terkunci ke `assets/palette.json`.
- Ukuran akhir tiap aset ditentukan di `data/asset-briefs.json` (kelipatan 32 untuk bangunan/prop yang punya footprint).
- Total aset runtime ≤ ~20 MB.

## 5. Manifest (per entri)
`id`, `file`, `type` (spritesheet | image | icon | font | audio), `frameWidth`, `frameHeight`, `frames` (peta nama→indeks), `anchor` (x,y 0–1, mis. kaki karakter 0.5,1), `footprint` (rect kolisi relatif di dasar sprite), `doorAnchor` (untuk bangunan), `symmetric`, `status` (`ready` | `placeholder`), `source` (`ai-generated` | pihak ketiga | manual), `tool`, `generatedAt`, `promptRef`, `qa` (ringkasan hasil validator), `license`, `creditRequired`. Template: `docs/ASSET-MANIFEST.template.json`.

## 6. Peta hub = layout-as-data (tanpa Tiled; peta interior dan registry peta: lihat `70-interior-maps-and-buildings.md`)
`data/maps/town_hub.layout.json` ditulis agen dan terdiri dari:
- `world`: lebar×tinggi dalam tile (default 40×24 tile @32 px) dan titik spawn pemain.
- `ground`: daftar zona persegi bertipe `rumput | jalan | trotoar | tanah | halaman` (dirender oleh tile prosedural, bagian 7).
- `objects`: `{assetId, x, y, layer, footprint?}` untuk bangunan, pohon, pagar, bangku, tiang lampu, dsb. Penempatan berdasar **dasar sprite** (anchor kaki/dasar).
- `colliders`: persegi tambahan (batas dunia, air, dsb.).
- `interactables`: `{id, type (door|piggybank|npc|sign), locationId, rect, prompt, panel}`; pintu bangunan memakai `doorAnchor`.
- `npcs`: `{id, assetId, x, y, dialogId}`.
Aturan tata letak: jarak antar-lokasi ≤ 20 detik berjalan; sekolah di kiri-atas, rumah pemain kiri-bawah, minimarket + toko kosmetik berdampingan kanan-atas, SPBU di tepi kanan, game center kanan-bawah, persimpangan di tengah; jalur lebar ≥ 2 tile; tidak ada jalan buntu yang menjebak pemain.
- Verifikasi wajib: `toggleCollisionOverlay()` + tangkapan layar browser untuk memeriksa kolisi, pintu, dan kedalaman (pemain di belakang atap/pohon bila y lebih kecil dari dasar objek). Perbaiki koordinat sampai lolos.

## 7. Tile prosedural: tanah, lantai, dan dinding (satu-satunya "gambar via kode" yang diizinkan; interior: lihat `70-interior-maps-and-buildings.md` §3)
Tile rumput (2 varian), jalan aspal (marka dibuat kode), trotoar paving, tanah/halaman dibuat di `src/assets-gen/groundTiles.js` hanya dari warna `palette.json` dengan pola sederhana (bintik/garis), ukuran `tileSize`, pola yang menyambung. Tidak boleh dipakai untuk karakter, bangunan, prop, atau ikon.

## 8. Lisensi & kredit
Aset buatan AI: `source: "ai-generated"`, nama alat, tanggal, prompt di manifest + `docs/ASSET-LICENSES.md`. Layar **Kredit** (Settings) membaca `assets/credits.json` (alat generator, font OFL, pustaka). Aset pihak ketiga hanya bila lisensinya tercatat.
