# Reproduksi Masalah B9: Sprite Motor Liar di Ruang Kelas
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Naik motor di `town_hub`, kendarai menuju pintu masuk sekolah SMA Negeri 1, tekan E untuk masuk.
- **Hasil Aktual:** Karakter masuk ke ruang kelas, namun sprite motor parkir (`prop_motor_parkir`) tetap tampil mengambang di lantai kelas pada koordinat sekolah.
- **Tangkapan Layar:** `docs/regression/b9_motor_di_kelas_red.png`
- **Akar Masalah:** `_spawnParkedMotor()` membuat sprite Phaser scene tanpa mengaitkannya ke `mapManager._mapObjects`, dan tidak ada validasi `mapId === currentMapId` saat transisi peta (Rule 75 §6).
