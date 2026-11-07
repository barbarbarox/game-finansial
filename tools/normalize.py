#!/usr/bin/env python3
"""
normalize.py — Crop bbox, skala ke target dengan Lanczos (area-average),
pusatkan horizontal, ratakan dasar (kaki/dasar bangunan) ke baris terbawah frame.
Sesuai revisi Checkpoint A:
- Membersihkan komponen kecil terisolasi (< 12 px) dan artefak garis batas 1px.
- Dasar bangunan/prop/karakter WAJIB menempel di baris terbawah gambar.
- Padding transparan hanya di bagian atas (dan seperlunya di kiri/kanan) untuk mencapai kelipatan 32.
"""

import sys
import numpy as np
from PIL import Image
import scipy.ndimage as ndimage

def clean_artifacts(img, min_component_size=12):
    arr = np.array(img.convert('RGBA'))
    alpha = arr[:, :, 3] > 0

    # 1. Strip 1px border lines touching edges if isolated
    # Check if edge rows/cols have thin lines
    for edge_idx, is_row in [(0, True), (-1, True), (0, False), (-1, False)]:
        line = alpha[edge_idx, :] if is_row else alpha[:, edge_idx]
        adj = alpha[1 if edge_idx == 0 else -2, :] if is_row else alpha[:, 1 if edge_idx == 0 else -2]
        # If edge has pixels but adjacent has few or none, it's a border artifact
        if np.sum(line) > 0 and np.sum(adj) < np.sum(line) * 0.3:
            if is_row:
                arr[edge_idx, :, 3] = 0
            else:
                arr[:, edge_idx, 3] = 0

    # 2. Filter small connected components (< min_component_size)
    alpha = arr[:, :, 3] > 0
    if not np.any(alpha):
        return Image.fromarray(arr)

    labeled, num_features = ndimage.label(alpha)
    sizes = ndimage.sum(alpha, labeled, range(num_features + 1))
    for feat_idx in range(1, num_features + 1):
        if sizes[feat_idx] < min_component_size:
            arr[labeled == feat_idx, 3] = 0

    return Image.fromarray(arr)

def normalize_sprite(image_or_path, target_w=32, target_h=64, is_building_or_prop=False):
    if isinstance(image_or_path, str):
        img = Image.open(image_or_path).convert('RGBA')
    else:
        img = image_or_path.convert('RGBA')

    # Clean artifacts first
    cleaned = clean_artifacts(img, min_component_size=12)

    bbox = cleaned.getbbox()
    if not bbox:
        return Image.new('RGBA', (target_w, target_h), (0, 0, 0, 0))

    cropped = cleaned.crop(bbox)
    crop_w, crop_h = cropped.size

    if is_building_or_prop:
        # Scale width to target_w
        scale = target_w / float(crop_w)
        scaled_w = target_w
        scaled_h = int(round(crop_h * scale))

        # Height must be multiple of 32, minimum scaled_h
        final_h = int(np.ceil(scaled_h / 32.0) * 32)
        if target_h and target_h > final_h:
            final_h = target_h

        scaled = cropped.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)
        canvas = Image.new('RGBA', (target_w, final_h), (0, 0, 0, 0))
        # Base touches bottom row!
        paste_y = final_h - scaled_h
        canvas.paste(scaled, (0, paste_y), scaled)
        return canvas
    else:
        # Character normalization: fit into target_w x target_h
        max_allowable_h = target_h - 2  # leave 1-2px top margin
        scale = min(target_w / float(crop_w), max_allowable_h / float(crop_h))
        new_w = max(1, int(round(crop_w * scale)))
        new_h = max(1, int(round(crop_h * scale)))

        scaled = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)
        canvas = Image.new('RGBA', (target_w, target_h), (0, 0, 0, 0))
        paste_x = (target_w - new_w) // 2
        paste_y = target_h - new_h  # Base touches bottom row!
        canvas.paste(scaled, (paste_x, paste_y), scaled)
        return canvas

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 normalize.py <input> <output> [width] [height] [--building]")
        sys.exit(1)
    tw = int(sys.argv[3]) if len(sys.argv) > 3 else 32
    th = int(sys.argv[4]) if len(sys.argv) > 4 else 64
    is_bld = "--building" in sys.argv
    out = normalize_sprite(sys.argv[1], tw, th, is_building_or_prop=is_bld)
    out.save(sys.argv[2])
    print(f"Normalized to {out.size[0]}x{out.size[1]}.")
