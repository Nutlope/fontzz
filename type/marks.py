"""Combining marks, accented composites and extra Latin letters."""
import math
from core import (Glyph, Path, rect, oval, H, V, D, lerp, T_rot180, T_translate, add, sub, mul,
                  norm, poly, cap_round)
from parts import (vstem, hstem, stroke, dot_shape, cut_line, arc_stroke, ring, is_round, dquad,
                   slant_w, vee)
from glyphs import glyph, composite, sb, new
import lc
import uc
import punct


def mark_base(F, case):
    if case:
        return F.cap + F.cap * F.get("mk_gap_uc", 0.075)
    return F.xh + F.xh * F.get("mk_gap", 0.14)


def mark_h(F, case):
    return (F.xh * F.get("mk_h", 0.20) + F.S * 0.42) * (0.82 if case else 1.0)


def mk_t(F):
    return F.S * F.get("mk_t", 0.88)


def mark(name, uni=None, case_variant=True):
    """Register a zero-width combining mark drawn around x=0 (and a .case variant)."""
    def deco(fn):
        def lc_fn(F):
            g = fn(F, False)
            g.name = name
            g.width = 0
            g.lsb = None
            return g
        glyph(name, uni)(lc_fn)
        if case_variant:
            def uc_fn(F):
                g = fn(F, True)
                g.name = name + ".case"
                g.width = 0
                g.lsb = None
                return g
            glyph(name + ".case", None)(uc_fn)
        return fn
    return deco


@mark("acutecomb", 0x301)
def m_acute(F, case):
    g = Glyph("a")
    y0 = mark_base(F, case)
    h = mark_h(F, case)
    t = mk_t(F) * (0.9, 0.9, 0.8)[F.mi]
    ang = math.radians(F.get("acute_ang", 42 if case else 48))
    d = (math.cos(ang), math.sin(ang))
    n = (-d[1] * t / 2, d[0] * t / 2)
    # endpoints chosen so the mark spans y0 .. y0 + h
    L = (F.xh * 0.25 + t * 0.75) * (0.86 if case else 1.0)
    h = d[1] * L + 2 * abs(n[1])
    c0 = (-d[0] * L / 2, y0 + abs(n[1]))
    c1 = (d[0] * L / 2, y0 + abs(n[1]) + d[1] * L)
    if is_round(F):
        g.add(stroke(F, c0, c1, t, True, True))
    else:
        g.add(Path(sub(c0, n)).L(sub(c1, n)).L(add(c1, n)).L(add(c0, n)))
    return g


@mark("gravecomb", 0x300)
def m_grave(F, case):
    g = m_acute(F, case)
    g.mirror_x(0)
    return g


@mark("hungarumlautcomb", 0x30B)
def m_hung(F, case):
    g = Glyph("h")
    a = m_acute(F, case)
    w = mark_h(F, case) * 0.62
    for p, hh in a.paths:
        g.add(p.map(lambda q: (q[0] - w, q[1])))
        g.add(p.map(lambda q: (q[0] + w, q[1])))
    return g


@mark("circumflexcomb", 0x302)
def m_circ(F, case):
    g = Glyph("c")
    y0 = mark_base(F, case)
    h = mark_h(F, case) * 0.92
    t = mk_t(F) * (0.92, 0.9, 0.8)[F.mi]
    W = h * 1.9 + t * 0.6
    for p in vee(F, -W / 2, W, y0, y0 + h, t, apex=t * 1.0):
        g.add(p)
    return g


@mark("caroncomb", 0x30C)
def m_caron(F, case):
    g = Glyph("c")
    y0 = mark_base(F, case)
    h = mark_h(F, case) * 0.92
    t = mk_t(F) * (0.92, 0.9, 0.8)[F.mi]
    W = h * 1.9 + t * 0.6
    for p in vee(F, -W / 2, W, y0 + h, y0, t, apex=t * 1.0):
        g.add(p)
    return g


@mark("dieresiscomb", 0x308)
def m_dier(F, case):
    g = Glyph("d")
    w = F.dotw * F.get("mk_dot", 0.92)
    y0 = mark_base(F, case) + w / 2 - (4 if case else 0)
    gap = w * 0.5 + F.n_c * 0.13
    g.add(dot_shape(F, -gap - w / 2 + w / 2 - 0, y0, w).map(lambda q: (q[0] - w / 2 + 0, q[1])) if False else
          dot_shape(F, -(gap / 2 + w / 2), y0, w))
    g.add(dot_shape(F, (gap / 2 + w / 2), y0, w))
    return g


