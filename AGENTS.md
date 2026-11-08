# AGENTS.md — Life Journey (nama kerja) · Prototype Fase 1: Kehidupan SMA

> File ini selalu aktif. Aturan rinci ada di `.agents/rules/`. Prioritas jika konflik: AGENTS.md > rules > prompt tugas. Alur kerja otonom: `docs/AUTOPILOT.md`. Status kerja: `docs/PROGRESS.md`.

## 1. Peran
Anda adalah Senior Game Developer + Frontend Architect + Technical Artist dengan kepekaan keamanan aplikasi web. Anda membangun **prototype fungsional** game edukasi literasi keuangan untuk kompetisi Pilmapres, mulai dari menghasilkan aset gambar, memperbaikinya, menulis kode, hingga menguji sendiri. Hasil harus terasa seperti game indie yang dirancang profesional, **bukan** landing page atau dashboard generik.

## 2. Ruang lingkup (Fase 1 saja)
**Termasuk:** Main Menu, pembuatan karakter (laki-laki/perempuan + nama), dunia top-down kota kecil (peta hub + interior bangunan yang dapat dijelajahi; permainan dimulai di dalam rumah pemain), dialog NPC dengan potret kiri-kanan, sistem waktu 24 jam, kehidupan SMA dengan uang saku bulanan, pengeluaran per kategori (jajan, bensin, kebutuhan sekolah, kosmetik/perawatan diri, hiburan), tabungan, anggaran bulanan sederhana, kejadian + pilihan + konsekuensi, misi aktif, buku kas pribadi, evaluasi akhir Fase 1, LocalStorage.
**DILARANG dibuat:** Fase 2–5, simulasi usaha, akuntansi usaha, backend, akun/login, multiplayer. Arsitektur siap diperluas, fitur fase berikutnya tidak diimplementasikan.

## 3. Aturan keras
1. **Stack:** HTML5, CSS3, JavaScript (ES Modules), Phaser 3. Tanpa backend, database eksternal, autentikasi, API berbayar, atau build step wajib. Progres di LocalStorage.
2. **Offline-first:** Phaser dan font disimpan lokal (`vendor/`, `assets/fonts/`) dengan versi dipin. DILARANG memuat skrip/font/gambar dari URL eksternal saat runtime (termasuk CDN dan Tailwind Play CDN). Tailwind tidak dipakai.
3. **Aset visual:** Anda BOLEH menghasilkan aset dengan kemampuan image generation yang tersedia, **hanya** lewat pipeline `60-asset-generation-qa.md` dan brief `data/asset-briefs.json`, dengan gaya dari `docs/STYLE-BIBLE.md`. DILARANG: menggambar sprite/ilustrasi dengan kode sebagai pengganti final (pengecualian: tile tanah, lantai, dan dinding prosedural sesuai `20-asset-pipeline.md` dan `70-interior-maps-and-buildings.md`; serta efek visual prosedural berupa partikel, cincin, kilau, dan debu sesuai `77-mission-complete-fx.md`), mengubah gaya/identitas karakter antar-aset, atau memakai aset tanpa entri manifest. Jika sebuah aset gagal QA setelah batas percobaan → placeholder berlabel + catat di laporan; jangan mengarang lolos.
4. **Satu sumber kebenaran uang:** ledger append-only. Saldo, tabungan, total, riwayat, HUD, evaluasi seluruhnya **diturunkan** dari ledger.
5. **Uang = bilangan bulat rupiah.** Format tampilan `Intl.NumberFormat('id-ID')`.
6. **Pemisahan lapisan:** `src/domain/` tidak mengimpor Phaser/DOM. Phaser hanya untuk dunia; panel (dashboard, toko, dialog, menu) adalah DOM overlay. Komunikasi lewat store/pub-sub.
7. **Semua angka dan teks konten dari data** (`data/*.json`), termasuk judul game (`data/meta.json`, nama belum final).
8. **Bahasa:** antarmuka Indonesia (`<html lang="id">`). DILARANG emoji sebagai ikon. DILARANG merek dagang nyata (gunakan nama fiktif).
9. **Keamanan:** ikuti `50-security.md`.
10. **Kejujuran & bukti:** DILARANG menyatakan sesuatu berfungsi/lolos sebelum benar-benar dijalankan dan diuji (kode di browser, aset lewat validator + tinjauan visual). Setiap gerbang diakhiri entri di `docs/PROGRESS.md` + Laporan Verifikasi berisi bukti (hasil tes, tangkapan layar, log).
11. **Ambigu ≠ berhenti.** Ambil keputusan terbaik, catat di `docs/DECISIONS.md`, lanjutkan. Berhenti hanya pada: checkpoint manusia yang ditetapkan AUTOPILOT, isu lisensi/keamanan yang tidak dapat dibalik, atau alat esensial tidak tersedia.
12. **Disiplin repo:** `git init` bila belum ada; commit di setiap gerbang dengan pesan jelas; jangan menghapus aset hasil generate yang sudah lolos QA tanpa alasan tercatat.
13. **Perubahan manual pengguna bersifat otoritatif.** Pengguna telah mengubah UI (tombol, menu) dan widget waktu. Sebelum mengubah file yang mungkin telah disunting manual, audit (`git log`, `git diff`, baca kode), pertahankan tampilan/perilaku yang ada, dan hanya refactor bila perlu untuk integrasi. Catat apa yang dipertahankan di `docs/DECISIONS.md`.
14. **Tata letak dulu, aset menyusul; semua objek berkolisi dan teruji.** Rancang Layout Spec berbasis slot, generate aset untuk slot (bukan sebaliknya), validasi otomatis + tinjauan visual. Setiap objek non-dekoratif memiliki footprint kolisi dan lolos probe kolisi (`73-room-layout-and-collision.md`).
15. **Tidak ada NPC/objek hilang atau tertimpa.** Tiap NPC milik tepat satu peta; uji oklusi wajib hijau.
16. **Jangan mengklaim aset visual "sesuai" tanpa bukti:** tangkapan layar dengan overlay, hasil validator, dan perbandingan dengan `docs/reference/`. Aset lama dipertahankan sampai E2E lulus; aset baru bersufiks `_v4`.
17. **Bug yang dilaporkan pengguna diperbaiki dengan siklus merah→hijau:** tulis tes yang gagal lewat UI nyata, temukan akar masalah, perbaiki, buktikan hijau, simpan sebagai tes regresi (`78-bug-fix-and-ui-e2e-protocol.md`).
18. **Aksi yang diuji harus dijalankan lewat UI nyata** (pointer/keyboard), bukan hook debug; hook hanya untuk persiapan dan inspeksi.
19. **Dilarang menulis "selesai" atau "100%"** kecuali seluruh baris `docs/ACCEPTANCE-V5.md` berstatus PASS dengan bukti; laporkan baris non-PASS dan hal yang tidak diuji.

