# Spesifikasi Tata Letak (Layout Spec): Rumah Pemain (home)

Peta ID: `home`  
Ukuran: 30 x 20 tile (960 x 640 px)  
Ukuran Tile: 32 x 32 px  
Tipe: Interior (Rule 70 & Rule 73)

---

## 1. Denah Skematis Ruangan

```
      x=2                 x=11                x=21        x=28
y=2   +-------------------+-------------------+-----------+
      |  KAMAR PEMAIN     |  KAMAR ORANG TUA  |   KAMAR   |
      |  (Kayu 9x8)       |  (Kayu 9x8)       |   MANDI   |
      |                   |                   | (Ubin 6x8)|
y=9   +===== [PINTU] =====+===== [PINTU] =====+== [PINTU] =+
y=10  |                   | LORONG            |           |
      |  RUANG TAMU       | TENGAH            |   DAPUR   |
      |  (Keramik 11x9)   | (1x9)             |  & MAKAN  |
      |                   |                   |(Ubin 14x9)|
y=18  |                   |   [PINTU UTAMA]   |           |
y=19  +-------------------+-------------------+-----------+
```

---

## 2. Rincian Ruangan & Penataan Slot

### 2.1. Dapur & Ruang Makan (`home.dapur_makan`)
- **Lantai:** Ubin hijau muda / keramik dapur (`x: 14..28, y: 10..19`).
- **Garis Dasar Dinding Belakang (`wallBaseY`):** `y = 13` (tile y=13, garis dasar sprite).
- **Deretan Counter Kontinu (Rule 73 §4):**
  Tersusun rapat dari kiri ke kanan tanpa celah di dinding utara:
  1. `furn_kulkas_v4` (`counter_module`, 64x96 px, pos `x: 15, y: 10`, dasar `y: 13`).
  2. `furn_counter_polos_v4` (`counter_module`, 64x64 px, pos `x: 17, y: 11`, dasar `y: 13`).
  3. `furn_counter_kompor_v4` (`counter_module`, 64x64 px, pos `x: 19, y: 11`, dasar `y: 13`) — terhubung dengan `int_dapur`.
  4. `furn_counter_wastafel_v4` (`counter_module`, 64x64 px, pos `x: 21, y: 11`, dasar `y: 13`).
  5. `furn_counter_polos_v4` (`counter_module`, 64x64 px, pos `x: 23, y: 11`, dasar `y: 13`).
  6. `furn_dispenser_galon_v4` (`wall_back`, 32x64 px, pos `x: 25, y: 11`, dasar `y: 13`).
  7. `furn_tempat_sampah_v4` (`free`, 32x32 px, pos `x: 26, y: 12`, dasar `y: 13`).
- **Wall Decor (Menggantung di Muka Dinding):**
  - `furn_jendela_dapur_v4` (`wall_decor`, pos `x: 17, y: 9.5`).
  - `furn_rak_bumbu_dinding_v4` (`wall_decor`, pos `x: 19, y: 9.5`).
  - `furn_rak_piring_dinding_v4` (`wall_decor`, pos `x: 21, y: 9.5`).
- **Kluster Meja Makan di Tengah Ruang:**
  - `furn_meja_makan_v4` (`cluster`, 96x64 px, pos `x: 18, y: 15`) — terhubung dengan `int_makan`.
  - `furn_kursi_makan_kiri_v4` (`cluster`, 32x48 px, pos `x: 17, y: 15.5`).
  - `furn_kursi_makan_kanan_v4` (`cluster`, 32x48 px, pos `x: 21, y: 15.5`).
  - `furn_kursi_makan_depan_v4` (`cluster`, 32x48 px, pos `x: 18.5, y: 17`).
  - `furn_kursi_makan_depan_v4` (`cluster`, 32x48 px, pos `x: 19.5, y: 17`).
- **Penempatan NPC Ibu:**
  - Posisi berdiri di depan kompor: `x: 20, y: 14`, menghadap ke atas/utara menghadap kompor.

### 2.2. Kamar Mandi (`home.kamar_mandi`)
- **Lantai:** Keramik kamar mandi (`x: 22..28, y: 2..10`).
- **Garis Dasar Dinding Belakang (`wallBaseY`):** `y = 4`.
- **Penataan Objek Sesuai Rule 73 §4:**
  - `furn_bak_mandi_v4` (`wall_back`, 64x64 px, pos `x: 22, y: 2`, dasar `y: 4`) — terhubung dengan `int_bak_mandi`.
  - `furn_ember_v4` (`free`, 32x32 px, pos `x: 24, y: 3`, dasar `y: 4`).
  - `furn_toilet_v4` (`wall_back`, 32x48 px, pos `x: 26, y: 2.5`, dasar `y: 4`).
  - `furn_wastafel_cermin_v4` (`wall_back`, 64x80 px, pos `x: 25, y: 5.5`, dasar `y: 8`).
  - `furn_rak_handuk_v4` (`wall_back`, 32x64 px, pos `x: 22, y: 5`, dasar `y: 7`).
  - `furn_tempat_sampah_v4` (`free`, 32x32 px, pos `x: 27, y: 4`).
  - `furn_keset_v4` (`floor_decal`, 64x32 px, pos `x: 23, y: 8`).
  - Jalur pintu masuk bebas tanpa rintangan.

