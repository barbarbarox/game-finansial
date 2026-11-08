#!/usr/bin/env python3
"""
slice_all_v4_furniture.py - Chromakey and slice newly generated v4 furniture assets:
1. Minimarket & SPBU props
2. Game Center & Toko Kosmetik props
3. School Facilities & Canteen props
4. School Classroom student desks & chairs
"""

import os
import json
import numpy as np
from PIL import Image

def chromakey_crop(im_crop, thresh=70):
    """Replaces magenta background with transparent alpha."""
    arr = np.array(im_crop.convert("RGBA"))
    r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
    
    # Pure magenta #FF00FF is high R, low G, high B
    is_magenta = (r > 165) & (g < 95) & (b > 165) & (np.abs(r.astype(int) - b.astype(int)) < 55)
    
    # Also clean anti-aliasing edges near magenta
    edge_magenta = (r > 140) & (g < 120) & (b > 140) & (r > g + 40) & (b > g + 40)
    
    mask = is_magenta | edge_magenta
    arr[mask, 3] = 0
    
    # Crop to non-transparent bounding box
    alpha = arr[:, :, 3]
    bbox = np.where(alpha > 20)
    if len(bbox[0]) == 0 or len(bbox[1]) == 0:
        return Image.fromarray(arr)
    
    y0, y1 = bbox[0].min(), bbox[0].max() + 1
    x0, x1 = bbox[1].min(), bbox[1].max() + 1
    
    return Image.fromarray(arr[y0:y1, x0:x1])

def process_and_save(img, box, target_size, out_paths):
    crop = img.crop(box)
    keyed = chromakey_crop(crop)
    
    # Resize preserving aspect ratio into target_size bounding box
    tw, th = target_size
    kw, kh = keyed.size
    
    scale = min(tw / kw, th / kh)
    nw = max(1, int(round(kw * scale)))
    nh = max(1, int(round(kh * scale)))
    
    scaled = keyed.resize((nw, nh), Image.Resampling.NEAREST)
    
    # Pad to exact target size with bottom-center anchor
    final_img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    paste_x = (tw - nw) // 2
    paste_y = th - nh
    final_img.paste(scaled, (paste_x, paste_y), scaled)
    
    for p in out_paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        final_img.save(p)
        print(f"  Saved ({tw}x{th}): {os.path.basename(p)}")

