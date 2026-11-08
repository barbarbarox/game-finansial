# Spesifikasi Tata Letak (Layout Spec): Pixel Arena Game Center (game_center)

Peta ID: `game_center`  
Ukuran: 26 x 18 tile (832 x 576 px)  
Ukuran Tile: 32 x 32 px  
Tipe: Interior Hiburan & Kafe (Rule 70 & Rule 73)

---

## 1. Denah Skematis Game Center

```
      x=2                                                 x=24
y=2   +---------------------------------------------------+
      | ARCADE A (x3)  ARCADE B (x3)   TV BESAR + STAND   |
      | (Dinding Belakang: wallBaseY = y=5)               |
y=5   +---------------------------------------------------+
      |                                                   |
      |   [MESIN CAPIT]             [SOFA NONTON 1]       |
y=8   |   (2x3 tile)                (3x2 tile)            |
      |                                                   |
      |                             [SOFA NONTON 2]       |
y=11  |                                                   |
      |                                                   |
y=12  | COUNTER KAFE & KOIN         MEJA KAFE (x3)        |
      | (x:3..7, y:12)              + KURSI BULAT         |
y=15  |                  [PINTU EXIT]                     |
y=16  +---------------------------------------------------+
```

---

## 2. Rincian Slot Sesuai Katalog v4

### 2.1. Dinding Belakang Utara (`wallBaseY = 5`)
- `furn_arcade_a_v4` x3 (`wall_back`, 48x96 px, pos `x: 3, y: 2`, `x: 5, y: 2`, `x: 7, y: 2`, dasar `y: 5`).
- `furn_arcade_b_v4` x3 (`wall_back`, 48x96 px, pos `x: 10, y: 2`, `x: 12, y: 2`, `x: 14, y: 2`, dasar `y: 5`).
- `furn_tv_besar_v4` (`wall_back`, 96x64 px, pos `x: 17, y: 3`, dasar `y: 5`).
- `furn_dispenser_galon_v4` (`wall_back`, 32x64 px, pos `x: 21, y: 3`, dasar `y: 5`).
- `furn_poster_kosong_v4` x2 (`wall_decor`, pos `x: 9, y: 1.5`, `x: 16, y: 1.5`).

### 2.2. Area Lounge, Nonton, dan Mesin Capit
- `furn_mesin_capit_v4` (`free`, 64x96 px, pos `x: 4, y: 7`).
- `furn_sofa_nonton_v4` x2 (`free`, 96x64 px, pos `x: 17, y: 7`, `x: 17, y: 10`).
- `furn_tanaman_pot_v4` (`free`, 32x48 px, pos `x: 21, y: 7.5`).

### 2.3. Area Counter Kafe & Meja Santai
- `furn_counter_kafe_v4` (`wall_back`, 128x64 px, pos `x: 3, y: 12`) — kasir koin arcade & kafe.
- `furn_meja_kafe_v4` x3 (`cluster`, 48x48 px, pos `x: 10, y: 13`, `x: 14, y: 13`, `x: 18, y: 13`).
- `furn_kursi_kafe_v4` x6 (`cluster`, 32x48 px, dua kursi per meja kafe).
- Pintu Masuk / Exit: `x: 13, y: 15` (menuju `town_hub`).
- **NPC Operator Game:** berdiri di balik meja counter `x: 5, y: 11`.