### 2.3. Ruang Tamu (`home.ruang_tamu`)
- **Lantai:** Keramik ruang tamu (`x: 2..13, y: 10..19`).
- **Garis Dasar Dinding Belakang (`wallBaseY`):** `y = 12`.
- **Penataan Objek Sesuai Rule 73 §4:**
  - `furn_rak_pajangan_v4` (`wall_back`, 64x96 px, pos `x: 2, y: 9`, dasar `y: 12`).
  - `furn_tv_dan_rak_v4` (`wall_back`, 96x64 px, pos `x: 5, y: 10`, dasar `y: 12`) — terhubung dengan `int_tv`.
  - `furn_tanaman_pot_v4` (`free`, 32x48 px, pos `x: 8, y: 10.5`).
  - `furn_sofa_single_v4` (`wall_back`, 64x64 px, pos `x: 9, y: 10`, dasar `y: 12`).
  - **Kluster Santai:**
    - `furn_karpet_tamu_v4` (`floor_decal`, 128x96 px, pos `x: 4, y: 13`).
    - `furn_sofa_3dudukan_v4` (`wall_back`, 128x64 px, pos `x: 4, y: 12`, dasar `y: 14`).
    - `furn_meja_tamu_v4` (`free`, 64x48 px, pos `x: 5, y: 14.5`).
    - `furn_sofa_single_v4` (`free`, 64x64 px, pos `x: 2, y: 13.5`).
  - `furn_kipas_berdiri_v4` (`free`, 32x64 px, pos `x: 11, y: 12`).
  - `furn_rak_sepatu_v4` (`wall_back`, 64x48 px, pos `x: 10, y: 17`).
  - `furn_tanaman_pot_v4` (`free`, 32x48 px, pos `x: 9, y: 17`).
  - `furn_jam_dinding_v4` (`wall_decor`, pos `x: 7, y: 9.5`).
  - `furn_bingkai_kosong_v4` (`wall_decor`, pos `x: 4, y: 9.5`).

### 2.4. Kamar Tidur Pemain (`home.kamar_pemain`)
- **Lantai:** Kayu kamar (`x: 2..11, y: 2..10`).
- **Garis Dasar Dinding Belakang (`wallBaseY`):** `y = 5`.
- **Penataan Objek:**
  - `furn_lemari_pakaian_v4` (`wall_back`, 64x96 px, pos `x: 2, y: 2`, dasar `y: 5`).
  - `furn_kasur_single_v4` (`wall_back`, 64x96 px, pos `x: 4, y: 2`, dasar `y: 5`) — terhubung dengan `int_kasur`.
  - `furn_nakas_lampu_v4` (`wall_back`, 32x48 px, pos `x: 6, y: 3.5`, dasar `y: 5`).
  - `furn_cermin_berdiri_v4` (`wall_back`, 32x80 px, pos `x: 7, y: 2.5`, dasar `y: 5`).
  - `furn_rak_buku_v4` (`wall_back`, 64x96 px, pos `x: 8, y: 2`, dasar `y: 5`).
  - `furn_meja_belajar_v4` (`cluster`, 96x64 px, pos `x: 6, y: 6`) — terhubung dengan `int_meja_belajar`.
  - `furn_kursi_belajar_v4` (`cluster`, 32x48 px, pos `x: 7, y: 8`).
  - `furn_celengan_ayam_v4` (`free`, 32x32 px, pos `x: 8, y: 6`) — terhubung dengan `int_celengan`.
  - `furn_keranjang_baju_v4` (`free`, 32x32 px, pos `x: 2, y: 6`).
  - `furn_tempat_sampah_v4` (`free`, 32x32 px, pos `x: 2, y: 7`).
  - `furn_karpet_kecil_v4` (`floor_decal`, 96x64 px, pos `x: 3, y: 5`).
  - `furn_jendela_v4` (`wall_decor`, pos `x: 5, y: 1.5`).

### 2.5. Kamar Tidur Orang Tua (`home.kamar_ortu`)
- **Lantai:** Kayu kamar (`x: 12..21, y: 2..10`).
- **Garis Dasar Dinding Belakang (`wallBaseY`):** `y = 5`.
- **Penataan Objek:**
  - `furn_nakas_lampu_v4` (`wall_back`, 32x48 px, pos `x: 13, y: 3.5`, dasar `y: 5`).
  - `furn_kasur_besar_v4` (`wall_back`, 96x112 px, pos `x: 14, y: 2`, dasar `y: 5.5`).
  - `furn_nakas_lampu_v4` (`wall_back`, 32x48 px, pos `x: 17, y: 3.5`, dasar `y: 5`).
  - `furn_lemari_besar_v4` (`wall_back`, 96x96 px, pos `x: 18, y: 2`, dasar `y: 5`).
  - `furn_meja_rias_v4` (`wall_back`, 64x80 px, pos `x: 12, y: 6`).
  - `furn_kursi_rias_v4` (`cluster`, 32x40 px, pos `x: 13, y: 7.5`).
  - `furn_kipas_berdiri_v4` (`free`, 32x64 px, pos `x: 19, y: 6`).
  - `furn_karpet_besar_v4` (`floor_decal`, 128x80 px, pos `x: 14, y: 6`).
  - `furn_jendela_v4` (`wall_decor`, pos `x: 15, y: 1.5`).

