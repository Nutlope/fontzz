"""Punctuation and symbols (drawn)."""
import math
from core import (Glyph, Path, rect, oval, quad_cubics, H, V, D, lerp, T_rot180, T_translate, add,
                  sub, mul, norm, poly, cap_round, split, bez, T_rotate)
from parts import (vstem, hstem, stroke, dot_shape, cut_line, arc_stroke, ring, is_round, dquad,
                   slant_w, hook_ring)
from glyphs import glyph, sb, new
import lc
import uc
import figs


def dw(F):
    return F.get("pdot", F.dotw * 1.0)


def ym(F):
    """Math axis."""
    return F.get("math_y", F.cap * 0.42)


def sbP(F, k=1.0):
    return sb(F, "S") * k


def comma_shape(F, x0, y0, flip=False):
    """Comma whose dot sits with its bottom-left at (x0, y0)."""
    w = dw(F)
    tail = w * F.get("comma_tail", 1.05)
    out = []
    if is_round(F) or F.dot == "round":
        r = w / 2
        out.append(oval(x0 + r, y0 + r, r, r, 0.5523))
        t = w * 0.62
        out.append(stroke(F, (x0 + r + r * 0.35, y0 + r * 0.6), (x0 + r * 0.35, y0 - tail + t * 0.5),
                          t, False, True) if is_round(F) else
                   Path((x0 + r * 0.25, y0 + r)).L((x0 + w, y0 + r)).L((x0 + w * 0.98, y0 + r * 0.6))
                   .L((x0 + w * 0.42, y0 - tail)).L((x0 + w * 0.08, y0 - tail)).L((x0 + w * 0.42, y0 + r * 0.3)))
    else:
        out.append(rect(x0, y0, x0 + w, y0 + w))
        out.append(poly((x0 + w * 0.35, y0 + w * 0.5), (x0 + w, y0 + w * 0.5), (x0 + w, y0),
                        (x0 + w * 0.50, y0 - tail), (x0 + w * 0.05, y0 - tail), (x0 + w * 0.35, y0)))
    if flip:
        c = (x0 + w / 2, y0 + w / 2)
        out = [p.map(T_rot180(*c)) for p in out]
    return out


@glyph("period", 0x2E)
def g_period(F):
    g = new("period")
    w = dw(F)
    g.add(dot_shape(F, w / 2, w / 2, w))
    g.lsb = g.rsb = sbP(F, F.get("p_sb", 1.0))
    return g


@glyph("comma", 0x2C)
def g_comma(F):
    g = new("comma")
    g.add(comma_shape(F, 0, 0))
    g.lsb = g.rsb = sbP(F, F.get("p_sb", 1.0))
    return g


@glyph("colon", 0x3A)
def g_colon(F):
    g = g_period(F)
    g.name = "colon"
    w = dw(F)
    g.add(dot_shape(F, w / 2, F.xh - w / 2, w))
    return g


@glyph("semicolon", 0x3B)
def g_semicolon(F):
    g = g_comma(F)
    g.name = "semicolon"
    w = dw(F)
    g.add(dot_shape(F, w / 2, F.xh - w / 2, w))
    return g


@glyph("ellipsis", 0x2026)
def g_ellipsis(F):
    g = new("ellipsis")
    w = dw(F)
    gap = w + sbP(F) * 1.6
    for i in range(3):
        g.add(dot_shape(F, w / 2 + i * gap, w / 2, w))
    g.lsb = g.rsb = sbP(F)
    return g


@glyph("periodcentered", 0xB7)
def g_periodcentered(F):
    g = new("periodcentered")
    w = dw(F)
    g.add(dot_shape(F, w / 2, ym(F), w))
    g.lsb = g.rsb = sbP(F)
    return g


@glyph("bullet", 0x2022)
def g_bullet(F):
    g = new("bullet")
    w = dw(F) * 1.5
    g.add(oval(w / 2, ym(F), w / 2, w / 2, 0.5523) if F.dot != "square" else
          rect(0, ym(F) - w / 2, w, ym(F) + w / 2))
    g.lsb = g.rsb = sbP(F) * 1.2
    return g


