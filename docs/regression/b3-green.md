# Laporan Pengujian Hijau: B3 (Meja dan Bangku Kantin Serong)

- **Status:** PASS (HIJAU)
- **Komponen:** `data/maps/school.layout.json`, `assets/furniture/school/furn_meja_kantin_set_a_v6.png`, `furn_meja_kantin_set_b_v6.png`, `furn_bangku_dinding_v6.png`, `tools/test_j5_green.py`
- **Tangkapan Layar:**
  - SEBELUM (RED): `docs/regression/b3_meja_bangku_kantin_red.png`
  - SESUDAH (GREEN): `docs/regression/b3_meja_bangku_kantin_green.png`
- **Akar Masalah:**
  Meja panjang kantin dan bangku-bangkunya sebelumnya digambar dari sudut miring isometrik, menyebabkan proporsi meja menjadi serong dan bangku terpotong di tepi.
- **Perbaikan yang Diterapkan:**
  1. Dibuat set meja kantin komposit baru `furn_meja_kantin_set_a_v6` dan `b_v6` (128x80) dengan meja frontal lurus, bangku atas tampak depan dan bangku bawah tampak belakang.
  2. Dibuat bangku dinding kantin `furn_bangku_dinding_v6` (96x32) untuk area istirahat pinggir.
  3. Memperbarui `school.layout.json` menggunakan set meja kantin baru pada $y=6.2$, $w=4$, $h=2.5$.
- **Hasil Verifikasi:**
  Pengujian runtime via CDP memvalidasi `slot_sch_meja_kantin_1` dan `2` berhasil merender `furn_meja_kantin_set_a_v6` dan `b_v6` dengan proporsi frontal penuh tanpa kemiringan serong.

