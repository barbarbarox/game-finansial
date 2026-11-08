#!/usr/bin/env python3
"""
render_layout_guide.py - Render exact schematic guide and class masks for town_hub terrain plate.
Follows Rule 76 (Level 1: plate terpandu).
"""

import json
import os
from PIL import Image, ImageDraw

def render_guide():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    layout_path = os.path.join(base_dir, "data", "maps", "town_hub.layout.json")
    out_dir = os.path.join(base_dir, "assets", "terrain")
    masks_dir = os.path.join(out_dir, "guide_masks")
    os.makedirs(masks_dir, exist_ok=True)

    with open(layout_path, "r", encoding="utf-8") as f:
        layout = json.load(f)

    w_tiles = layout["world"]["widthTiles"]
    h_tiles = layout["world"]["heightTiles"]
    tile_size = layout["world"]["tileSize"]
    width = w_tiles * tile_size   # 1280
    height = h_tiles * tile_size  # 768

    print(f"Rendering town_hub guide: {width}x{height} px ({w_tiles}x{h_tiles} tiles of {tile_size}px)")

    # Colors for guide schematic
    COLOR_GRASS = (74, 124, 89)      # #4a7c59 Lush green
    COLOR_YARD = (195, 170, 130)     # #c3aa82 Sandy yard / building lot
    COLOR_SIDEWALK = (145, 155, 165) # #919ba5 Stone/pavement
    COLOR_ROAD = (50, 56, 68)        # #323844 Dark asphalt
    COLOR_MARKING = (245, 235, 205)  # #f5ebcd Road marking
    COLOR_PAD = (40, 48, 60)         # #28303c Building footprint / contact shadow

    guide_img = Image.new("RGB", (width, height), COLOR_GRASS)
    draw = ImageDraw.Draw(guide_img)

    # Masks (single channel grayscale 0 or 255)
    mask_grass = Image.new("L", (width, height), 255)
    mask_yard = Image.new("L", (width, height), 0)
    mask_sidewalk = Image.new("L", (width, height), 0)
    mask_road = Image.new("L", (width, height), 0)
    mask_marking = Image.new("L", (width, height), 0)
    mask_pad = Image.new("L", (width, height), 0)

    draw_m_grass = ImageDraw.Draw(mask_grass)
    draw_m_yard = ImageDraw.Draw(mask_yard)
    draw_m_sw = ImageDraw.Draw(mask_sidewalk)
    draw_m_road = ImageDraw.Draw(mask_road)
    draw_m_mark = ImageDraw.Draw(mask_marking)
    draw_m_pad = ImageDraw.Draw(mask_pad)

    # 1. Yards (halaman)
    for g in layout.get("ground", []):
        if g.get("type") == "halaman":
            rx0 = g["x"] * tile_size
            ry0 = g["y"] * tile_size
            rx1 = rx0 + g["w"] * tile_size
            ry1 = ry0 + g["h"] * tile_size
            draw.rectangle([rx0, ry0, rx1, ry1], fill=COLOR_YARD)
            draw_m_yard.rectangle([rx0, ry0, rx1, ry1], fill=255)
            draw_m_grass.rectangle([rx0, ry0, rx1, ry1], fill=0)

    # 2. Sidewalks (trotoar)
    for g in layout.get("ground", []):
        if g.get("type") == "trotoar":
            rx0 = g["x"] * tile_size
            ry0 = g["y"] * tile_size
            rx1 = rx0 + g["w"] * tile_size
            ry1 = ry0 + g["h"] * tile_size
            draw.rectangle([rx0, ry0, rx1, ry1], fill=COLOR_SIDEWALK)
            draw_m_sw.rectangle([rx0, ry0, rx1, ry1], fill=255)
            draw_m_grass.rectangle([rx0, ry0, rx1, ry1], fill=0)
            draw_m_yard.rectangle([rx0, ry0, rx1, ry1], fill=0)

    # 3. Roads (jalan)
    for g in layout.get("ground", []):
        if g.get("type") == "jalan":
            rx0 = g["x"] * tile_size
            ry0 = g["y"] * tile_size
            rx1 = rx0 + g["w"] * tile_size
            ry1 = ry0 + g["h"] * tile_size
            draw.rectangle([rx0, ry0, rx1, ry1], fill=COLOR_ROAD)
            draw_m_road.rectangle([rx0, ry0, rx1, ry1], fill=255)
            draw_m_sw.rectangle([rx0, ry0, rx1, ry1], fill=0)
            draw_m_grass.rectangle([rx0, ry0, rx1, ry1], fill=0)
            draw_m_yard.rectangle([rx0, ry0, rx1, ry1], fill=0)

    # 4. Road Markings (marka garis tengah & zebra cross)
    # Horizontal road: y=15..17 (center is y=16*32 = 512). Centerline dashed 4px wide
    h_road_center_y = 16 * tile_size
    for x in range(0, width, 64):
        # Don't draw marking in intersection (x between 20*32 and 22*32, i.e. 640..704)
        if 620 <= x <= 720:
            continue
        draw.rectangle([x + 10, h_road_center_y - 2, x + 50, h_road_center_y + 2], fill=COLOR_MARKING)
        draw_m_mark.rectangle([x + 10, h_road_center_y - 2, x + 50, h_road_center_y + 2], fill=255)

    # Vertical road: x=20..22 (center is x=21*32 = 672). Centerline dashed 4px wide
    v_road_center_x = 21 * tile_size
    for y in range(0, height, 64):
        if 460 <= y <= 560:
            continue
        draw.rectangle([v_road_center_x - 2, y + 10, v_road_center_x + 2, y + 50], fill=COLOR_MARKING)
        draw_m_mark.rectangle([v_road_center_x - 2, y + 10, v_road_center_x + 2, y + 50], fill=255)

    # Zebra crosses near intersection:
    # West zebra: x=19*32 (608) to 20*32 (640), y=15*32..17*32 (480..544)
    for zy in range(15 * tile_size + 4, 17 * tile_size - 4, 12):
        draw.rectangle([19 * tile_size + 2, zy, 20 * tile_size - 2, zy + 6], fill=COLOR_MARKING)
        draw_m_mark.rectangle([19 * tile_size + 2, zy, 20 * tile_size - 2, zy + 6], fill=255)
    # East zebra: x=22*32 (704) to 23*32 (736)
    for zy in range(15 * tile_size + 4, 17 * tile_size - 4, 12):
        draw.rectangle([22 * tile_size + 2, zy, 23 * tile_size - 2, zy + 6], fill=COLOR_MARKING)
        draw_m_mark.rectangle([22 * tile_size + 2, zy, 23 * tile_size - 2, zy + 6], fill=255)
    # North zebra: y=14*32 (448) to 15*32 (480), x=20*32..22*32 (640..704)
    for zx in range(20 * tile_size + 4, 22 * tile_size - 4, 12):
        draw.rectangle([zx, 14 * tile_size + 2, zx + 6, 15 * tile_size - 2], fill=COLOR_MARKING)
        draw_m_mark.rectangle([zx, 14 * tile_size + 2, zx + 6, 15 * tile_size - 2], fill=255)
    # South zebra: y=17*32 (544) to 18*32 (576), x=20*32..22*32 (640..704)
    for zx in range(20 * tile_size + 4, 22 * tile_size - 4, 12):
        draw.rectangle([zx, 17 * tile_size + 2, zx + 6, 18 * tile_size - 2], fill=COLOR_MARKING)
        draw_m_mark.rectangle([zx, 17 * tile_size + 2, zx + 6, 18 * tile_size - 2], fill=255)

    # 5. Building Pads (contact foundations)
    for obj in layout.get("objects", []):
        fp = obj.get("footprint", {"w": 4, "h": 3})
        w = fp["w"] * tile_size
        h = fp["h"] * tile_size
        x = obj["x"] * tile_size
        y = obj["y"] * tile_size
        bx0 = x - w // 2
        by0 = y - h
        bx1 = bx0 + w
        by1 = by0 + h
        draw.rectangle([bx0, by0, bx1, by1], fill=COLOR_PAD)
        draw_m_pad.rectangle([bx0, by0, bx1, by1], fill=255)

    # Thin tile grid line
    for x in range(0, width, tile_size):
        draw.line([(x, 0), (x, height)], fill=(0, 0, 0, 40))
    for y in range(0, height, tile_size):
        draw.line([(0, y), (width, y)], fill=(0, 0, 0, 40))

    guide_path = os.path.join(out_dir, "guide_hub.png")
    guide_img.save(guide_path)
    print(f"Saved guide schematic: {guide_path}")

    # Save masks
    mask_grass.save(os.path.join(masks_dir, "mask_rumput.png"))
    mask_yard.save(os.path.join(masks_dir, "mask_halaman.png"))
    mask_sidewalk.save(os.path.join(masks_dir, "mask_trotoar.png"))
    mask_road.save(os.path.join(masks_dir, "mask_jalan.png"))
    mask_marking.save(os.path.join(masks_dir, "mask_marka.png"))
    mask_pad.save(os.path.join(masks_dir, "mask_pad.png"))
    print(f"Saved 6 masks to: {masks_dir}")

if __name__ == "__main__":
    render_guide()
