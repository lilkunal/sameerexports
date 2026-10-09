"""Static site generator for Sameer Exports. Run: python build_site.py  -> writes site/"""
import json, re, html, os, collections, datetime
from urllib.parse import quote_plus

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'site')
P = json.load(open(os.path.join(ROOT, 'data', 'products.json'), encoding='utf-8'))
CO = dict(name='Sameer Exports', tag='Brass Builders Hardware & Art Ware since 1994',
          addr='C-235, Ramghat Road, UPSIDC Sector 2, Talanagri, Talashpur, Aligarh 202002, Uttar Pradesh, India',
          phone='+91-571-2513295', fax='+91-571-2520541', email='info@brass-builders.com',
          owner='Sanjeev Agarwal', wa='919758155555', gst='09ACZPA8884B1Z2', iec='0694001716')
YEAR = datetime.date.today().year
e = html.escape


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


for p in P:
    p['slug'] = slug(f"{p['code']}-{p['name']}")[:80]
    p['cslug'] = slug(p['category'])
SECTIONS = collections.OrderedDict()
for p in P:
    SECTIONS.setdefault(p['section'], collections.OrderedDict()).setdefault(p['category'], []).append(p)
CATS = {c: ps for s in SECTIONS.values() for c, ps in s.items()}

CSS = """
/* preloader: a hand presses the lever, the door swings open */
#pl{position:fixed;inset:0;z-index:999;background:#0b0907;display:grid;place-items:center;perspective:1400px;transition:opacity .6s,visibility .6s}html.nopl #pl{display:none}#pl.gone{opacity:0;visibility:hidden}
.pl-room{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 55%,#f6e3b4 0,#d9b45a 18%,#2a2014 48%,#0b0907 70%);opacity:0;transition:opacity 1s .9s}#pl.go .pl-room{opacity:1}
.pl-frame{position:relative;width:min(46vw,260px);aspect-ratio:1/2;border:10px solid #3a2d1c;border-bottom:0;border-radius:6px 6px 0 0;box-shadow:0 0 0 2px #5a4528,0 30px 80px #000;transform-style:preserve-3d}
.pl-door{position:absolute;inset:0;background:linear-gradient(135deg,#5b3d22,#3c2715);transform-origin:left center;transition:transform 1.25s cubic-bezier(.65,0,.3,1) 1s;box-shadow:inset 0 0 0 1px #ffffff12}#pl.go .pl-door{transform:rotateY(-104deg)}
.pl-panel{position:absolute;left:14%;right:14%;top:8%;height:36%;border:2px solid #ffffff14;border-radius:4px;box-shadow:inset 0 0 20px #0005}.pl-panel.b{top:52%;height:40%}
.pl-plate{position:absolute;right:9%;top:46%;width:16%;height:22%;border-radius:999px;background:linear-gradient(160deg,#f3d98a,#b8892b 55%,#6b4c12);box-shadow:0 4px 10px #0008}
.pl-lever{position:absolute;top:18%;right:30%;width:420%;height:13%;border-radius:999px;background:linear-gradient(180deg,#f7e3a6,#c9962f 60%,#7a5714);transform-origin:96% 50%;transition:transform .35s ease .65s;box-shadow:0 3px 6px #0008}#pl.go .pl-lever{transform:rotate(-24deg)}
.pl-key{position:absolute;left:38%;bottom:20%;width:24%;height:22%;border-radius:50% 50% 30% 30%;background:#2a1d0e}
.pl-hand{position:absolute;right:62%;top:39%;width:130%;filter:drop-shadow(0 8px 10px #0009);opacity:0;transform:translateX(-70%);overflow:visible}#pl.go .pl-hand{opacity:1;animation:press 1s cubic-bezier(.3,.7,.2,1) .05s both}
@keyframes press{0%{opacity:0;transform:translateX(-70%)}45%{opacity:1;transform:translate(0,0)}70%{transform:translate(0,30%) rotate(-12deg)}88%{opacity:1;transform:translate(0,30%) rotate(-12deg)}100%{opacity:0;transform:translate(-20%,30%) rotate(-12deg)}}
.pl-name{position:absolute;bottom:9vh;text-align:center;color:#f5ecd9;font:600 clamp(22px,4vw,34px) Fraunces,serif;letter-spacing:.02em;opacity:0;transform:translateY(10px);transition:all .6s .4s}.pl-name small{display:block;font:500 12px Inter;letter-spacing:.2em;text-transform:uppercase;color:#d9b45a;margin-top:6px}#pl.go .pl-name{opacity:1;transform:none}
.pl-skip{position:absolute;top:18px;right:18px;background:#ffffff14;color:#e9dcc0;border:1px solid #ffffff2a;border-radius:999px;padding:8px 16px;cursor:pointer;font:500 13px Inter;backdrop-filter:blur(8px)}

/* scroll reveal */
.rv{opacity:0;transform:translateY(26px) scale(.985);transition:opacity .7s cubic-bezier(.2,.7,.2,1) var(--d,0ms),transform .7s cubic-bezier(.2,.7,.2,1) var(--d,0ms)}.rv.in{opacity:1;transform:none}
.hero .w>div:first-child{transform:translateY(calc(var(--py,0px)*-.4))}.hero .h3d{transform:translateY(calc(var(--py,0px)*.3))}
html:not(.plx) .hero .w>div:first-child>*{opacity:0}html.plx .hero .w>div:first-child>*{animation:up .9s cubic-bezier(.2,.7,.2,1) both}html.plx .hero .w>div:first-child>*:nth-child(2){animation-delay:.12s}html.plx .hero .w>div:first-child>*:nth-child(3){animation-delay:.24s}html.plx .hero .w>div:first-child>*:nth-child(4){animation-delay:.36s}
@keyframes up{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:none}}

/* ambient brass light behind the glass */
.ambient{position:fixed;inset:0;z-index:-1;pointer-events:none;background:radial-gradient(40vw 40vw at 85% 10%,#d9b45a2e,transparent 60%),radial-gradient(35vw 35vw at 5% 60%,#b8892b24,transparent 60%),radial-gradient(30vw 30vw at 60% 95%,#e8c77a22,transparent 60%)}

/* glassmorphism */
:root{--glass:rgba(255,255,255,.62);--glass-b:rgba(255,255,255,.75);--glass-s:0 8px 32px rgba(60,40,10,.10)}
:root[data-theme=dark]{--glass:rgba(30,26,20,.55);--glass-b:rgba(255,255,255,.08);--glass-s:0 8px 32px rgba(0,0,0,.35)}
@media(prefers-color-scheme:dark){:root:not([data-theme=light]){--glass:rgba(30,26,20,.55);--glass-b:rgba(255,255,255,.08);--glass-s:0 8px 32px rgba(0,0,0,.35)}}
header{background:var(--glass)!important;backdrop-filter:blur(18px) saturate(1.4);-webkit-backdrop-filter:blur(18px) saturate(1.4);border-bottom:1px solid var(--glass-b);transition:box-shadow .3s}header.sc{box-shadow:var(--glass-s)}
.pc,.sec,.card,.post,.person,.trust,.feat,.side,.bulk,.dd .menu,.sug,.drawer:not([hidden]),.mbar,.qt{background:var(--glass)!important;backdrop-filter:blur(16px) saturate(1.3);-webkit-backdrop-filter:blur(16px) saturate(1.3);border:1px solid var(--glass-b)!important;box-shadow:var(--glass-s)}
.pc,.sec{transition:opacity .7s cubic-bezier(.2,.7,.2,1) var(--d,0ms),transform .35s cubic-bezier(.2,.7,.2,1),box-shadow .35s}.pc.in:hover,.sec.in:hover{transform:translateY(-6px);box-shadow:0 20px 44px rgba(60,40,10,.18)}
.pc .im,.sec .im{border-radius:12px;margin:8px;background:var(--well)}.pc .im img,.sec .im img{transition:transform .5s cubic-bezier(.2,.7,.2,1)}.pc:hover .im img,.sec:hover .im img{transform:scale(1.06) rotate(-1deg)}
.band{background:linear-gradient(135deg,rgba(20,17,13,.92),rgba(43,34,22,.88))!important;backdrop-filter:blur(14px);border:1px solid #ffffff14}
.btn{box-shadow:0 6px 18px rgba(184,137,43,.35);transition:transform .2s,box-shadow .2s,background .2s}.btn:hover{transform:translateY(-2px);box-shadow:0 10px 24px rgba(184,137,43,.45)}.btn.o{box-shadow:none}
@media(prefers-reduced-motion:reduce){.rv{opacity:1!important;transform:none!important}#pl{display:none}}

.h3d{position:relative;aspect-ratio:1;max-height:560px;width:100%}.h3d canvas{position:absolute;inset:0;width:100%;height:100%;opacity:0;transition:opacity .8s;cursor:grab;touch-action:pan-y}.h3d.ready canvas{opacity:1}.h3d.ready .hgrid{opacity:0;pointer-events:none}.h3d .hgrid{position:absolute;inset:8% 0;transition:opacity .6s}
.h3d::before{content:"";position:absolute;inset:12%;border-radius:50%;background:radial-gradient(circle,#d9b45a33,transparent 65%)}.h3hint{position:absolute;bottom:4px;left:50%;transform:translateX(-50%);font-size:12px;color:#a8997c;opacity:0;transition:opacity .6s}.h3d.ready .h3hint{opacity:1}
.trust{display:grid;grid-template-columns:repeat(5,1fr);gap:0;border:1px solid var(--line);border-radius:var(--r);background:var(--card);margin-top:22px}.trust div{padding:14px 16px;border-right:1px solid var(--line)}.trust div:last-child{border:0}.trust b{display:block;font-size:14px}.trust span{font-size:12.5px;color:var(--mute)}
.rng{margin-bottom:34px}.rng h2{font-size:24px;margin:0}.rowx{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(190px,210px);gap:14px;overflow-x:auto;padding-bottom:10px;scroll-snap-type:x mandatory}.rowx .pc{scroll-snap-align:start}
.bulk{display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap;background:var(--tint);border:1px solid var(--line);border-radius:18px;padding:26px 28px;margin-top:30px}.bulk h2{font-size:24px;margin:0 0 4px}.bulk p{margin:0;color:var(--text2)}
@media(max-width:900px){.trust{grid-template-columns:1fr 1fr}.trust div{border-bottom:1px solid var(--line)}.rowx{grid-auto-columns:46%}.h3d{max-height:340px;margin-top:8px}.h3d .hgrid{display:none}}
.wab{background:#1fa855}.wab:hover{background:#178a45}@media(max-width:900px){.wa span{display:none}.wa{padding:14px;bottom:80px}}
.sug{position:absolute;top:calc(100% + 6px);left:0;right:0;background:var(--card);border:1px solid var(--line);border-radius:14px;box-shadow:0 16px 36px #00000026;z-index:70;overflow:hidden;max-height:70vh;overflow-y:auto}.sug a{display:flex;gap:12px;align-items:center;padding:8px 12px;border-bottom:1px solid var(--line)}.sug a:hover,.sug a.on{background:var(--tint)}.sug img{width:44px;height:44px;object-fit:contain;background:var(--well);border-radius:8px;flex:none}.sug b{display:block;font-size:14px;font-weight:600}.sug small{color:var(--mute);font-size:12px}.sug .all{justify-content:center;color:var(--brass);font-weight:600;font-size:14px}.sug .none{padding:14px;margin:0;color:var(--mute);font-size:14px}
:root{--text:#14110d;--text2:#3b342a;--well:#fff;--tint:#f4ecda;--ink:#14110d;--ink2:#2a241c;--brass:#b8892b;--brass2:#d9b45a;--paper:#faf7f1;--card:#fff;--line:#e8e1d3;--mute:#6e665a;--ok:#2f7a4a;--r:14px;color-scheme:light}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;font:16px/1.6 Inter,system-ui,sans-serif;color:var(--text);background:var(--paper)}
a{color:inherit;text-decoration:none}img{max-width:100%;display:block}h1,h2,h3{font-family:Fraunces,Georgia,serif;line-height:1.15;margin:0 0 .5em;font-weight:600}
.w{max-width:1240px;margin:0 auto;padding:0 20px}.btn{display:inline-flex;align-items:center;gap:8px;background:var(--brass);color:#fff;border:0;border-radius:999px;padding:12px 22px;font-weight:600;cursor:pointer;font-size:15px}
.btn:hover{background:#9c7220}.btn.o{background:transparent;border:1.5px solid currentColor;color:inherit}.btn.s{padding:8px 14px;font-size:13px}
.top{background:var(--ink);color:#d8cdb6;font-size:13px}.top .w{display:flex;justify-content:space-between;gap:12px;padding:7px 20px;flex-wrap:wrap}
header{background:var(--card);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:20}.hd{display:flex;align-items:center;gap:20px;padding:14px 20px}
.logo{display:flex;align-items:center;gap:10px;font-family:Fraunces,serif;font-weight:700;font-size:22px}.logo i{width:38px;height:38px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#f3d98a,#b8892b 55%,#6b4c12);display:block}
.logo small{display:block;font:500 11px Inter;color:var(--mute);letter-spacing:.08em;text-transform:uppercase}
.srch{flex:1;display:flex;max-width:520px;position:relative}.srch input{flex:1;border:1.5px solid var(--line);border-right:0;border-radius:999px 0 0 999px;padding:10px 16px;font:inherit;background:var(--paper)}
.srch button{border-radius:0 999px 999px 0}.qc{position:relative;font-weight:600;display:flex;gap:6px;align-items:center}.qc b{background:var(--brass);color:#fff;border-radius:999px;font-size:12px;padding:1px 8px}
nav.mn{border-top:1px solid var(--line)}nav.mn .w{display:flex;gap:4px;align-items:stretch}.dd{position:relative}.dd .menu{display:none;position:absolute;left:0;top:100%;background:var(--card);border:1px solid var(--line);border-radius:12px;box-shadow:0 14px 34px #0000001f;padding:8px;min-width:260px;z-index:30}.dd:hover .menu,.dd:focus-within .menu{display:grid}.dd .menu a{border:0;padding:9px 12px;border-radius:8px}.dd .menu a:hover{background:var(--tint)}nav.mn a{padding:11px 14px;font-size:14px;font-weight:500;white-space:nowrap;border-bottom:2px solid transparent}nav.mn a:hover,nav.mn a.on{border-color:var(--brass);color:var(--brass)}
.hero{background:linear-gradient(120deg,#14110d 55%,#2b2216);color:#f5ecd9;overflow:hidden}.hero .w{display:grid;grid-template-columns:1.1fr 1fr;gap:30px;align-items:center;padding:64px 20px}
.hero h1{font-size:clamp(34px,5vw,58px)}.hero h1 em{color:var(--brass2);font-style:normal}.hero p{color:#cbbfa6;font-size:18px;max-width:520px}
.hgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.hgrid div{background:var(--card);border-radius:var(--r);aspect-ratio:1;padding:10px;display:grid;place-items:center}.hgrid img{max-height:100%;object-fit:contain}
.hgrid div:nth-child(2){transform:translateY(24px)}.hgrid div:nth-child(5){transform:translateY(24px)}
.feat{display:grid;grid-template-columns:repeat(4,1fr);gap:0;background:var(--card);border:1px solid var(--line);border-radius:var(--r);margin:-28px auto 0;position:relative;box-shadow:0 10px 30px #0000000d}
.feat div{padding:18px 20px;border-right:1px solid var(--line)}.feat div:last-child{border:0}.feat b{display:block;font-size:14px}.feat span{font-size:13px;color:var(--mute)}
section{padding:56px 0}.sh{display:flex;justify-content:space-between;align-items:end;gap:16px;margin-bottom:24px}.sh h2{font-size:clamp(26px,3vw,36px);margin:0}.sh a{color:var(--brass);font-weight:600;font-size:14px}
.kick{color:var(--brass);font-weight:600;font-size:13px;letter-spacing:.12em;text-transform:uppercase}
.secs{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:16px}.sec{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:16px;transition:.2s}.sec:hover{border-color:var(--brass);transform:translateY(-3px)}
.sec .im{aspect-ratio:4/3;display:grid;place-items:center;margin-bottom:10px}.sec .im{overflow:hidden}.sec .im img{width:100%;height:100%;object-fit:contain}.sec b{display:block}.sec span{font-size:13px;color:var(--mute)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:16px}.pc{background:var(--card);border:1px solid var(--line);border-radius:var(--r);display:flex;flex-direction:column;overflow:hidden;transition:.2s}
.pc:hover{box-shadow:0 12px 28px #0000001a;border-color:#d9c9a5}.pc .im{aspect-ratio:1;padding:14px;display:grid;place-items:center}.pc .im{overflow:hidden}.pc .im img{width:100%;height:100%;object-fit:contain}
.pc .bd{padding:12px 14px 14px;border-top:1px solid var(--line);display:flex;flex-direction:column;gap:4px;flex:1}.pc .cd{font-size:12px;color:var(--brass);font-weight:700;letter-spacing:.04em}.pc h3{font:600 15px/1.3 Inter;margin:0}
.pc .mt{font-size:12.5px;color:var(--mute)}.pc .btn{margin-top:auto;align-self:flex-start}
.band{background:var(--ink);color:#efe4cc;border-radius:22px;padding:44px;display:grid;grid-template-columns:1.3fr 1fr;gap:30px;align-items:center}.band p{color:#c7bba3}
.stats{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}.stats div{background:var(--card)fff0d;border:1px solid #ffffff1f;border-radius:var(--r);padding:18px}.stats b{font:600 32px Fraunces;color:var(--brass2);display:block}
.layout{display:grid;grid-template-columns:260px 1fr;gap:28px;padding:30px 0 60px}.side{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:16px;align-self:start;position:sticky;top:130px;max-height:calc(100vh - 150px);overflow:auto}
.side h4{margin:12px 0 6px;font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--mute)}.side a{display:flex;justify-content:space-between;padding:5px 8px;border-radius:8px;font-size:14px}.side a:hover,.side a.on{background:var(--tint);color:#7a5813}
.side a span{color:var(--mute);font-size:12px}.bar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:18px}.bar input,.bar select{border:1.5px solid var(--line);border-radius:10px;padding:9px 12px;font:inherit;background:var(--card)}
.crumb{font-size:13px;color:var(--mute);padding:18px 0 0}.crumb a:hover{color:var(--brass)}
.pd{display:grid;grid-template-columns:1fr 1fr;gap:40px;padding:26px 0 50px}.pd .gal{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:30px;aspect-ratio:1;display:grid;place-items:center}.pd .gal img{max-height:100%;object-fit:contain}
.spec{width:100%;border-collapse:collapse;margin:18px 0}.spec td{padding:10px 0;border-bottom:1px solid var(--line);font-size:15px}.spec td:first-child{color:var(--mute);width:40%}
.qty{display:flex;gap:10px;align-items:center;margin:18px 0}.qty input{width:90px;border:1.5px solid var(--line);border-radius:10px;padding:10px;font:inherit}
.note{background:var(--tint);border-radius:12px;padding:14px 16px;font-size:14px}.prose{max-width:760px}.prose p,.prose li{color:var(--text2)}.prose h2{margin-top:1.4em}
.cards3{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:22px}
.blog{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px}.post{background:var(--card);border:1px solid var(--line);border-radius:var(--r);overflow:hidden}.post .im{background:#f3eee4;aspect-ratio:16/9;display:grid;grid-template-columns:repeat(3,1fr);gap:6px;padding:14px}.post .im img{object-fit:contain;height:100%;width:100%;background:var(--card);border-radius:8px}.post .bd{padding:18px}
form .f{display:grid;grid-template-columns:1fr 1fr;gap:12px}form label{display:flex;flex-direction:column;font-size:13px;font-weight:600;gap:5px}form input,form textarea,form select{border:1.5px solid var(--line);border-radius:10px;padding:10px 12px;font:inherit;font-weight:400;background:var(--card)}form .full{grid-column:1/-1}
.qt{width:100%;border-collapse:collapse;background:var(--card);border-radius:var(--r);overflow:hidden}.qt td,.qt th{padding:12px;border-bottom:1px solid var(--line);text-align:left;font-size:14px}.qt img{width:64px;height:64px;object-fit:contain}.qt input{width:70px;padding:6px;border:1px solid var(--line);border-radius:8px}
.x{background:none;border:0;color:#a33;cursor:pointer;font-size:13px}
footer{background:var(--ink);color:#cdbfa3;padding:50px 0 20px;font-size:14px}footer .w{display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:30px}footer h4{color:#fff;font-size:14px;margin:0 0 12px}footer a{display:block;padding:3px 0}footer a:hover{color:var(--brass2)}
.copy{border-top:1px solid #ffffff1a;margin-top:30px;padding-top:16px;text-align:center;font-size:13px;grid-column:1/-1}
.toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%) translateY(120px);background:var(--ink);color:#fff;padding:12px 20px;border-radius:999px;transition:.3s;z-index:50}.toast.on{transform:translateX(-50%)}
.wa{display:flex;align-items:center;gap:8px;position:fixed;right:18px;bottom:18px;background:#1fa855;color:#fff;border-radius:999px;padding:12px 18px;font-weight:600;box-shadow:0 8px 20px #0003;z-index:40}
.hb{display:none;background:none;border:0;font-size:24px;width:44px;height:44px;cursor:pointer;color:var(--text)}.drawer,.ov,.mbar,.fbtn{display:none}
:focus-visible{outline:2px solid var(--brass);outline-offset:2px}
@media(max-width:900px){body{padding-bottom:64px}.hb{display:grid;place-items:center}nav.mn{display:none}.top .w span:first-child{display:none}.hd{gap:10px;padding:10px 16px}.logo{font-size:19px}.logo small{display:none}.qc{display:none}
.ov:not([hidden]){display:block;position:fixed;inset:0;background:#0006;z-index:60}.drawer:not([hidden]){display:flex;flex-direction:column;position:fixed;top:0;left:0;bottom:0;width:min(86vw,340px);background:var(--card);z-index:61;padding:12px 16px;overflow:auto}
.drawer a{padding:12px 4px;border-bottom:1px solid var(--line);min-height:44px}.dh{display:flex;justify-content:space-between;align-items:center;padding-bottom:6px}.drawer hr{border:0;margin:8px 0}
.mbar{display:grid;grid-template-columns:repeat(5,1fr);position:fixed;left:0;right:0;bottom:0;height:64px;background:var(--card);border-top:1px solid var(--line);z-index:45;padding-bottom:env(safe-area-inset-bottom)}.mbar a{display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:11px;font-weight:600;color:var(--mute)}.mbar span{font-size:20px;line-height:1.1;position:relative;color:var(--text)}.mbar b{position:absolute;top:-4px;right:-14px;background:var(--brass);color:#fff;border-radius:999px;font-size:10px;padding:0 6px}
.toast{bottom:80px}.wa{bottom:80px}input,select,textarea{font-size:16px!important}
.grid{grid-template-columns:repeat(2,1fr);gap:10px}.pc .im{padding:8px}.pc .bd{padding:10px}.pc h3{font-size:14px}.pc h3 a{display:block;padding:6px 0;min-height:32px}.pc .btn{width:100%;justify-content:center;min-height:40px}
.secs{grid-template-columns:repeat(2,1fr);gap:10px}.fbtn{display:inline-flex}.side{display:none}.side.open{display:block;margin-bottom:12px}.layout{gap:0;padding-top:16px}
.pd{gap:20px}.pd .gal{padding:14px}.pd .qty{position:sticky;bottom:72px;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:10px;box-shadow:0 6px 20px #0000001a;z-index:5}.pd .qty .btn{flex:1;justify-content:center}
.hero .w{padding:36px 16px}.feat{margin-top:16px}.band{padding:24px}section{padding:36px 0}.qt td,.qt th{padding:8px}.qt img{width:48px;height:48px}}
@media(max-width:360px){.grid{grid-template-columns:1fr}}
@media(prefers-reduced-motion:reduce){*{transition:none!important;scroll-behavior:auto!important}}
@media(max-width:900px){nav.mn .w{overflow-x:auto;scrollbar-width:none}nav.mn .w::-webkit-scrollbar{display:none}nav.mn .btn{display:none}.dd .menu{position:fixed;left:12px;right:12px;top:auto;max-height:60vh;overflow:auto}.hero .w,.pd,.band,.layout{grid-template-columns:1fr}.feat{grid-template-columns:1fr 1fr}.feat div:nth-child(2){border-right:0}.side{position:static;max-height:none}.cards3{grid-template-columns:1fr}footer .w{grid-template-columns:1fr 1fr}.hd{flex-wrap:wrap}.srch{order:3;max-width:none;flex-basis:100%}.hero .hgrid{display:none}form .f{grid-template-columns:1fr}}
@media(prefers-color-scheme:dark){:root:not([data-theme=light]){--text:#efe7d8;--text2:#d4cab8;--paper:#100e0b;--card:#1b1813;--line:#332d23;--mute:#a69c8a;--tint:#2c2417;--ink:#0a0907;color-scheme:dark}}:root[data-theme=dark]{--text:#efe7d8;--text2:#d4cab8;--paper:#100e0b;--card:#1b1813;--line:#332d23;--mute:#a69c8a;--tint:#2c2417;--ink:#0a0907;color-scheme:dark}
.pc .im,.sec .im,.pd .gal,.hgrid div,.post .im img,.qt img{background:var(--well)}input,select,textarea{color:var(--text)}
nav.mn .w{align-items:center}nav.mn a,.dd>a{display:flex;align-items:center;height:48px}.dd{display:flex}nav.mn a.btn{height:auto}.dd .menu a{height:auto}
.tt{background:none;border:1.5px solid var(--line);border-radius:999px;width:40px;height:40px;cursor:pointer;color:var(--text);font-size:17px;flex:none}
.team{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:18px;margin:16px 0}.person{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:22px;display:flex;gap:16px;align-items:center}.av{width:64px;height:64px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#f3d98a,#b8892b 55%,#6b4c12);color:#14110d;display:grid;place-items:center;font:700 22px Fraunces;flex:none}.person b{display:block;font-size:17px}.person span{color:var(--mute);font-size:14px}.person a{color:var(--brass);font-size:14px;font-weight:600}
"""

