# PROGRESS V5   Tag: pre-v5
- [x] H0 Audit + patch + tes merah   - [x] H1 HUD sync + bar bensin
- [x] H2 Akses interactable + nakas  - [ ] H3 Ransel + hotbar + aksi item
- [ ] H4 Toko + vendor               - [ ] H5 Klik-untuk-bergerak
- [ ] H6 Regresi + matriks penerimaan + laporan

## Log gerbang (terbaru di atas)
| Tanggal | Gerbang | Hasil | Bukti | Commit |
|---|---|---|---|---|
| 2026-11-09 | H2 | PASS | `tests/layout-check.html` 70/70 LULUS (ApproachCheck 7/7 peta), `tools/test_h2_nakas_access.py`, `docs/regression/a8_nakas_unblocked_green.png` | `feat(v5): h2 unblock bed access and validate all interactables` |
| 2026-11-09 | H1 | PASS | `tests/hud-sync.html` allPassed, `tools/test_h1_hud_fuel.py`, `docs/regression/a9_gas_bar_green.png` | `4426036` |
| 2026-11-09 | H0 | PASS | `tools/test_h0_red_suite.py`, 6 screenshot merah di `docs/regression/`, `docs/AUDIT-V5.md` | `2328d09` |

Baris matriks non-PASS: A1, A2, A3, A4, A5, A6, A7, A10 dalam proses pengerjaan (H3–H6). PASS: A8, A9, A11.
Temuan terbuka: Alur pembelian tanpa inventory.add, sistem ransel dan popup aksi item.
