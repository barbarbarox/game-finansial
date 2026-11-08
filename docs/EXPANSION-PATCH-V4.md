# EXPANSION-PATCH-V4 — perubahan pada file lama (diterapkan agen pada G0)
> Terapkan persis. Jika teks lama sudah berbeda (mis. Anda atau agen mengeditnya), terapkan *maksud* perubahan dan catat di `docs/DECISIONS.md`. Tampilkan `git diff --stat` sesudahnya. Jangan mengubah hal lain.

## Patch 1 — `AGENTS.md`
**Cari:**
```
- `72-time-system.md` — jam 24 jam, widget waktu, aktivitas yang memakan waktu, jam buka
```
**Ganti dengan:**
```
- `72-time-system.md` — jam 24 jam, widget waktu, aktivitas yang memakan waktu, jam buka
- `73-room-layout-and-collision.md` — tata letak berbasis slot, kolisi, NPC dan oklusi
- `74-energy-inventory-items.md` — energi, inventaris/hotbar, item makanan-minuman
- `75-vehicle-motor.md` — motor pemain, bensin per 5 detik
- `76-terrain-plate.md` — tanah peta kota dari image generation yang mengikuti layout
- `77-mission-complete-fx.md` — penanda misi selesai dan efek visual prosedural
```

## Patch 2 — `AGENTS.md`
**Cari:**
```
Catat apa yang dipertahankan di `docs/DECISIONS.md`.
```
**Ganti dengan:**
```
Catat apa yang dipertahankan di `docs/DECISIONS.md`.
14. **Tata letak dulu, aset menyusul; semua objek berkolisi dan teruji.** Rancang Layout Spec berbasis slot, generate aset untuk slot (bukan sebaliknya), validasi otomatis + tinjauan visual. Setiap objek non-dekoratif memiliki footprint kolisi dan lolos probe kolisi (`73-room-layout-and-collision.md`).
15. **Tidak ada NPC/objek hilang atau tertimpa.** Tiap NPC milik tepat satu peta; uji oklusi wajib hijau.
16. **Jangan mengklaim aset visual "sesuai" tanpa bukti:** tangkapan layar dengan overlay, hasil validator, dan perbandingan dengan `docs/reference/`. Aset lama dipertahankan sampai E2E lulus; aset baru bersufiks `_v4`.
```

## Patch 3 — `AGENTS.md`
**Cari:**
```
dan dinding prosedural sesuai `20-asset-pipeline.md` dan `70-interior-maps-and-buildings.md`)
```
**Ganti dengan:**
```
dan dinding prosedural sesuai `20-asset-pipeline.md` dan `70-interior-maps-and-buildings.md`; serta efek visual prosedural berupa partikel, cincin, kilau, dan debu sesuai `77-mission-complete-fx.md`)
```

## Patch 4 — `.agents/rules/40-phase1-game-design.md`
**Cari:**
```
- Bensin: indikator 0–100%, turun 5%/hari; isi Rp20.000 = +40%. Bensin 0% → pemain berjalan kaki lebih lambat dan memicu kejadian "terlambat".
```
**Ganti dengan:**
```
- Bensin: indikator 0–100%; **turun hanya saat bermotor** (per 5 detik penggunaan, lihat `75-vehicle-motor.md`; penurunan harian lama dihapus); isi Rp20.000 = +40%. Bensin 0% → pengendara dipaksa turun dan tombol motor nonaktif hingga diisi. Energi pemain (rule 74): 0–100, turun karena aktivitas, terisi dengan makan/minum/tidur.
```

## Patch 5 — `.agents/rules/20-asset-pipeline.md`
**Cari:**
```
`assets/` → `characters/`, `npcs/`, `portraits/`, `buildings/`, `furniture/`, `props/`, `backgrounds/`
```
**Ganti dengan:**
```
`assets/` → `characters/`, `npcs/`, `portraits/`, `buildings/`, `furniture/`, `props/`, `vehicles/`, `items/`, `terrain/` (guide, mask, plate, swatch), `decals/`, `backgrounds/`
```

