# Laporan Pengujian Hijau: B17 (Simulasi Gameplay Multi-Hari E2E & Nol Regresi)

- **Status:** PASS (HIJAU)
- **Komponen:** `tools/test_j7_e2e_regression.py`, `tests/self-test.html`, `tests/time-test.html`, `tests/dialogue-test.html`, `tests/map-check.html`, `tests/layout-check.html`, `tests/hud-sync.html`, `src/domain/inventory.js`, `src/ui/shopPanel.js`
- **Tangkapan Layar:**
  - SEBELUM (RED): `docs/regression/b17_e2e_multiday_red.png`
  - SESUDAH (GREEN): `docs/regression/b17_e2e_multiday_green.png`
- **Akar Masalah:**
  Sebelum integrasi Gate J7, pengujian multi-hari komprehensif dari Hari 1 hingga Hari 3 belum divalidasi secara otomatis. Risiko regresi antar sistem (peta, keterjangkauan jalur, siklus tidur kasur, pengisian bensin di SPBU, transaksi kantin, pemulihan energi, serta invarian pembukuan berpasangan) perlu dipastikan tidak mengalami konflik atau penurunan fungsionalitas setelah penambahan fitur V6.
- **Perbaikan & Validasi yang Diterapkan:**
  1. **Node Property Invariant Test (`tests/inventory_property_test.mjs`):**
     - 500 operasi acak (Add, Use, Move, Discard, Full Rejection) diuji terhadap invarian inventaris.
     - Hasil: 500/500 operasi LULUS (100% PASS), kapasitas tas dan hotbar terjaga konsisten tanpa kebocoran memori atau stack overflow.
  2. **Eksekusi 6 HTML Test Suites:**
     - `tests/self-test.html`: SEMUA 6 INVARIAN AKUNTANSI LULUS (100% PASS).
     - `tests/time-test.html`: LULUS SEMUA (12/12) — Sistem Waktu & Aktivitas Rule 72 Terverifikasi Penuh.
     - `tests/dialogue-test.html`: LULUS SEMUA (21/21) — Sistem Dialog & Potret Rule 71 Terverifikasi Penuh.
     - `tests/map-check.html`: LULUS SEMUA (36/36) — Seluruh 7 Peta Lolos Uji Keterjangkauan BFS Jalur dan Timbal Balik setelah penyesuaian meja guru ($y=3.0, h=1.2$) dan posisi Budi ($x=7.5, y=6$).
     - `tests/layout-check.html`: LULUS SEMUA TATA LETAK (77/77) — Seluruh 7 peta memenuhi spesifikasi Rule 73 dan Rule 85.
     - `tests/hud-sync.html`: SEMUA PENGUJIAN HUD SYNC LULUS — Sinkronisasi event bahan bakar, kas, energi, dan jam terverifikasi.
  3. **Simulasi Gameplay Multi-Hari E2E (Hari 1 -> Hari 3):**
     - **Hari 1:** Karakter baru dibuat, tutorial T01–T20 diselesaikan, uang saku Ibu diterima (Rp1.000.000), pelajaran sekolah diikuti (energi turun 20%), jajan makan siang di kantin sekolah dengan katalog penjual Bu Sri, pulang ke rumah dan tidur di kasur (`int_kasur`).
     - **Hari 2:** Bangun pagi jam 06:00 dengan energi pulih 100%, mengendarai sepeda motor ke Hub Kota, singgah di SPBU untuk isi bensin (50% -> 70%), penurunan energi ke < 50% memicu toast peringatan persis `"Energi kamu di bawah 50%, silakan makan untuk menambahnya."`, pulang ke rumah dan tidur di kasur.
     - **Hari 3:** Bangun pagi jam 06:00 dengan energi 100%, verifikasi saldo kas akhir (Rp980.000), verifikasi integritas pembukuan berpasangan ($\sum \text{Debit} = \sum \text{Kredit} = \text{Rp}1.020.000$).
- **Hasil Verifikasi:**
  - `tools/test_j7_e2e_regression.py` menyelesaikan seluruh 3 tahapan pengujian tanpa error (`Exit code: 0`).
  - Nol regresi (0 failures) di seluruh suite pengujian inti.
  - Tangkapan layar hijau tersimpan di `docs/regression/b17_e2e_multiday_green.png`.

