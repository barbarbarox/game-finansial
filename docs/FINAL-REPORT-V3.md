# LAPORAN AKHIR EKSPANSI v3: LIFE JOURNEY

**Proyek:** Life Journey — Simulasi Kehidupan & Literasi Finansial Pelajar SMA  
**Cakupan:** Ekspansi v3 (Gerbang E0 – E9: Interior, Sistem Waktu, Dialog Potret, 7 Peta, QA Multi-Hari)  
**Status:** **SELESAI & TERVERIFIKASI PENUH (E0–E9 LULUS 100%)**  
**Tanggal:** 2026-11-08  
**Tag Git:** `v3-expansion-complete` (pra-ekspansi: `pre-expansion`)  

---

## 1. Ringkasan Eksekutif

Ekspansi v3 game web statis *Life Journey* telah berhasil diselesaikan secara otonom dari gerbang E0 sampai E9 sesuai spesifikasi teknis (`70-interior-maps.md`, `71-dialogue-system.md`, `72-time-system.md`, `AUTOPILOT-EXPANSION.md`) dan arahan pengguna.

Semua fitur baru terintegrasi mulus dengan tetap **menjaga 100% kustomisasi UI manual pengguna** (widget jam Harvest Moon di kiri-atas, tombol aksi cepat di kanan-atas, toggle Dark/Light mode, indikator nama NPC mengambang, serta badge status).

Masalah tampilan map bleed (tampilan interior dan eksterior kota bercampur aduk) telah **diperbaiki tuntas** melalui arsitektur isolasi layer MapManager dengan latar belakang solid void (`0x0A0F1A`) berkedalaman -200, serta penataan seluruh furnitur interior rumah (kamar tidur, ruang keluarga, dapur, kamar mandi, kamar ortu) yang rapi, proporsional, dan tidak tertutup HUD.

---

## 2. Fitur Utama Ekspansi v3

### A. Sistem Waktu & Siklus Kehidupan (Rule 72)
- **Rasio Waktu:** 1 detik dunia nyata = 1 menit waktu game (60 detik = 1 jam).
- **Fase Waktu & Langit Dinamis:** Pagi (06:00–11:59), Siang (12:00–14:59), Sore (15:00–17:59), Malam (18:00–05:59) yang secara dinamis memperbarui warna latar langit dan ikon fase pada widget Harvest Moon.
- **Jam Operasional Realistis:**
  - Sekolah Harmoni: 06:30 – 15:30 (Kantin: 06:30 – 15:00, Sabtu/Minggu Libur).
  - Minimarket Harmoni: 07:00 – 22:00.
  - Toko Kosmetik Cantik: 09:00 – 20:00.
  - SPBU Harmoni: 06:00 – 23:00.
  - Game Center Harmoni: 10:00 – 22:00.
- **Aktivitas Berbiaya Waktu:** Belajar di kelas (+420 menit), makan siang (+20 menit), mandi (+15 menit), sarapan (+20 menit), main arcade (+60 menit), tidur malam memajukan hari ke pukul 06:00 hari berikutnya.

### B. Kerangka Peta Interior & Hub Separation (Rule 70)
- **7 Peta Terintegrasi Penuh:**
  1. `town_hub` (Peta kota luar dengan gedung-gedung dan pintu masuk).
  2. `home` (Rumah 5 ruangan: Kamar Pemain, Kamar Ortu, Ruang Tamu, Dapur, Kamar Mandi).
  3. `school` (Sekolah: Ruang Kelas, Kantin Sekolah, Perpustakaan).
  4. `minimarket` (Minimarket Harmoni: Rak belanja, kasir Mbak Maya).
  5. `toko_kosmetik` (Toko Kosmetik Cantik: Display produk, kasir Kak Cindy).
  6. `spbu` (SPBU Harmoni: Pompa bensin, loket Mas Doni).
  7. `game_center` (Game Center Harmoni: Mesin arcade, loket Kak Riko, teman Rani).
- **Zero Map Bleed:** MapManager mengisolasi 100% objek visual per peta. Saat memasuki interior, background void solid `0x0A0F1A` pada kedalaman -200 merender batas ruang secara independen, mencegah tampilan rumput/gedung luar kota merembes.
- **Transisi Timbal-Balik:** Seluruh pintu masuk dan keluar memiliki koordinat spawn timbal-balik yang telah diverifikasi keterjangkauannya via algoritma BFS (27/27 titik lolos).

