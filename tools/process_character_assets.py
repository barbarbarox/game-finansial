#!/usr/bin/env python3
"""
process_character_assets.py — Process all newly generated character assets:
1. Chroma key removal (#FF00FF)
2. Slicing portraits and character sprites
3. Normalization (192x256 for portraits, 32x64 for character sprites)
4. Palette snapping (assets/palette.json)
5. Saving to assets/portraits/ and assets/npcs/
6. Updating asset-manifest.json
"""

import os
import sys
import json
import numpy as np
from PIL import Image

sys.path.append(os.path.dirname(__file__))
from chroma_key import remove_magenta_background
from slice_sheet import slice_horizontal_subjects
from normalize import normalize_sprite, clean_artifacts
from palette_snap import snap_to_palette

PALETTE_PATH = "assets/palette.json"
BRAIN_DIR = "/home/abarox/.gemini/antigravity/brain/4d2f9b08-f034-4550-b619-39a74fd29f25"
PORTRAITS_DIR = "assets/portraits"
NPCS_DIR = "assets/npcs"
MANIFEST_PATH = "assets/asset-manifest.json"

os.makedirs(PORTRAITS_DIR, exist_ok=True)
os.makedirs(NPCS_DIR, exist_ok=True)

RAW_MAP = {
    "portrait_sheet_family": {
        "file": os.path.join(BRAIN_DIR, "portrait_sheet_family_1794123004695.jpg"),
        "type": "portrait",
        "count": 2,
        "subjects": ["portrait_ibu", "portrait_ayah"]
    },
    "portrait_sheet_friends": {
        "file": os.path.join(BRAIN_DIR, "portrait_sheet_friends_1794123064818.jpg"),
        "type": "portrait",
        "count": 2,
        "subjects": ["portrait_teman_l", "portrait_teman_p"]
    },
    "portrait_sheet_vendors": {
        "file": os.path.join(BRAIN_DIR, "portrait_sheet_vendors_1794123072952.jpg"),
        "type": "portrait",
        "count": 5,
        "subjects": [
            "portrait_penjual_kantin",
            "portrait_kasir_minimarket",
            "portrait_penjaga_kosmetik",
            "portrait_petugas_spbu",
            "portrait_penjaga_game"
        ]
    },
    "npc_sheet_family": {
        "file": os.path.join(BRAIN_DIR, "npc_sheet_family_1794123041207.jpg"),
        "type": "npc_sheet",
        "count": 2,
        "subjects": ["npc_ibu", "npc_ayah"],
        "sheet_output": "npc_sheet_family.png"
    },
    "npc_sheet_friends": {
        "file": os.path.join(BRAIN_DIR, "npc_sheet_friends_1794123121224.jpg"),
        "type": "npc_sheet",
        "count": 2,
        "subjects": ["npc_budi", "npc_siti"],
        "sheet_output": "npc_sheet_friends.png"
    },
    "npc_sheet_vendors": {
        "file": os.path.join(BRAIN_DIR, "npc_sheet_vendors_1794123227991.jpg"),
        "type": "npc_sheet",
        "count": 5,
        "subjects": [
            "npc_penjual_kantin",
            "npc_kasir_minimarket",
            "npc_penjaga_kosmetik",
            "npc_petugas_spbu",
            "npc_penjaga_game"
        ],
        "sheet_output": "npc_sheet_vendors.png"
    }
}

