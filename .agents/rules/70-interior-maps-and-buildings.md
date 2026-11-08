---
trigger: model_decision
description: "Terapkan saat membuat atau mengubah peta interior (rumah, sekolah, minimarket, toko kosmetik, SPBU, game center), perpindahan antar-peta, furnitur, pintu/jam buka, titik interaksi bangunan, alur awal permainan di rumah, atau tes peta."
---

# 70 · Peta Interior, Perpindahan Peta, dan Fitur Bangunan

## 1. Prinsip
- Setiap bangunan yang bisa dimasuki adalah **peta interior terpisah yang dapat dijelajahi**. Menekan E pada pintu **memindahkan pemain ke peta itu** (bukan membuka panel pilihan). Transaksi hanya terjadi pada titik interaksi spesifik di dalam bangunan (mis. belanja jajan hanya di konter kantin).
- **Permainan baru dimulai di dalam rumah pemain**, bangun di kasur kamarnya.
- Panel DOM lama (`bg_panel_*`) tidak lagi menjadi pintu masuk; pertahankan hanya bila dipakai sebagai latar kecil di dalam panel transaksi. Jangan menghapus kode/asetnya tanpa alasan tercatat.

## 2. Registry dan format
- `data/maps/index.json`: `{id, file, kind (hub|interior), displayName, buildingId, openHours?, defaultSpawn}` untuk: `town_hub`, `home`, `school`, `minimarket`, `toko_kosmetik`, `spbu`, `game_center`.
- Layout v2 `data/maps/<id>.layout.json` (hub tetap kompatibel): `size` (tile), `floor` (zona + jenis lantai), `walls` (segmen + tinggi muka dinding + gaya), `openings` (celah pintu/lorong, lebar ≥ 2 tile), `objects` (`{assetId,x,y,layer,footprint?}`), `colliders`, `interactables`, `npcs`, `spawns` (`{id,x,y,facing}`), `exits` (`{id,rect,targetMap,targetSpawn,prompt}`), `bounds`.
- Pintu bangunan di hub memakai `doorAnchor` dari manifest dan menautkan ke `exits` interior; tiap `exit` WAJIB punya pasangan timbal-balik (keluar dari interior mendarat di depan pintu hub yang benar).

## 3. Elemen prosedural interior (perluasan pengecualian di rule 20 §7)
Lantai dan muka dinding digambar kode **hanya dari `assets/palette.json`**: lantai kayu (rumah), ubin keramik (dapur/kamar mandi), ubin kelas (krem-abu), tegel kantin, lantai gelap navy (game center), beton (SPBU), karpet (decal). Dinding: muka dinding setinggi 2 tile + lis bawah (baseboard) + garis atap/langit-langit; warna per ruangan dari palet. Pola menyambung, ukuran `tileSize`. Tidak boleh dipakai untuk furnitur, karakter, atau ikon.

## 4. Furnitur
- Sprite hasil generate (brief di `data/asset-briefs-expansion.json`), tampak depan 3/4, dasar sprite rata di baris terbawah, `footprint` dari manifest (bagian dasar saja; bagian atas sprite tidak menghalangi).
- Penempatan memakai dasar sprite; urutan kedalaman berdasarkan y-dasar; benda tempel dinding (jam, bingkai kosong, jendela, papan tulis) berada di muka dinding dan tidak punya kolisi.
- Kelonggaran: jalur utama ≥ 2 tile, ≥ 1 tile di sekeliling titik interaksi. Ruangan tidak boleh terasa kosong: isi sesuai daftar furnitur di bawah; ruangan tidak boleh penuh sehingga memblokir jalan.

## 5. MapManager
- Transisi: fade ke gelap 200 ms → ganti peta → fade masuk 200 ms; input dikunci selama transisi; jam permainan berjalan normal (tanpa biaya waktu tambahan kecuali ditentukan aktivitas).
- Simpan `{mapId, x, y, facing}` pemain; autosave saat pindah peta. Kamera mengikuti pemain dengan batas peta; peta lebih kecil dari viewport dipusatkan dengan latar `--navy-950`.
- HUD menampilkan nama lokasi aktif (`displayName`). Peta interior tidak diberi tint waktu (lampu menyala); hub boleh (lihat 72).
- Migrasi save: `lj_save_v1` → `lj_save_v2` (posisi diset ke depan pintu rumah di hub bila tidak ada data peta; tambahkan field jam bila belum ada). Jangan merusak save lama.

## 6. Rumah pemain (peta `home`, satu peta terhubung dengan celah pintu antar-ruang)
Ruangan wajib: **kamar pemain, kamar orang tua, ruang tamu, dapur + ruang makan, kamar mandi/toilet**, lorong, serta pintu depan ke hub. Ukuran total sekitar 28–32 × 18–22 tile; susunan bebas asal logis dan semua titik terjangkau.
| Ruang | Furnitur wajib | Titik interaksi |
|---|---|---|
| Kamar pemain | kasur single, meja belajar + kursi, lemari pakaian, rak buku, nakas + lampu, celengan ayam, jendela | kasur (tidur/istirahat), meja belajar (belajar, anggaran bulanan), lemari (ganti baju), celengan (tabung/tarik) |
| Kamar orang tua | kasur besar, lemari besar, meja rias, nakas, kipas berdiri | (dekoratif; boleh dimasuki) |
| Ruang tamu | sofa 3 dudukan + sofa single, meja tamu, TV + rak, rak pajangan, karpet, bingkai kosong | TV (nonton), ayah/ibu (dialog) |
| Dapur + makan | kompor + counter, kulkas, meja makan + kursi, rak piring, wastafel | meja makan (makan di rumah), ibu (uang saku, dialog) |
| Kamar mandi | toilet, bak mandi + gayung, wastafel + cermin, rak handuk | bak mandi (mandi) |
Pintu depan: titik `exit` ke hub. Jam dinding di ruang tamu. Semua teks pada bingkai/papan kosong.
**Alur awal (hari 1, Senin, 06:00):** pemain bangun di kasur → dialog singkat (potret) → misi "Temui ibu di dapur untuk uang saku" → ibu memberi uang saku bulanan (transaksi ledger) → misi "Susun anggaran di meja belajar" → boleh keluar rumah. Tutorial berupa petunjuk kontekstual singkat (bukan layar panjang).

