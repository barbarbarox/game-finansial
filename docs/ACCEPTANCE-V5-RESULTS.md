# ACCEPTANCE-V5-RESULTS — Matriks Hasil Penerimaan V5

> Diisi baris per baris dengan bukti. Semua pengujian wajib melalui **UI nyata** (pointer/keyboard), bukan hook debug (Rule 78). Status: PASS / FAIL / BELUM.

| ID | Permintaan Pengguna | Langkah UI yang Diuji | Hasil yang Diharapkan | Status | Nama Tes / Bukti | Tangkapan Layar |
|---|---|---|---|---|---|---|
| A1 | Membeli makanan/minuman → item masuk inventaris | Di kantin, minimarket, kafe game center: buka vendor → "Beli sesuatu" → beli item | Ledger tercatat, Kas berkurang tepat, item muncul di hotbar/tas (DOM + state) | PASS (H4) | `tools/test_h4_shops.py` | `docs/regression/a1_shop_purchase_green.png` |
| A2 | Menu pilihan item beli tersedia | Dialog vendor DAN interaktif rak/kulkas/etalase/konter membuka panel toko; SPBU membuka menu nominal | Panel menampilkan item dengan ikon, harga, efek; tab kategori; jumlah 1–5 | PASS (H4) | `tools/test_h4_shops.py` | `docs/regression/a2_shop_menu_green.png` |
| A3 | Hotbar penuh → ransel menampung; hotbar kosong → terisi otomatis | Beli 7 item; pakai 1 dari hotbar | 5 di hotbar + 2 di ransel; setelah pakai, slot terisi otomatis dari ransel; invarian properti hijau | PASS (H3) | `tests/inventory_property_test.mjs` (500 ops), `tools/test_h3_backpack.py` | `docs/regression/a3_backpack_refill_green.png` |
| A4 | Tombol ransel di sebelah inventaris | Klik tombol ransel (dan tombol B) | Panel ransel 20 slot terbuka; lencana jumlah benar; Esc menutup | PASS (H3) | `tools/test_h3_backpack.py` | `docs/regression/a4_backpack_button_green.png` |
| A5 | Item disentuh → opsi untuk menggunakannya | Klik slot hotbar dan slot ransel | Popup: Gunakan / Pindahkan / Buang; Gunakan menaikkan energi dan mengurangi jumlah; Buang meminta konfirmasi; 1–5 pakai cepat | PASS (H3) | `tools/test_h3_backpack.py` | `docs/regression/a5_item_popup_green.png` |
| A6 | Tas penuh menolak pembelian | Isi 25/25 lalu beli | Pesan "Tas penuh"; saldo dan ledger tidak berubah | PASS (H3) | `tools/test_h3_backpack.py` | `docs/regression/a6_backpack_full_green.png` |
| A7 | Gerak dengan klik titik tujuan | Klik titik di hub dan interior; klik NPC/pintu/kasur; tekan WASD saat berjalan; klik HUD | Berjalan lewat jalur menghindari rintangan, tiba di titik; klik NPC/pintu/kasur → auto-interaksi; WASD membatalkan; klik HUD tidak menggerakkan | PASS (H5) | `tools/test_h5_click_to_move.py` | `docs/regression/a7_click_to_move_green.png` |
| A8 | Nakas tidak menghalangi jalan ke kasur | Dari pintu kamar, klik kasur (atau jalan manual) → tidur | Pemain mencapai titik interaksi kasur tanpa terhalang; tidur berjalan; `approachCheck` hijau untuk semua interactable 7 peta | PASS (H2) | `tools/test_h2_nakas_access.py`, `tests/layout-check.html` | `docs/regression/a8_nakas_unblocked_green.png` |
| A9 | Bar bensin terupdate setelah isi bensin | Di SPBU isi tiap preset dan "Isi penuh"; muat ulang | Bar bensin, teks persen, state, dan saldo konsisten dan berubah sesuai; tetap benar setelah muat ulang; tangki penuh → pesan tanpa transaksi | PASS (H1) | `tools/test_h1_hud_fuel.py`, `tests/hud-sync.html` | `docs/regression/a9_gas_bar_green.png` |
| A10 | Tidak ada regresi | Jalankan self-test, time-test, dialogue-test, map-check, layout-check, hud-sync, E2E multi-hari berbasis UI | Semua hijau (100%); tidak ada regresi fungsional atau akuntansi | PASS (H6) | `tools/test_h6_full_regression.py` | `docs/regression/a10_e2e_multiday_green.png` |
| A11 | Keaslian aset | Audit piksel + tinjauan visual tiap interior | 0 aset placeholder berstatus ready; contact sheet per peta | PASS (Audit H0) | `tools/audit_asset_authenticity.py` | 301 file, 0 placeholder boks |

**Ringkasan Status Saat Ini:**
- **PASS (11/11 - 100%):** A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, A11
- **SELURUH GERBANG AUTOPILOT V5 TELAH LULUS PENUH (100% GREEN)**
  - Bukti sebelum (RED) dan sesudah (GREEN) terdokumentasi lengkap di `docs/regression/`
  - Seluruh pengujian diverifikasi melalui browser UI nyata (CDP pointer & keyboard) sesuai Rule 78.

