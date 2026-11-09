# Laporan Pengujian Hijau: B9 (Isolasi Motor dari Ruang Kelas)

- **Status:** PASS (HIJAU)
- **Komponen:** `src/game/scenes/World.js`, `src/game/mapManager.js`, `tools/test_j1_green.py`
- **Tangkapan Layar:**
  - SEBELUM (RED): `docs/regression/b9_motor_di_kelas_red.png`
  - SESUDAH (GREEN): `docs/regression/b9_motor_di_kelas_green.png`
- **Akar Masalah:**
  Saat pemain berkendara ke pintu sekolah di `town_hub` lalu masuk, auto-dismount memunculkan sprite motor di koordinat dunia Phaser tanpa mencatat `mapId`. Sprite motor tidak dihancurkan saat `clearCurrentMap()` sehingga tetap merender di koordinat dunia yang sama di dalam interior kelas sekolah.
- **Perbaikan yang Diterapkan:**
  1. Menambahkan parameter `mapId` pada state kendaraan `parked: { mapId, x, y }`.
  2. `clearCurrentMap()` memanggil `_removeParkedMotor()` untuk membersihkan sprite motor lama dari memori Phaser.
  3. `loadMap()` memanggil `_syncParkedMotor()` yang memverifikasi `parked.mapId === currentMapId` sebelum membuat sprite motor parkir.
- **Hasil Verifikasi:**
  Pemain memarkir motor di `town_hub` -> masuk sekolah -> motor terbukti TIDAK ada di dalam sekolah (`motor_in_school == False`) -> keluar kembali ke `town_hub` -> motor terparkir rapi di posisi semula (`motor_restored_in_hub == True`).