@glyph("exclam", 0x21)
def g_exclam(F):
    g = new("exclam")
    w = dw(F)
    S = F.SU * F.get("excl_s", 0.92)
    cx = w / 2
    top = F.cap
    bot = w + F.cap * F.get("excl_gap", 0.13)
    if is_round(F):
        g.add(vstem(F, cx - S / 2, cx + S / 2, bot, top, True, True))
    else:
        tb = S * F.get("excl_taper", 0.86)
        g.add(poly((cx - tb / 2, bot), (cx + tb / 2, bot), (cx + S / 2, top), (cx - S / 2, top)))
    g.add(dot_shape(F, cx, w / 2, w))
    g.lsb = g.rsb = sbP(F)
    return g


@glyph("exclamdown", 0xA1)
def g_exclamdown(F):
    g = g_exclam(F)
    g.name = "exclamdown"
    g.apply(T_rot180(0, F.xh / 2 + (F.cap - F.xh) * 0.0 + (F.cap - F.cap) / 2))
    g.apply(T_translate(0, -(F.cap - F.xh)))
    return g


def question_shape(F, W, h):
    w = dw(F)
    S, T = F.SU * 0.94, F.TU * 0.96
    bot_stem = w + h * F.get("excl_gap", 0.13)
    ry = h * F.get("q_ry", 0.27)
    rx = W / 2
    cx, cy = W / 2, h + F.oc - ry
    outer, inner = ring(F, cx, cy, rx, ry, rx - S, ry - T, F.kU, F.kiU)
    p1, d1 = cut_line(F, cx, cy, rx - S / 2, ry - T / 2, F.get("q_th", 155), inner=(rx - S, ry - T))
    xs = cx - min(S * 0.5, (rx - S) * 0.85) + W * F.get("q_sx", 0.0)
    # arc from the bottom-left of the bowl (where the stem starts) around to the left terminal
    from core import line_param
    out = [arc_stroke(F, outer, inner, (2, (xs, 0), V), (1, p1, d1), False, True)]
    yb = cy - ry
    out.append(vstem(F, xs, xs + S, bot_stem, yb + T, True, False))
    out.append(dot_shape(F, xs + S / 2, w / 2, w))
    return out


@glyph("question", 0x3F)
def g_question(F):
    g = new("question")
    W = uc.cw(F, F.q_w)
    g.add(question_shape(F, W, F.cap))
    g.lsb, g.rsb = sbP(F) * 0.9, sbP(F) * 0.9
    return g


@glyph("questiondown", 0xBF)
def g_questiondown(F):
    g = g_question(F)
    g.name = "questiondown"
    b = g.bounds()
    g.apply(T_rot180((b[0] + b[2]) / 2, F.cap / 2))
    g.apply(T_translate(0, -(F.cap - F.xh)))
    return g


# ---------------------------------------------------------------- quotes

def qmark(F, x0, y0):
    """Straight quote stroke with top at y0."""
    S = F.SU * F.get("quote_s", 0.86)
    L = F.cap * F.get("quote_l", 0.30)
    if is_round(F):
        return vstem(F, x0, x0 + S, y0 - L, y0, True, True)
    tb = S * 0.8
    return poly((x0 + (S - tb) / 2, y0 - L), (x0 + (S + tb) / 2, y0 - L), (x0 + S, y0), (x0, y0))


@glyph("quotesingle", 0x27)
def g_quotesingle(F):
    g = new("quotesingle")
    g.add(qmark(F, 0, F.cap))
    g.lsb = g.rsb = sbP(F)
    return g


@glyph("quotedbl", 0x22)
def g_quotedbl(F):
    g = new("quotedbl")
    S = F.SU * F.get("quote_s", 0.86)
    g.add(qmark(F, 0, F.cap))
    g.add(qmark(F, S + F.SU * 0.9, F.cap))
    g.lsb = g.rsb = sbP(F)
    return g


