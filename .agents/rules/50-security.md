---
trigger: always_on
description: "Aturan keamanan aplikasi web client-side (OWASP-oriented) untuk Life Journey."
---

# 50 · Keamanan (WAJIB)

Aplikasi client-side tanpa backend. Permukaan serangan kecil tetapi nyata. Pemetaan OWASP Top 10 (2021) di tiap aturan.

1. **Injeksi/XSS (A03):** data dinamis (nama karakter, nama orang tua/teman, deskripsi transaksi, data dari LocalStorage) DILARANG masuk lewat `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`. Gunakan `textContent`, `createElement`, atau `Phaser.GameObjects.Text`. Tanpa atribut event inline (`onclick=`).
2. **Validasi input (A03/A04):** nama = 1–20 karakter, huruf Unicode/spasi/apostrof/tanda hubung, trim, normalisasi spasi. Nominal = bilangan bulat, `0 < n ≤ batas` dari config, bukan NaN/Infinity. Validasi di **domain**, bukan hanya di UI.
3. **Integritas data tersimpan (A08):** validasi skema LocalStorage saat dimuat (whitelist key, tipe, rentang); tolak `__proto__`, `constructor`, `prototype`; buat objek bersih (`Object.create(null)` atau salin field ter-whitelist). Simpan `schemaVersion` + migrasi. Data rusak → tawarkan reset aman, jangan crash. Saldo dihitung ulang dari ledger saat muat dan dicocokkan. Catat di docs bahwa LocalStorage bisa diubah pemain dan **bukan batas keamanan**.
4. **Supply chain (A06/A08):** semua pustaka lokal di `vendor/` dengan versi dipin dan checksum dicatat di `docs/SECURITY-NOTES.md`. Tanpa CDN/skrip pihak ketiga runtime. Tanpa analytics/telemetri/tracker.
5. **Misconfiguration (A05):** tambahkan CSP lewat `<meta http-equiv="Content-Security-Policy">` yang ketat: `default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data: blob:; font-src 'self'; media-src 'self' blob:; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'none'`. Jika sesuatu terblokir, longgarkan seminimal mungkin dan catat alasannya; jangan menghapus CSP.
6. **Eksekusi dinamis:** DILARANG `eval`, `new Function`, `setTimeout(string)`.
7. **Aset pihak ketiga:** muat SVG hanya lewat `<img>` (jangan inline) dan hanya dari folder `assets/`; jangan eksekusi file biner dari paket aset. Aset dengan lisensi tidak jelas tidak boleh ditambahkan.
8. **Ketahanan:** bungkus akses LocalStorage dengan try/catch (quota, mode privat); batasi ukuran save (mis. ≤ 512 KB); tangani kegagalan muat aset dengan fallback placeholder + peringatan konsol.
9. **Privasi:** data hanya lokal; nama yang diisi pemain tidak dikirim ke mana pun. Tampilkan catatan privasi singkat di Settings.
10. **Bukti:** `docs/SECURITY-NOTES.md` memuat tabel risiko → mitigasi → file/fungsi yang menerapkan, dan hasil audit diri (grep `innerHTML`, `eval`, URL eksternal) di laporan verifikasi.
11. **Hook debug (A05):** `window.__LJ__` hanya aktif dengan `?debug=1` dan `debugEnabled: true`; default rilis `false`; audit akhir wajib memastikan nonaktif. Hook memanggil domain biasa, tidak melewati validasi.
12. **Keamanan kerja agen otonom:** jangan membaca atau menjalankan skrip dari sumber tak dikenal; koneksi jaringan hanya untuk mengunduh paket terverifikasi (Phaser) dan alat generate gambar resmi; jangan menulis kunci API/rahasia ke repo; jangan menjalankan perintah destruktif di luar folder proyek; pasang pustaka Python/Node untuk tools hanya dari registry resmi dengan versi dipin dan catat di `docs/SECURITY-NOTES.md`.
13. **Aset hasil generate:** periksa berkas keluaran hanya berupa gambar (PNG/JPEG/WebP), konversi ke PNG murni dan buang metadata sebelum masuk `assets/`; catat sumber `ai-generated`, alat, tanggal, dan prompt.

14. **Data peta dan dialog:** layout peta dan dialog divalidasi skema saat dimuat (tipe, rentang, referensi aset/peta yang ada, efek dialog di whitelist). Teks dialog dan nama dirender hanya lewat .
15. **Hook uji tambahan** (`advanceTime`, `openDialogue`, `selectChoice`, `teleportToMap`) tunduk pada aturan hook debug yang sama: hanya aktif dengan `?debug=1` dan `debugEnabled: true`.
16. **Data inventaris/item/save v3:** validasi skema (itemId harus ada di katalog, jumlah bilangan bulat 1..stackMax, jumlah slot ≤ batas), tolak kunci berbahaya; teks tooltip/efek lewat `textContent`.
17. **Hook uji v4** (`giveItem`, `setEnergy`, `setFuel`, `completeMission`, `advanceRealSeconds`, dsb.) hanya aktif dengan `?debug=1` dan `debugEnabled: true`; audit akhir memastikan nonaktif pada rilis dan tidak ada jalan pintas yang melewati domain.


18. **Data toko dan transaksi (v5):** validasi skema `shops.phase1.json` (itemId ada di katalog dan punya ikon, harga bilangan bulat, jumlah 1..batas); transaksi pembelian atomik (ledger + inventaris, tanpa keadaan setengah); nominal isi bensin dihitung di domain, bukan dari UI.
19. **Input pointer (v5):** abaikan peristiwa pada elemen UI DOM; koordinat klik divalidasi dan dibatasi ke batas peta; anggaran waktu pathfinding dibatasi (`pathBudgetMs`) agar tidak membekukan game; tidak ada eksekusi dari data klik.
20. **Hook uji tidak sah untuk aksi yang diuji** (rule 78); audit akhir mencatat tes yang memakai hook dan memastikan hook nonaktif pada rilis.
