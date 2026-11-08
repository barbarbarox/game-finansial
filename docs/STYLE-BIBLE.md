# STYLE BIBLE — Life Journey (sumber tunggal gaya untuk SEMUA aset gambar)

> Dipakai oleh pipeline `60-asset-generation-qa.md`. Prompt akhir untuk generator = **STYLE BLOCK + SUBJECT (dari `data/asset-briefs.json`) + NEGATIVE BLOCK**. Jangan menulis ulang gaya di tempat lain.

## 1. STYLE BLOCK
```
Cozy chunky pixel art with clearly visible square pixels, top-down 3/4 RPG perspective (camera tilted so building fronts and character faces are visible; NOT isometric, NOT pure overhead). Crisp hard-edged pixels, no anti-aliasing, no blur, no gradients, no dithering noise, flat shading with 2-3 tones per material, 1px dark warm outline (#2A1F1A-like deep brown/navy). Soft warm morning light from the upper left, shadows as one flat darker tone falling to the lower right. Calm, warm, cozy mood of a small Indonesian town. Limited palette built around: warm cream #F7EEDA and #E9D8B4; muted green #A5BE93, #6F9262, #44603F; soft brown #C9A27A, #9A6F4C, #5E3F2A; dark navy #1F2A44, #34456B. Sparing accents only: mustard #D9A441, terracotta #C0654A.
```

## 2. NEGATIVE BLOCK
```
Avoid: any text, letters, numbers, logos, watermarks, real-world brand names, photorealism, 3D render, smooth vector art, glow, neon, soft airbrushed shading, drop shadows with blur, emoji, isometric view, extra characters, cropped subjects, busy backgrounds, anti-aliased edges.
```

## 3. Latar untuk subjek terisolasi
Selalu **latar magenta polos #FF00FF** (tanpa bayangan jatuh di latar, tanpa gradasi), subjek utuh dengan margin kecil. Tidak boleh ada warna magenta/pink pada subjek.

## 4. Kanon karakter (TIDAK BOLEH BERUBAH)
- **Protagonis laki-laki:** remaja SMA ±16 th, ramping, proporsi chibi RPG (±3 kepala, lebar:tinggi ≈ 1:2), rambut pendek rapi cokelat gelap #5E3F2A, kaos cream #F7EEDA (bayangan #E9D8B4), celana panjang navy #1F2A44, sepatu cokelat #9A6F4C, tas punggung hijau gelap #44603F dengan tali terlihat dan saku kecil.
- **Protagonis perempuan:** sama (proporsi, warna kaos/celana/sepatu/tas), rambut cokelat gelap sebahu dengan kuncir rendah sederhana.
- **Varian seragam (opsional):** kemeja putih krem #FBF6EA + bawahan abu-abu #9AA0AA; rambut, sepatu, tas tetap.
- **Orang tua:** ayah ±45 th, rambut hitam pendek, polo hijau muted #6F9262, celana cokelat #5E3F2A. Ibu ±42 th, rambut disanggul rapi, blus cream, celemek terracotta #C0654A, rok navy #34456B.
- **Teman:** satu laki-laki, satu perempuan, seragam putih-abu-abu, gaya rambut berbeda, tas berwarna mustard #D9A441 dan navy #34456B.
- **Petugas/penjual:** penjual kantin (celemek, kain kepala), kasir minimarket (rompi hijau muted), penjaga toko kosmetik (blus cream, rambut dikuncir), petugas SPBU (topi dan rompi navy), penjaga game center (hoodie cream). Tanpa tanda merek.

## 5. Kanon lingkungan (kota kecil Indonesia, nuansa hangat)
Atap genteng terracotta, dinding krem/hijau muted, kanopi, pagar rendah, halaman kecil, pohon mangga dan palem, kabel listrik sederhana (opsional), motor matic parkir, warung/gerobak jajanan, gerbang sekolah dengan tiang bendera merah-putih kecil. Semua papan nama **dikosongkan**. Nama lokasi fiktif hanya muncul di UI game lewat font, bukan di gambar.

## 6. Perspektif & skala
Tile 32 px; karakter 32×64 px (1×2 tile). Pintu bangunan tingginya ±64 px agar sebanding dengan karakter. Semua aset memakai perspektif 3/4 yang sama dan arah cahaya yang sama.

## 7. Cara menjaga konsistensi
1. Generate karakter pertama sebagai **jangkar gaya**; setelah lolos QA + checkpoint manusia, sertakan sheet terpilih sebagai gambar referensi di setiap generate karakter/NPC berikutnya ("match the exact art style, pixel size, outline weight and palette of the reference image").
2. Bangunan pertama (sekolah) menjadi jangkar gaya lingkungan; sertakan sebagai referensi untuk bangunan/prop berikutnya.
3. Gunakan seed yang sama bila alat mendukungnya; catat di manifest.
4. Semua aset akhir dikunci ke `assets/palette.json` oleh tool `palette_snap`.
