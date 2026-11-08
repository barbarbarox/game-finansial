# Spesifikasi Tata Letak (Layout Spec): Toko Cantik Kosmetik (toko_kosmetik)

Peta ID: `toko_kosmetik`  
Ukuran: 22 x 16 tile (704 x 512 px)  
Ukuran Tile: 32 x 32 px  
Tipe: Interior Toko (Rule 70 & Rule 73)

---

## 1. Denah Skematis Toko

```
      x=2                                     x=20
y=2   +---------------------------------------+
      | RAK KOSMETIK DINDING (x3) SOFA TUNGGU |
      | (wallBaseY = y=5)                     |
y=5   +---------------------------------------+
      |                                       |
      |   [ETALASE KACA 1]   [ETALASE KACA 2] |
y=8   |   (3x2 tile)         (3x2 tile)       |
      |                                       |
      |   [MEJA CERMIN 1]    [MEJA CERMIN 2]  |
y=11  |   + KURSI TESTER     + KURSI TESTER   |
      |                                       |
y=12  |                   KASIR & POS         |
      |                   (x:13..15, y:12)    |
y=13  |           [PINTU EXIT]                |
y=14  +---------------------------------------+
```

---

## 2. Rincian Slot Sesuai Katalog v4

### 2.1. Dinding Belakang Utara (`wallBaseY = 5`)
- `furn_rak_dinding_kosmetik_v4` x3 (`wall_back`, 64x96 px, pos `x: 3, y: 2`, `x: 6, y: 2`, `x: 9, y: 2`, dasar `y: 5`).
- `furn_sofa_tunggu_v4` (`wall_back`, 64x64 px, pos `x: 15, y: 3`, dasar `y: 5`).
- `furn_poster_kosong_v4` x2 (`wall_decor`, 48x64 px, pos `x: 12, y: 2`, `x: 18, y: 2`).

### 2.2. Area Etalase & Pengujian Tester
- `furn_etalase_kaca_v4` x2 (`free`, 96x64 px, pos `x: 4, y: 6`, `x: 12, y: 6`).
- `furn_meja_cermin_v4` x2 (`cluster`, 64x80 px, pos `x: 4, y: 9`, `x: 8, y: 9`).
- `furn_kursi_cermin_v4` x2 (`cluster`, 32x48 px, pos `x: 4.5, y: 11`, `x: 8.5, y: 11`).

### 2.3. Area Kasir & Pintu Masuk
- `furn_kasir_kecil_v4` (`free`, 80x64 px, pos `x: 13, y: 10`) — terhubung dengan `shopId: toko_kosmetik`.
- `furn_keranjang_belanja_v4` (`free`, 32x32 px, pos `x: 17, y: 11`).
- `furn_tanaman_pot_v4` (`free`, 32x48 px, pos `x: 18, y: 12`).
- Pintu Masuk / Exit: `x: 11, y: 13` (menuju `town_hub`).
- **NPC Penjaga Toko (Mbak Maya):** berdiri di balik counter kasir `x: 14, y: 9`.

