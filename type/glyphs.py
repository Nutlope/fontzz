"""Glyph registry and spacing helpers."""
from core import Glyph

REG = {}
ORDER = []


def glyph(name, uni=None):
    def deco(fn):
        REG[name] = (uni, fn)
        ORDER.append(name)
        return fn
    return deco


def sb(F, kind, uc=False):
    base = F.sbU if uc else F.sb
    if isinstance(kind, (int, float)):
        return kind
    if kind == "S":
        return base
    if kind == "O":
        return base * F.rr
    if kind == "D":
        return base * F.get("rd", 0.16)
    if kind == "N":   # near-zero, e.g. hooks
        return base * 0.1
    raise ValueError(kind)


def finish(g):
    b = g.bounds()
    if g.lsb is not None and b is not None:
        dx = g.lsb - b[0]
        if abs(dx) > 1e-9:
            g.apply(lambda p: (p[0] + dx, p[1]))
        b = g.bounds()
        g.width = b[2] + (g.rsb or 0)
    return g


def new(name, uni=None):
    return Glyph(name, uni)


COMP = {}
CORDER = []


def composite(name, uni=None):
    """Glyph built from finished glyphs: fn(F, gs) -> Glyph (absolute coords, width set)."""
    def deco(fn):
        COMP[name] = (uni, fn)
        CORDER.append(name)
        return fn
    return deco