@mark("dotaccentcomb", 0x307)
def m_dot(F, case):
    g = Glyph("d")
    w = F.dotw * F.get("mk_dot", 0.92)
    g.add(dot_shape(F, 0, mark_base(F, case) + w / 2, w))
    return g


@mark("macroncomb", 0x304)
def m_macron(F, case):
    g = Glyph("m")
    t = mk_t(F) * 0.9
    W = mark_h(F, False) * 1.9
    y0 = mark_base(F, case) + (0 if case else mark_h(F, case) * 0.25)
    g.add(hstem(F, -W / 2, W / 2, y0, y0 + t, True, True))
    return g


@mark("brevecomb", 0x306)
def m_breve(F, case):
    g = Glyph("b")
    t = mk_t(F) * 0.9
    h = mark_h(F, case) * 0.95
    rx = h * 0.9 + t * 0.4
    ry = h * 0.8 + t * 0.3
    y0 = mark_base(F, case)
    o, i = ring(F, 0, y0 + ry, rx, ry, rx - t, ry - t * 0.92)
    g.add(arc_stroke(F, o, i, (2, 0.0, None), (3, 1.0, None), True, True))
    return g


@mark("ringcomb", 0x30A)
def m_ring(F, case):
    g = Glyph("r")
    t = mk_t(F) * 0.8
    r = mark_h(F, case) * 0.62 + t * 0.3
    y0 = mark_base(F, case) + r - (6 if case else 0)
    g.add(oval(0, y0, r, r, 0.5523 if F.k < 0.62 else F.k))
    g.hole(oval(0, y0, r - t, r - t, 0.5523 if F.k < 0.62 else F.k))
    return g


@mark("tildecomb", 0x303)
def m_tilde(F, case):
    g = Glyph("t")
    t = mk_t(F) * 0.88
    W = mark_h(F, False) * 2.1
    h = mark_h(F, case) * 0.55
    y = mark_base(F, case) + h * 0.5
    p = Path((-W / 2, y - h / 2))
    p.T((-W * 0.2, y + h / 2), (1, 1.4), H, 0.62).T((W * 0.2, y - h / 2), H, H, 0.6)
    p.T((W / 2, y + h / 2), H, (1, 1.4), 0.62).L((W / 2, y + h / 2 + t))
    p.T((W * 0.2, y - h / 2 + t), (1, 1.4), H, 0.62).T((-W * 0.2, y + h / 2 + t), H, H, 0.6)
    p.T((-W / 2, y - h / 2 + t), H, (1, 1.4), 0.62)
    g.add(p)
    return g


@mark("cedillacomb", 0x327, case_variant=False)
def m_cedilla(F, case):
    g = Glyph("c")
    t = mk_t(F) * 0.85
    T = t * 0.92
    rx = F.xh * 0.10 + t * 1.05
    ry = F.xh * 0.08 + T * 1.05
    cx, cy = rx * 0.2, -ry - F.xh * 0.02
    o, i = ring(F, cx, cy, rx, ry, rx - t, ry - T)
    pa, da = cut_line(F, cx, cy, rx - t / 2, ry - T / 2, 90, "vertical")
    g.add(arc_stroke(F, o, i, (3, 0.0, None), (1, 0.15, None), False, True))
    g.add(rect(-t * 0.5 + cx * 0.0, cy + ry - T * 0.5, t * 0.5, 4))
    return g


@mark("ogonekcomb", 0x328, case_variant=False)
def m_ogonek(F, case):
    g = Glyph("o")
    t = mk_t(F) * 0.9
    T = t * 0.9
    rx = F.xh * 0.09 + t * 1.1
    ry = F.xh * 0.11 + T * 1.05
    cx, cy = 0, 2 - ry * 0.9
    o, i = ring(F, cx, cy, rx, ry, rx - t, ry - T)
    pe, de = cut_line(F, cx, cy, rx - t / 2, ry - T / 2, -40, "radial" if is_round(F) else F.get("hook_term", F.term), inner=(rx - t, ry - T))
    g.add(arc_stroke(F, o, i, (1, 0.35, None), (3, pe, de), False, True))
    return g


