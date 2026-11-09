---
trigger: model_decision
description: "Terapkan saat mengubah sistem energi: pengurasan per aktivitas (pelajaran 20%, game center 20%), peringatan energi di bawah 50%, pingsan/tidur otomatis dan bangun kesiangan saat energi habis, tabel biaya energi realistis."
---

# 83 · Energi v2 (menggantikan §1 rule 74)

## 1. Biaya energi (default di `data/v6.config.additions.json`; semua dapat disetel)
| Aktivitas | Biaya energi | Catatan |
|---|---|---|
| ikut_pelajaran (satu hari penuh) | **−20%** total | dibagi proporsional: Sesi 1 (3 jam) ≈ −9%, Sesi 2 (4 jam) ≈ −11% |
| main_game (game center) | **−20% per jam** | opsi durasi 1–2 jam |
| belajar_mandiri | −8%/jam | |
| baca_perpustakaan | −3%/jam | |
| nongkrong_kafe | −4%/jam | |
| nonton_mini (bioskop mini) | −2%/jam | |
| nonton_tv | −1%/jam | |
| mandi | −1% | tetap |
| berjalan | −0,03% per detik bergerak | bermotor 0 |
| pasif saat terjaga | −1,5%/jam | lewat `advanceTime` |
| tidur | +10%/jam | istirahat +5%/jam |
Pengisi: makan di dapur ibu (+40), item (rule 74/79), tidur. Biaya aktivitas dihitung per menit simulasi lewat `advanceTime` (tanpa pembulatan yang membuat total menyimpang; uji: 7,5 jam kelas = tepat −20%).

## 2. Peringatan
- **Di bawah 50%:** tampilkan banner/toast teks **persis**: "Energi kamu di bawah 50%, silakan makan untuk menambahnya." Muncul sekali saat melewati ambang; diaktifkan kembali setelah energi ≥ 60%. Bar energi berdenyut singkat.
- **≤ 25%:** bar berwarna terracotta + pesan "Energi kamu hampir habis!" sekali; **≤ 10%:** kecepatan jalan ×0,85.
- Aktivitas yang diproyeksikan menurunkan energi di bawah 10% menampilkan konfirmasi "Energi tidak cukup, kamu bisa pingsan. Lanjutkan?".

## 3. Energi habis (0%) → bangun kesiangan
Urutan: layar memudar + teks "Kamu kelelahan dan tertidur…" → pemain **bangun di kasurnya di rumah pada hari berikutnya pukul `exhaustedWakeHour` (default 10:00, "kesiangan")** dengan energi `exhaustedWakeEnergy` (default 50%) → waktu dimajukan lewat `advanceTime` (hook hari/bulan, jam buka, uang saku bulanan tetap terpicu) → pesan "Kamu bangun kesiangan karena kelelahan." Konsekuensi: sesi sekolah pagi terlewat (`attendanceMissed++`, tercatat di evaluasi, tanpa efek uang). Bila pemain bermotor: turun otomatis, motor diparkir di hub dekat rumah. Tidak ada game over. Tidur normal (energi > 0) bangun 06:00.

## 4. Tutorial dan energi
Tutorial (rule 82) memakai tabel ini; langkah T19 (makan saat < 50%) dipicu oleh peringatan di atas.

## 5. Uji wajib (UI nyata)
Kelas penuh turun tepat 20% (± toleransi pembulatan 0,5%); satu jam game center turun 20%; tiap baris tabel diverifikasi via `advanceTime` simulasi; peringatan < 50% muncul sekali, teks persis, aktif lagi setelah ≥ 60%; energi 0 → pingsan → bangun hari berikutnya 10:00 di kasur, energi 50%, `attendanceMissed` bertambah, hook hari terpicu sekali; bermotor saat 0% → motor terparkir; simpan/muat; tangkapan layar peringatan dan layar bangun kesiangan.