## Tambah di akhir `.agents/rules/60-asset-generation-qa.md`
```
## 11. Mode generate v4
- **Furnitur turunan slot:** brief dibuat dari slot layout (`tools/derive_briefs_from_layout.py`) memakai `furnitureBriefTemplate` di `data/asset-briefs-v4.json`; satu sheet = 4–6 item dari ruang yang sama. Ukuran/kelas/arah dari slot. **Modul counter** harus tinggi dan garis dasarnya identik (±2 px) dengan sisi kiri/kanan dipotong datar agar menyambung; validator menghitung deretan.
- **Validator wajib (pelajaran Checkpoint A):** dasar sprite menempel baris terbawah untuk semua objek berkolisi; tidak ada komponen terhubung kecil (< 12 piksel) di luar subjek utama; tidak ada garis/titik artefak di tepi gambar; padding transparan hanya di atas/samping, tidak di bawah. Jangan menulis "N/A" untuk kelas aset apa pun.
- **Kandidat:** bila brief memuat `candidates: N`, hasilkan N variasi, bandingkan lewat QA + tinjauan visual terhadap `docs/reference/` dan bangunan lain, pilih satu, simpan sisanya di `assets/_rejected/`.
- **Generate terpandu:** terrain plate memakai gambar guide sebagai referensi dan uji kesesuaian (rule 76); tool tambahan `render_layout_guide`, `check_plate_conformance`, `check_swatch_seamless`.
- **Kendaraan multi-tampak:** motor (jangkar) → pengendara L/P dengan motor yang sama; QA warna motor konsisten antar-tampak dan antar-sheet.
- **Sheet ikon grid:** potong per sel, normalisasi 32×32, QA isi ≥ 60% sel, tanpa teks.
```

## Tambah di akhir `.agents/rules/72-time-system.md`
```
## 7. Integrasi energi (v4)
`advanceTime` memancarkan `energyChanged`; penguras pasif per jam, `energyCostPerHour` per aktivitas, dan pemulihan tidur/istirahat mengikuti `74-energy-inventory-items.md`. Katalog aktivitas mendapat field `energyCostPerHour` dan aturan penolakan bila energi tidak cukup. Makan/minum item memakai `advanceTime` untuk `consumeMinutes`. Konsumsi bensin motor **tidak** melalui `advanceTime` harian; ia mengikuti akumulator 5 detik di rule 75 (hanya saat bermotor).
```

## Tambah di akhir `.agents/rules/70-interior-maps-and-buildings.md`
```
## 11. Pembaruan v4
Tata letak seluruh peta mengikuti `73-room-layout-and-collision.md` (Layout Spec berbasis slot, dinding belakang tampak, kolisi, oklusi). **Katalog `data/furniture-catalog-v4.json` menggantikan daftar furnitur di §6–7 sebagai acuan minimum**; interior memakai aset `_v4`. Eksterior game center memakai `bld_game_center_v4` (menggantikan `bld_game_center` setelah lolos QA). NPC interior tidak boleh ada di layout hub.
```

## Tambah di akhir `.agents/rules/10-visual-identity.md`
```
## 9. Komponen HUD v4
Bar energi, hotbar (bawah-tengah), dan tombol motor mengikuti **gaya UI buatan pengguna** dan `docs/reference/hotbar-reference.png`; ikon pixel (bukan emoji); jangan menata ulang HUD yang ada. Efek prosedural (partikel, cincin, kilau, debu) hanya memakai token palet (rule 77).
```

## Tambah di akhir `.agents/rules/30-architecture-code.md`
```
## 10. Save v3 dan hook uji (v4)
Save v3 menambah: `energy`, `inventory[{itemId,count}]`, `vehicle{mounted,parked{map,x,y}}`, `missionsCompleted[]`, `terrain.mode`; migrasi dari v2 (energi 100, tas kosong, motor turun). Hook debug tambahan (aturan keamanan sama, hanya `?debug=1` + `debugEnabled:true`): `collisionProbe(mapId)`, `listNPCs(mapId)`, `completeMission(id)`, `useItem(slot)`, `giveItem(id,n)`, `setEnergy(n)`, `toggleVehicle()`, `measureSpeed()`, `setFuel(n)`, `advanceRealSeconds(n)` (jam palsu untuk uji bensin).
```

## Tambah di akhir `.agents/rules/50-security.md`
```
16. **Data inventaris/item/save v3:** validasi skema (itemId harus ada di katalog, jumlah bilangan bulat 1..stackMax, jumlah slot ≤ batas), tolak kunci berbahaya; teks tooltip/efek lewat `textContent`.
17. **Hook uji v4** (`giveItem`, `setEnergy`, `setFuel`, `completeMission`, `advanceRealSeconds`, dsb.) hanya aktif dengan `?debug=1` dan `debugEnabled: true`; audit akhir memastikan nonaktif pada rilis dan tidak ada jalan pintas yang melewati domain.
```