# ---------------------------------------------------------------- composites

def center(g):
    b = g.bounds()
    return (b[0] + b[2]) / 2


def top_x(gs, base):
    g = gs[base]
    if "top" in g.anchors:
        return g.anchors["top"][0]
    return center(g)


ACC = {
    "grave": "gravecomb", "acute": "acutecomb", "circumflex": "circumflexcomb",
    "tilde": "tildecomb", "dieresis": "dieresiscomb", "ring": "ringcomb", "caron": "caroncomb",
    "macron": "macroncomb", "breve": "brevecomb", "dotaccent": "dotaccentcomb",
    "hungarumlaut": "hungarumlautcomb", "cedilla": "cedillacomb", "ogonek": "ogonekcomb",
}

ACCENTED = [
    # name, base, accent, unicode
    ("Agrave", "A", "grave", 0xC0), ("Aacute", "A", "acute", 0xC1), ("Acircumflex", "A", "circumflex", 0xC2),
    ("Atilde", "A", "tilde", 0xC3), ("Adieresis", "A", "dieresis", 0xC4), ("Aring", "A", "ring", 0xC5),
    ("Ccedilla", "C", "cedilla", 0xC7), ("Egrave", "E", "grave", 0xC8), ("Eacute", "E", "acute", 0xC9),
    ("Ecircumflex", "E", "circumflex", 0xCA), ("Edieresis", "E", "dieresis", 0xCB),
    ("Igrave", "I", "grave", 0xCC), ("Iacute", "I", "acute", 0xCD), ("Icircumflex", "I", "circumflex", 0xCE),
    ("Idieresis", "I", "dieresis", 0xCF), ("Ntilde", "N", "tilde", 0xD1), ("Ograve", "O", "grave", 0xD2),
    ("Oacute", "O", "acute", 0xD3), ("Ocircumflex", "O", "circumflex", 0xD4), ("Otilde", "O", "tilde", 0xD5),
    ("Odieresis", "O", "dieresis", 0xD6), ("Ugrave", "U", "grave", 0xD9), ("Uacute", "U", "acute", 0xDA),
    ("Ucircumflex", "U", "circumflex", 0xDB), ("Udieresis", "U", "dieresis", 0xDC),
    ("Yacute", "Y", "acute", 0xDD), ("Ydieresis", "Y", "dieresis", 0x178),
    ("agrave", "a", "grave", 0xE0), ("aacute", "a", "acute", 0xE1), ("acircumflex", "a", "circumflex", 0xE2),
    ("atilde", "a", "tilde", 0xE3), ("adieresis", "a", "dieresis", 0xE4), ("aring", "a", "ring", 0xE5),
    ("ccedilla", "c", "cedilla", 0xE7), ("egrave", "e", "grave", 0xE8), ("eacute", "e", "acute", 0xE9),
    ("ecircumflex", "e", "circumflex", 0xEA), ("edieresis", "e", "dieresis", 0xEB),
    ("igrave", "dotlessi", "grave", 0xEC), ("iacute", "dotlessi", "acute", 0xED),
    ("icircumflex", "dotlessi", "circumflex", 0xEE), ("idieresis", "dotlessi", "dieresis", 0xEF),
    ("ntilde", "n", "tilde", 0xF1), ("ograve", "o", "grave", 0xF2), ("oacute", "o", "acute", 0xF3),
    ("ocircumflex", "o", "circumflex", 0xF4), ("otilde", "o", "tilde", 0xF5), ("odieresis", "o", "dieresis", 0xF6),
    ("ugrave", "u", "grave", 0xF9), ("uacute", "u", "acute", 0xFA), ("ucircumflex", "u", "circumflex", 0xFB),
    ("udieresis", "u", "dieresis", 0xFC), ("yacute", "y", "acute", 0xFD), ("ydieresis", "y", "dieresis", 0xFF),
    # Latin Extended-A selection
    ("Amacron", "A", "macron", 0x100), ("amacron", "a", "macron", 0x101),
    ("Abreve", "A", "breve", 0x102), ("abreve", "a", "breve", 0x103),
    ("Aogonek", "A", "ogonek", 0x104), ("aogonek", "a", "ogonek", 0x105),
    ("Cacute", "C", "acute", 0x106), ("cacute", "c", "acute", 0x107),
    ("Ccaron", "C", "caron", 0x10C), ("ccaron", "c", "caron", 0x10D),
    ("Dcaron", "D", "caron", 0x10E),
    ("Emacron", "E", "macron", 0x112), ("emacron", "e", "macron", 0x113),
    ("Edotaccent", "E", "dotaccent", 0x116), ("edotaccent", "e", "dotaccent", 0x117),
    ("Eogonek", "E", "ogonek", 0x118), ("eogonek", "e", "ogonek", 0x119),
    ("Ecaron", "E", "caron", 0x11A), ("ecaron", "e", "caron", 0x11B),
    ("Gbreve", "G", "breve", 0x11E), ("gbreve", "g", "breve", 0x11F),
    ("Imacron", "I", "macron", 0x12A), ("imacron", "dotlessi", "macron", 0x12B),
    ("Idotaccent", "I", "dotaccent", 0x130),
    ("Nacute", "N", "acute", 0x143), ("nacute", "n", "acute", 0x144),
    ("Ncaron", "N", "caron", 0x147), ("ncaron", "n", "caron", 0x148),
    ("Omacron", "O", "macron", 0x14C), ("omacron", "o", "macron", 0x14D),
    ("Ohungarumlaut", "O", "hungarumlaut", 0x150), ("ohungarumlaut", "o", "hungarumlaut", 0x151),
    ("Racute", "R", "acute", 0x154), ("racute", "r", "acute", 0x155),
    ("Rcaron", "R", "caron", 0x158), ("rcaron", "r", "caron", 0x159),
    ("Sacute", "S", "acute", 0x15A), ("sacute", "s", "acute", 0x15B),
    ("Scedilla", "S", "cedilla", 0x15E), ("scedilla", "s", "cedilla", 0x15F),
    ("Scaron", "S", "caron", 0x160), ("scaron", "s", "caron", 0x161),
    ("Tcaron", "T", "caron", 0x164),
    ("Umacron", "U", "macron", 0x16A), ("umacron", "u", "macron", 0x16B),
    ("Uring", "U", "ring", 0x16E), ("uring", "u", "ring", 0x16F),
    ("Uhungarumlaut", "U", "hungarumlaut", 0x170), ("uhungarumlaut", "u", "hungarumlaut", 0x171),
    ("Zacute", "Z", "acute", 0x179), ("zacute", "z", "acute", 0x17A),
    ("Zdotaccent", "Z", "dotaccent", 0x17B), ("zdotaccent", "z", "dotaccent", 0x17C),
    ("Zcaron", "Z", "caron", 0x17D), ("zcaron", "z", "caron", 0x17E),
]


