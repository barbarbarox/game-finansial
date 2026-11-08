# Reproduksi Masalah A7: Pemain Tidak Bisa Bergerak dengan Mengklik Titik Tujuan
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI:** Pemain mengklik canvas game di area terbuka pada koordinat yang dapat dijangkau.
- **Hasil Aktual:** Posisi karakter player tetap di `{x: 208, y: 592}` (tidak ada pergerakan, tidak ada penanda tujuan yang muncul).
- **Tangkapan Layar:** `docs/regression/a7_click_to_move_red.png`
- **Akar Masalah:** `player.js` hanya mendengarkan input keyboard (`cursors` dan `wasd`). Belum ada pointer listener pada canvas dan modul pathfinding A* `NavigationGrid`.
