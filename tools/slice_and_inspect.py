import os
from PIL import Image
import numpy as np

os.makedirs('game/tools/sliced_props', exist_ok=True)

def chroma_key_crop(im_crop):
    arr = np.array(im_crop.convert('RGBA'))
    r = arr[:, :, 0].astype(float)
    g = arr[:, :, 1].astype(float)
    b = arr[:, :, 2].astype(float)
    
    # Distance to magenta (255, 0, 255)
    # Magenta has high R, high B, low G
    diff_r = np.abs(r - 255)
    diff_g = g
    diff_b = np.abs(b - 255)
    dist = np.sqrt(diff_r**2 + diff_g**2 + diff_b**2)
    
    # Alpha mask:
    # dist < 70 -> fully transparent (0)
    # dist > 140 -> fully opaque (255)
    # between -> linear transition
    alpha = np.clip((dist - 65) / (135 - 65) * 255, 0, 255).astype(np.uint8)
    
    # Also defringe near edges where alpha < 255
    edge = (alpha > 0) & (alpha < 255)
    # replace magenta tint with nearby dark/neutral color
    arr[alpha == 0] = [0, 0, 0, 0]
    arr[:, :, 3] = alpha
    
    res = Image.fromarray(arr, 'RGBA')
    bbox = res.getbbox()
    if bbox:
        res = res.crop(bbox)
    return res

def process_atlas(path, prefix, box_list):
    im = Image.open(path)
    for idx, (ymin, xmin, ymax, xmax, target_name) in enumerate(box_list):
        crop = im.crop((xmin, ymin, xmax, ymax))
        cleaned = chroma_key_crop(crop)
        out_path = f'game/tools/sliced_props/{prefix}_{idx}_{target_name}.png'
        cleaned.save(out_path)
        print(f"Saved {out_path} ({cleaned.size})")

# Let's inspect HOME boxes
