# Rekam Keputusan Arsitektur & Desain (DECISIONS.md)

| ID | Tanggal | Konteks / Pertanyaan | Keputusan yang Diambil | Alasan / Dampak |
|---|---|---|---|---|
| D01 | 2026-11-07 | Folder kerja proyek | Root game diletakkan di subfolder `game/` dalam workspace agar terisolasi rapi dari kit mentah dan dokumen acuan. | Memastikan `git init` dan remote GitHub berada tepat di folder game mandiri tanpa menyertakan kit acuan atau file non-game. |
| D02 | 2026-11-07 | Mode awal aset visual | Mulai dengan mode `placeholder-only` untuk P0–P2, lalu beralih ke generasi aset terarah di P3 setelah model Gemini aktif. | Mematuhi permintaan user untuk konfirmasi model AI sebelum generasi gambar; memastikan seluruh fondasi kode teruji dulu dengan placeholder. |
| D03 | 2026-11-07 | Versi Phaser | Phaser v3.80.1 diunduh ke `vendor/phaser.min.js`. | Menjaga aturan offline-first tanpa CDN eksternal saat runtime. |
| D04 | 2026-11-07 | Ledger Structure | Double-entry penuh di backend domain (`src/domain/ledger.js`), tampilan buku kas sederhana untuk pemain di Fase 1. | Menjamin integritas akuntansi (ΣD = ΣK, Kas ≥ 0) dan kesiapan migrasi ke Fase 2 tanpa perombakan besar. |
| D05 | 2026-11-08 | Perubahan Manual Pengguna yang Dipertahankan (E0) | Mempertahankan 100% UI manual pengguna: (1) Widget status dashboard gaya Harvest Moon di kiri atas (Day tab, Sky dial dengan panah, inset box tanggal/jam/kas/tabungan, dan bar bensin hijau), (2) Tombol nav kanan atas tanpa emote, (3) Menu pengaturan dengan Dark/Light mode, (4) Indikator pemain melayang, (5) Label nama NPC di atas kepala (y-64), (6) Interaksi NPC via tombol [E]. | Sesuai mandat Rule 72 §0 dan AGENTS.md butir 13: UI pengguna bersifat otoritatif, tidak boleh ditimpa, hanya diintegrasikan dengan domain time/map baru. |

