# Reproduksi Masalah B14: Panel Toko Tidak Memiliki Penutup Luar / Esc
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Buka panel toko (atau SPBU), klik area backdrop di luar modal atau tekan Escape.
- **Hasil Aktual:** Backdrop modal tidak memiliki event handler `click` untuk menutup panel, dan pada menu SPBU tombol Escape tidak menutup modal.
- **Tangkapan Layar:** `docs/regression/b14_toko_tanpa_tombol_keluar_red.png`
- **Akar Masalah:** `closeOnOutsideClick` dan `closeOnEsc` belum diterapkan menyeluruh pada seluruh mode panel toko (Rule 86 §2).
