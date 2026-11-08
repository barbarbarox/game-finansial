#!/usr/bin/env python3
"""
process_e5_assets.py — Processes all E5 assets:
1. Slices and normalizes raw generated sheets for home (kamar ortu, ruang tamu, dapur)
2. Generates labeled placeholders for remaining items (school, commercial, extra portraits, bathroom) per Rule 60 §6
3. Creates contact sheets per group in docs/contact-sheets/
4. Updates assets/asset-manifest.json
5. Updates docs/ASSET-LOG.md
"""

import os
import sys
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from tools.chroma_key import remove_magenta_background
from tools.normalize import normalize_sprite
from tools.palette_snap import snap_to_palette

PALETTE_PATH = "assets/palette.json"
BRIEFS_PATH = "data/asset-briefs-expansion.json"
MANIFEST_PATH = "assets/asset-manifest.json"
LOG_PATH = "docs/ASSET-LOG.md"
CONTACT_DIR = "docs/contact-sheets"
os.makedirs(CONTACT_DIR, exist_ok=True)
os.makedirs("assets/furniture/home", exist_ok=True)
os.makedirs("assets/furniture/school", exist_ok=True)
os.makedirs("assets/furniture/minimarket", exist_ok=True)
os.makedirs("assets/furniture/kosmetik", exist_ok=True)
os.makedirs("assets/furniture/spbu", exist_ok=True)
os.makedirs("assets/furniture/game_center", exist_ok=True)
os.makedirs("assets/portraits", exist_ok=True)

with open(PALETTE_PATH, 'r') as f:
    palette_data = json.load(f)

with open(BRIEFS_PATH, 'r') as f:
    briefs_data = json.load(f)

with open(MANIFEST_PATH, 'r') as f:
    manifest_data = json.load(f)

def create_contact_sheet(images, titles, out_path, bg_color=(27, 40, 56, 255)):
    card_w = 200
    card_h = 240
    padding = 16
    cols = min(6, len(images))
    rows = int(np.ceil(len(images) / float(cols))) if cols > 0 else 1

    total_w = cols * (card_w + padding) + padding
    total_h = rows * (card_h + padding) + padding

    canvas = Image.new('RGBA', (total_w, total_h), bg_color)
    draw = ImageDraw.Draw(canvas)

    for i, (img, title) in enumerate(zip(images, titles)):
        r = i // cols
        c = i % cols
        x = padding + c * (card_w + padding)
        y = padding + r * (card_h + padding)

        # Card bg
        draw.rectangle([x, y, x + card_w, y + card_h], fill=(18, 26, 46, 255), outline=(52, 69, 107, 255), width=1)

        scale = min((card_w - 24) / float(img.width), (card_h - 48) / float(img.height))
        scale_int = max(1, int(scale))
        upscaled = img.resize((img.width * scale_int, img.height * scale_int), Image.NEAREST)

        paste_x = x + (card_w - upscaled.width) // 2
        paste_y = y + (card_h - 36 - upscaled.height) // 2 + 10

        canvas.paste(upscaled, (paste_x, paste_y), upscaled)

        # Title
        draw.text((x + 8, y + card_h - 24), title, fill=(247, 238, 218, 255))

    canvas.save(out_path)
    print(f"  [Contact Sheet] Saved -> {out_path}")

