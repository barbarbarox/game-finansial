# Reproduksi Masalah A1: Pembelian Item Tidak Masuk Inventaris
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI:** Pemain berinteraksi dengan Ibu Sri di kantin, memilih opsi "Beli Nasi Kuning Komplit (Rp12.000)".
- **Hasil Aktual:** Uang kas terpotong di buku kas, namun `state.inventory` tetap kosong (5 slot bernilai null) dan hotbar DOM tidak menampilkan item baru.
- **Tangkapan Layar:** `docs/regression/a1_shop_purchase_red.png`
- **Akar Masalah:** Pilihan dialog hanya memicu efek `ledger_expense` dan `start_activity`, tanpa memanggil `inventory.add(itemId, count)`.

