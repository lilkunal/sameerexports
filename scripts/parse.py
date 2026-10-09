import sys, json, glob, re, os
w = sys.argv[1]
CODE = re.compile(r'^\W*S[eE][\s\-–—.]?\s?(\d{3,6})\W*$')
CODE_IN = re.compile(r'S[eE][\s\-–—.]?(\d{4,6})')
SKIP = {'sameer', 'exports', 'exports.', 'sameer exports'}
WORDS = ['Tower', 'Bolt', 'Naked', 'Door', 'Knocker', 'Finish', 'Rod', 'Hinge', 'Handle', 'Knob', 'Oval', 'Flush', 'Size', 'Available', 'sizes', 'Brass', 'Pull', 'Stay', 'Hook', 'Latch', 'Lock', 'Casement', 'Window', 'Cabinet', 'Drawer', 'Tee', 'Round', 'Square', 'Plate', 'Letter', 'Finger', 'Stopper', 'Bronze', 'Antique', 'Chrome', 'Plated', 'Satin', 'Polished', 'Lacquered', 'Powder', 'Coating', 'Coated']


def fix(t):
    t = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', t)          # TowerBolt -> Tower Bolt
    t = re.sub(r'(?<=[a-z])(?=\d)|(?<=\d)(?=[A-Za-z]{3,})', ' ', t) if False else t
    t = re.sub(r'\b(oval|Naked|Rod)(?=[A-Z0-9])', r'\1 ', t)
    t = re.sub(r'Finish-?\s*', 'Finish- ', t)
    t = re.sub(r'(?<=[a-z])(oval)', r' \1', t)
    return re.sub(r'\s+', ' ', t).strip()


recs, pages = [], {}
for f in sorted(glob.glob(f'{w}/ocr/*.json')):
    pg = os.path.basename(f)[:-5]
    d = json.load(open(f)); W, H = d['size']
    L = []
    for l in d['lines']:
        xs = [p[0] for p in l['box']]; ys = [p[1] for p in l['box']]
        L.append(dict(t=l['text'], x0=min(xs), x1=max(xs), y0=min(ys), y1=max(ys), c=l['conf']))
    codes = [l for l in L if CODE.match(l['t'])]
    for l in codes:
        l['code'] = 'SE-' + CODE.match(l['t']).group(1)
    # headers: big text near top, per half
    head = {0: [], 1: []}
    for l in L:
        if l['y0'] < 260 and l['t'].lower() not in SKIP and not CODE_IN.search(l['t']):
            head[0 if l['x0'] < W / 2 else 1].append(l['t'])
    pages[pg] = {'W': W, 'H': H, 'head': [' '.join(head[0]), ' '.join(head[1])], 'n_codes': len(codes)}
    used = set()
    for c in codes:
        below = [o for o in codes if o is not c and abs(o['x0'] - c['x0']) < 90 and o['y0'] > c['y0']]
        ylim = min([o['y0'] for o in below] + [c['y0'] + 210])
        txt = []
        for l in L:
            if l in codes or l['t'].lower() in SKIP: continue
            if c['y1'] - 4 < l['y0'] < ylim - 6 and c['x0'] - 90 < l['x0'] < c['x0'] + 50:
                txt.append(l)
        txt.sort(key=lambda l: (round(l['y0'] / 14), l['x0']))
        lines = [fix(l['t']) for l in txt]
        side = 0 if c['x0'] < W / 2 else 1
        recs.append(dict(page=pg, code=c['code'], x=c['x0'], y=c['y0'], x1=c['x1'], y1=c['y1'], side=side,
                         category=pages[pg]['head'][side], lines=lines,
                         conf=round(min([l['c'] for l in txt] + [c['c']]), 2)))
json.dump(dict(pages=pages, recs=recs), open(f'{w}/parsed.json', 'w'), indent=1)
print(len(recs), 'records', len({r['code'] for r in recs}), 'unique codes')
for p, v in pages.items():
    print(p, v['n_codes'], v['head'])
