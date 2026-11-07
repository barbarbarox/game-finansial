#!/usr/bin/env python3
"""
normalize.py — Crop bbox, skala ke target dengan Lanczos (area-average),
pusatkan horizontal, ratakan dasar (kaki) ke baris terbawah frame.
"""

import sys
from PIL import Image

def normalize_sprite(image_or_path, target_w=32, target_h=64):
    if isinstance(image_or_path, str):
        img = Image.open(image_or_path).convert('RGBA')
    else:
        img = image_or_path.convert('RGBA')

    # Get bounding box of visible content
    bbox = img.getbbox()
    if not bbox:
        # Empty sprite
        return Image.new('RGBA', (target_w, target_h), (0, 0, 0, 0))

    cropped = img.crop(bbox)

    # Scale to fit target while maintaining aspect ratio,
    # ensuring height fills >= 88% of target_h for characters
    crop_w, crop_h = cropped.size
    max_allowable_h = target_h - 2  # leave 1-2px top margin
    scale = min(target_w / crop_w, max_allowable_h / crop_h)

    new_w = max(1, int(crop_w * scale))
    new_h = max(1, int(crop_h * scale))

    scaled = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # Create target canvas
    canvas = Image.new('RGBA', (target_w, target_h), (0, 0, 0, 0))
    paste_x = (target_w - new_w) // 2
    paste_y = target_h - new_h  # align bottom to bottom row

    canvas.paste(scaled, (paste_x, paste_y), scaled)
    return canvas

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 normalize.py <input> <output> [width] [height]")
        sys.exit(1)
    tw = int(sys.argv[3]) if len(sys.argv) > 3 else 32
    th = int(sys.argv[4]) if len(sys.argv) > 4 else 64
    out = normalize_sprite(sys.argv[1], tw, th)
    out.save(sys.argv[2])
    print(f"Normalized to {tw}x{th}.")

