# Reproduksi Masalah A2: Menu Pilihan Item Beli Tidak Tersedia
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI:** Pemain mendekati vendor kantin / minimarket / kafe dan berinteraksi.
- **Hasil Aktual:** Hanya muncul opsi dialog teks percakapan biasa; tidak ada menu panel katalog toko dengan ikon, harga, tab kategori, pilihan kuantitas, maupun mode makan di tempat vs bungkus.
- **Tangkapan Layar:** `docs/regression/a2_shop_menu_red.png`
- **Akar Masalah:** Tidak ada implementasi `shopPanel.js` dan efek dialog `openShop` yang di-whitelist pada dialog vendor maupun interactable rak.
