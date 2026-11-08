# AUDIT-V5: Investigasi Akar Masalah & Rencana Perbaikan (Gerbang H0)
**Tanggal:** 9 November 2026  
**Status:** Selesai (Temuan terverifikasi pada kode sumber dan state)

---

## 1. Alur Pembelian & Menu Pilihan Item (Poin a & b)
- **Kondisi Saat Ini:**
  - Dialog vendor (`dia_sri_kantin`, `dia_maya_minimarket`, dll.) saat ini menyediakan pilihan hardcoded teks seperti *"Beli Nasi Kuning Komplit (Rp12.000)"*.
  - Efek pilihan dialog hanya memproses `type: "ledger_expense"` dan `type: "start_activity"`.
  - **Titik Putus:** Tidak pernah ada pemanggilan ke `inventory.add(itemId, count)`. Akibatnya, uang kas dipotong pada buku kas (*ledger*), namun item tidak pernah masuk ke slot inventaris atau tas pemain.
  - Selain itu, tidak ada pemanggilan pembukaan panel toko (`openShop`), sehingga pemain tidak disajikan menu daftar barang dengan pilihan tab kategori, kuantitas 1–5, maupun mode *"Makan di tempat"* vs *"Bungkus"*.
- **Solusi V5 (Rule 79):**
  - Mengintegrasikan panel toko visual `shopPanel.js` yang menampilkan katalog item lengkap dengan ikon, harga, tombol kuantitas, dan mode konsumsi.
  - Menambahkan efek dialog `openShop(shopId)` pada pilihan *"Beli sesuatu"* di setiap NPC vendor.
  - Mengaitkan interactable rak/kulkas/etalase/counter langsung ke panel toko dengan filter kategori yang sesuai.
  - Menjalankan transaksi secara atomik di domain: `canAdd()` dipanggil sebelum memotong kas, lalu memotong kas dan menambahkan item ke `inventory.add()` secara bersamaan.

---

## 2. Sinkronisasi Bar Bensin SPBU (Poin d)
- **Kondisi Saat Ini:**
  - Pada `dia_doni_spbu.json`, opsi isi bensin hanya memicu efek dialog `ledger_expense` dan `start_activity: "isi_bensin_motor"`.
  - Pada `dialogueBox.js`, penanganan `start_activity` hanya memunculkan animasi `showTimeSkip` dan memajukan jam 30 menit. Tidak ada satu baris kode pun yang mengubah `state.gasoline` atau memanggil fungsi pengisian BBM domain.
  - Di sisi HUD, widget status waktu dan bar bensin (`hud.js`) hanya membaca nilai pasif saat event tertentu, tanpa berlangganan event domain bertipe `fuelChanged`.
  - **Mengapa lolos tes sebelumnya:** Skrip tes otomatis sebelumnya menggunakan jalan pintas hook `window.__LJ__.setGasoline(100)` alih-alih berinteraksi lewat klik UI SPBU nyata.
- **Solusi V5 (Rule 78 & 79):**
  - Menerapkan fungsi domain `fuel.refuelPercent(n)` atau `refuelAmount(amount)` yang menambah `state.gasoline` dan memancarkan event bertipe `fuelChanged`.
  - Bar bensin di `hud.js` mendaftar sebagai pelanggan (*subscriber*) event `fuelChanged` dan mengupdate lebar bar serta teks persentase seketika (animasi transisi $\le 200\text{ ms}$).
  - Membuat panel SPBU khusus dengan opsi preset Rp10.000, Rp20.000, Rp30.000, dan *"Isi Penuh"* dengan pengecekan batas maksimal 100%.

---

