# Reproduksi Masalah A5: Item Hotbar Tidak Memiliki Opsi Aksi Saat Disentuh
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI:** Pemain mengklik slot hotbar yang berisi item.
- **Hasil Aktual:** Tidak ada popup aksi yang muncul (`.item-action-popup` bernilai null / tidak ditemukan di DOM).
- **Tangkapan Layar:** `docs/regression/a5_item_popup_red.png`
- **Akar Masalah:** `hotbar.js` hanya menampilkan slot pasif atau shortcut angka tanpa listener klik yang menampilkan modal/popup menu Gunakan / Pindahkan / Buang.

