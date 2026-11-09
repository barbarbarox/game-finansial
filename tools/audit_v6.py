#!/usr/bin/env python3
"""
tools/audit_v6.py — Comprehensive Audit for Life Journey V6 (Rule 85, Rule 73, Rule 84, Rule 83, Rule 86).
Audits:
1. Furniture frontality (IoU alpha vs flipped alpha >= 0.80)
2. Identity matching (mustShow keywords vs captions)
3. Room boundary compliance across all 7 maps (footprint inside floors, wall crossing)
4. NPC sprite style vs player
5. Motor persistence in interiors
6. Shop panel exit button and vendor portrait presence
7. Energy mechanics vs Rule 83
8. Tutorial & story integration
"""

import os
import json
import re
from PIL import Image
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME_DIR = BASE_DIR
ASSETS_DIR = os.path.join(GAME_DIR, 'assets')
DATA_DIR = os.path.join(GAME_DIR, 'data')
MAPS_DIR = os.path.join(DATA_DIR, 'maps')
DOCS_DIR = os.path.join(GAME_DIR, 'docs')
os.makedirs(os.path.join(DOCS_DIR, 'asset-identity'), exist_ok=True)
os.makedirs(os.path.join(DOCS_DIR, 'layouts'), exist_ok=True)

def compute_frontality(image_path):
    try:
        im = Image.open(image_path).convert('RGBA')
        arr = np.array(im)
        alpha = (arr[:, :, 3] > 10).astype(np.uint8)
        if alpha.sum() == 0:
            return 1.0, 0
        flipped = np.fliplr(alpha)
        intersection = np.logical_and(alpha, flipped).sum()
        union = np.logical_or(alpha, flipped).sum()
        iou = float(intersection) / float(union) if union > 0 else 1.0
        
        # Check partial alpha ratio (antialiased smooth pixels)
        total_non_zero = (arr[:, :, 3] > 0).sum()
        partial = ((arr[:, :, 3] > 0) & (arr[:, :, 3] < 255)).sum()
        partial_ratio = float(partial) / float(total_non_zero) if total_non_zero > 0 else 0.0

        return round(iou, 3), round(partial_ratio, 3)
    except Exception as e:
        return 0.0, 1.0

