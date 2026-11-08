# PROGRESS V4
Tag pra-v4: pre-v4 | Kapabilitas gambar: `image-generator` subagent (Gemini Image API) aktif

- [x] G0 Audit + patch + preflight
- [x] G1 Kolisi + NPC/oklusi + efek misi
- [ ] G2 Energi + hotbar + item
- [ ] G3 Motor pemain
- [ ] G4 Tata letak slot 7 peta
- [ ] G5 Aset batch 1 → [ ] CHECKPOINT C disetujui
- [ ] G6 Aset sisanya (+ game center eksterior ulang)
- [ ] G7 Terrain plate → [ ] CHECKPOINT D disetujui
- [ ] G8 Integrasi + QA multi-hari + laporan

## Log gerbang (terbaru di atas)
| Tanggal | Gerbang | Hasil | Bukti (file/tangkapan layar/log) | Commit |
|---|---|---|---|---|
| 2026-11-08 | G1 Kolisi + NPC/oklusi + efek misi | LULUS | collisionProbe 100% hijau di 7 peta; map-check.html lulus 36/36 (termasuk oklusi & isolasi NPC); Ibu terhapus dari hub (listNPCs=['npc_teman', 'npc_pak_anto']); completeMission idempoten; 3 tangkapan layar di docs/g1-quickfixes/; tools/test_g1_quickfixes.py 100% hijau | HEAD |
| 2026-11-08 | G0 Audit, patch, preflight | LULUS | docs/AUDIT-V4.md disusun lengkap (7 peta, kolisi, NPC Ibu di hub, layout dapur/WC, game center, bensin, item); EXPANSION-PATCH-V4 diterapkan ke AGENTS.md dan rules; config additions digabung ke phase1.config.json; items.phase1.json siap; tag pre-v4 dibuat | 14a78e2 |

## Aset placeholder tersisa
- Seluruh aset ekspansi v4 belum digenerate; siap dimulai dari G0.

## Temuan terbuka
- Mengawali fase G0 sesuai instruksi AUTOPILOT-V4.md.