def curly(F, flip, n=1):
    g = Glyph("q")
    w = dw(F)
    gap = w + F.SU * 0.45
    for i in range(n):
        y0 = F.cap - w if not flip else F.cap - w * 1.0 - w * F.get("comma_tail", 1.05) + w * 0.0
        for p in comma_shape(F, i * gap, F.cap - w, flip):
            g.add(p)
    return g


@glyph("quoteright", 0x2019)
def g_quoteright(F):
    g = curly(F, False)
    g.name = "quoteright"
    g.lsb = g.rsb = sbP(F)
    return g


@glyph("quoteleft", 0x2018)
def g_quoteleft(F):
    g = curly(F, True)
    g.name = "quoteleft"
    b = g.bounds()
    g.apply(T_translate(0, F.cap - b[3]))
    g.lsb = g.rsb = sbP(F)
    return g


@glyph("quotedblright", 0x201D)
def g_quotedblright(F):
    g = curly(F, False, 2)
    g.name = "quotedblright"
    g.lsb = g.rsb = sbP(F)
    return g


@glyph("quotedblleft", 0x201C)
def g_quotedblleft(F):
    g = curly(F, True, 2)
    g.name = "quotedblleft"
    b = g.bounds()
    g.apply(T_translate(0, F.cap - b[3]))
    g.lsb = g.rsb = sbP(F)
    return g


@glyph("quotesinglbase", 0x201A)
def g_quotesinglbase(F):
    g = new("quotesinglbase")
    g.add(comma_shape(F, 0, 0))
    g.lsb = g.rsb = sbP(F)
    return g


@glyph("quotedblbase", 0x201E)
def g_quotedblbase(F):
    g = new("quotedblbase")
    w = dw(F)
    g.add(comma_shape(F, 0, 0))
    g.add(comma_shape(F, w + F.SU * 0.45, 0))
    g.lsb = g.rsb = sbP(F)
    return g


# ---------------------------------------------------------------- dashes

def dash_y(F):
    return F.get("dash_y", F.xh * 0.47)


def dash(F, name, W):
    g = new(name)
    T = F.TU * F.get("dash_t", 0.95)
    y = dash_y(F)
    g.add(hstem(F, 0, W, y - T / 2, y + T / 2, True, True))
    return g


@glyph("hyphen", 0x2D)
def g_hyphen(F):
    g = dash(F, "hyphen", F.n_c * F.get("hyph_w", 0.78) + F.S * 0.4)
    g.lsb = g.rsb = sbP(F) * 0.8
    return g


@glyph("endash", 0x2013)
def g_endash(F):
    g = dash(F, "endash", 500 - 2 * sbP(F) * 0.4)
    g.lsb = g.rsb = sbP(F) * 0.4
    return g


@glyph("emdash", 0x2014)
def g_emdash(F):
    g = dash(F, "emdash", 1000 - 2 * sbP(F) * 0.4)
    g.lsb = g.rsb = sbP(F) * 0.4
    return g


@glyph("underscore", 0x5F)
def g_underscore(F):
    g = new("underscore")
    T = F.TU * 0.9
    g.add(rect(0, -F.get("us_y", 130) - T, 520, -F.get("us_y", 130)))
    g.lsb = g.rsb = 0
    return g


# ---------------------------------------------------------------- brackets

def br_top(F):
    return F.cap + F.get("br_up", 0.12) * F.cap


def br_bot(F):
    return -F.get("br_dn", 0.22) * F.cap


@glyph("parenleft", 0x28)
def g_parenleft(F):
    g = new("parenleft")
    S = F.SU * F.get("paren_s", 0.9)
    top, bot = br_top(F), br_bot(F)
    hgt = top - bot
    cy = (top + bot) / 2
    ry = hgt * F.get("paren_ry", 0.56)
    rx = hgt * F.get("paren_rx", 0.30)
    cx = rx
    outer, inner = ring(F, cx, cy, rx, ry, rx - S, ry - S * 0.22, F.k, F.ki)
    g.add(arc_stroke(F, outer, inner, (1, (0, top), H), (2, (0, bot), H)))
    g.lsb, g.rsb = sbP(F) * 1.0, sbP(F) * 0.6
    return g


