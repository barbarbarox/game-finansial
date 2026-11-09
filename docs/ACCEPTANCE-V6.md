# ACCEPTANCE-V6 — matriks penerimaan (permintaan pengguna → uji → bukti)

> Salin ke `docs/ACCEPTANCE-V6-RESULTS.md`; isi Status (PASS/FAIL/BELUM), nama tes, bukti. **PASS hanya sah dengan bukti**; uji aksi lewat UI nyata (rule 78). Dilarang menulis "selesai/100%" bila ada baris non-PASS.

| ID | Permintaan pengguna | Uji | Hasil yang diharapkan | Bukti |
|---|---|---|---|---|
| B1 | Kursi dan meja sekolah menghadap benar (dari belakang/depan), tidak serong | Audit frontalitas + tangkapan layar kelas, kantin, perpustakaan | Semua `front/back` memiliki IoU simetri ≥ 0,80; set komposit; tinjauan visual | laporan audit + tangkapan layar |
| B2 | Meja guru dan papan tulis frontal | Kelas: tangkapan layar + frontalitas | Tidak miring | tangkapan layar |
| B3 | Meja dan bangku kantin benar | Kantin: tangkapan layar + audit | Set komposit frontal; tidak melintasi dinding | tangkapan layar |
| B4 | Tidak ada furnitur menembus dinding | `layout-check` batas ruang (7 peta) | 0 pelanggaran footprint/piksel di luar ruang | VALIDATION-*.md |
| B5 | Nama berkas = isi gambar (bak mandi, rak piring dapur, jendela dapur, dst.) | Identity report seluruh furnitur | 0 ketidakcocokan; `identityVerified` semua `ready` | IDENTITY-REPORT.md + contact sheet |
| B6 | Wastafel/toilet perspektif konsisten | Kamar mandi: frontalitas + tangkapan layar | Semua frontal, posisi konsisten | tangkapan layar |
| B7 | Tekan E dekat Ibu → bicara dengan Ibu (bukan furnitur) | Dari 3 titik berdiri dekat Ibu, tekan E nyata | Dialog Ibu terbuka; `interactionOverlapCheck` hijau | log + tangkapan layar |
| B8 | Rak buku kelas di sudut kiri ruangan | Kelas: posisi di layout + tangkapan layar | Pojok kiri-belakang, di dalam lantai | tangkapan layar |
| B9 | Tidak ada motor di ruang kelas | Bermotor → masuk sekolah → keluar | Interior tanpa motor; motor di hub depan pintu | tangkapan layar |
| B10 | Energi: pelajaran −20%, game center −20%, aktivitas lain realistis | `advanceTime`/UI: kelas penuh, 1 jam game, tiap baris tabel | Sesuai tabel rule 83 | log energi |
| B11 | Peringatan < 50% | Turunkan energi lewat aktivitas nyata | Teks persis "Energi kamu di bawah 50%, silakan makan untuk menambahnya." sekali; aktif lagi ≥ 60% | tangkapan layar |
| B12 | Energi habis → bangun kesiangan hari berikutnya | Habiskan energi lewat UI | Bangun di kasur 10:00 hari berikutnya, energi 50%, kehadiran terlewat tercatat | log + tangkapan layar |
| B13 | Budi bergaya piksel, lebih menarik, bukan kartun | Audit gaya NPC + tinjauan visual | Ukuran piksel ±25% pemain, tanpa alfa parsial, konsisten potret | audit + tangkapan layar |
| B14 | Katalog toko punya tombol keluar | Tiap toko: X, Esc, klik luar | Panel menutup; input dan jam melanjutkan | tangkapan layar + log |
| B15 | Katalog menampilkan NPC kasir (kantin, minimarket, kosmetik, game center, SPBU) | Buka tiap toko | Potret vendor benar + sapaan/reaksi | tangkapan layar tiap toko |
| B16 | Tutorial wajib pertama kali dengan panah + teks panduan, mencakup semua bangunan | E2E UI nyata dari Permainan Baru sampai T20 | Semua langkah tuntas; panah, panel objektif, highlight HUD, petunjuk tombol tampil; resume setelah muat ulang; tidak muncul lagi; save lama tanpa tutorial | tangkapan layar per langkah |
| B17 | Regresi nol | Semua tes lama + V5 + E2E multi-hari UI nyata | Hijau; daftar tes berhook dilaporkan | log tes |