### C. Sistem Dialog dengan Potret Karakter (Rule 71)
- **Visual Dialog Responsif:** Panel dialog split dua sisi (kiri-kanan) untuk Desktop (1200×800) dan Tablet (768×1024).
- **Efek Sorotan Pembicara:** Karakter yang sedang berbicara membesar (+6px) dan terang, sedangkan lawan bicara meredup (opasitas 0.55).
- **Karakter AI Nyata (Bukan Bentuk Primitif):** Mengganti bentuk lingkaran/kotak dengan potret wajah dan sprite karakter pixel-art berkarakter:
  - Keluarga: Ibu, Ayah, Pemain.
  - Teman: Budi, Siti, Rani.
  - Penjual & Staf: Bu Sri (Guru), Mbak Maya (Minimarket), Kak Cindy (Kosmetik), Mas Doni (SPBU), Kak Riko (Game Center).
- **Efek Dialog Whitelist:** Memberi uang saku bulanan, memotong saldo belanja kas, menambah saldo tabungan celengan, memajukan jam, dan berpindah peta.

### D. Penataan Interior Rumah Teratur & Furnitur Nyata
- **Kamar Pemain:** Tempat tidur single digeser ke koordinat `x:2, y:6` (terlihat jelas di bawah HUD Harvest Moon), meja belajar rapi, rak buku, celengan ayam interaktif, dan lemari pakaian.
- **Dapur & Ruang Makan:** Kompor counter 2 tungku, wastafel cuci piring, kulkas 2 pintu, meja makan kayu dengan kursi, dan Ibu yang memasak.
- **Kamar Mandi:** Bak mandi keramik lengkap dengan gayung, toilet duduk putih, wastafel cermin, dan rak handuk.
- **Ruang Keluarga:** Sofa 3 dudukan, karpet tenun, meja kopi kayu, kabinet TV, dan Ayah bersantai.

---

## 3. Matriks Hasil Pengujian & Verifikasi Otomatis

Semua pengujian dijalankan langsung pada mesin Chrome headless asli melalui protokol Chrome DevTools (CDP) dengan status **100% HIJAU / LULUS**:

| Rangkaian Pengujian | Jumlah Kasus | Status | Keterangan & Bukti |
|---|---|---|---|
| **Accounting Invariants** (`tests/self-test.html`) | 6 Invarian | **LULUS (6/6)** | Debit = Kredit seimbang, Kas ≥ 0, Penolakan saldo defisit, Integritas autosave LocalStorage |
| **Sistem Waktu & Aktivitas** (`tests/time-test.html`) | 12 Skenario | **LULUS (12/12)** | Live tick 1s=1m, advanceTime, fase langit pagi/siang/sore/malam, jam buka tutup toko, tidur |
| **Sistem Dialog & Potret** (`tests/dialogue-test.html`) | 21 Validasi | **LULUS (21/21)** | Validasi skema JSON, batas teks ≤140 karakter, transisi simpul, highlight pembicara, pilihan dinamis |
| **Reachability & Timbal Balik Peta** (`tests/map-check.html`) | 27 Titik / 7 Peta | **LULUS (27/27)** | Algoritma BFS membuktikan semua pintu, spawn, dan furnitur interaktif dapat dijangkau pemain |
| **Alur Hari 1 Rumah** (`tools/test_home_day1_flow.py`) | 5 Tahap | **LULUS (100%)** | Bangun tidur, sarapan, mandi, uang saku Ibu Rp1.000.000, celengan ayam, transisi hub |
| **Alur Sekolah Harmoni** (`tools/test_school_flow.py`) | 5 Tahap | **LULUS (100%)** | Jam sekolah, pelajaran kelas (waktu maju ke 14:30), kantin beli makan, dialog Bu Sri & Budi, tutup hari Sabtu |
| **Bangunan Komersial E8** (`tools/test_commercial_buildings.py`) | 4 Bangunan | **LULUS (100%)** | Minimarket, Toko Kosmetik, SPBU, Game Center; jam buka tertutup di luar jam; dialog potret + transaksi |
| **Simulasi Multi-Hari E2E E9** (`tools/test_e9_full_simulation.py`) | 3 Hari Penuh | **LULUS (100%)** | Siklus Senin–Rabu: Uang saku (M1), Sekolah, Jajan, Bensin (M3), Tabungan (M4), Game Center (M5), Audit Ledger (M6), Save & Reload |

---

## 4. Log Bukti Tangkapan Layar (Screenshots)

