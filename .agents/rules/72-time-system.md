---
trigger: model_decision
description: "Terapkan saat menyentuh jam/kalender permainan, widget waktu (Sky Dial, Day Pill, jam digital, bar 24 jam), aktivitas yang memakan waktu, jam buka, jadwal sekolah, tidur, atau transaksi yang bertanda waktu."
---

# 72 · Sistem Waktu

## 0. Perubahan manual pengguna bersifat otoritatif
Pengguna sudah memperbarui UI (tombol, menu) dan mengimplementasikan widget waktu real-time. **Audit dulu** kode saat ini (`git log`, `git diff`, baca implementasi widget). Pertahankan tampilan dan perilaku yang sudah ada; hanya hubungkan ke domain clock dan tambahkan yang belum ada. Jangan menimpa atau menata ulang UI buatan pengguna.

## 1. Domain clock (satu sumber kebenaran, tanpa DOM)
- State: `gameMinutes` bilangan bulat sejak hari 1 pukul 00:00. Turunan: hari ke-N, hari dalam pekan (`startWeekday`, default Senin), bulan (30 hari), jam:menit, fase hari.
- Fase hari: PAGI 06:00–11:00, SIANG 11:00–15:00, SORE 15:00–18:00, MALAM 18:00–06:00.
- Tick real-time memakai laju `realSecondsPerGameMinute` dari config; **pertahankan laju yang kini dipakai pengguna** (baca implementasinya). Jam berhenti saat dialog/panel/menu terbuka.
- **Satu pintu `advanceTime(minutes, reason)`** untuk semua pergerakan waktu (tick real-time maupun aktivitas). Ia memproses interval dalam potongan ≤ 5 menit dan memancarkan hook berurutan: `minute`, `hourChanged`, `phaseChanged`, `dayChanged` (menaikkan hari + hari pekan), `monthChanged`, `openStateChanged(locationId)`. Tidak boleh ada pemicu yang terlewat saat lompat waktu.
- Setiap transaksi ledger mencatat `day` dan `minuteOfDay`; riwayat menampilkan jam.

## 2. Widget waktu (spesifikasi perilaku; tampilan mengikuti implementasi pengguna)
- **Sky Dial Box** di kiri: langit berubah sesuai fase — Pagi fajar keemasan, Siang biru cerah, Sore senja jingga kemerahan, Malam biru pekat; marker matahari/bulan aktif bergerak mengikuti jam. Gradient **diizinkan hanya di komponen ini** (pengecualian dari rule 10). Token warna: `--sky-dawn`, `--sky-day`, `--sky-dusk`, `--sky-night` (+ stop sekunder) di `tokens.css`. Marker dibuat dengan CSS/sprite pixel, **bukan emoji**.
- **Day Pill:** tab emas kontras (`--mustard-500`) berisi SENIN…MINGGU dihitung dari hari berjalan.
- **Tanggal:** "Hari N · Bln M".
- **Jam digital inset:** format HH:MM, titik dua berkedip tiap detik nyata, tag fase (PAGI/SIANG/SORE/MALAM).
- **Bar waktu 24 jam:** mengisi 0–100% halus (transisi) mengikuti 00:00–24:00; reset saat hari berganti. Saat lompat waktu aktivitas, bar dan jam bergerak cepat tetapi tetap konsisten.
- Opsional: tint ambient pada hub mengikuti fase (overlay warna solid beropasitas rendah, bukan gradient); interior tidak ditint.