@glyph("parenright", 0x29)
def g_parenright(F):
    g = g_parenleft(F)
    g.name = "parenright"
    g.mirror_x(0)
    g.lsb, g.rsb = sbP(F) * 0.6, sbP(F) * 1.0
    return g


@glyph("bracketleft", 0x5B)
def g_bracketleft(F):
    g = new("bracketleft")
    S, T = F.SU * 0.92, F.TU * 0.92
    top, bot = br_top(F), br_bot(F)
    W = S + F.get("brk_w", 150)
    g.add(vstem(F, 0, S, bot, top))
    g.add(hstem(F, S * 0.5, W, top - T, top, False, True))
    g.add(hstem(F, S * 0.5, W, bot, bot + T, False, True))
    g.lsb, g.rsb = sbP(F) * 1.1, sbP(F) * 0.5
    return g


@glyph("bracketright", 0x5D)
def g_bracketright(F):
    g = g_bracketleft(F)
    g.name = "bracketright"
    g.mirror_x(0)
    g.lsb, g.rsb = sbP(F) * 0.5, sbP(F) * 1.1
    return g


@glyph("braceleft", 0x7B)
def g_braceleft(F):
    g = new("braceleft")
    S, T = F.SU * 0.88, F.TU * 0.88
    top, bot = br_top(F), br_bot(F)
    cy = (top + bot) / 2
    r = F.get("brace_r", 60 + S * 0.95)
    x = r * 1.0  # stem left edge
    # top hook: quarter ring from the stem curling right
    o, i = ring(F, x + r, top - r, r, r, r - S, r - T, F.k, F.ki)
    g.add(arc_stroke(F, o, i, (0, 1.0, None), (1, 1.0, None), True, False))
    o, i = ring(F, x + r, bot + r, r, r, r - S, r - T, F.k, F.ki)
    g.add(arc_stroke(F, o, i, (2, 0.0, None), (3, 0.0, None), False, True))
    g.add(rect(x, cy + r * 0.9, x + S, top - r))
    g.add(rect(x, bot + r, x + S, cy - r * 0.9))
    # middle point: two quarter arcs meeting at the left tip
    o, i = ring(F, x - r * 0.0 + S - r, cy + r * 0.9, r, r * 0.9, r - S, r * 0.9 - T, F.k, F.ki)
    g.add(arc_stroke(F, o, i, (3, 0.0, None), (0, 0.0, None), True, False))
    o, i = ring(F, x + S - r, cy - r * 0.9, r, r * 0.9, r - S, r * 0.9 - T, F.k, F.ki)
    g.add(arc_stroke(F, o, i, (0, 0.0, None), (0, 1.0, None), False, True))
    g.lsb, g.rsb = sbP(F) * 0.8, sbP(F) * 0.5
    return g


@glyph("braceright", 0x7D)
def g_braceright(F):
    g = g_braceleft(F)
    g.name = "braceright"
    g.mirror_x(0)
    g.lsb, g.rsb = sbP(F) * 0.5, sbP(F) * 0.8
    return g


@glyph("slash", 0x2F)
def g_slash(F):
    g = new("slash")
    t = F.SU * 0.86
    top, bot = br_top(F), br_bot(F) * 0.6
    W = (top - bot) * F.get("slash_k", 0.36)
    if is_round(F):
        g.add(stroke(F, (t / 2, bot + t / 2), (W - t / 2, top - t / 2), t, True, True))
    else:
        w = slant_w(t, W, top - bot)
        g.add(dquad((w / 2, bot), (W - w / 2, top), w))
    g.lsb = g.rsb = sbP(F) * 0.15
    return g


@glyph("backslash", 0x5C)
def g_backslash(F):
    g = g_slash(F)
    g.name = "backslash"
    g.mirror_x(0)
    g.lsb = g.rsb = sbP(F) * 0.15
    return g