def make_accented(name, base, acc, uni):
    def fn(F, gs):
        b = gs[base]
        g = Glyph(name)
        g.comps.append((base, 0, 0))
        g.width = b.width
        case = base[0].isupper()
        mname = ACC[acc]
        bb = b.bounds()
        if acc in ("cedilla",):
            x = (bb[0] + bb[2]) / 2
            if base in ("S", "s"):
                x += (bb[2] - bb[0]) * 0.02
            g.comps.append((mname, x, 0))
        elif acc == "ogonek":
            x = bb[2] - (bb[2] - bb[0]) * (0.18 if base in ("A",) else 0.22)
            if base == "a":
                x = bb[2] - F.S * 0.5
            if base == "e":
                x = (bb[0] + bb[2]) / 2 + (bb[2] - bb[0]) * 0.18
            if base == "E":
                x = bb[2] - (bb[2] - bb[0]) * 0.28
            g.comps.append((mname, x, 0))
        else:
            x = top_x(gs, base)
            if base == "a" and F.a_story == 2:
                x = (bb[0] + bb[2]) / 2 + F.S * 0.12
            g.comps.append((mname + (".case" if case else ""), x, 0))
        return g
    composite(name, uni)(fn)


for (n, b, a, u) in ACCENTED:
    make_accented(n, b, a, u)


# caron alternates that use an apostrophe-like mark
def apos_caron(name, base, uni):
    def fn(F, gs):
        b = gs[base]
        g = Glyph(name)
        g.comps.append((base, 0, 0))
        bb = b.bounds()
        q = gs["quoteright"]
        qb = q.bounds()
        x = bb[2] + F.S * 0.35 - qb[0]
        y = (F.asc if base in ("d", "l", "t") else F.cap) - qb[3]
        if base == "t":
            y = F.t_top + F.S * 0.1 - qb[3]
        g.comps.append(("quoteright", x, y))
        g.width = max(b.width, bb[2] + F.S * 0.35 + (qb[2] - qb[0]) + sb(F, "S") * 0.6)
        return g
    composite(name, uni)(fn)


