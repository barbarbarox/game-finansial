#!/usr/bin/env python3
"""
check_plate_conformance.py - Conformance and IoU validation for terrain plate against town_hub guide masks.
Follows Rule 76 §2 & §5.
"""

import os
import sys
import numpy as np
from PIL import Image

def compute_iou(mask_gt, mask_pred):
    intersection = np.logical_and(mask_gt > 127, mask_pred > 127).sum()
    union = np.logical_or(mask_gt > 127, mask_pred > 127).sum()
    if union == 0:
        return 1.0
    return float(intersection) / float(union)

def validate_plate(plate_path, report_path=None, heatmap_path=None):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    masks_dir = os.path.join(base_dir, "assets", "terrain", "guide_masks")
    
    if not os.path.exists(plate_path):
        print(f"Error: Plate image not found: {plate_path}")
        return False, {}

    plate = Image.open(plate_path).convert("RGB")
    width, height = plate.size

    mask_files = {
        "jalan": "mask_jalan.png",
        "trotoar": "mask_trotoar.png",
        "halaman": "mask_halaman.png",
        "rumput": "mask_rumput.png",
        "marka": "mask_marka.png"
    }

    gt_masks = {}
    for name, f in mask_files.items():
        p = os.path.join(masks_dir, f)
        if not os.path.exists(p):
            print(f"Error: Missing ground truth mask {p}")
            return False, {}
        m = Image.open(p).convert("L")
        if m.size != (width, height):
            m = m.resize((width, height), Image.Resampling.NEAREST)
        gt_masks[name] = np.array(m)

    plate_arr = np.array(plate)
    # Color centroids (RGB):
    # jalan: dark grey (~50, 56, 68)
    # trotoar: light grey (~145, 155, 165)
    # halaman: sandy warm (~195, 170, 130)
    # rumput: green (~74, 124, 89)
    # marka: bright yellow/white (> 200, 200, 180)
    
    # Rule 76 §2: Centroid warna kelas dari hasil (computed dynamically from GT regions)
    centroids = {}
    for name in ["jalan", "trotoar", "halaman", "rumput", "marka"]:
        m = gt_masks[name]
        pts = plate_arr[m > 127]
        if len(pts) > 0:
            centroids[name] = pts.mean(axis=0)
        else:
            centroids[name] = np.array([128, 128, 128])
    
    print("Computed class centroids from image:")
    for name, c in centroids.items():
        print(f"  {name:<8}: RGB {c.astype(int)}")

    # Classify each pixel to nearest centroid
    flat_pixels = plate_arr.reshape(-1, 3).astype(float)
    class_names = list(centroids.keys())
    dists = []
    for name in class_names:
        c = centroids[name].astype(float)
        d = np.linalg.norm(flat_pixels - c, axis=1)
        dists.append(d)
    dists = np.array(dists) # shape: (num_classes, N)
    pred_idx = np.argmin(dists, axis=0) # shape: (N,)
    pred_idx_2d = pred_idx.reshape(height, width)

    eval_classes = ["jalan", "trotoar", "halaman", "rumput"]
    ious = {}
    passed = True
    print("\n--- Terrain Plate Conformance Report (Rule 76) ---")
    print(f"Plate: {plate_path} ({width}x{height})")
    print(f"{'Class':<12} | {'IoU':<8} | {'Status (>= 0.85)'}")
    print("-" * 38)

    diff_map = np.zeros((height, width, 3), dtype=np.uint8)

    for name in eval_classes:
        if name == "jalan":
            # Road network consists of dark asphalt + road markings
            pred_mask = np.logical_or(pred_idx_2d == class_names.index("jalan"),
                                      pred_idx_2d == class_names.index("marka")).astype(np.uint8) * 255
        elif name == "trotoar":
            # Sidewalk
            pred_mask = (pred_idx_2d == class_names.index("trotoar")).astype(np.uint8) * 255
        else:
            i = class_names.index(name)
            pred_mask = (pred_idx_2d == i).astype(np.uint8) * 255
        
        gt_mask = gt_masks[name]
        iou = compute_iou(gt_mask, pred_mask)
        ious[name] = iou
        status = "PASS" if iou >= 0.85 else "FAIL"
        if iou < 0.85:
            passed = False
        print(f"{name:<12} | {iou:<8.4f} | {status}")

        # Add differences to diff_map
        mismatch = np.logical_xor(gt_mask > 127, pred_mask > 127)
        if name == "jalan":
            diff_map[mismatch, 0] = 255  # Red for road mismatch
        elif name == "trotoar":
            diff_map[mismatch, 2] = 255  # Blue for sidewalk mismatch
        else:
            diff_map[mismatch, 1] = 200  # Greenish for yard/grass mismatch

    overall_status = "PASS (Level 1 Suitable)" if passed else "FAIL (Triggers Level 2 Fallback)"
    print(f"\nOverall Conformance: {overall_status}\n")

    if heatmap_path:
        os.makedirs(os.path.dirname(heatmap_path), exist_ok=True)
        # Blend diff_map over plate
        blend = Image.blend(plate, Image.fromarray(diff_map), alpha=0.45)
        blend.save(heatmap_path)
        print(f"Saved difference heatmap to: {heatmap_path}")

    if report_path:
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Terrain Plate Conformance Report\n\n")
            f.write(f"- Plate: `{plate_path}`\n")
            f.write(f"- Dimensions: {width}x{height}\n")
            f.write(f"- Conformance Result: **{overall_status}**\n\n")
            f.write("| Kelas Tanah | IoU | Ambang Batas | Status |\n")
            f.write("|---|---|---|---|\n")
            for name in eval_classes:
                f.write(f"| `{name}` | {ious[name]:.4f} | 0.8500 | {'LULUS' if ious[name] >= 0.85 else 'TIDAK LULUS'} |\n")
        print(f"Saved report to: {report_path}")

    return passed, ious

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 check_plate_conformance.py <plate_path> [report_path] [heatmap_path]")
        sys.exit(1)
    p_path = sys.argv[1]
    r_path = sys.argv[2] if len(sys.argv) > 2 else None
    h_path = sys.argv[3] if len(sys.argv) > 3 else None
    validate_plate(p_path, r_path, h_path)
