#!/usr/bin/env python3
"""
process_expansion_style_lock.py — Processes raw AI-generated assets for E4 Style Lock:
1. furn_sheet_kamar_pemain -> assets/furniture/kamar_pemain/
2. portrait_sheet_player -> assets/portraits/portrait_player_m.png & portrait_player_f.png
3. Generates 2x nearest-neighbor contact sheets in docs/checkpoint-B/
"""

import os
import sys
import numpy as np
from PIL import Image

# Import existing pipeline tools
from tools.chroma_key import remove_magenta_background
from tools.normalize import normalize_sprite
from tools.palette_snap import snap_to_palette

PALETTE_PATH = "assets/palette.json"
CHECKPOINT_DIR = "docs/checkpoint-B"
os.makedirs(CHECKPOINT_DIR, exist_ok=True)
os.makedirs("assets/furniture/kamar_pemain", exist_ok=True)
os.makedirs("assets/portraits", exist_ok=True)

def create_contact_sheet(images, titles, out_path, bg_color=(27, 40, 56, 255)):
    """Create a clean 2x contact sheet on neutral dark navy background"""
    card_w = 240
    card_h = 320
    padding = 20
    total_w = len(images) * (card_w + padding) + padding
    total_h = card_h + padding * 2

    canvas = Image.new('RGBA', (total_w, total_h), bg_color)

    for i, (img, title) in enumerate(zip(images, titles)):
        x = padding + i * (card_w + padding)
        y = padding

        # 2x nearest neighbor upscale for visual check
        scale = min((card_w - 20) / img.width, (card_h - 40) / img.height)
        scale_int = max(1, int(scale))
        upscaled = img.resize((img.width * scale_int, img.height * scale_int), Image.NEAREST)

        # Center in card
        paste_x = x + (card_w - upscaled.width) // 2
        paste_y = y + (card_h - upscaled.height - 20) // 2

        canvas.paste(upscaled, (paste_x, paste_y), upscaled)

    canvas.save(out_path)
    print(f"  [Contact Sheet] Saved -> {out_path}")

def process_furniture():
    raw_path = "assets/_raw/furn_sheet_kamar_pemain_raw.jpg"
    print(f"\n1. Memproses Furnitur Kamar Pemain: {raw_path}")
    temp_keyed = "/tmp/furn_kamar_keyed.png"
    remove_magenta_background(raw_path, temp_keyed, tolerance=55)
    keyed = Image.open(temp_keyed).convert('RGBA')

    # Detect horizontal segments
    arr = np.array(keyed)
    alpha = arr[:, :, 3] > 0
    col_has = np.any(alpha, axis=0)

    segments = []
    in_seg = False
    start_x = 0
    for x, val in enumerate(col_has):
        if val and not in_seg:
            in_seg = True
            start_x = x
        elif not val and in_seg:
            in_seg = False
            if (x - start_x) >= 30: # minimum width
                segments.append((start_x, x))
    if in_seg and (len(col_has) - start_x) >= 30:
        segments.append((start_x, len(col_has)))

    print(f"   Segmen furnitur terdeteksi: {len(segments)}")

    target_items = [
        ("furn_kasur_single", 64, 96, "Kasur Single"),
        ("furn_meja_belajar", 96, 64, "Meja Belajar"),
        ("furn_kursi_belajar", 32, 48, "Kursi Belajar"),
        ("furn_lemari_pakaian", 64, 96, "Lemari Pakaian"),
        ("furn_rak_buku", 64, 96, "Rak Buku"),
        ("furn_nakas_lampu", 32, 48, "Nakas & Lampu")
    ]

    # If count doesn't match, split equally
    if len(segments) != len(target_items):
        print(f"   [Peringatan] Jumlah segmen ({len(segments)}) != brief ({len(target_items)}). Membagi kolom secara proporsional.")
        w_step = keyed.width / len(target_items)
        segments = [(int(i * w_step), int((i + 1) * w_step)) for i in range(len(target_items))]

    processed_images = []
    titles = []

    for idx, (item_id, target_w, target_h, label) in enumerate(target_items):
        x1, x2 = segments[idx]
        item_crop = keyed.crop((x1, 0, x2, keyed.height))

        # Crop to alpha bbox
        bbox = item_crop.getbbox()
        if bbox:
            item_crop = item_crop.crop(bbox)

        # Normalize with Lanczos and bottom align
        normalized = normalize_sprite(item_crop, target_w, target_h)

        # Snap to palette
        snapped = snap_to_palette(normalized, PALETTE_PATH)

        out_path = f"assets/furniture/kamar_pemain/{item_id}.png"
        snapped.save(out_path)
        print(f"   ✓ Disimpan: {out_path} ({target_w}x{target_h})")

        processed_images.append(snapped)
        titles.append(f"{label} ({target_w}x{target_h})")

    # Create contact sheet
    contact_path = os.path.join(CHECKPOINT_DIR, "contact_sheet_kamar_pemain.png")
    create_contact_sheet(processed_images, titles, contact_path)

def process_portraits():
    raw_path = "assets/_raw/portrait_sheet_player_raw.jpg"
    print(f"\n2. Memproses Potret Karakter Pemain: {raw_path}")
    temp_keyed = "/tmp/portraits_player_keyed.png"
    remove_magenta_background(raw_path, temp_keyed, tolerance=55)
    keyed = Image.open(temp_keyed).convert('RGBA')

    # Detect 2 portraits horizontally
    arr = np.array(keyed)
    alpha = arr[:, :, 3] > 0
    col_has = np.any(alpha, axis=0)

    segments = []
    in_seg = False
    start_x = 0
    for x, val in enumerate(col_has):
        if val and not in_seg:
            in_seg = True
            start_x = x
        elif not val and in_seg:
            in_seg = False
            if (x - start_x) >= 80:
                segments.append((start_x, x))
    if in_seg and (len(col_has) - start_x) >= 80:
        segments.append((start_x, len(col_has)))

    print(f"   Segmen potret terdeteksi: {len(segments)}")
    if len(segments) != 2:
        mid = keyed.width // 2
        segments = [(0, mid), (mid, keyed.width)]

    target_portraits = [
        ("portrait_player_m", "Protagonis Laki-laki"),
        ("portrait_player_f", "Protagonis Perempuan")
    ]

    processed_portraits = []
    titles = []

    for idx, (p_id, label) in enumerate(target_portraits):
        x1, x2 = segments[idx]
        crop = keyed.crop((x1, 0, x2, keyed.height))
        bbox = crop.getbbox()
        if bbox:
            crop = crop.crop(bbox)

        normalized = normalize_sprite(crop, 192, 256)
        snapped = snap_to_palette(normalized, PALETTE_PATH)

        out_path = f"assets/portraits/{p_id}.png"
        snapped.save(out_path)
        print(f"   ✓ Disimpan: {out_path} (192x256)")

        processed_portraits.append(snapped)
        titles.append(f"{label} (192x256)")

    # Create contact sheet
    contact_path = os.path.join(CHECKPOINT_DIR, "contact_sheet_portraits_player.png")
    create_contact_sheet(processed_portraits, titles, contact_path)

if __name__ == "__main__":
    process_furniture()
    process_portraits()
    print("\n[OK] Seluruh aset E4 Style Lock berhasil diproses & disimpan!")
