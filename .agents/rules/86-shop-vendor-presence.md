---
trigger: model_decision
description: "Terapkan saat mengubah panel toko/katalog: tombol keluar/tutup, penutupan dengan Esc/klik di luar, tampilan karakter NPC kasir/penjual di dalam katalog (kantin, minimarket, toko kosmetik, game center, SPBU)."
---

# 86 · Panel Toko: Tombol Keluar dan Kehadiran NPC (menambah rule 79)

## 1. Bug yang diperbaiki
Katalog minimarket tidak memiliki tombol keluar. Katalog juga belum menampilkan karakter kasir/penjual.

## 2. Menutup panel (semua toko, termasuk menu SPBU)
- Tombol **X** di pojok kanan atas + tombol **"Selesai"/"Tutup"** di footer; **Esc** menutup; klik di luar panel menutup (kecuali saat konfirmasi). Fokus kembali ke dunia; input gerak, klik-untuk-bergerak, dan jam melanjutkan seperti sebelum panel dibuka; tidak ada panel tertinggal setengah tertutup.
- Panel dapat diakses keyboard (trap fokus saat terbuka, Tab berputar, Enter pada tombol).

## 3. Kehadiran NPC
- Di dalam panel tampil **potret vendor** (192×256, skala bilangan bulat, `portrait_*` yang sesuai: Bu Sri/penjual kantin, Mbak Maya/kasir minimarket, Kak Cindy/penjaga kosmetik, Kak Riko/penjaga game center, Mas Doni/petugas SPBU) di sisi **kiri** (`shop.vendorSide`), dengan plakat nama dan **gelembung ucapan**: sapaan saat dibuka ("Mau beli apa?"), reaksi setelah pembelian ("Terima kasih!"), reaksi saat saldo kurang/tas penuh/tutup. Teks dari data (`data/dialogues/*`), lewat `textContent`.
- Fallback bila potret tidak ada: siluet berlabel nama (mode debug) dan peringatan konsol; jangan menampilkan panel kosong tanpa NPC.
- Gaya mengikuti UI pengguna dan tata letak dialog (rule 71); tidak menutupi katalog.

## 4. Uji wajib (UI nyata)
Untuk tiap toko: buka → potret vendor benar tampil → X menutup; ulangi dengan Esc dan klik luar; setelah menutup pemain dapat bergerak dan jam berjalan; beli item → reaksi vendor tampil; tangkapan layar tiap toko (desktop + tablet). Tidak ada toko tanpa jalan keluar.
