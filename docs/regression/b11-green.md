# Laporan Verifikasi Hijau B11: Notifikasi Peringatan Energi < 50% & Rearm (Rule 83 §2)
- **Status:** PASS (Hijau Terverifikasi)
- **Akar Masalah:** Sebelumnya tidak ada deteksi ambang batas energi $< 50\%$ pada domain energi maupun HUD bar, dan tidak ada teks notifikasi panduan makan.
- **Perbaikan:**
  - Ditambahkan pendeteksi ambang batas $< 50\%$ di `changeEnergy()` dalam `src/domain/energy.js` dengan flag `warnBelowPercent: 50` dan mekanisme rearming `warnRearmAbovePercent: 60`.
  - Mengimplementasikan `_showEnergy50Toast()` di `src/game/scenes/World.js` yang menampilkan toast DOM dan teks prompt dengan kalimat persis:
    `"Energi kamu di bawah 50%, silakan makan untuk menambahnya."`
  - Menambahkan animasi `@keyframes energyPulseWarn` dan selector `.hm-energy-track.pulse-warn` pada `src/ui/tokens.css` untuk memberikan efek visual pulsasi kuning/emas saat ambang batas terlewati.
  - Memperbarui `src/ui/hud.js` dan `tokens.css` dengan indikator terracotta `#C0654A` (`.hm-energy-fill.danger`) saat energi pemain $\le 25\%$.
- **Langkah UI Nyata:**
  1. Turunkan energi pemain dari 52% ke 47% melalui aktivitas normal.
  2. Verifikasi toast muncul di layar dengan kalimat persis: `"Energi kamu di bawah 50%, silakan makan untuk menambahnya."` dan HUD track memicu class `.pulse-warn`.
  3. Naikkan energi pemain ke 70% ($\ge 60\%$) $\to$ verifikasi flag `warn50Triggered` berhasil di-rearm menjadi `false`.
  4. Turunkan kembali energi pemain ke 45% $\to$ verifikasi toast peringatan muncul kembali dengan sukses.
  5. Turunkan energi ke 20% ($\le 25\%$) $\to$ verifikasi warna fill bar HUD berubah menjadi terracotta `#C0654A` (`rgb(192, 101, 74)`).
- **Bukti Pengujian & Tangkapan Layar:**
  - Red: `docs/regression/b11_peringatan_energi_50_red.png`
  - Green: `docs/regression/b11_peringatan_energi_50_green.png`
- **Hasil:** PASS (100% konsisten dengan Rule 83 §2).

