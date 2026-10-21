import sys
from PIL import Image, ImageDraw, ImageFont
vf, out, text = sys.argv[1], sys.argv[2], sys.argv[3]
ws = [int(x) for x in (sys.argv[4] if len(sys.argv)>4 else "100,400,900").split(",")]
size = int(sys.argv[5]) if len(sys.argv)>5 else 360
img = Image.new("L", (2400, len(ws)*int(size*1.3)+40), 255)
d = ImageDraw.Draw(img)
for i,w in enumerate(ws):
    f = ImageFont.truetype(vf, size); f.set_variation_by_axes([w])
    y = 20 + i*int(size*1.3)
    # guides
    asc = size*0.95
    for frac in (0, 0.54, 0.72):
        yy = y + asc - frac*size + size*0.0
        d.line([(0, yy), (2400, yy)], fill=210)
    d.text((40, y), text, fill=0, font=f)
img.save(out)
