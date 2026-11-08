---
trigger: model_decision
description: "Terapkan saat membuat atau mengganti tampilan tanah peta kota (jalan, trotoar, rumput, halaman/pad bangunan) dengan gambar hasil image generation yang harus tepat mengikuti layout hub saat ini; termasuk guide render, uji kesesuaian, fallback swatch, dan dekor tanah."
---

# 76 · Terrain Plate (tanah peta kota dari image generation)

## 1. Tujuan dan batas
- Ganti tanah prosedural hub (jalan, trotoar, rumput, halaman, pad tempat bangunan berdiri) dengan gambar hasil generate yang **tepat mengikuti layout sekarang**. **Layout tidak boleh diubah** agar gambar cocok; jika gambar tidak cocok, gambarlah yang diperbaiki/diganti, bukan jalannya.
- **Tidak dibakar ke plate:** bangunan, pohon, semak, lampu, bangku, kendaraan, NPC, teks. Semua itu tetap sprite agar bisa di-y-sort dengan pemain (pohon yang dibakar ke tanah membuat pemain berjalan "di atas" pohon). Pohon dan dekor dibuat lebih bagus lewat sheet baru (bagian 6).
- Plate hanya memuat detail datar: tekstur aspal, marka, paving trotoar, rumput dengan bunga/rumput liar, tanah halaman, retakan, bayangan kontak bangunan (lembut satu nada).

## 2. Alur (Level 1: plate terpandu)
1. **Render guide** dari `town_hub.layout.json` (`tools/render_layout_guide.py` atau rute debug `?debug=1&guide=1` + tangkapan layar): satu warna datar per kelas — aspal, marka (garis), trotoar, rumput, halaman/pad bangunan, area luar dunia — plus grid tile tipis; bangunan tampil sebagai pad persegi berlabel warna "pad" (tanpa sprite). Simpan `assets/terrain/guide_hub.png` dan **mask per kelas** `guide_masks/*.png`. Ukuran dunia: `size` × `tileSize` (mis. 40×24×32 = 1280×768).
2. **Sesuaikan rasio** ke yang didukung generator: pad guide dengan zona "luar dunia" hingga rasio terdekat (mis. 16:9), catat rect dunia untuk crop ulang.
3. **Generate** (guide sebagai gambar referensi, STYLE BLOCK): "Repaint this schematic as cozy chunky pixel-art terrain, top-down 3/4 ground only. Keep every colored region exactly where it is: asphalt roads, sidewalks, grass, yards. Add texture and small ground details only (paving pattern, cracks, road markings, grass tufts, tiny flowers, curb edges). No buildings, trees, bushes, vehicles, people, signs, text. Seamless continuity across regions. Palette: [palet]." Simpan `assets/_raw/terrain_plate_vN.png`.
4. **Proses:** crop ke rect dunia → skala ke ukuran dunia dengan area-average → `palette_snap` (tanpa dithering).
5. **Uji kesesuaian** (`tools/check_plate_conformance.py`): klasifikasikan piksel ke kelas terdekat (centroid warna kelas dari hasil) dan bandingkan dengan mask guide: **IoU per kelas ≥ 0,85**; jarak tepi jalan/trotoar ≤ 6 px; area non-kelas (objek asing: bangunan/pohon/teks terdeteksi komponen besar) = 0; tinjauan visual. Simpan peta panas selisih di `docs/terrain/`.
6. Lulus → daftarkan `terrain_plate_hub` (manifest), `terrain.mode: "plate"`. Gagal 3× → Level 2.

## 3. Level 2 (fallback deterministik: lukis mask dengan swatch)
Generate **swatch** mulus-menyambung 256×256 untuk aspal, trotoar, rumput, halaman (`terrain_swatch_sheet`, QA: selisih tepi wrap ≤ ambang). Lukis tanah dengan mengisi tiap mask dari swatch (jitter offset agar tidak berulang), tambahkan tepi (curb, rumput menjorok) lewat stempel dari kontur mask, lalu tambahkan decal (zebra cross, marka, bunga, retakan, lubang drainase) dari `decal_sheet_v4` pada posisi dari layout. Hasil **pasti** mengikuti layout karena mask-nya dari layout.

## 4. Integrasi
Layer `terrain_plate` di bawah semua objek; `terrain.mode` dapat diganti ke `procedural` (fallback aman, kode tanah lama dipertahankan). Kolisi tetap dari layout, bukan dari gambar. Bila dunia > 2048 px per sisi, pecah plate menjadi potongan 512×512 agar muat memori. Perhatikan ukuran berkas total (≤ 20 MB, rule 20).

## 5. Pengujian
`tests/terrain-check.html`: overlay mask di atas plate (toggle), tabel IoU, tangkapan layar tiap persimpangan dan tiap pintu bangunan (pintu harus mendarat di trotoar/pad yang benar), pemain berjalan dari rumah ke semua bangunan tanpa melewati area yang tampak "air/tembok" yang tidak ada di layout.

## 6. Dekor dan pohon (sprite)
Sheet `prop_sheet_nature_v4` (pohon mangga besar/kecil, palem, pohon rindang, semak berbunga, rumpun bunga), `prop_sheet_street_v4` (lampu, bangku, tong sampah, halte kosong, kotak surat, pagar), `decal_sheet_v4` (zebra cross, panah jalan, bunga di rumput, kerikil, daun, lubang drainase). Pasang sesuai posisi pohon/dekor di layout (jangan menggeser jalan/bangunan); pertahankan sheet lama sampai uji lulus. Skala seragam per sheet (rule 60 §10).
