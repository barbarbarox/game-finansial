# Laporan Pengujian Hijau: B14 (Tombol Keluar Katalog Toko)

- **Status:** PASS (HIJAU)
- **Komponen:** `src/ui/shopPanel.js`, `src/ui/tokens.css`, `tools/test_j1_green.py`
- **Tangkapan Layar:**
  - SEBELUM (RED): `docs/regression/b14_toko_tanpa_tombol_keluar_red.png`
  - SESUDAH (GREEN): `docs/regression/b14_katalog_minimarket_exit_green.png`
- **Akar Masalah:**
  Katalog minimarket dan panel toko lainnya tidak memiliki tombol keluar yang konsisten di footer, tidak merespon klik di luar backdrop, dan listener tombol Escape tidak selalu terikat di semua mode (misalnya SPBU).
- **Perbaikan yang Diterapkan:**
  1. Menambahkan tombol close `[X]` di header (`.btn-close`).
  2. Menambahkan tombol `[Selesai]` di footer modal (`.shop-btn-done`).
  3. Mengimplementasikan event listener penutupan saat mengklik di luar area modal (`activeBackdrop`).
  4. Mengimplementasikan penutupan dengan tombol `Escape` di seluruh katalog toko termasuk menu bahan bakar SPBU.
- **Hasil Verifikasi:**
  Pengujian UI nyata menutup panel via `[X]`, `[Selesai]`, dan `[Esc]` pada seluruh 5 toko (Minimarket, Kantin, SPBU, Kosmetik, Game Center). Setelah ditutup, kontrol pemain kembali aktif.