JS = """
const K='se_quote';const get=()=>{try{return JSON.parse(localStorage.getItem(K))||{}}catch(e){return{}}};
const put=q=>{try{localStorage.setItem(K,JSON.stringify(q))}catch(e){}count()};
function count(){const n=Object.keys(get()).length;document.querySelectorAll('[data-qc]').forEach(b=>b.textContent=n)}
function toast(t){let el=document.querySelector('.toast');if(!el){el=document.createElement('div');el.className='toast';document.body.appendChild(el)}el.textContent=t;el.classList.add('on');setTimeout(()=>el.classList.remove('on'),1800)}
function addQ(code,qty){const q=get();q[code]=(q[code]||0)+(parseInt(qty)||1);put(q);toast(code+' added to your quote')}
document.addEventListener('click',ev=>{const b=ev.target.closest('[data-add]');if(b){ev.preventDefault();const qi=document.getElementById('qty');addQ(b.dataset.add,b.dataset.q?qi.value:1)}});
function plDone(){const p=document.getElementById('pl');if(!p)return;p.classList.add('gone');document.documentElement.classList.add('plx');try{sessionStorage.setItem('se_pl',1)}catch(e){}setTimeout(()=>p.remove(),700)}
document.addEventListener('DOMContentLoaded',()=>{if(document.documentElement.classList.contains('nopl')){const p=document.getElementById('pl');p&&p.remove();document.documentElement.classList.add('plx')}else{document.getElementById('pl').classList.add('go');setTimeout(plDone,2600)}
const rv=document.querySelectorAll('.sec,.pc,.card,.post,.band,.trust,.bulk,.person,.sh,.prose>*');rv.forEach((el,i)=>{el.classList.add('rv');el.style.setProperty('--d',(i%6)*60+'ms')});
if('IntersectionObserver' in window){const io=new IntersectionObserver(es=>es.forEach(en=>{if(en.isIntersecting){en.target.classList.add('in');io.unobserve(en.target)}}),{rootMargin:'0px 0px -8% 0px'});rv.forEach(el=>io.observe(el))}else rv.forEach(el=>el.classList.add('in'));
const hx=document.querySelector('.hero');if(hx&&!matchMedia('(prefers-reduced-motion: reduce)').matches){addEventListener('scroll',()=>{const y=scrollY;if(y<900)hx.style.setProperty('--py',y*0.25+'px')},{passive:true})}
const hd=document.querySelector('header');addEventListener('scroll',()=>hd.classList.toggle('sc',scrollY>10),{passive:true});
count();if(location.hash=='#search'){const i=document.getElementById('q')||document.getElementById('sq');i&&i.focus()}});
function menu(o){const d=document.getElementById('dr'),v=document.querySelector('.ov');d.hidden=v.hidden=!o;document.body.style.overflow=o?'hidden':'';document.querySelectorAll('[data-menu]').forEach(b=>b.setAttribute('aria-expanded',o));if(o)d.querySelector('a').focus()}
document.addEventListener('click',ev=>{if(ev.target.closest('[data-menu]'))menu(true);else if(ev.target.closest('[data-close]'))menu(false);const s=ev.target.closest('[data-share]');if(s&&navigator.share){ev.preventDefault();navigator.share({title:document.title,url:location.href})}const f=ev.target.closest('[data-filter]');if(f){const sd=document.querySelector('.side');sd.classList.toggle('open');f.setAttribute('aria-expanded',sd.classList.contains('open'))}});
document.addEventListener('keydown',ev=>{if(ev.key=='Escape')menu(false)});
let SI=null,sel=-1;async function sug(i){const q=i.value.toLowerCase().trim(),box=document.getElementById('sug'),b=i.dataset.base;if(q.length<2){box.hidden=true;i.setAttribute('aria-expanded',false);return}
if(!SI){try{SI=await (await fetch(b+'search.json')).json()}catch(e){return}}const words=q.split(/\s+/);const r=SI.filter(p=>{const t=(p[0]+' '+p[1]+' '+p[2]).toLowerCase();return words.every(w=>t.includes(w))}).slice(0,8);sel=-1;
box.innerHTML=r.length?r.map(p=>`<a role="option" href="${b}product/${p[3]}.html"><img src="${b}img/t/${p[0]}.jpg" alt=""><span><b>${p[1]}</b><small>${p[0]} · ${p[2]}</small></span></a>`).join('')+`<a class="all" href="${b}shop.html?q=${encodeURIComponent(q)}">See all results for “${q.replace(/</g,'')}”</a>`:`<p class="none">No products match “${q.replace(/</g,'')}”. Try a code like SE-3001.</p>`;box.hidden=false;i.setAttribute('aria-expanded',true)}
document.addEventListener('input',ev=>{if(ev.target.id=='sq')sug(ev.target)});
document.addEventListener('keydown',ev=>{if(ev.target.id!='sq')return;const a=[...document.querySelectorAll('#sug a')];if(!a.length)return;if(ev.key=='ArrowDown'||ev.key=='ArrowUp'){ev.preventDefault();sel=(sel+(ev.key=='ArrowDown'?1:-1)+a.length)%a.length;a.forEach((x,k)=>x.classList.toggle('on',k==sel))}else if(ev.key=='Enter'&&sel>=0){ev.preventDefault();location.href=a[sel].href}else if(ev.key=='Escape'){document.getElementById('sug').hidden=true}});
document.addEventListener('click',ev=>{if(!ev.target.closest('.srch')){const b=document.getElementById('sug');if(b)b.hidden=true}});
document.addEventListener('click',ev=>{if(!ev.target.closest('[data-theme-toggle]'))return;const r=document.documentElement,cur=r.dataset.theme||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'),n=cur=='dark'?'light':'dark';r.dataset.theme=n;try{localStorage.setItem('se_theme',n)}catch(e){}});
"""

