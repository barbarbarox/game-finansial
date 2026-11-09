---
trigger: model_decision
description: "Terapkan saat mengimplementasikan atau mengubah motor/kendaraan pemain: tombol kendaraan, naik-turun motor, kecepatan, konsumsi bensin per 5 detik, motor parkir, larangan di interior, atau aset motor dan sprite pengendara."
---

# 75 · Motor Pemain

## 1. Perilaku
- **Tombol kendaraan** (ikon motor) di kelompok tombol HUD kanan-atas (gaya UI pengguna) + pintasan **V**. Tekan → pemain **otomatis menaiki motor** (animasi §3); tekan lagi → turun. Status aktif terlihat (tombol tertekan).
- **Kecepatan:** `speedMultiplier` default 1,8× kecepatan jalan saat ini (baca kecepatan eksisting; jangan di-hardcode).
- **Bensin:** selama mode motor aktif (jam permainan berjalan, tidak sedang dialog/TimeSkip), bensin berkurang **setiap 5 detik nyata** sebesar `fuelPerTick` (default 2%). Penghitung memakai akumulator waktu (bukan `setInterval` bebas) agar uji dapat disimulasikan. Bar bensin eksisting diperbarui halus. SPBU mengisi (+40% per Rp20.000) seperti rancangan sebelumnya. **Gantikan** penurunan bensin harian lama (jika ada) agar tidak ganda; catat di `DECISIONS.md`.
- **Bensin 0%:** pengendara dipaksa turun dengan pesan; tombol kendaraan nonaktif dengan alasan ("Bensin habis, isi di SPBU") hingga bensin > 0. Kejadian E02 (bensin menipis) tetap memicu pada ≤ 20%.
- **Hanya di peta luar (hub).** Memasuki bangunan saat bermotor → **turun otomatis** di depan pintu dan motor diparkir di sana; di dalam bangunan tombol nonaktif dengan alasan.
- **Motor parkir:** setelah turun, sprite motor parkir muncul di samping pemain (kolisi kecil) dan hilang saat dinaiki lagi dari mana pun di hub (tidak perlu berjalan kembali). Posisi parkir disimpan di save.
- Tombol nonaktif saat dialog, TimeSkip, transisi peta, atau energi tidak relevan (energi 0% tidak menghalangi naik motor).

## 2. Kolisi dan kedalaman
Collider kaki pengendara sedikit lebih lebar (default 24×12 px). Lorong hub ≥ 2 tile tetap bisa dilalui. Depth = y dasar motor.

## 3. Animasi naik/turun (efek prosedural, rule 77 §3)
Durasi `mountAnimationMs` (default 350): lompatan kecil −6 px (ease-out/in), ganti sprite di puncak, 4–6 partikel debu persegi piksel (`--cream-300`, `--brown-300`) di roda saat mendarat, dan getar mesin 1 px saat bergerak. Input gerak dikunci selama animasi. `prefers-reduced-motion` → ganti sprite langsung tanpa lompatan.

## 4. Aset (generate AI, `data/asset-briefs-v4.json`)
- **Jangkar motor** `vehicle_motor_ref`: motor matic sederhana tanpa merek (warna dari palet: navy dan krem), tiga tampak: depan, belakang, samping kiri. Disetujui di Checkpoint C.
- **Sprite pengendara** `vehicle_rider_m` dan `vehicle_rider_f`: pemain duduk di motor yang **sama**, tiga tampak (depan, belakang, samping kiri; kanan = cermin kiri), pakaian dan tas sesuai kanon. Frame seragam 80×64 (samping 80 lebar; depan/belakang ±40 lebar, diratakan tengah-bawah), anchor (0.5, 1).
- `prop_motor_parkir` (tampak samping/depan) dari jangkar yang sama; `icon_motor` 32×32 untuk tombol.
- QA tambahan: warna motor konsisten di semua tampak dan antar-sheet; identitas pengendara cocok dengan sprite karakter.

## 5. Uji wajib
Toggle on/off via tombol dan V; kecepatan terukur ≥ 1,6× jalan (hook `measureSpeed`); bensin turun tepat tiap 5 detik simulasi (akumulator diuji dengan jam palsu, bukan menunggu nyata); bensin 0% memaksa turun dan menonaktifkan tombol; masuk bangunan memicu turun otomatis dan motor terparkir; isi bensin lalu naik lagi; save/load mempertahankan bensin dan posisi motor parkir; tangkapan layar frame animasi pada t=0/120/240/350 ms; tidak ada tembus kolisi saat bermotor (probe rule 73).

## 6. Pembaruan v6: motor parkir terikat peta
Posisi motor parkir menyimpan `mapId` dan **hanya dirender/berkolisi di peta itu**. Saat masuk gedung dalam keadaan bermotor, pemain turun otomatis dan motor diparkir di **peta hub di depan pintu bangunan tersebut**, bukan di interior. Bug yang dilaporkan: sprite motor muncul di ruang kelas. Uji (UI nyata): bermotor → masuk sekolah → ruang kelas tidak memuat motor; keluar → motor ada di depan pintu sekolah; simpan/muat mempertahankan `mapId` parkir.
