---
trigger: model_decision
description: "Terapkan saat mendesain/menata ulang tata letak peta (interior dan hub), menempatkan furnitur/objek/NPC, mendefinisikan kolisi (footprint), men-generate furnitur yang harus pas dengan slot tata letak, atau memperbaiki objek melayang, NPC tertimpa, dan pemain menembus objek."
---

# 73 · Tata Letak Berbasis Slot, Kolisi, dan Penempatan NPC

## 0. Masalah yang diperbaiki (bukti: `docs/reference/`)
Furnitur dapur dan kamar mandi tampak **melayang dan tersebar** (tidak menempel dinding, tidak membentuk deretan), ukuran/orientasi aset tidak cocok dengan letaknya; pemain bisa melewati objek; NPC ibu masih ada di hub dan **tertutup sprite rumah**. Penyebab umum: aset digenerate lebih dulu lalu ditempatkan "kira-kira". **Aturan baru: tata letak dirancang lebih dulu, aset digenerate untuk slot, lalu divalidasi.**

## 1. Alur wajib (layout-first)
1. **Layout Spec** per peta: `docs/layouts/<mapId>.md` (denah teks + alasan) dan slot di `data/maps/<mapId>.layout.json`.
2. **Turunkan brief** dari slot (`tools/derive_briefs_from_layout.py` ditulis agen) → `data/asset-briefs-v4-<mapId>.json`. Ukuran, kelas, dan arah tiap aset **berasal dari slot**, bukan ditebak.
3. **Generate + proses** (rule 60 §11) → ukuran akhir = ukuran slot.
4. **Tempatkan** objek persis di slot (tanpa koordinat bebas).
5. **Validasi otomatis** (bagian 5) + **tinjauan visual** tangkapan layar dengan overlay.
6. Aset lama dipertahankan sampai E2E lulus; aset baru memakai sufiks `_v4` dan layout menunjuk ke `_v4` (rollback mudah).
Katalog awal item per ruang: `data/furniture-catalog-v4.json` (daftar minimum; boleh diperluas, tidak boleh dikurangi tanpa catatan di `DECISIONS.md`).

## 2. Anatomi ruangan (wajib terlihat)
- **Dinding belakang (utara) tampak** setinggi 2 tile dengan lis bawah dan garis atap; dinding samping terlihat sebagai tepi tipis. Garis dasar dinding = `wallBaseY`.
- Lantai prosedural sesuai ruangan (rule 70 §3). Ambang pintu/lorong ≥ 2 tile, dengan bingkai pintu.
- Semua furnitur menghadap kamera (selatan) kecuali varian samping yang memang digenerate (mis. kursi makan kiri/kanan).

## 3. Kelas slot
| Kelas | Aturan penempatan | Kolisi |
|---|---|---|
| `wall_back` | dasar sprite menempel `wallBaseY` (toleransi ±2 px); x selaras kelipatan 8 px; di dalam batas ruang | ya |
| `counter_module` | deretan modul berdampingan di dinding belakang, **tinggi dan garis dasar sama**, jarak 0–2 px, sisi kiri/kanan dipotong datar agar menyambung | ya |
| `free` | ≥ 1 tile dari dinding (kecuali dinyatakan), tidak menutupi pintu/jalur utama | ya |
| `cluster` | kelompok dengan offset relatif tetap (mis. meja makan + 2 kursi samping + 2 kursi depan) | ya |
| `wall_decor` | menempel pada muka dinding (jendela, jam, papan tulis, bingkai, poster, rak dinding) | tidak |
| `floor_decal` | karpet/keset, digambar di bawah objek | tidak |
Larangan: objek melayang (dasar tidak menyentuh lantai/dinding sesuai kelas), furnitur saling menimpa (kecuali dekor/decal), objek di atas ambang pintu, ruangan kosong atau sebaliknya sesak sampai memblokir jalur.

## 4. Pedoman tata letak ruangan kunci
- **Dapur + makan (diperbaiki total):** satu **deretan kontinu di dinding belakang** dari kiri: kulkas → counter polos → counter kompor (rice cooker di atasnya) → counter wastafel → counter polos → dispenser galon; **rak piring dan rak bumbu menggantung di atas counter** (`wall_decor`); jendela dapur di dinding. **Meja makan di tengah dengan 4 kursi** (kursi samping kiri/kanan + dua kursi depan/belakang bila sprite tersedia), jarak ≥ 1 tile ke deretan counter dan ke dinding. Tempat sampah di ujung deretan. Ibu berdiri di depan kompor.
- **Kamar mandi:** toilet dan bak mandi di dinding belakang berdampingan dengan jarak ≥ 1 tile; wastafel + cermin di dinding belakang sisi lain; rak handuk menempel dinding; ember di samping bak; keset di depan pintu; jalur bebas ke pintu.
- **Ruang tamu:** TV + rak di tengah dinding belakang; sofa 3 dudukan dan sofa single di dinding belakang kiri/kanan atau sebagai kelompok dengan meja tamu di depannya; karpet di bawah kelompok; rak pajangan, tanaman, kipas di sudut; rak sepatu dekat pintu depan.
- **Kamar pemain/ortu:** kasur di dinding belakang (kepala di dinding), nakas di sampingnya, lemari dan rak buku di dinding belakang, meja belajar + kursi sebagai cluster, jendela di dinding.
- **Ruang kelas:** papan tulis di dinding belakang; meja siswa dalam **grid rapi** (mis. 6 kolom × 4 baris, jarak lorong 1 tile), meja guru di depan papan; lemari dan rak di dinding samping/belakang.
- **Toko (minimarket, kosmetik):** rak gondola dalam baris paralel dengan lorong ≥ 2 tile; kulkas dan rak dinding di dinding belakang; kasir dekat pintu.
- **Game center:** mesin arcade berderet di dinding belakang dan sebagai dua baris tengah; area kafe (counter + meja + kursi) dan sudut TV/sofa terpisah jelas.
- **SPBU:** dispenser berderet di bawah kanopi dengan tiang; kiosk di sisi; area kendaraan lega.

