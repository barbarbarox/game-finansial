#!/usr/bin/env python3
"""
process_generated_assets.py — Rule 60 processing pipeline for AI-generated images.
Processes:
1. indonesian_adult_npcs -> assets/npcs/npc_sheet_family.png (96x64)
2. sma_student_sprites -> assets/npcs/npc_sheet_friends.png (96x64)
3. indonesian_shop_npcs -> assets/npcs/npc_sheet_vendors.png (96x64)
4. indonesian_family_house -> assets/buildings/bld_rumah_pemain.png
5. minimarket_shop_front_facing -> assets/buildings/bld_minimarket.png
"""

import os
import sys
import numpy as np
from PIL import Image

from tools.chroma_key import remove_magenta_background
from tools.normalize import normalize_sprite
from tools.palette_snap import snap_to_palette
from tools.validate_asset import validate

PALETTE_PATH = "assets/palette.json"

def process_npc_sheet(raw_path, out_path, expected_count=2):
    print(f"\n--- Memproses NPC: {raw_path} -> {out_path} ---")
    # 1. Chroma key
    temp_keyed = "/tmp/temp_npc_keyed.png"
    remove_magenta_background(raw_path, temp_keyed, tolerance=60)
    keyed = Image.open(temp_keyed).convert('RGBA')

    # 2. Slice horizontally
    arr = np.array(keyed)
    alpha = arr[:, :, 3] > 0
    col_has = np.any(alpha, axis=0)

    # Find character segments
    segments = []
    in_seg = False
    start_x = 0
    for x, val in enumerate(col_has):
        if val and not in_seg:
            in_seg = True
            start_x = x
        elif not val and in_seg:
            in_seg = False
            if (x - start_x) >= 20: # NPC width > 20px
                segments.append((start_x, x))
    if in_seg and (len(col_has) - start_x) >= 20:
        segments.append((start_x, len(col_has)))

    print(f"Segmen karakter terdeteksi: {len(segments)}")
    if len(segments) < expected_count:
        w = keyed.width // expected_count
        segments = [(i * w, (i + 1) * w) for i in range(expected_count)]

    # We want a 96x64 sheet (3 frames @32x64)
    sheet = Image.new('RGBA', (96, 64), (0, 0, 0, 0))

    for idx in range(min(3, len(segments))):
        x1, x2 = segments[min(idx, len(segments) - 1)]
        char_crop = keyed.crop((x1, 0, x2, keyed.height))

        # Normalize to 32x64
        norm = normalize_sprite(char_crop, target_w=32, target_h=64, is_building_or_prop=False)

        # Temporary save for palette snap
        temp_norm = f"/tmp/temp_npc_norm_{idx}.png"
        norm.save(temp_norm, format="PNG")

        temp_snapped = f"/tmp/temp_npc_snapped_{idx}.png"
        snap_to_palette(temp_norm, PALETTE_PATH, temp_snapped)

        snapped = Image.open(temp_snapped).convert('RGBA')
        sheet.paste(snapped, (idx * 32, 0), snapped)

    # If only 2 characters, duplicate frame 0 to frame 2
    if len(segments) == 2:
        f0 = sheet.crop((0, 0, 32, 64))
        sheet.paste(f0, (64, 0), f0)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    sheet.save(out_path, format="PNG")
    print(f"✓ NPC Sheet tersimpan: {out_path} ({sheet.size[0]}x{sheet.size[1]})")

    res = validate(out_path)
    print(f"Hasil Validasi: {'PASS' if res['pass'] else 'FAIL'}")
    if not res['pass']:
        print("Failures:", res['failures'])

def process_building(raw_path, out_path, target_w, target_h):
    print(f"\n--- Memproses Bangunan: {raw_path} -> {out_path} ({target_w}x{target_h}) ---")
    # 1. Chroma key
    temp_keyed = f"/tmp/temp_bld_{target_w}_{target_h}_keyed.png"
    remove_magenta_background(raw_path, temp_keyed, tolerance=60)
    keyed = Image.open(temp_keyed).convert('RGBA')

    # 2. Normalize building
    norm = normalize_sprite(keyed, target_w=target_w, target_h=target_h, is_building_or_prop=True)

    # 3. Snap to palette
    temp_norm = f"/tmp/temp_bld_norm_{target_w}_{target_h}.png"
    norm.save(temp_norm, format="PNG")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    snap_to_palette(temp_norm, PALETTE_PATH, out_path)
    print(f"✓ Bangunan tersimpan: {out_path}")

    res = validate(out_path)
    print(f"Hasil Validasi: {'PASS' if res['pass'] else 'FAIL'}")
    if not res['pass']:
        print("Failures:", res['failures'])

def main():
    brain_dir = "/home/abarox/.gemini/antigravity/brain/4d2f9b08-f034-4550-b619-39a74fd29f25"

    adults_raw = os.path.join(brain_dir, "indonesian_adult_npcs_1794076770591.jpg")
    friends_raw = os.path.join(brain_dir, "sma_student_sprites_1794077171220.jpg")
    house_raw = os.path.join(brain_dir, "indonesian_family_house_pixel_art_1794077180245.jpg")
    minimarket_raw = os.path.join(brain_dir, "minimarket_shop_front_facing_1794077252826.jpg")
    if not os.path.exists(minimarket_raw):
        minimarket_raw = os.path.join(brain_dir, "minimarket_shop_sprite_1794077219187.jpg")
    vendors_raw = os.path.join(brain_dir, "indonesian_shop_npcs_16bit_1794077230852.jpg")

    # 1. NPC Family (Ibu & Ayah)
    if os.path.exists(adults_raw):
        process_npc_sheet(adults_raw, "assets/npcs/npc_sheet_family.png", expected_count=2)

    # 2. NPC Friends (Budi & Siswi SMA)
    if os.path.exists(friends_raw):
        process_npc_sheet(friends_raw, "assets/npcs/npc_sheet_friends.png", expected_count=2)

    # 3. NPC Vendors (Ibu Kantin, Kasir Minimarket, Petugas SPBU)
    if os.path.exists(vendors_raw):
        process_npc_sheet(vendors_raw, "assets/npcs/npc_sheet_vendors.png", expected_count=3)

    # 4. House Building (288x160)
    if os.path.exists(house_raw):
        process_building(house_raw, "assets/buildings/bld_rumah_pemain.png", target_w=288, target_h=160)

    # 5. Minimarket (256x160)
    if os.path.exists(minimarket_raw):
        process_building(minimarket_raw, "assets/buildings/bld_minimarket.png", target_w=256, target_h=160)

if __name__ == "__main__":
    main()