### E9 Multi-Day End-to-End Simulation (`docs/e9-integration/`)
- `01_day1_morning_home.png` — Permainan baru, pemain bangun tidur di kasur Senin 06:00 (di bawah HUD).
- `02_day1_ibu_allowance.png` — Dialog potret Ibu memberikan uang saku bulanan Rp1.000.000 (M1 selesai).
- `03_day1_school_arrival.png` — Kedatangan di Sekolah Harmoni jam pelajaran pagi.
- `04_day1_class_done.png` — Selesai mengikuti pelajaran di kelas, waktu maju tepat ke 14:30.
- `05_day1_canteen_lunch.png` — Membeli makan siang nasi kuning di kantin sekolah (Kas -Rp10.000).
- `06_day1_spbu_refuel.png` — Mengisi bensin motor di SPBU Harmoni bersama Mas Doni (M3 selesai).
- `07_day1_savings_deposited.png` — Menabung uang di celengan ayam kamar tidur (M4 selesai, Tabungan Rp100.000).
- `08_day2_kosmetik_purchase.png` — Hari ke-2 (Selasa): Belanja keperluan di Toko Kosmetik Cantik bersama Kak Cindy.
- `09_day3_game_center.png` — Hari ke-3 (Rabu): Bermain game arcade bersama Rani di Game Center Harmoni (M5 selesai).
- `10_day3_final_home.png` — Pulang ke rumah, verifikasi kondisi akhir seluruh invarian akuntansi (M6).
- `11_save_continue_restored.png` — Pengujian Save & Reload: Menu 'Lanjutkan Permainan' memulihkan posisi di rumah dan saldo kas Rp815.000 secara persisten.

### E8 Commercial Buildings (`docs/e8-commercial/`)
- `01_minimarket_interior.png` & `02_minimarket_maya_dialogue.png`
- `03_kosmetik_interior.png` & `04_kosmetik_cindy_dialogue.png`
- `05_spbu_interior.png` & `06_spbu_doni_dialogue.png`
- `07_game_center_interior.png`, `08_game_center_riko_dialogue.png`, `09_game_center_rani_dialogue.png`
- `10_town_hub_returned.png`

---

## 5. Ringkasan Keuangan Hasil Simulasi 3 Hari (Audit Ledger)

```json
{
  "totalEntries": 7,
  "totalIncome": 1000000,
  "totalExpense": 85000,
  "cash": 815000,
  "savings": 100000,
  "netWorth": 915000,
  "allEntriesBalanced": true,
  "cashPositive": true
}
```
- **Total Pemasukan:** Rp1.000.000 (Uang Saku Ibu)
- **Total Pengeluaran:** Rp85.000 (Kantin Rp10.000 + Bensin SPBU Rp20.000 + Skincare Rp25.000 + Camilan Minimarket Rp10.000 + Arcade Rp20.000)
- **Total Tabungan:** Rp100.000 (Celengan Ayam)
- **Sisa Kas Pegangan:** Rp815.000
- **Kekayaan Bersih (Net Worth):** Rp915.000 (Kas Rp815.000 + Tabungan Rp100.000 = Pemasukan Rp1.000.000 − Pengeluaran Rp85.000)
- **Invarian Matematika:** Σ Debit = Σ Kredit seimbang di setiap entri jurnal (100% valid).

---

## 6. Audit Keamanan & Kepatuhan Arsitektur

1. **Zero XSS / Zero Raw innerHTML:** Seluruh pembuatan elemen dinamis dialog, teks, dan nama menggunakan `document.createElement`, `textContent`, dan `setAttribute`.
2. **Validasi Skema Anti-Prototype Pollution:** Parser LocalStorage memvalidasi skema data JSON dan menolak kunci berbahaya (`__proto__`, `constructor`, `prototype`).
3. **Whitelist Efek Dialog:** Hanya efek yang terdaftar dalam katalog (`ledger_entry`, `advance_time`, `teleport_map`, `set_flag`) yang dapat dieksekusi oleh mesin dialog.
4. **Isolasi State Game:** Tidak ada global pollution di luar namespace resmi (`window.__LJ__` dan `window.__GAME__` untuk kemudahan pengujian).

---

## 7. Petunjuk Menjalankan Permainan

Permainan bersifat client-side murni tanpa backend. Jalankan web server lokal di folder `game`:

```bash
cd "game"
python3 -m http.server 3843
```

Akses melalui peramban web:
- **Game Utama:** `http://localhost:3843/`
- **Uji Invarian Keuangan:** `http://localhost:3843/tests/self-test.html`
- **Uji Sistem Waktu:** `http://localhost:3843/tests/time-test.html`
- **Uji Sistem Dialog & Potret:** `http://localhost:3843/tests/dialogue-test.html`
- **Uji Keterjangkauan Peta:** `http://localhost:3843/tests/map-check.html`
- **Uji Aset:** `http://localhost:3843/tests/asset-check.html`

Untuk menjalankan simulasi otomatis E2E:
```bash
python3 tools/test_e9_full_simulation.py
```
