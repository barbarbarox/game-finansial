# Reproduksi Masalah B11: Peringatan Energi di Bawah 50% Belum Ada
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Turunkan energi pemain menjadi 48%.
- **Hasil Aktual:** Tidak ada toast/banner peringatan teks yang muncul pada layar HUD.
- **Tangkapan Layar:** `docs/regression/b11_peringatan_energi_50_red.png`
- **Akar Masalah:** Ambang batas peringatan di HUD sebelumnya hanya pada 25% dan 10%, belum ada pendeteksi ambang <50% dengan teks persis "Energi kamu di bawah 50%, silakan makan untuk menambahnya." (Rule 83 §2).
