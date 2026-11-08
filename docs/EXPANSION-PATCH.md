# EXPANSION-PATCH — perubahan pada file lama (diterapkan oleh agen pada prompt E0)
> Terapkan setiap penggantian **persis**. Jika teks lama sudah berbeda (mis. Anda mengeditnya), terapkan *maksud* perubahan itu dan catat di `docs/DECISIONS.md`. Setelah selesai, tampilkan `git diff --stat` sebagai bukti. Jangan mengubah hal lain.

## Patch 1 — `AGENTS.md`
**Cari:**
```
dunia top-down kota kecil (satu peta hub)
```
**Ganti dengan:**
```
dunia top-down kota kecil (peta hub + interior bangunan yang dapat dijelajahi; permainan dimulai di dalam rumah pemain), dialog NPC dengan potret kiri-kanan, sistem waktu 24 jam
```

## Patch 2 — `AGENTS.md`
**Cari:**
```
(satu-satunya pengecualian: tile tanah prosedural di `20-asset-pipeline.md`)
```
**Ganti dengan:**
```
(pengecualian: tile tanah, lantai, dan dinding prosedural sesuai `20-asset-pipeline.md` dan `70-interior-maps-and-buildings.md`)
```

## Patch 3 — `AGENTS.md`
**Cari:**
```
- `60-asset-generation-qa.md` — pipeline generate → proses → QA → perbaiki → daftarkan
```
**Ganti dengan:**
```
- `60-asset-generation-qa.md` — pipeline generate → proses → QA → perbaiki → daftarkan
- `70-interior-maps-and-buildings.md` — peta interior, perpindahan peta, fitur bangunan, awal permainan di rumah
- `71-dialogue-system.md` — dialog dengan potret kiri-kanan dan menu pilihan
- `72-time-system.md` — jam 24 jam, widget waktu, aktivitas yang memakan waktu, jam buka
```

## Patch 4 — `AGENTS.md`
**Cari:**
```
jangan menghapus aset hasil generate yang sudah lolos QA tanpa alasan tercatat.
```
**Ganti dengan:**
```
jangan menghapus aset hasil generate yang sudah lolos QA tanpa alasan tercatat.
13. **Perubahan manual pengguna bersifat otoritatif.** Pengguna telah mengubah UI (tombol, menu) dan widget waktu. Sebelum mengubah file yang mungkin telah disunting manual, audit (`git log`, `git diff`, baca kode), pertahankan tampilan/perilaku yang ada, dan hanya refactor bila perlu untuk integrasi. Catat apa yang dipertahankan di `docs/DECISIONS.md`.
```

## Patch 5 — `.agents/rules/10-visual-identity.md`
**Cari:**
```
- DILARANG: gradient, glassmorphism, neon, bayangan blur, pill UI, kartu "SaaS", ikon emoji, elemen tanpa fungsi.
```
**Ganti dengan:**
```
- DILARANG: gradient, glassmorphism, neon, bayangan blur, pill UI, kartu "SaaS", ikon emoji, elemen tanpa fungsi. **Pengecualian disetujui pengguna:** gradient langit hanya di komponen Sky Dial widget waktu, dan tab hari (Day Pill) berbentuk tab emas bersudut piksel. Emoji tetap dilarang (matahari/bulan dibuat dengan CSS/sprite).
```

## Patch 6 — `.agents/rules/10-visual-identity.md`
**Cari:**
```
| `--grey-400` | #9AA0AA | HANYA untuk seragam putih-abu-abu |

```
**Ganti dengan:**
```
| `--grey-400` | #9AA0AA | HANYA untuk seragam putih-abu-abu |
| `--sky-dawn` | #E8B25A | HANYA Sky Dial: fajar keemasan (pagi) |
| `--sky-day` | #7FB6D9 | HANYA Sky Dial: biru cerah (siang) |
| `--sky-dusk` | #E07B4F | HANYA Sky Dial: senja jingga kemerahan (sore) |
| `--sky-night` | #16213B | HANYA Sky Dial: biru pekat (malam) |

```

## Patch 7 — `.agents/rules/20-asset-pipeline.md`
**Cari:**
```
`assets/` → `characters/`, `npcs/`, `buildings/`, `props/`, `backgrounds/`
```
**Ganti dengan:**
```
`assets/` → `characters/`, `npcs/`, `portraits/`, `buildings/`, `furniture/`, `props/`, `backgrounds/`
```

