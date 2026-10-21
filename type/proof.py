"""Render proof sheets from a variable font, shaped with HarfBuzz (kerning applied)."""
import sys
import uharfbuzz as hb
from PIL import Image, ImageDraw, ImageFont


def shaper(vf):
    blob = hb.Blob.from_file_path(vf)
    face = hb.Face(blob)
    return face


def proof(vf, lines, out, size=110, weights=(100, 200, 300, 400, 500, 600, 700, 800, 900),
          width=2400, pad=30):
    face = shaper(vf)
    upm = face.upem
    rows = [(w, t) for w in weights for t in lines]
    lh = int(size * 1.25)
    img = Image.new("L", (width, pad * 2 + lh * len(rows)), 255)
    d = ImageDraw.Draw(img)
    small = ImageFont.load_default()
    for i, (w, text) in enumerate(rows):
        f = ImageFont.truetype(vf, size)
        f.set_variation_by_axes([w])
        font = hb.Font(face)
        font.set_variations({"wght": w})
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(font, buf, {"kern": True, "liga": False})
        y = pad + i * lh
        d.text((10, y + 4), str(w), fill=128, font=small)
        x = 70.0
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            ch = text[info.cluster]
            d.text((x + pos.x_offset * size / upm, y), ch, fill=0, font=f)
            x += pos.x_advance * size / upm
    img.save(out)


if __name__ == "__main__":
    vf, out = sys.argv[1], sys.argv[2]
    size = int(sys.argv[3]) if len(sys.argv) > 3 else 110
    lines = sys.argv[4:] or ["nohbdpqmucerijl"]
    proof(vf, lines, out, size)
