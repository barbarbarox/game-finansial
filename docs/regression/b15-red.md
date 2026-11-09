# Reproduksi Masalah B15: Panel Toko Belum Menampilkan Potret Karakter NPC Vendor
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Buka katalog belanja toko (kantin, minimarket, kosmetik, SPBU, game center).
- **Hasil Aktual:** Panel hanya menampilkan thumbnail kecil 30x30 di subhead, tidak ada potret vendor besar 192x256 di sisi kiri dengan plakat nama dan gelembung ucapan dinamis.
- **Tangkapan Layar:** `docs/regression/b15_toko_tanpa_vendor_red.png`
- **Akar Masalah:** Layout panel toko belum dirancang dengan kolom potret vendor `shop.vendorSide = 'left'` (Rule 86 §3).
