"""Grid of every encoded glyph at one weight."""
import sys
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont
vf, out = sys.argv[1], sys.argv[2]
w = int(sys.argv[3]) if len(sys.argv) > 3 else 400
size = 64
cmap = TTFont(vf).getBestCmap()
chars = [chr(c) for c in sorted(cmap) if c > 32 and c != 0xA0]
cols = 28
cell = 84
rows = (len(chars) + cols - 1) // cols
img = Image.new("L", (cols * cell + 20, rows * cell + 20), 255)
d = ImageDraw.Draw(img)
f = ImageFont.truetype(vf, size)
f.set_variation_by_axes([w])
for i, ch in enumerate(chars):
    x = 10 + (i % cols) * cell
    y = 10 + (i // cols) * cell
    d.rectangle([x, y, x + cell - 2, y + cell - 2], outline=225)
    d.text((x + cell / 2, y + cell * 0.72), ch, font=f, fill=0, anchor="ms")
img.save(out)
print(len(chars), "glyphs")
