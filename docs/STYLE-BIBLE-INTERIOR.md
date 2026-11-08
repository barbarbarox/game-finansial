# STYLE BIBLE — Tambahan Interior, Furnitur, dan Potret (v3)

> Melengkapi `docs/STYLE-BIBLE.md` (STYLE BLOCK dan NEGATIVE BLOCK yang sama tetap dipakai di awal/akhir semua prompt). Jika bertentangan, STYLE-BIBLE.md menang kecuali untuk hal yang secara eksplisit diatur di sini.

## 1. Perspektif dan pencahayaan interior
Perspektif 3/4 yang sama dengan hub: furnitur dilihat dari depan dengan kamera agak menunduk (permukaan atas meja/kasur terlihat). Cahaya hangat dari kiri-atas, bayangan sebagai satu nada lebih gelap ke kanan-bawah. Warna interior sedikit lebih hangat dan terang daripada eksterior; tetap dalam palet.

## 2. Skala (acuan semua furnitur; tile = 32 px)
Karakter 64 px tinggi · pintu 64×96 · kursi tinggi ±48 · meja makan/belajar tinggi tampak ±64 · counter kantin/kasir ±64–80 · kasur single 64×96 (kepala di atas) · lemari 64–96 × 96 · sofa 3 dudukan 128×64 · kulkas 64×96 · mesin arcade 48×96. Semua item dalam satu sheet digambar **pada skala dunia nyata yang konsisten satu sama lain** dengan ukuran piksel tampak yang sama.

## 3. Aturan generate furnitur
- Satu sheet berisi 4–6 item sejenis, tersusun kiri→kanan, terpisah jelas, latar magenta polos #FF00FF, **tanpa bayangan jatuh di latar**, utuh (tidak terpotong).
- Pasang: skala dihitung **per sheet** (satu faktor skala untuk seluruh sheet), bukan per item (lihat rule 60 §10), agar ukuran piksel antar-furnitur seragam.
- Tanpa teks/huruf/angka/logo/merek: papan, bingkai, poster, layar TV/arcade, label produk, dan buku **dikosongkan atau dibuat abstrak**.
- Desain khas rumah Indonesia sederhana: perabot kayu/rotan, kipas berdiri, bak mandi dengan gayung, rice cooker, rak piring, sofa kain, karpet. Kamar mandi digambarkan wajar dan netral.

## 4. Potret
Setengah badan (kepala hingga pinggang), tampak 3/4 menghadap kanan, 192×256 px akhir, latar magenta polos. Warna dan pakaian sama dengan kanon sprite. Ekspresi netral-ramah. Kepadatan piksel boleh lebih halus daripada sprite, tetapi tebal outline, palet, dan gaya shading tetap sama. Satu sheet berisi 2–5 potret berdampingan dengan skala identik.

## 5. Kanon ruangan (warna dinding/lantai prosedural; dipilih dari palet)
Rumah: dinding krem `#F7EEDA`/`#E9D8B4`, lis bawah cokelat `#9A6F4C`, lantai kayu cokelat muda · dapur dan kamar mandi: ubin muted green terang `#A5BE93` · ruang kelas: dinding krem + lis hijau `#6F9262`, lantai ubin krem-abu · kantin: tegel cokelat muda · minimarket: dinding krem, lantai ubin abu-krem · toko kosmetik: dinding hijau muted terang · SPBU: beton krem-abu · game center: dinding navy `#34456B`, lantai navy tua `#1F2A44`.
