#!/usr/bin/env python3
"""
palette_snap.py — Petakan tiap piksel ke warna terdekat di palette.json,
tanpa dithering, threshold alpha strictly {0, 255}.
"""

import sys
import json
import numpy as np
from PIL import Image

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return [int(hex_str[i:i+2], 16) for i in (0, 2, 4)]

def snap_to_palette(image_path, palette_path, output_path):
    with open(palette_path, 'r') as f:
        pdata = json.load(f)
    palette_colors = np.array([hex_to_rgb(c) for c in pdata['colors']], dtype=np.float32)

    img = Image.open(image_path).convert('RGBA')
    arr = np.array(img, dtype=np.float32)

    rgb = arr[:, :, :3]
    alpha = arr[:, :, 3]

    # Reshape for broadcasting
    h, w, _ = rgb.shape
    pixels = rgb.reshape(-1, 3)

    # Compute Euclidean distance to all palette colors
    # (pixels[:, None, :] - palette_colors[None, :, :]) has shape (N, P, 3)
    diff = pixels[:, np.newaxis, :] - palette_colors[np.newaxis, :, :]
    dist = np.sum(diff**2, axis=2)
    nearest_idx = np.argmin(dist, axis=1)

    snapped_pixels = palette_colors[nearest_idx].astype(np.uint8)
    snapped_rgb = snapped_pixels.reshape(h, w, 3)

    # Alpha threshold strictly: < 128 -> 0, >= 128 -> 255
    clean_alpha = np.where(alpha >= 128, 255, 0).astype(np.uint8)

    out_arr = np.dstack((snapped_rgb, clean_alpha))
    out_img = Image.fromarray(out_arr, 'RGBA')
    out_img.save(output_path, 'PNG')
    return out_img

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python3 palette_snap.py <input> <palette.json> <output>")
        sys.exit(1)
    snap_to_palette(sys.argv[1], sys.argv[2], sys.argv[3])
    print("Palette snap complete.")