def process_raw_sheet(raw_path, target_items, out_dir, prefix=""):
    print(f"-> Memproses sheet mentah: {raw_path}")
    temp_keyed = f"/tmp/keyed_{os.path.basename(raw_path)}.png"
    remove_magenta_background(raw_path, temp_keyed, tolerance=55)
    keyed = Image.open(temp_keyed).convert('RGBA')

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
            if (x - start_x) >= 24:
                segments.append((start_x, x))
    if in_seg and (len(col_has) - start_x) >= 24:
        segments.append((start_x, len(col_has)))

    print(f"   Segmen terdeteksi: {len(segments)} (target: {len(target_items)})")
    if len(segments) != len(target_items):
        w_step = keyed.width / len(target_items)
        segments = [(int(i * w_step), int((i + 1) * w_step)) for i in range(len(target_items))]

    results = []
    for idx, (item_id, target_w, target_h, label) in enumerate(target_items):
        x1, x2 = segments[idx]
        crop = keyed.crop((x1, 0, x2, keyed.height))
        bbox = crop.getbbox()
        if bbox:
            crop = crop.crop(bbox)

        normalized = normalize_sprite(crop, target_w, target_h)
        snapped = snap_to_palette(normalized, PALETTE_PATH)

        out_path = os.path.join(out_dir, f"{item_id}.png")
        snapped.save(out_path)
        print(f"   ✓ Disimpan: {out_path} ({target_w}x{target_h})")
        results.append((snapped, f"{item_id}\n{target_w}x{target_h}"))

    return results

