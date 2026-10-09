import sys, json, os, re, glob
import numpy as np, cv2
from PIL import Image
w = sys.argv[1]
d = json.load(open(f'{w}/parsed.json'))
R, P = d['recs'], d['pages']
FIX = {('A06', 'SE-3014'): 'SE-2014', ('A13', 'SE-100014'): 'SE-10014', 
       ('A24', 'SE-240010'): 'SE-24010', ('B02', 'SE-2816'): 'SE-28016', ('B09', 'SE-380114'): 'SE-38014',
       ('B14', 'SE-410572'): 'SE-41072', ('B20', 'SE-35001'): 'SE-50001', ('B22', 'SE-44007'): 'SE-51007'}
for r in R:
    r['code'] = FIX.get((r['page'], r['code']), r['code'])
ALIAS_DROP = {('A17', 'SE-14008')}
R = [r for r in R if (r['page'], r['code']) not in ALIAS_DROP]
os.makedirs(f'{w}/products/raw', exist_ok=True)
imgs = {}
ocr = {}
for pg in P:
    imgs[pg] = cv2.imread(f'{w}/upright/{pg}.jpg')
    ocr[pg] = json.load(open(f'{w}/ocr/{pg}.json'))
meta = {}
for r in R:
    pg = r['page']; im = imgs[pg]; Wd, Ht = P[pg]['W'], P[pg]['H']
    s = im.shape[1] / Wd
    same_row = [o for o in R if o['page'] == pg and o is not r and abs(o['y'] - r['y']) < 70 and o['x'] != r['x']]
    pitch = min([abs(o['x'] - r['x']) for o in same_row] + [330])
    cx = (r['x'] + r['x1']) / 2
    hw = min(max(pitch * 0.55, 120), 230)
    x0, x1 = cx - hw, cx + hw
    ybot = r['y'] - 3
    ytop = ybot - 560
    for l in ocr[pg]['lines']:
        xs = [p[0] for p in l['box']]; ys = [p[1] for p in l['box']]
        if min(xs) < x1 and max(xs) > x0 and max(ys) < ybot - 90 and max(ys) > ytop:
            ytop = max(ytop, max(ys) + 4)
    ytop = max(ytop, 150)
    box = [int(max(x0, 0) * s), int(ytop * s), int(min(x1, Wd) * s), int(ybot * s)]
    c = im[box[1]:box[3], box[0]:box[2]]
    if c.size == 0:
        continue
    # trim to foreground: differs from paper (border median)
    border = np.concatenate([c[:6].reshape(-1, 3), c[-6:].reshape(-1, 3), c[:, :6].reshape(-1, 3), c[:, -6:].reshape(-1, 3)])
    bg = np.median(border, axis=0)
    diff = np.abs(c.astype(int) - bg).max(axis=2)
    m = (diff > 40).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    red = ((c[:, :, 2] > 140) & (c[:, :, 1] < 95) & (c[:, :, 0] < 95)).astype(np.uint8)
    cxl = (cx - box[0] / s) * s
    keep = []
    for i in range(1, n):
        if st[i, 4] < 0.004 * m.size: continue
        comp = lab == i
        if red[comp].mean() > 0.2: continue
        if st[i, 0] > 0.7 * c.shape[1] or st[i, 0] + st[i, 2] < 0.3 * c.shape[1]: continue
        keep.append(i)
    if keep:
        xa = min(st[i, 0] for i in keep); ya = min(st[i, 1] for i in keep)
        xb = max(st[i, 0] + st[i, 2] for i in keep); yb = max(st[i, 1] + st[i, 3] for i in keep)
        pad = 12
        c = c[max(ya - pad, 0):yb + pad, max(xa - pad, 0):xb + pad]
    cv2.imwrite(f'{w}/products/raw/{r["code"]}.jpg', c, [cv2.IMWRITE_JPEG_QUALITY, 95])
    meta[r['code']] = dict(h=c.shape[0], w=c.shape[1])
json.dump(R, open(f'{w}/records_fixed.json', 'w'), indent=1)
print(len(meta), 'crops')
