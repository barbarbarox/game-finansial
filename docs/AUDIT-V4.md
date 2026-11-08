# AUDIT V4 — Life Journey: Kondisi Aset, Tata Letak, Kolisi, NPC, dan Fitur

**Tanggal:** 2026-11-08  
**Fase:** G0 (Audit Preflight v4)  
**Tujuan:** Mengidentifikasi secara menyeluruh seluruh kekurangan visual, inkonsistensi kolisi, tumpang-tindih NPC, dan kesiapan sistem sebelum implementasi G1–G8.

---

## 1. Daftar Furnitur & Objek per Peta Beserta Statusnya

| Peta | Total Objek/Furnitur | Ready (AI) | Placeholder | Kode Prosedural | Catatan Kesiapan |
|---|---|---|---|---|---|
| `town_hub` | 6 bangunan | 6 (Sekolah, Rumah, Minimarket, Kosmetik, SPBU, Game Center) | 0 | 0 | Eksterior `bld_game_center` perlu digenerate ulang (`bld_game_center_v4`) agar selaras kanon. |
| `home` | 26 furnitur/interactable | 21 | 4 | 1 | Furnitur dapur, kamar mandi, dan ruang tamu perlu ditata ulang berbasis slot (`wall_back`, `counter_module`, `cluster`). |
| `school` | 11 furnitur | 0 | 11 | 0 | Masih memakai aset placeholder standar; siap ditata berbasis grid rapi meja kelas & kantin. |
| `minimarket` | 6 objek | 0 | 0 | 6 | Masih berupa representasi kotak kode prosedural. Perlu layout spec & aset furnitur v4. |
| `toko_kosmetik` | 5 objek | 0 | 0 | 5 | Masih berupa representasi kotak kode prosedural. Perlu layout spec & aset furnitur v4. |
| `spbu` | 4 dispenser/pompa | 0 | 0 | 4 | Masih berupa representasi kotak kode prosedural. Perlu layout spec & aset furnitur v4. |
| `game_center` | 6 objek | 0 | 0 | 6 | Masih berupa representasi kotak kode prosedural. Perlu layout spec & aset arcade/kafe v4. |

---

## 2. Audit Kolisi & Objek Tanpa Footprint

- **Kondisi Saat Ini:**
  - Di `town_hub`, kolisi bertumpu pada kotak `footprint` di layout objek dan colliders batas. Pemain kadang masih dapat menyenggol atau menembus sudut bangunan tertentu karena ukuran bounding box collider pemain cukup besar.
  - Di `home`, beberapa objek interior (`fur_kursi_makan_1`, `fur_kursi_makan_2`, `fur_kursi_belajar`, `fur_celengan_ayam`) ditandai `collidable: false`. Meskipun celengan berada di atas meja, kursi seharusnya memiliki footprint kolisi bawah agar pemain tidak berjalan menembusnya.
  - Di interior bangunan lain (`minimarket`, `toko_kosmetik`, `spbu`, `game_center`), kolisi mengandalkan rect statis global di array `colliders` bukan footprint per objek yang terikat pada dasar sprite.
- **Tindakan Perbaikan G1 & G4:**
  - Perkecil collider kaki pemain menjadi $16 \times 10$ px (saat jalan kaki) dan $24 \times 12$ px (saat bermotor).
  - Berikan footprint rect kolisi eksplisit di dasar sprite (40% tinggi bawah, inset 4 px) untuk setiap objek non-dekoratif.
  - Tambahkan hook pengujian otomatis `__LJ__.collisionProbe(mapId)` untuk memastikan semua objek berkolisi menahan pemain dan semua jalur utama tetap bebas.

---

## 3. Audit NPC & Oklusi (Depth Sorting)

- **Temuan Kritis: NPC Ibu Tertimpa Rumah di `town_hub`:**
  - Pada `town_hub.layout.json`, terdapat entri NPC `npc_ibu` di koordinat `x: 8, y: 20`.
  - Gedung rumah pemain `bld_rumah_pemain` berada di `x: 6, y: 22` dengan footprint `w: 9, h: 3`.
  - Karena nilai Y gedung (22) lebih besar dari Y NPC Ibu (20), maka sprite gedung digambar di atas NPC Ibu, menyebabkannya tertimpa atap rumah dan tampak aneh/hilang.
  - Selain itu, keberadaan Ibu di luar rumah bertentangan dengan Rule 73 §6: *"Tiap NPC memiliki tepat satu homeMap. NPC yang mestinya di interior (ibu, ayah, penjual, kasir, dll.) tidak boleh ada di layout hub."*
