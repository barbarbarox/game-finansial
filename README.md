# Life Journey — Simulasi Kehidupan Finansial SMA

Prototype game edukasi literasi keuangan untuk kompetisi Pilmapres.

## Gambaran Proyek
- **Genre:** 2D Top-Down 3/4 Cozy RPG Simulation
- **Target Platform:** Web (Desktop & Tablet)
- **Teknologi:** HTML5, CSS3, JavaScript (ES Modules), Phaser 3.80.1 (offline-first tanpa build step)
- **Arsitektur:** Pemisahan domain murni (Double-entry ledger), Store pub-sub, Scene Phaser, dan DOM overlay untuk antarmuka pengguna.

## Fitur Utama Fase 1
1. **Kehidupan Siswa SMA:** Uang saku bulanan Rp1.000.000, pengeluaran harian, bensin motor, dan pos kebutuhan vs keinginan.
2. **Akuntansi Terintegrasi:** Append-only ledger double-entry sebagai satu-satunya sumber kebenaran saldo.
3. **Peta Kota Kecil:** 6 lokasi interaktif (Rumah, Kantin Sekolah, Minimarket, Toko Kosmetik, SPBU, Game Center).
4. **Celengan Ayam:** Tabungan fleksibel dengan setoran/tarikan tanpa bunga atau biaya administrasi.
5. **Perencana Anggaran Bulanan:** Pos alokasi anggaran dengan perbandingan realisasi otomatis.
6. **Buku Kas Pribadi:** Dashboard riwayat transaksi lengkap dan filter kategori.
7. **11 Kejadian & Keputusan:** Pilihan dilema keuangan dengan tag edukasi literasi finansial.
8. **Keamanan Web Klien (OWASP):** Nol penggunaan `innerHTML` pada data dinamis, Content Security Policy ketat, sanitasi skema LocalStorage.

## Cara Menjalankan Game

Tidak memerlukan instalasi npm atau build tools. Jalankan server statis lokal:

```bash
cd game
python3 -m http.server 3838
```

Buka browser Anda ke:
[http://localhost:3838/](http://localhost:3838/)

### Menjalankan Pengujian Mandiri (Self-Tests)
- **Uji 6 Invarian Akuntansi:** Buka `http://localhost:3838/tests/self-test.html`
- **Uji Spritesheet Karakter & Animasi:** Buka `http://localhost:3838/tests/character-sheet.html`
- **Uji Manifest Aset:** Buka `http://localhost:3838/tests/asset-check.html`
- **Uji E2E Browser Otomatis:** `python3 tools/test_e2e_browser.py`
