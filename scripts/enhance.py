import sys, json, os
import numpy as np, cv2
w = sys.argv[1]
R = json.load(open(f'{w}/records_seg.json'))
os.makedirs(f'{w}/products/final', exist_ok=True)
os.makedirs(f'{w}/products/white', exist_ok=True)
ocr_cache = {}
flags = {}


def fillholes(m):
    h, wd = m.shape
    ff = m.copy(); mask = np.zeros((h + 2, wd + 2), np.uint8)
    cv2.floodFill(ff, mask, (0, 0), 255)
    return m | cv2.bitwise_not(ff)


for r in R:
    code = r['code']
    src = f'{w}/products/stage/{code}.jpg'
    if not os.path.exists(src): continue
    im = cv2.imread(src); mk = cv2.imread(f'{w}/products/stage/{code}_m.png', 0)
    H, Wd = im.shape[:2]
    # work copy
    sc = min(1.0, 560 / max(H, Wd))
    sm = cv2.resize(im, (int(Wd * sc), int(H * sc)), interpolation=cv2.INTER_AREA)
    mm = cv2.resize(mk, (sm.shape[1], sm.shape[0]), interpolation=cv2.INTER_NEAREST)
    mm = fillholes(cv2.morphologyEx(mm, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)))
    k = lambda v: np.ones((max(int(v * sc), 3),) * 2, np.uint8)
    gc = np.full(mm.shape, cv2.GC_BGD, np.uint8)
    gc[cv2.dilate(mm, k(22)) > 0] = cv2.GC_PR_BGD
    gc[mm > 0] = cv2.GC_PR_FGD
    gc[cv2.erode(mm, k(16)) > 0] = cv2.GC_FGD
    try:
        bgd = np.zeros((1, 65)); fgd = np.zeros((1, 65))
        if r.get('manual'):
            ys_, xs_ = np.where(mm > 0)
            rect = (int(xs_.min()) + 2, int(ys_.min()) + 2, int(xs_.max() - xs_.min()) - 4, int(ys_.max() - ys_.min()) - 4)
            gc = np.zeros(mm.shape, np.uint8)
            cv2.grabCut(sm, gc, rect, bgd, fgd, 5, cv2.GC_INIT_WITH_RECT)
        else:
            cv2.grabCut(sm, gc, None, bgd, fgd, 4, cv2.GC_INIT_WITH_MASK)
        a = np.where((gc == cv2.GC_FGD) | (gc == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    except Exception:
        a = mm
    # sanity: if grabcut ate too much, fall back to seg mask
    if a.sum() < 0.55 * mm.sum():
        a = mm
    cnts, _ = cv2.findContours(mm, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if cnts:
        hull = cv2.convexHull(np.vstack(cnts)); hm = np.zeros_like(mm); cv2.fillPoly(hm, [hull], 255)
        solid = (mm > 0).sum() / max((hm > 0).sum(), 1)
        if (a > 0).sum() < 0.75 * (mm > 0).sum() and solid > 0.72:
            a = hm
    a = cv2.morphologyEx(a, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(a)
    if n > 1:
        big = 1 + np.argmax(st[1:, 4]); keep = np.zeros_like(a)
        for i in range(1, n):
            if st[i, 4] > 0.04 * st[big, 4]: keep[lab == i] = 255
        a = keep
    a = fillholes(a)
    alpha = cv2.resize(a, (Wd, H), interpolation=cv2.INTER_LINEAR)
    alpha = cv2.GaussianBlur(alpha, (0, 0), 1.6)
    alpha = np.clip((alpha.astype(np.float32) - 40) * (255 / 175), 0, 255).astype(np.uint8)
    # white balance from paper (outside dilated mask)
    paper = im[cv2.dilate(mk, np.ones((41, 41), np.uint8)) == 0]
    f = im.astype(np.float32)
    if len(paper) > 400:
        p = np.median(paper, axis=0)
        gain = np.clip(p.max() / p, 0.85, 1.35)
        f = f * gain
    f = np.clip(f, 0, 255).astype(np.uint8)
    f = cv2.fastNlMeansDenoisingColored(f, None, 3, 3, 5, 15)
    lab_ = cv2.cvtColor(f, cv2.COLOR_BGR2LAB)
    cl = cv2.createCLAHE(clipLimit=1.8, tileGridSize=(4, 4))
    lab_[:, :, 0] = cl.apply(lab_[:, :, 0])
    f = cv2.cvtColor(lab_, cv2.COLOR_LAB2BGR)
    # crop to alpha bbox
    ys, xs = np.where(alpha > 30)
    if len(xs) == 0: continue
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    pad = 8
    y0, x0 = max(y0 - pad, 0), max(x0 - pad, 0); y1, x1 = min(y1 + pad, H), min(x1 + pad, Wd)
    f, alpha = f[y0:y1, x0:x1], alpha[y0:y1, x0:x1]
    # upscale small ones (long side -> >= 900, max 2.5x), then unsharp
    long_ = max(f.shape[:2]); up = min(max(900 / long_, 1.0), 2.5)
    if up > 1.01:
        f = cv2.resize(f, None, fx=up, fy=up, interpolation=cv2.INTER_LANCZOS4)
        alpha = cv2.resize(alpha, (f.shape[1], f.shape[0]), interpolation=cv2.INTER_LINEAR)
    blur = cv2.GaussianBlur(f, (0, 0), 1.4)
    f = cv2.addWeighted(f, 1.6, blur, -0.6, 0)
    rgba = np.dstack([f, alpha])
    cv2.imwrite(f'{w}/products/final/{code}.png', rgba, [cv2.IMWRITE_PNG_COMPRESSION, 6])
    al = (alpha.astype(np.float32) / 255)[:, :, None]
    white = (f * al + 255 * (1 - al)).astype(np.uint8)
    cv2.imwrite(f'{w}/products/white/{code}.jpg', white, [cv2.IMWRITE_JPEG_QUALITY, 92])
    flags[code] = dict(w=int(f.shape[1]), h=int(f.shape[0]), fill=round(float((alpha > 128).mean()), 2), shared=bool(r.get('shared')))
json.dump(flags, open(f'{w}/products/flags.json', 'w'))
print(len(flags), 'done')
