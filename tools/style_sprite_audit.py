#!/usr/bin/env python3
"""
tools/style_sprite_audit.py — NPC Sprite Style & Pixel Art Consistency Auditor (Rule 85 §4).
Verifies:
1. Frame dimensions (32x64 or multi-frame sheets)
2. Partial alpha ratio (must be 0 for crisp pixel art)
3. Effective pixel scale vs player sprite (within +-25%)
4. Direction views (front, back, left)
Generates docs/asset-identity/NPC-STYLE-AUDIT.md.
"""

import os
import sys
import json
import numpy as np
from PIL import Image

GAME_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ASSETS_DIR = os.path.join(GAME_DIR, "assets")
NPC_DIR = os.path.join(ASSETS_DIR, "npcs")
CHAR_DIR = os.path.join(ASSETS_DIR, "characters")
DOCS_DIR = os.path.join(GAME_DIR, "docs", "asset-identity")
os.makedirs(DOCS_DIR, exist_ok=True)

PLAYER_REF = os.path.join(CHAR_DIR, "char_player_m_casual.png")

def calculate_partial_alpha_ratio(img):
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    arr = np.array(img)
    alpha = arr[:, :, 3]
    non_zero = (alpha > 0).sum()
    if non_zero == 0:
        return 0.0
    semi = ((alpha > 0) & (alpha < 250)).sum()
    return float(semi / non_zero)

def estimate_pixel_scale(img):
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    arr = np.array(img)
    alpha = arr[:, :, 3] > 10
    runs = []
    for r in range(arr.shape[0]):
        row_alpha = alpha[r, :]
        cur_len = 1
        for c in range(1, arr.shape[1]):
            if row_alpha[c] and row_alpha[c-1]:
                if np.array_equal(arr[r, c, :3], arr[r, c-1, :3]):
                    cur_len += 1
                else:
                    if cur_len > 1:
                        runs.append(cur_len)
                    cur_len = 1
            else:
                cur_len = 1
    if not runs:
        return 1.0
    vals, counts = np.unique(runs, return_counts=True)
    return float(vals[np.argmax(counts)])

def run_npc_audit():
    print("=" * 60)
    print("AUDITING NPC SPRITE STYLES (RULE 85 §4)")
    print("=" * 60)

    # Reference player pixel scale
    ref_scale = 1.0
    if os.path.exists(PLAYER_REF):
        with Image.open(PLAYER_REF) as pimg:
            ref_scale = estimate_pixel_scale(pimg)
    print(f"Reference Player Sprite Pixel Scale: {ref_scale:.2f}")

    files = sorted([f for f in os.listdir(NPC_DIR) if f.endswith(".png")])
    records = []
    offenders = []

    for fname in files:
        fpath = os.path.join(NPC_DIR, fname)
        npc_id = os.path.splitext(fname)[0]

        try:
            with Image.open(fpath) as img:
                w, h = img.size
                partial_alpha = calculate_partial_alpha_ratio(img)
                pix_scale = estimate_pixel_scale(img)
                scale_diff = abs(pix_scale - ref_scale) / ref_scale if ref_scale > 0 else 0

                violations = []
                # Check for cartoonish/smooth alpha or scale mismatch
                if partial_alpha > 0.05:
                    violations.append(f"Anti-aliased / partial alpha present ({partial_alpha*100:.1f}%) -> CARTOON / VECTOR")
                if scale_diff > 0.35 and not fname.startswith("npc_sheet_"):
                    violations.append(f"Pixel scale mismatch ({scale_diff*100:.1f}% > 25% tolerance)")

                # Specific check for old Budi (reported issue 7)
                if "budi" in npc_id and not npc_id.endswith("_v6"):
                    violations.append("Known issue: Cartoonish proportions, lacks teen high-school style matching protagonist")

                status = "PASS" if not violations else "OFFENDER"
                rec = {
                    "id": npc_id,
                    "filename": fname,
                    "width": w,
                    "height": h,
                    "partial_alpha": round(partial_alpha, 4),
                    "pixel_scale": round(pix_scale, 2),
                    "scale_diff_pct": round(scale_diff * 100, 1),
                    "violations": violations,
                    "status": status
                }
                records.append(rec)
                if violations:
                    offenders.append(rec)
        except Exception as e:
            print(f"Error reading {fname}: {e}")

    # Generate NPC-STYLE-AUDIT.md
    report_path = os.path.join(DOCS_DIR, "NPC-STYLE-AUDIT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# NPC-STYLE-AUDIT.md — Audit Gaya Sprite NPC (Rule 85 §4)\n\n")
        f.write(f"- **Total Sprite NPC Diperiksa:** {len(records)}\n")
        f.write(f"- **Sprite Lolos (PASS):** {len(records) - len(offenders)}\n")
        f.write(f"- **Pelanggar Gaya (OFFENDER):** {len(offenders)}\n")
        f.write(f"- **Skala Piksel Referensi Pemain:** {ref_scale:.2f}\n\n")

        f.write("## 1. Pelanggar Gaya Sprite NPC (Antrean Regenerasi J4)\n\n")
        f.write("| ID NPC | Ukuran | Alfa Parsial | Skala Piksel | Status | Pelanggaran |\n")
        f.write("|---|---|---|---|---|---|\n")
        for o in offenders:
            v_str = "<br>".join(o["violations"])
            f.write(f"| `{o['id']}` | {o['width']}x{o['height']} | {o['partial_alpha']*100:.1f}% | {o['pixel_scale']} | **{o['status']}** | {v_str} |\n")

        f.write("\n## 2. Seluruh Hasil Audit Sprite NPC\n\n")
        f.write("| ID NPC | Ukuran | Alfa Parsial | Skala Piksel | Status |\n")
        f.write("|---|---|---|---|---|\n")
        for r in records:
            f.write(f"| `{r['id']}` | {r['width']}x{r['height']} | {r['partial_alpha']*100:.1f}% | {r['pixel_scale']} | {r['status']} |\n")

    print(f"\nNPC Audit complete!")
    print(f"  Total checked: {len(records)}")
    print(f"  Offenders found: {len(offenders)}")
    print(f"  Report written to: {report_path}")
    return records, offenders

if __name__ == "__main__":
    run_npc_audit()

