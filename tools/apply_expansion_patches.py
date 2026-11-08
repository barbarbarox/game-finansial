import os

def apply_patch(filepath, search_str, replace_str):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return False
    with open(filepath, "r") as f:
        content = f.read()
    if search_str in content:
        content = content.replace(search_str, replace_str, 1)
        with open(filepath, "w") as f:
            f.write(content)
        print(f"Patched {os.path.basename(filepath)}: OK")
        return True
    else:
        print(f"Search string not found in {os.path.basename(filepath)}!")
        return False

base = "/home/abarox/Desktop/prototipe web statis game/game"

# Patch 1
apply_patch(f"{base}/AGENTS.md",
    "dunia top-down kota kecil (satu peta hub)",
    "dunia top-down kota kecil (peta hub + interior bangunan yang dapat dijelajahi; permainan dimulai di dalam rumah pemain), dialog NPC dengan potret kiri-kanan, sistem waktu 24 jam")

# Patch 2
apply_patch(f"{base}/AGENTS.md",
    "(satu-satunya pengecualian: tile tanah prosedural di `20-asset-pipeline.md`)",
    "(pengecualian: tile tanah, lantai, dan dinding prosedural sesuai `20-asset-pipeline.md` dan `70-interior-maps-and-buildings.md`)")

# Patch 3
apply_patch(f"{base}/AGENTS.md",
    "- `60-asset-generation-qa.md` — pipeline generate → proses → QA → perbaiki → daftarkan",
    "- `60-asset-generation-qa.md` — pipeline generate → proses → QA → perbaiki → daftarkan\n- `70-interior-maps-and-buildings.md` — peta interior, perpindahan peta, fitur bangunan, awal permainan di rumah\n- `71-dialogue-system.md` — dialog dengan potret kiri-kanan dan menu pilihan\n- `72-time-system.md` — jam 24 jam, widget waktu, aktivitas yang memakan waktu, jam buka")

# Patch 4
apply_patch(f"{base}/AGENTS.md",
    "jangan menghapus aset hasil generate yang sudah lolos QA tanpa alasan tercatat.",
    "jangan menghapus aset hasil generate yang sudah lolos QA tanpa alasan tercatat.\n13. **Perubahan manual pengguna bersifat otoritatif.** Pengguna telah mengubah UI (tombol, menu) dan widget waktu. Sebelum mengubah file yang mungkin telah disunting manual, audit (`git log`, `git diff`, baca kode), pertahankan tampilan/perilaku yang ada, dan hanya refactor bila perlu untuk integrasi. Catat apa yang dipertahankan di `docs/DECISIONS.md`.")

# Patch 5
apply_patch(f"{base}/.agents/rules/10-visual-identity.md",
    '- DILARANG: gradient, glassmorphism, neon, bayangan blur, pill UI, kartu "SaaS", ikon emoji, elemen tanpa fungsi.',
    '- DILARANG: gradient, glassmorphism, neon, bayangan blur, pill UI, kartu "SaaS", ikon emoji, elemen tanpa fungsi. **Pengecualian disetujui pengguna:** gradient langit hanya di komponen Sky Dial widget waktu, dan tab hari (Day Pill) berbentuk tab emas bersudut piksel. Emoji tetap dilarang (matahari/bulan dibuat dengan CSS/sprite).')

# Patch 6
apply_patch(f"{base}/.agents/rules/10-visual-identity.md",
    "| `--grey-400` | #9AA0AA | HANYA untuk seragam putih-abu-abu |",
    "| `--grey-400` | #9AA0AA | HANYA untuk seragam putih-abu-abu |\n| `--sky-dawn` | #E8B25A | HANYA Sky Dial: fajar keemasan (pagi) |\n| `--sky-day` | #7FB6D9 | HANYA Sky Dial: biru cerah (siang) |\n| `--sky-dusk` | #E07B4F | HANYA Sky Dial: senja jingga kemerahan (sore) |\n| `--sky-night` | #16213B | HANYA Sky Dial: biru pekat (malam) |")

# Patch 7
apply_patch(f"{base}/.agents/rules/20-asset-pipeline.md",
    "`assets/` → `characters/`, `npcs/`, `buildings/`, `props/`, `backgrounds/`",
    "`assets/` → `characters/`, `npcs/`, `portraits/`, `buildings/`, `furniture/`, `props/`, `backgrounds/`")

# Patch 8
apply_patch(f"{base}/.agents/rules/20-asset-pipeline.md",
    "## 7. Tile tanah prosedural (satu-satunya \"gambar via kode\" yang diizinkan)",
    "## 7. Tile prosedural: tanah, lantai, dan dinding (satu-satunya \"gambar via kode\" yang diizinkan; interior: lihat `70-interior-maps-and-buildings.md` §3)")

# Patch 9
apply_patch(f"{base}/.agents/rules/20-asset-pipeline.md",
    "## 6. Peta hub = layout-as-data (tanpa Tiled)",
    "## 6. Peta hub = layout-as-data (tanpa Tiled; peta interior dan registry peta: lihat `70-interior-maps-and-buildings.md`)")

# Patch 10
apply_patch(f"{base}/.agents/rules/40-phase1-game-design.md",
    "Semua lokasi adalah **bangunan di peta hub**; menyentuh pintu membuka **panel DOM** dengan ilustrasi `bg_panel_*` (tidak ada interior yang bisa dijelajahi). NPC ibu, ayah, dan teman berdiri di hub; penjual/kasir tampil di panel masing-masing.",
    "Setiap lokasi adalah **bangunan di peta hub dengan peta interior yang dapat dijelajahi** (lihat `70-interior-maps-and-buildings.md`); pemain benar-benar masuk, dan transaksi hanya terjadi pada titik interaksi spesifik di dalamnya (mis. belanja makan/jajan hanya di konter kantin). Permainan dimulai di dalam rumah pemain.")

# Patch 11
apply_patch(f"{base}/.agents/rules/40-phase1-game-design.md",
    "- Durasi Fase 1: 2 bulan permainan × 30 hari; `dayDurationSeconds: 12` (≈12 menit bermain; tombol tidur untuk melompat hari).",
    "- Durasi Fase 1: `months` (default 2) × 30 hari. Pengaturan waktu mengikuti `72-time-system.md` (siklus 24 jam, aktivitas memakan waktu); total waktu bermain jauh lebih panjang daripada versi lama, jadi untuk demo kompetisi disarankan `months: 1`.")

# Patch 12
apply_patch(f"{base}/.agents/rules/30-architecture-code.md",
    "## 5. Jam permainan",
    "## 5. Jam permainan (DIGANTI oleh `72-time-system.md`; paragraf di bawah hanya ringkasan lama)")

# Patch 13
apply_patch(f"{base}/.agents/rules/30-architecture-code.md",
    "Key `lj_save_v1` (satu objek).",
    "Key `lj_save_v2` (satu objek; migrasi dari `lj_save_v1` wajib, lihat 70 dan 72).")

