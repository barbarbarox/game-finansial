# AUTOPILOT EKSPANSI v3 — Interior, Dialog Potret, Sistem Waktu

> Melengkapi `docs/AUTOPILOT.md` (fase P0–P9 sudah selesai). Status di `docs/PROGRESS-EXPANSION.md` (buat dari templat di bagian 3). Protokol umum (bukti wajib, satu gerbang = satu commit, anggaran percobaan, berhenti hanya pada checkpoint/isu esensial, uji sendiri di browser) sama dengan AUTOPILOT.md bagian 0 dan 3.

## 1. Fase dan gerbang

### E0 · Audit, patch rules, preflight
1. **Audit kondisi saat ini** (`git log`, `git status`, baca widget waktu, UI, kode peta). Tulis `docs/DECISIONS.md` bagian "Perubahan manual pengguna yang dipertahankan".
2. Terapkan `docs/EXPANSION-PATCH.md` ke AGENTS.md dan rules lama. Tampilkan `git diff --stat`.
3. Probe ulang image generation (rule 60 §1) dan catat.
4. Backup: tag git `pre-expansion`.
**Gerbang:** PROGRESS-EXPANSION terisi; diff patch ditampilkan; tes lama (`self-test.html`) masih hijau.

### E1 · Sistem waktu (tanpa aset baru)
Implementasi `72-time-system.md`: domain clock + `advanceTime`, hook berurutan, katalog aktivitas, TimeSkip overlay, jam buka, tidur, penghubungan widget pengguna ke domain, migrasi save v1→v2, transaksi bertanda waktu, hook debug, uji 1–9.
**Gerbang:** semua uji waktu hijau di browser + tangkapan layar widget pada 4 fase hari + bukti `main_game` 1 jam menambah tepat 60 menit.

### E2 · Kerangka peta interior (placeholder dulu)
`data/maps/index.json`, layout v2, MapManager (transisi fade, spawn/exit, simpan posisi), renderer lantai/dinding prosedural, y-sort, kamera, label lokasi, `tests/map-check.html`. Buat layout awal semua 7 peta dengan furnitur **placeholder berlabel**, termasuk pintu hub ↔ interior timbal-balik.
**Gerbang:** `map-check.html` hijau (keterjangkauan BFS, timbal-balik exit, batas, spawn); tangkapan layar tiap peta dengan overlay kolisi; berpindah hub↔rumah↔sekolah dll. berfungsi lewat `teleportToMap` dan lewat interaksi nyata.

### E3 · Sistem dialog dengan potret (placeholder potret)
Implementasi `71-dialogue-system.md`: UI kiri-kanan, sorotan pembicara, menu pilihan, data dialog + validasi skema, efek whitelist (ledger, aktivitas, transisi peta, flag), hook uji, dialog ibu/ayah/teman/penjual minimal.
**Gerbang:** uji sorotan berpindah, pilihan nonaktif, efek tereksekusi; tangkapan layar tiap tipe dialog (desktop + tablet).

### E4 · Style lock interior → CHECKPOINT B
Generate `furn_sheet_kamar_pemain` dan `portrait_sheet_player` sesuai `data/asset-briefs-expansion.json` (alur rule 60 lengkap + skala seragam per sheet). Render **kamar pemain nyata** di game (lantai/dinding prosedural + furnitur hasil generate) dan satu dialog dengan potret pemain di layar. Simpan tangkapan layar dan contact sheet di `docs/checkpoint-B/`.
**Gerbang = CHECKPOINT B (manusia):** berhenti; tampilkan gambar, ringkasan QA, cacat yang Anda lihat sendiri (jujur: gaya furnitur vs jangkar hub, skala terhadap karakter, potret vs sprite), lalu tanya: *"Setujui gaya interior dan potret ini atau beri catatan?"* Jangan generate massal sebelum jawaban.

