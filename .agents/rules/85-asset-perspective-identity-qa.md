---
trigger: model_decision
description: "Terapkan saat menghasilkan, memeriksa, atau meregenerasi aset furnitur/NPC: kontrak perspektif (depan/belakang/samping, bukan serong), kecocokan nama file dengan isi gambar (identitas), furnitur menembus dinding, gaya sprite NPC (piksel vs kartun), kursi/meja sekolah-kantin-perpustakaan, papan tulis, kamar mandi, dapur."
---

# 85 · Kontrak Perspektif, Verifikasi Identitas, dan Gaya Sprite

## 0. Masalah (bukti: tangkapan layar pengguna)
(a) Kursi dan meja sekolah/kantin/perpustakaan digambar **serong** (diagonal); meja guru dan papan tulis miring; (b) beberapa furnitur **menembus dinding** ruangnya; (c) **nama berkas tidak cocok dengan isi gambar**: `bak mandi` berisi rak piring, `rak piring dapur` berisi jendela; (d) wastafel/toilet serong dan tidak konsisten; (e) sprite NPC Budi bergaya **kartun**, bukan piksel seperti pemain. Penyebab utama: pemotongan sheet menamai item berdasarkan urutan kiri→kanan tanpa memeriksa isi, perspektif tidak dikontrak, dan tidak ada validator batas dinding maupun gaya.

## 1. Kontrak perspektif (semua furnitur)
Kamera menunduk ±20–25° dari depan. Tiap aset memiliki `facing` di katalog dan **hanya** salah satu:
- `front` — muka depan sejajar bidang gambar, **simetris kiri-kanan** (meja guru, papan tulis, meja kantin/baca, sofa, kulkas, toilet, bak mandi, wastafel, rak, lemari, kasur dengan kepala di dinding).
- `back` — dilihat dari belakang (sandaran menghadap kamera): kursi siswa, kursi perpustakaan, kursi sisi dekat meja kantin.
- `left` / `right` — tampak samping murni (kursi makan samping).
**Dilarang:** miring/diagonal/isometrik/diputar. Aset yang menggambarkan satu set (meja + kursi) dibuat sebagai **komposit satu sprite** dengan arah yang benar: meja siswa = meja `front` + kursi `back` di depan kamera (menimpa bawah meja); set kantin = meja panjang `front` + bangku dekat dilihat dari belakang + bangku jauh terlihat di balik meja; set baca = meja `front` + dua kursi `back`.
Prompt generator wajib memuat: "strict front elevation, camera slightly above (about 20-25 degrees), object's main face parallel to the picture plane, perfectly left-right symmetrical, NOT diagonal, NOT isometric, NOT rotated" (atau "seen from directly behind" untuk `back`).

## 2. Verifikasi identitas (nama berkas = isi gambar)
1. Setelah memotong sheet, **jangan** menamai berdasarkan urutan semata. Buat `contact_sheet` berlabel ID (label hanya untuk QA, bukan aset game) lalu **lihat tiap potongan** dan tulis keterangan apa yang tampak di `docs/asset-identity/IDENTITY-REPORT.md` (id → keterangan → cocok/tidak).
2. Bandingkan dengan `data/asset-identity-expectations.json` (kata kunci yang diharapkan per id). Tidak cocok → **tukar nama/pemetaan** bila isinya benar tapi namanya tertukar, atau **regenerate** bila isinya salah.
3. Manifest memuat `identityVerified: true` + `identityCaption`. Aset tanpa verifikasi tidak boleh `ready`.
4. Untuk set yang pernah tertukar (kamar mandi, dapur), bila verifikasi gagal pada sheet, generate **satu item per gambar**.
5. Deteksi duplikat: hash piksel identik antar-id dilaporkan; dua id berbeda dengan isi sama dicurigai.

## 3. Validator otomatis tambahan (`tools/audit_asset_perspective.py`, hasil di `docs/asset-identity/`)
- **Frontalitas:** untuk aset `front`/`back`, `IoU(alfa, alfa dicerminkan)` ≥ 0,80; di bawahnya ditandai serong dan diregenerasi.
- **Skala piksel:** estimasi ukuran piksel efektif (panjang run horizontal modus) dan **rasio piksel alfa parsial = 0**; selisih ukuran piksel antar-aset furnitur ≤ 25% dari rata-rata ruang.
- **Dasar rata:** aset berkolisi menempel baris terbawah (rule 60 §11).
- **Batas ruang (layout-check):** (i) footprint seluruh objek non-dekoratif **berada di dalam lantai** ruang; (ii) tidak ada piksel sprite non-`wall_decor` melintasi tepi ruang luar/ruang tetangga; (iii) benda `wall_back` hanya boleh menimpa muka dinding belakang, bukan dinding samping/bawah; (iv) bangku/meja tidak melintasi garis dinding atau ambang pintu. Hasil per objek ke `docs/layouts/VALIDATION-<mapId>.md`.
- Semua validator berjalan pada **seluruh** aset dan peta (bukan hanya yang disebut pengguna); daftar pelanggar menjadi antrean regenerasi.

## 4. Gaya sprite NPC (piksel, bukan kartun)
- Sprite NPC wajib setara sprite pemain: 32×64, 3 tampak (front/back/left; kanan = cermin), tepi tajam tanpa alfa parsial, warna ∈ `palette.json`, **ukuran piksel efektif dalam ±25% sprite pemain**, outline gelap 1 px, shading 2–3 nada.
- Jalankan audit gaya pada **semua** sprite NPC; outlier (termasuk Budi) diregenerasi. Potret dialog tidak dipakai sebagai sprite dunia.
- **Budi (teman sekolah laki-laki) dirancang ulang** agar lebih menarik dan khas (lihat brief `npc_sheet_budi_v6` di `data/asset-briefs-v6.json`): rambut hitam cepak dengan sedikit jambul, seragam putih-abu lengan digulung, tas selempang mustard, sepatu putih, postur santai ramah; 2 kandidat, pilih lewat QA + tinjauan visual; konsisten dengan potret `portrait_teman_l` (rambut, seragam, tas).

## 5. Alur regenerasi
Antrean = pelanggar validator + daftar di `data/asset-briefs-v6.json`. Aset baru bersufiks `_v6`; layout menunjuk `_v6` setelah lolos; aset lama dipertahankan sampai E2E lulus. Batas 3 percobaan; kandidat bila ada `candidates`. Setelah regenerasi: ukuran sesuai slot (rule 73), `layout-check` (termasuk batas ruang) hijau, tinjauan visual tangkapan layar tiap ruang dengan overlay kolisi, perbarui `IDENTITY-REPORT.md`. Tidak ada klaim "sesuai" tanpa bukti (AGENTS.md #16).
