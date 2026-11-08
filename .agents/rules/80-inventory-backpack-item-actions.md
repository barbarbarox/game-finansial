---
trigger: model_decision
description: "Terapkan saat mengubah inventaris: hotbar 5 slot, tombol dan panel ransel, penumpukan otomatis ke ransel, pengisian otomatis hotbar dari ransel, popup aksi item (Gunakan/Pindahkan/Buang), atau migrasi save inventaris."
---

# 80 · Hotbar, Ransel, dan Aksi Item (menggantikan §3 rule 74)

## 1. Model data (domain `inventory.js`)
`inventory = { hotbar: [slot|null ×5], backpack: [slot|null ×20] }`, `slot = {itemId, count}`, `stackMax` default 5 (config `inventory.*`). Kapasitas total = 25 slot. Save v4 memigrasikan `inventory[]` lama (v3): item mengisi hotbar lalu ransel.

## 2. Aturan penambahan dan pengisian otomatis
- `canAdd(itemId, n)` memeriksa **seluruh** n muat; pembelian memanggil `canAdd` **sebelum** mengurangi saldo (all-or-nothing).
- Urutan `add`: tumpukan item sama di hotbar → slot kosong hotbar → tumpukan item sama di ransel → slot kosong ransel.
- **Hotbar penuh → item ke ransel.** Hotbar dan ransel penuh → pembelian ditolak ("Tas penuh", saldo tetap).
- **Pengisian otomatis:** setiap kali sebuah slot hotbar menjadi kosong (dipakai habis, dipindah, dibuang) dan ransel masih berisi, hotbar **otomatis terisi** dari ransel: utamakan item yang **sama** dengan slot yang baru kosong; jika tidak ada, ambil slot ransel berisi pertama (urutan indeks); pindahkan hingga `stackMax`.
- **Invarian:** jika ada slot hotbar kosong maka ransel kosong. Tes properti acak (≥ 200 operasi) memeriksa invarian ini dan total jumlah item konservatif (tidak ada item hilang/ganda).

## 3. Tombol dan panel ransel
- **Tombol ransel** tepat di samping hotbar (kanan), ikon `icon_tas`, lencana jumlah total item di ransel, pintasan **B**. Gaya mengikuti hotbar/UI pengguna.
- Klik membuka **panel ransel** (grid 5×4 = 20 slot): ikon + jumlah per slot, kapasitas "y/20", tombol Tutup, Esc menutup. Panel ransel termasuk panel (jam berhenti).
- Slot kosong tampil sebagai kotak kosong; slot terkunci tidak ada.

## 4. Popup aksi item (sentuh = opsi)
- **Klik/ketuk slot** (hotbar atau ransel) membuka popup berlabuh di slot: ikon, nama, jumlah, deskripsi singkat (+N Energi, waktu makan), dan tombol:
  - **Gunakan** (nonaktif + alasan bila energi ≥ 95% untuk item energi-only, dialog terbuka, atau TimeSkip),
  - **Pindahkan** (hotbar → ransel atau ransel → hotbar; menukar bila tujuan penuh dan sejenis), 
  - **Buang** (konfirmasi: "Membuang makanan = membuang uang (Rp…)"; item hilang tanpa pengembalian).
- Popup bisa dioperasikan keyboard (panah/Enter, Esc menutup) dan sentuh; tidak menutupi slot lain; tertutup saat klik di luar.
- **Pintasan 1–5 = pakai cepat** slot hotbar (tanpa popup); ini dicatat di panduan tombol Settings.
- Gunakan dari ransel diperbolehkan; efek sama dengan rule 74 (energi naik, `consumeMinutes` lewat `advanceTime`, teks mengambang "+N Energi"). Setelah pemakaian, pengisian otomatis dijalankan.

## 5. Keamanan dan keandalan
Validasi skema save (itemId di katalog, jumlah bulat 1..stackMax, panjang array = kapasitas), tolak kunci berbahaya; popup/tooltip lewat `textContent`; operasi invent atomik (tidak ada keadaan setengah).

## 6. Uji wajib (UI nyata, rule 78)
Beli 7 item berbeda berturut-turut → 5 di hotbar, 2 di ransel (DOM + state); pakai satu dari hotbar → slot terisi otomatis dari ransel; invarian properti acak; tombol ransel membuka panel dan lencana benar; klik slot hotbar menampilkan popup Gunakan/Pindahkan/Buang dan masing-masing bekerja; Gunakan item dari panel ransel menaikkan energi; Buang meminta konfirmasi; tas 25/25 menolak pembelian tanpa mengurangi saldo; simpan/muat dan migrasi dari v3; tangkapan layar hotbar, panel ransel, popup (desktop + tablet).
