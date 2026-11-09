---
trigger: model_decision
description: "Terapkan saat mengimplementasikan atau mengubah energi pemain, bar energi, inventaris/hotbar bawah-tengah, item makanan/minuman, pembelian yang masuk tas, konsumsi item, makan di rumah/kantin, atau ikon item."
---

# 74 · Energi, Inventaris (Hotbar), dan Item

## 1. Energi (domain `src/domain/energy.js`, tanpa DOM)
- Rentang 0–100, awal 100. Parameter di `data/v4.config.additions.json` (gabungkan ke `phase1.config.json`).
- **Penguras:** (a) pasif saat terjaga: `passiveDrainPerGameHour` (default 2) lewat `advanceTime`; (b) **biaya aktivitas** per jam dari katalog aktivitas (`energyCostPerHour`): belajar_mandiri 10, ikut_pelajaran 5 (±35 total), main_game 4, nongkrong_kafe 2, baca_perpustakaan 3, nonton_tv 1, aktivitas lain 0; (c) opsional: berjalan `walkDrainPerMovingMinute` (default 0,1; nonaktif bila tidak diimplementasikan). Bermotor tidak menguras energi.
- **Pengisi:** makan di dapur ibu (`makan_rumah` +40, gratis), makan di tempat di kantin (+sesuai item), konsumsi item dari tas (lihat §3), tidur (+10/jam), istirahat (+5/jam).
- **Ambang:** ≤ 25% peringatan (bar berubah ke terracotta, pesan sekali), ≤ 10% kritis, 0% **kelelahan**: kecepatan ×0,7, aktivitas berat (belajar_mandiri, ikut_pelajaran, main_game) dinonaktifkan dengan alasan jelas, dan hanya makan/istirahat/tidur yang diizinkan. Tidak ada kematian atau game over.
- Aktivitas harus **menolak** dimulai bila energi tak cukup untuk durasi minimum; pemain bisa memilih durasi lebih pendek.
- Energi disimpan di save dan masuk kondisi `phase1Result` (ringkasan: berapa kali kelelahan).

## 2. Tampilan bar energi
Tambahkan bar energi di widget HUD **mengikuti gaya UI buatan pengguna** (audit tampilan widget saat ini; jangan menata ulang). Label ikon pixel (bukan emoji), angka persentase, animasi isi halus; warna normal hijau, ≤ 25% terracotta.

## 3. Inventaris dan hotbar
- Domain `src/domain/inventory.js`: `slots` (default 5), `stackMax` (default 5), `add/remove/use`, validasi bilangan bulat. Tas penuh → pembelian ditolak ("Tas penuh"), tanpa mengurangi saldo.
- **Hotbar kecil di bawah-tengah** layar, gaya mengikuti `docs/reference/hotbar-reference.png` (slot krem berbingkai); tiap slot: ikon item (skala bilangan bulat), lencana jumlah kanan-bawah, nomor slot kecil, fokus/hover menampilkan tooltip (nama, efek energi, durasi makan).
- **Pakai item:** klik/ketuk slot atau tombol 1–5. Efek: animasi konsumsi singkat (ikon naik ke arah karakter lalu memudar, teks mengambang "+N Energi"), bar energi terisi halus, waktu maju `consumeMinutes` lewat `advanceTime` (2–5 menit), jumlah slot berkurang. Dinonaktifkan saat dialog/TimeSkip/transisi; item energi-only dengan energi ≥ 95% menampilkan pesan dan tidak terkonsumsi.
- Hotbar disembunyikan di layar dialog; dapat dioperasikan keyboard; teks tooltip lewat `textContent`.
- Save v3: `inventory: [{itemId, count}]`, validasi skema (itemId harus ada di katalog); migrasi dari v2 = tas kosong.

## 4. Katalog item (`data/items.phase1.json`, gabungkan dengan data belanja yang sudah ada)
Default: air_mineral (Rp3.000, +5), isotonik (Rp8.000, +15), nasi_goreng (Rp15.000, +40), mie_goreng (Rp12.000, +35), nasi_kuning (kantin, Rp10.000, +30), bakso (kantin, Rp12.000, +30), roti_isi (Rp7.000, +20), pisang (Rp5.000, +12), keripik (Rp8.000, +10), gorengan (kantin, Rp5.000, +10), mie_cup (Rp6.000, +15), susu_kotak (Rp6.000, +12), teh_kemasan (Rp5.000, +8), jus_kotak (Rp7.000, +12), es_teh (kantin, Rp3.000, +5), coklat_batang (Rp10.000, +8). Tiap item: `id, label, price, energy, consumeMinutes, stackMax, sellAt[], category (kebutuhan|keinginan), iconAsset`. Item lama (mis. "camilan") dipetakan ke item baru; catat di `DECISIONS.md`.
- **Minimarket:** rak/kulkas menjual item → masuk tas. **Kantin:** "makan di tempat" (efek langsung, waktu 10–20 menit) atau bungkus ke tas. **Rumah:** makan di meja makan (ibu), gratis, jam makan sesuai 72.
- Transaksi tetap lewat ledger (kategori Beban Jajan/Makanan) dan tampil di buku kas.

## 5. Aset item
Ikon 32×32 untuk 16 item dari sheet grid (`data/asset-briefs-v4.json` → `item_icon_sheet`), tanpa teks/merek pada kemasan, gaya sama dengan ikon UI. Placeholder berlabel bila gagal QA.

## 6. Uji wajib
Penguras pasif dan biaya aktivitas benar per jam (belajar 1 jam → −10 − pasif); makan rumah +40 dan waktu maju; item dari minimarket → tas → dipakai → energi naik, jumlah turun, saldo benar di ledger; tas penuh menolak pembelian; energi 0% menonaktifkan aktivitas berat; hotbar via klik dan tombol 1–5; save/load mempertahankan energi dan tas; tangkapan layar hotbar dan bar energi pada desktop dan tablet.


## 7. Pembaruan v5
Bagian inventaris (§3) **digantikan oleh `80-inventory-backpack-item-actions.md`** (hotbar 5 + ransel 20, pengisian otomatis, popup aksi). Bagian katalog item (§4) dilengkapi `79-shop-and-vendors.md` dan `data/items-types.v5.json`; katalog **harus selaras dengan ikon yang ada**. Pembelian wajib masuk ke inventaris lewat `inventory.add` (atomik dengan ledger).

## 8. Pembaruan v6
Bagian energi (§1) **digantikan oleh `83-energy-v2.md`**: biaya per aktivitas (pelajaran −20%, game center −20%/jam), peringatan teks di bawah 50%, dan energi 0 = pingsan lalu bangun kesiangan di hari berikutnya (bukan penonaktifan aktivitas). Bagian inventaris tetap mengikuti rule 80.
