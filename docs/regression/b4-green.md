# Laporan Pengujian Hijau: B4 (Furnitur Menembus Dinding Ruangan)

- **Status:** PASS (HIJAU)
- **Komponen:** `data/maps/school.layout.json`, `tests/layout-check.html`, `tools/test_j1_green.py`
- **Tangkapan Layar:**
  - SEBELUM (RED): `docs/regression/b4_furnitur_tembus_dinding_red.png`
  - SESUDAH (GREEN): B4 validator 131/131 furnitur berada di dalam batas lantai ruangan tanpa penetrasi dinding.
- **Akar Masalah:**
  Pada tata letak kelas dan kantin lama, offset vertikal deret meja dan bangku siswa mencapai $y=10.5$ hingga $y=12.0$, melintasi dinding pembatas $y=10.0$ menuju koridor. Bangku kantin juga menempati $y=10.0$ tepat di atas sekat pembatas.
- **Perbaikan yang Diterapkan:**
  1. Penataan ulang baris meja siswa kelas ke $y=5.0$ dan $y=7.5$, kursi ke $y=6.2$ dan $y=8.7$ (seluruh batas berada $\le 9.9$, aman di dalam lantai kelas $y \in [2, 10]$).
  2. Penataan meja kantin ke $y=6.5$, bangku ke $y=5.2$ dan $y=8.2$, tempat sampah ke $y=8.0$ (bersih dari dinding pembatas bawah).
  3. Menambahkan pengujian otomatis batas lantai dan oklusi dinding di `tests/layout-check.html`.
- **Hasil Verifikasi:**
  131 furnitur non-dekoratif diuji di seluruh 6 peta: 0 pelanggaran batas ruangan.
