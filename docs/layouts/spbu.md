# Spesifikasi Tata Letak (Layout Spec): Kios SPBU Harmoni (spbu)

Peta ID: `spbu`  
Ukuran: 24 x 18 tile (768 x 576 px)  
Ukuran Tile: 32 x 32 px  
Tipe: Interior Kios & Fasilitas SPBU (Rule 70 & Rule 73)

---

## 1. Denah Skematis Kios SPBU

```
      x=2                                         x=22
y=2   +-------------------------------------------+
      | RAK OLI  KIOSK KASIR & ETALASE  BANGKU    |
      | (Dinding Belakang: wallBaseY = y=5)       |
y=5   +-------------------------------------------+
      |                                           |
      |   [TIANG KANOPI 1]     [TIANG KANOPI 2]   |
y=7   |                                           |
      |   [DISPENSER BBM 1]    [DISPENSER BBM 2]  |
y=9   |   (Pulau Pompa 1)      (Pulau Pompa 2)    |
      |                                           |
y=11  |   [TIANG KANOPI 3]     [TIANG KANOPI 4]   |
      |                                           |
y=13  | KOMPRESOR ANGIN BAN       TABUNG PEMADAM  |
      | (x:3, y:13)               (x:20, y:13)    |
y=15  |                  [PINTU EXIT]             |
y=16  +-------------------------------------------+
```

---

## 2. Rincian Slot Sesuai Katalog v4

### 2.1. Dinding Belakang Utara (`wallBaseY = 5`)
- `furn_rak_oli_v4` (`wall_back`, 64x80 px, pos `x: 3, y: 2.5`, dasar `y: 5`).
- `furn_kiosk_spbu_v4` (`wall_back`, 128x96 px, pos `x: 6, y: 2`, dasar `y: 5`) — loket pembayaran bensin.
- `furn_bangku_spbu_v4` (`wall_back`, 64x32 px, pos `x: 12, y: 4`, dasar `y: 5`).
- `furn_tong_pemadam_v4` (`wall_back`, 32x40 px, pos `x: 16, y: 3.5`, dasar `y: 5`).
- `furn_tempat_sampah_v4` (`free`, 32x32 px, pos `x: 18, y: 4`).

### 2.2. Pulau Pompa Dispenser BBM & Kanopi
- `furn_tiang_kanopi_v4` x4 (`free`, 32x128 px):
  - Tiang barat laut: `x: 5, y: 7`
  - Tiang timur laut: `x: 16, y: 7`
  - Tiang barat daya: `x: 5, y: 11`
  - Tiang timur daya: `x: 16, y: 11`
- `furn_dispenser_bbm_v4` x2 (`free`, 48x96 px):
  - Pompa 1: `x: 8, y: 8` — terhubung dengan aktivitas isi bensin.
  - Pompa 2: `x: 13, y: 8` — terhubung dengan aktivitas isi bensin.

### 2.3. Fasilitas Servis & Pintu Keluar
- `furn_kompresor_angin_v4` (`free`, 32x48 px, pos `x: 3, y: 13`) — isi angin ban.
- Pintu Masuk / Exit: `x: 12, y: 15` (menuju `town_hub`).
- **NPC Petugas SPBU (Bang Dodi):** pos `x: 7, y: 5`.