apos_caron("dcaron", "d", 0x10F)
apos_caron("tcaron", "t", 0x165)
apos_caron("lcaron", "l", 0x13E)
apos_caron("Lcaron", "L", 0x13D)


# spacing accents
SPACING = [("grave", "gravecomb", 0x60), ("acute", "acutecomb", 0xB4), ("dieresis", "dieresiscomb", 0xA8),
           ("macron", "macroncomb", 0xAF), ("cedilla", "cedillacomb", 0xB8),
           ("circumflex", "circumflexcomb", 0x2C6), ("caron", "caroncomb", 0x2C7),
           ("breve", "brevecomb", 0x2D8), ("dotaccent", "dotaccentcomb", 0x2D9),
           ("ring", "ringcomb", 0x2DA), ("ogonek", "ogonekcomb", 0x2DB), ("tilde", "tildecomb", 0x2DC),
           ("hungarumlaut", "hungarumlautcomb", 0x2DD)]


def make_spacing(name, mname, uni):
    def fn(F, gs):
        m = gs[mname]
        b = m.bounds()
        w = b[2] - b[0]
        side = sb(F, "S") * 0.8
        g = Glyph(name)
        g.comps.append((mname, side - b[0], 0))
        g.width = w + 2 * side
        return g
    composite(name, uni)(fn)


for (n, m, u) in SPACING:
    make_spacing(n, m, u)


@composite("nbspace", 0xA0)
def c_nbspace(F, gs):
    g = Glyph("nbspace")
    g.width = round(F.get("space_w", 0.5 * (2 * F.S + F.n_c) + F.sb * 0.9))
    return g


# ---------------------------------------------------------------- drawn extras

@glyph("Oslash", 0xD8)
def g_Oslash(F):
    g = uc.g_O(F)
    g.name = "Oslash"
    W = uc.O_w(F)
    t = F.SU * 0.82
    a = (W * 0.06, -F.cap * 0.05)
    b = (W * 0.94, F.cap * 1.05)
    if is_round(F):
        g.add(stroke(F, a, b, t, True, True))
    else:
        w = slant_w(t, b[0] - a[0], b[1] - a[1])
        g.add(dquad(a, b, w))
    return g


@glyph("oslash", 0xF8)
def g_oslash(F):
    g = lc.g_o(F)
    g.name = "oslash"
    W = lc.o_w(F)
    t = F.S * 0.82
    a = (W * 0.04, -F.xh * 0.06)
    b = (W * 0.96, F.xh * 1.06)
    if is_round(F):
        g.add(stroke(F, a, b, t, True, True))
    else:
        w = slant_w(t, b[0] - a[0], b[1] - a[1])
        g.add(dquad(a, b, w))
    return g


def slash_bar(F, x, y, w, t):
    """Short diagonal bar centred at (x, y) for l/L slash."""
    h = w * 0.62
    if is_round(F):
        return stroke(F, (x - w / 2, y - h / 2), (x + w / 2, y + h / 2), t, True, True)
    ww = slant_w(t, w, h)
    return dquad((x - w / 2 + ww / 2, y - h / 2), (x + w / 2 - ww / 2, y + h / 2), ww)


@glyph("lslash", 0x142)
def g_lslash(F):
    g = lc.g_l(F)
    g.name = "lslash"
    S = F.S
    w = S + F.n_c * 0.5
    g.add(slash_bar(F, S / 2, F.xh * 0.62, w, F.T * 0.9))
    g.lsb = g.rsb = sb(F, "S") * 0.5
    return g


@glyph("Lslash", 0x141)
def g_Lslash(F):
    g = uc.g_L(F)
    g.name = "Lslash"
    S = F.SU
    w = S + F.H_c * 0.36
    g.add(slash_bar(F, S / 2, F.cap * 0.46, w, F.TU * 0.9))
    g.lsb = sb(F, "S", True) * 0.5
    return g


