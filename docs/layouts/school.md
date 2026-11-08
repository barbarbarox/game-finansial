# Spesifikasi Tata Letak (Layout Spec): SMA Negeri 1 (school)

Peta ID: `school`  
Ukuran: 32 x 22 tile (1024 x 704 px)  
Ukuran Tile: 32 x 32 px  
Tipe: Interior (Rule 70 & Rule 73)

---

## 1. Denah Skematis Ruangan

```
      x=2                 x=16                x=30
y=2   +-------------------+-------------------+
      |  RUANG KELAS      |  KANTIN SEKOLAH   |
      |  (Lantai Kayu)    |  (Keramik Kantin) |
      |  (14 x 10)        |  (14 x 10)        |
y=11  +-------------------+-------------------+
y=12  |  PERPUSTAKAAN     |  LOBBY UTAMA      |
      |  (14 x 9)         |  (PINTU MASUK)    |
      |                   |  (14 x 9)         |
y=20  +-------------------+-------------------+
```

---

## 2. Rincian Ruangan & Penataan Slot

### 2.1. Ruang Kelas (`school.kelas`)
- **Lantai:** Kayu kelas (`x: 2..15, y: 2..11`).
- **Garis Dasar Dinding Belakang (`wallBaseY`):** `y = 4`.
- **Dinding Belakang:**
  - `furn_papan_tulis_v4` (`wall_decor`, 128x64 px, pos `x: 6, y: 2`).
  - `furn_jam_dinding_v4` (`wall_decor`, 32x32 px, pos `x: 12, y: 2`).
  - `furn_meja_guru_v4` (`wall_back`, 96x64 px, pos `x: 7, y: 3.5`, dasar `y: 5.5`) — terhubung dengan guru/pelajaran.
  - `furn_kursi_guru_v4` (`cluster`, 32x48 px, pos `x: 8, y: 3`).
- **Grid Meja Siswa (Rule 73 §4: Grid Rapi):**
  - Kolom 1 (kiri):
    - `furn_meja_siswa_v4` (`grid`, 96x48 px, pos `x: 4, y: 6`) + `furn_kursi_siswa_v4` x2 di belakangnya (`x: 4.5, y: 7.5`, `x: 6, y: 7.5`).
    - `furn_meja_siswa_v4` (`grid`, 96x48 px, pos `x: 4, y: 9`) + `furn_kursi_siswa_v4` x2 di belakangnya (`x: 4.5, y: 10.5`, `x: 6, y: 10.5`).
  - Kolom 2 (kanan):
    - `furn_meja_siswa_v4` (`grid`, 96x48 px, pos `x: 9, y: 6`) + `furn_kursi_siswa_v4` x2 di belakangnya (`x: 9.5, y: 7.5`, `x: 11, y: 7.5`).
    - `furn_meja_siswa_v4` (`grid`, 96x48 px, pos `x: 9, y: 9`) + `furn_kursi_siswa_v4` x2 di belakangnya (`x: 9.5, y: 10.5`, `x: 11, y: 10.5`).
  - Lorong tengah selebar 2 tile bebas hambatan antara kolom 1 dan kolom 2.
- **Dinding Samping & Belakang:**
  - `furn_rak_buku_v4` (`wall_back`, 64x96 px, pos `x: 2, y: 4`).
  - `furn_tempat_sampah_v4` (`free`, 32x32 px, pos `x: 2, y: 9`).
  - `furn_jendela_v4` x4 (`wall_decor` pada dinding barat).

### 2.2. Kantin Sekolah (`school.kantin`)
- **Lantai:** Keramik kantin (`x: 16..30, y: 2..11`).
- **Garis Dasar Dinding Belakang (`wallBaseY`):** `y = 5`.
- **Dinding Belakang:**
  - `furn_counter_kantin_etalase_v4` (`wall_back`, 160x80 px, pos `x: 18, y: 2.5`, dasar `y: 5`) — terhubung dengan `shopId: kantin`.
  - `furn_kulkas_minuman_v4` (`wall_back`, 64x96 px, pos `x: 24, y: 2`, dasar `y: 5`).
  - `furn_dispenser_galon_v4` (`wall_back`, 32x64 px, pos `x: 26, y: 3`, dasar `y: 5`).
  - `furn_wastafel_cuci_tangan_v4` (`wall_back`, 48x64 px, pos `x: 28, y: 3`, dasar `y: 5`).
  - `furn_papan_menu_kosong_v4` (`wall_decor`, pos `x: 19, y: 1.5`).
- **Area Makan Siswa:**
  - `furn_meja_kantin_panjang_v4` (`free`, 96x64 px, pos `x: 18, y: 8`) + `furn_bangku_kantin_v4` x2 (`x: 18, y: 7`, `x: 18, y: 10`).
  - `furn_meja_kantin_panjang_v4` (`free`, 96x64 px, pos `x: 23, y: 8`) + `furn_bangku_kantin_v4` x2 (`x: 23, y: 7`, `x: 23, y: 10`).
  - `furn_tempat_sampah_v4` (`free`, pos `x: 28, y: 9`).
- **NPC Penjual Kantin (Ibu Sri):** berdiri di belakang counter kantin `x: 20, y: 3`.

### 2.3. Perpustakaan (`school.perpustakaan`)
- **Lantai:** Kayu perpus (`x: 2..15, y: 12..20`).
- **Penataan Slot:**
  - `furn_counter_pustakawan_v4` (`wall_back`, 96x64 px, pos `x: 4, y: 13`).
  - `furn_komputer_meja_v4` (`free`, 48x48 px, pos `x: 7, y: 13.5`).
  - `furn_rak_buku_perpus_v4` x4 (`wall_back`, 64x96 px) berderet di dinding barat dan selatan.
  - `furn_meja_baca_v4` x2 (`cluster`, 96x64 px, pos `x: 4, y: 17`, `x: 9, y: 17`) + `furn_kursi_baca_v4` x4.
  - `furn_papan_info_v4` (`wall_decor`, pos `x: 8, y: 12.5`).

### 2.4. Lobby & Pintu Masuk (`school.lobby`)
- **Lantai:** Keramik lobby (`x: 16..30, y: 12..20`).
- **Pintu Masuk/Keluar:** `x: 16, y: 19` (terhubung ke `town_hub`).
- **Penataan Slot:**
  - `furn_papan_pengumuman_v4` (`wall_decor`, pos `x: 20, y: 12.5`).
  - `furn_rak_piala_v4` (`wall_back`, 64x96 px, pos `x: 25, y: 13`).
  - `furn_bangku_tunggu_v4` x2 (`wall_back`, 96x32 px, pos `x: 19, y: 15`, `x: 25, y: 15`).
  - `furn_vas_tanaman_v4` x2 (`free`, pos `x: 18, y: 18`, `x: 28, y: 18`).