### E5 · Generate sisa aset interior
Sesuai `generationOrder` (rumah → sekolah → potret lain → minimarket → kosmetik → SPBU → game center). Jangkar: aset yang disetujui. Tiap sheet lewat rule 60; ≤ 3 percobaan, lalu placeholder + log. Perbarui manifest, `ASSET-LOG.md`, kredit.
**Gerbang:** `tests/asset-check.html` memuat semua entri baru; laporan ready vs placeholder; contact sheet per kelompok.

### E6 · Rumah pemain + awal permainan
Layout `home` lengkap (5 ruangan wajib + furnitur), titik interaksi (kasur, meja belajar, lemari, celengan, meja makan, TV, bak mandi, ibu/ayah), alur awal hari 1 (bangun → dialog → ibu memberi uang saku → misi anggaran → keluar), New Journey memulai di kamar.
**Gerbang (browser):** New Journey → bangun di kasur Senin 06:00; semua titik interaksi bekerja dan memajukan waktu sesuai katalog; uang saku masuk ledger sekali; keluar rumah ke hub dan kembali; Continue memulihkan posisi di dalam rumah.

### E7 · Sekolah (kelas + kantin + perpustakaan)
Layout `school`, ruang kelas (meja tersusun rapi, papan tulis), ikut pelajaran (hari sekolah), kantin = satu-satunya tempat belanja makan/jajan, perpustakaan, jam buka sekolah/kantin, NPC teman dan penjual kantin.
**Gerbang:** skenario Senin pagi → sekolah → kelas (waktu maju ke 14:30) → kantin sebelum/sesudah jam buka (tutup/buka sesuai) → beli makan siang (Kas −Rp10.000, +20 menit); Sabtu: sekolah tutup.

### E8 · Bangunan lain dengan fitur masing-masing
Minimarket, toko kosmetik, SPBU, game center sesuai matriks 70 §7, masing-masing dengan NPC, transaksi di titik spesifik, jam buka, dan aktivitas berbiaya waktu. Ajakan teman ke game center via dialog (efek: transisi + waktu + biaya).
**Gerbang:** skenario per bangunan (masuk → transaksi → keluar) dengan invarian ledger dan jam diperiksa tiap langkah.

### E9 · Integrasi, QA E2E, hardening, laporan
Skenario penuh (70 §10) selama ≥ 3 hari permainan dengan dua gaya bermain (hemat/boros); audit visual (konsistensi gaya interior vs hub, skala furnitur vs karakter, tidak ada emoji/gradient di luar pengecualian); audit keamanan (`50-security.md` butir 11–15); perbarui README/ARCHITECTURE/SECURITY-NOTES dan buat `docs/FINAL-REPORT-V3.md` (fitur selesai-teruji/belum, aset ready/placeholder, hasil tes, batasan, rekomendasi).
**Gerbang:** semua tes hijau; laporan akhir.

## 2. Urutan alternatif
E1, E2, E3 independen terhadap aset dan dapat dijalankan terpisah (lihat prompt modular di `START-EXPANSION.md`). E4 membutuhkan E2 dan E3 (agar style lock dievaluasi dalam konteks nyata).

## 3. Templat `docs/PROGRESS-EXPANSION.md`
```
# PROGRESS EKSPANSI v3
Kapabilitas gambar: (alat, rasio, referensi?) | Tag pra-ekspansi: pre-expansion
- [ ] E0 Audit + patch + preflight
- [ ] E1 Sistem waktu
- [ ] E2 Kerangka peta interior
- [ ] E3 Dialog dengan potret
- [ ] E4 Style lock interior → [ ] CHECKPOINT B disetujui
- [ ] E5 Generate sisa aset
- [ ] E6 Rumah + awal permainan
- [ ] E7 Sekolah
- [ ] E8 Bangunan lain
- [ ] E9 Integrasi + QA + laporan
Log gerbang: | Tanggal | Gerbang | Hasil | Bukti | Commit |
Aset placeholder tersisa: ...  Temuan terbuka: ...
```
