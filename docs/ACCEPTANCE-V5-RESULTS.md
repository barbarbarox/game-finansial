# ACCEPTANCE-V5-RESULTS — Matriks Hasil Penerimaan V5

> Diisi baris per baris dengan bukti. Semua pengujian wajib melalui **UI nyata** (pointer/keyboard), bukan hook debug (Rule 78). Status: PASS / FAIL / BELUM.

| ID | Permintaan Pengguna | Langkah UI yang Diuji | Hasil yang Diharapkan | Status | Nama Tes / Bukti | Tangkapan Layar |
|---|---|---|---|---|---|---|
| A1 | Membeli makanan/minuman → item masuk inventaris | Di kantin, minimarket, kafe game center: buka vendor → "Beli sesuatu" → beli item | Ledger tercatat, Kas berkurang tepat, item muncul di hotbar/tas (DOM + state) | BELUM (H0) | `test_h0_red_suite.py` | `docs/regression/a1_shop_purchase_red.png` |
| A2 | Menu pilihan item beli tersedia | Dialog vendor DAN interaktif rak/kulkas/etalase/konter membuka panel toko; SPBU membuka menu nominal | Panel menampilkan item dengan ikon, harga, efek; tab kategori; jumlah 1–5 | BELUM (H0) | `test_h0_red_suite.py` | `docs/regression/a2_shop_menu_red.png` |
| A3 | Hotbar penuh → ransel menampung; hotbar kosong → terisi otomatis | Beli 7 item; pakai 1 dari hotbar | 5 di hotbar + 2 di ransel; setelah pakai, slot terisi otomatis dari ransel; invarian properti hijau | BELUM (H0) | `test_h0_red_suite.py` | `docs/regression/a3_backpack_refill_red.png` |
| A4 | Tombol ransel di sebelah inventaris | Klik tombol ransel (dan tombol B) | Panel ransel 20 slot terbuka; lencana jumlah benar; Esc menutup | BELUM (H0) | `test_h3_backpack.py` | Belum diuji |
| A5 | Item disentuh → opsi untuk menggunakannya | Klik slot hotbar dan slot ransel | Popup: Gunakan / Pindahkan / Buang; Gunakan menaikkan energi dan mengurangi jumlah; Buang meminta konfirmasi; 1–5 pakai cepat | BELUM (H0) | `test_h0_red_suite.py` | `docs/regression/a5_item_popup_red.png` |
| A6 | Tas penuh menolak pembelian | Isi 25/25 lalu beli | Pesan "Tas penuh"; saldo dan ledger tidak berubah | BELUM (H0) | `test_h0_red_suite.py` | Belum diuji |
| A7 | Gerak dengan klik titik tujuan | Klik titik di hub dan interior; klik NPC/pintu/kasur; tekan WASD saat berjalan; klik HUD | Berjalan lewat jalur menghindari rintangan, tiba di titik; klik NPC/pintu/kasur → auto-interaksi; WASD membatalkan; klik HUD tidak menggerakkan | BELUM (H0) | `test_h0_red_suite.py` | `docs/regression/a7_click_to_move_red.png` |
| A8 | Nakas tidak menghalangi jalan ke kasur | Dari pintu kamar, klik kasur (atau jalan manual) → tidur | Pemain mencapai titik interaksi kasur tanpa terhalang; tidur berjalan; `approachCheck` hijau untuk semua interactable 7 peta | PASS (H2) | `tools/test_h2_nakas_access.py`, `tests/layout-check.html` | `docs/regression/a8_nakas_unblocked_green.png` |
| A9 | Bar bensin terupdate setelah isi bensin | Di SPBU isi tiap preset dan "Isi penuh"; muat ulang | Bar bensin, teks persen, state, dan saldo konsisten dan berubah sesuai; tetap benar setelah muat ulang; tangki penuh → pesan tanpa transaksi | PASS (H1) | `tools/test_h1_hud_fuel.py`, `tests/hud-sync.html` | `docs/regression/a9_gas_bar_green.png` |
| A10 | Tidak ada regresi | Jalankan self-test, time-test, dialogue-test, map-check, layout-check, hud-sync, E2E multi-hari berbasis UI | Semua hijau; daftar tes yang memakai hook disebut beserta alasan | BELUM (H0) | Menunggu H6 | Belum diuji |
| A11 | Keaslian aset | Audit piksel + tinjauan visual tiap interior | 0 aset placeholder berstatus ready; contact sheet per peta | PASS (Audit H0) | `tools/audit_asset_authenticity.py` | 301 file, 0 placeholder boks |

**Ringkasan Status Saat Ini:**
- **PASS:** 1 (A11 Audit Keaslian Aset)
- **FAIL (Merah Reproduksi):** A1, A2, A3, A5, A7, A8, A9 (Diverifikasi gagal lewat tes merah UI nyata di H0)
- **BELUM:** A4, A6, A10 (Akan diuji di gerbang H1–H6)

