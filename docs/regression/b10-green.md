# Laporan Verifikasi Hijau B10: Biaya Energi Sesuai Tabel Realistis (Rule 83)
- **Status:** PASS (Hijau Terverifikasi)
- **Akar Masalah:** Sebelumnya konfigurasi tarif energi masih menggunakan skema generik Rule 74 (5%/jam tanpa pemisahan sesi sekolah dan biaya game center terlalu rendah 4%/jam).
- **Perbaikan:**
  - `src/domain/energy.js` dirombak total mengacu pada tabel Rule 83:
    - `ikut_pelajaran` / `pelajaran_sekolah`: Sesi 1 (180 menit) menguras tepat 9%, Sesi 2 (240 menit) menguras tepat 11%, total seharian sekolah tepat 20%.
    - `main_game`: 20% per jam (60 min = 20%, 120 min = 40%).
    - `belajar_mandiri`: 8% per jam (60 min = 8%).
    - `baca_perpustakaan`: 3% per jam.
    - `nonton_tv`: 1% per jam.
    - `mandi`: 1% flat.
  - Mengintegrasikan fungsi validasi ketersediaan energi `canPerformActivity()` yang memproyeksikan sisa energi dan memblokir aktivitas berat bila energi $\le 0\%$.
- **Langkah UI Nyata:**
  1. Inisialisasi pemain dengan energi 100%.
  2. Jalankan aktivitas `ikut_pelajaran` Sesi 1 (180 menit) $\to$ energi menjadi 91% (pengurangan 9%).
  3. Lanjutkan `ikut_pelajaran` Sesi 2 (240 menit) $\to$ energi menjadi 80% (pengurangan 11%, total 20%).
  4. Jalankan aktivitas `main_game` di game center (60 menit) $\to$ energi menjadi 60% (pengurangan 20%).
  5. Jalankan `belajar_mandiri` (60 menit) $\to$ energi menjadi 52% (pengurangan 8%).
- **Bukti Pengujian & Tangkapan Layar:**
  - Red: `docs/regression/b10_biaya_energi_red.png`
  - Green: `docs/regression/b10_biaya_energi_green.png`
- **Hasil:** PASS (100% konsisten dengan Rule 83).

