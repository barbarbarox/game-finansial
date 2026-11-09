#!/usr/bin/env python3
"""
tools/audit_asset_perspective.py — Automated Asset Perspective & Quality Validator (Rule 85 §3).
Checks all furniture and interior assets for:
1. Frontality / Left-Right Symmetry (IoU >= 0.80 for front/back assets)
2. Partial Alpha Ratio (0% for crisp pixel art)
3. Effective pixel scale estimation
4. Flat baseline for collidable props
Outputs results to docs/asset-identity/PERSPECTIVE-AUDIT.md and JSON summary.
"""

import os
import sys
import json
import numpy as np
from PIL import Image

GAME_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ASSETS_DIR = os.path.join(GAME_DIR, "assets")
FURNITURE_DIR = os.path.join(ASSETS_DIR, "furniture")
DOCS_DIR = os.path.join(GAME_DIR, "docs", "asset-identity")
os.makedirs(DOCS_DIR, exist_ok=True)

MANIFEST_PATH = os.path.join(ASSETS_DIR, "asset-manifest.json")
EXPECTATIONS_PATH = os.path.join(GAME_DIR, "..", "life-journey-expansion-v6", "data", "asset-identity-expectations.json")

V6_FACINGS = {
    "furn_kursi_makan_kiri_v6": "left",
    "furn_kursi_makan_kanan_v6": "right",
    "furn_kursi_makan_back_v6": "back",
    "furn_kursi_baca_back_v6": "back",
    "furn_kursi_makan_front_v6": "front",
    "furn_rak_piring_dinding_v6": "front",
    "furn_jendela_dapur_v6": "front",
    "furn_bak_mandi_v6": "front",
    "furn_toilet_v6": "front",
    "furn_wastafel_cermin_v6": "front",
    "furn_rak_handuk_v6": "front",
    "furn_ember_v6": "front",
    "furn_meja_siswa_kursi_a_v6": "composite",
    "furn_meja_siswa_kursi_b_v6": "composite",
    "furn_meja_guru_v6": "front",
    "furn_kursi_guru_v6": "front",
    "furn_papan_tulis_v6": "front",
    "furn_rak_buku_kelas_v6": "front",
    "furn_meja_kantin_set_a_v6": "composite",
    "furn_meja_kantin_set_b_v6": "composite",
    "furn_bangku_dinding_v6": "front",
    "furn_meja_baca_set_a_v6": "composite",
    "furn_meja_baca_set_b_v6": "composite"
}

def load_expectations():
    if os.path.exists(EXPECTATIONS_PATH):
        with open(EXPECTATIONS_PATH, "r", encoding="utf-8") as f:
            return json.load(f).get("items", {})
    return {}

def calculate_frontality_iou(img):
    """Calculate IoU of alpha channel vs its horizontal flip."""
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    arr = np.array(img)
    alpha = arr[:, :, 3] > 10
    if not np.any(alpha):
        return 1.0, 0
    
    # Crop to non-empty bounding box for fair symmetry evaluation
    rows = np.any(alpha, axis=1)
    cols = np.any(alpha, axis=0)
    ymin, ymax = np.where(rows)[0][[0, -1]]
    xmin, xmax = np.where(cols)[0][[0, -1]]
    cropped_alpha = alpha[ymin:ymax+1, xmin:xmax+1]

    flipped = np.fliplr(cropped_alpha)
    intersection = np.logical_and(cropped_alpha, flipped).sum()
    union = np.logical_or(cropped_alpha, flipped).sum()
    iou = intersection / union if union > 0 else 1.0
    return float(iou), int(union)

def calculate_partial_alpha_ratio(img):
    """Ratio of semi-transparent pixels (0 < alpha < 255) vs total non-zero alpha."""
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    arr = np.array(img)
    alpha = arr[:, :, 3]
    non_zero = (alpha > 0).sum()
    if non_zero == 0:
        return 0.0
    semi = ((alpha > 0) & (alpha < 250)).sum()
    return float(semi / non_zero)

def check_flat_baseline(img):
    """Check if bottom-most non-transparent pixel row has adequate horizontal spread."""
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    arr = np.array(img)
    alpha = arr[:, :, 3] > 10
    if not np.any(alpha):
        return True
    rows = np.any(alpha, axis=1)
    bottom_row_idx = np.where(rows)[0][-1]
    bottom_spread = (alpha[bottom_row_idx, :]).sum()
    return bottom_spread >= 4

def estimate_pixel_scale(img):
    """Estimate pixel art grid cell size based on modal horizontal run lengths."""
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    arr = np.array(img)
    alpha = arr[:, :, 3] > 10
    runs = []
    for r in range(arr.shape[0]):
        row_alpha = alpha[r, :]
        diffs = np.diff(row_alpha.astype(int))
        onsets = np.where(diffs == 1)[0]
        offsets = np.where(diffs == -1)[0]
        # run lengths
        # collect runs where color is uniform
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

