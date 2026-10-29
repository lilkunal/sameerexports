"""Fetch every product from the live brass-builders.com (Astro site) into data/brassbuilders.json.
Run: python scripts/fetch_brassbuilders.py
"""
import re, json, os, html, urllib.request, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://brass-builders.com'
H = {'User-Agent': 'Mozilla/5.0 (catalogue sync)'}


def get(u):
    for i in range(3):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40).read().decode('utf-8', 'replace')
        except Exception:
            time.sleep(2 * (i + 1))
    raise RuntimeError(u)


def text(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s)).replace('�', '×').strip()


sm = get(BASE + '/sitemap.xml')
ranges = [u for u in re.findall(r'<loc>([^<]+)</loc>', sm) if re.search(r'/products/[^/]+/$', u)]
out = {}
for u in ranges:
    t = get(u)
    rng = text(re.search(r'<h1[^>]*>(.*?)</h1>', t, re.S).group(1))
    for li in re.findall(r'<li class="design"[^>]*>(.*?)</li>', t, re.S):
        code = text(re.search(r'class="design-code[^"]*"[^>]*>(.*?)</p>', li, re.S).group(1))
        name = text(re.search(r'class="design-name"[^>]*>(.*?)</h3>', li, re.S).group(1))
        specs = [text(x) for x in re.findall(r'class="design-spec"[^>]*>(.*?)</p>', li, re.S)]
        img = re.search(r'<img src="([^"]+)"', li)
        alt = re.search(r'alt="([^"]*)"', li)
        out[code] = dict(code=code, name=name, specs=specs, range=rng, range_url=u, image=BASE + img.group(1) if img else '', alt=html.unescape(alt.group(1)) if alt else '')
    print(f'{rng}: {len(out)} so far', flush=True)
json.dump(out, open(os.path.join(ROOT, 'data', 'brassbuilders.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(len(ranges), 'ranges', len(out), 'products')
