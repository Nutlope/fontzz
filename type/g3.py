"""Basic character set at three weights, stacked, for quick visual QA."""
import sys
from PIL import Image, ImageDraw, ImageFont
vf, out = sys.argv[1], sys.argv[2]
ws = [int(x) for x in (sys.argv[3] if len(sys.argv) > 3 else "100,400,900").split(",")]
chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789&@?!$%#ßæøéñ"
lines = chars.split(" ")
size, lh = 70, 92
img = Image.new("L", (2500, 20 + lh * len(lines) * len(ws)), 255)
d = ImageDraw.Draw(img)
y = 10
for w in ws:
    f = ImageFont.truetype(vf, size)
    f.set_variation_by_axes([w])
    for ln in lines:
        d.text((20, y), "  ".join(ln) if False else " ".join(ln), fill=0, font=f)
        y += lh
img.save(out)
