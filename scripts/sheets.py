import os,json,sys
from PIL import Image, ImageDraw
w=sys.argv[1]
R=json.load(open(w+'/records_seg.json'))
codes=[r['code'] for r in R]
T=170;cols=10;per=60
os.makedirs(w+'/sheets',exist_ok=True)
for f in os.listdir(w+'/sheets'): os.remove(w+'/sheets/'+f)
for k in range(0,len(codes),per):
    cs=codes[k:k+per];rows=(len(cs)+cols-1)//cols
    sh=Image.new('RGB',(cols*T,rows*T),'white');dr=ImageDraw.Draw(sh)
    for i,c in enumerate(cs):
        f=f'{w}/products/white/{c}.jpg'
        if os.path.exists(f):
            im=Image.open(f);im.thumbnail((T-6,T-18));sh.paste(im,((i%cols)*T+3,(i//cols)*T+3))
        dr.text(((i%cols)*T+3,(i//cols)*T+T-13),c,fill='red')
    sh.save(f'{w}/sheets/s{k//per:02d}.jpg',quality=85)
print(len(codes)//per+1)
