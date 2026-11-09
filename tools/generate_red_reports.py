import os

reg_dir = '/home/abarox/Desktop/prototipe web statis game/game/docs/regression'
os.makedirs(reg_dir, exist_ok=True)

reports = {
    'b1-red.md': """# Reproduksi Masalah B1: Kursi dan Meja Sekolah Digambar Serong
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Buka peta sekolah (`school`), periksa orientasi meja dan kursi siswa di ruang kelas.
- **Hasil Aktual:** Meja dan kursi siswa digambar dalam sudut pandang diagonal/isometrik (IoU simetri = 0.698 < 0.80), bukan tampak depan/belakang komposit.
- **Tangkapan Layar:** `docs/regression/b1_kursi_meja_sekolah_red.png`
- **Akar Masalah:** Generator aset tidak mematuhi kontrak perspektif frontal (Rule 85 §1) dan meja-kursi dipecah menjadi aset terpisah yang tidak sejajar.
""",
    'b2-red.md': """# Reproduksi Masalah B2: Meja Guru dan Papan Tulis Miring
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Buka ruang kelas di `school`, periksa meja guru dan papan tulis di depan kelas.
- **Hasil Aktual:** Meja guru miring menyudut dan papan tulis memiliki bingkai bersudut asimetris (IoU simetri 0.544).
- **Tangkapan Layar:** `docs/regression/b2_meja_guru_papan_tulis_red.png`
- **Akar Masalah:** Prompt generator tidak mewajibkan elevasi frontal murni (front elevation, left-right symmetrical).
""",
    'b3-red.md': """# Reproduksi Masalah B3: Meja dan Bangku Kantin Serong & Melintasi Dinding
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Buka area kantin sekolah (`school`), periksa meja panjang dan bangku kantin.
- **Hasil Aktual:** Meja piknik kantin digambar diagonal, dan bangku kantin bawah ditempatkan di y=10 sehingga melintasi dinding pembatas dan pintu masuk koridor.
- **Tangkapan Layar:** `docs/regression/b3_meja_bangku_kantin_red.png`
- **Akar Masalah:** Meja dan bangku tidak dibuat sebagai satu komposit frontal, serta koordinat slot melampaui batas lantai lantai_kantin.
""",
    'b4-red.md': """# Reproduksi Masalah B4: Furnitur Menembus Dinding Ruangan
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Jalankan validasi batas ruang pada `school.layout.json`.
- **Hasil Aktual:** 4 kursi siswa baris belakang (`kursi_siswa_3a`, `kursi_siswa_3b`, `kursi_siswa_4a`, `kursi_siswa_4b`) ditaruh di y=10.5 dengan dasar y=12.0, menembus dinding kelas y=10 dan berada di koridor.
- **Tangkapan Layar:** `docs/regression/b4_furnitur_tembus_dinding_red.png`
- **Akar Masalah:** Slotting layout tidak memeriksa batas bounding box lantai ruang (`lantai_kelas` y=2..10).
""",
    'b5-red.md': """# Reproduksi Masalah B5: Nama Berkas Tidak Cocok dengan Isi Gambar
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Periksa isi berkas gambar `furn_bak_mandi_v4.png` dan `furn_rak_piring_v4.png`.
- **Hasil Aktual:** Berkas `furn_bak_mandi_v4.png` berisi gambar rak piring (dish rack) dengan piring/cangkir, sedangkan `furn_rak_piring_v4.png` berisi jendela bergorden.
- **Tangkapan Layar:** `docs/regression/b5_identitas_aset_tertukar_red.png`
- **Akar Masalah:** Pemotongan sheet menamai item berdasarkan nomor urut tanpa memverifikasi isi visual terhadap ekspektasi identitas (Rule 85 §2).
""",
    'b6-red.md': """# Reproduksi Masalah B6: Wastafel dan Toilet Perspektif Tidak Konsisten
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Periksa kamar mandi di `home.layout.json`.
- **Hasil Aktual:** Toilet dan wastafel digambar serong/isometrik (IoU toilet = 0.482, wastafel = 0.515), cermin terpisah dan tidak sejajar wastafel.
- **Tangkapan Layar:** `docs/regression/b6_wastafel_toilet_red.png`
- **Akar Masalah:** Tidak ada kontrak sudut pandang frontal untuk perlengkapan sanitasi kamar mandi.
""",
    'b7-red.md': """# Reproduksi Masalah B7: Menekan E Dekat Ibu Memicu Furnitur Dapur
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Pemain berdiri di depan Ibu di dapur (x=20, y=13) menghadap Ibu dan menekan tombol E.
- **Hasil Aktual:** Dialog interaksi yang muncul adalah `int_dapur` ("Tekan [E] Memasak Bersama Ibu") dari kompor dapur, bukan dialog NPC Ibu (`dia_ibu_home`).
- **Tangkapan Layar:** `docs/regression/b7_interaksi_ibu_dapur_red.png`
- **Akar Masalah:** `_checkInteractables()` di `World.js` memilih elemen pertama dalam radius 50px tanpa memprioritaskan NPC (+20px) dan tanpa memperhitungkan arah hadap pemain (Rule 84).
""",
    'b8-red.md': """# Reproduksi Masalah B8: Rak Buku Kelas Tidak di Sudut Kiri Ruangan
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Periksa posisi `slot_sch_rak_buku_kelas` di `school.layout.json`.
- **Hasil Aktual:** Rak buku berada di koordinat x=2, y=4 (di tengah dinding samping kiri), bukan di pojok kiri belakang menempel dinding atas.
- **Tangkapan Layar:** `docs/regression/b8_rak_buku_kelas_red.png`
- **Akar Masalah:** Tata letak kelas menaruh rak buku di lorong samping meja siswa alih-alih di sudut kiri atas ruangan.
""",
    'b9-red.md': """# Reproduksi Masalah B9: Sprite Motor Liar di Ruang Kelas
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Naik motor di `town_hub`, kendarai menuju pintu masuk sekolah SMA Negeri 1, tekan E untuk masuk.
- **Hasil Aktual:** Karakter masuk ke ruang kelas, namun sprite motor parkir (`prop_motor_parkir`) tetap tampil mengambang di lantai kelas pada koordinat sekolah.
- **Tangkapan Layar:** `docs/regression/b9_motor_di_kelas_red.png`
- **Akar Masalah:** `_spawnParkedMotor()` membuat sprite Phaser scene tanpa mengaitkannya ke `mapManager._mapObjects`, dan tidak ada validasi `mapId === currentMapId` saat transisi peta (Rule 75 §6).
""",
    'b10-red.md': """# Reproduksi Masalah B10: Biaya Energi Tidak Sesuai Tabel Realistis
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Hitung biaya energi untuk aktivitas `ikut_pelajaran` dan `main_game`.
- **Hasil Aktual:** `ikut_pelajaran` menguras 5% per jam (total 37.5% untuk 7.5 jam), bukan tepat -20% proporsional Sesi 1/2.
- **Tangkapan Layar:** `docs/regression/b10_biaya_energi_red.png`
- **Akar Masalah:** `src/domain/energy.js` masih memakai tarif lama Rule 74, belum mengadopsi tarif `v6.config.additions.json` (Rule 83 §1).
""",
    'b11-red.md': """# Reproduksi Masalah B11: Peringatan Energi di Bawah 50% Belum Ada
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Turunkan energi pemain menjadi 48%.
- **Hasil Aktual:** Tidak ada toast/banner peringatan teks yang muncul pada layar HUD.
- **Tangkapan Layar:** `docs/regression/b11_peringatan_energi_50_red.png`
- **Akar Masalah:** Ambang batas peringatan di HUD sebelumnya hanya pada 25% dan 10%, belum ada pendeteksi ambang <50% dengan teks persis "Energi kamu di bawah 50%, silakan makan untuk menambahnya." (Rule 83 §2).
""",
    'b12-red.md': """# Reproduksi Masalah B12: Energi 0% Belum Membangunkan Kesiangan Pukul 10:00
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Habiskan energi pemain menjadi 0%.
- **Hasil Aktual:** Pemain hanya mendapatkan pengurangan kecepatan gerak, tidak terjadi pingsan, dan pemain tidak terbangun di kasur pukul 10:00 hari berikutnya.
- **Tangkapan Layar:** `docs/regression/b12_bangun_kesiangan_red.png`
- **Akar Masalah:** Sistem exhaustion belum mengimplementasikan sekuens pingsan dan lompat waktu `advanceTime` ke hari berikutnya pukul 10:00 (Rule 83 §3).
""",
    'b13-red.md': """# Reproduksi Masalah B13: Sprite NPC Budi Bergaya Kartun
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Bandingkan berkas `assets/npcs/npc_budi.png` dengan `assets/characters/char_player_m_casual.png`.
- **Hasil Aktual:** Budi digambar dalam proporsi kepala terlalu besar (chibi/vektor kartun), hanya 1 frame statis, tanpa outline piksel retro 1px konsisten dengan pemain.
- **Tangkapan Layar:** `docs/regression/b13_sprite_budi_kartun_red.png`
- **Akar Masalah:** Prompt generasi sprite Budi di v4 menghasilkan gaya kartun anime halus alih-alih sprite piksel 32x64 3-arah (Rule 85 §4).
""",
    'b14-red.md': """# Reproduksi Masalah B14: Panel Toko Tidak Memiliki Penutup Luar / Esc
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Buka panel toko (atau SPBU), klik area backdrop di luar modal atau tekan Escape.
- **Hasil Aktual:** Backdrop modal tidak memiliki event handler `click` untuk menutup panel, dan pada menu SPBU tombol Escape tidak menutup modal.
- **Tangkapan Layar:** `docs/regression/b14_toko_tanpa_tombol_keluar_red.png`
- **Akar Masalah:** `closeOnOutsideClick` dan `closeOnEsc` belum diterapkan menyeluruh pada seluruh mode panel toko (Rule 86 §2).
""",
    'b15-red.md': """# Reproduksi Masalah B15: Panel Toko Belum Menampilkan Potret Karakter NPC Vendor
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Buka katalog belanja toko (kantin, minimarket, kosmetik, SPBU, game center).
- **Hasil Aktual:** Panel hanya menampilkan thumbnail kecil 30x30 di subhead, tidak ada potret vendor besar 192x256 di sisi kiri dengan plakat nama dan gelembung ucapan dinamis.
- **Tangkapan Layar:** `docs/regression/b15_toko_tanpa_vendor_red.png`
- **Akar Masalah:** Layout panel toko belum dirancang dengan kolom potret vendor `shop.vendorSide = 'left'` (Rule 86 §3).
""",
    'b16-red.md': """# Reproduksi Masalah B16: Tutorial Hari Pertama & Cerita Belum Diaktifkan
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Mulai permainan baru ("Mulai Petualangan").
- **Hasil Aktual:** Game langsung masuk ke mode bebas tanpa inisialisasi state tutorial 20 langkah (`T01–T20`), tanpa panah pemandu, dan jam langsung berdetak secara real-time.
- **Tangkapan Layar:** `docs/regression/b16_tutorial_red.png`
- **Akar Masalah:** Modul mesin tutorial `src/domain/tutorial.js` belum dibuat dan diintegrasikan ke siklus hidup permainan (Rule 82).
"""
}

for fname, text in reports.items():
    with open(os.path.join(reg_dir, fname), 'w') as f:
        f.write(text)
print('Generated all red reports successfully.')