## Patch 8 — `.agents/rules/20-asset-pipeline.md`
**Cari:**
```
## 7. Tile tanah prosedural (satu-satunya "gambar via kode" yang diizinkan)
```
**Ganti dengan:**
```
## 7. Tile prosedural: tanah, lantai, dan dinding (satu-satunya "gambar via kode" yang diizinkan; interior: lihat `70-interior-maps-and-buildings.md` §3)
```

## Patch 9 — `.agents/rules/20-asset-pipeline.md`
**Cari:**
```
## 6. Peta hub = layout-as-data (tanpa Tiled)
```
**Ganti dengan:**
```
## 6. Peta hub = layout-as-data (tanpa Tiled; peta interior dan registry peta: lihat `70-interior-maps-and-buildings.md`)
```

## Patch 10 — `.agents/rules/40-phase1-game-design.md`
**Cari:**
```
Semua lokasi adalah **bangunan di peta hub**; menyentuh pintu membuka **panel DOM** dengan ilustrasi `bg_panel_*` (tidak ada interior yang bisa dijelajahi). NPC ibu, ayah, dan teman berdiri di hub; penjual/kasir tampil di panel masing-masing.
```
**Ganti dengan:**
```
Setiap lokasi adalah **bangunan di peta hub dengan peta interior yang dapat dijelajahi** (lihat `70-interior-maps-and-buildings.md`); pemain benar-benar masuk, dan transaksi hanya terjadi pada titik interaksi spesifik di dalamnya (mis. belanja makan/jajan hanya di konter kantin). Permainan dimulai di dalam rumah pemain.
```

## Patch 11 — `.agents/rules/40-phase1-game-design.md`
**Cari:**
```
- Durasi Fase 1: 2 bulan permainan × 30 hari; `dayDurationSeconds: 12` (≈12 menit bermain; tombol tidur untuk melompat hari).
```
**Ganti dengan:**
```
- Durasi Fase 1: `months` (default 2) × 30 hari. Pengaturan waktu mengikuti `72-time-system.md` (siklus 24 jam, aktivitas memakan waktu); total waktu bermain jauh lebih panjang daripada versi lama, jadi untuk demo kompetisi disarankan `months: 1`.
```

## Patch 12 — `.agents/rules/30-architecture-code.md`
**Cari:**
```
## 5. Jam permainan
```
**Ganti dengan:**
```
## 5. Jam permainan (DIGANTI oleh `72-time-system.md`; paragraf di bawah hanya ringkasan lama)
```

## Patch 13 — `.agents/rules/30-architecture-code.md`
**Cari:**
```
Key `lj_save_v1` (satu objek).
```
**Ganti dengan:**
```
Key `lj_save_v2` (satu objek; migrasi dari `lj_save_v1` wajib, lihat 70 dan 72).
```

## Tambah di akhir `.agents/rules/60-asset-generation-qa.md`
```
## 10. Furnitur dan potret (tambahan v3)
- **Skala seragam per sheet:** untuk sheet berisi banyak item (furnitur, prop, potret), hitung SATU faktor skala untuk seluruh sheet (median dari `target_i / terukur_i`), bukan skala per item, supaya ukuran piksel tampak antar-item seragam. Setelah diskalakan, tiap item harus berada dalam ±20% dari ukuran target brief; item yang menyimpang digenerate ulang (bukan di-skala sendiri). Berlaku juga untuk `prop_sheet_*` yang sudah ada.
- Brief tambahan: `data/asset-briefs-expansion.json`; gaya: `docs/STYLE-BIBLE-INTERIOR.md`. Furnitur keluar ke `assets/furniture/`, potret ke `assets/portraits/` (192×256, menghadap kanan).
- Validator tambahan: `noText` diperiksa visual; dasar furnitur rata di baris terbawah; potret mengisi ≥ 85% tinggi dan identitas warna cocok dengan sprite.
```

## Tambah di akhir `.agents/rules/50-security.md`
```
14. **Data peta dan dialog:** layout peta dan dialog divalidasi skema saat dimuat (tipe, rentang, referensi aset/peta yang ada, efek dialog di whitelist). Teks dialog dan nama dirender hanya lewat `textContent`.
15. **Hook uji tambahan** (`teleportToMap`, `startDialogue`, `choose`, `listInteractables`) tunduk pada aturan hook debug yang sama: hanya aktif dengan `?debug=1` dan `debugEnabled: true`.
```
