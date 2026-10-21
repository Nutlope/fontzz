"""Compare families side by side: one row per family at a given weight."""
import sys
import uharfbuzz as hb
from PIL import Image, ImageDraw, ImageFont

FAMS = ["halden", "rondel", "tessera", "alder", "mallow", "strata", "plaza", "vesper", "ledger", "folio"]


def row(d, vf, text, w, size, y, x0=230):
    face = hb.Face(hb.Blob.from_file_path(vf))
    f = ImageFont.truetype(vf, size)
    f.set_variation_by_axes([w])
    font = hb.Font(face)
    font.set_variations({"wght": w})
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True})
    x = x0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        d.text((x, y), text[info.cluster], fill=0, font=f)
        x += pos.x_advance * size / face.upem


if __name__ == "__main__":
    out, w = sys.argv[1], int(sys.argv[2])
    text = sys.argv[3] if len(sys.argv) > 3 else "Hamburgefonstiv Rag 2049"
    fams = sys.argv[4].split(",") if len(sys.argv) > 4 else FAMS
    extra = sys.argv[5] if len(sys.argv) > 5 else None
    size = 84
    lh = int(size * 1.3)
    img = Image.new("L", (2600, 30 + lh * len(fams)), 255)
    d = ImageDraw.Draw(img)
    lab = ImageFont.load_default(size=26)
    for i, k in enumerate(fams):
        N = k[0].upper() + k[1:]
        vf = f"{extra or 'out'}/{k}/{N}[wght].ttf"
        d.text((20, 20 + i * lh + 30), N, fill=120, font=lab)
        row(d, vf, text, w, size, 20 + i * lh, 200)
    img.save(out)
