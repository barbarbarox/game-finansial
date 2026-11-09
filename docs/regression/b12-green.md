# Laporan Verifikasi Hijau B12: Bangun Kesiangan Pukul 10:00 Saat Kehabisan Energi (Rule 83 §3)
- **Status:** PASS (Hijau Terverifikasi)
- **Akar Masalah:** Sistem exhaustion sebelumnya hanya mengurangi kecepatan jalan tanpa alur pingsan (blackout), tidak memajukan waktu ke hari berikutnya, dan tidak memindahkan pemain kembali ke tempat tidur.
- **Perbaikan:**
  - Menambahkan metode `_triggerExhaustionSequence()` di `src/game/scenes/World.js`.
  - Menghentikan loop update dan pergerakan pemain selama pingsan (`this._isExhaustionSequenceRunning = true`).
  - Bila pemain sedang menaiki sepeda motor, otomatis di-dismount dan posisi motor diparkirkan secara aman di `town_hub` (tidak masuk ke dalam rumah/kamar).
  - Menampilkan overlay layar hitam blackout dengan teks: `"Kamu kelelahan dan tertidur…"`.
  - Memajukan jam permainan ke hari berikutnya pukul 10:00 pagi (600 menit dari tengah malam).
  - Merelokasi pemain ke kasur di kamar rumah (`home`, spawn target default pada tile kasur $x=5, y=5$).
  - Mereset energi pemain menjadi 50%, mencatat absensi sekolah (`school.attendanceMissed++`), dan menampilkan notifikasi prompt: `"Kamu bangun kesiangan karena kelelahan."`.
- **Langkah UI Nyata:**
  1. Catat hari awal (Hari 1) dan absensi missed (0).
  2. Habiskan energi pemain hingga 0% melalui aktivitas nyata.
  3. Amati sekuens blackout layar hitam `"Kamu kelelahan dan tertidur…"`.
  4. Tunggu transisi sekuens selesai (2.5 detik).
  5. Verifikasi peta saat ini adalah `home`, posisi pemain berada di dekat kasur $(x=5, y=5)$, hari bertambah menjadi Hari 2, waktu tepat pukul 10:00, energi pulih menjadi 50%, dan absensi sekolah tercatat bertambah 1 (`attendanceMissed = 1`).
- **Bukti Pengujian & Tangkapan Layar:**
  - Red: `docs/regression/b12_bangun_kesiangan_red.png`
  - Green: `docs/regression/b12_bangun_kesiangan_green.png`
- **Hasil:** PASS (100% konsisten dengan Rule 83 §3).
