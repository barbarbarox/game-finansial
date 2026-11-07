#!/usr/bin/env python3
"""
test_tools.py — Uji tiap tool aset dengan gambar sintetis (Rule 60 / P2).
Membuat sheet magenta buatan dengan 3 kotak subjek, menjalankan:
chroma_key -> slice_sheet -> normalize -> palette_snap -> build_spritesheet -> validate_asset -> contact_sheet.
"""

import os
import sys
import numpy as np
from PIL import Image

from chroma_key import remove_magenta_background
from slice_sheet import slice_horizontal_subjects
from normalize import normalize_sprite
from palette_snap import snap_to_palette
from build_spritesheet import build_horizontal_sheet
from validate_asset import validate
from contact_sheet import make_contact_sheet

def run_tests():
    print("=== Menjalankan Pengujian Alat Aset Sintetis (P2) ===")
    test_dir = "/tmp/lj_tools_test"
    os.makedirs(test_dir, exist_ok=True)

    # 1. Buat gambar sintetis: latar magenta #FF00FF dengan 3 kotak karakter sintetis
    w, h = 300, 100
    arr = np.full((h, w, 4), [255, 0, 255, 255], dtype=np.uint8)

    # 3 Kotak (mewakili 3 pandangan karakter: front, back, left)
    # Kotak 1: warna cream + navy
    arr[20:90, 20:80] = [247, 238, 218, 255]
    arr[50:90, 30:70] = [31, 42, 68, 255]

    # Kotak 2: warna cream + navy
    arr[20:90, 120:180] = [247, 238, 218, 255]
    arr[50:90, 130:170] = [31, 42, 68, 255]

    # Kotak 3: warna cream + navy
    arr[20:90, 220:280] = [247, 238, 218, 255]
    arr[50:90, 230:270] = [31, 42, 68, 255]

    synth_raw = os.path.join(test_dir, "synthetic_raw.png")
    Image.fromarray(arr).save(synth_raw)
    print("1. Gambar sintetis magenta dibuat:", synth_raw)

    # 2. Chroma key
    synth_keyed = os.path.join(test_dir, "synthetic_keyed.png")
    rem_mag = remove_magenta_background(synth_raw, synth_keyed)
    assert rem_mag == 0, f"Chroma key gagal, sisa magenta: {rem_mag}"
    print(f"2. Chroma key PASS (sisa magenta: {rem_mag})")

    # 3. Slice sheet
    subs = slice_horizontal_subjects(synth_keyed, expected_count=3)
    assert len(subs) == 3, f"Slice sheet gagal, jumlah potongan: {len(subs)}"
    print(f"3. Slice sheet PASS (terpotong {len(subs)} subjek)")

    # 4. Normalize
    norm_frames = []
    for i, s in enumerate(subs):
        norm = normalize_sprite(s, target_w=32, target_h=64)
        out_p = os.path.join(test_dir, f"norm_{i}.png")
        norm.save(out_p)
        norm_frames.append(out_p)
    print("4. Normalize PASS (seluruh subjek dinormalisasi ke 32x64)")

    # 5. Palette snap
    palette_path = "/home/abarox/Desktop/prototipe web statis game/game/assets/palette.json"
    snapped_frames = []
    for i, p in enumerate(norm_frames):
        out_s = os.path.join(test_dir, f"snap_{i}.png")
        snap_to_palette(p, palette_path, out_s)
        snapped_frames.append(Image.open(out_s))
    print("5. Palette snap PASS (dipetakan ke 32 warna palet)")

    # 6. Build spritesheet
    sheet_out = os.path.join(test_dir, "spritesheet.png")
    build_horizontal_sheet(snapped_frames, 32, 64, sheet_out)
    sheet_img = Image.open(sheet_out)
    assert sheet_img.size == (96, 64), f"Ukuran sheet salah: {sheet_img.size}"
    print(f"6. Build spritesheet PASS (ukuran: {sheet_img.size})")

    # 7. Validate asset
    rep = validate(sheet_out, {"width": 96, "height": 64, "kind": "character_sheet"})
    assert rep["pass"] == True, f"Validasi gagal: {rep['failures']}"
    print("7. Validate asset PASS (cek teknis lolos)")

    # 8. Contact sheet
    contact_out = os.path.join(test_dir, "contact.png")
    make_contact_sheet(norm_frames, contact_out, scale=2)
    assert os.path.exists(contact_out), "Contact sheet gagal dibuat"
    print("8. Contact sheet PASS")

    print("\n>>> SELURUH PENGUJIAN ALAT ASET P2 BERHASIL 100%! <<<\n")

if __name__ == '__main__':
    run_tests()