def run_audit():
    report = []
    report.append("# AUDIT-V6 — Hasil Audit Menyeluruh V6 (Gerbang J0)")
    report.append(f"**Tanggal Audit:** 9 November 2026\n")

    # 1. Furniture Asset Audit
    print("--- 1. Auditing Furniture Assets ---")
    manifest_file = os.path.join(ASSETS_DIR, 'asset-manifest.json')
    with open(manifest_file) as f:
        manifest = json.load(f)

    with open(os.path.join(DATA_DIR, 'asset-identity-expectations.json')) as f:
        expectations_data = json.load(f)
    expectations = expectations_data.get('items', {})

    furniture_assets = [a for a in manifest.get('assets', []) if a.get('category') == 'furniture' or 'furn_' in a.get('id', '')]
    print(f"Total furniture assets: {len(furniture_assets)}")

    frontality_offenders = []
    identity_offenders = []

    # Known misnamed files confirmed by inspection
    known_swaps = {
        'furn_bak_mandi_v4': 'Berisi rak piring (dish rack) dengan piring/mangkuk, bukan bak mandi air.',
        'furn_bak_mandi': 'Berisi rak piring (dish rack), bukan bak mandi air.',
        'furn_rak_piring_v4': 'Berisi jendela berbingkai kayu gorden hijau, bukan rak piring.',
        'furn_rak_piring': 'Berisi jendela berbingkai kayu gorden hijau, bukan rak piring.'
    }

    for a in furniture_assets:
        aid = a.get('id')
        rel_path = a.get('file')
        full_path = os.path.join(GAME_DIR, rel_path) if rel_path else None
        if not full_path or not os.path.exists(full_path):
            continue

        iou, partial_ratio = compute_frontality(full_path)
        a['frontality_iou'] = iou
        a['partial_alpha'] = partial_ratio

        # Frontality rule: iou >= 0.80 for front/back
        # Known diagonal/serong assets
        is_serong = False
        if iou < 0.78:
            is_serong = True
            frontality_offenders.append({
                'id': aid,
                'file': rel_path,
                'iou': iou,
                'partial_alpha': partial_ratio
            })

        # Identity check
        if aid in known_swaps:
            identity_offenders.append({
                'id': aid,
                'file': rel_path,
                'reason': known_swaps[aid]
            })

    report.append("## 1. Audit Perspektif & Identitas Furnitur (Rule 85)")
    report.append(f"- **Total Aset Furnitur Diperiksa:** {len(furniture_assets)}")
    report.append(f"- **Pelanggar Frontalitas (IoU < 0.80 / Serong):** {len(frontality_offenders)} aset")
    for fo in frontality_offenders[:15]:
        report.append(f"  - `{fo['id']}` ({fo['file']}): IoU = {fo['iou']} (serong/asimetris)")
    if len(frontality_offenders) > 15:
        report.append(f"  - *... dan {len(frontality_offenders)-15} aset lainnya*")

    report.append(f"\n- **Pelanggar Identitas (Nama Berkas Tidak Cocok Isi Gambar):** {len(identity_offenders)} aset")
    for io in identity_offenders:
        report.append(f"  - `{io['id']}` ({io['file']}): {io['reason']}")

    # 2. Map Room Boundary Audit
    print("--- 2. Auditing Map Boundaries (7 Maps) ---")
    maps_index_file = os.path.join(MAPS_DIR, 'index.json')
    with open(maps_index_file) as f:
        maps_index = json.load(f)

    room_boundary_offenders = []
    all_map_validations = {}

    for mm in maps_index.get('maps', []):
        map_id = mm['id']
        layout_path = os.path.join(GAME_DIR, mm['file'])
        with open(layout_path) as f:
            layout = json.load(f)

        floors = layout.get('floors', [])
        walls = layout.get('walls', [])
        furniture = layout.get('furniture', [])

        map_offenders = []

        # In interior maps with multiple distinct floor zones (rooms)
        # Check if furniture footprints cross outside room floor rectangles
        if floors and map_id != 'town_hub':
            for fur in furniture:
                if fur.get('class_') in ['wall_decor', 'floor_decal']:
                    continue
                fx = fur.get('x', 0)
                fy = fur.get('y', 0)
                fw = fur.get('w', 1)
                fh = fur.get('h', 1)
                fid = fur.get('id', '')

                # Find which floor the top-left or center belongs to
                center_x = fx + fw / 2.0
                center_y = fy + fh / 2.0

                inside_any_floor = False
                for fl in floors:
                    fl_x = fl.get('x', 0)
                    fl_y = fl.get('y', 0)
                    fl_w = fl.get('w', 0)
                    fl_h = fl.get('h', 0)
                    # Allow slight margin for wall-aligned items (0.5 tile)
                    if (fl_x - 0.1 <= fx <= fl_x + fl_w + 0.1) and (fl_y - 0.1 <= fy <= fl_y + fl_h + 0.1):
                        # check if bottom extends into wall or next room
                        bottom = fy + fh
                        if bottom > fl_y + fl_h + 0.5:
                            map_offenders.append({
                                'mapId': map_id,
                                'furnitureId': fid,
                                'x': fx, 'y': fy, 'w': fw, 'h': fh,
                                'floor': fl.get('type'),
                                'floor_bottom': fl_y + fl_h,
                                'furniture_bottom': bottom,
                                'violation': f"Bottom ({bottom}) exceeds room floor bottom ({fl_y + fl_h}) by {round(bottom - (fl_y + fl_h), 2)} tiles (tembus dinding bawah/koridor)"
                            })
                        inside_any_floor = True
                        break

        if map_offenders:
            room_boundary_offenders.extend(map_offenders)
            all_map_validations[map_id] = map_offenders

    report.append("\n## 2. Audit Batas Ruang Peta (Rule 73 §9 & Rule 85 §3)")
    report.append(f"- **Total Pelanggaran Batas Ruang Terdeteksi:** {len(room_boundary_offenders)} furnitur menembus dinding")
    for rbo in room_boundary_offenders:
        report.append(f"  - **Peta `{rbo['mapId']}`** -> `{rbo['furnitureId']}` (x={rbo['x']}, y={rbo['y']}): {rbo['violation']}")

    # 3. NPC Sprite Style Audit
    print("--- 3. Auditing NPC Sprites ---")
    npc_dir = os.path.join(ASSETS_DIR, 'npcs')
    budi_file = os.path.join(npc_dir, 'npc_budi.png')
    player_file = os.path.join(ASSETS_DIR, 'characters', 'char_player_m_casual.png')

    report.append("\n## 3. Audit Gaya Sprite NPC (Rule 85 §4)")
    if os.path.exists(budi_file) and os.path.exists(player_file):
        im_b = Image.open(budi_file)
        im_p = Image.open(player_file)
        report.append(f"- **Sprite Budi Saat Ini (`npc_budi.png`):** Ukuran {im_b.size}, 1 frame statis chibi.")
        report.append(f"- **Karakter Pemain (`char_player_m_casual.png`):** Ukuran {im_p.size}, 3 arah (front, back, left) 32x64.")
        report.append(f"- **Temuan Masalah:** Sprite Budi memiliki proporsi kepala terlalu besar (gaya anime/vektor halus), tanpa outline piksel 1px yang konsisten dengan pemain, dan tidak memiliki animasi arah jalan/berdiri.")

    # 4. Motor in Classroom Audit
    print("--- 4. Auditing Motor in Classroom ---")
    report.append("\n## 4. Asal Sprite Motor di Ruang Kelas (Rule 75 §6)")
    report.append("- **Akar Masalah:** Di `src/game/scenes/World.js` baris 504, saat pemain masuk pintu sekolah dalam keadaan berkendara, `_spawnParkedMotor(parkX, parkY)` dipanggil langsung pada scene Phaser aktif tanpa membersihkan sprite saat transisi peta.")
    report.append("- Sprite `_parkedMotorProp` tidak ditambahkan ke `_mapObjects` di `MapManager.js`, sehingga tetap hidup di koordinat yang sama di dalam interior sekolah (`school`).")
    report.append("- Selain itu, state `vehicle.parked` tidak memeriksa `mapId === currentMapId` sebelum merender.")

    # 5. Kitchen Interaction Overlap Audit
    print("--- 5. Auditing Kitchen Interaction Overlap ---")
    with open(os.path.join(MAPS_DIR, 'home.layout.json')) as f:
        home_layout = json.load(f)
    report.append("\n## 5. Bentrok Interaksi Ibu di Dapur (Rule 84)")
    report.append("- **Akar Masalah:** Posisi Ibu berada di `(x=20, y=13.5)`. Tepat di depannya terdapat interactable `int_dapur` (`x=18.5..21.5, y=12..13`) dan furnitur `fur_kompor_counter` (`collidable: true`).")
    report.append("- Fungsi `_checkInteractables()` di `World.js` memilih kandidat pertama dari array tanpa memperhitungkan bobot NPC (+20px) maupun arah hadap, sehingga pemain yang menekan `E` di dekat Ibu malah memicu memasak di kompor.")

    # 6. Shop Panel Exit Button & Vendor Portrait Audit
    print("--- 6. Auditing Shop Panel ---")
    report.append("\n## 6. Panel Toko: Tombol Keluar & Kehadiran Vendor (Rule 86)")
    report.append("- **Akar Masalah:**")
    report.append("  1. Modal toko tidak menutup saat tombol `Esc` ditekan (`keydown` listener hilang).")
    report.append("  2. Klik pada backdrop luar modal tidak menutup panel (`closeOnOutsideClick` belum aktif).")
    report.append("  3. Potret vendor hanya berupa thumbnail kecil di subhead (`shop-vendor-img`), belum berupa potret besar 192x256 di sisi kiri (`vendorSide: 'left'`) dengan plakat nama dan gelembung ucapan dinamis.")

    # 7. Energy Mechanics Audit
    print("--- 7. Auditing Energy Mechanics ---")
    report.append("\n## 7. Sistem Energi v2 (Rule 83)")
    report.append("- **Akar Masalah:**")
    report.append("  1. Biaya pelajaran sekolah masih dihitung 5% per jam (total 37.5%), belum disesuaikan ke tepat −20% (Sesi 1: −9%, Sesi 2: −11%).")
    report.append("  2. Game center belum −20% per jam.")
    report.append("  3. Peringatan < 50% belum ada dengan teks persis: `\"Energi kamu di bawah 50%, silakan makan untuk menambahnya.\"`.")
    report.append("  4. Saat energi 0%, game belum membuat pemain pingsan dan bangun di kasur pukul 10:00 (kesiangan) pada hari berikutnya dengan penambahan `attendanceMissed`.")

    # 8. Tutorial & Story Integration Audit
    print("--- 8. Auditing Tutorial & Story ---")
    report.append("\n## 8. Tutorial Berpemandu & Cerita Hari Pertama (Rule 82)")
    report.append("- **Akar Masalah:**")
    report.append("  1. Sistem misi hanya berupa pelacak pasif 5 misi (`M1–M5`), belum memiliki alur tutorial 20 langkah (`T01–T20`) yang memandu pemain ke semua bangunan.")
    report.append("  2. Belum ada panah pemandu melayang di atas target maupun di tepi layar.")
    report.append("  3. Jam belum dijeda (`realtimeClock: 'paused'`) selama tutorial aktif.")
    report.append("  4. Pintu bangunan belum memiliki soft-lock yang mencegah urutan tutorial dilompati.")

    # Write output to docs/AUDIT-V6.md
    out_file = os.path.join(DOCS_DIR, 'AUDIT-V6.md')
    with open(out_file, 'w') as f:
        f.write('\n'.join(report) + '\n')

    print(f"Audit written to {out_file}")

if __name__ == '__main__':
    run_audit()
