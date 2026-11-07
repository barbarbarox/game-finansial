# Rekam Keputusan Arsitektur & Desain (DECISIONS.md)

| ID | Tanggal | Konteks / Pertanyaan | Keputusan yang Diambil | Alasan / Dampak |
|---|---|---|---|---|
| D01 | 2026-11-07 | Folder kerja proyek | Root game diletakkan di subfolder `game/` dalam workspace agar terisolasi rapi dari kit mentah dan dokumen acuan. | Memastikan `git init` dan remote GitHub berada tepat di folder game mandiri tanpa menyertakan kit acuan atau file non-game. |
| D02 | 2026-11-07 | Mode awal aset visual | Mulai dengan mode `placeholder-only` untuk P0–P2, lalu beralih ke generasi aset terarah di P3 setelah model Gemini aktif. | Mematuhi permintaan user untuk konfirmasi model AI sebelum generasi gambar; memastikan seluruh fondasi kode teruji dulu dengan placeholder. |
| D03 | 2026-11-07 | Versi Phaser | Phaser v3.80.1 diunduh ke `vendor/phaser.min.js`. | Menjaga aturan offline-first tanpa CDN eksternal saat runtime. |
| D04 | 2026-11-07 | Ledger Structure | Double-entry penuh di backend domain (`src/domain/ledger.js`), tampilan buku kas sederhana untuk pemain di Fase 1. | Menjamin integritas akuntansi (ΣD = ΣK, Kas ≥ 0) dan kesiapan migrasi ke Fase 2 tanpa perombakan besar. |
