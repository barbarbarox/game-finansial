#!/usr/bin/env python3
"""
contact_sheet.py — Montase aset di atas latar netral, diperbesar 2x nearest-neighbor, untuk tinjauan visual.
"""

import sys
from PIL import Image

def make_contact_sheet(image_paths, output_path, scale=2):
    images = [Image.open(p).convert('RGBA') for p in image_paths]
    if not images:
        return

    # Total width and max height
    total_w = sum(img.width for img in images) + (len(images) + 1) * 16
    max_h = max(img.height for img in images) + 32

    # Canvas with neutral dark background (#1F2A44)
    canvas = Image.new('RGBA', (total_w, max_h), (31, 42, 68, 255))

    cur_x = 16
    for img in images:
        paste_y = (max_h - img.height) // 2
        canvas.paste(img, (cur_x, paste_y), img)
        cur_x += img.width + 16

    # Scale 2x with nearest neighbor
    scaled = canvas.resize((canvas.width * scale, canvas.height * scale), Image.Resampling.NEAREST)
    scaled.save(output_path, 'PNG')
    return scaled

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 contact_sheet.py <output.png> <img1.png> [img2.png ...]")
        sys.exit(1)
    make_contact_sheet(sys.argv[2:], sys.argv[1])
    print(f"Contact sheet saved to {sys.argv[1]}")