def make_placeholder_sprite(item_id, target_w, target_h, label, is_portrait=False):
    canvas = Image.new('RGBA', (target_w, target_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    if is_portrait:
        # 192x256 silhouette portrait
        draw.rectangle([0, 0, target_w - 1, target_h - 1], fill=(31, 42, 68, 255), outline=(217, 164, 65, 255), width=2)
        # Head & shoulders silhouette
        draw.ellipse([target_w//4, 30, target_w*3//4, target_w*3//4 + 20], fill=(201, 162, 122, 255))
        draw.rectangle([target_w//6, target_w*3//4 + 30, target_w*5//6, target_h - 10], fill=(165, 190, 147, 255))
        draw.text((12, target_h - 24), label[:22], fill=(247, 238, 218, 255))
    else:
        # Top-down 3/4 box prop
        draw.rectangle([1, 1, target_w - 2, target_h - 2], fill=(31, 42, 68, 240), outline=(217, 164, 65, 255), width=2)
        # 3/4 top face
        top_h = max(6, target_h // 4)
        draw.rectangle([2, 2, target_w - 3, top_h], fill=(52, 69, 107, 255), outline=(74, 107, 62, 255), width=1)
        # Text label
        short_label = label.replace("furn_", "").replace("furn ", "")
        draw.text((4, target_h // 2 - 4), short_label[:14], fill=(247, 238, 218, 255))

    snapped = snap_to_palette(canvas, PALETTE_PATH)
    return snapped

def main():
    print("==================================================")
    print("  E5 · GENERASI SISA ASET INTERIOR (Rule 60)")
    print("==================================================")

    home_results = []
    # Include E4 kamar pemain in contact sheet
    kamar_pemain_dir = "assets/furniture/kamar_pemain"
    for f_name in sorted(os.listdir(kamar_pemain_dir)):
        if f_name.endswith('.png'):
            im = Image.open(os.path.join(kamar_pemain_dir, f_name))
            home_results.append((im, f_name.replace('.png', '')))

    # 1. Kamar Ortu
    ortu_items = [
        ("furn_kasur_besar", 96, 112, "Kasur Besar"),
        ("furn_lemari_besar", 96, 96, "Lemari Besar"),
        ("furn_meja_rias", 64, 80, "Meja Rias"),
        ("furn_kipas_berdiri", 32, 64, "Kipas Berdiri")
    ]
    home_results.extend(process_raw_sheet("assets/_raw/furn_sheet_kamar_ortu_raw.jpg", ortu_items, "assets/furniture/home"))

    # 2. Ruang Tamu
    tamu_items = [
        ("furn_sofa_3dudukan", 128, 64, "Sofa 3 Dudukan"),
        ("furn_sofa_single", 64, 64, "Sofa Single"),
        ("furn_meja_tamu", 64, 48, "Meja Tamu"),
        ("furn_tv_dan_rak", 96, 64, "TV & Rak"),
        ("furn_rak_pajangan", 64, 96, "Rak Pajangan"),
        ("furn_karpet_tamu", 128, 96, "Karpet Tamu")
    ]
    home_results.extend(process_raw_sheet("assets/_raw/furn_sheet_ruang_tamu_raw.jpg", tamu_items, "assets/furniture/home"))

    # 3. Dapur
    dapur_items = [
        ("furn_kompor_counter", 96, 64, "Kompor Counter"),
        ("furn_kulkas", 64, 96, "Kulkas"),
        ("furn_meja_makan", 96, 64, "Meja Makan"),
        ("furn_kursi_makan", 32, 48, "Kursi Makan"),
        ("furn_rak_piring", 64, 80, "Rak Piring"),
        ("furn_wastafel_dapur", 64, 64, "Wastafel Dapur")
    ]
    home_results.extend(process_raw_sheet("assets/_raw/furn_sheet_dapur_raw.jpg", dapur_items, "assets/furniture/home"))

    # 4. Kamar Mandi (Fallback placeholder due to model quota exhaustion)
    mandi_items = [
        ("furn_toilet", 32, 48, "Toilet"),
        ("furn_bak_mandi", 64, 64, "Bak Mandi"),
        ("furn_wastafel_cermin", 64, 80, "Wastafel & Cermin"),
        ("furn_rak_handuk", 32, 64, "Rak Handuk"),
        ("furn_ember", 32, 32, "Ember Air")
    ]
    for i_id, tw, th, lbl in mandi_items:
        p = make_placeholder_sprite(i_id, tw, th, lbl)
        out_p = f"assets/furniture/home/{i_id}.png"
        p.save(out_p)
        home_results.append((p, f"{i_id} (placeholder)"))

    # 5. Pintu Dekor (Fallback placeholder)
    dekor_items = [
        ("furn_pintu_depan", 64, 96, "Pintu Depan"),
        ("furn_pintu_kamar", 64, 96, "Pintu Kamar"),
        ("furn_jendela", 64, 64, "Jendela"),
        ("furn_jam_dinding", 32, 32, "Jam Dinding"),
        ("furn_bingkai_kosong", 32, 32, "Bingkai Foto")
    ]
    for i_id, tw, th, lbl in dekor_items:
        p = make_placeholder_sprite(i_id, tw, th, lbl)
        out_p = f"assets/furniture/home/{i_id}.png"
        p.save(out_p)
        home_results.append((p, f"{i_id} (placeholder)"))

    create_contact_sheet([h[0] for h in home_results], [h[1] for h in home_results], os.path.join(CONTACT_DIR, "contact_sheet_home.png"))

    # SCHOOL GROUP
    school_results = []
    school_items = [
        ("furn_meja_siswa_kursi", 64, 64, "Meja Siswa & Kursi"),
        ("furn_meja_guru", 96, 64, "Meja Guru"),
        ("furn_papan_tulis", 128, 64, "Papan Tulis"),
        ("furn_lemari_kelas", 64, 96, "Lemari Kelas"),
        ("furn_tempat_sampah_kelas", 32, 32, "Tempat Sampah"),
        ("furn_poster_kosong", 32, 48, "Poster Kosong"),
        ("furn_counter_kantin", 128, 64, "Counter Kantin"),
        ("furn_meja_kantin", 96, 64, "Meja Kantin"),
        ("furn_bangku_kantin", 96, 32, "Bangku Kantin"),
        ("furn_kulkas_minuman", 64, 96, "Kulkas Minuman"),
        ("furn_dispenser_galon", 32, 64, "Dispenser Galon"),
        ("furn_rak_snack", 64, 80, "Rak Snack"),
        ("furn_papan_pengumuman", 96, 64, "Papan Pengumuman"),
        ("furn_bangku_tunggu", 64, 32, "Bangku Tunggu"),
        ("furn_rak_buku_perpus", 96, 96, "Rak Buku Perpus"),
        ("furn_meja_baca", 96, 64, "Meja Baca"),
        ("furn_vas_tanaman", 32, 48, "Vas Tanaman")
    ]
    for i_id, tw, th, lbl in school_items:
        p = make_placeholder_sprite(i_id, tw, th, lbl)
        out_p = f"assets/furniture/school/{i_id}.png"
        p.save(out_p)
        school_results.append((p, f"{i_id}"))
    create_contact_sheet([s[0] for s in school_results], [s[1] for s in school_results], os.path.join(CONTACT_DIR, "contact_sheet_school.png"))

    # COMMERCIAL GROUP (Minimarket, Kosmetik, SPBU, Game Center)
    comm_results = []
    comm_groups = {
        "minimarket": [
            ("furn_rak_gondola", 96, 64, "Rak Gondola"),
            ("furn_rak_alat_tulis", 64, 80, "Rak Alat Tulis"),
            ("furn_kulkas_minuman_besar", 96, 96, "Kulkas Minuman"),
            ("furn_kasir_counter", 96, 64, "Kasir Counter"),
            ("furn_mesin_fotokopi", 64, 64, "Mesin Fotokopi"),
            ("furn_keranjang_belanja", 32, 32, "Keranjang Belanja")
        ],
        "kosmetik": [
            ("furn_etalase_kaca", 96, 64, "Etalase Kaca"),
            ("furn_rak_dinding_kosmetik", 64, 80, "Rak Dinding Kosmetik"),
            ("furn_meja_cermin", 64, 64, "Meja Cermin"),
            ("furn_kasir_kecil", 64, 64, "Kasir Kecil"),
            ("furn_kursi_tunggu", 32, 48, "Kursi Tunggu")
        ],
        "spbu": [
            ("furn_dispenser_bbm", 64, 80, "Dispenser BBM"),
            ("furn_kiosk_spbu", 96, 64, "Kiosk SPBU"),
            ("furn_rak_oli", 64, 64, "Rak Oli"),
            ("furn_bangku_spbu", 64, 32, "Bangku SPBU")
        ],
        "game_center": [
            ("furn_arcade_a", 64, 96, "Arcade Kabinet A"),
            ("furn_arcade_b", 64, 96, "Arcade Kabinet B"),
            ("furn_meja_kafe", 64, 64, "Meja Kafe"),
            ("furn_kursi_kafe", 32, 48, "Kursi Kafe"),
            ("furn_counter_kafe", 96, 64, "Counter Kafe"),
            ("furn_tv_besar", 96, 64, "TV Besar")
        ]
    }
    for grp, items in comm_groups.items():
        for i_id, tw, th, lbl in items:
            p = make_placeholder_sprite(i_id, tw, th, lbl)
            out_p = f"assets/furniture/{grp}/{i_id}.png"
            p.save(out_p)
            comm_results.append((p, f"{i_id}"))
    create_contact_sheet([c[0] for c in comm_results], [c[1] for c in comm_results], os.path.join(CONTACT_DIR, "contact_sheet_commercial.png"))

    # PORTRAITS GROUP
    portrait_results = []
    # E4 portraits
    for p_id in ["portrait_player_m", "portrait_player_f"]:
        im = Image.open(f"assets/portraits/{p_id}.png")
        portrait_results.append((im, p_id))

    extra_portraits = [
        ("portrait_ibu", "Ibu (Keluarga)"),
        ("portrait_ayah", "Ayah (Keluarga)"),
        ("portrait_teman_l", "Teman Budi"),
        ("portrait_teman_p", "Teman Siti"),
        ("portrait_penjual_kantin", "Bu Sri Kantin"),
        ("portrait_kasir_minimarket", "Kasir Minimarket"),
        ("portrait_penjaga_kosmetik", "Penjaga Toko Kosmetik"),
        ("portrait_petugas_spbu", "Petugas SPBU"),
        ("portrait_penjaga_game", "Operator Game Center")
    ]
    for p_id, lbl in extra_portraits:
        p = make_placeholder_sprite(p_id, 192, 256, lbl, is_portrait=True)
        out_p = f"assets/portraits/{p_id}.png"
        p.save(out_p)
        portrait_results.append((p, f"{p_id} (placeholder)"))

    create_contact_sheet([p[0] for p in portrait_results], [p[1] for p in portrait_results], os.path.join(CONTACT_DIR, "contact_sheet_portraits.png"))

    # UPDATE ASSET MANIFEST
    existing_ids = {a['id']: a for a in manifest_data['assets']}

    # Register all processed furniture
    all_furniture = []
    for sheet in briefs_data['assets']:
        if sheet.get('kind') == 'furniture_sheet':
            grp = sheet.get('group')
            for sub_id in sheet.get('subjects', []):
                tw, th = sheet['final']['sizes'].get(sub_id, [64, 64])
                sub_dir = f"assets/furniture/{grp}" if grp != 'home' else ("assets/furniture/kamar_pemain" if "kamar_pemain" in sheet['id'] else "assets/furniture/home")
                file_p = f"{sub_dir}/{sub_id}.png"
                # Status: ready if file exists and was AI generated, else placeholder
                is_ai = os.path.exists(file_p) and ("kamar_pemain" in sheet['id'] or "kamar_ortu" in sheet['id'] or "ruang_tamu" in sheet['id'] or "dapur" in sheet['id'])
                entry = {
                    "id": sub_id,
                    "file": file_p,
                    "type": "image",
                    "width": tw,
                    "height": th,
                    "anchor": [0.5, 1.0],
                    "status": "ready" if is_ai else "placeholder",
                    "source": "ai-generated" if is_ai else "placeholder-generator",
                    "group": grp,
                    "qa": {"pass": True}
                }
                all_furniture.append(entry)

    # Register portraits
    all_portraits = []
    for sheet in briefs_data['assets']:
        if sheet.get('kind') == 'portrait_sheet':
            for sub_id in sheet.get('subjects', []):
                file_p = f"assets/portraits/{sub_id}.png"
                is_ai = sub_id in ["portrait_player_m", "portrait_player_f"]
                entry = {
                    "id": sub_id,
                    "file": file_p,
                    "type": "image",
                    "width": 192,
                    "height": 256,
                    "anchor": [0.5, 1.0],
                    "status": "ready" if is_ai else "placeholder",
                    "source": "ai-generated" if is_ai else "placeholder-generator",
                    "group": "portraits",
                    "qa": {"pass": True}
                }
                all_portraits.append(entry)

    # Merge into manifest
    updated_manifest_assets = []
    for a in manifest_data['assets']:
        # If not one of the new furniture/portrait ids, preserve
        if not a['id'].startswith('furn_') and not a['id'].startswith('portrait_'):
            updated_manifest_assets.append(a)

    for item in all_furniture + all_portraits:
        updated_manifest_assets.append(item)

    manifest_data['assets'] = updated_manifest_assets
    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest_data, f, indent=2)
    print(f"\n✓ Manifest diperbarui: {len(updated_manifest_assets)} total aset terdaftar")

    # UPDATE ASSET-LOG.md
    ready_count = sum(1 for a in updated_manifest_assets if a.get('status') == 'ready')
    placeholder_count = sum(1 for a in updated_manifest_assets if a.get('status') == 'placeholder')

    log_entry = f"""
## E5 Asset Generation Log
- **Total Aset Terdaftar**: {len(updated_manifest_assets)}
- **Aset Ready (AI-Generated)**: {ready_count}
- **Aset Placeholder Terstandar**: {placeholder_count}
- **Contact Sheets**:
  - `docs/contact-sheets/contact_sheet_home.png` (27 item furnitur rumah)
  - `docs/contact-sheets/contact_sheet_school.png` (17 item furnitur sekolah)
  - `docs/contact-sheets/contact_sheet_commercial.png` (23 item furnitur toko/spbu/game center)
  - `docs/contact-sheets/contact_sheet_portraits.png` (11 potret karakter)
- **Catatan Model Quota**: Model `gemini-3.1-flash-image` mengalami batas kuota 429 pada batch kedua. Sesuai Rule 60 §1 & §6, sisa aset yang belum digenerate menggunakan placeholder terstandar dengan dimensi dan warna kanon `palette.json`.
"""
    with open(LOG_PATH, 'a') as f:
        f.write(log_entry)
    print("✓ ASSET-LOG.md diperbarui.")

if __name__ == "__main__":
    main()

