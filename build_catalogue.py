"""Printable product catalogue (A4 PDF) for Sameer Exports.
Run: python build_catalogue.py  ->  site/catalogue/*.pdf (full + one per section)
Needs: playwright (uses installed Edge), pypdf, segno, Pillow.
"""
import json, os, re, io, math, html, base64, collections, datetime
from PIL import Image
import segno
from pypdf import PdfReader, PdfWriter
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'site', 'catalogue')
CACHE = os.path.join(ROOT, 'catalogue_img')
os.makedirs(OUT, exist_ok=True)
os.makedirs(CACHE, exist_ok=True)
P = json.load(open(os.path.join(ROOT, 'data', 'products.json'), encoding='utf-8'))
CFG = json.load(open(os.path.join(ROOT, 'site_config.json'), encoding='utf-8'))
URL = CFG['url'].rstrip('/') + '/'
e = html.escape
YEAR = datetime.date.today().year
PER = 12  # products per page: 3 columns x 4 rows


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


for p in P:
    p['slug'] = slug(f"{p['code']}-{p['name']}")[:80]

ORDER = ['Brass Hardware', 'Aluminium Hardware', 'Iron Hardware', 'Wooden & Bone Hardware', 'Garden Tools', 'Lanterns', 'Fire Sets', 'Bar Accessories', 'Coasters & Vases', 'Fancy Boxes', 'Saddlery Fittings', 'Candle Stands']
SECTIONS = collections.OrderedDict((s, collections.OrderedDict()) for s in ORDER)
for p in sorted(P, key=lambda p: int(p['code'][3:]) if len(p['code']) < 9 else 11017.5):
    SECTIONS.setdefault(p['section'], collections.OrderedDict()).setdefault(p['category'], []).append(p)
SECTIONS = collections.OrderedDict((s, v) for s, v in SECTIONS.items() if v)


