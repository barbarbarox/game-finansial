#!/usr/bin/env python3
"""
slice_sheet.py — Pisahkan sheet menjadi subjek terpisah lewat connected-components / bounding boxes pada alpha.
"""

import sys
from PIL import Image
import numpy as np

def slice_horizontal_subjects(image_path, expected_count=3):
    img = Image.open(image_path).convert('RGBA')
    arr = np.array(img)
    alpha = arr[:, :, 3]

    # Find columns that have any non-transparent pixel
    col_has_content = np.any(alpha > 0, axis=0)

    # Find segments of consecutive columns
    segments = []
    in_segment = False
    start_x = 0

    for x, has_content in enumerate(col_has_content):
        if has_content and not in_segment:
            in_segment = True
            start_x = x
        elif not has_content and in_segment:
            in_segment = False
            # Filter noise segments < 4px
            if (x - start_x) >= 4:
                segments.append((start_x, x))

    if in_segment and (len(col_has_content) - start_x) >= 4:
        segments.append((start_x, len(col_has_content)))

    # If count doesn't match expected_count, fallback to equal vertical cuts
    sliced_images = []
    if len(segments) == expected_count:
        for x1, x2 in segments:
            sub = img.crop((x1, 0, x2, img.height))
            sliced_images.append(sub)
    else:
        # Equal division
        w = img.width // expected_count
        for i in range(expected_count):
            sub = img.crop((i * w, 0, (i + 1) * w, img.height))
            sliced_images.append(sub)

    return sliced_images

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 slice_sheet.py <input> <output_prefix> [expected_count]")
        sys.exit(1)
    exp = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    subs = slice_horizontal_subjects(sys.argv[1], exp)
    for i, s in enumerate(subs):
        s.save(f"{sys.argv[2]}_{i}.png")
    print(f"Sliced into {len(subs)} images.")

