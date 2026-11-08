---
trigger: model_decision
description: "Terapkan saat menghasilkan, memproses, memvalidasi, memperbaiki, atau mendaftarkan aset gambar hasil image generation (karakter, NPC, bangunan, prop, panel, key art, ikon); atau saat menulis/menjalankan skrip di tools/."
---

# 60 · Pipeline Generate → Proses → QA → Perbaiki → Daftarkan

## 1. Probe kemampuan (sekali di awal, catat di `docs/PROGRESS.md`)
Temukan alat image generation yang tersedia pada Anda. Hasilkan satu gambar uji 1:1 berlatar magenta, simpan ke `assets/_raw/_probe.png`. Catat: nama alat/model, rasio aspek yang didukung, apakah mendukung gambar referensi/editing, di mana berkas keluaran tersimpan (salin ke workspace bila perlu). **Jika tidak ada alat generate:** set mode `placeholder-only`, lanjutkan seluruh pekerjaan kode, dan laporkan jelas bahwa aset belum ada.
Catatan: alat biasanya hanya mendukung rasio tetap (mis. 1:1, 3:2, 16:9) dan tidak menjamin ukuran piksel eksak; ukuran akhir dicapai oleh tools pemroses, bukan oleh generator.

## 2. Tools (tulis di `tools/`, Python + Pillow + numpy, versi dipin; uji dulu dengan gambar sintetis sebelum dipakai)
| Tool | Fungsi |
|---|---|
| `chroma_key` | Hapus latar magenta (toleransi kecil + despill tepi), hasilkan alpha; laporkan sisa piksel magenta |
| `slice_sheet` | Pisahkan sheet menjadi subjek terpisah lewat connected-components pada alpha (urut kiri→kanan, atas→bawah) atau grid tetap (ikon); gagal bila jumlah subjek ≠ brief |
| `normalize` | Crop bbox, skala ke tinggi/lebar target dengan **area-average (Box/Lanczos)** — bukan nearest, karena keluaran AI tidak selaras grid piksel — pusatkan horizontal, ratakan dasar (kaki) ke baris terbawah frame |
| `palette_snap` | Petakan tiap piksel ke warna terdekat (ruang Lab) di `assets/palette.json`, **tanpa dithering**, alpha di-threshold 0/255 |
| `build_spritesheet` | Susun frame sesuai urutan di brief dan keluarkan fragmen manifest |
| `validate_asset` | Jalankan cek teknis (bagian 4) dan keluarkan laporan JSON |
| `contact_sheet` | Montase aset di atas latar netral, diperbesar 2× nearest, untuk tinjauan visual |
`assets/palette.json` diturunkan dari token `10-visual-identity.md`: 14 token + turunan tonal hingga ≤ 32 warna (outline cokelat/navy gelap, bayangan, highlight).

## 3. Alur per aset (ikuti `data/asset-briefs.json`)
1. Susun prompt = STYLE BLOCK + `subject` + NEGATIVE BLOCK (`docs/STYLE-BIBLE.md`); lampirkan gambar referensi sesuai `refs`.
2. Generate → simpan mentah ke `assets/_raw/<id>_v<N>.png`.
3. `chroma_key` → `slice_sheet` (bila sheet) → `normalize` → `palette_snap` → simpan ke lokasi akhir sementara.
4. `validate_asset` → laporan JSON.
5. **Tinjauan visual:** buat `contact_sheet`, lihat gambarnya sendiri, bandingkan dengan kanon `STYLE-BIBLE.md` dan referensi jangkar; isi checklist bagian 5.
6. Lolos keduanya → daftarkan di manifest (`status: ready`), tulis baris di `docs/ASSET-LOG.md`. Gagal → bagian 6.

