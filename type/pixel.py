"""Dot-matrix families: sample a finished family onto a square grid.

The pixel pattern is decided once, from the source font at one weight, so every
master has the same pixels and only their size changes: small separate dots at
Thin, square LEDs at Regular, fused blocks at Black.
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from core import Glyph, rect
from glyphs import REG, ORDER, COMP, CORDER

HERE = os.path.dirname(os.path.abspath(__file__))
_CACHE = {}


def source_font(spec):
    from fam import FAMILIES
    key = spec["pixel_src"]
    name = FAMILIES[key]["name"]
    path = os.path.join(HERE, "out", key, "%s[wght].ttf" % name)
    if not os.path.exists(path):
        raise SystemExit("build %s before %s" % (name, spec["name"]))
    return path


def pattern(spec):
    """{glyph name: (advance, [(col, row), ...])}, rows counted up from the baseline."""
    key = spec["name"]
    if key in _CACHE:
        return _CACHE[key]
    cell, thr = spec["cell"], spec["pixel_thr"]
    font = ImageFont.truetype(source_font(spec), 1000)
    font.set_variation_by_axes([spec["pixel_wght"]])
    ox, base = cell * (600 // cell), cell * (1200 // cell)   # origin on grid lines
    cols, rows = 2400 // cell, 1600 // cell
    out = {}
    names = [(n, REG[n][0]) for n in ORDER] + [(n, COMP[n][0]) for n in CORDER]
    for name, uni in names:
        if isinstance(uni, list):
            uni = uni[0]
        if uni is None:
            out[name] = (0, [])
            continue
        ch = chr(uni)
        adv = font.getlength(ch)
        img = Image.new("L", (cols * cell, rows * cell), 0)
        ImageDraw.Draw(img).text((ox, base), ch, font=font, fill=255, anchor="ls")
        a = np.asarray(img, dtype=np.float32) / 255.0
        on = best_offset(a, cell, rows, cols, thr)
        px = []
        c0, r0 = ox // cell, base // cell
        for r, c in zip(*np.nonzero(on)):
            px.append((int(c - c0), int(r0 - 1 - r)))
        if adv < 1:
            w = 0
        else:
            # one clear column each side so wide Black dots never touch the next letter
            if px:
                cs = [c for c, _ in px]
                lo, hi = min(cs), max(cs)
                px = [(c - lo + 1, r) for c, r in px]
                w = (hi - lo + 3) * cell
            else:
                w = max(1, round(adv / cell)) * cell
        out[name] = (w, px)
    _CACHE[key] = out
    return out


def best_offset(a, cell, rows, cols, thr):
    """Slide the grid sideways under the glyph and keep the position where strokes
    land on single columns (fewest solid 2x2 blocks), then the most ink."""
    best = None
    for dx in range(0, cell, 5):
        sh = np.roll(a, dx, axis=1)
        cov = sh.reshape(rows, cell, cols, cell).mean(axis=(1, 3))
        on = cov >= thr
        blocks = int((on[1:, 1:] & on[:-1, 1:] & on[1:, :-1] & on[:-1, :-1]).sum())
        score = (blocks, -int(on.sum()))
        if best is None or score < best[0]:
            best = (score, on)
    return best[1]


def make(spec, f):
    cell = spec["cell"]
    sw, sh = cell * f.dot_w, cell * f.dot
    px_, py_ = (cell - sw) / 2, (cell - sh) / 2
    gs = {}
    for name, (w, px) in pattern(spec).items():
        g = Glyph(name)
        for c, r in px:
            x, y = c * cell + px_, r * cell + py_
            g.add(rect(x, y, x + sw, y + sh))
        g.width = w
        g.uni = (REG.get(name) or COMP.get(name))[0]
        gs[name] = g
    return gs