@glyph("bar", 0x7C)
def g_bar(F):
    g = new("bar")
    S = F.SU * 0.86
    g.add(vstem(F, 0, S, br_bot(F), br_top(F), True, True))
    g.lsb = g.rsb = sbP(F) * 1.3
    return g


# ---------------------------------------------------------------- math

def mt(F):
    return min(F.TU * F.get("math_t", 0.92), mW(F) * 0.3)


def mW(F):
    return F.get("math_w", 0.52) * F.cap


@glyph("plus", 0x2B)
def g_plus(F):
    g = new("plus")
    W, T, y = mW(F), mt(F), ym(F)
    g.add(hstem(F, 0, W, y - T / 2, y + T / 2, True, True))
    g.add(vstem(F, W / 2 - T / 2, W / 2 + T / 2, y - W / 2, y + W / 2, True, True))
    g.lsb = g.rsb = sbP(F) * 0.9
    return g


@glyph("minus", 0x2212)
def g_minus(F):
    g = new("minus")
    W, T, y = mW(F), mt(F), ym(F)
    g.add(hstem(F, 0, W, y - T / 2, y + T / 2, True, True))
    g.lsb = g.rsb = sbP(F) * 0.9
    return g


@glyph("equal", 0x3D)
def g_equal(F):
    g = new("equal")
    W, T, y = mW(F), mt(F), ym(F)
    gap = W * 0.2
    g.add(hstem(F, 0, W, y + gap / 2, y + gap / 2 + T, True, True))
    g.add(hstem(F, 0, W, y - gap / 2 - T, y - gap / 2, True, True))
    g.lsb = g.rsb = sbP(F) * 0.9
    return g


@glyph("plusminus", 0xB1)
def g_plusminus(F):
    g = new("plusminus")
    W, T = mW(F), mt(F)
    y = ym(F) + W * 0.12
    h = W * 0.42
    g.add(hstem(F, 0, W, y - T / 2, y + T / 2, True, True))
    g.add(vstem(F, W / 2 - T / 2, W / 2 + T / 2, y - h, y + h, True, True))
    g.add(hstem(F, 0, W, y - h - W * 0.16 - T, y - h - W * 0.16, True, True))
    g.lsb = g.rsb = sbP(F) * 0.9
    return g


@glyph("multiply", 0xD7)
def g_multiply(F):
    g = new("multiply")
    W, T, y = mW(F) * 0.8, mt(F) * (1.0 if F.mi < 2 else 0.86), ym(F)
    c = W / 2
    a = W / 2 - T * 0.36
    g.add(stroke(F, (c - a, y - a), (c + a, y + a), T, True, True))
    g.add(stroke(F, (c - a, y + a), (c + a, y - a), T, True, True))
    g.lsb = g.rsb = sbP(F) * 0.9 + mW(F) * 0.1
    return g


@glyph("divide", 0xF7)
def g_divide(F):
    g = new("divide")
    W, T, y = mW(F), mt(F), ym(F)
    w = dw(F) * 0.95
    g.add(hstem(F, 0, W, y - T / 2, y + T / 2, True, True))
    g.add(dot_shape(F, W / 2, y + T / 2 + W * 0.13 + w / 2, w))
    g.add(dot_shape(F, W / 2, y - T / 2 - W * 0.13 - w / 2, w))
    g.lsb = g.rsb = sbP(F) * 0.9
    return g


def chevron(F, x0, W, y, h, T, left=True):
    """Chevron pointing left (or right) with tip at x0 (or x0+W)."""
    T = min(T, W * 0.42, h * 0.3)
    if is_round(F):
        tip = (x0 + T / 2, y) if left else (x0 + W - T / 2, y)
        far = x0 + W - T / 2 if left else x0 + T / 2
        return [stroke(F, tip, (far, y + h / 2 - T / 2), T, True, True),
                stroke(F, tip, (far, y - h / 2 + T / 2), T, True, True)]
    a = math.atan2(h / 2, W)
    T = min(T, W * math.sin(a) * 0.62)
    wx = T / math.sin(a)  # horizontal thickness
    p = poly((x0, y), (x0 + W, y + h / 2), (x0 + W, y + h / 2 - T / math.cos(a)),
             (x0 + wx, y), (x0 + W, y - h / 2 + T / math.cos(a)), (x0 + W, y - h / 2))
    if not left:
        p = p.map(lambda q: (2 * x0 + W - q[0], q[1]))
    return [p]


