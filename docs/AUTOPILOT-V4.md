# AUTOPILOT v4 — Perbaikan Interior, Kolisi, Energi, Motor, Terrain, Efek Misi

> Melengkapi AUTOPILOT.md dan AUTOPILOT-EXPANSION.md. Status di `docs/PROGRESS-V4.md` (templat di bagian 3). Protokol umum sama: bukti wajib di tiap gerbang, satu gerbang = satu commit, berhenti hanya pada checkpoint/isu esensial/3 iterasi gagal, uji sendiri di browser, **jangan menimpa kerja manual pengguna**, aset baru bersufiks `_v4` dan aset lama dipertahankan sampai E2E lulus.

## 1. Fase dan gerbang

### G0 · Audit, patch, preflight
1. Lihat `docs/reference/*`. Audit: (a) daftar semua furnitur/objek per peta dengan status (AI-generated / placeholder / digambar kode) → `docs/AUDIT-V4.md`; (b) objek tanpa footprint/kolisi; (c) NPC per peta (temukan NPC interior yang tersisa di hub, termasuk ibu) dan penyebab oklusi (depth); (d) kondisi tata letak dapur/kamar mandi/ruang tamu vs rule 73; (e) bangunan game center (eksterior) vs bangunan lain; (f) bar bensin dan konsumsi bensin saat ini; (g) data belanja/item saat ini.
2. Terapkan `docs/EXPANSION-PATCH-V4.md`; tampilkan `git diff --stat`. Tag git `pre-v4`. Gabungkan `data/v4.config.additions.json` dan `data/items.phase1.json` ke data proyek tanpa menimpa nilai pengguna.
3. Probe image generation (rule 60 §1).
**Gerbang:** AUDIT-V4.md selesai; patch diterapkan; semua tes lama hijau.

### G1 · Perbaikan cepat (tanpa aset)
(a) **Kolisi:** setiap objek non-dekoratif mendapat footprint; collider pemain kecil; `collisionProbe`; (b) **NPC dan oklusi:** hapus NPC interior dari hub (ibu), perbaiki depth bangunan/NPC, uji oklusi, validasi nama pemain vs NPC; (c) **efek misi selesai** (rule 77) + banner/daftar misi bercentang.
**Gerbang:** probe kolisi hijau di 7 peta; `map-check` hijau termasuk oklusi; ibu tidak ada di hub (bukti `listNPCs('town_hub')`); tangkapan layar efek misi pada t=100/400/800 ms.

### G2 · Energi, inventaris, hotbar (ikon placeholder)
Implementasi rule 74 penuh: domain energi, hubungan dengan `advanceTime` dan aktivitas, bar energi di widget, inventaris, hotbar bawah-tengah bergaya referensi, katalog item, pembelian → tas di minimarket, "makan di tempat" di kantin, makan di dapur ibu, save v3 + migrasi.
**Gerbang:** uji rule 74 §6 hijau; tangkapan layar hotbar dan bar energi (desktop dan tablet).

### G3 · Motor (sprite placeholder)
Rule 75: tombol kendaraan + V, mode motor, kecepatan, bensin per 5 detik (akumulator), larangan interior + parkir otomatis, motor parkir, animasi naik/turun prosedural.
**Gerbang:** uji rule 75 §5 hijau (dengan jam palsu); tangkapan layar frame animasi.

### G4 · Tata letak berbasis slot untuk 7 peta (placeholder berlabel)
Rule 73 + `data/furniture-catalog-v4.json`: Layout Spec per peta (`docs/layouts/*.md` dan slot di layout JSON), render dinding belakang/lis, penataan ulang **dapur, kamar mandi, ruang tamu** (dan semua peta lain) sesuai pedoman, `tools/derive_briefs_from_layout.py`, `tests/layout-check.html`.
**Gerbang:** `layout-check` dan `map-check` hijau untuk semua peta; tangkapan layar overlay setiap ruang; deretan counter dapur kontinu (bukti).

