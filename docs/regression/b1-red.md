# Reproduksi Masalah B1: Kursi dan Meja Sekolah Digambar Serong
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Buka peta sekolah (`school`), periksa orientasi meja dan kursi siswa di ruang kelas.
- **Hasil Aktual:** Meja dan kursi siswa digambar dalam sudut pandang diagonal/isometrik (IoU simetri = 0.698 < 0.80), bukan tampak depan/belakang komposit.
- **Tangkapan Layar:** `docs/regression/b1_kursi_meja_sekolah_red.png`
- **Akar Masalah:** Generator aset tidak mematuhi kontrak perspektif frontal (Rule 85 §1) dan meja-kursi dipecah menjadi aset terpisah yang tidak sejajar.