## 7. Matriks fitur bangunan
| Bangunan (peta) | Area wajib | Furnitur utama | Titik interaksi dan transaksi | Jam buka (default) |
|---|---|---|---|---|
| Sekolah (`school`) | lobby/koridor, ruang kelas, kantin, perpustakaan kecil | meja siswa + kursi tersusun rapi, meja guru, papan tulis, lemari kelas, tempat sampah, papan pengumuman kosong, bangku tunggu, rak buku, counter kantin + etalase, meja/bangku kantin, kulkas minuman, dispenser | **Ruang kelas:** ikut pelajaran (hanya hari sekolah). **Kantin:** konter = SATU-SATUNYA tempat belanja makan/jajan/minuman. **Perpustakaan:** baca buku (gratis, waktu). NPC: teman, penjual kantin | Sen–Jum 06:30–15:30; kantin 06:30–14:30; tutup Sabtu–Minggu |
| Minimarket (`minimarket`) | satu ruang toko + area kasir | rak gondola, rak alat tulis, kulkas minuman, kasir, mesin fotokopi, keranjang | rak alat tulis, kulkas minuman/camilan, fotokopi, kasir (paket kuota). NPC: kasir | setiap hari 07:00–22:00 |
| Toko kosmetik (`toko_kosmetik`) | satu ruang toko | etalase kaca, rak dinding, meja cermin, kasir, kursi tunggu | etalase/rak (lip tint, skincare), kasir. NPC: penjaga | setiap hari 09:00–20:00 |
| SPBU (`spbu`) | pelataran terbuka + kiosk kecil | dispenser BBM, kiosk + kasir, rak oli, bangku tunggu | dispenser (isi bensin), kiosk (kasir). NPC: petugas | 24 jam |
| Game center (`game_center`) | area arcade, area kafe, sudut TV | mesin arcade (2 model), meja + kursi kafe, counter kafe, layar TV besar | mesin arcade (main per jam), counter (minuman/camilan), meja (nongkrong), TV (nonton mini). NPC: penjaga, teman | setiap hari 10:00–23:00 |
Kebijakan sama untuk semua: tiap bangunan memuat minimal 6 furnitur berbeda, 1 NPC, dan 2 titik interaksi bermakna. Fitur tambahan yang agen usulkan boleh dicatat di `docs/DECISIONS.md` asal tidak melampaui cakupan Fase 1.

## 8. Jam buka dan pintu tertutup
Pintu hub memeriksa jam dan hari dari domain clock. Tutup → pesan kontekstual ("Tutup. Buka pukul 07:00."), pemain tidak masuk. Pemain yang sedang di dalam saat jam tutup mendapat pemberitahuan dan diarahkan keluar (otomatis keluar setelah dialog singkat bila tidak keluar dalam 15 menit game).

## 9. NPC
Penempatan awal dari layout; dialog lewat sistem `71-dialogue-system.md`. Jadwal sederhana opsional (ayah/ibu di rumah pagi dan malam; teman di sekolah pada jam sekolah) via tabel `data/npc-schedule.json`; jika diimplementasikan, wajib diuji.

## 10. Verifikasi wajib (otomatis)
- `tests/map-check.html`: untuk setiap layout — semua `spawns`, `interactables`, `exits`, NPC **terjangkau** dari spawn utama (BFS pada grid kolisi); tidak ada spawn di dalam collider; semua objek dalam batas; setiap `exit` punya pasangan timbal-balik dan titik pendaratan bebas kolisi; semua `assetId` ada di manifest (placeholder dihitung terpisah).
- Hook `window.__LJ__`: `teleportToMap(mapId, spawnId)`, `listInteractables()`, `interact(id)`.
- Tangkapan layar tiap peta dengan overlay kolisi; periksa kedalaman (pemain di belakang/di depan furnitur), pintu, dan keterbacaan.
- Skenario E2E: bangun di rumah → ibu (uang saku) → anggaran → keluar → sekolah (kelas → kantin beli) → minimarket → SPBU → game center → pulang → tidur → hari berikutnya; invarian ledger dan jam diperiksa di tiap langkah.

## 11. Pembaruan v4
Tata letak seluruh peta mengikuti `73-room-layout-and-collision.md` (Layout Spec berbasis slot, dinding belakang tampak, kolisi, oklusi). **Katalog `data/furniture-catalog-v4.json` menggantikan daftar furnitur di §6–7 sebagai acuan minimum**; interior memakai aset `_v4`. Eksterior game center memakai `bld_game_center_v4` (menggantikan `bld_game_center` setelah lolos QA). NPC interior tidak boleh ada di layout hub.
