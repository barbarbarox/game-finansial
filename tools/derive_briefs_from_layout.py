#!/usr/bin/env python3
"""
derive_briefs_from_layout.py — Auto-derives AI image generation briefs from slot layouts (Rule 73 §1).
Reads the 7 map layout files, extracts all furniture slots (exact W x H px, class_, facing),
and structures them into sheets of 4–6 cohesive items per room with deterministic prompts.
"""

import os
import json
import math

MAPS = [
    ('home', 'game/data/maps/home.layout.json'),
    ('school', 'game/data/maps/school.layout.json'),
    ('minimarket', 'game/data/maps/minimarket.layout.json'),
    ('toko_kosmetik', 'game/data/maps/toko_kosmetik.layout.json'),
    ('spbu', 'game/data/maps/spbu.layout.json'),
    ('game_center', 'game/data/maps/game_center.layout.json'),
    ('town_hub', 'game/data/maps/town_hub.layout.json')
]

STYLE_BLOCK = (
    "Cozy chunky pixel art with clearly visible square pixels, top-down 3/4 RPG perspective "
    "(camera tilted so building fronts and character faces are visible; NOT isometric, NOT pure overhead). "
    "Crisp hard-edged pixels, no anti-aliasing, no blur, no gradients, no dithering noise, flat shading with 2-3 tones "
    "per material, 1px dark warm outline (#2A1F1A-like deep brown/navy). Soft warm morning light from the upper left, "
    "shadows as one flat darker tone falling to the lower right. Calm, warm, cozy mood of a small Indonesian town. "
    "Limited palette built around: warm cream #F7EEDA and #E9D8B4; muted green #A5BE93, #6F9262, #44603F; "
    "soft brown #C9A27A, #9A6F4C, #5E3F2A; dark navy #1F2A44, #34456B. Sparing accents only: mustard #D9A441, terracotta #C0654A."
)

NEGATIVE_BLOCK = (
    "Avoid: any text, letters, numbers, logos, watermarks, real-world brand names, photorealism, "
    "3D render, smooth vector art, glow, neon, soft airbrushed shading, drop shadows with blur, emoji, "
    "isometric view, extra characters, cropped subjects, busy backgrounds, anti-aliased edges."
)

def chunk_items(items, max_size=5):
    """Splits a list into chunks of at most max_size items."""
    return [items[i:i + max_size] for i in range(0, len(items), max_size)]

def derive_briefs():
    derived_catalog = {}
    master_assets = []

    for map_id, path in MAPS:
        if not os.path.exists(path):
            continue
        with open(path, 'r') as f:
            layout = json.load(f)

        furniture = layout.get('furniture', [])
        if not furniture:
            continue

        # Group by room / prefix
        grouped = {}
        for f in furniture:
            item_id = f.get('assetId') or f.get('id')
            slot_id = f.get('id')
            # Extract zone or prefix
            parts = slot_id.split('_')
            zone = parts[1] if len(parts) > 2 else 'main'
            key = f"{map_id}_{zone}"
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(f)

        map_briefs = []

        for group_key, items in grouped.items():
            # Deduplicate by assetId so sheets only generate unique assets
            unique_assets = {}
            for it in items:
                aid = it.get('assetId') or it.get('id')
                if aid not in unique_assets:
                    unique_assets[aid] = it

            chunks = chunk_items(list(unique_assets.values()), max_size=5)
            for idx, chunk in enumerate(chunks):
                sheet_id = f"sheet_{group_key}_{idx + 1}"
                item_desc_list = []
                subjects = []
                is_counter_module = any(it.get('class_') == 'counter_module' for it in chunk)

                for it in chunk:
                    aid = it.get('assetId') or it.get('id')
                    w_px = int(it.get('w', 1) * 32)
                    h_px = int(it.get('h', 1) * 32)
                    role = it.get('class_', 'free')
                    lbl = it.get('label') or it.get('id')
                    item_desc_list.append(f"{lbl} ({w_px}x{h_px} px, role: {role})")
                    subjects.append({
                        "assetId": aid,
                        "label": lbl,
                        "class_": role,
                        "w": w_px,
                        "h": h_px,
                        "facing": it.get('facing', 'front')
                    })

                items_text = ", ".join(item_desc_list)
                module_rule = (
                    "These are kitchen counter MODULES that must butt together into one continuous row: "
                    "identical total height, identical top-surface level and base line, plain flat vertical cut on the left "
                    "and right edges, no side panels, same wood and cream materials. "
                    if is_counter_module else ""
                )

                prompt = (
                    f"{STYLE_BLOCK} Furniture sprite sheet for {group_key}. "
                    f"Items left to right: {items_text}. Every item is front-facing (facing the camera), "
                    f"top-down 3/4 RPG view, drawn as ONE separate object with a flat straight base along its bottom edge, "
                    f"no walls, no floor, no surrounding room. {module_rule}Items are drawn at consistent real-world scale "
                    f"relative to each other with the same visible pixel size. All screens, labels, frames and book spines "
                    f"blank or abstract. Flat solid magenta #FF00FF background, no shadows on the background. "
                    f"Match the art style, pixel size, outline weight and palette of the reference image exactly. "
                    f"{NEGATIVE_BLOCK}"
                )

                brief = {
                    "id": sheet_id,
                    "mapId": map_id,
                    "zone": group_key,
                    "kind": "furniture_sheet",
                    "prompt": prompt,
                    "isCounterModule": is_counter_module,
                    "background": "#FF00FF",
                    "subjects": subjects
                }
                map_briefs.append(brief)
                master_assets.append(brief)

        # Write per-map brief
        out_path = f"game/data/asset-briefs-v4-{map_id}.json"
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'w') as f:
            json.dump({
                "mapId": map_id,
                "sheetsCount": len(map_briefs),
                "sheets": map_briefs
            }, f, indent=2)
        print(f"Generated {len(map_briefs)} sheets in {out_path}")

    # Write master brief
    master_out = "game/data/asset-briefs-v4.json"
    with open(master_out, 'w') as f:
        json.dump({
            "version": 1,
            "styleRef": ["docs/STYLE-BIBLE.md", "docs/STYLE-BIBLE-V4.md"],
            "totalSheets": len(master_assets),
            "sheets": master_assets
        }, f, indent=2)
    print(f"Generated master briefs in {master_out} ({len(master_assets)} sheets total).")

if __name__ == "__main__":
    derive_briefs()