@glyph("less", 0x3C)
def g_less(F):
    g = new("less")
    W, T, y = mW(F) * 0.92, mt(F), ym(F)
    g.add(chevron(F, 0, W, y, W * 1.1, T, True))
    g.lsb = g.rsb = sbP(F) * 0.9
    return g


@glyph("greater", 0x3E)
def g_greater(F):
    g = new("greater")
    W, T, y = mW(F) * 0.92, mt(F), ym(F)
    g.add(chevron(F, 0, W, y, W * 1.1, T, False))
    g.lsb = g.rsb = sbP(F) * 0.9
    return g


@glyph("guilsinglleft", 0x2039)
def g_guilsinglleft(F):
    g = new("guilsinglleft")
    W, T = F.xh * 0.34, F.T * 0.92
    g.add(chevron(F, 0, W, F.xh * 0.5, F.xh * 0.62, T, True))
    g.lsb = g.rsb = sbP(F) * 0.6
    return g


@glyph("guilsinglright", 0x203A)
def g_guilsinglright(F):
    g = g_guilsinglleft(F)
    g.name = "guilsinglright"
    g.mirror_x(0)
    return g


@glyph("guillemotleft", 0xAB)
def g_guillemotleft(F):
    g = new("guillemotleft")
    W, T = F.xh * 0.34, F.T * 0.92
    g.add(chevron(F, 0, W, F.xh * 0.5, F.xh * 0.62, T, True))
    g.add(chevron(F, W * 0.9 + F.S * 0.3, W, F.xh * 0.5, F.xh * 0.62, T, True))
    g.lsb = g.rsb = sbP(F) * 0.6
    return g


@glyph("guillemotright", 0xBB)
def g_guillemotright(F):
    g = g_guillemotleft(F)
    g.name = "guillemotright"
    g.mirror_x(0)
    return g


@glyph("asciicircum", 0x5E)
def g_asciicircum(F):
    g = new("asciicircum")
    W, T = mW(F) * 0.9, mt(F)
    for p in chevron(F, F.cap - W * 0.62, W * 0.62, W / 2, W, T, False):
        g.add(p.map(lambda q: (q[1], q[0])))
    g.lsb = g.rsb = sbP(F) * 0.7
    return g


@glyph("asciitilde", 0x7E)
def g_asciitilde(F):
    g = new("asciitilde")
    W, T, y = mW(F) * 1.0, mt(F), ym(F)
    a = W * 0.1
    # wave: top edge and bottom edge offset vertically
    def wave(dy):
        p = []
        return p
    t = T * 1.05
    p = Path((0, y - a + t * 0.0))
    p.T((W * 0.3, y + a), (1, 1.6), H, 0.6).T((W * 0.7, y - a), H, H, 0.6).T((W, y + a), H, (1, 1.6), 0.6)
    p.L((W, y + a + t))
    p.T((W * 0.7, y - a + t), (1, 1.6), H, 0.6).T((W * 0.3, y + a + t), H, H, 0.6).T((0, y - a + t), H, (1, 1.6), 0.6)
    g.add(p.map(lambda q: (q[0], q[1] - t / 2)))
    g.lsb = g.rsb = sbP(F) * 0.9
    return g


@glyph("asterisk", 0x2A)
def g_asterisk(F):
    g = new("asterisk")
    T = mt(F) * F.get("ast_t", (0.95, 0.9, 0.78))[F.mi] if isinstance(F.get("ast_t", None), tuple) else mt(F) * (0.95 if F.mi < 2 else 0.8)
    R = F.cap * 0.18
    cx, cy = R, F.cap - R * 1.05
    for i in range(5):
        a = math.radians(90 + 72 * i)
        tip = (cx + R * math.cos(a), cy + R * math.sin(a))
        g.add(stroke(F, (cx, cy), tip, T, False, True))
    g.lsb = g.rsb = sbP(F) * 0.6
    return g


