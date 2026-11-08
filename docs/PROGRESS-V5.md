# PROGRESS V5   Tag: pre-v5
- [x] H0 Audit + patch + tes merah   - [x] H1 HUD sync + bar bensin
- [ ] H2 Akses interactable + nakas  - [ ] H3 Ransel + hotbar + aksi item
- [ ] H4 Toko + vendor               - [ ] H5 Klik-untuk-bergerak
- [ ] H6 Regresi + matriks penerimaan + laporan

## Log gerbang (terbaru di atas)
| Tanggal | Gerbang | Hasil | Bukti | Commit |
|---|---|---|---|---|
| 2026-11-09 | H1 | PASS | `tests/hud-sync.html` allPassed, `tools/test_h1_hud_fuel.py`, `docs/regression/a9_gas_bar_green.png` | `feat(v5): h1 hud sync and fuel bar fix` |
| 2026-11-09 | H0 | PASS | `tools/test_h0_red_suite.py`, 6 screenshot merah di `docs/regression/`, `docs/AUDIT-V5.md` | `2328d09` |

Baris matriks non-PASS: A1, A2, A3, A4, A5, A6, A7, A8, A10 dalam proses pengerjaan (H2–H6). PASS: A9, A11.
Temuan terbuka: Alur pembelian tanpa inventory.add, nakas di y=3.5 memblokir kasur.
