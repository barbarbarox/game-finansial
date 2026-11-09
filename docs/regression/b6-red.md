# Reproduksi Masalah B6: Wastafel dan Toilet Perspektif Tidak Konsisten
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Periksa kamar mandi di `home.layout.json`.
- **Hasil Aktual:** Toilet dan wastafel digambar serong/isometrik (IoU toilet = 0.482, wastafel = 0.515), cermin terpisah dan tidak sejajar wastafel.
- **Tangkapan Layar:** `docs/regression/b6_wastafel_toilet_red.png`
- **Akar Masalah:** Tidak ada kontrak sudut pandang frontal untuk perlengkapan sanitasi kamar mandi.
