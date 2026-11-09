---
trigger: model_decision
description: "Terapkan saat membuat atau mengubah tutorial/alur cerita awal permainan (misi wajib pertama kali), panah petunjuk, teks panduan, highlight tombol HUD, petunjuk tombol interaksi, penguncian lunak bangunan selama tutorial, penyimpanan/lanjut tutorial, dan data tutorial."
---

# 82 · Tutorial Berpemandu dan Cerita Hari Pertama

## 1. Tujuan
Pada **permainan baru pertama kali**, pemain menjalani rangkaian misi **wajib** berpemandu (panah + teks panduan) yang mengajarkan semua sistem dan mengunjungi **semua bangunan** dalam satu hari bercerita: **"Hari Pertama Bulan Baru"**. Setelah selesai, tutorial tidak muncul lagi (kecuali "Ulangi tutorial" di Settings) dan permainan bebas dimulai. Data langkah: `data/tutorial.phase1.json` (diselaraskan dengan id objek/NPC/peta yang benar-benar ada; catat pemetaan di `docs/DECISIONS.md`).

## 2. Cerita (ringkas; dialog ditulis agen dalam Bahasa Indonesia santai, edukatif, ≤ 140 karakter per kotak)
Hari pertama bulan baru, Senin. Ibu menyerahkan uang saku sebulan Rp1.000.000 dan berpesan: "Cukup-cukupkan untuk satu bulan." Pemain belajar menyusun anggaran, menabung, membedakan kebutuhan dan keinginan, mengelola energi, belanja, bermotor dan mengisi bensin, lalu pulang dan tidur. Penutup: ringkasan keuangan hari itu + tujuan bulan ini. Setiap bangunan punya satu adegan singkat berpotret (vendor/teman) yang mengaitkan pelajaran literasi keuangan.

## 3. Rantai langkah wajib (urut; rinci di data)
**Rumah:** T01 bergerak (WASD atau klik lantai) → T02 temui Ibu → T03 terima uang saku → T04 sarapan di dapur (energi naik) → T05 susun anggaran (tombol Anggaran, "Gunakan saran") → T06 menabung ≥ Rp100.000 di celengan → T07 keluar rumah.
**Sekolah:** T08 pergi ke sekolah → T09 masuk kelas, Sesi 1 → T10 istirahat: belanja di kantin (beli 1 item) → T11 pakai item dari hotbar (klik item → Gunakan) → T12 Sesi 2 → T13 perpustakaan (baca 1 jam).
**Kota:** T14 minimarket (beli item + buka ransel) → T15 toko kosmetik (beli 1 barang; materi kebutuhan vs keinginan) → T16 naik motor (tombol Motor/V) ke SPBU → T17 isi bensin → T18 game center (main 1 jam; energi turun) → T19 *(kondisional)* bila energi < 50%: makan item untuk menambah energi.
**Penutup:** T20 pulang dan tidur → hari berikutnya; layar ringkasan; `tutorialCompleted = true`.
Pemetaan ke misi lama: M1 ← T03, M2 ← T05, M3 ← T17, M4 ← T06, M5 ← T18 (ajakan teman/hiburan) agar tidak ganda.

## 4. Sistem petunjuk
1. **Panel objektif** (perluas banner misi buatan pengguna): "LANGKAH n/N · judul" + 1–2 baris instruksi + titik progres. Dapat diciutkan.
2. **Panah pemandu:** (a) panah piksel melayang di atas target (NPC/objek/pintu); (b) bila target di luar layar/peta lain, panah di tepi layar menunjuk **arah belokan berikutnya** dari jalur A* (rule 81) atau ke pintu yang mengarah ke peta target (graf peta); (c) opsional jejak titik-titik di sepanjang jalur (toggle di Settings).
3. **Petunjuk tombol kontekstual:** gelembung ikon tombol di atas target saat dalam jangkauan ("E · Bicara" / "Klik · Bicara" pada perangkat sentuh), sesuai rule 84.
4. **Highlight elemen HUD:** bingkai berdenyut + keterangan pada Anggaran, Buku Kas, hotbar ("Klik item untuk menggunakannya"), tombol ransel, tombol Motor, bar energi/bensin pada langkah terkait. Efek prosedural (rule 77).
5. **Teks panduan input:** WASD/panah dan klik untuk bergerak; E atau klik karakter/objek untuk berinteraksi; klik item untuk opsi; 1–5 pakai cepat; B ransel; V motor.
6. **Pengunci lunak:** pintu bangunan di luar babak aktif menampilkan "Selesaikan langkah dulu"; tidak ada keadaan buntu (selalu ada cara menyelesaikan langkah: saldo cukup, item tersedia, jam buka). Tombol **Bantuan** di panel: "Tunjukkan arah" dan, **hanya setelah 3 menit tanpa kemajuan**, "Lewati langkah ini" (anti-macet).

## 5. Aturan waktu dan sistem lain selama tutorial
- `tutorial.realtimeClock: "paused"`: jam real-time dihentikan; waktu hanya maju oleh aktivitas (`advanceTime`), agar jam buka tidak terlewat karena berjalan. Menunggu bel (mis. kelas mulai 07:00) dilakukan otomatis dengan memajukan waktu.
- Kejadian acak (`events`) dinonaktifkan; energi, bensin, ledger tetap berjalan. Bensin awal permainan baru `newGame.fuelPercent = 60` agar T17 mungkin.
- Urutan jam harus feasible: tes E2E menghitung bahwa semua langkah selesai dalam jendela jam buka (sekolah 06:30–15:30, kantin sampai 14:30, minimarket 07–22, kosmetik 09–20, game center 10–23, SPBU 24 jam). Sesi kelas dipecah: **Sesi 1 07:00–10:00, istirahat 10:00–10:30 (kantin), Sesi 2 10:30–14:30**.

## 6. Penyimpanan
Save: `tutorial {active, stepIndex, completedSteps[], completed}`; melanjutkan setelah muat ulang di langkah terakhir. Save lama (sebelum v6) → `completed: true`. "Permainan baru" → tutorial aktif. "Ulangi tutorial" hanya pada permainan baru (tidak merusak save).

## 7. Keamanan dan kualitas
Data tutorial divalidasi skema (id target ada, tipe kondisi di whitelist); teks lewat `textContent`; kondisi selesai hanya dari **event domain** (`purchaseCompleted`, `itemUsed`, `activityCompleted`, `mapChanged`, dst.), bukan dari klik UI semata. Aksesibilitas: panel dapat diakses keyboard, kontras ≥ 4.5:1, reduced-motion → panah statis.

## 8. Uji wajib (UI nyata, rule 78)
Satu E2E penuh dari Permainan Baru sampai T20 dengan pointer/keyboard nyata, tangkapan layar tiap langkah (panah, panel objektif, highlight), pemeriksaan jam buka di tiap langkah; muat ulang di tengah tutorial lalu lanjut; pintu terkunci lunak berfungsi; "Lewati langkah" tidak muncul sebelum 3 menit; setelah T20 tutorial tidak muncul lagi pada hari berikutnya; save lama tidak memunculkan tutorial.
