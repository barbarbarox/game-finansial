# Spesifikasi Tata Letak (Layout Spec): Mini Mart Harmoni (minimarket)

Peta ID: `minimarket`  
Ukuran: 24 x 18 tile (768 x 576 px)  
Ukuran Tile: 32 x 32 px  
Tipe: Interior Toko (Rule 70 & Rule 73)

---

## 1. Denah Skematis Toko

```
      x=2                                         x=22
y=2   +-------------------------------------------+
      | CHILLER MINUMAN  ROTI  SNACK   FOTOKOPI   |
      | (Dinding Belakang: wallBaseY = y=5)       |
y=5   +-------------------------------------------+
      |                                           |
      |   [RAK GONDOLA 1]     [RAK GONDOLA 2]     |
y=8   |   (3x2 tile)          (3x2 tile)          |
      |                                           |
      |   [RAK GONDOLA 3]     [RAK GONDOLA 4]     |
y=11  |   (3x2 tile)          (3x2 tile)          |
      |                                           |
y=12  | KASIR & POS                     GALON     |
      | (x:4..7, y:12)                  KERANJANG |
y=15  |                  [PINTU EXIT]             |
y=16  +-------------------------------------------+
```

---

## 2. Rincian Slot Sesuai Katalog v4

### 2.1. Dinding Belakang Utara (`wallBaseY = 5`)
- `furn_kulkas_minuman_besar_v4` x2 (`wall_back`, 64x96 px, pos `x: 3, y: 2`, `x: 5, y: 2`, dasar `y: 5`).
- `furn_rak_roti_v4` (`wall_back`, 64x64 px, pos `x: 7, y: 3`, dasar `y: 5`).
- `furn_rak_mie_instan_v4` (`wall_back`, 64x80 px, pos `x: 9, y: 2.5`, dasar `y: 5`).
- `furn_rak_dinding_snack_v4` x2 (`wall_back`, 64x96 px, pos `x: 11, y: 2`, `x: 13, y: 2`, dasar `y: 5`).
- `furn_etalase_makanan_siap_saji_v4` (`wall_back`, 96x64 px, pos `x: 15, y: 3`, dasar `y: 5`).
- `furn_rak_alat_tulis_v4` (`wall_back`, 64x80 px, pos `x: 18, y: 2.5`, dasar `y: 5`).
- `furn_mesin_fotokopi_v4` (`wall_back`, 64x64 px, pos `x: 20, y: 3`, dasar `y: 5`).

### 2.2. Rak Gondola Tengah (Lorong Lega >= 2 Tile)
- Baris Depan:
  - `furn_rak_gondola_v4` (`free`, 96x64 px, pos `x: 4, y: 7`).
  - `furn_rak_gondola_v4` (`free`, 96x64 px, pos `x: 13, y: 7`).
- Baris Belakang:
  - `furn_rak_gondola_v4` (`free`, 96x64 px, pos `x: 4, y: 10`).
  - `furn_rak_gondola_v4` (`free`, 96x64 px, pos `x: 13, y: 10`).
- Lorong horizontal (antara dinding utara, gondola 1, gondola 2, dan kasir) selebar 2 tile bebas dilewati pemain.
- Lorong vertikal selebar 2–3 tile menghubungkan pintu ke lorong belanja.

### 2.3. Area Kasir & Pintu Masuk
- `furn_kasir_counter_v4` (`free`, 96x64 px, pos `x: 4, y: 13`) — terhubung dengan `shopId: minimarket`.
- `furn_keranjang_belanja_v4` (`free`, 32x32 px, pos `x: 8, y: 14`).
- `furn_galon_tumpuk_v4` (`free`, 32x48 px, pos `x: 19, y: 13`).
- `furn_tempat_sampah_v4` (`free`, 32x32 px, pos `x: 20, y: 14`).
- Pintu Masuk / Exit: `x: 12, y: 15` (menuju `town_hub`).
- **NPC Kasir:** berdiri di balik meja kasir `x: 5, y: 12`.