- **Tindakan Perbaikan G1:**
  - Hapus `npc_ibu` sepenuhnya dari `town_hub.layout.json` sehingga Ibu hanya berada di dalam `home`.
  - Pastikan seluruh NPC di setiap peta memiliki `homeMap` tunggal.
  - Implementasikan uji oklusi pada `tests/map-check.html` untuk memvalidasi tidak ada NPC yang tertutup $\ge 30\%$ oleh sprite berdepth lebih tinggi.

---

## 4. Kondisi Tata Letak Dapur, Kamar Mandi, Ruang Tamu vs Rule 73

- **Dapur & Ruang Makan:**
  - Sebelumnya, kompor (`x:15, y:12`), wastafel (`x:18, y:12`), kulkas (`x:23, y:12`), dan meja makan (`x:19, y:15`) tersebar secara terpisah.
  - Rule 73 mewajibkan **deretan counter kontinu di dinding belakang (`wall_back` / `counter_module`)** dari kiri ke kanan: Kulkas $\rightarrow$ Counter Polos $\rightarrow$ Counter Kompor $\rightarrow$ Counter Wastafel $\rightarrow$ Counter Polos $\rightarrow$ Dispenser Air Galon; dengan rak piring / bumbu menggantung di dinding (`wall_decor`), serta meja makan 4 kursi di area tengah dengan jarak lorong $\ge 1$ tile.
- **Kamar Mandi:**
  - Bak mandi keramik, gayung, kloset duduk, wastafel cermin, dan rak handuk perlu ditata sejajar di dinding belakang dengan jarak lorong $\ge 1$ tile agar tidak saling bertabrakan atau menghalangi pintu.
- **Ruang Tamu:**
  - TV kabinet, sofa 3 dudukan, meja kopi, dan karpet tenun perlu disusun dalam formasi `cluster` yang rapi di sisi kiri ruang keluarga, menyisakan koridor lega menuju pintu depan.

---

## 5. Bangunan Game Center Eksterior

- Fasad `bld_game_center` lama memiliki gaya visual yang sedikit kontras dengan gedung kanon sekolah dan toko lainnya.
- Perlu digenerate ulang sebagai `bld_game_center_v4`: fasad warna navy (`#34456B`) dan krem (`#F7EEDA`), kanopi hijau bergaris, jendela kaca besar yang memperlihatkan siluet mesin arcade, pintu kaca ganda di tengah bawah, dan garis dasar sprite rata tanpa artefak transparan.

---

## 6. Audit Sistem Bensin & Kendaraan

- **Kondisi Eksisting:**
  - Bensin berkurang 5% per hari secara pasif via siklus hari (`gasolineDrainPerDay`).
  - Belum ada entitas kendaraan motor yang dapat dikendarai langsung di peta hub.
- **Rencana V4 (Rule 75):**
  - Hapus pengurangan harian pasif. Bensin hanya berkurang saat pemain menaiki motor (berkurang 2% per 5 detik jalan via akumulator).
  - Tombol motor di HUD kanan atas + tombol pintasan **V**.
  - Kecepatan bermotor $1,8\times$ kecepatan jalan kaki.
  - Otomatis turun dan memunculkan motor parkir saat pemain memasuki pintu interior.

---

## 7. Audit Data Belanja & Item Makanan/Minuman

- **Kondisi Eksisting:**
  - Belanja di kantin dan minimarket langsung mengurangi kas dan memberikan efek instan tanpa inventaris.
- **Rencana V4 (Rule 74):**
  - Menggabungkan katalog 16 item makanan/minuman (`data/items.phase1.json`) ke dalam sistem game.
  - Pembelian di minimarket masuk ke dalam tas inventaris (maks 5 slot, stack 5).
  - Pembelian di kantin dapat berupa makan di tempat (efek langsung) atau dibungkus ke tas.
  - Makanan di meja makan rumah (masakan Ibu) gratis dan memulihkan +40 energi.
  - Hotbar 5 slot di bawah-tengah layar dapat diklik atau ditekan tombol 1–5 untuk mengonsumsi item.

---

## 8. Kesimpulan & Langkah Eksekusi G0

Audit telah selesai dengan pemetaan masalah yang jelas. Seluruh patch `EXPANSION-PATCH-V4.md` telah diterapkan, `phase1.config.json` telah diperkaya dengan parameter energi, inventaris, kendaraan, misi, dan terrain, serta tes lama terverifikasi aman. Gerbang G0 siap ditutup dan dilanjutkan ke G1.