@glyph("Eth", 0xD0)
def g_Eth(F):
    g = uc.g_D(F)
    g.name = "Eth"
    S, T = F.SU, F.TU
    g.add(hstem(F, -S * 0.75, S + F.H_c * 0.22, F.cap / 2 - T / 2, F.cap / 2 + T / 2, True, True))
    g.lsb = sb(F, "S", True) * 0.4
    return g


@glyph("Dcroat", 0x110)
def g_Dcroat(F):
    g = g_Eth(F)
    g.name = "Dcroat"
    return g


@glyph("dcroat", 0x111)
def g_dcroat(F):
    g = lc.g_d(F)
    g.name = "dcroat"
    S, T = F.S, F.T
    b = g.bounds()
    x1 = b[2]
    yb = F.asc - (F.asc - F.xh) * 0.42
    g.add(hstem(F, x1 - S - F.n_c * 0.36, x1 + S * 0.55, yb - T * 0.45, yb + T * 0.45, True, True))
    g.lsb, g.rsb = sb(F, "O"), sb(F, "S") * 0.3
    return g


@glyph("Thorn", 0xDE)
def g_Thorn(F):
    g = new("Thorn")
    S, T, cap = F.SU, F.TU, F.cap
    W = uc.cw(F, F.P_w)
    g.add(vstem(F, 0, S, 0, cap, True, True))
    o, i = uc.dbowl(F, S * 0.5, W, cap * 0.19, cap * 0.81, S, T, rxr=F.P_rx)
    g.add(o)
    g.hole(i)
    g.lsb, g.rsb = sb(F, "S", True), sb(F, "O", True)
    return g


@glyph("thorn", 0xFE)
def g_thorn(F):
    g = lc.b_shape(F, False)
    g.name = "thorn"
    g.add(vstem(F, 0, F.S, F.xh - 2, F.asc, False, True))
    g.lsb, g.rsb = sb(F, "S"), sb(F, "O")
    return g


@glyph("eth", 0xF0)
def g_eth(F):
    g = new("eth")
    S, T, xh, o = F.S, F.T, F.xh, F.o
    W = lc.o_w(F)
    # bowl
    h = xh * F.get("eth_h", 1.06)
    cx, cy = W / 2, h / 2
    g.add(oval(cx, cy, W / 2, h / 2 + o, F.k))
    g.hole(oval(cx, cy, W / 2 - S * 1.02, h / 2 + o - T, F.ki))
    # rising stroke from the right of the bowl curving left to the top
    rx = W * 0.62
    ry = F.asc - cy + o
    ccx, ccy = W - rx, cy
    oo, ii = ring(F, ccx, ccy, rx, ry, rx - S, ry - T * 0.9)
    pe, de = cut_line(F, ccx, ccy, rx - S / 2, ry - T / 2, 118, "radial" if is_round(F) else F.get("hook_term", F.term), inner=(rx - S, ry - T * 0.9))
    g.add(arc_stroke(F, oo, ii, (0, 0.0, None), (1, pe, de), False, True))
    # cross stroke
    g.add(slash_bar(F, W * 0.56, F.asc - (F.asc - xh) * 0.55, W * 0.5, T * 0.85))
    g.lsb = g.rsb = sb(F, "O")
    return g


@glyph("germandbls", 0xDF)
def g_germandbls(F):
    g = new("germandbls")
    S, T, xh, o = F.S, F.T, F.xh, F.o
    top = F.asc + o
    W = lc.n_w(F) * F.get("ss_w", 0.98)
    g.add(vstem(F, 0, S, 0, F.asc * 0.82, True, False))
    # upper bowl: from the stem up over the top and down to the middle
    ry1 = (top - xh * 0.60) / 2
    rx1 = (W * 0.90) / 2
    cx1, cy1 = rx1, top - ry1
    o1, i1 = ring(F, cx1, cy1, rx1, ry1, rx1 - S, ry1 - T)
    g.add(arc_stroke(F, o1, i1, (3, 0.0, None), (1, 1.0, None), False, False))
    g.add(rect(0, F.asc * 0.5, S, cy1 + 1))
    # lower bowl from the middle around to the bottom
    ym = cy1 - ry1  # bottom of upper bowl (outer)
    ry2 = (ym + T + o) / 2
    rx2 = W / 2 * 0.98
    cx2, cy2 = W - rx2, ym + T - ry2
    o2, i2 = ring(F, cx2, cy2, rx2, ry2, rx2 - S, ry2 - T)
    p2, d2 = cut_line(F, cx2, cy2, rx2 - S / 2, ry2 - T / 2, -128, F.get("hook_term", F.term) if not is_round(F) else "round", inner=(rx2 - S, ry2 - T))
    g.add(arc_stroke(F, o2, i2, (2, p2, d2), (0, 1.0, None), True, False))
    g.add(hstem(F, S * 0.5, min(cx1, cx2) + 1, ym, ym + T, False, False))
    g.lsb, g.rsb = sb(F, "S"), sb(F, "O")
    return g


