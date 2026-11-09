---
trigger: model_decision
description: "Terapkan saat membuat atau memperbaiki toko/pembelian: panel menu pilihan item beli, vendor (kantin, minimarket, game center, toko kosmetik, SPBU), rak/kulkas yang bisa dibeli, makan di tempat vs bungkus, pembelian masuk inventaris, isi bensin (nominal dan bar bensin), serta data shops."
---

# 79 · Toko dan Vendor

## 1. Masalah yang diperbaiki
Membeli makanan/minuman di NPC tidak memasukkan item ke inventaris dan **tidak ada menu untuk memilih item**. Kemungkinan penyebab (verifikasi lewat tes merah): dialog vendor belum memanggil efek buka-toko; katalog item tidak selaras dengan ikon yang ada (ikon hasil generate memakai item berbeda dari `items.phase1.json`); pembelian hanya mengurangi saldo tanpa memanggil `inventory.add`.

## 2. Sumber kebenaran
- **Item konsumsi:** `data/items.phase1.json` (+ tipe item di `data/items-types.v5.json`). **Selaraskan dengan ikon yang benar-benar ada** di `assets/items/`: jika ikon hasil generate berbeda dari katalog (mis. mie ayam, lemper, soto ayam), perbarui katalog agar sesuai ikon yang ada (id, label, harga, energi, `sellAt`, tipe). Jangan membuang ikon. Setiap item yang dijual **wajib** punya ikon valid; item tanpa ikon tidak boleh tampil di toko.
- **Toko:** `data/shops.phase1.json` (metadata toko, barang non-konsumsi, aturan rak, mode beli). Konsumsi per toko diturunkan dari `sellAt` di katalog item.

## 3. Panel toko (DOM, gaya UI pengguna; audit komponen panel yang ada dan pakai ulang)
- Header: nama toko + potret vendor (bila ada) + **Kas** saat ini. Tab kategori sesuai item yang tersedia (Makanan, Minuman, Snack, Lainnya).
- Kartu item: ikon, nama, harga, efek energi (+N), tombol **Beli**; pengatur jumlah 1–5.
- Mode beli per toko: **kantin** dan **kafe game center**: pilihan **Makan di tempat** (efek langsung, waktu `consumeMinutes`) atau **Bungkus** (masuk tas); **minimarket**: Bungkus saja. Item yang dibungkus masuk lewat `inventory.add` (lihat `80-inventory-backpack-item-actions.md`).
- Indikator kapasitas: "Hotbar x/5 · Ransel y/20". Tombol Beli nonaktif dengan alasan jelas bila saldo kurang, tas penuh, atau toko tutup.
- Umpan balik: toast "+1 Nasi goreng → Ransel", saldo dan lencana ransel/hotbar berubah seketika. Esc/tombol Tutup menutup panel. Jam berhenti saat panel terbuka; **setiap konfirmasi pembelian** memajukan `purchaseMinutes` (default 5) lewat `advanceTime`.
- Transaksi lewat domain: entri ledger (Beban Makanan/Jajan, deskripsi dari data) **dan** `inventory.add` dalam satu operasi **atomik**: jika `canAdd` gagal, saldo tidak berkurang.

## 4. Pemicu
- **Dialog vendor** (Bu Sri/penjual kantin, Mbak Maya, Kak Cindy, Kak Riko): pilihan **"Beli sesuatu"** memicu efek whitelist baru `openShop(shopId)` (tambahkan ke validator efek dialog). Setiap vendor juga punya pilihan lain yang relevan (mis. Kak Riko: main game).
- **Interactable rak/kulkas/etalase/konter** dengan properti `shop` membuka panel yang sama dengan filter:
  - minimarket: `rak_dinding_snack` → Snack; `kulkas_minuman_besar` → Minuman; `etalase_makanan_siap_saji` → Makanan; `kasir_counter` → semua + barang non-konsumsi; `rak_alat_tulis`, `mesin_fotokopi` → barang masing-masing.
  - kantin: `counter_kantin_etalase` (satu-satunya tempat belanja kantin); kafe game center: `counter_kafe`; toko kosmetik: `etalase_kaca`, `kasir_kecil`.
- Toko tutup (jam buka, rule 70/72) → panel tidak terbuka, pesan jam buka.

## 5. Barang non-konsumsi (langsung tercatat, tidak masuk tas)
Alat tulis Rp15.000, fotokopi Rp5.000, paket kuota hemat Rp15.000 / besar Rp35.000 (set flag), lip tint Rp35.000, skincare Rp75.000 (promo dari kejadian tetap berlaku). Mereka memakai panel yang sama (tab Lainnya), mencatat ledger kategori masing-masing dan `advanceTime` sesuai katalog aktivitas.

## 6. SPBU: isi bensin
- Menu di panel toko khusus: preset **Rp10.000 / Rp20.000 / Rp30.000 / Isi penuh**; harga per persen = `spbu.pricePerPercent` (default 500 → Rp20.000 = +40%). "Isi penuh" = (100 − bensin) × harga/persen; nominal tidak boleh melebihi kebutuhan; tangki 100% → "Tangki sudah penuh" (tanpa transaksi).
- Konfirmasi → ledger (Beban Transportasi) + **`fuel.refuelPercent(n)` di domain** yang memancarkan `fuelChanged`; **bar bensin berlangganan event itu** dan beranimasi ke nilai baru; `advanceTime(10)`.
- **Bug yang dilaporkan:** bar bensin tidak berubah setelah isi bensin. Tulis tes merah dulu (rule 78): bar sebelum/sesudah, teks persen, state domain, dan setelah simpan/muat. Periksa kemungkinan: efek isi bensin mengubah state tanpa event; bar membaca salinan nilai; atau dua penyimpanan bensin (harian lama vs motor).

## 7. Uji wajib (UI nyata, rule 78)
Untuk tiap vendor: berjalan/klik ke NPC → tekan E → pilih "Beli sesuatu" → panel terbuka → beli ≥ 2 item berbeda → cek ledger (jumlah tepat), saldo, hotbar/ransel (DOM + state), jam maju. Dari rak/kulkas minimarket yang sama. Negatif: saldo kurang, tas penuh (saldo tetap), toko tutup. SPBU: tiap preset + isi penuh + tangki penuh; bar bensin berubah sesuai, juga setelah muat ulang. Setiap item yang dijual punya ikon (uji katalog-ikon). Tangkapan layar tiap panel toko.

## 8. Pembaruan v6
Panel toko wajib memiliki tombol keluar (X, Selesai, Esc, klik luar) dan menampilkan karakter NPC vendor, sesuai `86-shop-vendor-presence.md`. Berlaku untuk kantin, minimarket, toko kosmetik, kafe game center, dan menu SPBU.