def img(code):
    """Small JPEG, data URI: sharp at print size, keeps the PDF phone-friendly."""
    f = os.path.join(CACHE, code + '.jpg')
    if not os.path.exists(f):
        im = Image.open(os.path.join(ROOT, 'images', code + '.jpg')).convert('RGB')
        im.thumbnail((520, 520))
        im.save(f, quality=76, optimize=True, progressive=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(open(f, 'rb').read()).decode()


def qr(data):
    b = io.BytesIO()
    segno.make(data, error='m').save(b, kind='svg', scale=4, border=1, dark='#14110d', light='#ffffff')
    return 'data:image/svg+xml;base64,' + base64.b64encode(b.getvalue()).decode()


WA = 'https://wa.me/919758155555?text=' + 'Hello%20Sameer%20Exports%2C%20I%20saw%20your%20catalogue%20and%20would%20like%20a%20quote.'
FINISHES = [("BPL", "Brass Polished Lacquered"), ("GPL", "Gold Polished Lacquered"), ("AB", "Antique Brass"), ("FB", "Florentine Bronze"), ("CP", "Chrome Plated"), ("SCP", "Satin Chrome Plated"),
            ("BSC", "Black Satin Chrome"), ("EPNS", "Electro Plated Nickel Silver"), ("ORB", "Oil Rubbed Bronze"), ("PC", "Powder Coated"), ("PCT", "Powder Coated Textured"), ("HDP", "Hot Dip Galvanised"), ("ZP", "Zinc Plated"), ("A", "Anodized")]
SWATCH = {"BPL": "linear-gradient(135deg,#f7e3a0,#c9962f 55%,#8a6418)", "GPL": "linear-gradient(135deg,#fff0b8,#d8a93a 55%,#9b7420)", "AB": "linear-gradient(135deg,#b08a4a,#6e5226 60%,#3f2e14)",
          "FB": "linear-gradient(135deg,#8a6a3e,#4d3519 60%,#2a1b0b)", "CP": "linear-gradient(135deg,#ffffff,#b9c0c8 50%,#7d8792)", "SCP": "linear-gradient(135deg,#e6e8ea,#b4b8bc 60%,#8d9196)",
          "BSC": "linear-gradient(135deg,#6b6d70,#3a3c3f 60%,#1f2022)", "EPNS": "linear-gradient(135deg,#f4f4f2,#c9c9c4 60%,#9c9c96)", "ORB": "linear-gradient(135deg,#5b3d2a,#2e1d12 60%,#160d07)",
          "PC": "linear-gradient(135deg,#3a3a3a,#1c1c1c 60%,#0a0a0a)", "PCT": "repeating-linear-gradient(45deg,#2a2a2a 0 2px,#151515 2px 4px)", "HDP": "linear-gradient(135deg,#d7dadc,#a3a8ac 60%,#7b8085)",
          "ZP": "linear-gradient(135deg,#eef2f4,#bfc8cd 60%,#94a0a6)", "A": "linear-gradient(135deg,#e9ebec,#c3c7ca 60%,#9ea3a7)"}

CSS = """
@page{size:A4;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
:root{--ink:#14110d;--brass:#b8892b;--brass2:#d9b45a;--paper:#fbf8f2;--line:#e6dcc8;--mute:#7a6f5e}
body{font:9.5pt/1.45 Inter,Arial,sans-serif;color:var(--ink);-webkit-print-color-adjust:exact;print-color-adjust:exact}
a{color:inherit;text-decoration:none}
h1,h2,h3,.serif{font-family:Fraunces,Georgia,serif;font-weight:600;letter-spacing:-.01em}
.page{width:210mm;height:297mm;position:relative;overflow:hidden;page-break-after:always;break-after:page;background:var(--paper)}
.page:last-child{page-break-after:auto;break-after:auto}
.dark{background:var(--ink);color:#f3ead7}
.pad{padding:18mm 16mm 20mm}
.kick{font:600 7.5pt Inter;letter-spacing:.22em;text-transform:uppercase;color:var(--brass)}
.rule{height:1.2mm;width:22mm;background:linear-gradient(90deg,var(--brass2),var(--brass));border-radius:1mm;margin:5mm 0}
/* cover */
.cover .glow{position:absolute;inset:0;background:radial-gradient(120mm 120mm at 78% 30%,#d9b45a40,transparent 70%),radial-gradient(90mm 90mm at 10% 95%,#b8892b33,transparent 70%)}
.cover .top{position:absolute;top:18mm;left:16mm;right:16mm;display:flex;justify-content:space-between;align-items:center;font:600 8pt Inter;letter-spacing:.2em;text-transform:uppercase;color:#cdbb92}
.logo{display:flex;align-items:center;gap:3mm}.logo i{width:9mm;height:9mm;border-radius:50%;background:radial-gradient(circle at 35% 30%,#f3d98a,#b8892b 55%,#6b4c12);display:block}
.cover h1{position:absolute;left:16mm;top:52mm;font-size:46pt;line-height:1.02;color:#f8efd9}
.cover h1 em{font-style:normal;color:#e2bd5e}
.cover .sub{position:absolute;left:16mm;top:112mm;width:100mm;font-size:11pt;color:#cbbd9f}
.collage{position:absolute;left:16mm;right:16mm;top:140mm;display:grid;grid-template-columns:repeat(3,1fr);gap:4mm}
.collage div{background:#fff;border-radius:3mm;height:52mm;position:relative;box-shadow:0 3mm 8mm #0006}
.collage div:nth-child(2),.collage div:nth-child(5){transform:translateY(7mm)}
.collage img{position:absolute;inset:4mm;width:calc(100% - 8mm);height:calc(100% - 8mm);object-fit:contain}
.cover .foot{position:absolute;left:16mm;right:16mm;bottom:14mm;display:flex;justify-content:space-between;border-top:.3mm solid #ffffff2a;padding-top:4mm;font-size:8.5pt;color:#bfae88}
.cover .year{position:absolute;right:16mm;top:52mm;font:600 9pt Inter;letter-spacing:.2em;color:#d9b45a;writing-mode:vertical-rl}
/* text pages */
.two{display:grid;grid-template-columns:1.25fr 1fr;gap:10mm}
p{margin-bottom:3mm}
.big{font-size:24pt;line-height:1.1;margin:3mm 0 2mm}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:3mm;margin:7mm 0}
.stats div{border:.3mm solid var(--line);border-radius:3mm;padding:4mm;background:#fff}
.stats b{display:block;font:600 20pt Fraunces,serif;color:var(--brass)}
.stats span{font-size:8pt;color:var(--mute)}
.box{background:#fff;border:.3mm solid var(--line);border-radius:3mm;padding:5mm;margin-bottom:4mm}
.box h3{font-size:12pt;margin-bottom:2mm}
.kv{display:grid;grid-template-columns:28mm 1fr;gap:1.5mm 3mm;font-size:9pt}.kv dt{color:var(--mute)}
.fin{display:grid;grid-template-columns:repeat(2,1fr);gap:3mm 6mm;margin-top:5mm}
.fin div{display:flex;align-items:center;gap:3mm}.fin i{width:11mm;height:11mm;border-radius:50%;flex:none;box-shadow:inset 0 0 0 .3mm #0002,0 1mm 2mm #0002}
.fin b{display:block;font-size:9.5pt}.fin span{font-size:8pt;color:var(--mute)}
.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:4mm;margin-top:4mm}.steps div{background:#fff;border:.3mm solid var(--line);border-radius:3mm;padding:4mm}.steps b{font:600 16pt Fraunces,serif;color:var(--brass);display:block}
.qrs{display:flex;gap:6mm;margin-top:5mm}.qrs a{display:flex;gap:3mm;align-items:center;background:#fff;border:.3mm solid var(--line);border-radius:3mm;padding:3mm;flex:1}.qrs img{width:22mm;height:22mm}
/* contents */
.toc{columns:2;column-gap:10mm;margin-top:4mm;height:226mm;column-fill:auto}
.toc .sec{margin-bottom:3.2mm}.toc h3{break-after:avoid}
.toc h3{font-size:10.5pt;display:flex;justify-content:space-between;border-bottom:.4mm solid var(--brass);padding-bottom:1mm;margin-bottom:1.5mm}
.toc a{display:flex;font-size:8pt;padding:.25mm 0}.toc a span{flex:1;border-bottom:.25mm dotted #c9b98f;margin:0 2mm 1.2mm}
/* section divider */
.divider .num{position:absolute;right:14mm;top:6mm;font:600 120pt Fraunces,serif;color:#ffffff0d;line-height:1}
.divider h1{position:absolute;left:16mm;top:70mm;font-size:40pt;line-height:1.05;width:150mm}
.divider .meta{position:absolute;left:16mm;top:122mm;color:#cbbd9f;font-size:10.5pt;width:150mm}
.divider .ranges{position:absolute;left:16mm;right:16mm;bottom:22mm;display:grid;grid-template-columns:repeat(4,1fr);gap:4mm}
.divider .ranges a{background:#ffffff0c;border:.3mm solid #ffffff1c;border-radius:3mm;padding:3mm;display:block}
.divider .ranges .im{background:#fff;border-radius:2mm;height:30mm;position:relative;margin-bottom:2mm}
.divider .ranges img{position:absolute;inset:2.5mm;width:calc(100% - 5mm);height:calc(100% - 5mm);object-fit:contain}
.divider .ranges b{font-size:8.3pt;color:#f3ead7;display:block;line-height:1.25}.divider .ranges span{font-size:7.5pt;color:#a99a79}
/* product pages */
.hd{position:absolute;top:0;left:0;right:0;height:22mm;padding:0 14mm;display:flex;align-items:flex-end;justify-content:space-between;padding-bottom:4mm;border-bottom:.3mm solid var(--line)}
.hd .t{font:600 16pt Fraunces,serif}.hd .s{font-size:7.5pt;letter-spacing:.18em;text-transform:uppercase;color:var(--brass);font-weight:600;margin-bottom:1mm}
.hd .r{font-size:8pt;color:var(--mute);text-align:right}
.grid{position:absolute;top:27mm;left:14mm;right:14mm;bottom:17mm;display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(4,1fr);gap:4mm}
.card{background:#fff;border:.3mm solid var(--line);border-radius:3mm;display:flex;flex-direction:column;overflow:hidden}
.card .im{flex:1;min-height:0;position:relative}
.card .im img{position:absolute;inset:3mm;width:calc(100% - 6mm);height:calc(100% - 6mm);object-fit:contain}
.card .bd{padding:2.2mm 3mm 2.6mm;border-top:.3mm solid #f0e8d8}
.card .cd{font:700 7.4pt Inter;letter-spacing:.06em;color:var(--brass)}
.card h4{font:600 8.6pt/1.25 Inter;margin:.5mm 0 .6mm;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.card .mt{font-size:7.2pt;color:var(--mute);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ft{position:absolute;bottom:0;left:0;right:0;height:13mm;padding:0 14mm;display:flex;align-items:center;justify-content:space-between;font-size:7.5pt;color:var(--mute);border-top:.3mm solid var(--line)}
.ft b{color:var(--ink)}.ft .pn{font:600 9pt Fraunces,serif;color:var(--ink)}
/* back */
.back .wrap{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;padding:0 22mm}
.back h1{font-size:34pt;margin-bottom:4mm}
.back .qrs a{background:#ffffff0c;border-color:#ffffff22;color:#f3ead7}
.back .qrs img{background:#fff;border-radius:2mm;padding:1mm}
"""


def card(p):
    meta = ' · '.join(x for x in (p['size'], p['finish']) if x)
    return (f'<a class="card" href="{URL}product/{p["slug"]}.html"><div class="im"><img src="{img(p["code"])}" alt=""></div>'
            f'<div class="bd"><div class="cd">{p["code"]}</div><h4>{e(p["name"])}</h4><div class="mt">{e(p["size"]) or "&nbsp;"}</div><div class="mt">{e(p["finish"]) or "&nbsp;"}</div></div></a>')


def footer(n, label):
    return f'<div class="ft"><span><b>Sameer Exports</b> · {e(label)}</span><span>{URL.replace("https://", "")}  ·  +91-571-2513295</span><span class="pn">{n:02d}</span></div>'


def build(sections):
    """Returns (html, page map). Page numbers are known up front because every range starts a new page."""
    pages, toc = [], collections.OrderedDict()
    front = 4  # cover, about, finishes & ordering, contents
    n = front
    plan = []
    for s, cs in sections.items():
        n += 1
        toc[s] = {'page': n, 'cats': collections.OrderedDict()}
        plan.append(('div', s, n))
        for c, ps in cs.items():
            toc[s]['cats'][c] = n + 1
            for i in range(0, len(ps), PER):
                n += 1
                plan.append(('grid', (s, c, ps[i:i + PER], i // PER + 1, math.ceil(len(ps) / PER)), n))
    total_products = sum(len(ps) for cs in sections.values() for ps in cs.values())

    # cover
    hero = ['SE-3017', 'SE-1021', 'SE-3001', 'SE-22008', 'SE-25011', 'SE-18001']
    pages.append(f"""<section class="page dark cover"><div class="glow"></div><div class="top"><span class="logo"><i></i>Sameer Exports</span><span>ISO 9001 Certified</span></div>
<div class="year">Catalogue {YEAR}</div><h1>Brass &amp;<br>Iron Hardware<br><em>Catalogue</em></h1>
<p class="sub">Builders hardware, door furniture and art ware, cast and finished in Aligarh, India since 1994. {total_products} designs, made to order for importers, wholesalers and builders.</p>
<div class="collage">{''.join(f'<div><img src="{img(c)}" alt=""></div>' for c in hero)}</div>
<div class="foot"><span>Manufacturer &amp; Exporter</span><span>Aligarh · India</span><span>{URL.replace('https://', '')}</span></div></section>""")

    # about
    pages.append(f"""<section class="page"><div class="pad"><span class="kick">About us</span><h2 class="big">Thirty years of brass,<br>made by hand in Aligarh</h2><div class="rule"></div>
<div class="two"><div><p>Sameer Exports was started in 1994 by Mr. Sanjeev Agarwal under the direction of Er. S.P. Agarwal. Today it is a leading manufacturer and exporter of brass, aluminium and forged wrought iron ironmongery, wooden products and art ware from Aligarh, India's traditional centre of brass and lock making.</p>
<p>We use traditional sand casting alongside modern forging machines. Every product is partly mechanised and partly handcrafted, then finished, polished, lacquered and packed to international standards and to each buyer's requirements.</p>
<p>As an ISO 9001 certified company we run strict quality control at every stage, and a team of designers keeps the range evolving. Our clients are spread across the UK, US, Mexico, Germany, Canada and Australia.</p></div>
<div><div class="box"><h3>Leadership</h3><dl class="kv"><dt>Owner</dt><dd>Sanjeev Agarwal</dd><dt>Director</dt><dd>Sarthak Agarwal</dd></dl></div>
<div class="box"><h3>Company</h3><dl class="kv"><dt>Established</dt><dd>1994</dd><dt>Certification</dt><dd>ISO 9001</dd><dt>GSTIN</dt><dd>09ACZPA8884B1Z2</dd><dt>IEC</dt><dd>0694001716</dd></dl></div></div></div>
<div class="stats"><div><b>1994</b><span>Established</span></div><div><b>{total_products}</b><span>Catalogue designs</span></div><div><b>{sum(len(cs) for cs in sections.values())}</b><span>Product ranges</span></div><div><b>6+</b><span>Export countries</span></div></div>
<div class="box"><h3>Visit or contact us</h3><dl class="kv"><dt>Factory &amp; office</dt><dd>C-235, Ramghat Road, UPSIDC Sector 2, Talanagri, Aligarh 202002, Uttar Pradesh, India</dd><dt>Phone</dt><dd>+91-571-2513295</dd><dt>WhatsApp</dt><dd>+91 97581 55555</dd><dt>Email</dt><dd>info@brass-builders.com</dd><dt>Website</dt><dd><a href="{URL}">{URL.replace('https://', '')}</a></dd></dl></div>
</div>{footer(2, 'About us')}</section>""")

    # finishes + how to order
    pages.append(f"""<section class="page"><div class="pad"><span class="kick">Finishes</span><h2 class="big">Finish codes</h2><div class="rule"></div>
<p>Each product lists its standard finish. Most designs can be supplied in any finish below on request.</p>
<div class="fin">{''.join(f'<div><i style="background:{SWATCH[c]}"></i><div><b>{c}</b><span>{n}</span></div></div>' for c, n in FINISHES)}</div>
<div style="height:10mm"></div><span class="kick">How to order</span><h2 class="big">Request a quote</h2><div class="rule"></div>
<div class="steps"><div><b>01</b>Note the product codes and quantities you need, and the finish for each.</div><div><b>02</b>Send the list on WhatsApp, email or through the website quote list.</div><div><b>03</b>We reply with price, MOQ, packing and lead time. Samples on request.</div></div>
<div class="qrs"><a href="{WA}"><img src="{qr(WA)}" alt=""><div><b>WhatsApp</b><br><span style="color:var(--mute);font-size:8pt">Scan to chat<br>+91 97581 55555</span></div></a>
<a href="{URL}"><img src="{qr(URL)}" alt=""><div><b>Website</b><br><span style="color:var(--mute);font-size:8pt">Full catalogue, search<br>and online quote list</span></div></a></div>
<p style="margin-top:6mm;font-size:8pt;color:var(--mute)">Product images are for reference. Specifications are subject to change without notice. Tap any product in this PDF to open its page on our website.</p>
</div>{footer(3, 'Finishes & ordering')}</section>""")

    # contents
    toc_html = ''.join(f'<div class="sec"><h3><a href="#p{v["page"]}">{e(s)}</a><span>{v["page"]:02d}</span></h3>'
                       + ''.join(f'<a href="#p{pg}">{e(c)}<span></span>{pg:02d}</a>' for c, pg in v['cats'].items()) + '</div>' for s, v in toc.items())
    pages.append(f'<section class="page"><div class="pad"><span class="kick">Contents</span><h2 class="big">Inside this catalogue</h2><div class="toc">{toc_html}</div></div>{footer(4, "Contents")}</section>')

    for kind, data, pn in plan:
        if kind == 'div':
            s = data
            cs = sections[s]
            pages.append(f"""<section class="page dark divider" id="p{pn}"><div class="glow" style="position:absolute;inset:0;background:radial-gradient(110mm 110mm at 80% 35%,#d9b45a2e,transparent 70%)"></div><div class="num">{list(sections).index(s) + 1:02d}</div>
<div style="position:absolute;left:16mm;top:56mm" class="kick">Section {list(sections).index(s) + 1:02d}</div><h1>{e(s)}</h1>
<p class="meta">{sum(len(v) for v in cs.values())} designs in {len(cs)} range{'s' if len(cs) > 1 else ''}. Tap a range to jump to it.</p>
<div class="ranges">{''.join(f'<a href="#p{toc[s]["cats"][c]}"><div class="im"><img src="{img(ps[0]["code"])}" alt=""></div><b>{e(c)}</b><span>{len(ps)} designs · p.{toc[s]["cats"][c]:02d}</span></a>' for c, ps in list(cs.items())[:8])}</div></section>""")
        else:
            s, c, ps, part, parts = data
            more = f' · {part}/{parts}' if parts > 1 else ''
            pages.append(f"""<section class="page" id="p{pn}"><div class="hd"><div><div class="s">{e(s)}</div><div class="t">{e(c)}</div></div><div class="r">{len(sections[s][c])} designs{more}</div></div>
<div class="grid">{''.join(card(p) for p in ps)}</div>{footer(pn, s)}</section>""")

    # back cover
    pages.append(f"""<section class="page dark back"><div class="glow" style="position:absolute;inset:0;background:radial-gradient(120mm 120mm at 50% 40%,#d9b45a33,transparent 70%)"></div><div class="wrap">
<span class="logo" style="font:600 13pt Fraunces,serif;margin-bottom:10mm"><i></i>Sameer Exports</span><h1>Let's build something<br>that lasts.</h1>
<p style="color:#cbbd9f;font-size:11pt;max-width:130mm">Send us your product codes and quantities. We reply with price, MOQ, packing and lead time for your market.</p>
<div class="qrs" style="max-width:150mm"><a href="{WA}"><img src="{qr(WA)}" alt=""><div><b>WhatsApp</b><br>+91 97581 55555</div></a><a href="{URL}"><img src="{qr(URL)}" alt=""><div><b>Website</b><br>{URL.replace('https://', '').rstrip('/')}</div></a></div>
<div style="margin-top:12mm;font-size:9.5pt;color:#cbbd9f;line-height:1.7">C-235, Ramghat Road, UPSIDC Sector 2, Talanagri, Aligarh 202002, Uttar Pradesh, India<br>Phone +91-571-2513295 · info@brass-builders.com<br>ISO 9001 Certified · GSTIN 09ACZPA8884B1Z2 · IEC 0694001716</div></div></section>""")

    doc = f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Sameer Exports Product Catalogue {YEAR}</title><link href="https://fonts.googleapis.com/css2?family=Fraunces:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet"><style>{CSS}</style></head><body>{"".join(pages)}</body></html>'
    return doc, toc, len(pages)


def render(doc, out_pdf):
    tmp = out_pdf.replace('.pdf', '.html')
    open(tmp, 'w', encoding='utf-8').write(doc)
    with sync_playwright() as pw:
        br = pw.chromium.launch(channel='msedge')
        pg = br.new_page()
        pg.goto('file:///' + tmp.replace('\\', '/'), wait_until='networkidle', timeout=180000)
        pg.evaluate('document.fonts.ready')
        pg.pdf(path=out_pdf, format='A4', print_background=True, prefer_css_page_size=True, tagged=True, outline=True)
        br.close()
    os.remove(tmp)
    # metadata so phones and email show a proper title
    r = PdfReader(out_pdf)
    w = PdfWriter(clone_from=r)
    w.add_metadata({'/Title': f'Sameer Exports Product Catalogue {YEAR}', '/Author': 'Sameer Exports, Aligarh', '/Subject': 'Brass, iron and aluminium builders hardware'})
    w.compress_identical_objects(remove_identicals=True, remove_orphans=True)
    w.write(out_pdf)
    return len(r.pages), os.path.getsize(out_pdf)


if __name__ == '__main__':
    results = {}
    doc, toc, n = build(SECTIONS)
    results['Sameer-Exports-Catalogue.pdf'] = render(doc, os.path.join(OUT, 'Sameer-Exports-Catalogue.pdf'))
    for s, cs in SECTIONS.items():
        doc, _, _ = build(collections.OrderedDict([(s, cs)]))
        results[f'Sameer-Exports-{slug(s)}.pdf'] = render(doc, os.path.join(OUT, f'Sameer-Exports-{slug(s)}.pdf'))
    index = [{'file': f, 'pages': pgs, 'mb': round(sz / 1048576, 1)} for f, (pgs, sz) in results.items()]
    json.dump(index, open(os.path.join(OUT, 'index.json'), 'w'), indent=1)
    for i in index:
        print(i)