## 3. Aktivitas yang memakan waktu
Satu katalog `data/activities.phase1.json`: `{id, label, durationMinutes | durationOptions[], cost, requires (lokasi/objek, jendela waktu, hari), effects[]}`. Eksekusi: pilih durasi (bila ada opsi) → validasi (jam buka, saldo) → **TimeSkip**: overlay redup + nama aktivitas + progres; jam dan bar bergerak cepat (≈ `fastForwardMinutesPerSecond`, default 75 → 1 jam ≈ 0,8 detik) lewat `advanceTime` → efek diterapkan (transaksi + flag) setelah selesai → ringkasan singkat. Kejadian acak ditunda sampai TimeSkip selesai. Tidak ada aktivitas yang mengubah waktu di luar `advanceTime`.
| Aktivitas | Lokasi/objek | Durasi default | Biaya | Catatan |
|---|---|---|---|---|
| tidur | kasur | sampai 06:00 (min 4 jam) | 0 | hari berganti |
| istirahat | kasur | 60 | 0 | |
| belajar_mandiri | meja belajar | 60 (1–3 jam) | 0 | |
| makan_rumah | meja makan | 20 | 0 | ditanggung ortu; jam makan 06–08, 12–14, 18–20 |
| mandi | kamar mandi | 15 | 0 | |
| ganti_baju | lemari | 5 | 0 | |
| nonton_tv | TV rumah | 60 (1–3 jam) | 0 | alternatif hiburan gratis |
| ngobrol_ortu | NPC | 10 | 0 | |
| ikut_pelajaran | ruang kelas | sampai 14:30 | 0 | hari sekolah, mulai 07:00 |
| baca_perpustakaan | perpustakaan | 60 | 0 | |
| makan_siang_kantin | konter kantin | 20 | 10.000 | kantin buka |
| jajan_kantin | konter kantin | 10 | 5.000 | |
| belanja_minimarket | kasir/rak | 15 | sesuai item | |
| fotokopi | mesin fotokopi | 10 | 5.000 | |
| beli_kosmetik | etalase/kasir | 20 | sesuai item | |
| isi_bensin | dispenser SPBU | 10 | 20.000 | +40% bensin |
| main_game | mesin arcade | 60 (1–3 jam) | 10.000/jam | contoh: 1 jam = +60 menit |
| nonton_mini | TV game center | 120 | 40.000 | |
| nongkrong_kafe | meja kafe | 90 | 30.000 | |
Biaya mengikuti `40-phase1-game-design.md`; angka ini default yang boleh disetel di data. Kejadian ekonomi memakan 5–10 menit.

## 4. Jadwal dan jam buka
- Hari sekolah Senin–Jumat: pelajaran 07:00–14:30. Kehadiran dicatat lunak (`attendanceCount`, tanpa efek uang; dilaporkan di evaluasi). Bangunan dan kantin mengikuti jam buka di `70-interior-maps-and-buildings.md`.
- Malam: 22:00 petunjuk "waktunya tidur"; 00:00–01:00 pemain yang masih di luar otomatis "pulang dan tidur" (bangun di kasur 06:00 hari berikut). Tidur memajukan waktu lewat `advanceTime`.
- Uang saku: tersedia hari ke-1 tiap bulan; diterima ketika pemain berdialog dengan ibu (sekali per bulan). Bensin menurun per hari sesuai config.

## 5. Penyimpanan dan migrasi
`gameMinutes` disimpan di save v2; migrasi dari save lama: hitung dari hari+jam yang ada. Jam dihitung ulang dari state, bukan dari timestamp nyata (menutup tab tidak memajukan waktu).

## 6. Uji wajib (tests/self-test.html + E2E)
1. `advanceTime(60)` menambah tepat 60 menit; widget menampilkan nilai identik.
2. Lewat 24:00 → hari +1 dan hari pekan maju; hari 6 = Sabtu, hari 8 = Senin (bila mulai Senin).
3. Lewat hari ke-30 → bulan +1; uang saku bulanan tersedia sekali per bulan.
4. `main_game` 2 jam → jam +120, Kas −20.000, transaksi bertanda waktu benar.
5. Minimarket menolak masuk 23:00; SPBU terbuka 24 jam; kantin tutup Sabtu.
6. Tidur pukul 23:00 → bangun 06:00 hari berikut; hook hari/bulan terpanggil sekali.
7. Simpan/muat mempertahankan menit; migrasi save lama berhasil.
8. Lompat waktu tidak melewatkan `openStateChanged` atau `dayChanged`.
9. Tangkapan layar widget pada keempat fase hari; titik dua berkedip; bar halus.