def ligature_pair(name, uni, left, right, overlap_fn):
    def fn(F, gs):
        a, b = gs[left], gs[right]
        ab = a.bounds()
        bb = b.bounds()
        ov = overlap_fn(F)
        dx = ab[2] - ov - bb[0]
        g = Glyph(name)
        g.comps.append((left, 0, 0))
        g.comps.append((right, dx, 0))
        g.width = dx + b.width
        return g
    composite(name, uni)(fn)


ligature_pair("ae", 0xE6, "a", "e", lambda F: F.S * 1.05)
ligature_pair("oe", 0x153, "o", "e", lambda F: F.S * 1.02)


@glyph("AE", 0xC6)
def g_AE(F):
    g = new("AE")
    S, T, cap = F.SU, F.TU, F.cap
    xE = uc.cw(F, 0.62)
    W = xE + uc.cw(F, F.E_w) * 0.80
    t = uc.cdiag(F)
    wx = slant_w(t, xE, cap)
    g.add(Path((0, 0)).L((wx, 0)).L((xE + S * 0.5, cap)).L((xE + S * 0.5 - wx, cap)))
    g.add(hstem(F, xE - wx * 0.5, W, cap - T, cap, False, True))
    yb = cap * 0.5 - T / 2 + 6
    g.add(hstem(F, xE, W * 0.97, yb, yb + T, False, True))
    g.add(hstem(F, xE, W, 0, T, False, True))
    g.add(vstem(F, xE, xE + S, 0, cap, False, False))
    ya = cap * F.A_bar
    xl = wx / 2 + xE * (ya + T / 2) / cap
    g.add(rect(xl, ya, xE + S * 0.5, ya + T * 0.95))
    g.lsb, g.rsb = sb(F, "D", True), sb(F, "D", True) * 2.4
    return g


@glyph("OE", 0x152)
def g_OE(F):
    g = new("OE")
    S, T, cap = F.SU, F.TU, F.cap
    Wo = uc.O_w(F)
    cx, cy, rxo, ryo, rxi, ryi = uc.cap_ring(F, Wo)
    o, i = ring(F, cx, cy, rxo, ryo, rxi, ryi, F.kU, F.kiU)
    g.add(arc_stroke(F, o, i, (1, 0.0, None), (2, 1.0, None), False, False))
    xs = cx - S * 0.1
    W = xs + uc.cw(F, F.E_w) * 0.78
    g.add(vstem(F, xs, xs + S, -F.oc * 0.0, cap, False, False))
    g.add(hstem(F, cx, W, cap - T, cap, False, True))
    yb = cap * 0.5 - T / 2 + 6
    g.add(hstem(F, xs + S * 0.5, W * 0.97, yb, yb + T, False, True))
    g.add(hstem(F, cx, W, 0, T, False, True))
    # flat top/bottom meet the arc's extremes
    g.add(rect(cx - 1, cap - T, xs + S, cap))
    g.add(rect(cx - 1, 0, xs + S, T))
    g.lsb, g.rsb = sb(F, "O", True), sb(F, "D", True) * 2.4
    return g


# ---------------------------------------------------------------- currency & misc

@glyph("dollar", 0x24)
def g_dollar(F):
    g = uc.g_S(F)
    g.name = "dollar"
    b = g.bounds()
    cx = (b[0] + b[2]) / 2
    t = F.SU * 0.62
    g.add(vstem(F, cx - t / 2, cx + t / 2, -F.cap * 0.11, F.cap * 1.11, True, True))
    return g


@glyph("cent", 0xA2)
def g_cent(F):
    g = lc.g_c(F)
    g.name = "cent"
    b = g.bounds()
    cx = (b[0] + b[2]) / 2 + (b[2] - b[0]) * 0.04
    t = F.S * 0.62
    g.add(vstem(F, cx - t / 2, cx + t / 2, -F.xh * 0.18, F.xh * 1.18, True, True))
    return g


