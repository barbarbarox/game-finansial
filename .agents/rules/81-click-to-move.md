---
trigger: model_decision
description: "Terapkan saat mengimplementasikan atau mengubah gerak pemain dengan klik/ketuk titik tujuan (point-and-click), pathfinding, penanda tujuan, auto-interaksi saat tiba, atau pembatalan gerak oleh input lain."
---

# 81 · Gerak dengan Klik/Ketuk (selain WASD/panah)

## 1. Perilaku
- **Klik/ketuk titik di dunia** → pemain berjalan ke sana lewat **jalur yang menghindari kolisi** (pathfinding), di hub maupun interior, dengan kecepatan berjalan atau motor yang berlaku. WASD/panah tetap bekerja.
- **Klik pada interactable/NPC/pintu/rak** → berjalan ke titik pendekatan yang bebas kolisi di dalam jarak interaksi, lalu **otomatis berinteraksi** (setara tekan E) saat tiba (`clickToMove.autoInteract`, default aktif).
- Klik titik tak terjangkau → ambil titik terjangkau terdekat dalam radius `maxSnapRadiusTiles` (default 3); bila tidak ada, penanda bergetar singkat dan balon "Tidak bisa ke sana".
- **Penanda tujuan** prosedural (cincin/X piksel, rule 77) berdenyut di titik tujuan, hilang saat tiba/batal; `prefers-reduced-motion` → statis.
- Arah hadap mengikuti sumbu dominan gerak. Gerak ke arah klik tidak boleh menembus kolisi (kolisi tetap ditegakkan oleh fisika).

## 2. Pembatalan dan pengabaian input
Dibatalkan oleh: tombol gerak (WASD/panah), Esc, dialog/panel/TimeSkip/transisi peta, klik baru (menggantikan tujuan), deteksi macet (tidak maju ≥ `stuckTimeoutMs`, default 1.500 ms). **Diabaikan:** klik/ketuk yang mengenai elemen UI DOM (HUD, hotbar, panel, popup), serta saat dialog/panel terbuka. Opsional: tahan tombol mouse/jari untuk terus memperbarui tujuan (default nonaktif).

## 3. Navigasi
Bangun **grid navigasi** per peta (sel 8 px) dari collider dan dinding, dengan kolisi **digembungkan** sebesar setengah collider kaki pemain (lebih lebar saat bermotor agar lorong ≥ 2 tile tetap lolos). A* 8-arah dengan pemangkasan sudut (tidak memotong sudut collider) + penghalusan jalur. Cache grid; bangun ulang saat peta berganti atau collider dinamis berubah (motor parkir). NPC dianggap rintangan dinamis kecil; jalur dihitung ulang bila terhalang. Waktu hitung target < 5 ms pada peta terbesar. Konversi layar→dunia memperhitungkan kamera, skala FIT, dan padding kamera interior.

## 4. Input dan layar sentuh
Pointer events (mouse + sentuh) pada canvas; `touch-action: none` pada canvas; hindari bentrok zoom ganda-ketuk; area klik tidak melewati overlay DOM. Bekerja pada desktop dan tablet.

## 5. Parameter (`data/v5.config.additions.json` → `clickToMove`)
`enabled`, `autoInteract`, `stopDistancePx` (4), `stuckTimeoutMs` (1500), `maxSnapRadiusTiles` (3), `markerMs`, `holdToMove` (false).

## 6. Uji wajib (pointer events NYATA, rule 78)
Klik titik jauh di hub → tiba (toleransi ≤ stopDistance) lewat jalur memutar rintangan; klik di balik dinding → jalur memutar/ditolak; klik kasur di kamar pemain → berjalan lalu dialog/aksi tidur terbuka (juga membuktikan akses ke kasur); klik NPC → berjalan lalu dialog; klik pintu → pindah peta; WASD saat berjalan → batal; klik tombol HUD → pemain tidak bergerak; dialog terbuka → klik dunia diabaikan; target tak terjangkau → snap/balon; bermotor → lebih cepat dan tetap menghormati kolisi; perhitungan jalur < 5 ms; tangkapan layar penanda dan jalur (overlay debug). Tidak ada tembus kolisi (probe rule 73 tetap hijau).
