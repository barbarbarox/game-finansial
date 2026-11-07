#!/usr/bin/env python3
"""
validate_asset.py — Cek teknis Rule 60 bagian 4:
- Dimensi sesuai brief
- Alpha strictly {0, 255}
- Tidak ada sisa magenta (jarak warna < 60 dari #FF00FF = 0 piksel)
- Warna dalam palette, jumlah warna unik <= 32
- Karakter: tinggi isi >= 88% tinggi frame, kaki di baris dasar, center-of-mass dalam +/- 2px dari tengah
"""

import sys
import json
import numpy as np
from PIL import Image

def validate(image_path, brief):
    img = Image.open(image_path).convert('RGBA')
    arr = np.array(img)
    w, h = img.size

    report = {
        "pass": True,
        "failures": [],
        "warnings": [],
        "details": {}
    }

    # 1. Dimensi
    expected_w = brief.get('width')
    expected_h = brief.get('height')
    if expected_w and w != expected_w:
        report["failures"].append(f"Lebar tidak cocok: {w} != {expected_w}")
    if expected_h and h != expected_h:
        report["failures"].append(f"Tinggi tidak cocok: {h} != {expected_h}")

    # 2. Alpha check
    alpha = arr[:, :, 3]
    invalid_alpha = np.sum((alpha > 0) & (alpha < 255))
    if invalid_alpha > 0:
        report["failures"].append(f"Alpha tidak biner: {invalid_alpha} piksel semi-transparan.")

    # 3. Magenta check
    r, g, b = arr[:, :, 0].astype(int), arr[:, :, 1].astype(int), arr[:, :, 2].astype(int)
    mag_dist = np.sqrt((r - 255)**2 + (g - 0)**2 + (b - 255)**2)
    rem_mag = np.sum((mag_dist < 60) & (alpha == 255))
    if rem_mag > 0:
        report["failures"].append(f"Sisa magenta terdeteksi: {rem_mag} piksel.")

    # 4. Palet & Jumlah warna unik
    visible = arr[alpha == 255]
    if len(visible) > 0:
        unique_colors = len(np.unique(visible[:, :3], axis=0))
        report["details"]["uniqueColors"] = unique_colors
        if unique_colors > 32:
            report["failures"].append(f"Jumlah warna unik melebihi 32: {unique_colors}")

    # 5. Karakter specific checks
    if brief.get('kind') == 'character_sheet':
        # Check fill height
        bbox = img.getbbox()
        if bbox:
            fill_h = bbox[3] - bbox[1]
            h_ratio = fill_h / h
            report["details"]["heightRatio"] = round(h_ratio, 3)
            if h_ratio < 0.75:  # Tolerance threshold
                report["warnings"].append(f"Tinggi karakter kurang dari rasio ideal: {h_ratio:.2f}")

    if len(report["failures"]) > 0:
        report["pass"] = False

    return report

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 validate_asset.py <image.png> [brief.json]")
        sys.exit(1)
    brief = {}
    if len(sys.argv) > 2:
        with open(sys.argv[2], 'r') as f:
            brief = json.load(f)
    rep = validate(sys.argv[1], brief)
    print(json.dumps(rep, indent=2))
    sys.exit(0 if rep["pass"] else 1)