@glyph("Euro", 0x20AC)
def g_euro(F):
    g = uc.g_C(F)
    g.name = "Euro"
    b = g.bounds()
    W = b[2] - b[0]
    T = F.TU * 0.88
    for y in (F.cap * 0.58, F.cap * 0.40):
        g.add(hstem(F, b[0] - W * 0.12, b[0] + W * 0.62, y - T / 2, y + T / 2, True, True))
    g.lsb = sb(F, "D", True)
    return g


@glyph("yen", 0xA5)
def g_yen(F):
    g = uc.g_Y(F)
    g.name = "yen"
    b = g.bounds()
    W = b[2] - b[0]
    T = F.TU * 0.88
    for y in (F.cap * 0.33, F.cap * 0.14):
        g.add(hstem(F, b[0] + W * 0.2, b[2] - W * 0.2, y - T / 2, y + T / 2, True, True))
    return g


@glyph("sterling", 0xA3)
def g_sterling(F):
    g = new("sterling")
    S, T, cap, o = F.SU * 0.96, F.TU, F.cap, F.oc
    W = uc.cw(F, 0.88)
    rx = W * 0.36
    ry = cap * 0.30
    xs = W * 0.22
    cx, cy = xs + rx, cap + o - ry
    oo, ii = ring(F, cx, cy, rx, ry, rx - S, ry - T, F.kU, F.kiU)
    p0, d0 = cut_line(F, cx, cy, rx - S / 2, ry - T / 2, 20, inner=(rx - S, ry - T))
    g.add(arc_stroke(F, oo, ii, (0, p0, d0), (1, 1.0, None), True, False))
    g.add(vstem(F, xs, xs + S, T * 0.5, cy, False, False))
    g.add(hstem(F, 0, W, 0, T, True, True))
    g.add(hstem(F, xs - W * 0.18, xs + S + W * 0.28, cap * 0.42 - T / 2, cap * 0.42 + T / 2, True, True))
    g.lsb, g.rsb = sb(F, "D", True), sb(F, "D", True)
    return g


def circled(name, uni, inner_name, scale):
    def fn(F, gs):
        g = Glyph(name)
        R = F.cap * F.get("circ_r", 0.52)
        t = F.SU * 0.52
        cy = F.cap / 2
        side = sb(F, "O", True)
        cx = side + R
        g.add(oval(cx, cy, R, R, 0.5523 if F.kU < 0.62 else F.kU))
        g.hole(oval(cx, cy, R - t, R - t, 0.5523 if F.kU < 0.62 else F.kU))
        ig = gs[inner_name]
        ib = ig.bounds()
        icx = (ib[0] + ib[2]) / 2 * scale
        icy = (ib[1] + ib[3]) / 2 * scale
        g.comps.append((inner_name, cx - icx, cy - icy, scale))
        g.width = 2 * side + 2 * R
        return g
    composite(name, uni)(fn)


circled("copyright", 0xA9, "C", 0.56)
circled("registered", 0xAE, "R", 0.56)


@composite("trademark", 0x2122)
def c_tm(F, gs):
    g = Glyph("trademark")
    s = 0.46
    T, M = gs["T"], gs["M"]
    tb, mb = T.bounds(), M.bounds()
    y = F.cap - F.cap * s
    x0 = sb(F, "D", True) - tb[0] * s
    g.comps.append(("T", x0, y, s))
    x1 = x0 + tb[2] * s + F.SU * 0.25 - mb[0] * s
    g.comps.append(("M", x1, y, s))
    g.width = x1 + mb[2] * s + sb(F, "D", True)
    return g


@glyph("section", 0xA7)
def g_section(F):
    g = new("section")
    W = lc.n_w(F) * 0.9
    S, T = F.SU * 0.9, F.TU * 0.88
    h = F.cap * 0.62
    s1 = lc.s_shape(F, W, h, F.oc, S, T, F.s_tth, F.s_bth)
    g.add(s1.map(lambda q: (q[0], q[1] + F.cap * 0.40)))
    g.add(s1.map(lambda q: (q[0], q[1] - F.cap * 0.02)))
    g.lsb = g.rsb = sb(F, "O")
    return g
