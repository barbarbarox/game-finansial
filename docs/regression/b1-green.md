# Laporan Pengujian Hijau: B1 (Kursi dan Meja Sekolah/Perpustakaan Serong)

- **Status:** PASS (HIJAU)
- **Komponen:** `data/maps/school.layout.json`, `assets/furniture/school/furn_meja_siswa_kursi_a_v6.png`, `furn_meja_baca_set_a_v6.png`, `tools/test_j5_green.py`
- **Tangkapan Layar:**
  - SEBELUM (RED): `docs/regression/b1_kursi_meja_sekolah_red.png`
  - SESUDAH (GREEN): `docs/regression/b1_kursi_meja_sekolah_green.png`
- **Akar Masalah:**
  Pada versi sebelumnya, sprite meja dan kursi sekolah serta perpustakaan digambar dengan proyeksi isometrik serong (diagonal), dan kursi siswa tampak depan sehingga seolah membelakangi meja atau menghadap ke samping.
- **Perbaikan yang Diterapkan:**
  1. Dibuat set komposit `furn_meja_siswa_kursi_a_v6` dan `b_v6` dengan perspektif frontal konsisten: meja menghadap ke depan, kursi tampak dari belakang (`back`) mengarah ke meja.
  2. Dibuat set membaca perpustakaan `furn_meja_baca_set_a_v6` dan `b_v6` serta kursi baca `furn_kursi_baca_back_v6` dengan orientasi tampak belakang.
  3. Menggantikan slot furnitur di `school.layout.json` dengan set `_v6` baru, teratur dalam grid 2x2 rapi dengan walkway tengah menuju pintu masuk.
- **Hasil Verifikasi:**
  Pengujian runtime via CDP membuktikan meja siswa menggunakan `furn_meja_siswa_kursi_a_v6` dan `b_v6`, seluruh kursi menghadap depan (tampak belakang), tidak serong, dan simetri horizontal $IoU \ge 0.98$.

