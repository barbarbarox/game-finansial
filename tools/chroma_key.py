#!/usr/bin/env python3
"""
chroma_key.py — Hapus latar magenta (#FF00FF), hasilkan alpha {0, 255}, despill tepi.
"""

import sys
import numpy as np
from PIL import Image

def remove_magenta_background(image_path, output_path, tolerance=60):
    img = Image.open(image_path).convert('RGBA')
    arr = np.array(img, dtype=np.int32)

    # Magenta reference: (255, 0, 255)
    r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]

    # Euclidean distance to #FF00FF in RGB
    dist = np.sqrt((r - 255)**2 + (g - 0)**2 + (b - 255)**2)

    # Mask for magenta background
    is_magenta = dist < tolerance

    # Clean alpha: 0 or 255 strictly
    out_arr = np.array(img)
    out_arr[:, :, 3] = np.where(is_magenta, 0, 255)

    # Edge despill: if a pixel is semi-magenta, reduce magenta spill
    edge_spill = (dist < tolerance * 1.5) & (~is_magenta)
    out_arr[edge_spill, 0] = np.clip(out_arr[edge_spill, 0] * 0.8, 0, 255)
    out_arr[edge_spill, 2] = np.clip(out_arr[edge_spill, 2] * 0.8, 0, 255)

    result = Image.fromarray(out_arr, 'RGBA')
    result.save(output_path, 'PNG')

    # Count remaining magenta pixels
    rem_dist = np.sqrt((out_arr[:, :, 0].astype(int) - 255)**2 +
                       (out_arr[:, :, 1].astype(int) - 0)**2 +
                       (out_arr[:, :, 2].astype(int) - 255)**2)
    rem_magenta = np.sum((rem_dist < 60) & (out_arr[:, :, 3] == 255))
    return int(rem_magenta)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 chroma_key.py <input> <output> [tolerance]")
        sys.exit(1)
    tol = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    rem = remove_magenta_background(sys.argv[1], sys.argv[2], tol)
    print(f"Chroma key complete. Remaining magenta pixels: {rem}")

