# AUTOPILOT v6 — Perspektif/Identitas Aset, Interaksi, Energi v2, Toko, dan Tutorial Berpemandu

> Melengkapi AUTOPILOT-V4/V5. Status di `docs/PROGRESS-V6.md` (templat di bagian 3). Protokol umum sama (bukti, satu gerbang = satu commit, UI nyata, jangan menimpa kerja manual, aset baru `_v6`, aset lama dipertahankan sampai E2E lulus). **Rule 78 berlaku penuh.** Image generation dipakai untuk regenerasi aset (rule 85, `data/asset-briefs-v6.json`).

## 1. Fase dan gerbang

### J0 · Audit, patch, reproduksi (merah)
1. Terapkan `docs/EXPANSION-PATCH-V6.md` (+ `git diff --stat`), tag `pre-v6`; gabungkan `data/v6.config.additions.json` tanpa menimpa nilai pengguna.
2. Audit di `docs/AUDIT-V6.md`: (a) **semua** aset furnitur: identitas (caption vs `asset-identity-expectations.json`), frontalitas, skala piksel, dasar rata; (b) batas ruang tiap objek di 7 peta; (c) **semua sprite NPC** (gaya piksel vs pemain; Budi); (d) bentrok interaksi NPC-furnitur di semua peta (kandidat: Ibu di dapur); (e) asal sprite motor di ruang kelas; (f) kode panel toko (tombol keluar, potret vendor); (g) kode energi vs rule 83; (h) kode tutorial/misi/banner yang ada.
3. Tulis **tes merah** (UI nyata/validator) untuk B1–B15 yang dapat direproduksi: pelanggar frontalitas, ketidakcocokan identitas (bak mandi/rak piring/jendela), pelanggaran batas ruang, E dekat Ibu → furnitur, motor di kelas, toko tanpa tombol keluar, vendor tak tampil, energi tidak sesuai tabel.
**Gerbang:** patch diterapkan; AUDIT-V6.md; daftar pelanggar lengkap (bukan hanya yang disebut pengguna); tes merah terbukti gagal untuk alasan yang benar.

### J1 · Perbaikan cepat non-aset
Panel toko: tombol keluar + potret vendor (rule 86); motor parkir terikat peta (rule 75 §6); penargetan interaksi + `interactionOverlapCheck` + penataan ulang Ibu/dapur (rule 84); rak buku kelas ke pojok kiri; validator batas ruang di `layout-check`.
**Gerbang:** B4 (validator berfungsi; pelanggar yang tersisa hanya yang menunggu aset baru), B7, B8, B9, B14, B15 hijau lewat UI nyata.

### J2 · Energi v2
Rule 83: biaya per aktivitas, sesi kelas (rule 72 §8), peringatan < 50%, pingsan → bangun kesiangan, atribut `attendanceMissed`.
**Gerbang:** B10, B11, B12 hijau.

### J3 · Alat audit aset
`tools/audit_asset_perspective.py` (frontalitas, skala piksel, alfa parsial), `tools/identity_contact_sheet.py` (contact sheet berlabel untuk QA), pemeriksa duplikat hash; jalankan pada SEMUA aset; hasil di `docs/asset-identity/`.
**Gerbang:** `IDENTITY-REPORT.md` + `AUDIT-V6.md` terisi; antrean regenerasi final.

### J4 · Regenerasi aset → CHECKPOINT E
Urutan sesuai `generationOrder`: Budi (2 kandidat) → sheet kelas → kantin → perpustakaan → kamar mandi → dapur → semua pelanggar audit. Alur rule 60 + rule 85 (verifikasi identitas sebelum menamai; frontalitas; skala seragam per sheet). Render di game: **kelas, kantin, perpustakaan, kamar mandi, dapur, dan Budi** dengan aset baru; simpan di `docs/checkpoint-E/`.
**Gerbang = CHECKPOINT E (manusia):** berhenti; tampilkan gambar, ringkasan audit (sebelum/sesudah), cacat yang Anda lihat sendiri jujur; tanya: *"Setujui perspektif, identitas, dan desain Budi atau beri catatan?"*

### J5 · Integrasi aset baru
Ganti rujukan layout ke `_v6`, sesuaikan slot/ukuran/footprint/kolisi, jalankan `layout-check` (batas ruang), `map-check`, probe kolisi, `interactionOverlapCheck`, tinjauan visual tiap ruang dengan overlay.
**Gerbang:** B1–B6, B13 hijau dengan bukti; 0 pelanggar validator.

### J6 · Tutorial dan cerita
Rule 82 penuh: mesin langkah dari `data/tutorial.phase1.json`, panel objektif, panah (dunia + tepi + arah belokan), petunjuk tombol, highlight HUD, soft-lock bangunan, jam dijeda, kejadian dimatikan, save/resume, dialog cerita berpotret, ringkasan akhir, "Ulangi tutorial".
**Gerbang:** tes langkah per langkah lewat UI nyata; jendela jam buka feasible.

### J7 · E2E tutorial penuh + regresi
Satu rangkaian dari Permainan Baru sampai T20 dengan pointer/keyboard nyata dan tangkapan layar tiap langkah; E2E bebas 3 hari berbasis UI; semua tes lama (self, time, dialogue, map, layout, hud-sync, regresi V4/V5).
**Gerbang:** B16, B17 hijau.

### J8 · Dokumen dan laporan
`docs/ACCEPTANCE-V6-RESULTS.md` (semua baris dengan bukti), `docs/FINAL-REPORT-V6.md` (jujur: non-PASS, tes berhook, hal tak teruji, aset ready/placeholder/ditolak).

## 2. Urutan modular
J1 dan J2 tidak membutuhkan aset. J3–J5 membutuhkan image generation. J6–J7 membutuhkan J1, J2 (dan idealnya J5 agar tutorial memakai ruangan final).

## 3. Templat `docs/PROGRESS-V6.md`
```
# PROGRESS V6   Tag: pre-v6
- [ ] J0 Audit + patch + merah    - [ ] J1 Perbaikan cepat
- [ ] J2 Energi v2                 - [ ] J3 Alat audit aset
- [ ] J4 Regenerasi → [ ] CHECKPOINT E disetujui
- [ ] J5 Integrasi aset            - [ ] J6 Tutorial + cerita
- [ ] J7 E2E tutorial + regresi    - [ ] J8 Laporan
Log gerbang: | Tanggal | Gerbang | Hasil | Bukti | Commit |
Baris matriks non-PASS: ...   Temuan terbuka: ...
```
