# Reproduksi Masalah B12: Energi 0% Belum Membangunkan Kesiangan Pukul 10:00
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Habiskan energi pemain menjadi 0%.
- **Hasil Aktual:** Pemain hanya mendapatkan pengurangan kecepatan gerak, tidak terjadi pingsan, dan pemain tidak terbangun di kasur pukul 10:00 hari berikutnya.
- **Tangkapan Layar:** `docs/regression/b12_bangun_kesiangan_red.png`
- **Akar Masalah:** Sistem exhaustion belum mengimplementasikan sekuens pingsan dan lompat waktu `advanceTime` ke hari berikutnya pukul 10:00 (Rule 83 §3).
