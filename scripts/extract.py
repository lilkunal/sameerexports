import pymupdf, sys
w = sys.argv[1]
src = sys.argv[2]
for tag, f in [('A', 'SE 1.pdf'), ('B', 'SE 2.pdf')]:
    d = pymupdf.open(f"{src}/{f}")
    for i, p in enumerate(d):
        x = d.extract_image(p.get_images(full=True)[0][0])
        open(f"{w}/raw/{tag}{i+1:02d}.{x['ext']}", 'wb').write(x['image'])
        if i < 2:
            print(tag, i + 1, x['width'], x['height'], x['ext'])
        p.get_pixmap(dpi=110).save(f"{w}/pages/{tag}{i+1:02d}.png")
