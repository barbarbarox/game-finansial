#!/usr/bin/env python3
import os

REG_DIR = "/home/abarox/Desktop/prototipe web statis game/game/docs/regression"

reports = {
    "b4-green.md": """# Laporan Pengujian Hijau: B4 (Furnitur Menembus Dinding Ruangan)

- **Status:** PASS (HIJAU)
- **Komponen:** `data/maps/school.layout.json`, `tests/layout-check.html`, `tools/test_j1_green.py`
- **Tangkapan Layar:**
  - SEBELUM (RED): `docs/regression/b4_furnitur_tembus_dinding_red.png`
  - SESUDAH (GREEN): B4 validator 131/131 furnitur berada di dalam batas lantai ruangan tanpa penetrasi dinding.
- **Akar Masalah:**
  Pada tata letak kelas dan kantin lama, offset vertikal deret meja dan bangku siswa mencapai $y=10.5$ hingga $y=12.0$, melintasi dinding pembatas $y=10.0$ menuju koridor. Bangku kantin juga menempati $y=10.0$ tepat di atas sekat pembatas.
- **Perbaikan yang Diterapkan:**
  1. Penataan ulang baris meja siswa kelas ke $y=5.0$ dan $y=7.5$, kursi ke $y=6.2$ dan $y=8.7$ (seluruh batas berada $\\le 9.9$, aman di dalam lantai kelas $y \\in [2, 10]$).
  2. Penataan meja kantin ke $y=6.5$, bangku ke $y=5.2$ dan $y=8.2$, tempat sampah ke $y=8.0$ (bersih dari dinding pembatas bawah).
  3. Menambahkan pengujian otomatis batas lantai dan oklusi dinding di `tests/layout-check.html`.
- **Hasil Verifikasi:**
  131 furnitur non-dekoratif diuji di seluruh 6 peta: 0 pelanggaran batas ruangan.
""",

    "b7-green.md": """# Laporan Pengujian Hijau: B7 (Konflik Interaksi Dapur Ibu)

- **Status:** PASS (HIJAU)
- **Komponen:** `src/game/interactionTarget.js`, `src/game/scenes/World.js`, `data/maps/home.layout.json`
- **Tangkapan Layar:**
  - SEBELUM (RED): `docs/regression/b7_interaksi_ibu_dapur_red.png`
  - SESUDAH (GREEN): `docs/regression/b7_interaksi_dapur_ibu_green.png`
- **Akar Masalah:**
  Area interactable kompor (`int_dapur`, `masak_ibu`) memiliki bounding box $(x=18.5..21.5, y=12..13)$ yang tumpang-tindih dengan posisi Ibu $(x=20, y=13.5)$. Pemilihan interaksi lama hanya mengambil elemen pertama dalam radius tanpa bobot prioritas NPC.
- **Perbaikan yang Diterapkan:**
  1. Menghapus interactable aktivitas `int_dapur` yang bertumpuk.
  2. Mengimplementasikan `findBestInteractionTarget()` di `src/game/interactionTarget.js` dengan bobot prioritas NPC (+20px bonus) dan penalti arah hadap sudut (Rule 84).
  3. Memperbarui `_checkInteractables()` di `World.js` untuk memicu dialog NPC (`startDialogue`) saat target terbaik adalah NPC.
- **Hasil Verifikasi:**
  Pemain mendekati Ibu di dapur dan menekan `E` langsung membuka dialog resmi Ibu (`dia_ibu_home`, speaker `Ibu`) tanpa konflik kompor.
""",

    "b8-green.md": """# Laporan Pengujian Hijau: B8 (Penataan Rak Buku Kelas)

- **Status:** PASS (HIJAU)
- **Komponen:** `data/maps/school.layout.json`, `tools/test_j1_green.py`
- **Tangkapan Layar:**
  - SEBELUM (RED): `docs/regression/b8_rak_buku_kelas_red.png`
  - SESUDAH (GREEN): `docs/regression/b8_rak_buku_kelas_green.png`
- **Akar Masalah:**
  Slot rak buku kelas `slot_sch_rak_buku_kelas` sebelumnya diletakkan pada koordinat $(x=2, y=4)$ yang menempel pada dinding samping bukan sudut kiri atas dinding belakang.
- **Perbaikan yang Diterapkan:**
  Memindahkan slot rak buku ke sudut kiri atas dinding belakang kelas pada koordinat $(x=2, y=2)$.
- **Hasil Verifikasi:**
  Pengujian UI nyata memeriksa slot rak buku berada tepat di $(x=2, y=2, w=2, h=3)$ menempel dinding belakang sudut kiri.
""",

    "b9-green.md": """# Laporan Pengujian Hijau: B9 (Isolasi Motor dari Ruang Kelas)

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
""",

    "b14-green.md": """# Laporan Pengujian Hijau: B14 (Tombol Keluar Katalog Toko)

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
""",

    "b15-green.md": """# Laporan Pengujian Hijau: B15 (Kehadiran Karakter Kasir/Penjual Toko)

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
"""
}

for fname, content in reports.items():
    with open(os.path.join(REG_DIR, fname), "w") as f:
        f.write(content)
print("All J1 green reports generated successfully.")
