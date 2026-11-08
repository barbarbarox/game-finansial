# Spesifikasi Tata Letak (Layout Spec): Pusat Kota Harmoni (town_hub)

Peta ID: `town_hub`  
Ukuran: 40 x 24 tile (1280 x 768 px)  
Ukuran Tile: 32 x 32 px  
Tipe: Eksterior / Hub Luar Ruang (Rule 70 & Rule 76)

---

## 1. Denah Skematis Eksterior

```
      x=0                 x=19    x=23                x=39
y=0   +-------------------+-------+-------------------+
      |                   | JALAN |                   |
      |   SEKOLAH SMAN 1  | UTARA | MINIMART  KOSMETIK|
      |   (x:10, y:9)     | (19-22| (x:27,y:8)(x:35,y:8|
y=9   +-------------------+   )   +-------------------+
      |                   |       |      SPBU         |
      |                   |       |   (x:36, y:14)    |
y=14  +===================+=======+===================+
      |      JALAN UTAMA TIMUR-BARAT (y: 14 - 17)     |
y=17  +===================+=======+===================+
      |                   | JALAN |                   |
      |   RUMAH PEMAIN    | SELAT |    GAME CENTER    |
      |   (x:6, y:22)     |  AN   |    (x:30, y:22)   |
y=23  +-------------------+-------+-------------------+
```

---

## 2. Struktur Bangunan & Pintu Masuk
Setiap bangunan eksterior memiliki pintu dengan interaksi `[E]` dan jadwal buka/tutup (Rule 72):
1. **SMA Negeri 1 (`bld_sekolah`):** pos `x: 10, y: 9`, footprint `w: 14, h: 4`, pintu `x: 10, y: 8` -> `school`.
2. **Rumah Pemain (`bld_rumah_pemain`):** pos `x: 6, y: 22`, footprint `w: 9, h: 3`, pintu `x: 6, y: 21` -> `home`.
3. **Minimarket (`bld_minimarket`):** pos `x: 27, y: 8`, footprint `w: 8, h: 3`, pintu `x: 27, y: 7` -> `minimarket`.
4. **Toko Kosmetik (`bld_toko_kosmetik`):** pos `x: 35, y: 8`, footprint `w: 7, h: 3`, pintu `x: 35, y: 7` -> `toko_kosmetik`.
5. **SPBU (`bld_spbu`):** pos `x: 36, y: 14`, footprint `w: 10, h: 4`, pintu `x: 36, y: 13` -> `spbu`.
6. **Game Center (`bld_game_center`):** pos `x: 30, y: 22`, footprint `w: 8, h: 3`, pintu `x: 30, y: 21` -> `game_center`.

---

## 3. Penempatan NPC Hub (Rule 73 §6)
- **Isolasi Total:** Tidak ada NPC interior (Ibu, Ayah, Kasir, Penjaga) di peta kota.
- **NPC Pejalan/Warga:**
  - `npc_teman` (Budi): berdiri di trotoar persimpangan `x: 18, y: 14`. Bebas oklusi.
  - `npc_pak_anto`: berdiri di trotoar timur `x: 29, y: 14`. Bebas oklusi dari bangunan mana pun.

---

## 4. Slot Dekorasi Jalan & Kolisi
- Jalur berkendara motor membentang di jalan utama (`y: 15..17`) dan jalan vertikal (`x: 20..22`).
- Kolisi batas luar di tepi peta 4 sisi mencegah pemain keluar dari area game.
- Parkir motor otomatis dipicu saat pemain memasuki pintu interior mana pun.