@glyph("numbersign", 0x23)
def g_numbersign(F):
    g = new("numbersign")
    W = uc.cw(F, 0.86)
    T = mt(F) * 0.95
    h = F.cap
    sl = W * 0.12
    for x in (W * 0.33, W * 0.67):
        g.add(stroke(F, (x - sl, 0 + T * 0.0), (x + sl, h), T, True, True) if is_round(F) else
              dquad((x - sl, 0), (x + sl, h), slant_w(T, 2 * sl, h)))
    for y in (h * 0.31, h * 0.66):
        g.add(hstem(F, 0, W, y - T / 2, y + T / 2, True, True))
    g.lsb = g.rsb = sbP(F) * 0.4
    return g


@glyph("percent", 0x25)
def g_percent(F):
    g = new("percent")
    S, T = F.SU * 0.8, F.TU * 0.8
    r = F.cap * 0.2
    W = max(uc.cw(F, 1.2), F.cap * 0.62)
    h = F.cap
    rx = min(r, W * 0.27)   # narrow families get upright ovals instead of overlapping rings
    # keep the counters open at heavy weights (and in narrow families)
    S, T = min(S, rx * (0.5 if rx < r else 0.6)), min(T, r * (0.5 if rx < r else 0.6))
    for (cx, cy) in ((rx, h - r), (W - rx, r)):
        g.add(oval(cx, cy, rx, r + F.oc * 0.5, F.kU))
        g.hole(oval(cx, cy, rx - S, r + F.oc * 0.5 - T, F.kiU))
    t = min(S, W * 0.16) if rx < r else S
    if is_round(F):
        g.add(stroke(F, (W * 0.24, t / 2), (W * 0.76, h - t / 2), t, True, True))
    else:
        w = slant_w(t, W * 0.52, h)
        g.add(dquad((W * 0.24 + w / 2, 0), (W * 0.76 - w / 2, h), w))
    g.lsb = g.rsb = sbP(F) * 0.7
    return g


@glyph("degree", 0xB0)
def g_degree(F):
    g = new("degree")
    r = F.cap * 0.14
    S = F.SU * 0.7
    cy = F.cap - r
    g.add(oval(r, cy, r, r, 0.5523))
    g.hole(oval(r, cy, r - S, r - S, 0.5523))
    g.lsb = g.rsb = sbP(F) * 0.7
    return g


def arrow(F, name, direction):
    g = new(name)
    T = mt(F)
    L = F.get("arrow_l", 0.86) * F.cap
    hw = L * 0.34  # head half height
    hl = L * 0.36
    y = ym(F)
    if is_round(F):
        tip = (L - T / 2, y)
        g.add(hstem(F, 0, L - T * 0.6, y - T / 2, y + T / 2, True, False))
        g.add(stroke(F, tip, (L - hl, y + hw), T, True, True))
        g.add(stroke(F, tip, (L - hl, y - hw), T, True, True))
    else:
        a = math.atan2(hw, hl)
        g.add(rect(0, y - T / 2, L - T * 0.8, y + T / 2))
        g.add(chevron(F, L - hl, hl, y, 2 * hw, T * 0.98, False)[0])
    c = (L / 2, y)
    if direction == "left":
        g.mirror_x(L / 2)
    elif direction == "up":
        g.apply(T_rotate(90, *c))
    elif direction == "down":
        g.apply(T_rotate(-90, *c))
    g.lsb = g.rsb = sbP(F) * 0.8
    return g


@glyph("arrowright", 0x2192)
def g_arrowright(F):
    return arrow(F, "arrowright", "right")


@glyph("arrowleft", 0x2190)
def g_arrowleft(F):
    return arrow(F, "arrowleft", "left")


@glyph("arrowup", 0x2191)
def g_arrowup(F):
    return arrow(F, "arrowup", "up")


