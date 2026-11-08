---
trigger: model_decision
description: "Terapkan saat mengimplementasikan penanda/animasi saat misi selesai (efek level-up pada karakter, banner misi, daftar misi), atau efek visual prosedural lain (partikel, cincin, kilau, debu)."
---

# 77 · Penanda Misi Selesai dan Efek Visual Prosedural

## 1. Prinsip
Setiap misi yang selesai **wajib** memberi penanda yang jelas, sekali per misi (idempoten) lewat satu event domain `missionCompleted(id)`. Efek visual prosedural (partikel, cincin, kilau, debu) adalah **kode**, bukan sprite karakter; diizinkan sebagai pengecualian rule 3 AGENTS.md, hanya memakai warna `palette.json`/token.

## 2. Efek "level up" pada karakter (default 1.200 ms)
1. **0–120 ms:** kilat krem pada karakter (tint sementara ≤ 80 ms; identitas warna kembali penuh sesudahnya).
2. **0–900 ms:** dua **cincin** persegi-piksel mengembang dari kaki (mustard → krem), 10–14 **bintang piksel** (4×4 dan 6×6) naik dengan jitter dan memudar.
3. **200–1.200 ms:** teks piksel **"MISI SELESAI!"** + nama misi melayang naik 24 px di atas karakter (isi mustard, outline navy), lalu memudar.
4. Opsional: bunyi singkat jika ada berkas audio di `assets/audio/` (tanpa audio eksternal).

## 3. Banner dan daftar misi (HUD pengguna)
Banner misi aktif menampilkan **centang** + kilau satu kali, teks dicoret sesaat, lalu geser ke misi berikutnya. Riwayat misi (di Buku Kas atau panel misi) menandai misi selesai dengan centang. Mengikuti gaya UI pengguna.

## 4. Aturan teknis
- Antrean efek maks 3; efek ditunda hingga dialog/TimeSkip/transisi selesai.
- Bekerja di peta luar maupun interior; kedalaman di atas semua objek; tidak memblokir input.
- `prefers-reduced-motion`: hanya banner + teks tanpa gerak partikel.
- Efek lain yang memakai prinsip sama: debu naik-turun motor (rule 75), +N Energi (rule 74).

## 5. Uji
Hook `completeMission(id)` memicu efek tepat sekali (panggilan kedua diabaikan); tangkapan layar frame t=100/400/800 ms memakai jam deterministik; antrean dua misi berurutan; mode reduced-motion; efek tidak muncul saat dialog terbuka lalu muncul setelah ditutup.
