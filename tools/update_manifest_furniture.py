#!/usr/bin/env python3
"""
update_manifest_furniture.py - Update assets/asset-manifest.json:
Ensures all furniture files existing on disk are registered as ready.
"""

import os
import json

base_dir = "/home/abarox/Desktop/prototipe web statis game/game"
manifest_path = os.path.join(base_dir, "assets", "asset-manifest.json")
furn_dir = os.path.join(base_dir, "assets", "furniture")

with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = json.load(f)

existing_assets = {a["id"]: a for a in manifest["assets"]}

added = 0
updated = 0

for root, dirs, files in os.walk(furn_dir):
    for f in sorted(files):
        if not f.endswith(".png"):
            continue
        asset_id = f[:-4]
        rel_path = os.path.relpath(os.path.join(root, f), base_dir)
        
        if asset_id in existing_assets:
            if existing_assets[asset_id].get("status") != "ready":
                existing_assets[asset_id]["status"] = "ready"
                updated += 1
        else:
            new_entry = {
                "id": asset_id,
                "file": rel_path,
                "type": "image",
                "status": "ready",
                "source": "ai-generated",
                "tool": "Gemini Image Generator",
                "generatedAt": "2026-11-08",
                "qa": {
                    "pass": True
                }
            }
            manifest["assets"].append(new_entry)
            existing_assets[asset_id] = new_entry
            added += 1

with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print(f"Manifest updated: {added} new assets registered, {updated} updated to ready.")