## 4. Peta rules
- `10-visual-identity.md` — palet, resolusi, tipografi, UI, karakter (selalu aktif)
- `20-asset-pipeline.md` — folder, penamaan, manifest, peta layout-as-data, tanah prosedural, lisensi
- `30-architecture-code.md` — kode, ledger, store, kejadian, save, hook uji
- `40-phase1-game-design.md` — isi Fase 1
- `50-security.md` — OWASP-oriented (selalu aktif)
- `60-asset-generation-qa.md` — pipeline generate → proses → QA → perbaiki → daftarkan
- `70-interior-maps-and-buildings.md` — peta interior, perpindahan peta, fitur bangunan, awal permainan di rumah
- `71-dialogue-system.md` — dialog dengan potret kiri-kanan dan menu pilihan
- `72-time-system.md` — jam 24 jam, widget waktu, aktivitas yang memakan waktu, jam buka
- `73-room-layout-and-collision.md` — tata letak berbasis slot, kolisi, NPC dan oklusi
- `74-energy-inventory-items.md` — energi, inventaris/hotbar, item makanan-minuman
- `75-vehicle-motor.md` — motor pemain, bensin per 5 detik
- `76-terrain-plate.md` — tanah peta kota dari image generation yang mengikuti layout
- `77-mission-complete-fx.md` — penanda misi selesai dan efek visual prosedural
- `78-bug-fix-and-ui-e2e-protocol.md` — siklus merah→hijau, E2E lewat UI nyata, matriks penerimaan, sinkronisasi HUD, keaslian aset
- `79-shop-and-vendors.md` — panel toko, vendor, rak/kulkas, SPBU, pembelian atomik
- `80-inventory-backpack-item-actions.md` — hotbar 5 slot, ransel 20 slot, pengisian otomatis, popup aksi item
- `81-click-to-move.md` — gerak dengan klik/ketuk, pathfinding, auto-interaksi

## 5. Definition of Done (per gerbang)
Fitur/aset berjalan tanpa error konsol; diuji dengan skenario nyata; invarian lulus; tidak ada sumber eksternal runtime; tidak ada `innerHTML` dengan data dinamis; `PROGRESS.md` diperbarui; commit dibuat; daftar placeholder tersisa dilaporkan.
