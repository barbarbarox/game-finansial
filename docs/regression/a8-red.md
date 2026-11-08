# Reproduksi Masalah A8: Nakas Menghalangi Jalan ke Kasur Kamar Pemain
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI:** Pemain masuk dari pintu kamar tidur dan berjalan menuju kasur.
- **Hasil Aktual:** Nakas lampu berada di posisi $x=6.8, y=3.5$ berstatus `collidable: true`, menonjol di sebelah kanan kasur ($x=4.5..6.5, y=2..5$). Di sebelah kiri terdapat lemari pakaian, sehingga menyisakan koridor sempit yang menghalangi rute bebas ke titik interaksi kasur.
- **Tangkapan Layar:** `docs/regression/a8_nakas_blocked_red.png`
- **Akar Masalah:** Koordinat $y=3.5$ pada nakas mempersempit akses samping dan bawah kasur.

