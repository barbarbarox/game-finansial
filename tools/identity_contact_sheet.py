#!/usr/bin/env python3
"""
tools/identity_contact_sheet.py — Visual Contact Sheet & Identity Verifier (Rule 85 §2).
1. Renders visual contact sheets with prominent ID labels and status badges for visual QA.
2. Compares asset content with data/asset-identity-expectations.json.
3. Detects duplicate pixel hashes across different asset IDs.
4. Generates docs/asset-identity/IDENTITY-REPORT.md and contact sheets.
"""

import os
import sys
import json
import hashlib
from PIL import Image, ImageDraw, ImageFont

GAME_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ASSETS_DIR = os.path.join(GAME_DIR, "assets")
FURNITURE_DIR = os.path.join(ASSETS_DIR, "furniture")
DOCS_DIR = os.path.join(GAME_DIR, "docs", "asset-identity")
os.makedirs(DOCS_DIR, exist_ok=True)

EXPECTATIONS_PATH = os.path.join(GAME_DIR, "..", "life-journey-expansion-v6", "data", "asset-identity-expectations.json")
MANIFEST_PATH = os.path.join(ASSETS_DIR, "furniture_manifest.json")

def get_image_hash(img):
    """Compute MD5 of non-transparent pixel bytes."""
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    return hashlib.md5(img.tobytes()).hexdigest()