## 5. Kolisi
- **Setiap objek non-dekoratif memiliki `footprint`** (rect kolisi di dasar sprite) di manifest/layout: default = bagian bawah 40% tinggi, inset 4 px; furnitur `wall_back` memakai kedalaman dasar 24–32 px; kasur/sofa/meja memakai tapak penuh bagian bawah. Dinding = collider penuh. Pintu = celah tanpa collider.
- **Collider pemain** kecil (kotak kaki ±16×10 px, dua kali lebih lebar saat bermotor) agar bisa berjalan rapat tetapi tidak menembus; objek di depan pemain digambar di atasnya (depth = y dasar).
- **Uji probe kolisi** (`__LJ__.collisionProbe(mapId)`): untuk tiap objek berkolisi, pemain disimulasikan bergerak dari sisi bebas terdekat menuju pusat footprint; harus **tertahan** di luar footprint. Laporkan per objek. Uji kebalikan: semua pintu/jalur utama tetap bisa dilewati (BFS rule 70 §10).
- Overlay kolisi (`toggleCollisionOverlay`) wajib dipakai pada tangkapan layar tinjauan.

## 6. NPC dan oklusi
- Tiap NPC memiliki **tepat satu** `homeMap`. NPC yang mestinya di interior (ibu, ayah, penjual, kasir, dll.) **tidak boleh ada di layout hub**. Audit dan hapus sisa (mis. ibu di hub). Hub hanya berisi NPC yang memang berjalan di luar (mis. teman).
- Posisi NPC tidak boleh berada di dalam collider mana pun atau di dalam kotak sprite bangunan; `depth` NPC = y kaki, `depth` bangunan/objek = y dasar sprite sehingga bangunan hanya menutupi NPC yang berada di belakangnya.
- **Uji oklusi (map-check):** untuk tiap NPC dan interactable, jika kotak sprite-nya tertutup ≥ 30% oleh sprite berdepth lebih tinggi → gagal.
- Nama NPC tidak boleh sama dengan nama pemain: validasi nama pemain terhadap nama NPC default; bila bentrok, NPC memakai `altName` dari data dan label tidak ganda.

## 7. Validator tata letak (`tests/layout-check.html` + `map-check.html`)
Untuk tiap peta: (a) semua objek di dalam batas; (b) kelas `wall_back`/`counter_module` dasar rata `wallBaseY`; (c) tidak ada tumpang-tindih non-dekoratif (IoU > 0.1) dan tidak ada objek melayang; (d) jalur ≥ 2 tile ke semua interactable (BFS); (e) probe kolisi hijau; (f) oklusi hijau; (g) setiap `assetId` ada di manifest; (h) daftar item minimum dari katalog terpenuhi; (i) tidak ada NPC yang salah peta. Hasil ditulis ke `docs/layouts/VALIDATION-<mapId>.md` dengan tangkapan layar overlay.


## 8. Zona pendekatan interactable (v5; perbaikan nakas yang menghalangi kasur)
- Setiap interactable memiliki **zona pendekatan** bebas kolisi, minimal `layout.approachZoneMinTiles` (default 2 lebar × 1 dalam tile) di sisi tempat pemain berinteraksi (default: depan/selatan), dan zona itu **terjangkau dari pintu ruangan** lewat BFS/pathfinding dengan collider kaki pemain yang sebenarnya.
- Furnitur samping (nakas, rak kecil, tanaman) **tidak boleh** berada di zona pendekatan atau menyempitkan lorong menuju interactable di bawah 1 tile. **Kasur:** kepala di dinding belakang; nakas menempel dinding belakang di samping kepala kasur; jalur ke kaki dan sisi kasur tetap lega. Perbaiki posisi nakas di kamar pemain (dan temuan serupa di ruang lain).
- Validator `approachCheck` (di `layout-check.html`) berjalan untuk semua interactable di 7 peta dan melaporkan: zona bebas, terjangkau, jarak jalur dari pintu. Tes jalan dari pintu kamar ke titik interaksi kasur dijalankan dengan pathfinding rule 81.

## 9. Pembaruan v6
- **Batas ruang:** footprint semua objek non-dekoratif harus di dalam lantai ruangnya; tidak ada piksel sprite non-`wall_decor` yang melintasi tepi ruang atau dinding samping/bawah (validator di rule 85 §3). Bangku/meja tidak boleh melintasi garis dinding atau ambang pintu (pelanggaran terlihat di kantin dan perpustakaan).
- **Ruang kelas:** meja siswa dalam grid rapi menghadap papan tulis (komposit meja + kursi dari belakang); **rak buku kelas di pojok kiri ruangan** (menempel dinding belakang di ujung kiri); papan tulis dan meja guru frontal.
- **Dapur:** Ibu tidak berdiri di depan furnitur yang dapat berinteraksi; counter kompor bukan interactable; lihat rule 84.
- Penargetan interaksi dan penempatan NPC mengikuti rule 84; set meja+kursi memakai sprite komposit (rule 85).