## 4. Cek teknis (validator)
- Dimensi frame/gambar = brief; jumlah frame = brief.
- Alpha hanya {0,255}; sudut bebas piksel buram; tidak ada sisa magenta (jarak warna < 60 dari #FF00FF = 0 piksel).
- Seluruh warna ∈ palette (pasca-snap); jumlah warna unik ≤ 32.
- Karakter/NPC: tinggi isi ≥ 88% tinggi frame; kaki menyentuh baris dasar; pusat massa horizontal dalam ±2 px dari tengah; **ketiga tampak** satu karakter selisih tinggi ≤ 6%.
- Heuristik identitas karakter: area dominan hijau gelap (tas), cokelat gelap (rambut), cream (kaos), navy (celana) terdeteksi pada ukuran minimum yang wajar.
- Bangunan/prop: dasar sprite rata di baris terbawah; footprint dalam batas gambar.
- Panel/key art: rasio 16:9; tidak ada area transparan.
- Ikon: tiap ikon terpusat dan mengisi ≥ 60% sel.

## 5. Checklist tinjauan visual (jujur, tulis cacat spesifik)
- [ ] Gaya sama dengan jangkar (ukuran piksel tampak, tebal outline, arah cahaya, saturasi)
- [ ] Tidak ada teks/huruf/angka/logo/merek (termasuk pada papan dan poster)
- [ ] Proporsi dan warna sesuai kanon (khusus karakter: rambut, kaos, celana, sepatu, tas)
- [ ] Siluet terbaca pada ukuran akhir; tidak ada artefak/piksel liar/halo
- [ ] Perspektif 3/4 konsisten, bukan isometrik/overhead
- [ ] Tepi bersih untuk dipasang di peta (bangunan/prop) dan pintu terlihat jelas
Catatan: validator menangkap cacat teknis; kemiripan gaya dan identitas bergantung penilaian visual Anda yang tidak selalu andal — karena itu ada checkpoint manusia (AUTOPILOT).

## 6. Memperbaiki aset yang salah
1. **Perbaikan otomatis (tanpa generate ulang)** bila cacatnya teknis: sisa magenta, alpha buram, posisi/ukuran, warna di luar palet, piksel liar kecil.
2. **Generate ulang** bila cacatnya gaya/identitas/teks/anatomi: ulangi dengan prompt yang ditambah daftar cacat spesifik percobaan sebelumnya ("previous attempt had X; fix X; keep everything else identical") dan gambar mentah sebelumnya sebagai referensi bila alat mendukung editing.
3. Batas **3 percobaan** per aset (`defaults.maxRetries`). Simpan percobaan terbaik; yang gagal pindah ke `assets/_rejected/`.
4. Setelah batas: pakai placeholder berlabel, `status: placeholder`, catat di `ASSET-LOG.md` dan Laporan. Jangan menurunkan ambang QA agar lolos.
5. Pembatasan biaya: jangan menjalankan generate massal paralel tanpa perlu; urutkan sesuai prioritas brief; hentikan batch bila alat menolak (kuota/rate limit) dan laporkan sisa antrean.

## 7. Karakter (tampak terpisah — jawaban atas sheet multi-sisi)
- Generate **satu sheet** berisi tiga tampak karakter yang sama berdampingan: front, back, left (konsistensi terbaik karena satu generasi). `slice_sheet` memisahkannya menjadi tiga gambar; `normalize` menyamakan skala dan dasar; **tampak kanan = cermin tampak kiri** (`symmetric` ditandai di manifest; cermin dilakukan saat runtime lewat flipX).
- Bila satu tampak gagal QA, generate ulang **hanya tampak itu** dengan sheet terpilih sebagai referensi (brief `perViewFallback`).
- Spritesheet akhir: frame 0 front, 1 back, 2 left (+ kanan = flip). Nama frame di manifest: `idle_down`, `idle_up`, `idle_left`, `idle_right`.
- **Animasi jalan Tahap A (wajib):** saat bergerak, frame diam yang sama dengan pantulan vertikal 1–2 px bergantian (≈ 8 Hz), ayunan horizontal ≤ 1 px, bayangan elips berdenyut; tanpa rotasi/skala. Terbaca sebagai "melangkah ringan" dan cukup untuk prototype.
- **Tahap B (opsional, hanya setelah semua gerbang inti lulus):** coba hasilkan pose langkah (`step_a`, `step_b`) per arah dengan stills terpilih sebagai referensi; terima hanya bila lolos QA + tumpang-tindih siluet ≥ 70% terhadap frame diam; bila tidak, pertahankan Tahap A.

## 8. Bangunan, prop, panel, key art, ikon
- Bangunan: satu generasi per bangunan, tampak depan 3/4, pintu di tengah bawah. Tetapkan `doorAnchor` dari gambar (tinjau visual) dan `footprint` (≈ 35% bawah, inset 6% kiri-kanan); verifikasi di overlay kolisi.
- Prop: sheet beberapa objek → `slice_sheet` → `normalize` per ukuran brief.
- Panel lokasi & key art: gambar penuh 16:9, diproses ke ukuran brief (box-downscale + palette_snap), tanpa transparansi.
- Ikon: sheet grid 4×4 → 16 ikon 32×32.

## 9. Log
`docs/ASSET-LOG.md`: tabel `id | percobaan | alat | cacat ditemukan | tindakan | verdict`. Perbarui manifest `qa` dengan ringkasan validator.


## 10. Furnitur dan potret (tambahan v3)
- **Skala seragam per sheet:** untuk sheet berisi banyak item (furnitur, prop, potret), hitung SATU faktor skala untuk seluruh sheet (median dari ), bukan skala per item, supaya ukuran piksel tampak antar-item seragam. Setelah diskalakan, tiap item harus berada dalam ±20% dari ukuran target brief; item yang menyimpang digenerate ulang (bukan di-skala sendiri). Berlaku juga untuk  yang sudah ada.
- Brief tambahan: ; gaya: . Furnitur keluar ke , potret ke  (192×256, menghadap kanan).
- Validator tambahan:  diperiksa visual; dasar furnitur rata di baris terbawah; potret mengisi ≥ 85% tinggi dan identitas warna cocok dengan sprite.
