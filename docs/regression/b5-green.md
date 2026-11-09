# Laporan Pengujian Hijau: B5 (Identitas Aset Tertukar - Bak Mandi & Rak Piring)

- **Status:** PASS (HIJAU)
- **Komponen:** `data/maps/home.layout.json`, `assets/furniture/home/furn_bak_mandi_v6.png`, `furn_rak_piring_dinding_v6.png`, `furn_jendela_dapur_v6.png`, `tools/test_j5_green.py`
- **Tangkapan Layar:**
  - SEBELUM (RED): `docs/regression/b5_identitas_aset_tertukar_red.png`
  - SESUDAH (GREEN): `docs/regression/b5_identitas_aset_tertukar_green.png`
- **Akar Masalah:**
  Pada versi V5, berkas `furn_bak_mandi.png` secara visual menampilkan rak piring dapur, sedangkan `furn_rak_piring.png` menampilkan jendela berkusen kayu. Ini disebabkan oleh kesalahan pemotongan (slicing) sheet lama tanpa verifikasi visual identitas.
- **Perbaikan yang Diterapkan:**
  1. Dibuat aset baru `furn_bak_mandi_v6.png` (64x64) yang benar-benar merupakan bak mandi keramik kotak berisi air biru jernih dan gayung air tradisional.
  2. Dibuat aset baru `furn_rak_piring_dinding_v6.png` (64x48) yang berisi rak gantung dinding dengan piring dan mangkuk tersusun rapi.
  3. Dibuat aset terpisah `furn_jendela_dapur_v6.png` (64x48) untuk jendela dapur.
  4. Memperbarui `home.layout.json` sehingga `fur_bak_mandi` merujuk ke `furn_bak_mandi_v6` dan `fur_rak_piring` merujuk ke `furn_rak_piring_dinding_v6`.
- **Hasil Verifikasi:**
  Pengujian runtime via CDP membuktikan bak mandi di kamar mandi merender `furn_bak_mandi_v6` (bak air) dan rak piring di dapur merender `furn_rak_piring_dinding_v6` (rak piring nyata).

