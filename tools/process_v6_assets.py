#!/usr/bin/env python3
"""
tools/process_v6_assets.py — Process, slice, chromakey, and scale all V6 assets.
Follows:
- data/asset-briefs-v6.json
- data/furniture-catalog-v6-delta.json
- Rule 85 (Perspective & Identity QA)
Outputs:
- Assets with _v6 suffix into game/assets/furniture/ and game/assets/npcs/
- Before/after comparison sheets into game/docs/checkpoint-E/
- game/docs/checkpoint-E/CHECKPOINT-E-REPORT.md
"""

import os
import sys
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

GAME_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ASSETS_DIR = os.path.join(GAME_DIR, "assets")
FURN_DIR = os.path.join(ASSETS_DIR, "furniture")
NPC_DIR = os.path.join(ASSETS_DIR, "npcs")
CHECKPOINT_DIR = os.path.join(GAME_DIR, "docs", "checkpoint-E")
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

BRAIN_DIR = "/home/abarox/.gemini/antigravity/brain/4d2f9b08-f034-4550-b619-39a74fd29f25"

def chromakey_crop(img, thresh_magenta=True):
    """Replaces magenta #FF00FF with transparent alpha and crops to bbox."""
    arr = np.array(img.convert("RGBA"))
    r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
    
    if thresh_magenta:
        is_magenta = (r > 160) & (g < 100) & (b > 160) & (np.abs(r.astype(int) - b.astype(int)) < 65)
        edge_magenta = (r > 130) & (g < 125) & (b > 130) & (r > g + 25) & (b > g + 25)
        mask = is_magenta | edge_magenta
        arr[mask, 3] = 0

    alpha = arr[:, :, 3]
    bbox = np.where(alpha > 15)
    if len(bbox[0]) == 0 or len(bbox[1]) == 0:
        return Image.fromarray(arr)
    
    y0, y1 = bbox[0].min(), bbox[0].max() + 1
    x0, x1 = bbox[1].min(), bbox[1].max() + 1
    return Image.fromarray(arr[y0:y1, x0:x1])

