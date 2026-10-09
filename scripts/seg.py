import sys, json, os
import numpy as np, cv2
w = sys.argv[1]
only = sys.argv[2] if len(sys.argv) > 2 else None
OV = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'overrides.json')))
R = json.load(open(f'{w}/records_fixed.json'))
pages = sorted({r['page'] for r in R})
os.makedirs(f'{w}/products/stage', exist_ok=True)
os.makedirs(f'{w}/debug', exist_ok=True)
assign = {}
for pg in pages:
    if only and pg != only: continue
    ocr = json.load(open(f'{w}/ocr/{pg}.json'))
    Wd, Ht = ocr['size']
    full = cv2.imread(f'{w}/upright/{pg}.jpg')
    s = full.shape[1] / Wd
    img = cv2.resize(full, (Wd, Ht), interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    gray = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (5, 5), 0)
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0); gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1)
    edge = (np.hypot(gx, gy) > 70).astype(np.uint8)
    edge = cv2.dilate(edge, np.ones((5, 5), np.uint8))
    small = cv2.resize(gray, (Wd // 8, Ht // 8), interpolation=cv2.INTER_AREA)
    bgs = cv2.medianBlur(small, 81)
    bg = cv2.resize(bgs, (Wd, Ht), interpolation=cv2.INTER_LINEAR)
    dev = (cv2.GaussianBlur(np.abs(gray.astype(np.int16) - bg.astype(np.int16)).astype(np.uint8), (7, 7), 0) > 22).astype(np.uint8)
    fg = (((hsv[:, :, 1] > 70) & (hsv[:, :, 2] > 60)) | (hsv[:, :, 2] < 85) | (edge > 0) | ((dev > 0) if pg in ('A24', 'A25') else 0)).astype(np.uint8)
    # mask out OCR text (pad) and header
    hdr = 0
    for l in ocr['lines']:
        xs = [p[0] for p in l['box']]; ys = [p[1] for p in l['box']]
        if (max(ys) - min(ys)) > 60 and max(ys) > 400 and len(l['text'].strip()) < 4: continue
        px, py = (34, 16) if l['text'].strip().upper().replace(' ','').startswith('SE') else (10, 8)
        fg[max(min(ys) - py, 0):max(ys) + py, max(min(xs) - px, 0):max(xs) + px] = 0
        if ('Exports' in l['text'] or 'Sameer' in l['text']) and max(ys) < 400:
            hdr = max(hdr, max(ys))
    fg[:hdr + 62 if hdr else 150] = 0
    red = ((img[:, :, 2] > 140) & (img[:, :, 1] < 95) & (img[:, :, 0] < 95)).astype(np.uint8)
    fg[cv2.dilate(red, np.ones((9, 9), np.uint8)) > 0] = 0
    fg[-60:] = 0
    fg[:, :20] = 0; fg[:, -20:] = 0
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    thin = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((70, 1), np.uint8)) & ~cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((70, 9), np.uint8))
    fg[cv2.dilate(thin, np.ones((3, 5), np.uint8)) > 0] = 0
    n0, lab0, st0, _ = cv2.connectedComponentsWithStats(fg)
    for i in range(1, n0):
        x, y, cw, ch, a = st0[i]
        if (ch > 160 and cw < 18) or (cw > 160 and ch < 18):
            fg[lab0 == i] = 0
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    n, lab, st, cen = cv2.connectedComponentsWithStats(fg)
    recs = [r for r in R if r['page'] == pg]
    for r in recs:
        r['cx'] = (r['x'] + r['x1']) / 2
    prim, frag = [], []
    for i in range(1, n):
        x, y, cw, ch, a = st[i]
        if a < 700 or a > 0.2 * Wd * Ht: continue
        if cw > 6 * ch and ch < 40: continue
        if ch > 8 * cw and cw < 30: continue
        if ch > 0.55 * Ht and cw < 90: continue
        (prim if a >= 3500 else frag).append(i)
    def rd(a, b):
        dx = max(a[0] - b[2], b[0] - a[2], 0); dy = max(a[1] - b[3], b[1] - a[3], 0)
        return (dx * dx + dy * dy) ** 0.5
    def lbl(r):
        return (r['x'] - 40, r['y'] - 4, r['x'] + 270, r['y'] + 125)
    cost = np.zeros((len(recs), len(prim)))
    for j, i in enumerate(prim):
        x, y, cw, ch, a = st[i]
        cb = (x, y, x + cw, y + ch)
        ys, xs = np.where(lab[y:y + ch, x:x + cw] == i)
        sel = ys > ch * 0.8
        bx = xs[sel].mean() + x if sel.any() else x + cw / 2
        for k, r in enumerate(recs):
            L = lbl(r)
            c = rd(L, cb) + 0.3 * abs(bx - r['cx'])
            if y + ch / 2 > r['y'] + 20: c += 400 + (y + ch / 2 - r['y'])
            cost[k, j] = c
    from scipy.optimize import linear_sum_assignment
    comps = {}
    if len(prim):
        rows, cols = linear_sum_assignment(cost)
        for k, j in zip(rows, cols):
            if cost[k, j] < 700: comps.setdefault(recs[k]['code'], []).append(prim[j])
        got = {recs[k]['code'] for k in rows if cost[k, cols[list(rows).index(k)]] < 700}
        for k, r in enumerate(recs):
            if r['code'] not in got:
                j = int(cost[k].argmin())
                if cost[k, j] < 500: comps.setdefault(r['code'], []).append(prim[j]); r['shared'] = True
    # attach fragments to the group of the nearest primary within 45px
    owner = {i: c for c, ids in comps.items() for i in ids}
    for i in frag:
        x, y, cw, ch, a = st[i]; cb = (x, y, x + cw, y + ch)
        best, bo = 45, None
        for j in prim:
            if j in owner:
                x2, y2, w2, h2, _ = st[j]
                d = rd(cb, (x2, y2, x2 + w2, y2 + h2))
                if d < best: best, bo = d, owner[j]
        if bo: comps[bo].append(i)
    vis = img.copy()
    for r in recs:
        ids = comps.get(r['code'])
        if r['code'] in OV:
            f = Wd / 1800.0; bx = [int(v * f) for v in OV[r['code']]]
            m = np.zeros(lab.shape, bool); m[bx[1]:bx[3] + 1, bx[0]:bx[2] + 1] = True
            r['manual'] = True
        elif not ids:
            r['seg'] = None; continue
        else:
            m = np.isin(lab, ids)
        ys, xs = np.where(m)
        x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
        r['seg'] = [int(x0), int(y0), int(x1), int(y1)]
        cv2.rectangle(vis, (x0, y0), (x1, y1), (0, 0, 255), 3)
        cv2.putText(vis, r['code'], (x0, y0 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
        mk = (m[y0:y1 + 1, x0:x1 + 1]).astype(np.uint8) * 255
        # full-res crop of page with the mask region
        X0, Y0, X1, Y1 = [int(v * s) for v in (x0, y0, x1 + 1, y1 + 1)]
        pad = int(14 * s)
        cr = full[max(Y0 - pad, 0):Y1 + pad, max(X0 - pad, 0):X1 + pad]
        mk_full = cv2.resize(np.pad(mk, 0), (X1 - X0, Y1 - Y0), interpolation=cv2.INTER_NEAREST)
        mk_pad = np.zeros(cr.shape[:2], np.uint8)
        oy, ox = Y0 - max(Y0 - pad, 0), X0 - max(X0 - pad, 0)
        mk_pad[oy:oy + mk_full.shape[0], ox:ox + mk_full.shape[1]] = mk_full
        cv2.imwrite(f'{w}/products/stage/{r["code"]}.jpg', cr, [cv2.IMWRITE_JPEG_QUALITY, 95])
        cv2.imwrite(f'{w}/products/stage/{r["code"]}_m.png', mk_pad)
    cv2.imwrite(f'{w}/debug/{pg}.jpg', cv2.resize(vis, (1800, int(1800 * Ht / Wd))))
    miss = [r['code'] for r in recs if not r.get('seg')]
    print(pg, len(recs), 'miss', miss, flush=True)
json.dump(R, open(f'{w}/records_seg.json', 'w'), indent=1)
