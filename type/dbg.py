"""Draw generator contours (pre-compile) for glyphs at masters: outlines + node dots."""
import sys
from PIL import Image, ImageDraw
from fam import FAMILIES, F
import build
from glyphs import REG, finish
COL = [(220,40,40),(30,120,220),(20,160,80),(200,120,0),(150,50,200),(0,160,160),(120,120,120)]
fam, names = sys.argv[1], sys.argv[2].split(",")
mis = [int(x) for x in (sys.argv[3] if len(sys.argv)>3 else "0,1,2").split(",")]
out = sys.argv[4] if len(sys.argv)>4 else "out/dbg.png"
sc = float(sys.argv[5]) if len(sys.argv)>5 else 0.42
cell = int(1100*sc)
img = Image.new("RGB", (cell*len(names)+40, cell*len(mis)+40), "white")
d = ImageDraw.Draw(img)
for r, mi in enumerate(mis):
    f, gs = build.make_glyphs(FAMILIES[fam], mi, names)
    for c, n in enumerate(names):
        g = gs[n]
        ox, oy = 20 + c*cell + 20, 20 + r*cell + int(820*sc)
        tr = lambda p: (ox + p[0]*sc, oy - p[1]*sc)
        for yy in (0, f.xh, f.cap, f.asc, f.desc):
            d.line([tr((-30,yy)), tr((g.width+30,yy))], fill=(225,225,225))
        d.line([tr((0,-250)),tr((0,900))], fill=(200,200,240)); d.line([tr((g.width,-250)),tr((g.width,900))], fill=(200,200,240))
        for i,(p,h) in enumerate(g.paths):
            pts = [tr(q) for q in p.flatten(20)]
            d.line(pts+[pts[0]], fill=COL[i%len(COL)], width=2)
            for q in p.points():
                x,y = tr(q); d.ellipse([x-2,y-2,x+2,y+2], fill=COL[i%len(COL)])
img.save(out)