### G5 · Aset batch 1 → CHECKPOINT C
Urutan: furnitur rumah (turunan slot) → ikon item + ikon HUD → `vehicle_motor_ref` (style lock). Alur rule 60 (+ §11) lengkap; skala seragam per sheet; kandidat terbaik. Render **dapur, kamar mandi, ruang tamu** di game dengan aset baru, hotbar berisi ikon item, dan satu tangkapan layar motor (tampak referensi). Simpan di `docs/checkpoint-C/`.
**Gerbang = CHECKPOINT C (manusia):** berhenti; tampilkan gambar, ringkasan QA, cacat yang Anda lihat sendiri (susunan dapur, kecocokan ukuran, konsistensi dengan hub, ikon terbaca di hotbar), tanya: *"Setujui gaya interior v4, ikon item, dan jangkar motor ini atau beri catatan?"*

### G6 · Aset sisanya
Sprite pengendara L/P + motor parkir + `icon_motor`; **game center eksterior diulang** (2 kandidat, pilih terbaik, dasar rata, bersihkan artefak) + tata ulang interior; furnitur sekolah, minimarket, kosmetik, SPBU, game center (turunan slot, lengkap sesuai katalog); sheet dekor (`nature_v4`, `street_v4`, `decal_sheet_v4`). Perbarui manifest, `ASSET-LOG.md`, kredit; ganti placeholder; jalankan lagi `layout-check`.
**Gerbang:** tidak ada objek non-dekoratif tanpa aset generate kecuali yang dicatat sebagai placeholder dengan alasan; laporan ready/placeholder; contact sheet per ruang.

### G7 · Terrain plate → CHECKPOINT D
Rule 76: render guide dari layout hub saat ini, generate plate, uji kesesuaian (IoU, tepi), Level 2 bila perlu, integrasi `terrain.mode`, pasang dekor (pohon, decal) pada posisi layout, `tests/terrain-check.html`. Tangkapan layar tiap persimpangan, tiap pintu bangunan, dan satu tampilan bermotor. Simpan di `docs/checkpoint-D/`.
**Gerbang = CHECKPOINT D (manusia):** berhenti; tampilkan perbandingan sebelum/sesudah, tabel IoU, cacat yang Anda lihat; tanya: *"Setujui tampilan terrain dan motor atau beri catatan?"*

### G8 · Integrasi, QA E2E, hardening, laporan
Skenario E2E ≥ 3 hari: bangun di rumah, makan di dapur ibu (+energi), ke sekolah (belajar mengurangi energi), beli makanan di kantin/minimarket → tas → pakai dari hotbar, naik motor ke SPBU (bensin turun per 5 detik, isi bensin), game center, misi selesai (efek), pulang, tidur. Audit: konsistensi visual interior vs hub, objek melayang, kolisi, emoji/gradient (di luar pengecualian), keamanan (rule 50 butir 11–17), performa (ukuran plate/aset). Dokumen: `docs/FINAL-REPORT-V4.md` (selesai-teruji/belum, aset ready/placeholder/ditolak, hasil tes, batasan).
**Gerbang:** semua tes hijau; laporan akhir.

## 2. Urutan modular
G1, G2, G3, G4 tidak membutuhkan aset baru dan dapat dijalankan terpisah (lihat `START-V4.md`). G5–G7 membutuhkan G4 (slot) dan image generation.

## 3. Templat `docs/PROGRESS-V4.md`
```
# PROGRESS V4
Tag pra-v4: pre-v4 | Kapabilitas gambar: ...
- [ ] G0 Audit + patch   - [ ] G1 Kolisi + NPC/oklusi + efek misi
- [ ] G2 Energi + hotbar  - [ ] G3 Motor
- [ ] G4 Tata letak slot 7 peta
- [ ] G5 Aset batch 1 → [ ] CHECKPOINT C disetujui
- [ ] G6 Aset sisanya (+ game center)
- [ ] G7 Terrain → [ ] CHECKPOINT D disetujui
- [ ] G8 Integrasi + QA + laporan
Log gerbang: | Tanggal | Gerbang | Hasil | Bukti | Commit |
Aset placeholder tersisa: ...   Temuan terbuka: ...
```
