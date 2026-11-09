# AUDIT-V6 — Hasil Audit Menyeluruh V6 (Gerbang J0)
**Tanggal Audit:** 9 November 2026

## 1. Audit Perspektif & Identitas Furnitur (Rule 85)
- **Total Aset Furnitur Diperiksa:** 126
- **Pelanggar Frontalitas (IoU < 0.80 / Serong):** 59 aset
  - `furn_kursi_belajar` (assets/furniture/kamar_pemain/furn_kursi_belajar.png): IoU = 0.703 (serong/asimetris)
  - `furn_karpet_tamu` (assets/furniture/home/furn_karpet_tamu.png): IoU = 0.735 (serong/asimetris)
  - `furn_kompor_counter` (assets/furniture/home/furn_kompor_counter.png): IoU = 0.7 (serong/asimetris)
  - `furn_kursi_makan` (assets/furniture/home/furn_kursi_makan.png): IoU = 0.53 (serong/asimetris)
  - `furn_kursi_makan_kiri` (assets/furniture/home/furn_kursi_makan_kiri.png): IoU = 0.58 (serong/asimetris)
  - `furn_rak_piring` (assets/furniture/home/furn_rak_piring.png): IoU = 0.73 (serong/asimetris)
  - `furn_wastafel_dapur` (assets/furniture/home/furn_wastafel_dapur.png): IoU = 0.648 (serong/asimetris)
  - `furn_toilet` (assets/furniture/home/furn_toilet.png): IoU = 0.482 (serong/asimetris)
  - `furn_wastafel_cermin` (assets/furniture/home/furn_wastafel_cermin.png): IoU = 0.515 (serong/asimetris)
  - `furn_rak_handuk` (assets/furniture/home/furn_rak_handuk.png): IoU = 0.52 (serong/asimetris)
  - `furn_meja_siswa_kursi` (assets/furniture/school/furn_meja_siswa_kursi.png): IoU = 0.698 (serong/asimetris)
  - `furn_meja_guru` (assets/furniture/school/furn_meja_guru.png): IoU = 0.7 (serong/asimetris)
  - `furn_papan_tulis` (assets/furniture/school/furn_papan_tulis.png): IoU = 0.544 (serong/asimetris)
  - `furn_poster_kosong` (assets/furniture/school/furn_poster_kosong.png): IoU = 0.592 (serong/asimetris)
  - `furn_counter_kantin` (assets/furniture/school/furn_counter_kantin.png): IoU = 0.678 (serong/asimetris)
  - *... dan 44 aset lainnya*

- **Pelanggar Identitas (Nama Berkas Tidak Cocok Isi Gambar):** 2 aset
  - `furn_rak_piring` (assets/furniture/home/furn_rak_piring.png): Berisi jendela berbingkai kayu gorden hijau, bukan rak piring.
  - `furn_bak_mandi` (assets/furniture/home/furn_bak_mandi.png): Berisi rak piring (dish rack), bukan bak mandi air.

## 2. Audit Batas Ruang Peta (Rule 73 §9 & Rule 85 §3)
- **Total Pelanggaran Batas Ruang Terdeteksi:** 2 furnitur menembus dinding
  - **Peta `school`** -> `slot_sch_bangku_kantin_1b` (x=18, y=10): Bottom (11) exceeds room floor bottom (10) by 1 tiles (tembus dinding bawah/koridor)
  - **Peta `school`** -> `slot_sch_bangku_kantin_2b` (x=23, y=10): Bottom (11) exceeds room floor bottom (10) by 1 tiles (tembus dinding bawah/koridor)

## 3. Audit Gaya Sprite NPC (Rule 85 §4)
- **Sprite Budi Saat Ini (`npc_budi.png`):** Ukuran (32, 64), 1 frame statis chibi.
- **Karakter Pemain (`char_player_m_casual.png`):** Ukuran (96, 64), 3 arah (front, back, left) 32x64.
- **Temuan Masalah:** Sprite Budi memiliki proporsi kepala terlalu besar (gaya anime/vektor halus), tanpa outline piksel 1px yang konsisten dengan pemain, dan tidak memiliki animasi arah jalan/berdiri.

## 4. Asal Sprite Motor di Ruang Kelas (Rule 75 §6)
- **Akar Masalah:** Di `src/game/scenes/World.js` baris 504, saat pemain masuk pintu sekolah dalam keadaan berkendara, `_spawnParkedMotor(parkX, parkY)` dipanggil langsung pada scene Phaser aktif tanpa membersihkan sprite saat transisi peta.
- Sprite `_parkedMotorProp` tidak ditambahkan ke `_mapObjects` di `MapManager.js`, sehingga tetap hidup di koordinat yang sama di dalam interior sekolah (`school`).
- Selain itu, state `vehicle.parked` tidak memeriksa `mapId === currentMapId` sebelum merender.

## 5. Bentrok Interaksi Ibu di Dapur (Rule 84)
- **Akar Masalah:** Posisi Ibu berada di `(x=20, y=13.5)`. Tepat di depannya terdapat interactable `int_dapur` (`x=18.5..21.5, y=12..13`) dan furnitur `fur_kompor_counter` (`collidable: true`).
- Fungsi `_checkInteractables()` di `World.js` memilih kandidat pertama dari array tanpa memperhitungkan bobot NPC (+20px) maupun arah hadap, sehingga pemain yang menekan `E` di dekat Ibu malah memicu memasak di kompor.

## 6. Panel Toko: Tombol Keluar & Kehadiran Vendor (Rule 86)
- **Akar Masalah:**
  1. Modal toko tidak menutup saat tombol `Esc` ditekan (`keydown` listener hilang).
  2. Klik pada backdrop luar modal tidak menutup panel (`closeOnOutsideClick` belum aktif).
  3. Potret vendor hanya berupa thumbnail kecil di subhead (`shop-vendor-img`), belum berupa potret besar 192x256 di sisi kiri (`vendorSide: 'left'`) dengan plakat nama dan gelembung ucapan dinamis.

## 7. Sistem Energi v2 (Rule 83)
- **Akar Masalah:**
  1. Biaya pelajaran sekolah masih dihitung 5% per jam (total 37.5%), belum disesuaikan ke tepat −20% (Sesi 1: −9%, Sesi 2: −11%).
  2. Game center belum −20% per jam.
  3. Peringatan < 50% belum ada dengan teks persis: `"Energi kamu di bawah 50%, silakan makan untuk menambahnya."`.
  4. Saat energi 0%, game belum membuat pemain pingsan dan bangun di kasur pukul 10:00 (kesiangan) pada hari berikutnya dengan penambahan `attendanceMissed`.

## 8. Tutorial Berpemandu & Cerita Hari Pertama (Rule 82)
- **Akar Masalah:**
  1. Sistem misi hanya berupa pelacak pasif 5 misi (`M1–M5`), belum memiliki alur tutorial 20 langkah (`T01–T20`) yang memandu pemain ke semua bangunan.
  2. Belum ada panah pemandu melayang di atas target maupun di tepi layar.
  3. Jam belum dijeda (`realtimeClock: 'paused'`) selama tutorial aktif.
  4. Pintu bangunan belum memiliki soft-lock yang mencegah urutan tutorial dilompati.