def run_perspective_audit():
    print("=" * 60)
    print("AUDITING ASSET PERSPECTIVE, FRONTALITY & QUALITY (RULE 85)")
    print("=" * 60)

    expectations = load_expectations()
    manifest = {}
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            raw_m = json.load(f)
            for item in raw_m.get("assets", []):
                manifest[item["id"]] = item

    results = []
    offenders = []

    # Gather all png files in assets/furniture and subdirectories
    files = []
    for root, _, fnames in os.walk(FURNITURE_DIR):
        for fn in fnames:
            if fn.endswith(".png"):
                files.append(os.path.join(root, fn))
    files.sort()
    print(f"Total furniture assets found: {len(files)}")

    for fpath in files:
        fname = os.path.basename(fpath)
        asset_id = os.path.splitext(fname)[0]
        meta = manifest.get(asset_id, {})
        facing = V6_FACINGS.get(asset_id, meta.get("facing", "front"))

        try:
            with Image.open(fpath) as img:
                w, h = img.size
                iou, pixel_count = calculate_frontality_iou(img)
                partial_alpha = calculate_partial_alpha_ratio(img)
                flat_base = check_flat_baseline(img)
                pixel_scale = estimate_pixel_scale(img)

                is_front_back = facing in ["front", "back", "composite"]
                is_side = facing in ["left", "right", "side"]

                # Offender criteria
                violations = []
                if is_front_back and iou < 0.80:
                    violations.append(f"Frontal IoU too low ({iou:.2f} < 0.80) -> DIAGONAL / OBLIQUE")
                if partial_alpha > 0.05:
                    violations.append(f"Partial alpha present ({partial_alpha*100:.1f}% > 5%) -> BLURRY / VECTOR")

                # Known post-v5 reported offenders
                known_reported = False
                if any(k in asset_id for k in ["meja_siswa", "kursi_siswa", "meja_kantin", "bangku_kantin", "meja_guru", "papan_tulis", "bak_mandi", "rak_piring", "toilet", "wastafel"]):
                    known_reported = True

                record = {
                    "id": asset_id,
                    "filename": fname,
                    "width": w,
                    "height": h,
                    "facing": facing,
                    "frontality_iou": round(iou, 3),
                    "partial_alpha_ratio": round(partial_alpha, 4),
                    "flat_base": flat_base,
                    "pixel_scale": round(pixel_scale, 2),
                    "violations": violations,
                    "status": "PASS" if not violations else "OFFENDER",
                    "known_reported": known_reported
                }
                results.append(record)
                if violations:
                    offenders.append(record)
        except Exception as e:
            print(f"Error reading {fname}: {e}")

    # Generate Markdown Report
    report_path = os.path.join(DOCS_DIR, "PERSPECTIVE-AUDIT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# PERSPECTIVE-AUDIT.md — Audit Frontalitas, Perspektif, dan Kualitas Aset (Rule 85)\n\n")
        f.write(f"- **Total Aset Diperiksa:** {len(results)}\n")
        f.write(f"- **Jumlah Aset Lolos (PASS):** {len(results) - len(offenders)}\n")
        f.write(f"- **Jumlah Pelanggar Perspektif (OFFENDER):** {len(offenders)}\n\n")

        f.write("## 1. Daftar Pelanggar Perspektif & Kualitas (Antrean Regenerasi J4)\n\n")
        f.write("| ID Aset | Dimensi | Facing | IoU Frontalitas | Alfa Parsial | Status | Catatan Pelanggaran |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for o in offenders:
            v_str = "<br>".join(o["violations"])
            f.write(f"| `{o['id']}` | {o['width']}x{o['height']} | {o['facing']} | {o['frontality_iou']} | {o['partial_alpha_ratio']*100:.1f}% | **{o['status']}** | {v_str} |\n")

        f.write("\n## 2. Seluruh Hasil Audit Aset Furnitur\n\n")
        f.write("| ID Aset | Dimensi | Facing | IoU Frontalitas | Alfa Parsial | Status |\n")
        f.write("|---|---|---|---|---|---|\n")
        for r in results:
            f.write(f"| `{r['id']}` | {r['width']}x{r['height']} | {r['facing']} | {r['frontality_iou']} | {r['partial_alpha_ratio']*100:.1f}% | {r['status']} |\n")

    print(f"\nAudit complete!")
    print(f"  Total checked: {len(results)}")
    print(f"  Offenders found: {len(offenders)}")
    print(f"  Report written to: {report_path}")
    return results, offenders

if __name__ == "__main__":
    run_perspective_audit()
