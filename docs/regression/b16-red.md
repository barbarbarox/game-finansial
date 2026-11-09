# Reproduksi Masalah B16: Tutorial Hari Pertama & Cerita Belum Diaktifkan
- **Status:** RED (Terverifikasi Gagal)
- **Langkah UI/Audit:** Mulai permainan baru ("Mulai Petualangan").
- **Hasil Aktual:** Game langsung masuk ke mode bebas tanpa inisialisasi state tutorial 20 langkah (`T01–T20`), tanpa panah pemandu, dan jam langsung berdetak secara real-time.
- **Tangkapan Layar:** `docs/regression/b16_tutorial_red.png`
- **Akar Masalah:** Modul mesin tutorial `src/domain/tutorial.js` belum dibuat dan diintegrasikan ke siklus hidup permainan (Rule 82).
