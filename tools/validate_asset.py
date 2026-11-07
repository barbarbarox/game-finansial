#!/usr/bin/env python3
"""
validate_asset.py — Cek teknis Rule 60 bagian 4 diperkuat:
(a) Dasar sprite menyentuh baris terbawah (bangunan/prop/karakter)
(b) Bounding box mengisi >= 90% lebar gambar (untuk bangunan/prop; untuk karakter >= 50%)
(c) Tidak ada komponen terhubung kecil (< 12 piksel) yang terpisah dari subjek utama
(d) Tidak ada piksel buram pada kolom/baris tepi (alpha strictly 0 atau 255)
(e) Dimensi kelipatan 32 untuk bangunan/prop
(f) Palet <= 32 warna unik, tanpa sisa magenta
"""

import sys
import json
import numpy as np
from PIL import Image
import scipy.ndimage as ndimage

def validate(image_path, brief=None):
    if brief is None:
        brief = {}

    img = Image.open(image_path).convert('RGBA')
    arr = np.array(img)
    w, h = img.size
    alpha = arr[:, :, 3]

    report = {
        "pass": True,
        "failures": [],
        "warnings": [],
        "details": {
            "dimensions": f"{w}x{h}",
            "kind": brief.get("kind", "unknown")
        }
    }

    # 1. Dimensi kelipatan 32 (jika bangunan atau prop)
    kind = brief.get('kind', '')
    is_building = kind in ['building', 'prop'] or 'bld_' in image_path or 'prop_' in image_path
    if is_building:
        if w % 32 != 0:
            report["failures"].append(f"Lebar bukan kelipatan 32: {w}")
        if h % 32 != 0:
            report["failures"].append(f"Tinggi bukan kelipatan 32: {h}")

    # Cek kecocokan dimensi dengan brief (jika ada)
    expected_w = brief.get('width')
    expected_h = brief.get('height')
    if expected_w and w != expected_w:
        report["failures"].append(f"Lebar tidak cocok brief: {w} != {expected_w}")
    if expected_h and h != expected_h:
        report["warnings"].append(f"Tinggi berbeda dari brief: {h} != {expected_h} (disesuaikan untuk proporsi)")

    # 2. Alpha check (harus strictly 0 atau 255)
    invalid_alpha = int(np.sum((alpha > 0) & (alpha < 255)))
    report["details"]["semiTransparentPixels"] = invalid_alpha
    if invalid_alpha > 0:
        report["failures"].append(f"Alpha tidak biner: {invalid_alpha} piksel semi-transparan terdeteksi.")

    # 3. (a) Dasar sprite menyentuh baris terbawah
    bottom_row_visible = int(np.sum(alpha[-1, :] == 255))
    report["details"]["bottomRowVisiblePixels"] = bottom_row_visible
    if bottom_row_visible == 0:
        report["failures"].append("Dasar sprite TIDAK menyentuh baris terbawah (baris terbawah kosong).")

    # 4. (b) Bounding box lebar
    bbox = img.getbbox()
    if not bbox:
        report["failures"].append("Gambar sepenuhnya kosong/transparan.")
        report["pass"] = False
        return report

    bbox_w = bbox[2] - bbox[0]
    bbox_h = bbox[3] - bbox[1]
    w_ratio = round(bbox_w / float(w), 3)
    report["details"]["bboxWidthRatio"] = w_ratio
    report["details"]["bboxDimensions"] = f"{bbox_w}x{bbox_h}"

    min_w_ratio = 0.90 if is_building else 0.50
    if w_ratio < min_w_ratio:
        report["failures"].append(f"Bounding box tidak mengisi lebar yang cukup: {w_ratio:.1%} (minimal {min_w_ratio:.0%})")

    # 5. (c) Tidak ada komponen terhubung kecil (< 12 piksel) terpisah
    binary_mask = alpha == 255
    labeled, num_features = ndimage.label(binary_mask)
    sizes = ndimage.sum(binary_mask, labeled, range(num_features + 1))
    small_components = [int(sizes[i]) for i in range(1, num_features + 1) if sizes[i] < 12]
    report["details"]["smallComponentsCount"] = len(small_components)
    if len(small_components) > 0:
        report["failures"].append(f"Ditemukan {len(small_components)} komponen terhubung kecil (< 12 px): {small_components}")

    # 6. (d) Tidak ada piksel buram/artefak liar pada kolom/baris tepi
    # Edge checks (left, right, top, bottom boundary)
    edge_blur_count = 0
    for edge in [alpha[0, :], alpha[-1, :], alpha[:, 0], alpha[:, -1]]:
        edge_blur_count += int(np.sum((edge > 0) & (edge < 255)))
    report["details"]["edgeBlurPixels"] = edge_blur_count
    if edge_blur_count > 0:
        report["failures"].append(f"Ditemukan {edge_blur_count} piksel buram pada tepi luar.")

    # 7. Sisa magenta (#FF00FF)
    r, g, b = arr[:, :, 0].astype(int), arr[:, :, 1].astype(int), arr[:, :, 2].astype(int)
    mag_dist = np.sqrt((r - 255)**2 + (g - 0)**2 + (b - 255)**2)
    rem_mag = int(np.sum((mag_dist < 60) & (alpha == 255)))
    report["details"]["remainingMagentaPixels"] = rem_mag
    if rem_mag > 0:
        report["failures"].append(f"Sisa magenta terdeteksi: {rem_mag} piksel.")

    # 8. Palet warna unik (<= 32)
    visible = arr[alpha == 255]
    if len(visible) > 0:
        unique_colors = len(np.unique(visible[:, :3], axis=0))
        report["details"]["uniqueColors"] = unique_colors
        if unique_colors > 32:
            report["failures"].append(f"Jumlah warna unik melebihi 32: {unique_colors}")

    # 9. Karakter height check
    if kind == 'character_sheet':
        h_ratio = round(bbox_h / float(h), 3)
        report["details"]["heightRatio"] = h_ratio
        if h_ratio < 0.88:
            report["failures"].append(f"Tinggi karakter kurang dari 88%: {h_ratio:.1%}")

    if len(report["failures"]) > 0:
        report["pass"] = False

    return report

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 validate_asset.py <image.png> [brief.json]")
        sys.exit(1)
    b = {}
    if len(sys.argv) > 2:
        with open(sys.argv[2], 'r') as f:
            b = json.load(f)
    res = validate(sys.argv[1], b)
    print(json.dumps(res, indent=2))
    sys.exit(0 if res["pass"] else 1)
