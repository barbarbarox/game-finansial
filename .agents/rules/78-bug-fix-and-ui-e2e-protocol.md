---
trigger: model_decision
description: "Terapkan setiap kali memperbaiki bug yang dilaporkan pengguna, menulis/menjalankan tes E2E atau QA, menyatakan fitur 'selesai/lulus', memeriksa sinkronisasi HUD dengan state, atau mengaudit keaslian aset (placeholder)."
---

# 78 · Protokol Perbaikan Bug dan E2E Berbasis UI Nyata

## 0. Mengapa aturan ini ada
Laporan sebelumnya menyatakan "100% lulus", padahal pengguna menemukan: item yang dibeli tidak masuk inventaris, menu pilihan item tidak ada, bar bensin tidak berubah setelah isi bensin, furnitur "AI" ternyata kotak placeholder berlabel (46 berkas). Penyebab umum: **tes memakai hook debug atau pemeriksaan metadata yang melewati jalur UI nyata**, sehingga hijau palsu. Aturan di bawah menutup celah itu.

## 1. Siklus Merah → Hijau untuk setiap bug
1. **Reproduksi dulu:** tulis tes yang **gagal** (merah) dan mencerminkan laporan pengguna lewat UI nyata. Simpan hasil merah (log + tangkapan layar) di `docs/regression/<id>-red.md`.
2. **Temukan akar masalah** (tulis satu paragraf: file, fungsi, mengapa) di `docs/DECISIONS.md`.
3. **Perbaiki seminimal mungkin**, tanpa menimpa kerja manual pengguna (AGENTS.md #13).
4. Jalankan tes yang sama → **hijau**, dengan tangkapan layar sebelum/sesudah. Tes tetap dipertahankan sebagai tes regresi (`tests/regression/`).
5. Jalankan seluruh tes lama; tidak boleh ada regresi.

## 2. E2E harus lewat UI nyata
- Aksi yang **diuji** (beli item, klik slot, naik motor, isi bensin, klik untuk berjalan, tidur) harus dijalankan dengan **peristiwa pointer/keyboard nyata** pada browser (mis. CDP `Input.dispatchMouseEvent`/`dispatchKeyEvent` atau klik DOM sungguhan), bukan lewat `window.__LJ__`.
- Hook debug hanya boleh dipakai untuk **persiapan** (beri saldo, set waktu, teleport awal) dan **inspeksi** (baca state). Jika sebuah tes memakai hook untuk melakukan aksi yang diuji, tes itu **tidak sah**.
- Setiap aksi diverifikasi di tiga tempat: (a) **state domain** (ledger, inventaris, bensin, energi), (b) **DOM** (teks/lebar bar/ikon slot yang benar-benar tampil), (c) **tangkapan layar** sebelum dan sesudah.
- Sertakan **uji negatif**: saldo kurang, tas penuh, toko tutup, target tak terjangkau, tangki sudah penuh.

## 3. Matriks penerimaan
`docs/ACCEPTANCE-V5.md` memuat setiap permintaan pengguna sebagai baris (ID, langkah UI, hasil yang diharapkan, bukti). Agen mengisi `docs/ACCEPTANCE-V5-RESULTS.md`: status **PASS/FAIL/BELUM**, nama tes, tautan tangkapan layar. **PASS hanya sah dengan bukti.** Dilarang menulis "100%" atau "selesai" bila ada baris non-PASS; laporkan jumlahnya dan alasannya.

## 4. Sinkronisasi HUD dengan state
- Semua perubahan state melalui satu pintu domain yang **memancarkan event bertipe** (mis. `fuelChanged`, `energyChanged`, `cashChanged`, `inventoryChanged`, `backpackChanged`, `mapChanged`). Komponen UI **berlangganan** event, bukan menyalin angka.
- **Tes sinkronisasi** (`tests/hud-sync.html`): untuk tiap indikator HUD (saldo, tabungan, bensin, energi, jam, hotbar, lencana ransel, misi), ubah state lewat fungsi domain yang sama dengan yang dipakai game, lalu pastikan DOM berubah ≤ 200 ms dan nilainya sama dengan state. Tambahkan tes bahwa **setiap tipe event punya minimal satu pelanggan**.
- Audit statis: cari kode yang mengubah `state.*` langsung tanpa melalui domain.

## 5. Keaslian aset (anti-placeholder)
Status `ready` di manifest **tidak cukup**. Jalankan audit piksel (`tools/audit_asset_authenticity.py`): tandai PNG yang berjumlah warna sangat sedikit (≤ 6) dan terisi blok polos ≥ 95% bounding box, atau memiliki pola tepi emas/teks, atau ukurannya identik dengan placeholder diketahui. Hasil dilengkapi `contact_sheet` per peta dan **tinjauan visual** tangkapan layar tiap interior. Laporkan jumlah aset mencurigakan; aset yang ternyata placeholder tidak boleh berstatus `ready`.

## 6. Pelaporan jujur
Laporan akhir wajib memuat: ringkasan matriks penerimaan (PASS/FAIL/BELUM), bug yang direproduksi + akar masalah, hal yang **tidak** diuji, batasan yang diketahui, dan daftar tes yang memakai hook (beserta alasannya). Angka 100% hanya bila seluruh matriks PASS.
