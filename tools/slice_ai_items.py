#!/usr/bin/env python3
"""
slice_ai_items.py — Slices AI-generated Gemini item sheets into 32x32 pixel art icons.
Removes magenta chroma-key background and centers each icon in assets/items/*.png.
"""

import os
from PIL import Image
import numpy as np

OUTPUT_DIR = "/home/abarox/Desktop/prototipe web statis game/game/assets/items"
os.makedirs(OUTPUT_DIR, exist_ok=True)

SHEETS = [
    {
        "path": "/home/abarox/.gemini/antigravity/brain/4d2f9b08-f034-4550-b619-39a74fd29f25/beverage_spritesheet_1794142150116.jpg",
        "items": [
            "item_air_mineral",
            "item_teh_kemasan",
            "item_jus_kotak",
            "item_susu_kotak",
            "item_isotonik"
        ]
    },
    {
        "path": "/home/abarox/.gemini/antigravity/brain/4d2f9b08-f034-4550-b619-39a74fd29f25/snack_items_spritesheet_clean_1794142188044.jpg",
        "items": [
            "item_pisang",
            "item_roti_isi",
            "item_keripik",
            "item_coklat_batang",
            "item_gorengan"
        ]
    },
    {
        "path": "/home/abarox/.gemini/antigravity/brain/4d2f9b08-f034-4550-b619-39a74fd29f25/pixel_food_spritesheet_single_row_1794142198681.jpg",
        "items": [
            "item_mie_cup",
            "item_es_teh",
            "item_nasi_kuning",
            "item_nasi_goreng",
            "item_mie_goreng",
            "item_bakso"
        ]
    }
]

def chroma_key(im):
    arr = np.array(im.convert("RGBA"))
    # Detect magenta background: high R, low G, high B
    r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
    # Magenta distance
    is_magenta = (r > 165) & (g < 100) & (b > 165)
    # Also catch near-magenta fringing
    diff = np.abs(r.astype(int) - b.astype(int))
    is_fringe = (r > 140) & (b > 140) & (g < 120) & (diff < 50)
    alpha = np.where(is_magenta | is_fringe, 0, 255).astype(np.uint8)
    arr[:, :, 3] = alpha
    return Image.fromarray(arr), alpha > 0

def slice_sheet(sheet_info):
    path = sheet_info["path"]
    item_names = sheet_info["items"]
    raw_im = Image.open(path)
    keyed_im, fg_mask = chroma_key(raw_im)

    # Find columns containing foreground
    col_has_fg = np.any(fg_mask, axis=0)
    cols = []
    in_obj = False
    start = 0
    for i, has in enumerate(col_has_fg):
        if has and not in_obj:
            in_obj = True
            start = i
        elif not has and in_obj:
            in_obj = False
            if i - start > 15: # minimum 15px width
                cols.append((start, i))
    if in_obj and len(col_has_fg) - start > 15:
        cols.append((start, len(col_has_fg)))

    print(f"Processing {os.path.basename(path)}: found {len(cols)} segments for {len(item_names)} items")

    if len(cols) != len(item_names):
        print(f"  [WARN] Column count mismatch: {len(cols)} vs {len(item_names)}")

    for idx, name in enumerate(item_names):
        if idx >= len(cols):
            break
        c_start, c_end = cols[idx]
        # Crop column
        cropped = keyed_im.crop((c_start, 0, c_end, keyed_im.height))
        # Find exact tight bounding box by alpha
        bbox = cropped.getbbox()
        if not bbox:
            print(f"  [WARN] Empty bbox for {name}")
            continue
        tight = cropped.crop(bbox)

        # Fit into 28x28 (maintaining aspect ratio), then paste centered in 32x32 canvas
        tw, th = tight.size
        scale = min(28.0 / tw, 28.0 / th)
        nw, nh = max(1, int(round(tw * scale))), max(1, int(round(th * scale)))
        scaled = tight.resize((nw, nh), Image.NEAREST)

        icon32 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        ox = (32 - nw) // 2
        oy = (32 - nh) // 2
        icon32.paste(scaled, (ox, oy), scaled)

        out_path = os.path.join(OUTPUT_DIR, f"{name}.png")
        icon32.save(out_path)
        print(f"  Saved AI item icon: {name}.png (32x32, tight={tw}x{th})")

if __name__ == "__main__":
    for s in SHEETS:
        slice_sheet(s)
    print("\nAll 16 AI Gemini item icons generated and saved successfully!")
