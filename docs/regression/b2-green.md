# Laporan Pengujian Hijau: B2 (Meja Guru dan Papan Tulis Miring/Serong)

- **Status:** PASS (HIJAU)
- **Komponen:** `data/maps/school.layout.json`, `assets/furniture/school/furn_papan_tulis_v6.png`, `furn_meja_guru_v6.png`, `furn_kursi_guru_v6.png`, `tools/test_j5_green.py`
- **Tangkapan Layar:**
  - SEBELUM (RED): `docs/regression/b2_meja_guru_papan_tulis_red.png`
  - SESUDAH (GREEN): `docs/regression/b2_meja_guru_papan_tulis_green.png`
- **Akar Masalah:**
  Papan tulis lama digambar dengan sudut serong 3/4 dengan garis tepi miring tidak ortogonal, dan meja guru miring ke arah kanan sehingga tidak simetris frontal.
- **Perbaikan yang Diterapkan:**
  1. Dibuat papan tulis kelas baru `furn_papan_tulis_v6` (128x64) dengan proyeksi frontal datar simetris sempurna ($IoU = 1.00$).
  2. Dibuat meja guru baru `furn_meja_guru_v6` (96x64) dan kursi guru `furn_kursi_guru_v6` (32x48) dengan orientasi frontal 100% horizontal.
  3. Diletakkan simetris di bagian depan ruang kelas: papan tulis pada dinding belakang ($y=1.5$), meja guru di depannya ($y=3.5$), kursi guru di balik meja ($y=2.8$).
- **Hasil Verifikasi:**
  Pengujian runtime via CDP memvalidasi texture `furn_papan_tulis_v6` dan `furn_meja_guru_v6` berhasil dimuat dan dirender di koordinat kelas dengan simetri frontal penuh tanpa kemiringan serong.