## 3. Posisi Nakas & Halangan Akses Kasur Kamar Pemain (Poin e)
- **Kondisi Saat Ini:**
  - Pada `home.layout.json`:
    - Kasur kamar pemain (`fur_kasur_single`) berada di $x=4.5, y=2, w=2, h=3$ (merentang dari $x=4.5$ hingga $6.5$, dan $y=2$ hingga $5$).
    - Titik interaksi tidur (`int_kasur`) terletak di $x=4.5, y=3, w=2, h=2$.
    - Nakas lampu (`fur_nakas_lampu`) ditempatkan di $x=6.8, y=3.5, w=1, h=1.5$ dengan status kolisi aktif (`collidable: true`).
    - Di sisi kiri kasur terdapat lemari pakaian (`x=2..4`), menyisakan celah sempit hanya $0.5\text{ tile}$ ($16\text{ px}$) yang tidak muat dilewati pemain (lebar collider pemain $24\text{ px}$).
    - Di sisi kanan kasur, penempatan nakas pada $y=3.5$ menonjol ke bawah dan mempersempit koridor jalan. Saat pemain mencoba mendekati kasur dari bawah atau samping, pemain bertabrakan dengan nakas dan batas bawah kasur sebelum mencapai radius interaksi tidur.
- **Solusi V5 (Rule 73 §8):**
  - Menggeser posisi nakas kamar pemain menempel pada dinding belakang di samping kepala kasur: $x=6.8, y=2.0$ (sama dengan $y$ kepala kasur).
  - Dengan pergeseran ini, seluruh area samping kasur ($y=3.0..5.0$) dan area kaki kasur terbuka lapang (lebar $\ge 2\text{ tile}$), menjamin pemain dapat berjalan langsung dari pintu kamar ke kasur tanpa halangan fisik.

---

## 4. Penyelarasan Katalog Item & Aset Ikon (Poin c)
- **Hasil Pemeriksaan Berkas:**
  - Seluruh 16 ikon pada `assets/items/` tersedia lengkap dan dalam format pixel art $32\times 32$ transparan:
    `item_air_mineral`, `item_bakso`, `item_coklat_batang`, `item_es_teh`, `item_gorengan`, `item_isotonik`, `item_jus_kotak`, `item_keripik`, `item_mie_cup`, `item_mie_goreng`, `item_nasi_goreng`, `item_nasi_kuning`, `item_pisang`, `item_roti_isi`, `item_susu_kotak`, `item_teh_kemasan`.
  - Pada `items.phase1.json`, seluruh 16 item tersebut ada, namun properti `"icon"` belum diisi (`null`), dan belum memiliki kategori `game_center` pada `sellAt`.
- **Rencana Penyelarasan:**
  - Mengisi properti `"icon": "assets/items/item_<id>.png"` pada seluruh item.
  - Menambahkan kategori tipe dari `items-types.v5.json`.
  - Menambahkan item konsumsi kafe game center (`air_mineral`, `isotonik`, `keripik`, `es_teh`).

---

## 5. Analisis Input Gerak Click-to-Move (Poin f)
- **Kondisi Saat Ini:**
  - `PlayerController` (`player.js`) hanya membaca input keyboard: `this.cursors` (panah) dan `this.wasd`.
  - Canvas game belum memiliki listener `pointerdown` untuk navigasi.
- **Rencana Implementasi V5 (Rule 81):**
  - Membangun `NavigationGrid` per peta dengan resolusi grid sel $8\text{ px}$ berbasis collider physics yang diperbesar (*inflated*) setengah collider kaki pemain.
  - Mengimplementasikan algoritma A* pathfinding dengan pemangkasan sudut (*corner cutting prevention*) dan penghalusan jalur (*path smoothing*).
  - Menambahkan penanda tujuan (*destination marker*) cincin berdenyut di titik klik dunia.
  - Mendukung auto-interaksi (tekan E otomatis) saat pemain tiba di target interactable/NPC.
  - Membatalkan gerak klik saat tombol WASD/panah ditekan, atau saat Esc/dialog dibuka.
  - Mengabaikan klik jika mengenai elemen DOM UI (HUD, hotbar, panel, popup).

---

## 6. Audit Keaslian Aset (Poin g & Rule 78 §5)
- **Hasil Audit Piksel:**
  - Dari 301 file PNG pada direktori aset, **0 aset furnitur berupa kotak placeholder**.
  - Seluruh 46 perabot yang sebelumnya bermasalah telah diganti dengan sprite pixel art 16-bit asli transparan dengan palet warna kaya.
  - Aset dengan warna rendah hanya ikon energi kecil ($16\times 16$) dan prop bangku jalanan sederhana.

