# ACCEPTANCE-V6-RESULTS — Matriks Hasil Penerimaan V6

> Diisi baris per baris dengan bukti. Semua pengujian aksi wajib melalui **UI nyata** (pointer/keyboard), bukan hook debug (Rule 78). Status: PASS / FAIL / BELUM.

| ID | Permintaan Pengguna | Uji UI Nyata / Validator | Hasil yang Diharapkan | Status | Nama Tes / Bukti | Tangkapan Layar |
|---|---|---|---|---|---|---|
| B1 | Kursi dan meja sekolah menghadap benar (dari belakang/depan), tidak serong | Audit frontalitas + tangkapan layar kelas, kantin, perpustakaan | Semua `front/back` memiliki IoU simetri ≥ 0,80; set komposit; tinjauan visual | BELUM | J0: RED terbukti serong | `docs/regression/b1_kursi_meja_sekolah_red.png` |
| B2 | Meja guru dan papan tulis frontal | Kelas: tangkapan layar + frontalitas | Tidak miring | BELUM | J0: RED terbukti miring | `docs/regression/b2_meja_guru_papan_tulis_red.png` |
| B3 | Meja dan bangku kantin benar | Kantin: tangkapan layar + audit | Set komposit frontal; tidak melintasi dinding | BELUM | J0: RED terbukti serong & melintasi dinding | `docs/regression/b3_meja_bangku_kantin_red.png` |
| B4 | Tidak ada furnitur menembus dinding | `layout-check` batas ruang (7 peta) | 0 pelanggaran footprint/piksel di luar ruang | BELUM | J0: RED pelanggaran batas ruang terdeteksi | `docs/regression/b4_furnitur_tembus_dinding_red.png` |
| B5 | Nama berkas = isi gambar (bak mandi, rak piring dapur, jendela dapur, dst.) | Identity report seluruh furnitur | 0 ketidakcocokan; `identityVerified` semua `ready` | BELUM | J0: RED bak mandi berisi rak piring | `docs/regression/b5_identitas_aset_tertukar_red.png` |
| B6 | Wastafel/toilet perspektif konsisten | Kamar mandi: frontalitas + tangkapan layar | Semua frontal, posisi konsisten | BELUM | J0: RED toilet & wastafel serong | `docs/regression/b6_wastafel_toilet_red.png` |
| B7 | Tekan E dekat Ibu → bicara dengan Ibu (bukan furnitur) | Dari 3 titik berdiri dekat Ibu, tekan E nyata | Dialog Ibu terbuka; `interactionOverlapCheck` hijau | BELUM | J0: RED tekan E memicu counter kompor | `docs/regression/b7_interaksi_ibu_dapur_red.png` |
| B8 | Rak buku kelas di sudut kiri ruangan | Kelas: posisi di layout + tangkapan layar | Pojok kiri-belakang, di dalam lantai | BELUM | J0: RED rak buku di tengah dinding kiri | `docs/regression/b8_rak_buku_kelas_red.png` |
| B9 | Tidak ada motor di ruang kelas | Bermotor → masuk sekolah → keluar | Interior tanpa motor; motor di hub depan pintu | BELUM | J0: RED sprite motor muncul di kelas | `docs/regression/b9_motor_di_kelas_red.png` |
| B10 | Energi: pelajaran −20%, game center −20%, aktivitas lain realistis | `advanceTime`/UI: kelas penuh, 1 jam game, tiap baris tabel | Sesuai tabel rule 83 | BELUM | J0: RED biaya aktivitas lama | `docs/regression/b10_biaya_energi_red.png` |
| B11 | Peringatan < 50% | Turunkan energi lewat aktivitas nyata | Teks persis "Energi kamu di bawah 50%, silakan makan untuk menambahnya." sekali; aktif lagi ≥ 60% | BELUM | J0: RED teks peringatan 50% belum ada | `docs/regression/b11_peringatan_energi_50_red.png` |
| B12 | Energi habis → bangun kesiangan hari berikutnya | Habiskan energi lewat UI | Bangun di kasur 10:00 hari berikutnya, energi 50%, kehadiran terlewat tercatat | BELUM | J0: RED belum bangun kesiangan | `docs/regression/b12_bangun_kesiangan_red.png` |
| B13 | Budi bergaya piksel, lebih menarik, bukan kartun | Audit gaya NPC + tinjauan visual | Ukuran piksel ±25% pemain, tanpa alfa parsial, konsisten potret | BELUM | J0: RED sprite Budi kartun | `docs/regression/b13_sprite_budi_kartun_red.png` |
| B14 | Katalog toko punya tombol keluar | Tiap toko: X, Esc, klik luar | Panel menutup; input dan jam melanjutkan | BELUM | J0: RED toko tidak ada tombol keluar X / Esc | `docs/regression/b14_toko_tanpa_tombol_keluar_red.png` |
| B15 | Katalog menampilkan NPC kasir (kantin, minimarket, kosmetik, game center, SPBU) | Buka tiap toko | Potret vendor benar + sapaan/reaksi | BELUM | J0: RED panel toko tanpa potret NPC vendor | `docs/regression/b15_toko_tanpa_vendor_red.png` |
| B16 | Tutorial wajib pertama kali dengan panah + teks panduan, mencakup semua bangunan | E2E UI nyata dari Permainan Baru sampai T20 | Semua langkah tuntas; panah, panel objektif, highlight HUD, petunjuk tombol tampil; resume setelah muat ulang; tidak muncul lagi; save lama tanpa tutorial | BELUM | J0: RED tutorial belum diaktifkan | `docs/regression/b16_tutorial_red.png` |
| B17 | Regresi nol | Semua tes lama + V5 + E2E multi-hari UI nyata | Hijau; daftar tes berhook dilaporkan | BELUM | Menunggu seluruh gerbang selesai | - |

**Ringkasan Status Saat Ini:**
- **PASS (0/17):** -
- **BELUM (17/17):** B1 sampai B17
- Gerbang J0 sedang berlangsung.
