# Reproduksi Masalah B10: Biaya Energi Tidak Sesuai Tabel Realistis
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Hitung biaya energi untuk aktivitas `ikut_pelajaran` dan `main_game`.
- **Hasil Aktual:** `ikut_pelajaran` menguras 5% per jam (total 37.5% untuk 7.5 jam), bukan tepat -20% proporsional Sesi 1/2.
- **Tangkapan Layar:** `docs/regression/b10_biaya_energi_red.png`
- **Akar Masalah:** `src/domain/energy.js` masih memakai tarif lama Rule 74, belum mengadopsi tarif `v6.config.additions.json` (Rule 83 §1).