def run():
    base_dir = "/home/abarox/Desktop/prototipe web statis game/game"
    furn_dir = os.path.join(base_dir, "assets", "furniture")

    # =========================================================================
    # 1. Minimarket & SPBU Props
    # =========================================================================
    p1 = "/home/abarox/.gemini/antigravity/brain/4d2f9b08-f034-4550-b619-39a74fd29f25/props_batch2_atlas_1794151246281.jpg"
    im1 = Image.open(p1).convert("RGB")
    print(f"\nProcessing Batch 1: Minimarket & SPBU props ({im1.size})...")

    # [0] furn_rak_roti: y: 37..391, x: 45..287
    process_and_save(im1, (45, 37, 287, 391), (64, 64), [
        os.path.join(furn_dir, "minimarket", "furn_rak_roti.png"),
        os.path.join(furn_dir, "minimarket", "furn_rak_roti_v4.png")
    ])

    # [1] furn_rak_mie_instan: y: 29..390, x: 341..579
    process_and_save(im1, (341, 29, 579, 390), (64, 80), [
        os.path.join(furn_dir, "minimarket", "furn_rak_mie_instan.png"),
        os.path.join(furn_dir, "minimarket", "furn_rak_mie_instan_v4.png")
    ])

    # [2] furn_rak_dinding_snack: y: 44..384, x: 630..871
    process_and_save(im1, (630, 44, 871, 384), (64, 96), [
        os.path.join(furn_dir, "minimarket", "furn_rak_dinding_snack.png"),
        os.path.join(furn_dir, "minimarket", "furn_rak_dinding_snack_v4.png")
    ])

    # [3] furn_etalase_makanan_siap_saji: y: 107..388, x: 914..1166
    process_and_save(im1, (914, 107, 1166, 388), (96, 64), [
        os.path.join(furn_dir, "minimarket", "furn_etalase_makanan_siap_saji.png"),
        os.path.join(furn_dir, "minimarket", "furn_etalase_makanan_siap_saji_v4.png")
    ])

    # [5] furn_galon_tumpuk: y: 473..802, x: 90..239
    process_and_save(im1, (90, 473, 239, 802), (32, 48), [
        os.path.join(furn_dir, "minimarket", "furn_galon_tumpuk.png"),
        os.path.join(furn_dir, "minimarket", "furn_galon_tumpuk_v4.png")
    ])

    # [7] furn_tempat_sampah: y: 547..790, x: 373..552
    process_and_save(im1, (373, 547, 552, 790), (32, 32), [
        os.path.join(furn_dir, "minimarket", "furn_tempat_sampah.png"),
        os.path.join(furn_dir, "minimarket", "furn_tempat_sampah_v4.png"),
        os.path.join(furn_dir, "school", "furn_tempat_sampah.png"),
        os.path.join(furn_dir, "school", "furn_tempat_sampah_v4.png"),
        os.path.join(furn_dir, "spbu", "furn_tempat_sampah.png"),
        os.path.join(furn_dir, "spbu", "furn_tempat_sampah_v4.png")
    ])

    # [6] furn_kompresor_angin: y: 497..802, x: 666..870
    process_and_save(im1, (666, 497, 870, 802), (32, 48), [
        os.path.join(furn_dir, "spbu", "furn_kompresor_angin.png"),
        os.path.join(furn_dir, "spbu", "furn_kompresor_angin_v4.png")
    ])

    # [8] furn_tong_pemadam: y: 503..801, x: 985..1114
    process_and_save(im1, (985, 503, 1114, 801), (32, 40), [
        os.path.join(furn_dir, "spbu", "furn_tong_pemadam.png"),
        os.path.join(furn_dir, "spbu", "furn_tong_pemadam_v4.png")
    ])

    # =========================================================================
    # 2. Game Center & Toko Kosmetik Props
    # =========================================================================
    p2 = "/home/abarox/.gemini/antigravity/brain/4d2f9b08-f034-4550-b619-39a74fd29f25/entertainment_boutique_props_atlas_1794151268320.jpg"
    im2 = Image.open(p2).convert("RGB")
    print(f"\nProcessing Batch 2: Game Center & Kosmetik props ({im2.size})...")

    # [0] furn_mesin_capit: y: 30..474, x: 48..300
    process_and_save(im2, (48, 30, 300, 474), (64, 96), [
        os.path.join(furn_dir, "game_center", "furn_mesin_capit.png"),
        os.path.join(furn_dir, "game_center", "furn_mesin_capit_v4.png")
    ])

    # [1] furn_sofa_nonton: y: 54..382, x: 356..743
    process_and_save(im2, (356, 54, 743, 382), (96, 64), [
        os.path.join(furn_dir, "game_center", "furn_sofa_nonton.png"),
        os.path.join(furn_dir, "game_center", "furn_sofa_nonton_v4.png")
    ])

    # [2] furn_tanaman_pot: y: 54..377, x: 780..974
    process_and_save(im2, (780, 54, 974, 377), (32, 48), [
        os.path.join(furn_dir, "game_center", "furn_tanaman_pot.png"),
        os.path.join(furn_dir, "game_center", "furn_tanaman_pot_v4.png"),
        os.path.join(furn_dir, "kosmetik", "furn_tanaman_pot.png"),
        os.path.join(furn_dir, "kosmetik", "furn_tanaman_pot_v4.png")
    ])

    # [3] furn_tiang_kanopi: y: 440..942, x: 798..943
    process_and_save(im2, (798, 440, 943, 942), (32, 128), [
        os.path.join(furn_dir, "spbu", "furn_tiang_kanopi.png"),
        os.path.join(furn_dir, "spbu", "furn_tiang_kanopi_v4.png")
    ])

    # [4] furn_kursi_cermin: y: 686..934, x: 112..236
    process_and_save(im2, (112, 686, 236, 934), (32, 48), [
        os.path.join(furn_dir, "kosmetik", "furn_kursi_cermin.png"),
        os.path.join(furn_dir, "kosmetik", "furn_kursi_cermin_v4.png")
    ])

    # [5] furn_sofa_tunggu: y: 678..968, x: 353..681
    process_and_save(im2, (353, 678, 681, 968), (64, 64), [
        os.path.join(furn_dir, "kosmetik", "furn_sofa_tunggu.png"),
        os.path.join(furn_dir, "kosmetik", "furn_sofa_tunggu_v4.png")
    ])

    # =========================================================================
    # 3. School Facilities & Canteen Props
    # =========================================================================
    p3 = "/home/abarox/.gemini/antigravity/brain/4d2f9b08-f034-4550-b619-39a74fd29f25/indonesian_school_facilities_spritesheet_1794151258192.jpg"
    im3 = Image.open(p3).convert("RGB")
    print(f"\nProcessing Batch 3: School Facilities props ({im3.size})...")

    # (0, 0) furn_counter_kantin_etalase: x: 35..326, y: 37..300
    process_and_save(im3, (35, 37, 326, 300), (160, 80), [
        os.path.join(furn_dir, "school", "furn_counter_kantin_etalase.png"),
        os.path.join(furn_dir, "school", "furn_counter_kantin_etalase_v4.png")
    ])

    # (0, 1) furn_meja_kantin_panjang: x: 371..653, y: 51..310
    process_and_save(im3, (371, 51, 653, 310), (96, 64), [
        os.path.join(furn_dir, "school", "furn_meja_kantin_panjang.png"),
        os.path.join(furn_dir, "school", "furn_meja_kantin_panjang_v4.png")
    ])

    # (0, 2) furn_counter_pustakawan: x: 698..989, y: 92..285
    process_and_save(im3, (698, 92, 989, 285), (96, 64), [
        os.path.join(furn_dir, "school", "furn_counter_pustakawan.png"),
        os.path.join(furn_dir, "school", "furn_counter_pustakawan_v4.png")
    ])

    # (1, 0) furn_komputer_meja: x: 55..297, y: 380..650
    process_and_save(im3, (55, 380, 297, 650), (48, 48), [
        os.path.join(furn_dir, "school", "furn_komputer_meja.png"),
        os.path.join(furn_dir, "school", "furn_komputer_meja_v4.png")
    ])

    # (1, 1) furn_kursi_baca: x: 413..612, y: 381..650
    process_and_save(im3, (413, 381, 612, 650), (32, 48), [
        os.path.join(furn_dir, "school", "furn_kursi_baca.png"),
        os.path.join(furn_dir, "school", "furn_kursi_baca_v4.png")
    ])

    # (1, 2) furn_rak_piala: x: 757..946, y: 368..650
    process_and_save(im3, (757, 368, 946, 650), (64, 96), [
        os.path.join(furn_dir, "school", "furn_rak_piala.png"),
        os.path.join(furn_dir, "school", "furn_rak_piala_v4.png")
    ])

    # (2, 0) furn_wastafel_cuci_tangan: x: 82..271, y: 713..984
    process_and_save(im3, (82, 713, 271, 984), (48, 64), [
        os.path.join(furn_dir, "school", "furn_wastafel_cuci_tangan.png"),
        os.path.join(furn_dir, "school", "furn_wastafel_cuci_tangan_v4.png")
    ])

    # (2, 1) furn_papan_info: x: 374..650, y: 748..947
    process_and_save(im3, (374, 748, 650, 947), (96, 48), [
        os.path.join(furn_dir, "school", "furn_papan_info.png"),
        os.path.join(furn_dir, "school", "furn_papan_info_v4.png")
    ])

    # (2, 2) furn_papan_menu_kosong: x: 732..973, y: 730..952
    process_and_save(im3, (732, 730, 973, 952), (96, 48), [
        os.path.join(furn_dir, "school", "furn_papan_menu_kosong.png"),
        os.path.join(furn_dir, "school", "furn_papan_menu_kosong_v4.png")
    ])

    # =========================================================================
    # 4. School Classroom Props
    # =========================================================================
    p4 = "/home/abarox/.gemini/antigravity/brain/4d2f9b08-f034-4550-b619-39a74fd29f25/furn_classroom_sprites_1794151289696.jpg"
    im4 = Image.open(p4).convert("RGB")
    print(f"\nProcessing Batch 4: School Classroom props ({im4.size})...")

    # [0] furn_meja_siswa: y: 66..461, x: 82..461
    process_and_save(im4, (82, 66, 461, 461), (64, 48), [
        os.path.join(furn_dir, "school", "furn_meja_siswa.png"),
        os.path.join(furn_dir, "school", "furn_meja_siswa_v4.png")
    ])

    # [1] furn_kursi_siswa: y: 56..461, x: 645..886
    process_and_save(im4, (645, 56, 886, 461), (32, 48), [
        os.path.join(furn_dir, "school", "furn_kursi_siswa.png"),
        os.path.join(furn_dir, "school", "furn_kursi_siswa_v4.png")
    ])

    # [2] furn_kursi_guru: y: 563..963, x: 128..410
    process_and_save(im4, (128, 563, 410, 963), (32, 48), [
        os.path.join(furn_dir, "school", "furn_kursi_guru.png"),
        os.path.join(furn_dir, "school", "furn_kursi_guru_v4.png")
    ])

    # [3] furn_rak_buku_kelas: y: 512..1004, x: 609..922
    process_and_save(im4, (609, 512, 922, 1004), (64, 96), [
        os.path.join(furn_dir, "school", "furn_rak_buku_kelas.png"),
        os.path.join(furn_dir, "school", "furn_rak_buku_kelas_v4.png")
    ])

    print("\nAll 27 missing v4 furniture assets sliced, keyed, and saved successfully!")

if __name__ == "__main__":
    run()