WA_SVG = '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.1l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6a2.7 2.7 0 0 0 1.8-1.3 2.2 2.2 0 0 0 .2-1.3c-.1-.1-.3-.2-.6-.3z"/></svg>'
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Fraunces:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">'


def page(path, title, body, desc='', nav=''):
    depth = path.count('/')
    b = '../' * depth
    cats_nav = ''.join(f'<a href="{b}category/{slug(s)}.html" class="{"on" if nav == s else ""}">{e(s)}</a>' for s in SECTIONS)
    html_ = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc or CO['tag'])}">{FONTS}<meta name="theme-color" content="#14110d"><script>try{{const t=localStorage.getItem("se_theme");if(t)document.documentElement.dataset.theme=t}}catch(e){{}}try{{if(sessionStorage.getItem("se_pl")||matchMedia("(prefers-reduced-motion: reduce)").matches)document.documentElement.classList.add("nopl")}}catch(e){{document.documentElement.classList.add("nopl")}}</script><link rel="manifest" href="{b}manifest.webmanifest"><link rel="icon" href="{b}icon-192.png"><link rel="apple-touch-icon" href="{b}icon-192.png"><link rel="stylesheet" href="{b}style.css"><script>{JS}</script></head><body>
<div id="pl" aria-hidden="true"><div class="pl-room"></div><div class="pl-frame"><div class="pl-door"><div class="pl-panel"></div><div class="pl-panel b"></div><div class="pl-plate"><div class="pl-lever"></div><div class="pl-key"></div></div>
<svg class="pl-hand" viewBox="0 0 160 100"><defs><linearGradient id="sk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f0c9a2"/><stop offset="1" stop-color="#c98f63"/></linearGradient><linearGradient id="sl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1c1712"/><stop offset="1" stop-color="#3a3026"/></linearGradient></defs><rect x="-60" y="30" width="78" height="52" rx="14" fill="url(#sl)"/><rect x="10" y="28" width="12" height="56" rx="5" fill="#e9e1d2"/><path d="M20 36c18-8 40-10 62-8l46 4c8 1 13 5 13 10s-5 9-13 9l-36-1c6 4 8 9 6 14-3 7-10 10-18 10H44c-14 0-24-10-24-22z" fill="url(#sk)"/><path d="M86 44l42 2M84 52l40 1M78 60l34 0" stroke="#b77d55" stroke-width="2.2" stroke-linecap="round" opacity=".55"/><path d="M118 34c6 0 10 3 10 7" stroke="#fff" stroke-opacity=".35" stroke-width="2" fill="none" stroke-linecap="round"/><ellipse cx="128" cy="40" rx="4" ry="3" fill="#f6dccb" opacity=".8"/></svg></div></div>
<div class="pl-name">Sameer Exports<small>Since 1994 · Aligarh</small></div><button class="pl-skip" onclick="plDone()">Skip</button></div>
<div class="ambient"></div>
<div class="top"><div class="w"><span>ISO 9001 certified manufacturer &amp; exporter · Aligarh, India · Since 1994</span><span>{CO['phone']} · <a href="mailto:{CO['email']}">{CO['email']}</a></span></div></div>
<header><div class="hd w"><button class="hb" aria-label="Open menu" aria-controls="dr" aria-expanded="false" data-menu>☰</button><a class="logo" href="{b}index.html"><i></i><span>Sameer Exports<small>Brass Builders Hardware</small></span></a>
<form class="srch" action="{b}shop.html"><input id="sq" type="search" enterkeyhint="search" name="q" placeholder="Search products or codes" aria-label="Search products" autocomplete="off" role="combobox" aria-expanded="false" aria-controls="sug" data-base="{b}"><div class="sug" id="sug" role="listbox" hidden></div><button class="btn">Search</button></form>
<button class="tt" data-theme-toggle aria-label="Switch light or dark theme">◐</button><a class="qc" href="{b}quote.html">Quote list <b data-qc>0</b></a></div>
<nav class="mn"><div class="w"><a href="{b}index.html">Home</a><div class="dd"><a href="{b}shop.html" class="{"on" if nav and nav != "shop" or nav == "shop" else ""}">Products ▾</a><div class="menu"><a href="{b}shop.html"><b>All products</b></a>{cats_nav}</div></div><a href="{b}export.html">Export &amp; Bulk</a><a href="{b}finishes.html">Finishes</a><a href="{b}about.html">About</a><a href="{b}blog/index.html">Blog</a><a href="{b}contact.html">Contact</a><a class="btn s" href="{b}quote.html" style="margin-left:auto;align-self:center">Get a quote</a></div></nav></header>
<div class="ov" data-close hidden></div><nav class="drawer" id="dr" aria-label="Mobile menu" hidden><div class="dh"><b>Menu</b><button class="hb" aria-label="Close menu" data-close>✕</button></div><a href="{b}shop.html"><b>All products</b></a>{cats_nav}<hr><a href="{b}export.html">Export &amp; bulk orders</a><a href="{b}finishes.html">Finishes guide</a><a href="{b}about.html">About</a><a href="{b}blog/index.html">Blog</a><a href="{b}faq.html">FAQ</a><a href="{b}contact.html">Contact</a><a class="btn" href="tel:{CO['phone']}" style="margin-top:12px;justify-content:center">Call {CO['phone']}</a></nav>
<nav class="mbar" aria-label="Quick actions"><a href="{b}index.html"><span>⌂</span>Home</a><a href="{b}shop.html"><span>▦</span>Shop</a><a href="{b}shop.html#search" data-search><span>⌕</span>Search</a><a href="{b}quote.html"><span>☰<b data-qc>0</b></span>Quote</a><a href="tel:{CO['phone']}"><span>✆</span>Call</a></nav>
<a class="wa" href="https://wa.me/{CO['wa']}?text={quote_plus('Hello Sameer Exports, I would like a quote.')}" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">{WA_SVG}<span>WhatsApp</span></a>
<main>{body.replace('{B}', b)}</main>
<footer><div class="w"><div><a class="logo" href="{b}index.html" style="color:#fff"><i></i>Sameer Exports</a><p>Manufacturer and exporter of brass, iron and aluminium builders hardware, wooden and bone knobs, and art ware. Supplying the UK, US, Mexico, Germany, Canada and Australia.</p><p>{e(CO['addr'])}</p></div>
<div><h4>Shop</h4>{''.join(f'<a href="{b}category/{slug(s)}.html">{e(s)}</a>' for s in list(SECTIONS)[:7])}</div>
<div><h4>Company</h4><a href="{b}about.html">About us</a><a href="{b}finishes.html">Finishes guide</a><a href="{b}export.html">Export &amp; bulk orders</a><a href="{b}faq.html">FAQ</a><a href="{b}blog/index.html">Blog</a><a href="{b}contact.html">Contact</a></div>
<div><h4>Contact</h4><a href="tel:{CO['phone']}">Phone {CO['phone']}</a><span>Fax {CO['fax']}</span><a href="mailto:{CO['email']}">{CO['email']}</a><p style="font-size:12px">GSTIN {CO['gst']}<br>IEC {CO['iec']}</p><a href="{b}privacy.html">Privacy</a><a href="{b}terms.html">Terms</a></div>
<div class="copy">© {YEAR} Sameer Exports, Aligarh. All rights reserved.</div></div></footer>
</body></html>"""
    f = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(f), exist_ok=True)
    open(f, 'w', encoding='utf-8').write(html_)


TRUST = '<div class="trust"><div><b>ISO 9001</b><span>Certified quality</span></div><div><b>Since 1994</b><span>Aligarh manufacturer</span></div><div><b>Custom finishes</b><span>14 finish options</span></div><div><b>Export packing</b><span>Sea &amp; air freight</span></div><div><b>WhatsApp support</b><span>Fast replies</span></div></div>'
BULK = '<div class="bulk"><div><h2>Buying in bulk?</h2><p>Send your product codes and quantities. We reply with price, MOQ, packing and lead time for your market.</p></div><div style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn" href="{B}quote.html">Request bulk quote</a><a class="btn wab" target="_blank" rel="noopener" href="https://wa.me/919758155555?text=Bulk%20enquiry">WhatsApp us</a></div></div>'


def row(c, ps, href):
    return f'<div class="rng"><div class="sh"><div><h2>{e(c)}</h2><span class="mt">{len(ps)} designs</span></div><a href="{href}">View all →</a></div><div class="rowx">{"".join(card(p) for p in ps[:10])}</div></div>'


def card(p):
    meta = ' · '.join(x for x in (p['size'], p['finish']) if x)
    return f"""<article class="pc"><a class="im" href="{{B}}product/{p['slug']}.html"><img loading="lazy" src="{{B}}img/t/{p['code']}.jpg" alt="{e(p['name'])} {p['code']}"></a>
