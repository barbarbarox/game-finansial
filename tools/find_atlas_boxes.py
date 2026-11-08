import sys
from PIL import Image
import numpy as np
from scipy import ndimage

def analyze(path, name):
    im = Image.open(path).convert('RGB')
    arr = np.array(im)
    r = arr[:, :, 0].astype(int)
    g = arr[:, :, 1].astype(int)
    b = arr[:, :, 2].astype(int)
    
    # Magenta threshold: High R and B, Low G
    # or (R > 180 and B > 180 and G < 80)
    is_magenta = (r > 160) & (b > 160) & (g < 100)
    foreground = ~is_magenta
    
    labeled, num_features = ndimage.label(foreground)
    print(f"\n=== {name} ({num_features} raw components) ===")
    
    objects = ndimage.find_objects(labeled)
    boxes = []
    for idx, sl in enumerate(objects):
        ymin, ymax = sl[0].start, sl[0].stop
        xmin, xmax = sl[1].start, sl[1].stop
        w = xmax - xmin
        h = ymax - ymin
        area = w * h
        if w >= 20 and h >= 20 and area > 600:
            boxes.append((ymin, xmin, ymax, xmax, w, h, area))
            
    # Sort top-to-bottom, left-to-right
    boxes.sort(key=lambda b: (b[0] // 80, b[1]))
    print(f"Significant boxes ({len(boxes)}):")
    for i, b in enumerate(boxes):
        print(f"  [{i}] y={b[0]}..{b[2]}, x={b[1]}..{b[3]} (w={b[4]}, h={b[5]}, area={b[6]})")

analyze('/home/abarox/.gemini/antigravity/brain/4d2f9b08-f034-4550-b619-39a74fd29f25/indonesian_furniture_spritesheet_1794154709614.jpg', 'HOME')
analyze('/home/abarox/.gemini/antigravity/brain/4d2f9b08-f034-4550-b619-39a74fd29f25/arcade_boutique_props_spritesheet_1794154749207.jpg', 'ARCADE_BOUTIQUE')
analyze('/home/abarox/.gemini/antigravity/brain/4d2f9b08-f034-4550-b619-39a74fd29f25/indonesian_school_interior_props_atlas_1794154814669.jpg', 'SCHOOL')
analyze('/home/abarox/.gemini/antigravity/brain/4d2f9b08-f034-4550-b619-39a74fd29f25/minimarket_spbu_props_atlas_1794154814680.jpg', 'MINI_SPBU')
