# ACCEPTANCE-V6-RESULTS — Matriks Hasil Penerimaan V6

> Diisi baris per baris dengan bukti. Semua pengujian aksi wajib melalui **UI nyata** (pointer/keyboard), bukan hook debug (Rule 78). Status: PASS / FAIL / BELUM.

| ID | Permintaan Pengguna | Uji UI Nyata / Validator | Hasil yang Diharapkan | Status | Nama Tes / Bukti | Tangkapan Layar |
|---|---|---|---|---|---|---|
| B1 | Kursi dan meja sekolah menghadap benar (dari belakang/depan), tidak serong | Audit frontalitas + tangkapan layar kelas, kantin, perpustakaan | Semua `front/back` memiliki IoU simetri ≥ 0,80; set komposit; tinjauan visual | BELUM | Menunggu Gate J3 & J4 | `docs/regression/b1_kursi_meja_sekolah_red.png` |
| B2 | Meja guru dan papan tulis frontal | Kelas: tangkapan layar + frontalitas | Tidak miring | BELUM | Menunggu Gate J3 & J4 | `docs/regression/b2_meja_guru_papan_tulis_red.png` |
| B3 | Meja dan bangku kantin benar | Kantin: tangkapan layar + audit | Set komposit frontal; tidak melintasi dinding | BELUM | Menunggu Gate J3 & J4 | `docs/regression/b3_meja_bangku_kantin_red.png` |
| B4 | Tidak ada furnitur menembus dinding | `layout-check` batas ruang (6 peta, 131 furnitur) | 0 pelanggaran footprint/piksel di luar ruang | PASS | `tools/test_j1_green.py` (verify_b4_layouts) · [Laporan](docs/regression/b4-green.md) | `docs/regression/b4_furnitur_tembus_dinding_red.png` |
| B5 | Nama berkas = isi gambar (bak mandi, rak piring dapur, jendela dapur, dst.) | Identity report seluruh furnitur | 0 ketidakcocokan; `identityVerified` semua `ready` | BELUM | Menunggu Gate J3 & J4 | `docs/regression/b5_identitas_aset_tertukar_red.png` |
| B6 | Wastafel/toilet perspektif konsisten | Kamar mandi: frontalitas + tangkapan layar | Semua frontal, posisi konsisten | BELUM | Menunggu Gate J3 & J4 | `docs/regression/b6_wastafel_toilet_red.png` |
| B7 | Tekan E dekat Ibu → bicara dengan Ibu (bukan furnitur) | Dari titik berdiri dekat Ibu, tekan E nyata | Dialog Ibu terbuka; `findBestInteractionTarget` +20px NPC bonus | PASS | `tools/test_j1_green.py` · [Laporan](docs/regression/b7-green.md) | `docs/regression/b7_interaksi_dapur_ibu_green.png` |
| B8 | Rak buku kelas di sudut kiri ruangan | Kelas: posisi di layout + tangkapan layar | Pojok kiri-belakang pada (x=2, y=2), di dalam lantai | PASS | `tools/test_j1_green.py` · [Laporan](docs/regression/b8-green.md) | `docs/regression/b8_rak_buku_kelas_green.png` |
| B9 | Tidak ada motor di ruang kelas | Bermotor → masuk sekolah → keluar | Interior tanpa motor; motor di hub depan pintu | PASS | `tools/test_j1_green.py` · [Laporan](docs/regression/b9-green.md) | `docs/regression/b9_motor_di_kelas_green.png` |
| B10 | Energi: pelajaran −20%, game center −20%, aktivitas lain realistis | `advanceTime`/UI: kelas penuh, 1 jam game, tiap baris tabel | Sesuai tabel rule 83 | PASS | `tools/test_j2_green.py` · [Laporan](docs/regression/b10-green.md) | `docs/regression/b10_biaya_energi_green.png` |
| B11 | Peringatan < 50% | Turunkan energi lewat aktivitas nyata | Teks persis "Energi kamu di bawah 50%, silakan makan untuk menambahnya." sekali; aktif lagi ≥ 60% | PASS | `tools/test_j2_green.py` · [Laporan](docs/regression/b11-green.md) | `docs/regression/b11_peringatan_energi_50_green.png` |
| B12 | Energi habis → bangun kesiangan hari berikutnya | Habiskan energi lewat UI | Bangun di kasur 10:00 hari berikutnya, energi 50%, kehadiran terlewat tercatat | PASS | `tools/test_j2_green.py` · [Laporan](docs/regression/b12-green.md) | `docs/regression/b12_bangun_kesiangan_green.png` |
| B13 | Budi bergaya piksel, lebih menarik, bukan kartun | Audit gaya NPC + tinjauan visual | Ukuran piksel ±25% pemain, tanpa alfa parsial, konsisten potret | BELUM | Menunggu Gate J3 & J4 | `docs/regression/b13_sprite_budi_kartun_red.png` |
| B14 | Katalog toko punya tombol keluar | Tiap toko: X, Esc, klik luar | Panel menutup; input dan jam melanjutkan | PASS | `tools/test_j1_green.py` · [Laporan](docs/regression/b14-green.md) | `docs/regression/b14_katalog_minimarket_exit_green.png` |
| B15 | Katalog menampilkan NPC kasir (kantin, minimarket, kosmetik, game center, SPBU) | Buka tiap toko | Potret vendor benar + sapaan/reaksi | PASS | `tools/test_j1_green.py` · [Laporan](docs/regression/b15-green.md) | `docs/regression/b15_vendor_minimarket_green.png` |
| B16 | Tutorial wajib pertama kali dengan panah + teks panduan, mencakup semua bangunan | E2E UI nyata dari Permainan Baru sampai T20 | Semua langkah tuntas; panah, panel objektif, highlight HUD, petunjuk tombol tampil; resume setelah muat ulang; tidak muncul lagi; save lama tanpa tutorial | BELUM | Menunggu Gate J6 | `docs/regression/b16_tutorial_red.png` |
| B17 | Regresi nol | Semua tes lama + V5 + E2E multi-hari UI nyata | Hijau; daftar tes berhook dilaporkan | BELUM | Menunggu seluruh gerbang selesai | - |

**Ringkasan Status Saat Ini:**
- **PASS (9/17):** B4, B7, B8, B9, B10, B11, B12, B14, B15
- **BELUM (8/17):** B1, B2, B3, B5, B6, B13, B16, B17
- Gerbang J2 SELESAI (100% sistem Energi v2 terverifikasi hijau). Siap lanjut ke Gerbang J3 & J4 (Audit & Regenerasi Aset -> Checkpoint E).