<div class="bd"><span class="cd">{p['code']}</span><h3><a href="{{B}}product/{p['slug']}.html">{e(p['name'])}</a></h3><span class="mt">{e(meta)}</span><button class="btn s" data-add="{p['code']}">Add to quote</button></div></article>"""


def pick(n, step):
    return [P[i] for i in range(0, len(P), step)][:n]


# ---------- home
hero_imgs = ''.join(f'<div><img src="{{B}}img/t/{c}.jpg" alt=""></div>' for c in ['SE-3001', 'SE-1021', 'SE-3017', 'SE-22008', 'SE-25011', 'SE-18001'])
sec_tiles = ''.join(f"""<a class="sec" href="{{B}}category/{slug(s)}.html"><div class="im"><img loading="lazy" src="{{B}}img/t/{list(c.values())[0][0]['code']}.jpg" alt=""></div><b>{e(s)}</b><span>{sum(len(v) for v in c.values())} products · {len(c)} ranges</span></a>""" for s, c in SECTIONS.items())
popular = ''.join(card(p) for p in pick(10, 91))
brass_cats = ''.join(f"""<a class="sec" href="{{B}}category/{slug(c)}.html"><div class="im"><img loading="lazy" src="{{B}}img/t/{ps[0]['code']}.jpg" alt=""></div><b>{e(c)}</b><span>{len(ps)} products</span></a>""" for c, ps in list(SECTIONS['Brass Hardware'].items())[:12])
home = f"""<div class="hero"><div class="w"><div><span class="kick">Manufacturer &amp; exporter · Aligarh, India</span>
<h1>Solid brass hardware, <em>cast and finished</em> by hand since 1994.</h1><p>Door knockers, lever handles, hinges, cabinet fittings and wrought iron. Over 900 catalogue designs, made to order for importers, wholesalers and builders worldwide.</p>
<p style="display:flex;gap:12px;flex-wrap:wrap"><a class="btn" href="{{B}}shop.html">Browse the catalogue</a><a class="btn o" href="{{B}}export.html">Bulk &amp; export orders</a></p></div>
<div class="h3d"><canvas id="knock" aria-label="Animated 3D brass door knocker. Drag to rotate." role="img"></canvas><div class="hgrid">{hero_imgs}</div><span class="h3hint">Drag to rotate</span></div></div></div>
<script type="importmap">{{"imports":{{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}}}</script><script type="module" src="{{B}}knocker3d.js"></script>
<div class="w"><div class="feat"><div><b>ISO 9001 certified</b><span>Strict quality control</span></div><div><b>900+ designs</b><span>Brass, iron, aluminium, wood</span></div><div><b>14 finishes</b><span>BPL, SCP, antique, powder coat</span></div><div><b>Exporting worldwide</b><span>UK, US, EU, Canada, Australia</span></div></div></div>
<section><div class="w"><div class="sh"><div><span class="kick">Catalogue</span><h2>Shop by range</h2></div><a href="{{B}}shop.html">View all products →</a></div><div class="secs">{sec_tiles}</div></div></section>
<section style="padding-top:0"><div class="w"><div class="sh"><div><span class="kick">Brass hardware</span><h2>Popular brass ranges</h2></div><a href="{{B}}category/brass-hardware.html">All brass →</a></div><div class="secs">{brass_cats}</div></div></section>
<section style="padding-top:0"><div class="w"><div class="sh"><div><span class="kick">Featured</span><h2>From the catalogue</h2></div><a href="{{B}}shop.html">See everything →</a></div><div class="grid">{popular}</div></div></section>
<section style="padding-top:0"><div class="w"><div class="band"><div><span class="kick">Since 1994</span><h2>Sand cast, forged, polished and lacquered in Aligarh</h2><p>Sameer Exports was started in 1994 by Mr. Sanjeev Agarwal under the direction of Er. S.P. Agarwal. Production combines traditional sand casting with modern forging machines, and every piece is finished, polished, lacquered and packed to international buyer standards.</p><a class="btn" href="{{B}}about.html">Our story</a></div>
<div class="stats"><div><b>1994</b>Established</div><div><b>{len(P)}+</b>Catalogue designs</div><div><b>{len(CATS)}</b>Product ranges</div><div><b>6+</b>Export countries</div></div></div></div></section>
<section style="padding-top:0"><div class="w"><div class="sh"><div><span class="kick">How ordering works</span><h2>Request a quote in three steps</h2></div></div><div class="cards3"><div class="card"><h3>1. Build your list</h3><p>Add any catalogue code to your quote list, with the quantity and finish you need.</p></div><div class="card"><h3>2. Send the enquiry</h3><p>Submit the list. We reply with pricing, MOQ, packing and lead time for your market.</p></div><div class="card"><h3>3. Sample and ship</h3><p>Approve samples, confirm the order and we dispatch by sea or air freight.</p></div></div></div></section>"""
page('index.html', 'Sameer Exports | Brass Builders Hardware Manufacturer, Aligarh', home, 'Manufacturer and exporter of brass door hardware, iron hardware, knobs and art ware from Aligarh, India since 1994.')

# ---------- shop (client side filter over embedded index)
idx = [[p['code'], p['name'], p['category'], p['section'], p['size'], p['finish'], p['slug']] for p in P]
side = ''.join(f'<h4>{e(s)}</h4>' + ''.join(f'<a href="#" data-c="{e(c)}">{e(c)} <span>{len(ps)}</span></a>' for c, ps in cs.items()) for s, cs in SECTIONS.items())
fins = sorted({p['finish'] for p in P if p['finish']})
shop = f"""<div class="w"><div class="crumb"><a href="{{B}}index.html">Home</a> / All products</div><div class="layout"><aside class="side"><a href="#" data-c="" class="on">All products <span>{len(P)}</span></a>{side}</aside>
<div><div class="bar"><button class="btn o s fbtn" data-filter aria-expanded="false">Filter by range</button><input id="q" type="search" enterkeyhint="search" placeholder="Search name or code" style="flex:1;min-width:200px"><select id="sort" aria-label="Sort"><option value="">Sort: catalogue order</option><option value="az">Name A to Z</option><option value="za">Name Z to A</option><option value="code">Product code</option></select><select id="fin" aria-label="Finish"><option value="">All finishes</option>{''.join(f'<option>{e(f)}</option>' for f in fins)}</select><span id="n" class="mt"></span></div><div class="grid" id="g"></div><p style="text-align:center"><button class="btn o" id="more">Load more</button></p></div></div></div>
<script>const D={json.dumps(idx)};let lim=48,cat='';const qs=new URLSearchParams(location.search);const qi=document.getElementById('q');qi.value=qs.get('q')||'';cat=qs.get('cat')||'';
function esc(s){{return s.replace(/[&<>"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]))}}
function render(){{const q=qi.value.toLowerCase().trim(),f=document.getElementById('fin').value;let r=D.filter(p=>(!cat||p[2]==cat)&&(!f||p[5]==f)&&(!q||(p[0]+' '+p[1]+' '+p[2]+' '+p[3]).toLowerCase().includes(q)));
const so=document.getElementById('sort').value;if(so)r=[...r].sort((a,b)=>so=='code'?parseInt(a[0].slice(3))-parseInt(b[0].slice(3)):so=='az'?a[1].localeCompare(b[1]):b[1].localeCompare(a[1]));document.getElementById('n').textContent='Showing '+Math.min(lim,r.length)+' of '+r.length+' products';document.getElementById('g').innerHTML=r.slice(0,lim).map(p=>`<article class="pc"><a class="im" href="product/${{p[6]}}.html"><img loading="lazy" src="img/t/${{p[0]}}.jpg" alt="${{esc(p[1])}}"></a><div class="bd"><span class="cd">${{p[0]}}</span><h3><a href="product/${{p[6]}}.html">${{esc(p[1])}}</a></h3><span class="mt">${{esc([p[4],p[5]].filter(Boolean).join(' · '))}}</span><button class="btn s" data-add="${{p[0]}}">Add to quote</button></div></article>`).join('');
document.getElementById('more').style.display=r.length>lim?'':'none';document.querySelectorAll('.side a').forEach(a=>a.classList.toggle('on',a.dataset.c==cat))}}
document.querySelectorAll('.side a').forEach(a=>a.onclick=ev=>{{ev.preventDefault();cat=a.dataset.c;lim=48;render();document.querySelector('.side').classList.remove('open');scrollTo(0,0)}});qi.oninput=()=>{{lim=48;render()}};document.getElementById('fin').onchange=render;document.getElementById('sort').onchange=()=>{{lim=48;render()}};document.getElementById('more').onclick=()=>{{lim+=48;render()}};new IntersectionObserver(es=>{{if(es[0].isIntersecting&&document.getElementById('more').style.display!='none'){{lim+=48;render()}}}},{{rootMargin:'600px'}}).observe(document.getElementById('more'));render();</script>"""
page('shop.html', 'All Products | Sameer Exports', shop, 'Browse the full Sameer Exports catalogue of brass, iron, aluminium and wooden hardware.', 'shop')

# ---------- section + category pages
for s, cs in SECTIONS.items():
    tiles = ''.join(f"""<a class="sec" href="{slug(c)}.html"><div class="im"><img loading="lazy" src="{{B}}img/t/{ps[0]['code']}.jpg" alt=""></div><b>{e(c)}</b><span>{len(ps)} products</span></a>""" for c, ps in cs.items())
    rows = ''.join(row(c, ps, f'{slug(c)}.html') for c, ps in cs.items() if slug(c) != slug(s))
    body = f'<div class="w"><div class="crumb"><a href="{{B}}index.html">Home</a> / {e(s)}</div><section style="padding-top:20px"><h1>{e(s)}</h1><p class="mt">{sum(len(v) for v in cs.values())} designs across {len(cs)} ranges.</p><div class="secs">{tiles}</div>{TRUST}</section><section style="padding-top:0">{rows}{BULK}</section></div>'
    page(f'category/{slug(s)}.html', f'{s} | Sameer Exports', body, f'{s} manufactured and exported by Sameer Exports, Aligarh.', s)
    for c, ps in cs.items():
        if slug(c) == slug(s):
            continue
        body = f'<div class="w"><div class="crumb"><a href="{{B}}index.html">Home</a> / <a href="{slug(s)}.html">{e(s)}</a> / {e(c)}</div><section style="padding-top:20px"><div class="sh"><div><h1>{e(c)}</h1><p class="mt">{len(ps)} designs. All items are made to order; add codes to your quote list for pricing.</p></div></div><div class="grid">{"".join(card(p) for p in ps)}</div>{BULK}</section></div>'
        page(f'category/{slug(c)}.html', f'{c} | Sameer Exports', body, f'{c}: {len(ps)} designs from Sameer Exports, Aligarh, India.', s)

# ---------- product pages
for i, p in enumerate(P):
    rel = [q for q in CATS[p['category']] if q is not p][:8]
    rows = ''.join(f'<tr><td>{k}</td><td>{e(v)}</td></tr>' for k, v in [('Product code', p['code']), ('Range', p['category']), ('Material group', p['section']), ('Size', p['size']), ('Finish', p['finish'])] if v)
    ld = json.dumps({"@context": "https://schema.org", "@type": "Product", "name": p['name'], "sku": p['code'], "category": p['category'], "brand": {"@type": "Brand", "name": "Sameer Exports"}, "image": f"img/p/{p['code']}.jpg"})
    body = f"""<div class="w"><div class="crumb"><a href="{{B}}index.html">Home</a> / <a href="{{B}}category/{slug(p['section'])}.html">{e(p['section'])}</a> / <a href="{{B}}category/{p['cslug']}.html">{e(p['category'])}</a> / {p['code']}</div>
<div class="pd"><div class="gal"><img src="{{B}}img/p/{p['code']}.jpg" alt="{e(p['name'])}"></div><div><span class="kick">{p['code']}</span><h1>{e(p['name'])}</h1><p class="mt">{e(p['category'])}</p><table class="spec">{rows}</table>
<div class="qty"><label for="qty">Qty</label><input id="qty" type="number" inputmode="numeric" min="1" value="100"><button class="btn" data-add="{p['code']}" data-q="1">Add to quote list</button></div>
<div class="note">Made to order. Other finishes and sizes are usually possible. Pricing, MOQ and lead time are sent with your quote.</div>
<p style="margin-top:16px;display:flex;gap:8px;flex-wrap:wrap"><a class="btn s wab" target="_blank" rel="noopener" href="https://wa.me/{CO['wa']}?text={quote_plus(f"Hello, I am interested in {p['code']} {p['name']}. Please send price and MOQ.")}">{WA_SVG} Ask on WhatsApp</a><button class="btn o s" data-share>Share</button><a class="btn o s" href="mailto:{CO['email']}?subject=Enquiry%20{p['code']}">Email about this item</a></p></div></div>
<section style="padding-top:0"><div class="sh"><h2>More {e(p['category'].lower())}</h2></div><div class="grid">{''.join(card(q) for q in rel)}</div></section></div><script type="application/ld+json">{ld}</script>"""
    page(f"product/{p['slug']}.html", f"{p['code']} {p['name']} | Sameer Exports", body, f"{p['name']} ({p['code']}), {p['category']}. {p['size']} {p['finish']}".strip())

# ---------- quote list (cart)
qidx = {p['code']: [p['name'], p['slug'], p['finish']] for p in P}
quote = f"""<div class="w"><div class="crumb"><a href="{{B}}index.html">Home</a> / Quote list</div><section style="padding-top:20px"><h1>Your quote list</h1><p class="mt">Review quantities, add your details and send. We reply with prices, MOQ and lead times.</p>
<table class="qt"><thead><tr><th></th><th>Product</th><th>Qty</th><th></th></tr></thead><tbody id="rows"></tbody></table><p id="empty" class="note" style="display:none">Your list is empty. <a href="shop.html" style="color:var(--brass)">Browse products</a>.</p>
<h2 style="margin-top:36px">Your details</h2><form id="qf"><div class="f"><label>Name<input required name="name" autocomplete="name"></label><label>Company<input name="company" autocomplete="organization"></label><label>Email<input required type="email" name="email" autocomplete="email"></label><label>Phone / WhatsApp<input name="phone" autocomplete="tel"></label>
<label>Country<input name="country" autocomplete="country-name"></label><label>Buyer type<select name="type"><option>Importer / distributor</option><option>Wholesaler</option><option>Retailer</option><option>Builder / architect</option><option>Individual</option></select></label><label class="full">Notes (finish, packing, target price)<textarea name="notes" rows="4"></textarea></label></div>
<p style="display:flex;gap:10px;flex-wrap:wrap"><button class="btn">Send enquiry by email</button><button type="button" class="btn wab" id="wasend">{WA_SVG} Send on WhatsApp</button></p><p class="mt">This opens your email app with the full list filled in, addressed to {CO['email']}.</p></form></section></div>
<script>const I={json.dumps(qidx)};function draw(){{const q=get(),k=Object.keys(q);document.getElementById('empty').style.display=k.length?'none':'';document.getElementById('rows').innerHTML=k.map(c=>`<tr><td><img src="img/t/${{c}}.jpg" alt=""></td><td><b>${{c}}</b><br><a href="product/${{I[c][1]}}.html">${{I[c][0]}}</a><br><span class="mt">${{I[c][2]}}</span></td><td><input type="number" min="1" value="${{q[c]}}" data-c="${{c}}"></td><td><button class="x" data-r="${{c}}">Remove</button></td></tr>`).join('')}}
document.addEventListener('input',ev=>{{const c=ev.target.dataset.c;if(c){{const q=get();q[c]=Math.max(1,parseInt(ev.target.value)||1);put(q)}}}});document.addEventListener('click',ev=>{{const r=ev.target.dataset.r;if(r){{const q=get();delete q[r];put(q);draw()}}}});
document.getElementById('qf').onsubmit=ev=>{{ev.preventDefault();const q=get();if(!Object.keys(q).length){{toast('Add products first');return}}const f=new FormData(ev.target);let b='Quote request\\n\\n'+Object.keys(q).map(c=>`${{c}}  ${{I[c][0]}}  x ${{q[c]}}`).join('\\n')+'\\n\\n';for(const [k,v] of f)b+=k+': '+v+'\\n';location.href='mailto:{CO['email']}?subject='+encodeURIComponent('Quote request - '+(f.get('company')||f.get('name')))+'&body='+encodeURIComponent(b)}};document.getElementById('wasend').onclick=()=>{{const q=get();if(!Object.keys(q).length){{toast('Add products first');return}}const f=new FormData(document.getElementById('qf'));let b='Quote request\n'+Object.keys(q).map(c=>`${{c}} ${{I[c][0]}} x ${{q[c]}}`).join('\n')+'\n';for(const [k,v] of f)if(v)b+=k+': '+v+'\n';window.open('https://wa.me/{CO['wa']}?text='+encodeURIComponent(b),'_blank')}};draw();</script>"""
page('quote.html', 'Quote List | Sameer Exports', quote)

# ---------- static content pages
FIN = [("BPL", "Brass Polished Lacquered"), ("CP", "Chrome Plated"), ("SCP", "Satin Chrome Plated"), ("AB", "Antique Brass"), ("GPL", "Gold Polished Lacquered"), ("BSC", "Black Satin Chrome"), ("HDP", "Hot Dip Galvanised"), ("PC", "Powder Coated"), ("PCT", "Powder Coated Textured"), ("FB", "Florantine Bronze"), ("ZP", "Zinc Plated"), ("EPNS", "Electro Plated Nickel Silver"), ("ORB", "Oil Rubbed Bronze"), ("A", "Anodized")]
fcount = collections.Counter(p['finish'] for p in P)
pages = {
 'about.html': ('About Us', f"""<span class="kick">Since 1994</span><h1>About Sameer Exports</h1><p>Sameer Exports was started in 1994 by Mr. Sanjeev Agarwal under the direction of Er. S.P. Agarwal. Today it is one of the leading manufacturers and exporters of brass, aluminium and forged wrought iron ironmongery, wooden products and art ware from Aligarh, India, the country's traditional centre for brass and lock making.</p>
<h2>Leadership</h2><div class="team"><div class="person"><div class="av">SA</div><div><b>Sanjeev Agarwal</b><span>Owner &amp; Proprietor</span><br><span>Founded Sameer Exports in 1994</span></div></div><div class="person"><div class="av">SA</div><div><b>Sarthak Agarwal</b><span>Director</span><br><a href="https://www.instagram.com/_agarwalsarthak_/" target="_blank" rel="noopener">Instagram @_agarwalsarthak_</a></div></div></div>
<h2>Infrastructure</h2><p>The company has well equipped in-house manufacturing. We use traditional sand casting, and products are partly mechanised and partly handcrafted. Modern forging machines produce high-density, non-porous, high-quality parts, while finishing, polishing, lacquering and packaging conform to international standards and buyer requirements.</p>
<h2>Quality</h2><p>Sameer Exports is an ISO 9001 certified company. We run strict quality control programmes and bring innovative ideas into design and production so that every product is functional, elegant and competitively priced.</p>
<h2>Clients</h2><p>Our range has earned clients across the UK, US, Mexico, Germany, Canada and Australia.</p><h2>Research &amp; development</h2><p>A team of qualified designers and consultants keeps the range evolving, using high quality materials to match international standards.</p>
<h2>Company details</h2><table class="spec"><tr><td>Owner</td><td>{CO['owner']}</td></tr><tr><td>Director</td><td>Sarthak Agarwal</td></tr><tr><td>Address</td><td>{CO['addr']}</td></tr><tr><td>GSTIN</td><td>{CO['gst']}</td></tr><tr><td>Import Export Code</td><td>{CO['iec']}</td></tr><tr><td>Legal status</td><td>Proprietorship</td></tr></table>"""),
 'finishes.html': ('Finishes Guide', '<span class="kick">Finish codes</span><h1>Finishes guide</h1><p>Every catalogue item lists a finish code. Most designs can be produced in other finishes on request.</p><table class="spec">' + ''.join(f'<tr><td><b>{c}</b></td><td>{n} <span class="mt">({fcount.get(n, 0)} catalogue items)</span></td></tr>' for c, n in FIN) + '</table>'),
 'export.html': ('Export & Bulk Orders', """<span class="kick">B2B</span><h1>Export &amp; bulk orders</h1><p>We manufacture to order for importers, distributors, wholesalers and project buyers. Send your product list with codes and quantities and we will reply with a detailed quotation.</p><h2>What we offer</h2><ul><li>Custom finishes, sizes and packing on most designs</li><li>Private label and custom packaging</li><li>Samples before bulk production</li><li>Sea and air freight from India, with export documentation</li><li>Quality checks at every stage under our ISO 9001 system</li></ul><h2>What to include in an enquiry</h2><ul><li>Product codes and quantities</li><li>Required finish for each item</li><li>Destination country and port</li><li>Packing requirements</li></ul><p><a class="btn" href="quote.html">Open quote list</a></p>"""),
 'faq.html': ('FAQ', """<h1>Frequently asked questions</h1><h2>Do you sell retail?</h2><p>We are a manufacturer and exporter, so orders are made to order in trade quantities. Small trial orders and samples can be discussed.</p><h2>Why are prices not shown?</h2><p>Price depends on finish, quantity, packing and destination. Add items to your quote list and we will send exact pricing.</p><h2>Can I get a different finish?</h2><p>Yes. Most brass items can be supplied in polished lacquered, chrome, satin chrome, antique or other finishes. See the finishes guide.</p><h2>What is the lead time?</h2><p>Lead time depends on the quantity and finish and is confirmed with each quotation.</p><h2>Which countries do you ship to?</h2><p>We export worldwide, with regular clients in the UK, US, Mexico, Germany, Canada and Australia.</p>"""),
 'contact.html': ('Contact', f"""<span class="kick">Get in touch</span><h1>Contact us</h1><div class="cards3"><div class="card"><h3>Factory &amp; office</h3><p>{CO['addr']}</p><p><a style="color:var(--brass)" href="https://www.google.com/maps/place/?q=place_id:0x3974bb9986410309:0x683f90c2772f122f" target="_blank" rel="noopener">Get directions →</a></p></div><div class="card"><h3>Phone</h3><p><a href="tel:{CO['phone']}">{CO['phone']}</a><br>Fax {CO['fax']}</p></div><div class="card"><h3>WhatsApp</h3><p><a href="https://wa.me/{CO['wa']}" target="_blank" rel="noopener">+91 97581 55555</a></p></div><div class="card"><h3>Email</h3><p><a href="mailto:{CO['email']}">{CO['email']}</a></p></div></div>
<h2>Send a message</h2><form onsubmit="event.preventDefault();const f=new FormData(this);location.href='mailto:{CO['email']}?subject='+encodeURIComponent('Website enquiry - '+f.get('name'))+'&body='+encodeURIComponent(f.get('msg')+'\\n\\n'+f.get('name')+'\\n'+f.get('email')+'\\n'+f.get('phone'))"><div class="f"><label>Name<input required name="name" autocomplete="name"></label><label>Email<input required type="email" name="email" autocomplete="email"></label><label>Phone<input name="phone" autocomplete="tel"></label><label class="full">Message<textarea required name="msg" rows="5"></textarea></label></div><p><button class="btn">Send</button></p></form>
<iframe title="Map" style="width:100%;height:320px;border:0;border-radius:14px;margin-top:20px" loading="lazy" src="https://maps.google.com/maps?q=27.9303815,78.1375334&z=16&output=embed"></iframe>"""),
 'privacy.html': ('Privacy Policy', '<h1>Privacy policy</h1><p>This website does not use tracking cookies or collect personal data on its servers. Your quote list is stored only in your own browser. When you send an enquiry, it opens your email application, and the details you choose to send are used only to reply to your enquiry.</p>'),
 'terms.html': ('Terms', '<h1>Terms of use</h1><p>Product images and specifications are for reference. Specifications are subject to change without notice. All orders are confirmed by written quotation and proforma invoice.</p>'),
 '404.html': ('Page not found', '<h1>Page not found</h1><p>The page you are looking for does not exist.</p><p><a class="btn" href="index.html">Go home</a> <a class="btn o" href="shop.html">Browse products</a></p>'),
}
for f, (t, b) in pages.items():
    page(f, f'{t} | Sameer Exports', f'<div class="w"><section class="prose">{b}</section></div>')

# ---------- blog
def imgs(codes):
    return ''.join(f'<img src="../img/t/{c}.jpg" alt="">' for c in codes)
POSTS = [
 ('choosing-a-brass-door-knocker', 'How to choose a brass door knocker', ['SE-3001', 'SE-3005', 'SE-3017'], """<p>A door knocker is the first piece of hardware a visitor touches. Choosing one comes down to three things: the style of the door, the size, and the finish.</p><h2>Match the period of the house</h2><p>Georgian homes suit urn and ring knockers such as SE-3001. Victorian doors carry heavier, ornate designs like the Medusa head SE-3017. Cottages and country doors look right with animal motifs, for example the horse head SE-3005.</p><h2>Get the size right</h2><p>Most front doors take a knocker between 150mm and 210mm. Smaller 110 to 125mm designs suit narrow or cottage doors.</p><h2>Pick a finish that lasts</h2><p>Polished lacquered brass (BPL) keeps its shine for years. Antique and Florentine bronze finishes hide fingerprints and weather well. See our <a href="../finishes.html">finishes guide</a>.</p>"""),
 ('brass-finishes-explained', 'Brass hardware finishes explained: BPL, SCP, antique and more', ['SE-1021', 'SE-2004', 'SE-2001'], """<p>Our catalogue lists a finish code next to every product. Here is what they mean in practice.</p><h2>BPL, Brass Polished Lacquered</h2><p>Bright polished brass sealed with clear lacquer. The classic look and our most common finish.</p><h2>CP and SCP, chrome and satin chrome</h2><p>Chrome plating over brass gives a cool modern tone. Satin chrome is brushed and hides marks.</p><h2>Antique brass and Florentine bronze</h2><p>Darkened finishes that look aged from day one, ideal for heritage projects.</p><h2>PC and PCT, powder coated</h2><p>Used on our iron range: a tough black coating, smooth or textured.</p>"""),
 ('wrought-iron-hardware-guide', 'Wrought iron door hardware for rustic and heritage doors', ['SE-25011', 'SE-30005', 'SE-39001'], """<p>Black iron hardware suits oak doors, barns, gates and cottages. Our iron range covers lever handles, gate latches, hinges, studs and hand forged entrance handles.</p><h2>Hand forged vs cast</h2><p>Hand forged handles are shaped one by one on the anvil, so each piece has slight variation. Cast iron pieces are uniform and cost less in volume.</p><h2>Finishes</h2><p>Powder coated (PC) and textured powder coat (PCT) finishes protect iron from rust indoors. For exterior gates, hot dip galvanised (HDP) is recommended.</p>"""),
 ('importing-hardware-from-india', 'Importing builders hardware from India: a buyer checklist', ['SE-4001', 'SE-15003', 'SE-10001'], """<p>Aligarh has supplied brass hardware to the world for generations. If you are importing for the first time, this checklist keeps orders smooth.</p><ol><li>Shortlist product codes from the catalogue.</li><li>Agree the finish and packing for each item.</li><li>Order samples and approve them in writing.</li><li>Confirm MOQ, price terms (FOB or CIF) and lead time.</li><li>Check documents: invoice, packing list, certificate of origin.</li></ol><p>Ready to start? Add items to your <a href="../quote.html">quote list</a>.</p>"""),
 ('cabinet-knobs-and-pulls', 'Cabinet knobs and pulls in brass, wood and bone', ['SE-18011', 'SE-41051', 'SE-8001'], """<p>Small hardware changes a kitchen or a wardrobe more than any other detail. We make cabinet knobs in brass, iron, wood and bone with inlay.</p><h2>Brass cabinet knobs</h2><p>Ring, octagonal, Georgian and reeded designs from 25 to 50mm.</p><h2>Wooden and bone knobs</h2><p>Hand carved and inlaid knobs are popular for boutique and furniture brands.</p><h2>Drawer and cup pulls</h2><p>Cup pulls from 65 to 102mm in brass and iron suit shaker and vintage cabinets.</p>"""),
]
cards = ''
for sl, t, cs, body in POSTS:
    page(f'blog/{sl}.html', f'{t} | Sameer Exports Blog', f'<div class="w"><div class="crumb"><a href="../index.html">Home</a> / <a href="index.html">Blog</a></div><section class="prose"><h1>{e(t)}</h1><div class="post" style="margin-bottom:20px"><div class="im">{imgs(cs)}</div></div>{body}<p><a class="btn" href="../shop.html">Browse the catalogue</a></p></section></div>', t)
    cards += f'<a class="post" href="{sl}.html"><div class="im">{imgs(cs)}</div><div class="bd"><h3>{e(t)}</h3><span class="mt">Read article →</span></div></a>'
page('blog/index.html', 'Blog | Sameer Exports', f'<div class="w"><section><span class="kick">Guides</span><h1>Hardware guides &amp; news</h1><div class="blog">{cards}</div></section></div>')

open(os.path.join(OUT, 'style.css'), 'w').write(CSS)
import shutil; shutil.copy(os.path.join(ROOT, 'knocker3d.js'), os.path.join(OUT, 'knocker3d.js'))
json.dump([[p['code'], p['name'], p['category'], p['slug']] for p in P], open(os.path.join(OUT, 'search.json'), 'w'))
json.dump({"name": "Sameer Exports", "short_name": "Sameer", "start_url": "index.html", "display": "standalone", "background_color": "#faf7f1", "theme_color": "#14110d", "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"}]}, open(os.path.join(OUT, 'manifest.webmanifest'), 'w'))
from PIL import Image, ImageDraw
for n in (192, 512):
    im = Image.new('RGB', (n, n), '#14110d'); d = ImageDraw.Draw(im); m = n // 6
    d.ellipse((m, m, n - m, n - m), fill='#b8892b'); d.ellipse((m * 2, m * 2, n - m * 2, n - m * 2), fill='#d9b45a')
    im.save(os.path.join(OUT, f'icon-{n}.png'))
urls = ['index.html', 'shop.html', 'quote.html', 'blog/index.html'] + list(pages) + [f'blog/{p[0]}.html' for p in POSTS] + [f"product/{p['slug']}.html" for p in P]
open(os.path.join(OUT, 'sitemap.txt'), 'w').write('\n'.join(urls))
print('pages:', len(urls) + len(CATS) + len(SECTIONS))
