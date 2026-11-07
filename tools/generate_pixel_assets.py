#!/usr/bin/env python3
"""
generate_pixel_assets.py — Procedural 16-bit Pixel Art Asset Generator for Life Journey.
Generates:
1. Secondary buildings: bld_rumah_pemain, bld_minimarket, bld_toko_kosmetik, bld_spbu, bld_game_center
2. NPC Spritesheets: npc_sheet_family, npc_sheet_friends, npc_sheet_vendors (96x64: 3f @ 32x64)
3. Environment Props: prop_tree_large, prop_tree_small, prop_bush, prop_street_lamp, prop_bench, prop_trashcan, prop_flowerpot

All assets strictly use the 32-color palette in assets/palette.json,
have binary alpha (0 or 255), and pass validate_asset.py.
"""

import os
import json
import numpy as np
from PIL import Image, ImageDraw

# Color constants from assets/palette.json
CREAM_LIGHT = (247, 238, 218, 255)  # #F7EEDA
CREAM_MID   = (233, 216, 180, 255)  # #E9D8B4
OFF_WHITE   = (251, 246, 234, 255)  # #FBF6EA
PARCHMENT   = (240, 228, 200, 255)  # #F0E4C8
TAN         = (184, 168, 138, 255)  # #B8A88A
SAND        = (232, 201, 168, 255)  # #E8C9A8
WHEAT       = (212, 184, 144, 255)  # #D4B890
KHAKI       = (160, 144, 96, 255)   # #A09060

GREEN_LIGHT = (165, 190, 147, 255)  # #A5BE93
GREEN_MID   = (111, 146, 98, 255)   # #6F9262
GREEN_DARK  = (68, 96, 63, 255)     # #44603F
DARK_GREEN  = (61, 82, 54, 255)     # #3D5236
FOREST      = (74, 107, 64, 255)    # #4A6B40
SAGE        = (139, 150, 128, 255)  # #8B9680

BROWN_LIGHT = (201, 162, 122, 255)  # #C9A27A
BROWN_MID   = (154, 111, 76, 255)   # #9A6F4C
BROWN_DARK  = (94, 63, 42, 255)     # #5E3F2A
DARK_BROWN  = (42, 31, 26, 255)     # #2A1F1A
SIENNA      = (107, 74, 48, 255)    # #6B4A30

NAVY_MID    = (52, 69, 107, 255)    # #34456B
NAVY_DARK   = (31, 42, 68, 255)     # #1F2A44
NAVY_DEEP   = (18, 26, 46, 255)     # #121A2E
DEEP_NAVY   = (40, 52, 79, 255)     # #28344F
MIDNIGHT    = (22, 32, 56, 255)     # #162038
GREY_BLUE   = (122, 128, 144, 255)  # #7A8090
GREY_LIGHT  = (154, 160, 170, 255)  # #9AA0AA
SLATE       = (80, 88, 96, 255)     # #505860

TERRACOTTA  = (192, 101, 74, 255)   # #C0654A
TERRA_DARK  = (158, 74, 51, 255)    # #9E4A33
BURNT       = (139, 74, 54, 255)    # #8B4A36

GOLD        = (217, 164, 65, 255)   # #D9A441
AMBER       = (196, 131, 46, 255)   # #C4832E

TRANSPARENT = (0, 0, 0, 0)

OUT_DIR_BLD = "assets/buildings"
OUT_DIR_NPC = "assets/npcs"
OUT_DIR_PROP = "assets/props"

# ========================================================
# 1. BUILDINGS GENERATION
# ========================================================

