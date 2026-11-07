#!/usr/bin/env python3
"""
build_spritesheet.py — Susun frame sesuai urutan di brief (idle_down, idle_up, idle_left).
"""

import sys
from PIL import Image

def build_horizontal_sheet(frames, frame_w, frame_h, output_path):
    sheet = Image.new('RGBA', (frame_w * len(frames), frame_h), (0, 0, 0, 0))
    for i, frame in enumerate(frames):
        sheet.paste(frame, (i * frame_w, 0))
    sheet.save(output_path, 'PNG')
    return sheet

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("Usage: python3 build_spritesheet.py <output_sheet.png> <w> <h> <frame1> <frame2> ...")
        sys.exit(1)
    out_path = sys.argv[1]
    fw = int(sys.argv[2])
    fh = int(sys.argv[3])
    frame_paths = sys.argv[4:]
    frames = [Image.open(p) for p in frame_paths]
    build_horizontal_sheet(frames, fw, fh, out_path)
    print(f"Spritesheet saved to {out_path} with {len(frames)} frames.")