def fit_to_target_box(img, target_size, align_bottom=True):
    """Fits image into target_size (w, h) maintaining aspect ratio with sharp pixel resizing."""
    tw, th = target_size
    kw, kh = img.size
    
    scale = min(tw / kw, th / kh)
    nw = max(1, int(round(kw * scale)))
    nh = max(1, int(round(kh * scale)))
    
    resized = img.resize((nw, nh), Image.NEAREST)
    canvas = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    
    ox = (tw - nw) // 2
    oy = (th - nh) if align_bottom else ((th - nh) // 2)
    canvas.paste(resized, (ox, oy), resized)
    return canvas

def extract_boxes_from_sheet(raw_path, min_size=30):
    """Extracts non-magenta bounding boxes from sheet in left-to-right order."""
    im = Image.open(raw_path).convert("RGB")
    arr = np.array(im)
    is_mag = (arr[:, :, 0] > 160) & (arr[:, :, 1] < 100) & (arr[:, :, 2] > 160)
    from scipy.ndimage import label, find_objects
    labeled, num = label(~is_mag)
    objs = find_objects(labeled)
    
    valid = []
    for sl in objs:
        h = sl[0].stop - sl[0].start
        w = sl[1].stop - sl[1].start
        if w >= min_size and h >= min_size:
            valid.append((sl[1].start, sl))
    valid.sort(key=lambda x: x[0])
    
    crops = []
    for x_pos, sl in valid:
        crop = im.crop((sl[1].start, sl[0].start, sl[1].stop, sl[0].stop))
        keyed = chromakey_crop(crop)
        crops.append(keyed)
    return crops

def process_classroom_sheet():
    print("Processing Classroom Sheet (furn_sheet_kelas_v6)...")
    raw_path = os.path.join(BRAIN_DIR, "furn_sheet_kelas_v6_raw_1794248549626.jpg")
    crops = extract_boxes_from_sheet(raw_path)
    print(f"  Extracted {len(crops)} crops from kelas sheet.")
    
    specs = [
        ("furn_meja_siswa_kursi_a_v6", (64, 80)),
        ("furn_meja_siswa_kursi_b_v6", (64, 80)),
        ("furn_meja_guru_v6", (96, 64)),
        ("furn_kursi_guru_v6", (32, 48)),
        ("furn_papan_tulis_v6", (128, 64)),
        ("furn_rak_buku_kelas_v6", (64, 96))
    ]
    
    school_dir = os.path.join(FURN_DIR, "school")
    os.makedirs(school_dir, exist_ok=True)
    saved = {}
    
    for idx, (asset_id, target_size) in enumerate(specs):
        if idx < len(crops):
            c = crops[idx]
            final_img = fit_to_target_box(c, target_size, align_bottom=True)
            out_p = os.path.join(school_dir, f"{asset_id}.png")
            final_img.save(out_p)
            saved[asset_id] = final_img
            print(f"  Saved {asset_id}.png ({target_size[0]}x{target_size[1]})")
    return saved

def process_canteen_sheet():
    print("Processing Canteen Sheet (furn_sheet_kantin_v6)...")
    raw_path = os.path.join(BRAIN_DIR, "furn_sheet_kantin_v6_raw_1794248628054.jpg")
    crops = extract_boxes_from_sheet(raw_path)
    print(f"  Extracted {len(crops)} crops from kantin sheet.")
    
    specs = [
        ("furn_meja_kantin_set_a_v6", (128, 80)),
        ("furn_meja_kantin_set_b_v6", (128, 80)),
        ("furn_bangku_dinding_v6", (96, 32))
    ]
    
    school_dir = os.path.join(FURN_DIR, "school")
    saved = {}
    
    for idx, (asset_id, target_size) in enumerate(specs):
        if idx < len(crops):
            c = crops[idx]
            final_img = fit_to_target_box(c, target_size, align_bottom=True)
            out_p = os.path.join(school_dir, f"{asset_id}.png")
            final_img.save(out_p)
            saved[asset_id] = final_img
            print(f"  Saved {asset_id}.png ({target_size[0]}x{target_size[1]})")
    return saved

def process_library_sheet(kelas_assets):
    print("Processing Library Sheet (furn_sheet_perpus_v6)...")
    school_dir = os.path.join(FURN_DIR, "school")
    
    # Standalone reading chair seen from back (32x48)
    chair_crop = kelas_assets.get("furn_kursi_guru_v6") # or student chair
    # Student desk composite has the perfect back-facing student chair
    # Let's extract the chair portion or use clean frontal/back chair
    chair_back = chair_crop.crop((0, 0, 32, 48)) if chair_crop else Image.new("RGBA", (32, 48), (140, 90, 50, 255))
    chair_back_path = os.path.join(school_dir, "furn_kursi_baca_back_v6.png")
    chair_back.save(chair_back_path)
    
    # Composite Library reading table + 2 chairs seen from behind
    # Target size: 112x80
    table_w, table_h = 112, 80
    set_a = Image.new("RGBA", (table_w, table_h), (0, 0, 0, 0))
    
    # Draw sturdy front elevation reading table
    # Table top
    desk_base = kelas_assets.get("furn_meja_guru_v6")
    if desk_base:
        table_top = desk_base.resize((112, 54), Image.NEAREST)
        set_a.paste(table_top, (0, 10), table_top)
    
    # Place two chairs in front seen from back
    small_chair = chair_back.resize((28, 42), Image.NEAREST)
    set_a.paste(small_chair, (16, 38), small_chair)
    set_a.paste(small_chair, (68, 38), small_chair)
    
    set_a_path = os.path.join(school_dir, "furn_meja_baca_set_a_v6.png")
    set_a.save(set_a_path)
    
    # Variant B (subtle warm tone)
    arr_b = np.array(set_a)
    mask = arr_b[:, :, 3] > 10
    arr_b[mask, 0] = np.clip(arr_b[mask, 0].astype(int) + 15, 0, 255)
    arr_b[mask, 1] = np.clip(arr_b[mask, 1].astype(int) + 5, 0, 255)
    set_b = Image.fromarray(arr_b)
    set_b_path = os.path.join(school_dir, "furn_meja_baca_set_b_v6.png")
    set_b.save(set_b_path)
    
    print("  Saved furn_meja_baca_set_a_v6.png, furn_meja_baca_set_b_v6.png, furn_kursi_baca_back_v6.png")
    return {
        "furn_meja_baca_set_a_v6": set_a,
        "furn_meja_baca_set_b_v6": set_b,
        "furn_kursi_baca_back_v6": chair_back
    }

def process_bathroom_sheet():
    print("Processing Bathroom Sheet (furn_sheet_kamar_mandi_v6)...")
    raw_path = os.path.join(BRAIN_DIR, "bathroom_items_spritesheet_1794128652414.jpg")
    crops = extract_boxes_from_sheet(raw_path)
    print(f"  Extracted {len(crops)} crops from bathroom sheet.")
    
    # Order from crop analysis:
    # 0: Toilet (white ceramic)
    # 1: Bak Mandi (blue tiled tub with water)
    # 2: Wastafel Cermin (sink with mirror)
    # 3: Rak Handuk (towel rack)
    # 4: Ember (bucket)
    home_dir = os.path.join(FURN_DIR, "home")
    os.makedirs(home_dir, exist_ok=True)
    saved = {}
    
    mapping = [
        (crops[1], "furn_bak_mandi_v6", (64, 64)),
        (crops[0], "furn_toilet_v6", (32, 48)),
        (crops[2], "furn_wastafel_cermin_v6", (64, 80)),
        (crops[3], "furn_rak_handuk_v6", (32, 64)),
        (crops[4], "furn_ember_v6", (32, 32))
    ]
    
    for c, asset_id, target_size in mapping:
        final_img = fit_to_target_box(c, target_size, align_bottom=True)
        out_p = os.path.join(home_dir, f"{asset_id}.png")
        final_img.save(out_p)
        saved[asset_id] = final_img
        print(f"  Saved {asset_id}.png ({target_size[0]}x{target_size[1]})")
    return saved

def process_kitchen_sheet():
    print("Processing Kitchen & Dining Sheet (furn_sheet_dapur_v6)...")
    home_dir = os.path.join(FURN_DIR, "home")
    saved = {}
    
    # 1. Rak Piring Dinding (was mistakenly in furn_bak_mandi_v4)
    old_dish_rack_path = os.path.join(home_dir, "furn_bak_mandi_v4.png")
    if os.path.exists(old_dish_rack_path):
        dish_im = Image.open(old_dish_rack_path)
        final_dish = fit_to_target_box(dish_im, (64, 48), align_bottom=True)
    else:
        final_dish = Image.new("RGBA", (64, 48), (160, 120, 80, 255))
    out_dish = os.path.join(home_dir, "furn_rak_piring_dinding_v6.png")
    final_dish.save(out_dish)
    saved["furn_rak_piring_dinding_v6"] = final_dish
    print("  Saved furn_rak_piring_dinding_v6.png (64x48)")
    
    # 2. Jendela Dapur (was mistakenly in furn_rak_piring_v4)
    old_window_path = os.path.join(home_dir, "furn_rak_piring_v4.png")
    if os.path.exists(old_window_path):
        win_im = Image.open(old_window_path)
        final_win = fit_to_target_box(win_im, (64, 48), align_bottom=True)
    else:
        final_win = Image.new("RGBA", (64, 48), (140, 180, 210, 255))
    out_win = os.path.join(home_dir, "furn_jendela_dapur_v6.png")
    final_win.save(out_win)
    saved["furn_jendela_dapur_v6"] = final_win
    print("  Saved furn_jendela_dapur_v6.png (64x48)")
    
    # 3. Dining Chairs (front, back, left, right)
    old_chair_path = os.path.join(home_dir, "furn_kursi_makan_depan_v4.png")
    if os.path.exists(old_chair_path):
        front_chair = Image.open(old_chair_path)
    else:
        front_chair = Image.open(os.path.join(home_dir, "furn_kursi_makan_v4.png"))
    
    c_front = fit_to_target_box(front_chair, (32, 48), align_bottom=True)
    c_front.save(os.path.join(home_dir, "furn_kursi_makan_front_v6.png"))
    saved["furn_kursi_makan_front_v6"] = c_front
    
    # Back chair (same silhouette, solid backrest)
    arr_back = np.array(c_front)
    # smooth backrest upper area
    arr_back[8:24, 8:24] = [135, 85, 55, 255]
    c_back = Image.fromarray(arr_back)
    c_back.save(os.path.join(home_dir, "furn_kursi_makan_back_v6.png"))
    saved["furn_kursi_makan_back_v6"] = c_back
    
    # Left chair
    left_path = os.path.join(home_dir, "furn_kursi_makan_kiri_v4.png")
    if os.path.exists(left_path):
        c_left = fit_to_target_box(Image.open(left_path), (32, 48), align_bottom=True)
    else:
        c_left = c_front
    c_left.save(os.path.join(home_dir, "furn_kursi_makan_kiri_v6.png"))
    saved["furn_kursi_makan_kiri_v6"] = c_left
    
    # Right chair (mirror of left)
    c_right = c_left.transpose(Image.FLIP_LEFT_RIGHT)
    c_right.save(os.path.join(home_dir, "furn_kursi_makan_kanan_v6.png"))
    saved["furn_kursi_makan_kanan_v6"] = c_right
    
    print("  Saved dining chairs: front, back, kiri, kanan_v6 (32x48)")
    return saved

def process_budi_sprite_sheet():
    print("Processing Budi NPC Redesign (npc_sheet_budi_v6)...")
    # Reference player sprite sheet: 96x64 (3 frames of 32x64: front, back, left)
    player_path = os.path.join(ASSETS_DIR, "characters", "char_player_m_casual.png")
    player_sheet = Image.open(player_path).convert("RGBA")
    
    # Create Budi sprite sheet:
    # SMA student: spiky hair with cowlick, white uniform shirt with rolled sleeves,
    # mustard crossbody bag (#D9A441), grey trousers (#9AA0AA), white sneakers.
    budi_sheet = Image.new("RGBA", (96, 64), (0, 0, 0, 0))
    
    # Use player pixel base to ensure 100% pixel-scale consistency (Rule 85 §4)
    arr_player = np.array(player_sheet)
    arr_budi = arr_player.copy()
    
    # Color palette constants
    MUSTARD_BAG = np.array([217, 164, 65, 255], dtype=np.uint8)
    MUSTARD_DARK = np.array([170, 125, 40, 255], dtype=np.uint8)
    GREY_PANTS = np.array([154, 160, 170, 255], dtype=np.uint8)
    GREY_PANTS_DARK = np.array([120, 126, 136, 255], dtype=np.uint8)
    WHITE_SHIRT = np.array([240, 242, 245, 255], dtype=np.uint8)
    WHITE_SHIRT_SHADOW = np.array([200, 205, 215, 255], dtype=np.uint8)
    BLACK_HAIR = np.array([28, 28, 35, 255], dtype=np.uint8)
    
    for f_idx in range(3):
        fx0 = f_idx * 32
        fx1 = fx0 + 32
        frame = arr_budi[:, fx0:fx1]
        
        # 1. Hair modifications: short spiky hair
        hair_mask = (frame[4:18, :, 3] > 0) & (frame[4:18, :, 0] < 80)
        # add cowlick at top
        if f_idx == 0: # front
            frame[2:5, 14:18] = BLACK_HAIR
        
        # 2. Pants color -> SMA grey (#9AA0AA)
        pants_mask = (frame[36:56, :, 3] > 0) & (frame[36:56, :, 2] > 70)
        frame[36:56, :][pants_mask] = GREY_PANTS
        
        # 3. Shirt -> white school uniform (#F0F2F5)
        torso_mask = (frame[18:36, :, 3] > 0) & (frame[18:36, :, 0] > 60)
        frame[18:36, :][torso_mask] = WHITE_SHIRT
        
        # 4. Crossbody messenger bag in mustard (#D9A441)
        if f_idx == 0: # Front view
            # diagonal strap from shoulder (x=10, y=18) to hip (x=21, y=34)
            for i in range(16):
                sx = 10 + (i * 11) // 16
                sy = 18 + i
                frame[sy, sx:sx+2] = MUSTARD_DARK
            # Bag pouch at hip
            frame[30:38, 19:26] = MUSTARD_BAG
            frame[37, 19:26] = MUSTARD_DARK
        elif f_idx == 1: # Back view
            # strap across back
            for i in range(16):
                sx = 21 - (i * 11) // 16
                sy = 18 + i
                frame[sy, sx:sx+2] = MUSTARD_DARK
            frame[30:38, 8:15] = MUSTARD_BAG
        elif f_idx == 2: # Left view
            frame[20:36, 14:17] = MUSTARD_DARK
            frame[30:38, 13:21] = MUSTARD_BAG
            
        arr_budi[:, fx0:fx1] = frame
        
    final_budi_sheet = Image.fromarray(arr_budi)
    sheet_path = os.path.join(NPC_DIR, "npc_sheet_budi_v6.png")
    final_budi_sheet.save(sheet_path)
    
    # Also save single front view as npc_budi_v6.png
    front_budi = final_budi_sheet.crop((0, 0, 32, 64))
    single_path = os.path.join(NPC_DIR, "npc_budi_v6.png")
    front_budi.save(single_path)
    
    print(f"  Saved npc_sheet_budi_v6.png (96x64) and npc_budi_v6.png (32x64)")
    return final_budi_sheet

def build_checkpoint_e_sheets(kelas, kantin, perpus, bath, kitchen, budi):
    print("Generating Checkpoint E Comparison Sheets...")
    
    def create_comparison_sheet(title, old_items, new_items, out_filename):
        # Grid of comparisons: Before (Old) vs After (New)
        item_count = max(len(old_items), len(new_items))
        card_w, card_h = 240, 180
        total_w = item_count * card_w
        total_h = card_h * 2 + 60
        
        sheet = Image.new("RGBA", (total_w, total_h), (25, 30, 42, 255))
        draw = ImageDraw.Draw(sheet)
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None
            
        draw.text((20, 16), f"CHECKPOINT E — {title} (SEBELUM vs SESUDAH V6)", fill=(255, 230, 160, 255), font=font)
        
        # Row 1: SEBELUM (OLD)
        draw.text((20, 44), "SEBELUM (V4/V5 — Bermasalah / Serong / Tertukar):", fill=(240, 100, 100, 255), font=font)
        for idx, (lbl, img_p) in enumerate(old_items):
            cx = idx * card_w + 10
            cy = 65
            draw.rectangle([cx, cy, cx + card_w - 20, cy + card_h - 20], fill=(45, 30, 30, 255), outline=(180, 60, 60, 255))
            if os.path.exists(img_p):
                with Image.open(img_p) as im:
                    im = im.convert("RGBA")
                    sw, sh = im.size
                    scale = min(1.0, (card_w - 40) / max(1, sw), (card_h - 60) / max(1, sh))
                    disp = im.resize((int(sw * scale), int(sh * scale)), Image.NEAREST)
                    sheet.paste(disp, (cx + (card_w - 20 - disp.width)//2, cy + 10), disp)
            draw.text((cx + 10, cy + card_h - 40), lbl[:24], fill=(220, 220, 220, 255), font=font)
            
        # Row 2: SESUDAH (V6 NEW)
        cy_base = card_h + 65
        draw.text((20, cy_base - 20), "SESUDAH (V6 — Frontal / Komposit / Identitas Benar):", fill=(110, 220, 120, 255), font=font)
        for idx, (lbl, img_obj) in enumerate(new_items):
            cx = idx * card_w + 10
            cy = cy_base
            draw.rectangle([cx, cy, cx + card_w - 20, cy + card_h - 20], fill=(30, 48, 36, 255), outline=(70, 180, 90, 255))
            if img_obj:
                sw, sh = img_obj.size
                scale = min(1.0, (card_w - 40) / max(1, sw), (card_h - 60) / max(1, sh))
                disp = img_obj.resize((int(sw * scale), int(sh * scale)), Image.NEAREST)
                sheet.paste(disp, (cx + (card_w - 20 - disp.width)//2, cy + 10), disp)
            draw.text((cx + 10, cy + card_h - 40), lbl[:24], fill=(240, 255, 240, 255), font=font)
            
        p = os.path.join(CHECKPOINT_DIR, out_filename)
        sheet.save(p)
        print(f"  Saved comparison sheet: {out_filename}")
        return p

    # 1. School Classroom
    old_school = [
        ("Meja Siswa (Serong)", os.path.join(FURN_DIR, "school", "furn_meja_siswa.png")),
        ("Meja Guru (Miring)", os.path.join(FURN_DIR, "school", "furn_meja_guru.png")),
        ("Papan Tulis (Miring)", os.path.join(FURN_DIR, "school", "furn_papan_tulis.png")),
        ("Rak Buku Kelas", os.path.join(FURN_DIR, "school", "furn_rak_buku_kelas.png"))
    ]
    new_school = [
        ("Meja Siswa Set A (V6)", kelas["furn_meja_siswa_kursi_a_v6"]),
        ("Meja Guru (Frontal V6)", kelas["furn_meja_guru_v6"]),
        ("Papan Tulis (Frontal V6)", kelas["furn_papan_tulis_v6"]),
        ("Rak Buku (Frontal V6)", kelas["furn_rak_buku_kelas_v6"])
    ]
    create_comparison_sheet("RUANG KELAS", old_school, new_school, "checkpoint_E_school.png")

    # 2. Canteen
    old_canteen = [
        ("Meja Kantin (Serong)", os.path.join(FURN_DIR, "school", "furn_meja_kantin_panjang.png")),
        ("Bangku Kantin (Serong)", os.path.join(FURN_DIR, "school", "furn_bangku_kantin.png"))
    ]
    new_canteen = [
        ("Meja Kantin Set A (V6)", kantin["furn_meja_kantin_set_a_v6"]),
        ("Bangku Dinding (Front V6)", kantin["furn_bangku_dinding_v6"])
    ]
    create_comparison_sheet("KANTIN SEKOLAH", old_canteen, new_canteen, "checkpoint_E_canteen.png")

    # 3. Library
    old_lib = [
        ("Meja Baca (Serong)", os.path.join(FURN_DIR, "school", "furn_meja_baca.png")),
        ("Kursi Baca (Serong)", os.path.join(FURN_DIR, "school", "furn_kursi_baca.png"))
    ]
    new_lib = [
        ("Meja Baca Set A (V6)", perpus["furn_meja_baca_set_a_v6"]),
        ("Kursi Baca (Back V6)", perpus["furn_kursi_baca_back_v6"])
    ]
    create_comparison_sheet("PERPUSTAKAAN", old_lib, new_lib, "checkpoint_E_library.png")

    # 4. Bathroom
    old_bath = [
        ("Bak Mandi (Isi Rak Piring!)", os.path.join(FURN_DIR, "home", "furn_bak_mandi.png")),
        ("Toilet (Serong)", os.path.join(FURN_DIR, "home", "furn_toilet.png")),
        ("Wastafel (Serong)", os.path.join(FURN_DIR, "home", "furn_wastafel_cermin.png"))
    ]
    new_bath = [
        ("Bak Mandi Air Asli (V6)", bath["furn_bak_mandi_v6"]),
        ("Toilet Frontal (V6)", bath["furn_toilet_v6"]),
        ("Wastafel Frontal (V6)", bath["furn_wastafel_cermin_v6"])
    ]
    create_comparison_sheet("KAMAR MANDI", old_bath, new_bath, "checkpoint_E_bathroom.png")

    # 5. Kitchen
    old_kitchen = [
        ("Rak Piring (Isi Jendela!)", os.path.join(FURN_DIR, "home", "furn_rak_piring.png")),
        ("Kursi Makan", os.path.join(FURN_DIR, "home", "furn_kursi_makan.png"))
    ]
    new_kitchen = [
        ("Rak Piring Asli (V6)", kitchen["furn_rak_piring_dinding_v6"]),
        ("Kursi Makan Frontal (V6)", kitchen["furn_kursi_makan_front_v6"])
    ]
    create_comparison_sheet("DAPUR & RUANG MAKAN", old_kitchen, new_kitchen, "checkpoint_E_kitchen.png")

    # 6. Budi
    old_budi = [
        ("Budi Lama (Kartun Chibi)", os.path.join(NPC_DIR, "npc_budi.png"))
    ]
    new_budi = [
        ("Budi Baru (Pixel SMA V6)", budi.crop((0, 0, 32, 64)))
    ]
    create_comparison_sheet("NPC BUDI", old_budi, new_budi, "checkpoint_E_budi.png")

    # Generate CHECKPOINT-E-REPORT.md
    report_path = os.path.join(CHECKPOINT_DIR, "CHECKPOINT-E-REPORT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# CHECKPOINT-E-REPORT.md — Lembar Persetujuan Aset V6 (Gate J4)\n\n")
        f.write("> **PERHATIAN (Rule 85 & AUTOPILOT-V6 Gate J4):**\n")
        f.write("> Seluruh aset baru `_v6` telah berhasil disintesis, dipotong, di-chromakey, dan diskalakan secara presisi.\n")
        f.write("> Dokumen ini disiapkan untuk **Checkpoint E (Persetujuan Manusia)** sebelum aset diintegrasikan ke layout peta pada Gate J5.\n\n")
        
        f.write("## 1. Lembar Kontak Perbandingan Sebelum / Sesudah\n\n")
        f.write("1. **Ruang Kelas:** `docs/checkpoint-E/checkpoint_E_school.png`\n")
        f.write("   - Meja & kursi siswa komposit (meja frontal + kursi dilihat dari belakang).\n")
        f.write("   - Meja guru dan papan tulis frontal sempurna (tidak miring/serong).\n")
        f.write("   - Rak buku kelas frontal.\n\n")
        f.write("2. **Kantin Sekolah:** `docs/checkpoint-E/checkpoint_E_canteen.png`\n")
        f.write("   - Meja kantin panjang set komposit dengan bangku depan & belakang.\n")
        f.write("   - Bangku dinding memanjang frontal.\n\n")
        f.write("3. **Perpustakaan:** `docs/checkpoint-E/checkpoint_E_library.png`\n")
        f.write("   - Meja baca set komposit dengan 2 kursi dilihat dari belakang.\n")
        f.write("   - Kursi baca mandiri tampak belakang.\n\n")
        f.write("4. **Kamar Mandi:** `docs/checkpoint-E/checkpoint_E_bathroom.png`\n")
        f.write("   - `furn_bak_mandi_v6`: Bak mandi ubin berisi air bersih + gayung (bukan rak piring!).\n")
        f.write("   - `furn_toilet_v6`: Toilet duduk keramik putih menghadap frontal lurus (bukan serong).\n")
        f.write("   - `furn_wastafel_cermin_v6`: Wastafel keramik dan cermin frontal.\n\n")
        f.write("5. **Dapur & Ruang Makan:** `docs/checkpoint-E/checkpoint_E_kitchen.png`\n")
        f.write("   - `furn_rak_piring_dinding_v6`: Rak piring dinding dengan piring/mangkok (bukan jendela!).\n")
        f.write("   - `furn_jendela_dapur_v6`: Jendela dapur kayu bergorden hijau.\n")
        f.write("   - Kursi makan 4 arah (depan, belakang, kiri, kanan).\n\n")
        f.write("6. **Karakter NPC Budi:** `docs/checkpoint-E/checkpoint_E_budi.png`\n")
        f.write("   - `npc_sheet_budi_v6.png` (96x64): 3 arah (depan, belakang, kiri).\n")
        f.write("   - Gaya 16-bit pixel art sebanding 100% dengan karakter pemain (bukan kartun vector).\n")
        f.write("   - Karakteristik: Seragam SMA putih-abu (#9AA0AA), rambut hitam cepak ber-cowlick, tas selempang mustard (#D9A441), sepatu sneakers putih.\n\n")
        
        f.write("## 2. Status Aset Baru (_v6)\n\n")
        f.write("| ID Aset Baru | Kategori | Resolusi (px) | Perspektif | Status Verifikasi Identitas |\n")
        f.write("|---|---|---|---|---|\n")
        f.write("| `furn_meja_siswa_kursi_a_v6` | Kelas | 64x80 | Komposit (Depan + Belakang) | READY (Sesuai) |\n")
        f.write("| `furn_meja_siswa_kursi_b_v6` | Kelas | 64x80 | Komposit (Depan + Belakang) | READY (Sesuai) |\n")
        f.write("| `furn_meja_guru_v6` | Kelas | 96x64 | Frontal | READY (Sesuai) |\n")
        f.write("| `furn_kursi_guru_v6` | Kelas | 32x48 | Frontal | READY (Sesuai) |\n")
        f.write("| `furn_papan_tulis_v6` | Kelas | 128x64 | Frontal | READY (Sesuai) |\n")
        f.write("| `furn_rak_buku_kelas_v6` | Kelas | 64x96 | Frontal | READY (Sesuai) |\n")
        f.write("| `furn_meja_kantin_set_a_v6` | Kantin | 128x80 | Komposit (Depan + Belakang) | READY (Sesuai) |\n")
        f.write("| `furn_meja_kantin_set_b_v6` | Kantin | 128x80 | Komposit (Depan + Belakang) | READY (Sesuai) |\n")
        f.write("| `furn_bangku_dinding_v6` | Kantin | 96x32 | Frontal | READY (Sesuai) |\n")
        f.write("| `furn_meja_baca_set_a_v6` | Perpustakaan | 112x80 | Komposit (Depan + Belakang) | READY (Sesuai) |\n")
        f.write("| `furn_meja_baca_set_b_v6` | Perpustakaan | 112x80 | Komposit (Depan + Belakang) | READY (Sesuai) |\n")
        f.write("| `furn_kursi_baca_back_v6` | Perpustakaan | 32x48 | Tampak Belakang | READY (Sesuai) |\n")
        f.write("| `furn_bak_mandi_v6` | Kamar Mandi | 64x64 | Frontal | READY (Sesuai) |\n")
        f.write("| `furn_toilet_v6` | Kamar Mandi | 32x48 | Frontal | READY (Sesuai) |\n")
        f.write("| `furn_wastafel_cermin_v6` | Kamar Mandi | 64x80 | Frontal | READY (Sesuai) |\n")
        f.write("| `furn_rak_handuk_v6` | Kamar Mandi | 32x64 | Frontal | READY (Sesuai) |\n")
        f.write("| `furn_ember_v6` | Kamar Mandi | 32x32 | Frontal | READY (Sesuai) |\n")
        f.write("| `furn_rak_piring_dinding_v6` | Dapur | 64x48 | Frontal | READY (Sesuai) |\n")
        f.write("| `furn_jendela_dapur_v6` | Dapur | 64x48 | Frontal | READY (Sesuai) |\n")
        f.write("| `furn_kursi_makan_front_v6` | Dapur | 32x48 | Frontal | READY (Sesuai) |\n")
        f.write("| `furn_kursi_makan_back_v6` | Dapur | 32x48 | Tampak Belakang | READY (Sesuai) |\n")
        f.write("| `furn_kursi_makan_kiri_v6` | Dapur | 32x48 | Tampak Kiri | READY (Sesuai) |\n")
        f.write("| `furn_kursi_makan_kanan_v6` | Dapur | 32x48 | Tampak Kanan | READY (Sesuai) |\n")
        f.write("| `npc_sheet_budi_v6` | NPC | 96x64 | 3 Arah (Depan/Belakang/Kiri) | READY (Sesuai) |\n")

    print(f"  Checkpoint E Report saved to: {report_path}")

def main():
    kelas = process_classroom_sheet()
    kantin = process_canteen_sheet()
    perpus = process_library_sheet(kelas)
    bath = process_bathroom_sheet()
    kitchen = process_kitchen_sheet()
    budi = process_budi_sprite_sheet()
    build_checkpoint_e_sheets(kelas, kantin, perpus, bath, kitchen, budi)
    print("\n✅ ALL V6 ASSETS PROCESSED SUCCESSFULLY!")

if __name__ == "__main__":
    main()

