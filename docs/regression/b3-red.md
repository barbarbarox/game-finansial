# Reproduksi Masalah B3: Meja dan Bangku Kantin Serong & Melintasi Dinding
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Buka area kantin sekolah (`school`), periksa meja panjang dan bangku kantin.
- **Hasil Aktual:** Meja piknik kantin digambar diagonal, dan bangku kantin bawah ditempatkan di y=10 sehingga melintasi dinding pembatas dan pintu masuk koridor.
- **Tangkapan Layar:** `docs/regression/b3_meja_bangku_kantin_red.png`
- **Akar Masalah:** Meja dan bangku tidak dibuat sebagai satu komposit frontal, serta koordinat slot melampaui batas lantai lantai_kantin.
