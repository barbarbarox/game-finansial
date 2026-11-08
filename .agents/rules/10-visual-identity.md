---
trigger: always_on
description: "Identitas visual Life Journey: palet, resolusi pixel art, tipografi, komponen UI, aturan konsistensi karakter."
---

# 10 · Identitas Visual (WAJIB konsisten di semua halaman)

## 1. Gaya
- **Cozy 16-bit pixel art, top-down 3/4 ala RPG** (kamera miring, fasad bangunan terlihat). Bukan isometrik, bukan overhead murni.
- Nuansa hangat, tenang, kota kecil Indonesia. Dunia game = pixel art. Dashboard/tabel = tipografi modern yang mudah dibaca.

## 2. Palet (token tunggal di `src/ui/tokens.css`, jangan menyalin hex di tempat lain)
| Token | Hex | Peran |
|---|---|---|
| `--cream-100` | #F7EEDA | latar panel terang |
| `--cream-300` | #E9D8B4 | latar sekunder, shading |
| `--green-400` | #A5BE93 | sorotan hijau |
| `--green-600` | #6F9262 | hijau utama (nilai positif) |
| `--green-800` | #44603F | hijau gelap (teks positif, tas punggung) |
| `--brown-300` | #C9A27A | cokelat muda |
| `--brown-500` | #9A6F4C | soft brown utama |
| `--brown-800` | #5E3F2A | cokelat gelap (rambut, outline hangat) |
| `--navy-600` | #34456B | navy menengah |
| `--navy-800` | #1F2A44 | dark navy utama (teks, border UI) |
| `--navy-950` | #121A2E | latar tergelap |
| `--terracotta-500` | #C0654A | isi/ikon negatif & peringatan |
| `--terracotta-700` | #9E4A33 | TEKS negatif (kontras ≥ 4.5:1) |
| `--mustard-500` | #D9A441 | koin, tabungan, sorotan kecil |
| `--grey-400` | #9AA0AA | HANYA untuk seragam putih-abu-abu |
| `--sky-dawn` | #E8B25A | HANYA Sky Dial: fajar keemasan (pagi) |
| `--sky-day` | #7FB6D9 | HANYA Sky Dial: biru cerah (siang) |
| `--sky-dusk` | #E07B4F | HANYA Sky Dial: senja jingga kemerahan (sore) |
| `--sky-night` | #16213B | HANYA Sky Dial: biru pekat (malam) |

Aturan warna: nilai positif = hijau, negatif = terracotta, netral = navy. Mustard hanya aksen kecil. Teks wajib memakai token gelap (`-700/-800`) di atas cream agar kontras ≥ 4.5:1.

## 3. Resolusi & rendering Phaser
- Tile dasar **32×32 px** (parameter `tileSize` di `data/phase1.config.json`, jangan di-hard-code). Karakter **32×64 px** (1×2 tile). Canvas logis **960×540** (16:9), skala FIT dan terpusat; utamakan zoom bilangan bulat.
- Alasan 32 px: aset hasil generator gambar kehilangan terlalu banyak detail bila diturunkan ke grid 16 px. Gaya yang dituju adalah "chunky pixel art" yang bersih; bukan strict 16-bit.
- Config wajib: `pixelArt: true`, `antialias: false`, `roundPixels: true`. CSS: `image-rendering: pixelated` pada canvas dan gambar pixel di DOM.
- DILARANG: skala non-integer pada sprite, rotasi sprite, blur, tint yang mengubah identitas warna karakter.

## 4. Karakter (konsistensi mutlak)
- Pemain memilih **laki-laki atau perempuan**; tiap pilihan = **satu spritesheet tetap** dari manifest, dipakai di SEMUA scene (menu, dunia, panel, evaluasi).
- Kanon karakter ada di `docs/STYLE-BIBLE.md` (rambut cokelat gelap, kaos cream, bawahan navy, sepatu cokelat, tas punggung hijau gelap). Jangkar rambut/sepatu/tas tidak berubah lintas fase.
- Empat arah hadap: bawah (front), atas (back), kiri (left), kanan = cermin kiri. Animasi jalan: lihat `60-asset-generation-qa.md` bagian Karakter.
- Dilarang membuat varian karakter ad-hoc atau mengganti proporsi.

## 5. Tipografi
- Font pixel (OFL, lokal): hanya untuk logo, judul scene, dialog NPC, label HUD pendek.
- Font sans-serif modern (OFL, lokal) untuk dashboard, tabel, form, riwayat transaksi, panel toko. Angka memakai `font-variant-numeric: tabular-nums`, rata kanan di tabel.
- Font pixel DILARANG dipakai untuk angka uang berukuran kecil di tabel.
- Tunggu font siap (`document.fonts.load`) sebelum membuat teks Phaser.

## 6. Komponen UI (CSS, bukan gambar)
- Panel: isi solid cream, border 2–3 px `--navy-800`, bayangan keras bertahap (tanpa blur), radius 0–2 px. Tombol punya state: normal, hover, active, disabled, focus-visible.
- Animasi sederhana dan fungsional (umpan balik klik, perubahan saldo, panel masuk 120–200 ms). Hormati `prefers-reduced-motion`.
- DILARANG: gradient, glassmorphism, neon, bayangan blur, pill UI, kartu "SaaS", ikon emoji, elemen tanpa fungsi. **Pengecualian disetujui pengguna:** gradient langit hanya di komponen Sky Dial widget waktu, dan tab hari (Day Pill) berbentuk tab emas bersudut piksel. Emoji tetap dilarang (matahari/bulan dibuat dengan CSS/sprite). **Pengecualian disetujui pengguna:** gradient langit hanya di komponen Sky Dial widget waktu, dan tab hari (Day Pill) berbentuk tab emas bersudut piksel. Emoji tetap dilarang (matahari/bulan dibuat dengan CSS/sprite).
- Ikon hanya dari `assets/icons/` (PNG pixel 16/24 px) atau set SVG proyek yang dimuat lewat `<img>`. Tanpa icon font eksternal.

## 7. Layout & aksesibilitas
- Responsif desktop (≥1024 px) dan tablet (≥768 px, portrait/landscape). HUD tidak menutupi area bermain penting.
- Kontrol: WASD/panah bergerak, E/Spasi berinteraksi, Esc menutup panel/menu. Semua tombol bisa dioperasikan keyboard; fokus terlihat; trap fokus di dialog modal.

## 8. Checklist konsistensi (jalankan sebelum melapor selesai)
- [ ] Hanya token warna dari `tokens.css` yang dipakai.
- [ ] Karakter identik di menu, dunia, panel, evaluasi.
- [ ] Font pixel tidak bocor ke tabel/dashboard.
- [ ] Tidak ada emoji, gradient, bayangan blur.
- [ ] Teks memenuhi kontras; panel dapat dioperasikan keyboard.
