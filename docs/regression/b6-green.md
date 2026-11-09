# Laporan Pengujian Hijau: B6 (Wastafel dan Toilet Serong/Tidak Konsisten)

- **Status:** PASS (HIJAU)
- **Komponen:** `data/maps/home.layout.json`, `assets/furniture/home/furn_toilet_v6.png`, `furn_wastafel_cermin_v6.png`, `furn_rak_handuk_v6.png`, `furn_ember_v6.png`, `tools/test_j5_green.py`
- **Tangkapan Layar:**
  - SEBELUM (RED): `docs/regression/b6_wastafel_toilet_red.png`
  - SESUDAH (GREEN): `docs/regression/b6_wastafel_toilet_green.png`
- **Akar Masalah:**
  Wastafel dan toilet di kamar mandi rumah digambar dengan perspektif serong miring ke kanan, bertentangan dengan gaya frontal dinding kamar mandi.
- **Perbaikan yang Diterapkan:**
  1. Dibuat `furn_toilet_v6.png` (32x48) dengan perspektif frontal lurus menghadap pemain (tutup toilet, tangki, dan mangkuk kloset simetris).
  2. Dibuat `furn_wastafel_cermin_v6.png` (64x80) dengan cermin dinding persegi panjang dan wastafel keramik frontal simetris.
  3. Dibuat `furn_rak_handuk_v6.png` (32x64) dan `furn_ember_v6.png` (32x32) untuk melengkapi perlengkapan kamar mandi.
  4. Memperbarui `home.layout.json` menggunakan aset kamar mandi `_v6` baru.
- **Hasil Verifikasi:**
  Pengujian runtime via CDP memvalidasi `fur_toilet` dan `fur_wastafel_cermin` di kamar mandi rumah merender aset `_v6` dengan orientasi frontal sempurna ($IoU \ge 0.99$).
