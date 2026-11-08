---
trigger: model_decision
description: "Terapkan saat mengimplementasikan gameplay, angka ekonomi, kejadian, misi, dialog, konten edukasi, penilaian, atau alur Fase 1 (Kehidupan SMA)."
---

# 40 · Desain Game Fase 1: Kehidupan SMA

> Semua angka di bawah adalah **default** untuk `data/phase1.config.json`. Ubah di data, bukan di kode.

## 1. Premis & tujuan belajar
Karakter adalah siswa SMA yang tinggal bersama orang tua. Kebutuhan dasar (tempat tinggal, makan di rumah, listrik, air) ditanggung orang tua. Pemain menerima **uang saku Rp1.000.000/bulan** dan menentukan pengeluaran pribadi.
Tujuan belajar: (1) membedakan kebutuhan dan keinginan; (2) mencatat pemasukan dan pengeluaran; (3) membuat anggaran sederhana; (4) membentuk kebiasaan menabung; (5) memahami bahwa pengeluaran kecil berulang terakumulasi.

## 2. Parameter default
- Durasi Fase 1: `months` (default 2) × 30 hari. Pengaturan waktu mengikuti `72-time-system.md` (siklus 24 jam, aktivitas memakan waktu); total waktu bermain jauh lebih panjang daripada versi lama, jadi untuk demo kompetisi disarankan `months: 1`.
- Uang saku: Rp1.000.000 pada hari ke-1 tiap bulan. Saldo awal Kas Rp0 sebelum uang saku pertama; Tabungan awal Rp0.
- Bensin: indikator 0–100%; **turun hanya saat bermotor** (per 5 detik penggunaan, lihat `75-vehicle-motor.md`; penurunan harian lama dihapus); isi Rp20.000 = +40%. Bensin 0% → pengendara dipaksa turun dan tombol motor nonaktif hingga diisi. Energi pemain (rule 74): 0–100, turun karena aktivitas, terisi dengan makan/minum/tidur.
- Kenaikan nominal beli kelipatan Rp5.000; tabung kelipatan Rp10.000.
- Anggaran saran bulanan: Tabungan 100.000 · Jajan 250.000 · Bensin 100.000 · Kebutuhan sekolah 100.000 · Perawatan diri 100.000 · Hiburan 150.000 · Cadangan 200.000 (total 1.000.000). Anggaran awal kosong; tombol "Gunakan saran". Anggaran **memperingatkan**, tidak memblokir.

## 3. Lokasi dan interaksi (ID lokasi → panel)
Setiap lokasi adalah **bangunan di peta hub dengan peta interior yang dapat dijelajahi** (lihat `70-interior-maps-and-buildings.md`); pemain benar-benar masuk, dan transaksi hanya terjadi pada titik interaksi spesifik di dalamnya (mis. belanja makan/jajan hanya di konter kantin). Permainan dimulai di dalam rumah pemain.
| Lokasi | Interaksi | Kategori |
|---|---|---|
| Rumah | tidur, celengan (tabung/tarik), anggaran bulanan, ngobrol dengan ibu/ayah | tabungan |
| Kantin sekolah | makan siang Rp10.000; jajan Rp5.000; minuman Rp5.000 | jajan |
| Minimarket "Mini Mart Harapan" | alat tulis Rp15.000; fotokopi Rp5.000; paket kuota Rp15.000/Rp35.000; camilan Rp8.000 | sekolah, komunikasi, jajan |
| Toko kosmetik "Toko Cantik Sari" | lip tint Rp35.000; skincare Rp75.000 | perawatan diri |
| SPBU mini | isi bensin Rp20.000 | transportasi |
| Game center / kafe | game 1 jam Rp10.000; nonton Rp40.000; nongkrong Rp30.000 | hiburan |
Klasifikasi default: kebutuhan = makan siang, bensin, alat tulis, fotokopi, kuota hemat, iuran; keinginan = jajan camilan, kosmetik, hiburan, kuota besar.

