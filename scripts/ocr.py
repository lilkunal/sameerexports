import sys, json, glob, os
import numpy as np
from PIL import Image, ImageOps
from rapidocr_onnxruntime import RapidOCR

w = sys.argv[1]
os.makedirs(f"{w}/upright", exist_ok=True)
os.makedirs(f"{w}/ocr", exist_ok=True)
eng = RapidOCR()


def score(img):
    res, _ = eng(np.array(img))
    if not res:
        return 0, res
    return sum(float(r[2]) * len(r[1]) for r in res if float(r[2]) > 0.6), res


for f in sorted(glob.glob(f"{w}/raw/*.jpeg") + glob.glob(f"{w}/raw/*.jpg")):
    name = os.path.splitext(os.path.basename(f))[0]
    if os.path.exists(f"{w}/ocr/{name}.json"):
        continue
    im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
    small = im.copy()
    small.thumbnail((1400, 1400))
    best = max(((score(small.rotate(a, expand=True))[0], a) for a in (0, 90, 180, 270)))
    ang = best[1]
    up = im.rotate(ang, expand=True)
    up.save(f"{w}/upright/{name}.jpg", quality=92)
    big = up.copy()
    big.thumbnail((2600, 2600))
    _, res = score(big)
    lines = [{"text": r[1], "conf": float(r[2]), "box": [[int(p[0]), int(p[1])] for p in r[0]]} for r in (res or [])]
    json.dump({"rot": ang, "size": big.size, "lines": lines}, open(f"{w}/ocr/{name}.json", "w"))
    print(name, "rot", ang, len(lines), "lines", flush=True)
