# Reproduksi Masalah B4: Furnitur Menembus Dinding Ruangan
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Jalankan validasi batas ruang pada `school.layout.json`.
- **Hasil Aktual:** 4 kursi siswa baris belakang (`kursi_siswa_3a`, `kursi_siswa_3b`, `kursi_siswa_4a`, `kursi_siswa_4b`) ditaruh di y=10.5 dengan dasar y=12.0, menembus dinding kelas y=10 dan berada di koridor.
- **Tangkapan Layar:** `docs/regression/b4_furnitur_tembus_dinding_red.png`
- **Akar Masalah:** Slotting layout tidak memeriksa batas bounding box lantai ruang (`lantai_kelas` y=2..10).
