# PERSPECTIVE-AUDIT.md — Audit Frontalitas, Perspektif, dan Kualitas Aset (Rule 85)

- **Total Aset Diperiksa:** 207
- **Jumlah Aset Lolos (PASS):** 80
- **Jumlah Pelanggar Perspektif (OFFENDER):** 127

## 1. Daftar Pelanggar Perspektif & Kualitas (Antrean Regenerasi J4)

| ID Aset | Dimensi | Facing | IoU Frontalitas | Alfa Parsial | Status | Catatan Pelanggaran |
|---|---|---|---|---|---|---|
| `furn_arcade_a` | 64x96 | front | 0.751 | 8.1% | **OFFENDER** | Frontal IoU too low (0.75 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (8.1% > 5%) -> BLURRY / VECTOR |
| `furn_arcade_a_v4` | 64x96 | front | 0.751 | 8.1% | **OFFENDER** | Frontal IoU too low (0.75 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (8.1% > 5%) -> BLURRY / VECTOR |
| `furn_arcade_b` | 64x96 | front | 0.725 | 18.1% | **OFFENDER** | Frontal IoU too low (0.73 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (18.1% > 5%) -> BLURRY / VECTOR |
| `furn_arcade_b_v4` | 64x96 | front | 0.725 | 18.1% | **OFFENDER** | Frontal IoU too low (0.73 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (18.1% > 5%) -> BLURRY / VECTOR |
| `furn_counter_kafe` | 96x64 | front | 0.636 | 15.1% | **OFFENDER** | Frontal IoU too low (0.64 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (15.1% > 5%) -> BLURRY / VECTOR |
| `furn_counter_kafe_v4` | 96x64 | front | 0.636 | 15.1% | **OFFENDER** | Frontal IoU too low (0.64 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (15.1% > 5%) -> BLURRY / VECTOR |
| `furn_kursi_kafe` | 32x48 | front | 0.984 | 27.4% | **OFFENDER** | Partial alpha present (27.3% > 5%) -> BLURRY / VECTOR |
| `furn_kursi_kafe_v4` | 32x48 | front | 0.984 | 27.4% | **OFFENDER** | Partial alpha present (27.3% > 5%) -> BLURRY / VECTOR |
| `furn_meja_kafe` | 64x64 | front | 0.989 | 18.6% | **OFFENDER** | Partial alpha present (18.7% > 5%) -> BLURRY / VECTOR |
| `furn_meja_kafe_v4` | 64x64 | front | 0.989 | 18.6% | **OFFENDER** | Partial alpha present (18.7% > 5%) -> BLURRY / VECTOR |
| `furn_sofa_nonton` | 96x64 | front | 0.581 | 0.0% | **OFFENDER** | Frontal IoU too low (0.58 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_sofa_nonton_v4` | 96x64 | front | 0.581 | 0.0% | **OFFENDER** | Frontal IoU too low (0.58 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_tanaman_pot` | 32x48 | front | 0.585 | 0.0% | **OFFENDER** | Frontal IoU too low (0.59 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_tanaman_pot_v4` | 32x48 | front | 0.585 | 0.0% | **OFFENDER** | Frontal IoU too low (0.59 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_tv_besar` | 96x64 | front | 0.693 | 9.9% | **OFFENDER** | Frontal IoU too low (0.69 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (9.9% > 5%) -> BLURRY / VECTOR |
| `furn_tv_besar_v4` | 96x64 | front | 0.693 | 9.9% | **OFFENDER** | Frontal IoU too low (0.69 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (9.9% > 5%) -> BLURRY / VECTOR |
| `furn_bak_mandi` | 64x64 | front | 0.896 | 12.4% | **OFFENDER** | Partial alpha present (12.4% > 5%) -> BLURRY / VECTOR |
| `furn_bak_mandi_v4` | 64x64 | front | 0.896 | 12.4% | **OFFENDER** | Partial alpha present (12.4% > 5%) -> BLURRY / VECTOR |
| `furn_bingkai_kosong` | 32x32 | front | 0.998 | 14.6% | **OFFENDER** | Partial alpha present (14.6% > 5%) -> BLURRY / VECTOR |
| `furn_bingkai_kosong_v4` | 32x32 | front | 0.998 | 14.6% | **OFFENDER** | Partial alpha present (14.6% > 5%) -> BLURRY / VECTOR |
| `furn_jam_dinding` | 32x32 | front | 1.0 | 14.9% | **OFFENDER** | Partial alpha present (14.9% > 5%) -> BLURRY / VECTOR |
| `furn_jam_dinding_v4` | 32x32 | front | 1.0 | 14.9% | **OFFENDER** | Partial alpha present (14.9% > 5%) -> BLURRY / VECTOR |
| `furn_jendela` | 64x64 | front | 0.877 | 9.8% | **OFFENDER** | Partial alpha present (9.8% > 5%) -> BLURRY / VECTOR |
| `furn_jendela_v4` | 64x64 | front | 0.877 | 9.8% | **OFFENDER** | Partial alpha present (9.8% > 5%) -> BLURRY / VECTOR |
| `furn_karpet_tamu` | 128x96 | front | 0.735 | 0.0% | **OFFENDER** | Frontal IoU too low (0.74 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_kompor_counter` | 96x64 | front | 0.713 | 0.0% | **OFFENDER** | Frontal IoU too low (0.71 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_kursi_makan` | 32x48 | front | 0.53 | 36.9% | **OFFENDER** | Frontal IoU too low (0.53 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (36.9% > 5%) -> BLURRY / VECTOR |
| `furn_kursi_makan_depan` | 32x48 | front | 0.53 | 36.9% | **OFFENDER** | Frontal IoU too low (0.53 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (36.9% > 5%) -> BLURRY / VECTOR |
| `furn_kursi_makan_depan_v4` | 32x48 | front | 0.53 | 36.9% | **OFFENDER** | Frontal IoU too low (0.53 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (36.9% > 5%) -> BLURRY / VECTOR |
| `furn_kursi_makan_kanan` | 32x48 | front | 0.961 | 39.2% | **OFFENDER** | Partial alpha present (39.2% > 5%) -> BLURRY / VECTOR |
| `furn_kursi_makan_kanan_v4` | 32x48 | front | 0.961 | 39.2% | **OFFENDER** | Partial alpha present (39.2% > 5%) -> BLURRY / VECTOR |
| `furn_kursi_makan_kiri` | 32x48 | front | 0.58 | 37.7% | **OFFENDER** | Frontal IoU too low (0.58 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (37.7% > 5%) -> BLURRY / VECTOR |
| `furn_kursi_makan_kiri_v4` | 32x48 | front | 0.58 | 37.7% | **OFFENDER** | Frontal IoU too low (0.58 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (37.7% > 5%) -> BLURRY / VECTOR |
| `furn_kursi_makan_v4` | 32x48 | front | 0.53 | 36.9% | **OFFENDER** | Frontal IoU too low (0.53 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (36.9% > 5%) -> BLURRY / VECTOR |
| `furn_rak_handuk` | 32x64 | front | 0.52 | 0.0% | **OFFENDER** | Frontal IoU too low (0.52 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_rak_piring` | 64x80 | front | 0.73 | 9.7% | **OFFENDER** | Frontal IoU too low (0.73 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (9.7% > 5%) -> BLURRY / VECTOR |
| `furn_rak_piring_v4` | 64x80 | front | 0.73 | 9.7% | **OFFENDER** | Frontal IoU too low (0.73 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (9.7% > 5%) -> BLURRY / VECTOR |
| `furn_toilet` | 32x48 | front | 0.482 | 0.0% | **OFFENDER** | Frontal IoU too low (0.48 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_wastafel_cermin` | 64x80 | front | 0.515 | 17.3% | **OFFENDER** | Frontal IoU too low (0.51 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (17.3% > 5%) -> BLURRY / VECTOR |
| `furn_wastafel_cermin_v4` | 64x80 | front | 0.515 | 17.3% | **OFFENDER** | Frontal IoU too low (0.51 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (17.3% > 5%) -> BLURRY / VECTOR |
| `furn_wastafel_dapur` | 96x64 | front | 0.648 | 0.0% | **OFFENDER** | Frontal IoU too low (0.65 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_kursi_belajar` | 32x48 | front | 0.687 | 0.0% | **OFFENDER** | Frontal IoU too low (0.69 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_etalase_kaca` | 96x64 | front | 0.735 | 8.6% | **OFFENDER** | Frontal IoU too low (0.73 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (8.6% > 5%) -> BLURRY / VECTOR |
| `furn_etalase_kaca_v4` | 96x64 | front | 0.735 | 8.6% | **OFFENDER** | Frontal IoU too low (0.73 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (8.6% > 5%) -> BLURRY / VECTOR |
| `furn_kasir_kecil` | 64x64 | front | 0.707 | 17.8% | **OFFENDER** | Frontal IoU too low (0.71 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (17.9% > 5%) -> BLURRY / VECTOR |
| `furn_kasir_kecil_v4` | 64x64 | front | 0.707 | 17.8% | **OFFENDER** | Frontal IoU too low (0.71 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (17.9% > 5%) -> BLURRY / VECTOR |
| `furn_kursi_tunggu` | 32x48 | front | 0.792 | 17.1% | **OFFENDER** | Frontal IoU too low (0.79 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (17.1% > 5%) -> BLURRY / VECTOR |
| `furn_kursi_tunggu_v4` | 32x48 | front | 0.792 | 17.1% | **OFFENDER** | Frontal IoU too low (0.79 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (17.1% > 5%) -> BLURRY / VECTOR |
| `furn_meja_cermin` | 64x64 | front | 0.59 | 26.2% | **OFFENDER** | Frontal IoU too low (0.59 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (26.2% > 5%) -> BLURRY / VECTOR |
| `furn_meja_cermin_v4` | 64x64 | front | 0.59 | 26.2% | **OFFENDER** | Frontal IoU too low (0.59 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (26.2% > 5%) -> BLURRY / VECTOR |
| `furn_rak_dinding_kosmetik` | 64x80 | front | 0.623 | 11.2% | **OFFENDER** | Frontal IoU too low (0.62 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (11.2% > 5%) -> BLURRY / VECTOR |
| `furn_rak_dinding_kosmetik_v4` | 64x80 | front | 0.623 | 11.2% | **OFFENDER** | Frontal IoU too low (0.62 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (11.2% > 5%) -> BLURRY / VECTOR |
| `furn_sofa_tunggu` | 64x64 | front | 0.71 | 0.0% | **OFFENDER** | Frontal IoU too low (0.71 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_sofa_tunggu_v4` | 64x64 | front | 0.71 | 0.0% | **OFFENDER** | Frontal IoU too low (0.71 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_tanaman_pot` | 32x48 | front | 0.585 | 0.0% | **OFFENDER** | Frontal IoU too low (0.59 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_tanaman_pot_v4` | 32x48 | front | 0.585 | 0.0% | **OFFENDER** | Frontal IoU too low (0.59 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_etalase_makanan_siap_saji` | 96x64 | front | 0.68 | 0.0% | **OFFENDER** | Frontal IoU too low (0.68 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_etalase_makanan_siap_saji_v4` | 96x64 | front | 0.68 | 0.0% | **OFFENDER** | Frontal IoU too low (0.68 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_kasir_counter` | 96x64 | front | 0.687 | 13.0% | **OFFENDER** | Frontal IoU too low (0.69 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (13.0% > 5%) -> BLURRY / VECTOR |
| `furn_kasir_counter_v4` | 96x64 | front | 0.687 | 13.0% | **OFFENDER** | Frontal IoU too low (0.69 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (13.0% > 5%) -> BLURRY / VECTOR |
| `furn_keranjang_belanja` | 32x32 | front | 0.895 | 15.5% | **OFFENDER** | Partial alpha present (15.5% > 5%) -> BLURRY / VECTOR |
| `furn_keranjang_belanja_v4` | 32x32 | front | 0.895 | 15.5% | **OFFENDER** | Partial alpha present (15.5% > 5%) -> BLURRY / VECTOR |
| `furn_kulkas_minuman_besar` | 96x96 | front | 0.786 | 5.9% | **OFFENDER** | Frontal IoU too low (0.79 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (5.9% > 5%) -> BLURRY / VECTOR |
| `furn_kulkas_minuman_besar_v4` | 96x96 | front | 0.786 | 5.9% | **OFFENDER** | Frontal IoU too low (0.79 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (5.9% > 5%) -> BLURRY / VECTOR |
| `furn_mesin_fotokopi` | 64x64 | front | 0.879 | 13.7% | **OFFENDER** | Partial alpha present (13.7% > 5%) -> BLURRY / VECTOR |
| `furn_mesin_fotokopi_v4` | 64x64 | front | 0.879 | 13.7% | **OFFENDER** | Partial alpha present (13.7% > 5%) -> BLURRY / VECTOR |
| `furn_rak_alat_tulis` | 64x80 | front | 0.775 | 14.1% | **OFFENDER** | Frontal IoU too low (0.78 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (14.1% > 5%) -> BLURRY / VECTOR |
| `furn_rak_alat_tulis_v4` | 64x80 | front | 0.775 | 14.1% | **OFFENDER** | Frontal IoU too low (0.78 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (14.1% > 5%) -> BLURRY / VECTOR |
| `furn_rak_dinding_snack` | 64x96 | front | 0.676 | 0.0% | **OFFENDER** | Frontal IoU too low (0.68 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_rak_dinding_snack_v4` | 64x96 | front | 0.676 | 0.0% | **OFFENDER** | Frontal IoU too low (0.68 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_rak_gondola` | 96x64 | front | 0.695 | 11.9% | **OFFENDER** | Frontal IoU too low (0.69 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (11.9% > 5%) -> BLURRY / VECTOR |
| `furn_rak_gondola_v4` | 96x64 | front | 0.695 | 11.9% | **OFFENDER** | Frontal IoU too low (0.69 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (11.9% > 5%) -> BLURRY / VECTOR |
| `furn_rak_mie_instan` | 64x80 | front | 0.752 | 0.0% | **OFFENDER** | Frontal IoU too low (0.75 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_rak_mie_instan_v4` | 64x80 | front | 0.752 | 0.0% | **OFFENDER** | Frontal IoU too low (0.75 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_rak_roti` | 64x64 | front | 0.729 | 0.0% | **OFFENDER** | Frontal IoU too low (0.73 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_rak_roti_v4` | 64x64 | front | 0.729 | 0.0% | **OFFENDER** | Frontal IoU too low (0.73 < 0.80) -> DIAGONAL / OBLIQUE |
| `prop_motor_parkir` | 48x32 | front | 0.588 | 46.3% | **OFFENDER** | Frontal IoU too low (0.59 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (46.3% > 5%) -> BLURRY / VECTOR |
| `furn_bangku_kantin` | 96x32 | front | 0.533 | 31.5% | **OFFENDER** | Frontal IoU too low (0.53 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (31.5% > 5%) -> BLURRY / VECTOR |
| `furn_bangku_kantin_v4` | 96x32 | front | 0.533 | 31.5% | **OFFENDER** | Frontal IoU too low (0.53 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (31.5% > 5%) -> BLURRY / VECTOR |
| `furn_bangku_tunggu` | 64x32 | front | 0.533 | 32.8% | **OFFENDER** | Frontal IoU too low (0.53 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (32.8% > 5%) -> BLURRY / VECTOR |
| `furn_bangku_tunggu_v4` | 64x32 | front | 0.533 | 32.8% | **OFFENDER** | Frontal IoU too low (0.53 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (32.8% > 5%) -> BLURRY / VECTOR |
| `furn_counter_kantin` | 128x64 | front | 0.678 | 24.0% | **OFFENDER** | Frontal IoU too low (0.68 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (24.0% > 5%) -> BLURRY / VECTOR |
| `furn_counter_kantin_v4` | 128x64 | front | 0.678 | 24.0% | **OFFENDER** | Frontal IoU too low (0.68 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (24.0% > 5%) -> BLURRY / VECTOR |
| `furn_dispenser_galon` | 32x64 | front | 0.989 | 10.7% | **OFFENDER** | Partial alpha present (10.7% > 5%) -> BLURRY / VECTOR |
| `furn_dispenser_galon_v4` | 32x64 | front | 0.989 | 10.7% | **OFFENDER** | Partial alpha present (10.7% > 5%) -> BLURRY / VECTOR |
| `furn_kursi_baca` | 32x48 | front | 0.577 | 0.0% | **OFFENDER** | Frontal IoU too low (0.58 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_kursi_baca_v4` | 32x48 | front | 0.577 | 0.0% | **OFFENDER** | Frontal IoU too low (0.58 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_kursi_guru` | 32x48 | front | 0.507 | 0.0% | **OFFENDER** | Frontal IoU too low (0.51 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_kursi_guru_v4` | 32x48 | front | 0.507 | 0.0% | **OFFENDER** | Frontal IoU too low (0.51 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_kursi_siswa` | 32x48 | front | 0.464 | 0.0% | **OFFENDER** | Frontal IoU too low (0.46 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_kursi_siswa_v4` | 32x48 | front | 0.464 | 0.0% | **OFFENDER** | Frontal IoU too low (0.46 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_lemari_kelas` | 64x96 | front | 0.802 | 5.6% | **OFFENDER** | Partial alpha present (5.6% > 5%) -> BLURRY / VECTOR |
| `furn_lemari_kelas_v4` | 64x96 | front | 0.802 | 5.6% | **OFFENDER** | Partial alpha present (5.6% > 5%) -> BLURRY / VECTOR |
| `furn_meja_baca` | 96x64 | front | 0.503 | 19.9% | **OFFENDER** | Frontal IoU too low (0.50 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (19.9% > 5%) -> BLURRY / VECTOR |
| `furn_meja_baca_v4` | 96x64 | front | 0.503 | 19.9% | **OFFENDER** | Frontal IoU too low (0.50 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (19.9% > 5%) -> BLURRY / VECTOR |
| `furn_meja_guru` | 96x64 | front | 0.7 | 16.5% | **OFFENDER** | Frontal IoU too low (0.70 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (16.5% > 5%) -> BLURRY / VECTOR |
| `furn_meja_guru_v4` | 96x64 | front | 0.7 | 16.5% | **OFFENDER** | Frontal IoU too low (0.70 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (16.5% > 5%) -> BLURRY / VECTOR |
| `furn_meja_kantin` | 96x64 | front | 0.54 | 25.5% | **OFFENDER** | Frontal IoU too low (0.54 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (25.5% > 5%) -> BLURRY / VECTOR |
| `furn_meja_kantin_v4` | 96x64 | front | 0.54 | 25.5% | **OFFENDER** | Frontal IoU too low (0.54 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (25.5% > 5%) -> BLURRY / VECTOR |
| `furn_meja_siswa` | 64x48 | front | 0.661 | 0.0% | **OFFENDER** | Frontal IoU too low (0.66 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_meja_siswa_kursi` | 64x64 | front | 0.698 | 22.6% | **OFFENDER** | Frontal IoU too low (0.70 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (22.6% > 5%) -> BLURRY / VECTOR |
| `furn_meja_siswa_kursi_v4` | 64x64 | front | 0.698 | 22.6% | **OFFENDER** | Frontal IoU too low (0.70 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (22.6% > 5%) -> BLURRY / VECTOR |
| `furn_meja_siswa_v4` | 64x48 | front | 0.661 | 0.0% | **OFFENDER** | Frontal IoU too low (0.66 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_papan_pengumuman` | 96x64 | front | 0.605 | 8.7% | **OFFENDER** | Frontal IoU too low (0.60 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (8.7% > 5%) -> BLURRY / VECTOR |
| `furn_papan_pengumuman_v4` | 96x64 | front | 0.605 | 8.7% | **OFFENDER** | Frontal IoU too low (0.60 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (8.7% > 5%) -> BLURRY / VECTOR |
| `furn_papan_tulis` | 128x64 | front | 0.544 | 10.5% | **OFFENDER** | Frontal IoU too low (0.54 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (10.5% > 5%) -> BLURRY / VECTOR |
| `furn_papan_tulis_v4` | 128x64 | front | 0.544 | 10.5% | **OFFENDER** | Frontal IoU too low (0.54 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (10.5% > 5%) -> BLURRY / VECTOR |
| `furn_poster_kosong` | 32x48 | front | 0.592 | 12.0% | **OFFENDER** | Frontal IoU too low (0.59 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (12.0% > 5%) -> BLURRY / VECTOR |
| `furn_poster_kosong_v4` | 32x48 | front | 0.592 | 12.0% | **OFFENDER** | Frontal IoU too low (0.59 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (12.0% > 5%) -> BLURRY / VECTOR |
| `furn_rak_buku_perpus` | 96x96 | front | 0.783 | 5.0% | **OFFENDER** | Frontal IoU too low (0.78 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_rak_buku_perpus_v4` | 96x96 | front | 0.783 | 5.0% | **OFFENDER** | Frontal IoU too low (0.78 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_rak_snack` | 64x80 | front | 0.765 | 20.1% | **OFFENDER** | Frontal IoU too low (0.77 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (20.1% > 5%) -> BLURRY / VECTOR |
| `furn_rak_snack_v4` | 64x80 | front | 0.765 | 20.1% | **OFFENDER** | Frontal IoU too low (0.77 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (20.1% > 5%) -> BLURRY / VECTOR |
| `furn_tempat_sampah_kelas` | 32x32 | front | 0.911 | 18.9% | **OFFENDER** | Partial alpha present (19.0% > 5%) -> BLURRY / VECTOR |
| `furn_tempat_sampah_kelas_v4` | 32x32 | front | 0.911 | 18.9% | **OFFENDER** | Partial alpha present (19.0% > 5%) -> BLURRY / VECTOR |
| `furn_vas_tanaman` | 32x48 | front | 0.835 | 33.3% | **OFFENDER** | Partial alpha present (33.3% > 5%) -> BLURRY / VECTOR |
| `furn_vas_tanaman_v4` | 32x48 | front | 0.835 | 33.3% | **OFFENDER** | Partial alpha present (33.3% > 5%) -> BLURRY / VECTOR |
| `furn_bangku_spbu` | 64x32 | front | 0.734 | 18.9% | **OFFENDER** | Frontal IoU too low (0.73 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (18.9% > 5%) -> BLURRY / VECTOR |
| `furn_bangku_spbu_v4` | 64x32 | front | 0.734 | 18.9% | **OFFENDER** | Frontal IoU too low (0.73 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (18.9% > 5%) -> BLURRY / VECTOR |
| `furn_dispenser_bbm` | 64x80 | front | 0.773 | 16.9% | **OFFENDER** | Frontal IoU too low (0.77 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (16.9% > 5%) -> BLURRY / VECTOR |
| `furn_dispenser_bbm_v4` | 64x80 | front | 0.773 | 16.9% | **OFFENDER** | Frontal IoU too low (0.77 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (16.9% > 5%) -> BLURRY / VECTOR |
| `furn_kiosk_spbu` | 96x64 | front | 0.993 | 11.0% | **OFFENDER** | Partial alpha present (11.0% > 5%) -> BLURRY / VECTOR |
| `furn_kiosk_spbu_v4` | 96x64 | front | 0.993 | 11.0% | **OFFENDER** | Partial alpha present (11.0% > 5%) -> BLURRY / VECTOR |
| `furn_rak_oli` | 64x64 | front | 0.732 | 16.9% | **OFFENDER** | Frontal IoU too low (0.73 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (16.9% > 5%) -> BLURRY / VECTOR |
| `furn_rak_oli_v4` | 64x64 | front | 0.732 | 16.9% | **OFFENDER** | Frontal IoU too low (0.73 < 0.80) -> DIAGONAL / OBLIQUE<br>Partial alpha present (16.9% > 5%) -> BLURRY / VECTOR |
| `furn_tong_pemadam` | 32x40 | front | 0.56 | 0.0% | **OFFENDER** | Frontal IoU too low (0.56 < 0.80) -> DIAGONAL / OBLIQUE |
| `furn_tong_pemadam_v4` | 32x40 | front | 0.56 | 0.0% | **OFFENDER** | Frontal IoU too low (0.56 < 0.80) -> DIAGONAL / OBLIQUE |

## 2. Seluruh Hasil Audit Aset Furnitur

| ID Aset | Dimensi | Facing | IoU Frontalitas | Alfa Parsial | Status |
|---|---|---|---|---|---|
| `furn_arcade_a` | 64x96 | front | 0.751 | 8.1% | OFFENDER |
| `furn_arcade_a_v4` | 64x96 | front | 0.751 | 8.1% | OFFENDER |
| `furn_arcade_b` | 64x96 | front | 0.725 | 18.1% | OFFENDER |
| `furn_arcade_b_v4` | 64x96 | front | 0.725 | 18.1% | OFFENDER |
| `furn_counter_kafe` | 96x64 | front | 0.636 | 15.1% | OFFENDER |
| `furn_counter_kafe_v4` | 96x64 | front | 0.636 | 15.1% | OFFENDER |
| `furn_kursi_kafe` | 32x48 | front | 0.984 | 27.4% | OFFENDER |
| `furn_kursi_kafe_v4` | 32x48 | front | 0.984 | 27.4% | OFFENDER |
| `furn_meja_kafe` | 64x64 | front | 0.989 | 18.6% | OFFENDER |
| `furn_meja_kafe_v4` | 64x64 | front | 0.989 | 18.6% | OFFENDER |
| `furn_mesin_capit` | 64x96 | front | 0.851 | 0.0% | PASS |
| `furn_mesin_capit_v4` | 64x96 | front | 0.851 | 0.0% | PASS |
| `furn_sofa_nonton` | 96x64 | front | 0.581 | 0.0% | OFFENDER |
| `furn_sofa_nonton_v4` | 96x64 | front | 0.581 | 0.0% | OFFENDER |
| `furn_tanaman_pot` | 32x48 | front | 0.585 | 0.0% | OFFENDER |
| `furn_tanaman_pot_v4` | 32x48 | front | 0.585 | 0.0% | OFFENDER |
| `furn_tv_besar` | 96x64 | front | 0.693 | 9.9% | OFFENDER |
| `furn_tv_besar_v4` | 96x64 | front | 0.693 | 9.9% | OFFENDER |
| `furn_bak_mandi` | 64x64 | front | 0.896 | 12.4% | OFFENDER |
| `furn_bak_mandi_v4` | 64x64 | front | 0.896 | 12.4% | OFFENDER |
| `furn_bak_mandi_v6` | 64x64 | front | 0.98 | 0.0% | PASS |
| `furn_bingkai_kosong` | 32x32 | front | 0.998 | 14.6% | OFFENDER |
| `furn_bingkai_kosong_v4` | 32x32 | front | 0.998 | 14.6% | OFFENDER |
| `furn_ember` | 32x32 | front | 0.969 | 0.0% | PASS |
| `furn_ember_v6` | 32x32 | front | 0.965 | 0.0% | PASS |
| `furn_jam_dinding` | 32x32 | front | 1.0 | 14.9% | OFFENDER |
| `furn_jam_dinding_v4` | 32x32 | front | 1.0 | 14.9% | OFFENDER |
| `furn_jendela` | 64x64 | front | 0.877 | 9.8% | OFFENDER |
| `furn_jendela_dapur_v6` | 64x48 | front | 1.0 | 0.0% | PASS |
| `furn_jendela_v4` | 64x64 | front | 0.877 | 9.8% | OFFENDER |
| `furn_karpet_tamu` | 128x96 | front | 0.735 | 0.0% | OFFENDER |
| `furn_kasur_besar` | 96x112 | front | 0.992 | 0.0% | PASS |
| `furn_kipas_berdiri` | 32x64 | front | 0.914 | 0.0% | PASS |
| `furn_kompor_counter` | 96x64 | front | 0.713 | 0.0% | OFFENDER |
| `furn_kulkas` | 64x96 | front | 0.927 | 0.0% | PASS |
| `furn_kursi_makan` | 32x48 | front | 0.53 | 36.9% | OFFENDER |
| `furn_kursi_makan_back_v6` | 32x48 | back | 1.0 | 0.0% | PASS |
| `furn_kursi_makan_depan` | 32x48 | front | 0.53 | 36.9% | OFFENDER |
| `furn_kursi_makan_depan_v4` | 32x48 | front | 0.53 | 36.9% | OFFENDER |
| `furn_kursi_makan_front_v6` | 32x48 | front | 1.0 | 0.0% | PASS |
| `furn_kursi_makan_kanan` | 32x48 | front | 0.961 | 39.2% | OFFENDER |
| `furn_kursi_makan_kanan_v4` | 32x48 | front | 0.961 | 39.2% | OFFENDER |
| `furn_kursi_makan_kanan_v6` | 32x48 | right | 0.503 | 0.0% | PASS |
| `furn_kursi_makan_kiri` | 32x48 | front | 0.58 | 37.7% | OFFENDER |
| `furn_kursi_makan_kiri_v4` | 32x48 | front | 0.58 | 37.7% | OFFENDER |
| `furn_kursi_makan_kiri_v6` | 32x48 | left | 0.503 | 0.0% | PASS |
| `furn_kursi_makan_v4` | 32x48 | front | 0.53 | 36.9% | OFFENDER |
| `furn_lemari_besar` | 96x96 | front | 1.0 | 0.0% | PASS |
| `furn_meja_makan` | 96x64 | front | 0.982 | 0.0% | PASS |
| `furn_meja_rias` | 64x80 | front | 1.0 | 0.0% | PASS |
| `furn_meja_tamu` | 64x48 | front | 0.99 | 0.0% | PASS |
| `furn_pintu_depan` | 64x96 | front | 1.0 | 1.0% | PASS |
| `furn_pintu_depan_v4` | 64x96 | front | 1.0 | 1.0% | PASS |
| `furn_pintu_kamar` | 64x96 | front | 1.0 | 1.2% | PASS |
| `furn_pintu_kamar_v4` | 64x96 | front | 1.0 | 1.2% | PASS |
| `furn_rak_handuk` | 32x64 | front | 0.52 | 0.0% | OFFENDER |
| `furn_rak_handuk_v6` | 32x64 | front | 1.0 | 0.0% | PASS |
| `furn_rak_pajangan` | 64x96 | front | 0.943 | 0.0% | PASS |
| `furn_rak_piring` | 64x80 | front | 0.73 | 9.7% | OFFENDER |
| `furn_rak_piring_dinding_v6` | 64x48 | front | 1.0 | 0.0% | PASS |
| `furn_rak_piring_v4` | 64x80 | front | 0.73 | 9.7% | OFFENDER |
| `furn_sofa_3dudukan` | 128x64 | front | 0.996 | 0.0% | PASS |
| `furn_sofa_single` | 64x64 | front | 0.982 | 0.0% | PASS |
| `furn_toilet` | 32x48 | front | 0.482 | 0.0% | OFFENDER |
| `furn_toilet_v6` | 32x48 | front | 1.0 | 0.0% | PASS |
| `furn_tv_dan_rak` | 96x64 | front | 0.998 | 0.0% | PASS |
| `furn_wastafel_cermin` | 64x80 | front | 0.515 | 17.3% | OFFENDER |
| `furn_wastafel_cermin_v4` | 64x80 | front | 0.515 | 17.3% | OFFENDER |
| `furn_wastafel_cermin_v6` | 64x80 | front | 1.0 | 0.0% | PASS |
| `furn_wastafel_dapur` | 96x64 | front | 0.648 | 0.0% | OFFENDER |
| `furn_kasur_single` | 64x96 | front | 0.998 | 0.0% | PASS |
| `furn_kursi_belajar` | 32x48 | front | 0.687 | 0.0% | OFFENDER |
| `furn_lemari_pakaian` | 64x96 | front | 0.971 | 0.0% | PASS |
| `furn_meja_belajar` | 96x64 | front | 0.838 | 0.0% | PASS |
| `furn_nakas_lampu` | 32x48 | front | 0.962 | 0.0% | PASS |
| `furn_rak_buku` | 64x96 | front | 1.0 | 0.0% | PASS |
| `furn_etalase_kaca` | 96x64 | front | 0.735 | 8.6% | OFFENDER |
| `furn_etalase_kaca_v4` | 96x64 | front | 0.735 | 8.6% | OFFENDER |
| `furn_kasir_kecil` | 64x64 | front | 0.707 | 17.8% | OFFENDER |
| `furn_kasir_kecil_v4` | 64x64 | front | 0.707 | 17.8% | OFFENDER |
| `furn_kursi_cermin` | 32x48 | front | 0.968 | 0.0% | PASS |
| `furn_kursi_cermin_v4` | 32x48 | front | 0.968 | 0.0% | PASS |
| `furn_kursi_tunggu` | 32x48 | front | 0.792 | 17.1% | OFFENDER |
| `furn_kursi_tunggu_v4` | 32x48 | front | 0.792 | 17.1% | OFFENDER |
| `furn_meja_cermin` | 64x64 | front | 0.59 | 26.2% | OFFENDER |
| `furn_meja_cermin_v4` | 64x64 | front | 0.59 | 26.2% | OFFENDER |
| `furn_rak_dinding_kosmetik` | 64x80 | front | 0.623 | 11.2% | OFFENDER |
| `furn_rak_dinding_kosmetik_v4` | 64x80 | front | 0.623 | 11.2% | OFFENDER |
| `furn_sofa_tunggu` | 64x64 | front | 0.71 | 0.0% | OFFENDER |
| `furn_sofa_tunggu_v4` | 64x64 | front | 0.71 | 0.0% | OFFENDER |
| `furn_tanaman_pot` | 32x48 | front | 0.585 | 0.0% | OFFENDER |
| `furn_tanaman_pot_v4` | 32x48 | front | 0.585 | 0.0% | OFFENDER |
| `furn_etalase_makanan_siap_saji` | 96x64 | front | 0.68 | 0.0% | OFFENDER |
| `furn_etalase_makanan_siap_saji_v4` | 96x64 | front | 0.68 | 0.0% | OFFENDER |
| `furn_galon_tumpuk` | 32x48 | front | 0.89 | 0.0% | PASS |
| `furn_galon_tumpuk_v4` | 32x48 | front | 0.89 | 0.0% | PASS |
| `furn_kasir_counter` | 96x64 | front | 0.687 | 13.0% | OFFENDER |
| `furn_kasir_counter_v4` | 96x64 | front | 0.687 | 13.0% | OFFENDER |
| `furn_keranjang_belanja` | 32x32 | front | 0.895 | 15.5% | OFFENDER |
| `furn_keranjang_belanja_v4` | 32x32 | front | 0.895 | 15.5% | OFFENDER |
| `furn_kulkas_minuman_besar` | 96x96 | front | 0.786 | 5.9% | OFFENDER |
| `furn_kulkas_minuman_besar_v4` | 96x96 | front | 0.786 | 5.9% | OFFENDER |
| `furn_mesin_fotokopi` | 64x64 | front | 0.879 | 13.7% | OFFENDER |
| `furn_mesin_fotokopi_v4` | 64x64 | front | 0.879 | 13.7% | OFFENDER |
| `furn_rak_alat_tulis` | 64x80 | front | 0.775 | 14.1% | OFFENDER |
| `furn_rak_alat_tulis_v4` | 64x80 | front | 0.775 | 14.1% | OFFENDER |
| `furn_rak_dinding_snack` | 64x96 | front | 0.676 | 0.0% | OFFENDER |
| `furn_rak_dinding_snack_v4` | 64x96 | front | 0.676 | 0.0% | OFFENDER |
| `furn_rak_gondola` | 96x64 | front | 0.695 | 11.9% | OFFENDER |
| `furn_rak_gondola_v4` | 96x64 | front | 0.695 | 11.9% | OFFENDER |
| `furn_rak_mie_instan` | 64x80 | front | 0.752 | 0.0% | OFFENDER |
| `furn_rak_mie_instan_v4` | 64x80 | front | 0.752 | 0.0% | OFFENDER |
| `furn_rak_roti` | 64x64 | front | 0.729 | 0.0% | OFFENDER |
| `furn_rak_roti_v4` | 64x64 | front | 0.729 | 0.0% | OFFENDER |
| `furn_tempat_sampah` | 32x32 | front | 0.973 | 0.0% | PASS |
| `furn_tempat_sampah_v4` | 32x32 | front | 0.973 | 0.0% | PASS |
| `prop_motor_parkir` | 48x32 | front | 0.588 | 46.3% | OFFENDER |
| `furn_bangku_dinding_v6` | 96x32 | front | 0.999 | 0.0% | PASS |
| `furn_bangku_kantin` | 96x32 | front | 0.533 | 31.5% | OFFENDER |
| `furn_bangku_kantin_v4` | 96x32 | front | 0.533 | 31.5% | OFFENDER |
| `furn_bangku_tunggu` | 64x32 | front | 0.533 | 32.8% | OFFENDER |
| `furn_bangku_tunggu_v4` | 64x32 | front | 0.533 | 32.8% | OFFENDER |
| `furn_counter_kantin` | 128x64 | front | 0.678 | 24.0% | OFFENDER |
| `furn_counter_kantin_etalase` | 160x80 | front | 0.81 | 0.0% | PASS |
| `furn_counter_kantin_etalase_v4` | 160x80 | front | 0.81 | 0.0% | PASS |
| `furn_counter_kantin_v4` | 128x64 | front | 0.678 | 24.0% | OFFENDER |
| `furn_counter_pustakawan` | 96x64 | front | 0.897 | 0.0% | PASS |
| `furn_counter_pustakawan_v4` | 96x64 | front | 0.897 | 0.0% | PASS |
| `furn_dispenser_galon` | 32x64 | front | 0.989 | 10.7% | OFFENDER |
| `furn_dispenser_galon_v4` | 32x64 | front | 0.989 | 10.7% | OFFENDER |
| `furn_komputer_meja` | 48x48 | front | 0.945 | 0.0% | PASS |
| `furn_komputer_meja_v4` | 48x48 | front | 0.945 | 0.0% | PASS |
| `furn_kulkas_minuman` | 64x96 | front | 0.924 | 4.9% | PASS |
| `furn_kulkas_minuman_v4` | 64x96 | front | 0.924 | 4.9% | PASS |
| `furn_kursi_baca` | 32x48 | front | 0.577 | 0.0% | OFFENDER |
| `furn_kursi_baca_back_v6` | 32x48 | back | 0.989 | 0.0% | PASS |
| `furn_kursi_baca_v4` | 32x48 | front | 0.577 | 0.0% | OFFENDER |
| `furn_kursi_guru` | 32x48 | front | 0.507 | 0.0% | OFFENDER |
| `furn_kursi_guru_v4` | 32x48 | front | 0.507 | 0.0% | OFFENDER |
| `furn_kursi_guru_v6` | 32x48 | front | 0.989 | 0.0% | PASS |
| `furn_kursi_siswa` | 32x48 | front | 0.464 | 0.0% | OFFENDER |
| `furn_kursi_siswa_v4` | 32x48 | front | 0.464 | 0.0% | OFFENDER |
| `furn_lemari_kelas` | 64x96 | front | 0.802 | 5.6% | OFFENDER |
| `furn_lemari_kelas_v4` | 64x96 | front | 0.802 | 5.6% | OFFENDER |
| `furn_meja_baca` | 96x64 | front | 0.503 | 19.9% | OFFENDER |
| `furn_meja_baca_set_a_v6` | 112x80 | composite | 0.97 | 0.0% | PASS |
| `furn_meja_baca_set_b_v6` | 112x80 | composite | 0.97 | 0.0% | PASS |
| `furn_meja_baca_v4` | 96x64 | front | 0.503 | 19.9% | OFFENDER |
| `furn_meja_guru` | 96x64 | front | 0.7 | 16.5% | OFFENDER |
| `furn_meja_guru_v4` | 96x64 | front | 0.7 | 16.5% | OFFENDER |
| `furn_meja_guru_v6` | 96x64 | front | 0.972 | 0.0% | PASS |
| `furn_meja_kantin` | 96x64 | front | 0.54 | 25.5% | OFFENDER |
| `furn_meja_kantin_panjang` | 96x64 | front | 0.925 | 0.0% | PASS |
| `furn_meja_kantin_panjang_v4` | 96x64 | front | 0.925 | 0.0% | PASS |
| `furn_meja_kantin_set_a_v6` | 128x80 | composite | 0.976 | 0.0% | PASS |
| `furn_meja_kantin_set_b_v6` | 128x80 | composite | 0.978 | 0.0% | PASS |
| `furn_meja_kantin_v4` | 96x64 | front | 0.54 | 25.5% | OFFENDER |
| `furn_meja_siswa` | 64x48 | front | 0.661 | 0.0% | OFFENDER |
| `furn_meja_siswa_kursi` | 64x64 | front | 0.698 | 22.6% | OFFENDER |
| `furn_meja_siswa_kursi_a_v6` | 64x80 | composite | 0.991 | 0.0% | PASS |
| `furn_meja_siswa_kursi_b_v6` | 64x80 | composite | 0.971 | 0.0% | PASS |
| `furn_meja_siswa_kursi_v4` | 64x64 | front | 0.698 | 22.6% | OFFENDER |
| `furn_meja_siswa_v4` | 64x48 | front | 0.661 | 0.0% | OFFENDER |
| `furn_papan_info` | 96x48 | front | 1.0 | 0.0% | PASS |
| `furn_papan_info_v4` | 96x48 | front | 1.0 | 0.0% | PASS |
| `furn_papan_menu_kosong` | 96x48 | front | 0.997 | 0.0% | PASS |
| `furn_papan_menu_kosong_v4` | 96x48 | front | 0.997 | 0.0% | PASS |
| `furn_papan_pengumuman` | 96x64 | front | 0.605 | 8.7% | OFFENDER |
| `furn_papan_pengumuman_v4` | 96x64 | front | 0.605 | 8.7% | OFFENDER |
| `furn_papan_tulis` | 128x64 | front | 0.544 | 10.5% | OFFENDER |
| `furn_papan_tulis_v4` | 128x64 | front | 0.544 | 10.5% | OFFENDER |
| `furn_papan_tulis_v6` | 128x64 | front | 0.983 | 0.0% | PASS |
| `furn_poster_kosong` | 32x48 | front | 0.592 | 12.0% | OFFENDER |
| `furn_poster_kosong_v4` | 32x48 | front | 0.592 | 12.0% | OFFENDER |
| `furn_rak_buku_kelas` | 64x96 | front | 0.816 | 0.0% | PASS |
| `furn_rak_buku_kelas_v4` | 64x96 | front | 0.816 | 0.0% | PASS |
| `furn_rak_buku_kelas_v6` | 64x96 | front | 1.0 | 0.0% | PASS |
| `furn_rak_buku_perpus` | 96x96 | front | 0.783 | 5.0% | OFFENDER |
| `furn_rak_buku_perpus_v4` | 96x96 | front | 0.783 | 5.0% | OFFENDER |
| `furn_rak_piala` | 64x96 | front | 0.996 | 0.0% | PASS |
| `furn_rak_piala_v4` | 64x96 | front | 0.996 | 0.0% | PASS |
| `furn_rak_snack` | 64x80 | front | 0.765 | 20.1% | OFFENDER |
| `furn_rak_snack_v4` | 64x80 | front | 0.765 | 20.1% | OFFENDER |
| `furn_tempat_sampah` | 32x32 | front | 0.973 | 0.0% | PASS |
| `furn_tempat_sampah_kelas` | 32x32 | front | 0.911 | 18.9% | OFFENDER |
| `furn_tempat_sampah_kelas_v4` | 32x32 | front | 0.911 | 18.9% | OFFENDER |
| `furn_tempat_sampah_v4` | 32x32 | front | 0.973 | 0.0% | PASS |
| `furn_vas_tanaman` | 32x48 | front | 0.835 | 33.3% | OFFENDER |
| `furn_vas_tanaman_v4` | 32x48 | front | 0.835 | 33.3% | OFFENDER |
| `furn_wastafel_cuci_tangan` | 48x64 | front | 0.999 | 0.0% | PASS |
| `furn_wastafel_cuci_tangan_v4` | 48x64 | front | 0.999 | 0.0% | PASS |
| `furn_bangku_spbu` | 64x32 | front | 0.734 | 18.9% | OFFENDER |
| `furn_bangku_spbu_v4` | 64x32 | front | 0.734 | 18.9% | OFFENDER |
| `furn_dispenser_bbm` | 64x80 | front | 0.773 | 16.9% | OFFENDER |
| `furn_dispenser_bbm_v4` | 64x80 | front | 0.773 | 16.9% | OFFENDER |
| `furn_kiosk_spbu` | 96x64 | front | 0.993 | 11.0% | OFFENDER |
| `furn_kiosk_spbu_v4` | 96x64 | front | 0.993 | 11.0% | OFFENDER |
| `furn_kompresor_angin` | 32x48 | front | 0.88 | 0.0% | PASS |
| `furn_kompresor_angin_v4` | 32x48 | front | 0.88 | 0.0% | PASS |
| `furn_rak_oli` | 64x64 | front | 0.732 | 16.9% | OFFENDER |
| `furn_rak_oli_v4` | 64x64 | front | 0.732 | 16.9% | OFFENDER |
| `furn_tempat_sampah` | 32x32 | front | 0.973 | 0.0% | PASS |
| `furn_tempat_sampah_v4` | 32x32 | front | 0.973 | 0.0% | PASS |
| `furn_tiang_kanopi` | 32x128 | front | 0.996 | 0.0% | PASS |
| `furn_tiang_kanopi_v4` | 32x128 | front | 0.996 | 0.0% | PASS |
| `furn_tong_pemadam` | 32x40 | front | 0.56 | 0.0% | OFFENDER |
| `furn_tong_pemadam_v4` | 32x40 | front | 0.56 | 0.0% | OFFENDER |
