import sys, os, re, json, urllib.request, urllib.parse
from html.parser import HTMLParser

out = sys.argv[1]
base = "https://www.brass-builders.com/"
os.makedirs(f"{out}/html", exist_ok=True)
os.makedirs(f"{out}/img", exist_ok=True)
H = {"User-Agent": "Mozilla/5.0"}


def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=30).read()


class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.links = set(); s.imgs = set(); s.text = []; s.skip = 0
    def handle_starttag(s, t, a):
        a = dict(a)
        if t == "a" and a.get("href"): s.links.add(a["href"])
        if t == "img" and a.get("src"): s.imgs.add((a["src"], a.get("alt", "")))
        if t in ("script", "style"): s.skip += 1
    def handle_endtag(s, t):
        if t in ("script", "style"): s.skip -= 1
    def handle_data(s, d):
        if not s.skip and d.strip(): s.text.append(d.strip())


seen, queue, site = set(), ["index.html"], {}
while queue:
    p = queue.pop(0).split("#")[0]
    if not p or p in seen or p.startswith(("http", "mailto", "javascript")) or not p.endswith(".html"):
        continue
    seen.add(p)
    try:
        raw = get(base + p).decode("utf-8", "ignore")
    except Exception as e:
        print("fail", p, e); continue
    pr = P(); pr.feed(raw)
    d = os.path.dirname(p)
    site[p] = {"text": pr.text, "imgs": sorted(pr.imgs)}
    for l in pr.links:
        l = l.replace("http://", "https://")
        if l.startswith(base): l = l[len(base):]
        elif l.startswith(("http", "mailto", "javascript")): continue
        queue.append(os.path.normpath(os.path.join(d, l)).replace("\\", "/"))
    for s, _ in pr.imgs:
        u = urllib.parse.urljoin(base + p, s)
        fn = u.replace(base, "").replace("/", "__")
        if base not in u: continue
        if not os.path.exists(f"{out}/img/{fn}"):
            try: open(f"{out}/img/{fn}", "wb").write(get(u))
            except Exception as e: print("img fail", u)
    print(p, len(pr.text), "text", len(pr.imgs), "imgs", flush=True)
json.dump(site, open(f"{out}/site.json", "w"), indent=1)
