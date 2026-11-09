# Laporan Pengujian Hijau: B15 (Kehadiran Karakter Kasir/Penjual Toko)

- **Status:** PASS (HIJAU)
- **Komponen:** `src/ui/shopPanel.js`, `src/ui/tokens.css`, `tools/test_j1_green.py`
- **Tangkapan Layar:**
  - SEBELUM (RED): `docs/regression/b15_toko_tanpa_vendor_red.png`
  - SESUDAH (GREEN):
    - Minimarket: `docs/regression/b15_vendor_minimarket_green.png` (Mbak Maya)
    - Kantin: `docs/regression/b15_vendor_kantin_sekolah_green.png` (Bu Sri)
    - SPBU: `docs/regression/b15_vendor_spbu_green.png` (Mas Doni)
    - Toko Kosmetik: `docs/regression/b15_vendor_toko_kosmetik_green.png` (Kak Cindy)
    - Game Center: `docs/regression/b15_vendor_game_center_kafe_green.png` (Kak Riko)
- **Akar Masalah:**
  Panel katalog toko sebelumnya hanya berupa grid item tanpa kolom representasi vendor NPC, plakat nama, atau gelembung ucapan responsif.
- **Perbaikan yang Diterapkan:**
  1. Menyusun layout 2 kolom: kolom kiri `.shop-vendor-col` dan kolom kanan `.shop-content-col`.
  2. Menyertakan potret resolusi tinggi 192x256 berskala integer pixelated (`portrait_*`).
  3. Menyertakan plakat nama dan peran vendor.
  4. Menyertakan gelembung ucapan interaktif (`.shop-vendor-speech`) yang dinamis menyapa saat buka, berterima kasih saat membeli, dan mengingatkan jika saldo kas kurang atau ransel penuh.
- **Hasil Verifikasi:**
  Seluruh 5 toko menampilkan profil vendor resmi yang sesuai dengan gelembung ucapan yang aktif dan informatif.
