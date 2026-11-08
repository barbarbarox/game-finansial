# PROGRESS V4
Tag pra-v4: pre-v4 | Kapabilitas gambar: `image-generator` subagent (Gemini Image API) aktif

- [x] G0 Audit + patch + preflight
- [x] G1 Kolisi + NPC/oklusi + efek misi
- [x] G2 Energi + hotbar + item
- [x] G3 Motor pemain
- [x] G4 Tata letak slot 7 peta
- [x] G5 Aset batch 1 → [x] CHECKPOINT C disetujui (disetujui oleh pengguna dengan catatan padding kamera telah diperbaiki)
- [x] G6 Aset sisanya (+ game center eksterior ulang)
- [x] G7 Terrain plate → [ ] CHECKPOINT D disetujui (Siap Review Manusia)
- [ ] G8 Integrasi + QA multi-hari + laporan

## Log gerbang (terbaru di atas)
| Tanggal | Gerbang | Hasil | Bukti (file/tangkapan layar/log) | Commit |
|---|---|---|---|---|
| 2026-11-08 | G7 Terrain plate (Checkpoint D) | LULUS (Siap Review) | Terrain plate town_hub sintetis AI (1280x768) terpasang di assets/terrain/terrain_plate_hub.png; Uji kesesuaian IoU Rule 76 100% LULUS (jalan: 0.8812, trotoar: 0.8763, halaman: 0.9867, rumput: 0.9740 seluruhnya >= 0.85); fallback aman ke procedural ground di mapManager.js; tests/terrain-check.html dibuat; 8 tangkapan layar di docs/checkpoint-D/ (persimpangan 4 arah, pintu rumah, sekolah, minimarket/kosmetik, SPBU, game center baru, tampilan bermotor, perbandingan sebelum/sesudah) | 6b5fd16 |
| 2026-11-08 | G6 Aset sisanya (+ Game Center baru) | LULUS | Game Center eksterior baru (flat baseline, orthogonal, AI Gemini) dipasang di assets/buildings/bld_game_center.png; Spritesheet pengendara motor pria & wanita (3 arah: down, up, left/right) dipasang di assets/characters/char_rider_m.png & char_rider_f.png; Player.js terintegrasi render pengendara motor; Padding batas kamera interior (padX=256, padY=160) menyelesaikan keluhan pengguna kamar tertutup HUD; 68 aset furnitur sekolah/minimarket/kosmetik/spbu/game center didaftarkan ready di manifest dan dimuat di Preload.js; 5 contact sheets di docs/g6-assets/ | 5b2d6db |
| 2026-11-08 | G5 Aset batch 1 (Checkpoint C) | LULUS (Disetujui Pengguna) | 16 item AI pixel art transparan di assets/items/; vehicle_motor_ref (3 sudut: depan, belakang, samping) dihasilkan via image-generator AI; prop_motor_parkir & icon_motor diperbarui; 6 bukti render Checkpoint C di docs/checkpoint-C/; pintu lorong dapur transparan dengan kusen & plakat lantai; baris counter dapur sejajar sempurna | 87bc6dc |
| 2026-11-08 | G4 Tata letak slot 7 peta | LULUS | Tata letak berbasis slot 7 peta memenuhi 9 kriteria Rule 73 (a–i) 100% lulus; perbaikan total rumah: lorong terbuka 3-tile x=14 y=13..15 dengan kusen tiang kayu, ambang lantai parket bergaris kuningan, dan plakat lantai; perataan baris counter dapur (kulkas + kompor + wastafel baseline rata); ruang tamu bebas rintangan dari kamar ke pintu depan dan ke dapur; 16 item makanan/minuman hasil AI pixel art dislice transparan 32x32 di assets/items/; Preload.js memuat lengkap seluruh furnitur & item; 7 diagram layout visual & kolisi di docs/g4-layouts/; 7 laporan validasi docs/layouts/VALIDATION-*.md | 3a8448c |
| 2026-11-08 | G3 Motor pemain | LULUS | Kecepatan 1.8x (172.8 px/s vs 96 px/s); toggle V & tombol HUD responsif; bensin turun 2% per 5 detik bergerak (100 -> 98 -> 96); bensin 0% auto-dismount & cegah naik; larangan interior & turun di pintu minimarket (motor parkir x=208, y=592); save v3 persistensi bensin & motor parkir; collisionProbe 27/27 kokoh (100% lulus); 4 tangkapan layar animasi naik motor di docs/g3-vehicle/ (t=0, 120, 240, 350 ms); tools/test_g3_vehicle.py 100% hijau | 100b35e |
| 2026-11-08 | G2 Energi + hotbar + item | LULUS | Domain energi 0-100, penguras pasif 2/jam, aktivitas drain tepat (belajar 1 jam -> -12), makan rumah +40, pembelian minimarket masuk tas, kantin makan di tempat / bungkus, penolakan saat tas penuh (tanpa potong kas), kelelahan 0% melambatkan jalan 0.7x & tolak aktivitas berat, hotbar tombol 1-5 & klik, save v3 diuji persistensi, tangkapan layar desktop & tablet di docs/g2-energy-hotbar/, tools/test_g2_energy_hotbar.py 100% hijau | 132039d |
| 2026-11-08 | G1 Kolisi + NPC/oklusi + efek misi | LULUS | collisionProbe 100% hijau di 7 peta; map-check.html lulus 36/36 (termasuk oklusi & isolasi NPC); Ibu terhapus dari hub (listNPCs=['npc_teman', 'npc_pak_anto']); completeMission idempoten; 3 tangkapan layar di docs/g1-quickfixes/; tools/test_g1_quickfixes.py 100% hijau | 5935571 |
| 2026-11-08 | G0 Audit, patch, preflight | LULUS | docs/AUDIT-V4.md disusun lengkap (7 peta, kolisi, NPC Ibu di hub, layout dapur/WC, game center, bensin, item); EXPANSION-PATCH-V4 diterapkan ke AGENTS.md dan rules; config additions digabung ke phase1.config.json; items.phase1.json siap; tag pre-v4 dibuat | 14a78e2 |

## Aset placeholder tersisa
- Seluruh aset ekspansi v4 belum digenerate; siap dimulai dari G0.

## Temuan terbuka
- Mengawali fase G0 sesuai instruksi AUTOPILOT-V4.md.
