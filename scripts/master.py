import json, re, difflib, csv, collections, sys
W = sys.argv[1]
R = json.load(open(f'{W}/records_seg.json'))
CATS = ["Brass Lever Handles","Brass Rose Latches","Brass Door Knockers","Brass Tower Bolts","Brass Casement Stays","Brass Casement Fasteners","Brass Cabinet Fittings","Brass Escutcheons","Brass Drawer Pulls","Brass Flush Pulls & Rings","Brass Cabinet Handles","Brass Pull Handles","Brass Hooks","Brass Curtain Holds & Tie Backs","Brass Sash Lifts & Sash Eyes","Brass Door Stoppers","Brass Gate Latches","Brass Hinges","Brass Letter Plates","Brass Newspaper Holders & Finger Plates","Brass Mortice Knobs","Brass Cabinet Knobs","Brass Bell Push & Corner Brackets","Brass Stair Fittings","Brass Numerals","Entrance Door Handles","Brass Bathroom Fittings","Brass Hammers & Bells","Aluminium Handles","Aluminium Accessories","Iron Lever Handles","Iron Mortice Knobs & Rose Handles","Iron Cabinet Knobs","Iron Knockers","Iron Hinges","Iron Window Fittings","Iron Gate Latches","Iron Latches","Iron Drawer Pulls","Iron Cabinet Handles","Iron Cage Handles","Iron Hooks","Iron Letter Plates","Iron Escutcheons","Iron Tower Bolts","Iron Hasps & Trunk Handles","Iron Studs & Table Corners","Hand Forged Entrance Door Handles","Cast Iron Pulleys","Speakeasy & Side Light Grills","Wooden Knobs","Wooden Cabinet Handles","Wooden Door Knobs","Wooden Cabinet Knobs","Bone Cabinet Knobs","Garden Tools","Lanterns","Fire Sets","Bar Accessories","Napkin Holders","Coasters","Aluminium Flower Vase","Fancy Boxes","Saddlery Fittings","Candle Stands"]
FIN = {"BPL":"Brass Polished Lacquered","CP":"Chrome Plated","SCP":"Satin Chrome Plated","AB":"Antique Brass","GPL":"Gold Polished Lacquered","BSC":"Black Satin Chrome","HDP":"Hot Dip Galvanised","PC":"Powder Coated","PCT":"Powder Coated Textured","FB":"Florantine Bronze","ZP":"Zinc Plated","EPNS":"Electro Plated Nickel Silver","ORB":"Oil Rubbed Bronze","AA":"Aluminium Anodized"}
def sec(code):
    n = int(code[3:])
    for lim, s in [(24000,"Brass Hardware"),(25000,"Aluminium Hardware"),(41000,"Iron Hardware"),(42000,"Wooden & Bone Hardware"),(43000,"Garden Tools"),(44000,"Lanterns"),(45000,"Fire Sets"),(47000,"Bar Accessories"),(49000,"Coasters & Vases"),(50000,"Fancy Boxes"),(51000,"Saddlery Fittings")]:
        if n < lim: return s
    return "Candle Stands"
def cat(head, code):
    h = re.sub(r'[^A-Za-z& ]', ' ', head).strip()
    m = difflib.get_close_matches(h.title(), CATS, 1, 0.55)
    if m: return m[0]
    n = int(code[3:]); s = sec(code); return s
SIZE = re.compile(r'(\d+\s*(mm|cm|cms|")|size|sizes)', re.I)
out = []; seen = set()
for r in R:
    if r['code'] in seen: continue
    seen.add(r['code'])
    lines = [l.replace('�','x') for l in r['lines'] if not re.fullmatch(r'[\d\-\s]{1,4}', l)]
    fin = next((l for l in lines if l.lower().startswith(('finish','finih'))), '')
    fin = re.sub(r'(?i)^fini[sh]h?-?\s*', '', fin).strip()
    fl = FIN.get(fin.upper(), fin)
    size = ' / '.join(re.sub(r'(?i)^sizes?-?\s*', '', l) for l in lines if SIZE.search(l) and not l.lower().startswith('finish'))
    name = ' '.join(l for l in lines if not SIZE.search(l) and not l.lower().startswith(('finish','finih'))).strip()
    c = cat(r['category'], r['code'])
    if not name: name = re.sub(r'^(Brass|Iron) ', '', c).rstrip('s')
    out.append(dict(code=r['code'], section=sec(r['code']), category=c, name=name, size=size, finish=fl, finish_code=fin if fin.upper() in FIN else '', image=f"images/{r['code']}.jpg", catalogue_page=r['page']))
SECS = {"Brass Hardware","Aluminium Hardware","Iron Hardware","Wooden & Bone Hardware","Garden Tools","Lanterns","Fire Sets","Bar Accessories","Coasters & Vases","Fancy Boxes","Saddlery Fittings","Candle Stands"}
good = sorted((int(p['code'][3:]), p['category']) for p in out if p['category'] not in SECS or p['category'] in CATS)
for p in out:
    if p['category'] in SECS and p['category'] not in CATS:
        n = int(p['code'][3:]); p['category'] = min(good, key=lambda g: abs(g[0]-n))[1]
NF = {'PCTextured':'Powder Coated Textured','PC Textured':'Powder Coated Textured','Antique':'Antique Brass','Ss':'Stainless Steel','SS':'Stainless Steel','Powder Coating':'Powder Coated','Aluminium':'Aluminium Anodized'}
for p in out: p['finish'] = NF.get(p['finish'], p['finish'])
json.dump(out, open(f'{W}/repo/data/products.json','w'), indent=1)
with open(f'{W}/repo/data/products.csv','w',newline='',encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
c = collections.Counter(p['category'] for p in out)
print(len(out)); print(sorted(c.items(), key=lambda x:-x[1])[:80])
print(collections.Counter(p['finish'] for p in out).most_common(15))
