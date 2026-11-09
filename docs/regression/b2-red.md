# Reproduksi Masalah B2: Meja Guru dan Papan Tulis Miring
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Buka ruang kelas di `school`, periksa meja guru dan papan tulis di depan kelas.
- **Hasil Aktual:** Meja guru miring menyudut dan papan tulis memiliki bingkai bersudut asimetris (IoU simetri 0.544).
- **Tangkapan Layar:** `docs/regression/b2_meja_guru_papan_tulis_red.png`
- **Akar Masalah:** Prompt generator tidak mewajibkan elevasi frontal murni (front elevation, left-right symmetrical).