@glyph("arrowdown", 0x2193)
def g_arrowdown(F):
    return arrow(F, "arrowdown", "down")


# ---------------------------------------------------------------- @ & $ etc

@glyph("at", 0x40)
def g_at(F):
    g = new("at")
    R = F.cap * 0.56
    t = min(F.SU * 0.80, R * 0.25)
    T = min(F.TU * 0.80, R * 0.23)
    cx, cy = R, F.cap * 0.40
    outer, inner = ring(F, cx, cy, R, R, R - t, R - T, F.kU, F.kiU)
    p1, d1 = cut_line(F, cx, cy, R - t / 2, R - T / 2, -58, "radial" if F.term != "round" else "round")
    g.add(arc_stroke(F, outer, inner, (0, 0.0, None), (3, p1, d1), False, True))
    rb = R * 0.40
    xs = cx + R * 0.30  # stem right edge
    bcx = xs - t - rb + t
    g.add(oval(xs - rb, cy, rb, rb + 6, F.k))
    g.hole(oval(xs - rb, cy, rb - t, rb + 6 - T, F.ki))
    # stem with a hook that rejoins the outer ring on the right
    rxh = (cx + R - (xs - t)) / 2
    ryh = R * 0.26
    cyh = cy - rb + ryh - T * 0.3
    o2, i2 = ring(F, xs - t + rxh, cyh, rxh, ryh, rxh - t, ryh - T, F.kU, F.kiU)
    g.add(arc_stroke(F, o2, i2, (2, 0.0, None), (3, 1.0, None), False, False))
    g.add(rect(xs - t, cyh, xs, cy + rb))
    g.add(rect(cx + R - t, cyh, cx + R, cy + 1))
    g.lsb = g.rsb = sbP(F) * 0.6
    return g


@glyph("ampersand", 0x26)
def g_ampersand(F):
    g = new("ampersand")
    S, T = F.SU * 0.95, F.TU * 0.95
    h, o = F.cap, F.oc
    W = uc.cw(F, F.get("amp_w", 1.02))
    # top loop
    rxt = W * 0.25
    ryt = h * 0.21
    cxt, cyt = W * 0.40, h + o - ryt
    g.add(oval(cxt, cyt, rxt, ryt, F.kU))
    g.hole(oval(cxt, cyt, rxt - S * 0.92, ryt - T, F.kiU))
    # lower bowl
    rxl = W * 0.40
    ryl = h * 0.33
    cxl, cyl = W * 0.40, ryl - o
    ol, il = ring(F, cxl, cyl, rxl, ryl, rxl - S, ryl - T, F.kU, F.kiU)
    pe, de = cut_line(F, cxl, cyl, rxl - S / 2, ryl - T / 2, F.get("amp_th", 22), inner=(rxl - S, ryl - T))
    ps, ds = cut_line(F, cxl, cyl, rxl - S / 2, ryl - T / 2, 128, "radial")
    g.add(arc_stroke(F, ol, il, (1, ps, ds), (0, pe, de), False, True))
    # spine: loop lower-right down to bowl upper-left
    a = (cxt + (rxt - S / 2) * math.cos(math.radians(-58)), cyt + (ryt - T / 2) * math.sin(math.radians(-58)))
    b = (cxl + (rxl - S / 2) * math.cos(math.radians(128)), cyl + (ryl - T / 2) * math.sin(math.radians(128)))
    g.add(stroke(F, a, b, S * 0.92))
    # leg: loop lower-left down to the bottom right
    c = (cxt + (rxt - S / 2) * math.cos(math.radians(222)), cyt + (ryt - T / 2) * math.sin(math.radians(222)))
    t = S * 0.94
    if is_round(F):
        g.add(stroke(F, c, (W - t / 2, t / 2), t, False, True))
    else:
        w = slant_w(t, W - c[0], c[1])
        g.add(dquad((W - w / 2, 0), c, w))
    g.lsb, g.rsb = sbP(F) * 0.7, sbP(F) * 0.2
    return g