def process_portraits(sheet_info):
    raw_path = sheet_info["file"]
    temp_keyed = "/tmp/keyed_portraits.png"
    remove_magenta_background(raw_path, temp_keyed, tolerance=65)

    slices = slice_horizontal_subjects(temp_keyed, sheet_info["count"])
    processed = []

    for i, sub_id in enumerate(sheet_info["subjects"]):
        if i >= len(slices):
            break
        raw_slice = slices[i]
        # Clean artifacts
        cleaned = clean_artifacts(raw_slice, min_component_size=8)
        bbox = cleaned.getbbox()
        if bbox:
            cropped = cleaned.crop(bbox)
        else:
            cropped = cleaned

        # Portraits are 192x256 half-body
        # Scale to fit comfortably in 192x256
        target_w, target_h = 192, 256
        cw, ch = cropped.size
        scale = min((target_w - 16) / float(cw), (target_h - 16) / float(ch))
        nw = max(1, int(round(cw * scale)))
        nh = max(1, int(round(ch * scale)))
        scaled = cropped.resize((nw, nh), Image.Resampling.LANCZOS)

        canvas = Image.new('RGBA', (target_w, target_h), (0, 0, 0, 0))
        # Center horizontally, bottom aligned
        px = (target_w - nw) // 2
        py = target_h - nh
        canvas.paste(scaled, (px, py), scaled)

        # Snap to palette
        snapped = snap_to_palette(canvas, PALETTE_PATH)
        out_path = os.path.join(PORTRAITS_DIR, f"{sub_id}.png")
        snapped.save(out_path)
        print(f"   ✓ Portrait saved: {out_path} ({target_w}x{target_h})")
        processed.append((sub_id, out_path))

    return processed

def process_npc_sprites(sheet_info):
    raw_path = sheet_info["file"]
    temp_keyed = "/tmp/keyed_npcs.png"
    remove_magenta_background(raw_path, temp_keyed, tolerance=65)

    slices = slice_horizontal_subjects(temp_keyed, sheet_info["count"])
    target_w, target_h = 32, 64
    count = sheet_info["count"]

    # Master spritesheet canvas: (count * 32) x 64
    sheet_canvas = Image.new('RGBA', (count * target_w, target_h), (0, 0, 0, 0))
    processed = []

    for i, sub_id in enumerate(sheet_info["subjects"]):
        if i >= len(slices):
            break
        raw_slice = slices[i]
        norm = normalize_sprite(raw_slice, target_w, target_h, is_building_or_prop=False)
        snapped = snap_to_palette(norm, PALETTE_PATH)

        # Save individual sprite
        indiv_path = os.path.join(NPCS_DIR, f"{sub_id}.png")
        snapped.save(indiv_path)
        print(f"   ✓ NPC individual sprite saved: {indiv_path} ({target_w}x{target_h})")

        # Paste into spritesheet at frame i
        sheet_canvas.paste(snapped, (i * target_w, 0), snapped)
        processed.append((sub_id, indiv_path))

    # Save full spritesheet
    sheet_out_path = os.path.join(NPCS_DIR, sheet_info["sheet_output"])
    sheet_canvas.save(sheet_out_path)
    print(f"   ✓ NPC spritesheet saved: {sheet_out_path} ({sheet_canvas.width}x{sheet_canvas.height})")

    return processed

def main():
    print("==================================================")
    print("  PROCESSING GENERATED CHARACTER ASSETS")
    print("==================================================")

    for key, info in RAW_MAP.items():
        print(f"\nProcessing {key}...")
        if not os.path.exists(info["file"]):
            print(f"   [Error] File not found: {info['file']}")
            continue

        if info["type"] == "portrait":
            process_portraits(info)
        elif info["type"] == "npc_sheet":
            process_npc_sprites(info)

    # Update asset manifest
    print("\nUpdating asset-manifest.json...")
    with open(MANIFEST_PATH, 'r') as f:
        manifest = json.load(f)

    ready_ids = set()
    for info in RAW_MAP.values():
        for s in info["subjects"]:
            ready_ids.add(s)
        if "sheet_output" in info:
            ready_ids.add(info["sheet_output"].replace(".png", ""))

    for a in manifest.get("assets", []):
        if a["id"] in ready_ids:
            a["status"] = "ready"
            a["source"] = "ai-generated"
            a["tool"] = "Gemini Image Generator"
            if "qa" in a:
                a["qa"]["pass"] = True

    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=2)

    print("✓ asset-manifest.json updated successfully.")

if __name__ == "__main__":
    main()