## 4. Kejadian default (muncul 5–6 per bulan; seed menentukan urutan)
| ID | Situasi | Pilihan → dampak | Tag belajar |
|---|---|---|---|
| E01 teman_ajak_jajan | Teman mengajak jajan Rp5.000 (repeatable) | Ikut: −5.000 jajan / Tolak: 0, catat "disiplin" | pengeluaran kecil berulang |
| E02 bensin_menipis | Bensin ≤ 20% | Isi: −20.000 / Tunda: motor mogok, ojek −15.000 | menunda kebutuhan bisa lebih mahal |
| E03 iuran_kelas | Iuran mendadak Rp25.000 | Bayar dari kas / Ambil dari tabungan / Minta tunda 1 minggu (wajib dibayar) | dana darurat |
| E04 promo_kosmetik | Diskon 30% skincare (Rp75.000 → Rp52.500) | Beli / Lewati / Tunda sampai akhir bulan (promo hilang) | diskon ≠ kebutuhan |
| E05 ajakan_nonton | Ajakan nonton Rp40.000 | Ikut / Usul nongkrong gratis di taman / Tolak | alternatif hemat |
| E06 kuota_habis | Kuota habis | Paket hemat −15.000 / Paket besar −35.000 / Wi-Fi sekolah (gratis, terbatas) | membandingkan opsi |
| E07 ulang_tahun_teman | Teman ulang tahun | Kado −30.000 / Kado buatan sendiri −10.000 / Tanpa kado | anggaran sosial |
| E08 bonus_nilai | Orang tua beri bonus Rp50.000 (positif) | Simpan semua / Simpan setengah / Pakai semua | perilaku saat uang tambahan |
| E09 turnamen_game | Pendaftaran turnamen Rp15.000 | Ikut / Tonton saja | hiburan terkendali |
| E10 teman_pinjam | Teman pinjam Rp20.000, janji kembali 1 minggu | Pinjamkan (RNG ber-seed, 70% kembali) / Tolak sopan / Beri Rp10.000 | risiko meminjamkan uang |
| E11 barang_rusak | Charger/sepatu rusak | Perbaiki −30.000 / Beli baru −60.000 / Tunda (mengganggu) | pengeluaran tak terduga |
Setiap pilihan menampilkan: dampak langsung (angka), dampak jangka panjang (teks singkat), dan tag belajar. Pembelian ditolak bila Kas kurang, dengan pesan edukatif.

## 5. Misi aktif (HUD menampilkan satu misi utama + progres)
M1 Terima uang saku & lihat buku kas · M2 Susun anggaran bulan ini · M3 Isi bensin sebelum 20% · M4 Tabung minimal Rp100.000 bulan ini · M5 Hadapi satu ajakan teman · M6 Pertahankan Kas > Rp0 sampai akhir bulan · M7 Tinjau ringkasan akhir bulan.

## 6. Dashboard (buku kas pribadi)
Saldo kas, tabungan, total pemasukan, total pengeluaran, pengeluaran per kategori (batang CSS sederhana, bukan pustaka grafik), rasio kebutuhan:keinginan, riwayat transaksi (filter kategori), anggaran vs realisasi, sisa hari bulan ini. Semua dari ledger.

## 7. Evaluasi akhir bulan dan akhir Fase 1
- Ringkasan bulanan: pemasukan, pengeluaran per kategori, tabungan, kepatuhan anggaran, 1–2 umpan balik personal.
- Akhir Fase 1: `savingsRate = tabunganAkhir / totalPemasukan`, `wantsRatio`, `budgetAdherence`, keputusan kunci. Peringkat (ambang di config): ≥15% **Sangat Baik**, 8–15% **Cukup Baik**, <8% **Perlu Berlatih** (label netral, tidak menghakimi).
- Simpan `phase1Result` {tabunganAkhir, savingsRate, wantsRatio, budgetAdherence, rating, keyDecisions[]} untuk dibaca Fase 2. Fase 2 belum ada: tampilkan layar "Bersambung" + ringkasan.

## 8. Pembuatan karakter
Alur: pilih laki-laki/perempuan → nama karakter → nama ayah → nama ibu. Nama teman diminta saat teman pertama kali muncul. Validasi sesuai `50-security.md`. Pratinjau memakai sprite asli dari manifest.

## 9. Nada teks
Bahasa Indonesia santai, sopan, edukatif tanpa menggurui. Dialog ≤ 140 karakter per kotak. Tidak ada merek nyata. Konten bersifat inklusif untuk semua gender (kategori "perawatan diri", bukan "makeup wanita").
