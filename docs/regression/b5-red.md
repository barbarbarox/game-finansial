# Reproduksi Masalah B5: Nama Berkas Tidak Cocok dengan Isi Gambar
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Periksa isi berkas gambar `furn_bak_mandi_v4.png` dan `furn_rak_piring_v4.png`.
- **Hasil Aktual:** Berkas `furn_bak_mandi_v4.png` berisi gambar rak piring (dish rack) dengan piring/cangkir, sedangkan `furn_rak_piring_v4.png` berisi jendela bergorden.
- **Tangkapan Layar:** `docs/regression/b5_identitas_aset_tertukar_red.png`
- **Akar Masalah:** Pemotongan sheet menamai item berdasarkan nomor urut tanpa memverifikasi isi visual terhadap ekspektasi identitas (Rule 85 §2).
