# EXPANSION-PATCH-V6 — perubahan pada file lama (diterapkan agen pada J0)
> Terapkan persis. Jika teks lama sudah berbeda (mis. diedit agen/pengguna), terapkan *maksud* perubahan dan catat di `docs/DECISIONS.md`. Tampilkan `git diff --stat` sesudahnya. Jangan mengubah hal lain.

## Patch 1 — `AGENTS.md`
**Cari:**
```
- `81-click-to-move.md` — gerak dengan klik/ketuk, pathfinding, auto-interaksi
```
**Ganti dengan:**
```
- `81-click-to-move.md` — gerak dengan klik/ketuk, pathfinding, auto-interaksi
- `82-tutorial-and-story.md` — tutorial berpemandu wajib pertama kali, cerita hari pertama, panah dan teks panduan
- `83-energy-v2.md` — energi per aktivitas (pelajaran 20%, game center 20%), peringatan < 50%, bangun kesiangan
- `84-interaction-targeting.md` — penargetan interaksi (NPC vs objek), petunjuk tombol
- `85-asset-perspective-identity-qa.md` — kontrak perspektif, identitas aset, batas dinding, gaya sprite NPC
- `86-shop-vendor-presence.md` — tombol keluar panel toko dan tampilan NPC kasir
```

## Patch 2 — `AGENTS.md`
**Cari:**
```
laporkan baris non-PASS dan hal yang tidak diuji.
```
**Ganti dengan:**
```
laporkan baris non-PASS dan hal yang tidak diuji.
20. **Aset visual diverifikasi pada empat sumbu sebelum berstatus `ready`:** perspektif (frontal/belakang/samping, bukan serong), identitas (isi gambar = nama), batas ruang (tidak menembus dinding), gaya piksel (bukan kartun). Validator berjalan pada SEMUA aset (`85-asset-perspective-identity-qa.md`), bukan hanya yang disebut pengguna.
21. **Tutorial pertama kali dan energi v2 adalah sistem inti.** Klaim selesai memakai `docs/ACCEPTANCE-V6.md` (aturan #19 berlaku juga untuk V6).
22. **Interaksi harus deterministik:** satu target terpilih dengan petunjuk tombol; NPC tidak boleh kalah oleh furnitur di dekatnya (`84-interaction-targeting.md`).
```

## Tambah di akhir `.agents/rules/74-energy-inventory-items.md`
```
## 8. Pembaruan v6
Bagian energi (§1) **digantikan oleh `83-energy-v2.md`**: biaya per aktivitas (pelajaran −20%, game center −20%/jam), peringatan teks di bawah 50%, dan energi 0 = pingsan lalu bangun kesiangan di hari berikutnya (bukan penonaktifan aktivitas). Bagian inventaris tetap mengikuti rule 80.
```

## Tambah di akhir `.agents/rules/73-room-layout-and-collision.md`
```
## 9. Pembaruan v6
- **Batas ruang:** footprint semua objek non-dekoratif harus di dalam lantai ruangnya; tidak ada piksel sprite non-`wall_decor` yang melintasi tepi ruang atau dinding samping/bawah (validator di rule 85 §3). Bangku/meja tidak boleh melintasi garis dinding atau ambang pintu (pelanggaran terlihat di kantin dan perpustakaan).
- **Ruang kelas:** meja siswa dalam grid rapi menghadap papan tulis (komposit meja + kursi dari belakang); **rak buku kelas di pojok kiri ruangan** (menempel dinding belakang di ujung kiri); papan tulis dan meja guru frontal.
- **Dapur:** Ibu tidak berdiri di depan furnitur yang dapat berinteraksi; counter kompor bukan interactable; lihat rule 84.
- Penargetan interaksi dan penempatan NPC mengikuti rule 84; set meja+kursi memakai sprite komposit (rule 85).
```

## Tambah di akhir `.agents/rules/75-vehicle-motor.md`
```
## 6. Pembaruan v6: motor parkir terikat peta
Posisi motor parkir menyimpan `mapId` dan **hanya dirender/berkolisi di peta itu**. Saat masuk gedung dalam keadaan bermotor, pemain turun otomatis dan motor diparkir di **peta hub di depan pintu bangunan tersebut**, bukan di interior. Bug yang dilaporkan: sprite motor muncul di ruang kelas. Uji (UI nyata): bermotor → masuk sekolah → ruang kelas tidak memuat motor; keluar → motor ada di depan pintu sekolah; simpan/muat mempertahankan `mapId` parkir.
```

## Tambah di akhir `.agents/rules/79-shop-and-vendors.md`
```
## 8. Pembaruan v6
Panel toko wajib memiliki tombol keluar (X, Selesai, Esc, klik luar) dan menampilkan karakter NPC vendor, sesuai `86-shop-vendor-presence.md`. Berlaku untuk kantin, minimarket, toko kosmetik, kafe game center, dan menu SPBU.
```

## Tambah di akhir `.agents/rules/72-time-system.md`
```
## 8. Pembaruan v6
- **Sesi sekolah:** `ikut_pelajaran` dipecah: Sesi 1 07:00–10:00, istirahat 10:00–10:30 (kantin buka), Sesi 2 10:30–14:30; biaya energi mengikuti `83-energy-v2.md`. Memulai sesi sebelum jam mulai memajukan waktu ke jam mulai ("menunggu bel").
- **Tutorial:** selama tutorial (rule 82) jam real-time dijeda; waktu hanya maju lewat aktivitas. Energi habis menyebabkan bangun kesiangan di hari berikutnya (rule 83).
```

## Tambah di akhir `.agents/rules/50-security.md`
```
21. **Data tutorial/cerita (v6):** validasi skema `tutorial.phase1.json` (id target ada, tipe kondisi/efek di whitelist); kondisi selesai hanya dari event domain; teks lewat `textContent`; tombol "Lewati langkah" tidak dapat dimanipulasi (penghitung waktu di domain).
22. **Alat audit aset (v6):** skrip audit/regenerasi hanya membaca/menulis di `assets/` dan `docs/asset-identity/`; keluaran generator dikonversi ke PNG murni tanpa metadata; tidak ada eksekusi dari berkas gambar.
23. **Hook uji (v6)** yang memicu energi/tutorial (`setEnergy`, `skipTutorialStep`) hanya aktif dengan `?debug=1` dan `debugEnabled: true` dan tidak sah untuk aksi yang diuji (rule 78).
```