def generate_house():
    """bld_rumah_pemain: 288x160 (9x5 tiles). Indonesian residential home."""
    w, h = 288, 160
    img = Image.new('RGBA', (w, h), TRANSPARENT)
    draw = ImageDraw.Draw(img)

    # 1. Base foundation / sidewalk step (touches bottom row, covers >= 90% width)
    base_x1, base_x2 = 12, 276
    draw.rectangle([base_x1, 148, base_x2, 159], fill=SLATE, outline=DARK_BROWN)
    draw.rectangle([base_x1 + 4, 142, base_x2 - 4, 148], fill=GREY_LIGHT, outline=DARK_BROWN)

    # 2. House Main Walls (Cream stucco)
    wall_x1, wall_x2 = 24, 264
    wall_y1, wall_y2 = 64, 142
    draw.rectangle([wall_x1, wall_y1, wall_x2, wall_y2], fill=CREAM_LIGHT, outline=DARK_BROWN)
    # Wall base wainscot
    draw.rectangle([wall_x1 + 1, 130, wall_x2 - 1, wall_y2 - 1], fill=CREAM_MID)

    # 3. Pitched Terracotta Roof
    # Main roof triangle / trapezoid
    roof_y_top = 16
    roof_y_bot = 64
    roof_points = [
        (wall_x1 - 10, roof_y_bot),
        (w // 2, roof_y_top),
        (wall_x2 + 10, roof_y_bot)
    ]
    draw.polygon(roof_points, fill=TERRACOTTA, outline=DARK_BROWN)
    # Roof ridge
    draw.rectangle([wall_x1 - 12, roof_y_bot - 4, wall_x2 + 12, roof_y_bot + 2], fill=BURNT, outline=DARK_BROWN)
    # Shingle horizontal texture lines
    for ry in range(roof_y_top + 10, roof_y_bot - 6, 8):
        y_progress = (ry - roof_y_top) / (roof_y_bot - roof_y_top)
        span_left = int(w // 2 - (w // 2 - (wall_x1 - 8)) * y_progress)
        span_right = int(w // 2 + ((wall_x2 + 8) - w // 2) * y_progress)
        draw.line([(span_left, ry), (span_right, ry)], fill=TERRA_DARK, width=2)
    # Roof peak finial
    draw.rectangle([w // 2 - 4, roof_y_top - 4, w // 2 + 4, roof_y_top + 4], fill=TERRA_DARK, outline=DARK_BROWN)

    # 4. Front Porch (Teras) in Center-Left (x: 96 to 192)
    porch_x1, porch_x2 = 96, 192
    draw.rectangle([porch_x1 - 4, 56, porch_x2 + 4, 68], fill=TERRACOTTA, outline=DARK_BROWN)
    # Wooden porch pillars
    draw.rectangle([porch_x1 + 2, 68, porch_x1 + 10, 142], fill=BROWN_MID, outline=DARK_BROWN)
    draw.rectangle([porch_x2 - 10, 68, porch_x2 - 2, 142], fill=BROWN_MID, outline=DARK_BROWN)

    # 5. Front Door (Center porch: x: 128 to 160)
    door_x1, door_x2 = 130, 158
    door_y1, door_y2 = 84, 142
    draw.rectangle([door_x1, door_y1, door_x2, door_y2], fill=BROWN_DARK, outline=DARK_BROWN)
    draw.rectangle([door_x1 + 3, door_y1 + 4, door_x1 + 12, door_y1 + 24], fill=BROWN_MID)
    draw.rectangle([door_x2 - 12, door_y1 + 4, door_x2 - 3, door_y1 + 24], fill=BROWN_MID)
    draw.rectangle([door_x1 + 3, door_y1 + 30, door_x1 + 12, door_y2 - 4], fill=BROWN_MID)
    draw.rectangle([door_x2 - 12, door_y1 + 30, door_x2 - 3, door_y2 - 4], fill=BROWN_MID)
    # Brass door knob
    draw.rectangle([door_x2 - 7, door_y1 + 26, door_x2 - 5, door_y1 + 30], fill=GOLD)

    # 6. Windows (Left and Right Wings)
    # Left window
    draw.rectangle([48, 86, 84, 122], fill=NAVY_DEEP, outline=DARK_BROWN)
    draw.rectangle([52, 90, 80, 118], fill=GREY_BLUE)
    draw.line([(66, 90), (66, 118)], fill=CREAM_LIGHT, width=2)
    draw.line([(52, 104), (80, 104)], fill=CREAM_LIGHT, width=2)
    # Window shutters
    draw.rectangle([40, 86, 48, 122], fill=BROWN_MID, outline=DARK_BROWN)
    draw.rectangle([84, 86, 92, 122], fill=BROWN_MID, outline=DARK_BROWN)

    # Right window
    draw.rectangle([204, 86, 240, 122], fill=NAVY_DEEP, outline=DARK_BROWN)
    draw.rectangle([208, 90, 236, 118], fill=GREY_BLUE)
    draw.line([(222, 90), (222, 118)], fill=CREAM_LIGHT, width=2)
    draw.line([(208, 104), (236, 104)], fill=CREAM_LIGHT, width=2)
    draw.rectangle([196, 86, 204, 122], fill=BROWN_MID, outline=DARK_BROWN)
    draw.rectangle([240, 86, 248, 122], fill=BROWN_MID, outline=DARK_BROWN)

    # 7. Porch Plants / Clay Pots
    draw.rectangle([102, 124, 116, 142], fill=TERRACOTTA, outline=DARK_BROWN)
    draw.ellipse([100, 110, 118, 126], fill=GREEN_MID, outline=DARK_GREEN)
    draw.rectangle([172, 124, 186, 142], fill=TERRACOTTA, outline=DARK_BROWN)
    draw.ellipse([170, 110, 188, 126], fill=GREEN_MID, outline=DARK_GREEN)

    return img

def generate_minimarket():
    """bld_minimarket: 256x160 (8x5 tiles). Modern commercial convenience store."""
    w, h = 256, 160
    img = Image.new('RGBA', (w, h), TRANSPARENT)
    draw = ImageDraw.Draw(img)

    # 1. Base sidewalk step (touches bottom row)
    base_x1, base_x2 = 8, 248
    draw.rectangle([base_x1, 148, base_x2, 159], fill=SLATE, outline=DARK_BROWN)
    draw.rectangle([base_x1 + 4, 140, base_x2 - 4, 148], fill=GREY_LIGHT, outline=DARK_BROWN)

    # 2. Building Main Block (Off-white / light cream)
    bld_x1, bld_x2 = 16, 240
    bld_y1, bld_y2 = 40, 140
    draw.rectangle([bld_x1, bld_y1, bld_x2, bld_y2], fill=OFF_WHITE, outline=DARK_BROWN)

    # 3. Upper Facade & Brand Signboard
    draw.rectangle([bld_x1, bld_y1, bld_x2, bld_y1 + 32], fill=NAVY_MID, outline=DARK_BROWN)
    # Red & Yellow branding stripe
    draw.rectangle([bld_x1 + 1, bld_y1 + 24, bld_x2 - 1, bld_y1 + 28], fill=TERRACOTTA)
    draw.rectangle([bld_x1 + 1, bld_y1 + 28, bld_x2 - 1, bld_y1 + 32], fill=GOLD)
    # Store Name "MINI MART" text placeholder graphic
    draw.rectangle([bld_x1 + 40, bld_y1 + 6, bld_x2 - 40, bld_y1 + 22], fill=OFF_WHITE, outline=NAVY_DEEP)
    # Letter-like pixel blocks
    for bx in range(bld_x1 + 52, bld_x2 - 50, 16):
        draw.rectangle([bx, bld_y1 + 10, bx + 8, bld_y1 + 18], fill=TERRACOTTA)

    # 4. Striped Awning (Canopy) below sign
    awn_y1, awn_y2 = bld_y1 + 32, bld_y1 + 44
    draw.rectangle([bld_x1 - 4, awn_y1, bld_x2 + 4, awn_y2], fill=NAVY_MID, outline=DARK_BROWN)
    # Stripes
    stripe_colors = [NAVY_MID, OFF_WHITE, TERRACOTTA, OFF_WHITE]
    for i, sx in enumerate(range(bld_x1 - 4, bld_x2 + 4, 12)):
        c = stripe_colors[i % len(stripe_colors)]
        draw.rectangle([sx, awn_y1 + 1, sx + 12, awn_y2 - 1], fill=c)

    # 5. Large Glass Storefront Windows
    # Left Window (Beverage fridge displays)
    draw.rectangle([24, awn_y2 + 6, 112, 136], fill=NAVY_DEEP, outline=DARK_BROWN)
    draw.rectangle([28, awn_y2 + 10, 108, 132], fill=GREY_BLUE)
    # Drink cans shelves
    for sy in [awn_y2 + 16, awn_y2 + 24, awn_y2 + 32, awn_y2 + 40]:
        draw.line([(30, sy), (106, sy)], fill=GREY_LIGHT, width=1)
        for dx in range(32, 104, 6):
            c = TERRACOTTA if dx % 12 == 0 else (GREEN_MID if dx % 18 == 0 else GOLD)
            draw.rectangle([dx, sy - 5, dx + 4, sy - 1], fill=c)

    # Right Glass Window & Automatic Sliding Door (Center-Right: 120 to 180)
    door_x1, door_x2 = 124, 176
    draw.rectangle([door_x1, awn_y2 + 6, door_x2, 140], fill=NAVY_DEEP, outline=DARK_BROWN)
    draw.rectangle([door_x1 + 3, awn_y2 + 10, door_x2 - 3, 138], fill=GREY_BLUE)
    # Door frames
    draw.line([((door_x1 + door_x2) // 2, awn_y2 + 6), ((door_x1 + door_x2) // 2, 138)], fill=OFF_WHITE, width=2)
    # Handles
    mid_x = (door_x1 + door_x2) // 2
    draw.rectangle([mid_x - 4, awn_y2 + 28, mid_x - 2, awn_y2 + 36], fill=GOLD)
    draw.rectangle([mid_x + 2, awn_y2 + 28, mid_x + 4, awn_y2 + 36], fill=GOLD)

    # Far Right Display Window (184 to 232)
    draw.rectangle([184, awn_y2 + 6, 232, 136], fill=NAVY_DEEP, outline=DARK_BROWN)
    draw.rectangle([188, awn_y2 + 10, 228, 132], fill=GREY_BLUE)
    for sy in [awn_y2 + 18, awn_y2 + 30]:
        draw.line([(190, sy), (226, sy)], fill=GREY_LIGHT, width=1)
        for sx in range(192, 224, 8):
            draw.rectangle([sx, sy - 6, sx + 5, sy - 1], fill=GOLD)

    # Rooftop AC units
    draw.rectangle([36, 24, 68, 40], fill=GREY_LIGHT, outline=DARK_BROWN)
    draw.rectangle([180, 26, 216, 40], fill=GREY_LIGHT, outline=DARK_BROWN)

    return img

def generate_cosmetics():
    """bld_toko_kosmetik: 224x160 (7x5 tiles). Boutique cosmetic & health store."""
    w, h = 224, 160
    img = Image.new('RGBA', (w, h), TRANSPARENT)
    draw = ImageDraw.Draw(img)

    # 1. Base sidewalk step (touches bottom row)
    base_x1, base_x2 = 8, 216
    draw.rectangle([base_x1, 148, base_x2, 159], fill=SLATE, outline=DARK_BROWN)
    draw.rectangle([base_x1 + 4, 140, base_x2 - 4, 148], fill=GREY_LIGHT, outline=DARK_BROWN)

    # 2. Main Wall (Pastel cream / warm tan)
    wall_x1, wall_x2 = 16, 208
    wall_y1, wall_y2 = 48, 140
    draw.rectangle([wall_x1, wall_y1, wall_x2, wall_y2], fill=CREAM_LIGHT, outline=DARK_BROWN)

    # 3. Header Pediment & Signboard
    draw.rectangle([wall_x1 - 4, wall_y1, wall_x2 + 4, wall_y1 + 28], fill=TERRACOTTA, outline=DARK_BROWN)
    # Gold border
    draw.rectangle([wall_x1 + 2, wall_y1 + 4, wall_x2 - 2, wall_y1 + 24], fill=BURNT, outline=GOLD)
    # Sign text "CANTIK" / "BEAUTY"
    for bx in range(wall_x1 + 40, wall_x2 - 40, 16):
        draw.rectangle([bx, wall_y1 + 8, bx + 10, wall_y1 + 20], fill=GOLD)

    # 4. Scalloped Awning
    awn_y1, awn_y2 = wall_y1 + 28, wall_y1 + 40
    for sx in range(wall_x1 - 4, wall_x2 + 4, 16):
        draw.rectangle([sx, awn_y1, sx + 16, awn_y2], fill=TERRA_DARK if (sx // 16) % 2 == 0 else CREAM_LIGHT, outline=DARK_BROWN)

    # 5. Boutique Display Windows
    # Left showcase
    draw.rectangle([28, awn_y2 + 6, 96, 136], fill=NAVY_DEEP, outline=DARK_BROWN)
    draw.rectangle([32, awn_y2 + 10, 92, 132], fill=PARCHMENT)
    # Perfume bottles display
    for py in [awn_y2 + 20, awn_y2 + 36]:
        draw.line([(34, py), (90, py)], fill=GOLD, width=1)
        draw.rectangle([40, py - 8, 48, py - 1], fill=TERRACOTTA)
        draw.rectangle([56, py - 10, 64, py - 1], fill=AMBER)
        draw.rectangle([72, py - 8, 80, py - 1], fill=GREEN_LIGHT)

    # Right Glass Door (116 to 164)
    door_x1, door_x2 = 120, 168
    draw.rectangle([door_x1, awn_y2 + 6, door_x2, 140], fill=BROWN_DARK, outline=DARK_BROWN)
    draw.rectangle([door_x1 + 4, awn_y2 + 10, door_x2 - 4, 138], fill=GREY_BLUE)
    draw.rectangle([door_x1 + 8, awn_y2 + 30, door_x1 + 10, awn_y2 + 42], fill=GOLD)

    # Decorative planters beside door
    draw.rectangle([100, 120, 114, 140], fill=TERRACOTTA, outline=DARK_BROWN)
    draw.ellipse([98, 106, 116, 122], fill=GREEN_LIGHT, outline=DARK_GREEN)
    draw.rectangle([174, 120, 188, 140], fill=TERRACOTTA, outline=DARK_BROWN)
    draw.ellipse([172, 106, 190, 122], fill=GREEN_LIGHT, outline=DARK_GREEN)

    return img

def generate_spbu():
    """bld_spbu: 320x160 (10x5 tiles). Gas station canopy with pumps & kiosk."""
    w, h = 320, 160
    img = Image.new('RGBA', (w, h), TRANSPARENT)
    draw = ImageDraw.Draw(img)

    # 1. Base concrete island (touches bottom row, covers >= 90% width)
    base_x1, base_x2 = 12, 308
    draw.rectangle([base_x1, 148, base_x2, 159], fill=SLATE, outline=DARK_BROWN)
    draw.rectangle([base_x1 + 4, 140, base_x2 - 4, 148], fill=GREY_LIGHT, outline=DARK_BROWN)

    # 2. Canopy Pillars
    # 2 large red/white pillars holding up canopy
    pillar_left_x = 72
    pillar_right_x = 248
    draw.rectangle([pillar_left_x - 8, 44, pillar_left_x + 8, 140], fill=OFF_WHITE, outline=DARK_BROWN)
    draw.rectangle([pillar_left_x - 8, 112, pillar_left_x + 8, 140], fill=TERRACOTTA)
    draw.rectangle([pillar_right_x - 8, 44, pillar_right_x + 8, 140], fill=OFF_WHITE, outline=DARK_BROWN)
    draw.rectangle([pillar_right_x - 8, 112, pillar_right_x + 8, 140], fill=TERRACOTTA)

    # 3. Canopy Roof
    canopy_x1, canopy_x2 = 16, 304
    canopy_y1, canopy_y2 = 16, 44
    draw.rectangle([canopy_x1, canopy_y1, canopy_x2, canopy_y2], fill=OFF_WHITE, outline=DARK_BROWN)
    # Red fascia stripe
    draw.rectangle([canopy_x1 + 1, canopy_y1 + 4, canopy_x2 - 1, canopy_y1 + 18], fill=TERRACOTTA)
    # Under-canopy recessed lights
    for lx in range(canopy_x1 + 32, canopy_x2 - 20, 48):
        draw.rectangle([lx, canopy_y2 - 3, lx + 16, canopy_y2], fill=GOLD)

    # 4. Small Kiosk in Center-Left (128 to 192)
    kiosk_x1, kiosk_x2 = 132, 188
    kiosk_y1, kiosk_y2 = 64, 140
    draw.rectangle([kiosk_x1, kiosk_y1, kiosk_x2, kiosk_y2], fill=OFF_WHITE, outline=DARK_BROWN)
    draw.rectangle([kiosk_x1, kiosk_y1, kiosk_x2, kiosk_y1 + 12], fill=TERRACOTTA)
    # Kiosk glass window & cashier
    draw.rectangle([kiosk_x1 + 6, kiosk_y1 + 18, kiosk_x2 - 6, kiosk_y1 + 48], fill=GREY_BLUE, outline=DARK_BROWN)
    # Door
    draw.rectangle([kiosk_x1 + 14, kiosk_y1 + 48, kiosk_x2 - 14, kiosk_y2], fill=NAVY_MID, outline=DARK_BROWN)

    # 5. Twin Fuel Dispensing Pumps (Left Pump: 64, Right Pump: 240)
    def draw_pump(px):
        # Concrete pump base
        draw.rectangle([px - 18, 134, px + 18, 140], fill=SLATE, outline=DARK_BROWN)
        # Pump body
        draw.rectangle([px - 14, 76, px + 14, 134], fill=OFF_WHITE, outline=DARK_BROWN)
        # Red top casing
        draw.rectangle([px - 14, 76, px + 14, 92], fill=TERRACOTTA, outline=DARK_BROWN)
        # Digital readout display
        draw.rectangle([px - 10, 96, px + 10, 110], fill=MIDNIGHT)
        draw.rectangle([px - 8, 98, px + 8, 103], fill=GOLD)
        draw.rectangle([px - 8, 105, px + 8, 108], fill=GREEN_LIGHT)
        # Fuel nozzle and hose on sides
        draw.line([(px - 14, 90), (px - 17, 104), (px - 17, 126), (px - 14, 128)], fill=DARK_BROWN, width=2)
        draw.line([(px + 14, 90), (px + 17, 104), (px + 17, 126), (px + 14, 128)], fill=DARK_BROWN, width=2)

    draw_pump(72)
    draw_pump(248)

    # 6. Price Totem / Pillar Sign on Far Right
    totem_x = 292
    draw.rectangle([totem_x - 10, 56, totem_x + 10, 140], fill=NAVY_DEEP, outline=DARK_BROWN)
    draw.rectangle([totem_x - 8, 60, totem_x + 8, 72], fill=TERRACOTTA)
    # Price numbers glowing
    draw.rectangle([totem_x - 6, 78, totem_x + 6, 84], fill=GOLD)
    draw.rectangle([totem_x - 6, 88, totem_x + 6, 94], fill=GREEN_LIGHT)

    return img

def generate_game_center():
    """bld_game_center: 256x160 (8x5 tiles). Arcade / Gaming center."""
    w, h = 256, 160
    img = Image.new('RGBA', (w, h), TRANSPARENT)
    draw = ImageDraw.Draw(img)

    # 1. Base sidewalk step (touches bottom row)
    base_x1, base_x2 = 10, 246
    draw.rectangle([base_x1, 148, base_x2, 159], fill=SLATE, outline=DARK_BROWN)
    draw.rectangle([base_x1 + 4, 140, base_x2 - 4, 148], fill=GREY_LIGHT, outline=DARK_BROWN)

    # 2. Main Wall (Dark navy brick)
    bld_x1, bld_x2 = 18, 238
    bld_y1, bld_y2 = 38, 140
    draw.rectangle([bld_x1, bld_y1, bld_x2, bld_y2], fill=NAVY_DARK, outline=DARK_BROWN)
    # Brick pattern texture
    for by in range(bld_y1 + 40, bld_y2 - 10, 10):
        draw.line([(bld_x1, by), (bld_x2, by)], fill=NAVY_MID, width=1)

    # 3. Large Retro Neon Marquee "GAME ZONE"
    draw.rectangle([bld_x1 - 4, bld_y1, bld_x2 + 4, bld_y1 + 34], fill=NAVY_DEEP, outline=DARK_BROWN)
    draw.rectangle([bld_x1, bld_y1 + 4, bld_x2, bld_y1 + 30], fill=MIDNIGHT, outline=AMBER)
    # Neon letters / pixel blocks
    for bx in range(bld_x1 + 24, bld_x2 - 24, 18):
        c = GOLD if bx % 36 == 0 else TERRACOTTA
        draw.rectangle([bx, bld_y1 + 8, bx + 12, bld_y1 + 26], fill=c, outline=AMBER)

    # 4. Pixelated Joystick / Controller Icon in Center of Marquee
    ctrl_cx = (bld_x1 + bld_x2) // 2
    draw.rectangle([ctrl_cx - 14, bld_y1 + 8, ctrl_cx + 14, bld_y1 + 26], fill=GOLD, outline=NAVY_DEEP)

    # 5. Entrance Double Doors in Center
    door_x1, door_x2 = 104, 152
    draw.rectangle([door_x1, 80, door_x2, 140], fill=NAVY_DEEP, outline=AMBER)
    draw.rectangle([door_x1 + 3, 84, door_x2 - 3, 138], fill=MIDNIGHT)
    # Glass glow
    draw.rectangle([door_x1 + 6, 88, (door_x1 + door_x2) // 2 - 2, 120], fill=GREY_BLUE)
    draw.rectangle([(door_x1 + door_x2) // 2 + 2, 88, door_x2 - 6, 120], fill=GREY_BLUE)
    draw.rectangle([(door_x1 + door_x2) // 2 - 4, 108, (door_x1 + door_x2) // 2 + 4, 114], fill=GOLD)

    # 6. Showcase Windows with Arcade Machines Silhouettes
    # Left Window
    draw.rectangle([28, 80, 92, 136], fill=NAVY_DEEP, outline=AMBER)
    draw.rectangle([32, 84, 88, 132], fill=MIDNIGHT)
    # Arcade cabinet 1
    draw.polygon([(36, 128), (36, 96), (46, 92), (48, 102), (44, 112), (48, 128)], fill=TERRACOTTA)
    draw.rectangle([38, 96, 44, 104], fill=GOLD)  # screen
    # Arcade cabinet 2
    draw.polygon([(56, 128), (56, 96), (66, 92), (68, 102), (64, 112), (68, 128)], fill=GREEN_MID)
    draw.rectangle([58, 96, 64, 104], fill=GREEN_LIGHT)

    # Right Window
    draw.rectangle([164, 80, 228, 136], fill=NAVY_DEEP, outline=AMBER)
    draw.rectangle([168, 84, 224, 132], fill=MIDNIGHT)
    # Crane game / claw machine
    draw.rectangle([174, 92, 198, 128], fill=AMBER, outline=GOLD)
    draw.rectangle([178, 96, 194, 114], fill=GREY_BLUE)  # glass

    return img

# ========================================================
# 2. NPC SPRITESHEETS GENERATION (96x64: 3f @ 32x64)
# ========================================================

def generate_npc_family():
    """npc_sheet_family: Ibu (Mother). Batik skirt, cream kebaya, neat bun hair."""
    w, h = 96, 64
    img = Image.new('RGBA', (w, h), TRANSPARENT)
    draw = ImageDraw.Draw(img)

    # Frame 0: Facing Down (x: 0..32)
    # Hair bun
    draw.rectangle([12, 10, 20, 16], fill=DARK_BROWN)
    # Head & face
    draw.rectangle([10, 16, 22, 28], fill=SAND)
    # Eyes & smile
    draw.rectangle([13, 20, 15, 22], fill=DARK_BROWN)
    draw.rectangle([17, 20, 19, 22], fill=DARK_BROWN)
    draw.rectangle([14, 25, 18, 26], fill=TERRACOTTA)
    # Cream Kebaya blouse
    draw.rectangle([9, 28, 23, 44], fill=CREAM_LIGHT, outline=BROWN_MID)
    draw.rectangle([15, 30, 17, 44], fill=GOLD)  # broach/center
    # Batik Skirt (Terracotta & Gold)
    draw.rectangle([10, 44, 22, 59], fill=TERRACOTTA, outline=DARK_BROWN)
    for by in range(46, 58, 4):
        draw.line([(11, by), (21, by)], fill=GOLD, width=1)
    # Feet/sandals touching bottom row
    draw.rectangle([11, 59, 14, 63], fill=BROWN_DARK)
    draw.rectangle([18, 59, 21, 63], fill=BROWN_DARK)

    # Frame 1: Facing Up (x: 32..64)
    fx = 32
    # Hair bun (more prominent from back)
    draw.rectangle([fx + 11, 10, fx + 21, 18], fill=DARK_BROWN)
    draw.rectangle([fx + 10, 16, fx + 22, 28], fill=DARK_BROWN)
    # Back of Kebaya
    draw.rectangle([fx + 9, 28, fx + 23, 44], fill=CREAM_LIGHT, outline=BROWN_MID)
    # Batik Skirt
    draw.rectangle([fx + 10, 44, fx + 22, 59], fill=TERRACOTTA, outline=DARK_BROWN)
    for by in range(46, 58, 4):
        draw.line([(fx + 11, by), (fx + 21, by)], fill=GOLD, width=1)
    # Feet
    draw.rectangle([fx + 11, 59, fx + 14, 63], fill=BROWN_DARK)
    draw.rectangle([fx + 18, 59, fx + 21, 63], fill=BROWN_DARK)

    # Frame 2: Facing Left (x: 64..96)
    fx = 64
    # Hair bun on right side of head
    draw.rectangle([fx + 19, 14, fx + 23, 20], fill=DARK_BROWN)
    draw.rectangle([fx + 11, 14, fx + 20, 28], fill=DARK_BROWN)
    # Profile face
    draw.rectangle([fx + 9, 18, fx + 14, 26], fill=SAND)
    draw.rectangle([fx + 10, 21, fx + 12, 23], fill=DARK_BROWN)  # eye
    # Kebaya
    draw.rectangle([fx + 10, 28, fx + 21, 44], fill=CREAM_LIGHT, outline=BROWN_MID)
    # Batik Skirt
    draw.rectangle([fx + 11, 44, fx + 20, 59], fill=TERRACOTTA, outline=DARK_BROWN)
    for by in range(46, 58, 4):
        draw.line([(fx + 12, by), (fx + 19, by)], fill=GOLD, width=1)
    # Feet
    draw.rectangle([fx + 11, 59, fx + 16, 63], fill=BROWN_DARK)

    return img

def generate_npc_friends():
    """npc_sheet_friends: Budi (SMA Friend). High school uniform (white shirt, grey pants)."""
    w, h = 96, 64
    img = Image.new('RGBA', (w, h), TRANSPARENT)
    draw = ImageDraw.Draw(img)

    # Frame 0: Facing Down
    # Spiky brown hair
    draw.rectangle([11, 12, 21, 18], fill=BROWN_DARK)
    draw.rectangle([9, 14, 12, 19], fill=BROWN_DARK)
    draw.rectangle([20, 14, 23, 19], fill=BROWN_DARK)
    # Face
    draw.rectangle([11, 18, 21, 28], fill=SAND)
    draw.rectangle([13, 21, 15, 23], fill=DARK_BROWN)
    draw.rectangle([17, 21, 19, 23], fill=DARK_BROWN)
    # White SMA shirt & tie
    draw.rectangle([9, 28, 23, 42], fill=OFF_WHITE, outline=DARK_BROWN)
    draw.rectangle([15, 30, 17, 38], fill=GREY_BLUE)  # tie
    # Grey SMA trousers
    draw.rectangle([10, 42, 22, 58], fill=GREY_BLUE, outline=DARK_BROWN)
    draw.line([(16, 46), (16, 58)], fill=DARK_BROWN)
    # Sneakers touching bottom
    draw.rectangle([10, 58, 14, 63], fill=BROWN_MID)
    draw.rectangle([18, 58, 22, 63], fill=BROWN_MID)

    # Frame 1: Facing Up
    fx = 32
    draw.rectangle([fx + 10, 12, fx + 22, 26], fill=BROWN_DARK)
    # White shirt & dark green backpack
    draw.rectangle([fx + 9, 28, fx + 23, 42], fill=OFF_WHITE, outline=DARK_BROWN)
    draw.rectangle([fx + 11, 30, fx + 21, 42], fill=GREEN_DARK, outline=DARK_BROWN)
    # Grey trousers
    draw.rectangle([fx + 10, 42, fx + 22, 58], fill=GREY_BLUE, outline=DARK_BROWN)
    draw.line([(fx + 16, 46), (fx + 16, 58)], fill=DARK_BROWN)
    # Sneakers
    draw.rectangle([fx + 10, 58, fx + 14, 63], fill=BROWN_MID)
    draw.rectangle([fx + 18, 58, fx + 22, 63], fill=BROWN_MID)

    # Frame 2: Facing Left
    fx = 64
    draw.rectangle([fx + 12, 12, fx + 21, 26], fill=BROWN_DARK)
    draw.rectangle([fx + 9, 18, fx + 14, 26], fill=SAND)
    draw.rectangle([fx + 10, 21, fx + 12, 23], fill=DARK_BROWN)
    # Shirt & side backpack strap
    draw.rectangle([fx + 10, 28, fx + 21, 42], fill=OFF_WHITE, outline=DARK_BROWN)
    draw.rectangle([fx + 18, 30, fx + 22, 42], fill=GREEN_DARK)
    # Trousers
    draw.rectangle([fx + 11, 42, fx + 20, 58], fill=GREY_BLUE, outline=DARK_BROWN)
    # Sneakers
    draw.rectangle([fx + 10, 58, fx + 16, 63], fill=BROWN_MID)

    return img

def generate_npc_vendors():
    """npc_sheet_vendors: Pak Anto (Vendor / Attendant). Green polo, cap, khaki pants."""
    w, h = 96, 64
    img = Image.new('RGBA', (w, h), TRANSPARENT)
    draw = ImageDraw.Draw(img)

    # Frame 0: Facing Down
    # Cap (khaki/tan)
    draw.rectangle([10, 12, 22, 17], fill=KHAKI, outline=DARK_BROWN)
    draw.rectangle([8, 16, 24, 18], fill=KHAKI)  # visor
    # Face & moustache
    draw.rectangle([11, 18, 21, 28], fill=SAND)
    draw.rectangle([13, 20, 15, 22], fill=DARK_BROWN)
    draw.rectangle([17, 20, 19, 22], fill=DARK_BROWN)
    draw.rectangle([13, 24, 19, 26], fill=DARK_BROWN)  # moustache
    # Green polo shirt
    draw.rectangle([9, 28, 23, 42], fill=GREEN_MID, outline=DARK_BROWN)
    draw.rectangle([15, 29, 17, 34], fill=CREAM_LIGHT)  # collar
    # Brown pants
    draw.rectangle([10, 42, 22, 58], fill=BROWN_MID, outline=DARK_BROWN)
    draw.line([(16, 46), (16, 58)], fill=DARK_BROWN)
    # Work boots
    draw.rectangle([10, 58, 14, 63], fill=DARK_BROWN)
    draw.rectangle([18, 58, 22, 63], fill=DARK_BROWN)

    # Frame 1: Facing Up
    fx = 32
    draw.rectangle([fx + 10, 12, fx + 22, 26], fill=KHAKI, outline=DARK_BROWN)
    draw.rectangle([fx + 9, 28, fx + 23, 42], fill=GREEN_MID, outline=DARK_BROWN)
    draw.rectangle([fx + 10, 42, fx + 22, 58], fill=BROWN_MID, outline=DARK_BROWN)
    draw.line([(fx + 16, 46), (fx + 16, 58)], fill=DARK_BROWN)
    draw.rectangle([fx + 10, 58, fx + 14, 63], fill=DARK_BROWN)
    draw.rectangle([fx + 18, 58, fx + 22, 63], fill=DARK_BROWN)

    # Frame 2: Facing Left
    fx = 64
    draw.rectangle([fx + 12, 12, fx + 21, 24], fill=KHAKI, outline=DARK_BROWN)
    draw.rectangle([fx + 7, 16, fx + 14, 18], fill=KHAKI)  # cap visor to left
    draw.rectangle([fx + 10, 18, fx + 16, 27], fill=SAND)
    draw.rectangle([fx + 9, 23, fx + 12, 25], fill=DARK_BROWN)  # moustache profile
    draw.rectangle([fx + 10, 28, fx + 21, 42], fill=GREEN_MID, outline=DARK_BROWN)
    draw.rectangle([fx + 11, 42, fx + 20, 58], fill=BROWN_MID, outline=DARK_BROWN)
    draw.rectangle([fx + 10, 58, fx + 16, 63], fill=DARK_BROWN)

    return img

# ========================================================
# 3. PROPS & ENVIRONMENT DETAILS GENERATION
# ========================================================

def generate_prop_tree_large():
    """prop_tree_large: 64x96 (2x3 tiles). Lush tropical shade tree."""
    w, h = 64, 96
    img = Image.new('RGBA', (w, h), TRANSPARENT)
    draw = ImageDraw.Draw(img)

    # Trunk (brown textured, wide root flare at bottom)
    trunk_x1, trunk_x2 = 24, 40
    draw.rectangle([trunk_x1, 52, trunk_x2, 90], fill=BROWN_DARK, outline=DARK_BROWN)
    draw.rectangle([trunk_x1 + 4, 54, trunk_x2 - 4, 88], fill=BROWN_MID)
    # Root flare touching bottom row (90% width of base = 64 * 0.9 = 58px -> x: 2 to 62)
    draw.polygon([(20, 80), (trunk_x1, 56), (trunk_x2, 56), (44, 80), (62, 95), (2, 95)], fill=BROWN_DARK)
    draw.polygon([(24, 80), (28, 60), (36, 60), (40, 80), (54, 95), (10, 95)], fill=BROWN_MID)

    # Tree Foliage Canopy (overlapping lush green circles, spans x: 2 to 62)
    canopy_parts = [
        (2, 20, 42, 56, DARK_GREEN),
        (22, 20, 62, 56, GREEN_DARK),
        (6, 8, 58, 48, GREEN_MID),
        (12, 4, 52, 36, GREEN_LIGHT),
        (8, 24, 34, 44, GREEN_LIGHT),
        (30, 24, 56, 44, GREEN_LIGHT),
    ]
    for x1, y1, x2, y2, color in canopy_parts:
        draw.ellipse([x1, y1, x2, y2], fill=color, outline=DARK_GREEN)

    return img

def generate_prop_tree_small():
    """prop_tree_small: 64x64 (2x2 tiles). Medium garden flowering tree."""
    w, h = 64, 64
    img = Image.new('RGBA', (w, h), TRANSPARENT)
    draw = ImageDraw.Draw(img)

    # Trunk
    draw.rectangle([28, 36, 36, 58], fill=BROWN_MID, outline=DARK_BROWN)
    draw.polygon([(24, 50), (28, 40), (36, 40), (40, 50), (62, 63), (2, 63)], fill=BROWN_DARK)

    # Foliage (spans x: 2 to 62 = 60/64 = 93.7% width)
    draw.ellipse([2, 10, 62, 46], fill=GREEN_MID, outline=DARK_GREEN)
    draw.ellipse([8, 4, 56, 36], fill=GREEN_LIGHT, outline=DARK_GREEN)
    # Flowers (pink / cream dots)
    flowers = [(16, 14), (32, 10), (48, 16), (22, 26), (42, 24), (30, 20)]
    for fx, fy in flowers:
        draw.rectangle([fx, fy, fx + 3, fy + 3], fill=CREAM_LIGHT)
        draw.rectangle([fx + 1, fy + 1, fx + 2, fy + 2], fill=GOLD)

    return img

def generate_prop_bush():
    """prop_bush: 32x32. Decorative sidewalk flower shrub."""
    w, h = 32, 32
    img = Image.new('RGBA', (w, h), TRANSPARENT)
    draw = ImageDraw.Draw(img)

    # Spans x: 1 to 31 = 30/32 = 93.7% width
    draw.ellipse([1, 6, 31, 31], fill=GREEN_DARK, outline=DARK_GREEN)
    draw.ellipse([4, 8, 28, 28], fill=GREEN_MID)
    draw.ellipse([8, 10, 24, 22], fill=GREEN_LIGHT)
    # Flowers
    for fx, fy in [(8, 12), (20, 14), (14, 20)]:
        draw.rectangle([fx, fy, fx + 3, fy + 3], fill=TERRACOTTA)
        draw.rectangle([fx + 1, fy + 1, fx + 2, fy + 2], fill=GOLD)

    return img

def generate_prop_street_lamp():
    """prop_street_lamp: 32x64. Classic iron city street lamp."""
    w, h = 32, 64
    img = Image.new('RGBA', (w, h), TRANSPARENT)
    draw = ImageDraw.Draw(img)

    # Base platform touching bottom (spans x: 1 to 31 = 30/32 = 93.7% width)
    draw.rectangle([1, 58, 31, 63], fill=SLATE, outline=DARK_BROWN)
    draw.rectangle([6, 52, 26, 58], fill=NAVY_DEEP, outline=DARK_BROWN)
    # Vertical iron pole
    draw.rectangle([14, 16, 18, 52], fill=NAVY_MID, outline=DARK_BROWN)
    # Lamp head
    draw.rectangle([8, 10, 24, 16], fill=NAVY_DEEP, outline=DARK_BROWN)
    # Glowing lantern glass
    draw.rectangle([10, 16, 22, 26], fill=GOLD, outline=DARK_BROWN)
    draw.rectangle([12, 18, 20, 24], fill=CREAM_LIGHT)
    # Cap finial
    draw.polygon([(16, 4), (10, 10), (22, 10)], fill=NAVY_DEEP, outline=DARK_BROWN)

    return img

def generate_prop_bench():
    """prop_bench: 64x32 (2x1 tiles). Wooden sidewalk bench with iron legs."""
    w, h = 64, 32
    img = Image.new('RGBA', (w, h), TRANSPARENT)
    draw = ImageDraw.Draw(img)

    # Legs touching bottom
    draw.rectangle([6, 20, 12, 31], fill=NAVY_DEEP, outline=DARK_BROWN)
    draw.rectangle([52, 20, 58, 31], fill=NAVY_DEEP, outline=DARK_BROWN)
    # Base rail connecting legs (spans x: 2 to 62 = 60/64 = 93.7% width)
    draw.rectangle([2, 30, 62, 31], fill=DARK_BROWN)

    # Bench Seat slats (brown wood)
    draw.rectangle([2, 16, 62, 21], fill=BROWN_MID, outline=DARK_BROWN)
    # Bench Backrest slats
    draw.rectangle([4, 6, 60, 10], fill=BROWN_MID, outline=DARK_BROWN)
    draw.rectangle([4, 11, 60, 15], fill=BROWN_LIGHT, outline=DARK_BROWN)

    return img

def generate_prop_trashcan():
    """prop_trashcan: 32x32. Dual sorting public trash bin."""
    w, h = 32, 32
    img = Image.new('RGBA', (w, h), TRANSPARENT)
    draw = ImageDraw.Draw(img)

    # Base touching bottom
    draw.rectangle([2, 28, 30, 31], fill=DARK_BROWN)
    # Left bin (Green / Organic)
    draw.rectangle([4, 8, 15, 28], fill=GREEN_MID, outline=DARK_BROWN)
    draw.rectangle([3, 6, 16, 10], fill=GREEN_DARK, outline=DARK_BROWN)
    # Right bin (Navy / Inorganic)
    draw.rectangle([17, 8, 28, 28], fill=NAVY_MID, outline=DARK_BROWN)
    draw.rectangle([16, 6, 29, 10], fill=NAVY_DEEP, outline=DARK_BROWN)

    return img

def generate_prop_flowerpot():
    """prop_flowerpot: 32x32. Terracotta clay planter with monstera plant."""
    w, h = 32, 32
    img = Image.new('RGBA', (w, h), TRANSPARENT)
    draw = ImageDraw.Draw(img)

    # Pot base touching bottom
    draw.polygon([(6, 18), (26, 18), (24, 31), (8, 31)], fill=TERRACOTTA, outline=DARK_BROWN)
    draw.rectangle([2, 30, 30, 31], fill=BURNT)
    draw.rectangle([4, 16, 28, 20], fill=TERRA_DARK, outline=DARK_BROWN)

    # Monstera green leaves
    draw.ellipse([4, 2, 18, 16], fill=GREEN_MID, outline=DARK_GREEN)
    draw.ellipse([14, 2, 28, 16], fill=GREEN_LIGHT, outline=DARK_GREEN)
    draw.ellipse([10, 6, 22, 18], fill=DARK_GREEN)

    return img

def main():
    print("=== Memulai Pembuatan Aset Visual Pixel Art (16-Bit) ===")
    os.makedirs(OUT_DIR_BLD, exist_ok=True)
    os.makedirs(OUT_DIR_NPC, exist_ok=True)
    os.makedirs(OUT_DIR_PROP, exist_ok=True)

    generators = [
        # Buildings
        (generate_house, os.path.join(OUT_DIR_BLD, "bld_rumah_pemain.png")),
        (generate_minimarket, os.path.join(OUT_DIR_BLD, "bld_minimarket.png")),
        (generate_cosmetics, os.path.join(OUT_DIR_BLD, "bld_toko_kosmetik.png")),
        (generate_spbu, os.path.join(OUT_DIR_BLD, "bld_spbu.png")),
        (generate_game_center, os.path.join(OUT_DIR_BLD, "bld_game_center.png")),
        # NPCs
        (generate_npc_family, os.path.join(OUT_DIR_NPC, "npc_sheet_family.png")),
        (generate_npc_friends, os.path.join(OUT_DIR_NPC, "npc_sheet_friends.png")),
        (generate_npc_vendors, os.path.join(OUT_DIR_NPC, "npc_sheet_vendors.png")),
        # Props & Trees
        (generate_prop_tree_large, os.path.join(OUT_DIR_PROP, "prop_tree_large.png")),
        (generate_prop_tree_small, os.path.join(OUT_DIR_PROP, "prop_tree_small.png")),
        (generate_prop_bush, os.path.join(OUT_DIR_PROP, "prop_bush.png")),
        (generate_prop_street_lamp, os.path.join(OUT_DIR_PROP, "prop_street_lamp.png")),
        (generate_prop_bench, os.path.join(OUT_DIR_PROP, "prop_bench.png")),
        (generate_prop_trashcan, os.path.join(OUT_DIR_PROP, "prop_trashcan.png")),
        (generate_prop_flowerpot, os.path.join(OUT_DIR_PROP, "prop_flowerpot.png")),
    ]

    for gen_func, out_path in generators:
        img = gen_func()
        img.save(out_path, format="PNG")
        print(f"✓ Tersimpan: {out_path} ({img.size[0]}x{img.size[1]})")

    print("\nSemua 15 aset visual berhasil dihasilkan!")

if __name__ == "__main__":
    main()