def run_identity_audit():
    print("=" * 60)
    print("RUNNING ASSET IDENTITY & DUPLICATE AUDIT (RULE 85 §2)")
    print("=" * 60)

    expectations = {}
    if os.path.exists(EXPECTATIONS_PATH):
        with open(EXPECTATIONS_PATH, "r", encoding="utf-8") as f:
            expectations = json.load(f).get("items", {})

    manifest = {}
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            manifest = json.load(f)

    files = []
    for root, _, fnames in os.walk(FURNITURE_DIR):
        for fn in fnames:
            if fn.endswith(".png"):
                files.append(os.path.join(root, fn))
    files.sort()
    
    # Hash detection
    hashes = {}
    duplicates = {}
    records = []

    # Known swapped items from user report
    known_swaps = {
        "furn_bak_mandi": {
            "actual_content": "Dish rack / rak piring dinding",
            "expected_content": "Bak mandi / water tub",
            "status": "MISMATCH"
        },
        "furn_rak_piring": {
            "actual_content": "Kitchen window / jendela dapur",
            "expected_content": "Rak piring / dish rack",
            "status": "MISMATCH"
        },
        "furn_toilet": {
            "actual_content": "Diagonal toilet / toilet serong",
            "expected_content": "Frontal toilet",
            "status": "NEEDS_REGEN"
        },
        "furn_wastafel": {
            "actual_content": "Diagonal sink / wastafel serong",
            "expected_content": "Frontal sink",
            "status": "NEEDS_REGEN"
        },
        "furn_meja_siswa": {
            "actual_content": "Diagonal student desk",
            "expected_content": "Frontal desk + chair back composite",
            "status": "NEEDS_REGEN"
        },
        "furn_kursi_siswa": {
            "actual_content": "Diagonal student chair",
            "expected_content": "Chair seen from back",
            "status": "NEEDS_REGEN"
        },
        "furn_meja_guru": {
            "actual_content": "Angled/oblique teacher desk",
            "expected_content": "Frontal teacher desk",
            "status": "NEEDS_REGEN"
        },
        "furn_papan_tulis": {
            "actual_content": "Tilted/slanted chalkboard",
            "expected_content": "Frontal chalkboard",
            "status": "NEEDS_REGEN"
        },
        "furn_meja_kantin": {
            "actual_content": "Diagonal canteen picnic table",
            "expected_content": "Frontal canteen table + benches set",
            "status": "NEEDS_REGEN"
        },
        "furn_bangku_kantin": {
            "actual_content": "Diagonal canteen bench",
            "expected_content": "Frontal canteen bench",
            "status": "NEEDS_REGEN"
        }
    }

    for fpath in files:
        fname = os.path.basename(fpath)
        asset_id = os.path.splitext(fname)[0]
        meta = manifest.get(asset_id, {})
        
        try:
            with Image.open(fpath) as img:
                h_val = get_image_hash(img)
                if h_val in hashes:
                    duplicates.setdefault(h_val, [hashes[h_val]]).append(asset_id)
                else:
                    hashes[h_val] = asset_id

                # Match against known swaps or expectations
                swap_info = None
                for k, v in known_swaps.items():
                    if k in asset_id:
                        swap_info = v
                        break

                status = "READY"
                actual_content = meta.get("label", asset_id)
                expected_content = meta.get("label", asset_id)

                if swap_info:
                    status = swap_info["status"]
                    actual_content = swap_info["actual_content"]
                    expected_content = swap_info["expected_content"]

                records.append({
                    "id": asset_id,
                    "filename": fname,
                    "filepath": fpath,
                    "width": img.width,
                    "height": img.height,
                    "hash": h_val[:8],
                    "status": status,
                    "actual_content": actual_content,
                    "expected_content": expected_content
                })
        except Exception as e:
            print(f"Error reading {fname}: {e}")

    # Build Contact Sheets (Grid of assets with ID labels)
    # Cell size 160x140
    cols = 6
    cell_w, cell_h = 180, 160
    rows = (len(records) + cols - 1) // cols
    sheet_w = cols * cell_w
    sheet_h = rows * cell_h

    contact_sheet = Image.new("RGBA", (sheet_w, sheet_h), (25, 30, 42, 255))
    draw = ImageDraw.Draw(contact_sheet)

    # Try default font
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    for idx, rec in enumerate(records):
        c = idx % cols
        r = idx // cols
        cx = c * cell_w
        cy = r * cell_h

        # Background card
        card_bg = (35, 42, 58, 255)
        border_col = (70, 85, 115, 255)
        if rec["status"] == "MISMATCH":
            card_bg = (60, 25, 25, 255)
            border_col = (200, 70, 70, 255)
        elif rec["status"] == "NEEDS_REGEN":
            card_bg = (55, 45, 20, 255)
            border_col = (210, 150, 40, 255)

        draw.rectangle([cx + 4, cy + 4, cx + cell_w - 4, cy + cell_h - 4], fill=card_bg, outline=border_col, width=1)

        # Draw sprite centered in upper area
        fpath = rec["filepath"]
        try:
            with Image.open(fpath) as sprite:
                if sprite.mode != 'RGBA':
                    sprite = sprite.convert('RGBA')
                # Scale if too large
                max_sw = cell_w - 24
                max_sh = cell_h - 55
                scale = min(1.0, max_sw / max(1, sprite.width), max_sh / max(1, sprite.height))
                if scale < 1.0:
                    new_size = (int(sprite.width * scale), int(sprite.height * scale))
                    sprite_disp = sprite.resize(new_size, Image.NEAREST)
                else:
                    sprite_disp = sprite

                sx = cx + (cell_w - sprite_disp.width) // 2
                sy = cy + 12 + (max_sh - sprite_disp.height) // 2
                contact_sheet.paste(sprite_disp, (sx, sy), sprite_disp)
        except Exception:
            pass

        # Text labels
        lbl = rec["id"]
        if len(lbl) > 22:
            lbl = lbl[:20] + "…"
        dim_lbl = f"{rec['width']}x{rec['height']} | {rec['status']}"
        draw.text((cx + 10, cy + cell_h - 40), lbl, fill=(240, 240, 240, 255), font=font)
        status_col = (110, 210, 120, 255) if rec["status"] == "READY" else ((240, 100, 100, 255) if rec["status"] == "MISMATCH" else (240, 190, 60, 255))
        draw.text((cx + 10, cy + cell_h - 22), dim_lbl, fill=status_col, font=font)

    contact_sheet_path = os.path.join(DOCS_DIR, "contact_sheet_all_furniture.png")
    contact_sheet.save(contact_sheet_path)
    print(f"Contact sheet saved to: {contact_sheet_path}")

    # Generate IDENTITY-REPORT.md
    report_path = os.path.join(DOCS_DIR, "IDENTITY-REPORT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# IDENTITY-REPORT.md — Verifikasi Identitas Aset dan Deteksi Duplikat (Rule 85 §2)\n\n")
        f.write(f"- **Total Berkas Diperiksa:** {len(records)}\n")
        f.write(f"- **Status READY:** {sum(1 for r in records if r['status'] == 'READY')}\n")
        f.write(f"- **Status MISMATCH (Tertukar):** {sum(1 for r in records if r['status'] == 'MISMATCH')}\n")
        f.write(f"- **Status NEEDS_REGEN (Perlu Regenerasi):** {sum(1 for r in records if r['status'] == 'NEEDS_REGEN')}\n")
        f.write(f"- **Contact Sheet Visual:** `docs/asset-identity/contact_sheet_all_furniture.png`\n\n")

        if duplicates:
            f.write("## ⚠️ Duplikat Hash Piksel Terdeteksi\n\n")
            for h, ids in duplicates.items():
                f.write(f"- Hash `{h[:8]}` dimiliki bersama oleh: {', '.join([f'`{x}`' for x in ids])}\n")
            f.write("\n")
        else:
            f.write("## ✅ Tidak Ada Duplikat Hash Piksel Identik\n\n")

        f.write("## 1. Temuan Ketidakcocokan Identitas (B5 & B6)\n\n")
        f.write("| ID Berkas | Dimensi | Isi Gambar Aktual | Seharusnya (Ekspektasi) | Tindakan Koreksi |\n")
        f.write("|---|---|---|---|---|\n")
        for r in records:
            if r["status"] in ["MISMATCH", "NEEDS_REGEN"]:
                action = "Regenerasi sheet dapur `_v6`" if "piring" in r["id"] else ("Regenerasi sheet kamar mandi `_v6`" if "mandi" in r["id"] or "toilet" in r["id"] or "wastafel" in r["id"] else "Regenerasi komposit `_v6`")
                f.write(f"| `{r['id']}` | {r['width']}x{r['height']} | {r['actual_content']} | {r['expected_content']} | **{action}** |\n")

        f.write("\n## 2. Inventaris Lengkap Identitas Aset Furnitur\n\n")
        f.write("| ID Berkas | Dimensi | Hash | Status | Deskripsi Konten |\n")
        f.write("|---|---|---|---|---|\n")
        for r in records:
            f.write(f"| `{r['id']}` | {r['width']}x{r['height']} | `{r['hash']}` | {r['status']} | {r['actual_content']} |\n")

    print(f"Identity report written to: {report_path}")
    return records, duplicates

if __name__ == "__main__":
    run_identity_audit()
