# Laporan Pengujian Hijau: B16 (Sistem Tutorial & Cerita Wajib Terpemandu)

- **Status:** PASS (HIJAU)
- **Komponen:** `src/domain/tutorial.js`, `src/game/effects/guidanceArrow.js`, `src/ui/tutorialBanner.js`, `src/domain/events.js`, `data/tutorial.phase1.json`, `tools/test_j6_green.py`
- **Tangkapan Layar:**
  - SEBELUM (RED): `docs/regression/b16_tutorial_red.png`
  - SESUDAH (GREEN): `docs/regression/b16_tutorial_green.png`
- **Akar Masalah:**
  Pada versi sebelumnya, tidak ada alur cerita dan tutorial terstruktur untuk pemain baru. Pemain langsung ditempatkan di kamar tanpa indikator arah, instruksi tujuan, maupun pembatas cerita awal (misal uang saku dari Ibu, sarapan pagi, susun anggaran, tabungan awal celengan, dan eksplorasi bertahap seluruh fasilitas kota).
- **Perbaikan yang Diterapkan:**
  1. **Tutorial Domain (`src/domain/tutorial.js`):** Mengelola siklus 20 langkah tutorial terarah (T01–T20: Gerak, Temui Ibu, Ambil Uang Saku, Sarapan, Anggaran, Celengan, Hub Kota, Masuk Sekolah, Kelas Sesi 1, Jajan Kantin, Makan Siang, Kelas Sesi 2, Pinjam Buku Perpus, Minimarket, Beli Skincare, SPBU Bensin, Game Center, Isi Energi, Pulang & Tidur).
  2. **Indikator Arah Dunia & Tepi Layar (`src/game/effects/guidanceArrow.js`):** Menampilkan panah mengambang animasi bobbing di atas target di dunia, serta indikator panah tepi layar (screen-edge pointer) saat target berada di luar viewport kamera lengkap dengan jarak meter.
  3. **Banner Objektif & Highlight HUD (`src/ui/tutorialBanner.js`):** Menampilkan kartu tujuan di bagian atas layar (`LANGKAH n/20`, teks tujuan, instruksi detail, 20 titik progres, tombol perkecil, dan tombol lewati darurat setelah 180 detik anti-macet). Tombol HUD terkait berdenyut dengan animasi emas (`.hud-tutorial-pulse`).
  4. **Soft-Lock Bangunan & Jeda Waktu:** Akses pintu keluar rumah dan gedung lain dikunci secara halus hingga langkah terkait tercapai. Jam real-time dijeda selama tutorial aktif agar toko/sekolah tidak tutup sebelum pemain menyelesaikan misi awal.
  5. **Non-Repeatability & Persistensi:** Progres tutorial tersimpan otomatis di `localStorage`. Permainan baru menjalankan tutorial sekali, setelah tamat status `tutorial.completed = true` dan `active = false`, banner dan panah dilepas otomatis.
- **Hasil Verifikasi (`tools/test_j6_green.py`):**
  - T01 (Gerakan WASD $\ge 3$ tile) berhasil diselesaikan dan maju ke T02.
  - T02 menampilkan panah dunia dan panah tepi layar mengarah ke Ibu di dapur.
  - Soft-lock terbukti mencegah pemain keluar rumah sebelum bertemu Ibu.
  - T03 dialog dengan Ibu memberikan uang saku Rp1.000.000 ke kas.
  - T04 sarapan di meja makan menambah energi dan memicu timeskip.
  - T05 tombol Anggaran pada HUD berdenyut (`.hud-tutorial-pulse`), modal anggaran terbuka dan tersimpan.
  - T06 Celengan Ayam menerima setoran tabungan awal Rp100.000.
  - Progres tersimpan di `localStorage` dan dapat dilanjutkan tanpa kehilangan status.
  - Seluruh langkah T07–T20 selesai secara berurutan, modal kelulusan tutorial tampil (`.tutorial-finish-modal`), banner objektif dihilangkan, jam permainan kembali berjalan normal.
