"""Figures (tabular, lining)."""
import math
from core import (Glyph, Path, rect, oval, quad_cubics, H, V, D, lerp, T_rot180, add, sub, mul,
                  norm, split, line_param, cap_round, poly)
from parts import (vstem, hstem, stroke, cut_line, arc_stroke, ring, is_round, dquad, slant_w)
from glyphs import glyph, sb, new
import lc
import uc


def fw(F):
    return uc.cw(F, F.fig_w)


def fadv(F):
    return fw(F) + 2 * uc.S_(F, "O") * F.get("fig_sb", 0.9)


def FS(F):
    return F.SU * F.get("fig_s", 0.95)


def FT(F):
    return F.TU * F.get("fig_t", 0.95)


def tab(g, F):
    b = g.bounds()
    w = b[2] - b[0]
    A = fadv(F)
    g.lsb = (A - w) / 2
    g.rsb = (A - w) / 2
    return g


def fig(name, uni):
    def deco(fn):
        def wrapped(F):
            g = fn(F)
            g.name = name
            return tab(g, F)
        return glyph(name, uni)(wrapped)
    return deco


def ringset(F, cx, cy, rxo, ryo, S, T):
    return ring(F, cx, cy, rxo, ryo, rxo - S, ryo - T, F.kU, F.kiU)


def tangent_theta(cx, cy, rx, ry, target, lo, hi, cw=True):
    """Find theta (deg) in [lo, hi] where the ellipse tangent aims at target."""
    best, bt = 1e9, lo
    for i in range(401):
        th = lo + (hi - lo) * i / 400
        r = math.radians(th)
        p = (cx + rx * math.cos(r), cy + ry * math.sin(r))
        t = (rx * math.sin(r), -ry * math.cos(r)) if cw else (-rx * math.sin(r), ry * math.cos(r))
        v = sub(target, p)
        a = math.atan2(t[1], t[0]) - math.atan2(v[1], v[0])
        a = abs((a + math.pi) % (2 * math.pi) - math.pi)
        if a < best:
            best, bt = a, th
    return bt


@fig("zero", 0x30)
def g_zero(F):
    g = new("zero")
    W = fw(F) * F.get("zero_w", 0.96)
    S, T, h, o = FS(F) * 1.04, FT(F), F.cap, F.oc
    g.add(oval(W / 2, h / 2, W / 2, h / 2 + o, F.kU))
    g.hole(oval(W / 2, h / 2, W / 2 - S, h / 2 + o - T, F.kiU))
    return g


@fig("one", 0x31)
def g_one(F):
    g = new("one")
    S, T, h = FS(F), FT(F), F.cap
    W = fw(F)
    x0 = W * F.get("one_x", 0.52) - S / 2
    g.add(vstem(F, x0, x0 + S, 0, h, False if F.get("one_base") else "B", True))
    fwid = W * F.get("one_fw", 0.34)
    fh = h * F.get("one_fh", 0.17)
    ft = T * F.get("one_ft", 1.0)
    if is_round(F):
        g.add(stroke(F, (x0 + S / 2, h - S / 2), (x0 - fwid + ft / 2, h - fh - ft / 2), ft, False, True))
    else:
        ang = math.atan2(fh, fwid + S * 0.5)
        tv = ft / math.cos(ang)
        g.add(poly((x0 + S * 0.5, h), (x0 - fwid, h - fh), (x0 - fwid, h - fh - tv),
                   (x0 + S * 0.5, h - tv)))
    if F.get("one_base"):
        g.add(hstem(F, x0 - W * 0.26, x0 + S + W * 0.26, 0, T, True, True))
    return g


def two_shape(F, W, h, o, S, T):
    from parts import cubic_tangent_to
    from core import bez
    g = Glyph("two")
    ry = h * F.two_ry
    rx = W / 2 * F.get("two_rx", 0.98)
    cx, cy = W / 2 + W * 0.01, h + o - ry
    outer, inner = ringset(F, cx, cy, rx, ry, S, T)
    rxm, rym = rx - S / 2, ry - T / 2
    p0, d0 = cut_line(F, cx, cy, rxm, rym, F.two_th, inner=(rx - S, ry - T))
    # neck: tangent from the inner bowl to the base corner, outer edge parallel
    tn = S * F.get("two_neck", 0.94)
    ti = cubic_tangent_to(inner[3], (0, T), 0.0, 0.999)
    Pi = bez(*inner[3], ti)
    v = sub((0, T), Pi)
    sa = abs(v[1]) / math.hypot(*v)
    wb = tn / max(sa, 0.3)
    to = cubic_tangent_to(outer[3], (wb, T), 0.0, 0.999)
    Po = bez(*outer[3], to)
    g.add(arc_stroke(F, outer, inner, (3, (to, ti), "tt"), (1, p0, d0), cap0=False))
    g.add(Path(Pi).L(Po).L((wb, T)).L((0, T)))
    g.add(hstem(F, 0, W, 0, T, False, True))
    return g


@fig("two", 0x32)
def g_two(F):
    W = fw(F)
    return two_shape(F, W, F.cap, F.oc, FS(F), FT(F))


@fig("three", 0x33)
def g_three(F):
    g = new("three")
    W = fw(F)
    S, T, h, o = FS(F), FT(F) * F.get("three_t", 0.96), F.cap, F.oc
    m0 = h * F.three_m - T / 2
    ryt = (h + o - m0) / 2
    cyt = m0 + ryt
    ryl = (m0 + T + o) / 2
    cyl = m0 + T - ryl
    rxl = W / 2
    rxt = W / 2 * F.three_up
    cxl = W / 2
    cxt = W - rxt
    ot, it = ringset(F, cxt, cyt, rxt, ryt, S * 0.97, T)
    ol, il = ringset(F, cxl, cyl, rxl, ryl, S, T)
    pt, dt = cut_line(F, cxt, cyt, rxt - S / 2, ryt - T / 2, F.three_tth, inner=(rxt - S, ryt - T))
    pb, db = cut_line(F, cxl, cyl, rxl - S / 2, ryl - T / 2, F.three_bth, inner=(rxl - S, ryl - T))
    g.add(arc_stroke(F, ot, it, (3, 0.0, None), (1, pt, dt), cap0=False))
    g.add(arc_stroke(F, ol, il, (2, pb, db), (0, 1.0, None), cap1=False))
    g.add(hstem(F, W * F.three_bar, max(cxt, cxl) + 1, m0, m0 + T, True, False))
    return g


@fig("four", 0x34)
def g_four(F):
    g = new("four")
    W = fw(F) * F.get("four_w", 1.04)
    S, T, h = FS(F), FT(F), F.cap
    xs = W * F.four_x - S
    yb = h * F.four_bar
    g.add(vstem(F, xs, xs + S, 0, h, True, True))
    g.add(hstem(F, 0, W, yb, yb + T, False, True))
    if is_round(F):
        g.add(stroke(F, (xs + S / 2, h - S / 2), (T / 2, yb + T / 2), S * 0.92, False, False))
    else:
        wd = S * F.get("four_d", 1.04)
        g.add(poly((0, yb + T * 0.5), (wd, yb + T * 0.5), (xs + S, h), (xs + S - wd, h)))
    return g


@fig("five", 0x35)
def g_five(F):
    g = new("five")
    W = fw(F)
    S, T, h, o = FS(F), FT(F), F.cap, F.oc
    ry = h * F.five_ry
    rx = W / 2
    cx, cy = W / 2, ry - o
    outer, inner = ringset(F, cx, cy, rx, ry, S, T)
    pb, db = cut_line(F, cx, cy, rx - S / 2, ry - T / 2, F.five_bth, inner=(rx - S, ry - T))
    pe, de = cut_line(F, cx, cy, rx - S / 2, ry - T / 2, F.five_je, "radial")
    xs = pe[0] - S * 0.5
    from core import solve_t_for, bez
    xcut = min(max(xs + S * 0.5, cx - (rx - S) + 3), xs + S - 3)
    yb = bez(*inner[1], solve_t_for(inner[1], 0, xcut))[1]
    g.add(arc_stroke(F, outer, inner, (2, pb, db), (1, (xcut, 0), V), True, False))
    g.add(vstem(F, xs, xs + S, yb, h, False, True))
    g.add(hstem(F, xs + S * 0.5, W * F.five_bar, h - T, h, False, True))
    return g


def six_shape(F, W, h, o, S, T):
    g = Glyph("six")
    ryb = h * F.six_ry
    rxb = W / 2
    cyb = ryb - o
    g.add(oval(W / 2, cyb, rxb, ryb, F.kU))
    g.hole(oval(W / 2, cyb, rxb - S, ryb - T, F.kiU))
    # big arc: left side rising to the top, ending in a terminal
    ryB = (h + o - (cyb)) * 1.0
    rxB = rxb * F.get("six_bx", 1.0)
    cxB, cyB = rxB, cyb
    oB, iB = ringset(F, cxB, cyB, rxB, ryB, S, T)
    pt, dt = cut_line(F, cxB, cyB, rxB - S / 2, ryB - T / 2, F.six_th, inner=(rxB - S, ryB - T))
    g.add(arc_stroke(F, oB, iB, (0, pt, dt), (1, 1.0, None), True, False))
    return g


@fig("six", 0x36)
def g_six(F):
    W = fw(F)
    return six_shape(F, W, F.cap, F.oc, FS(F), FT(F))


@fig("nine", 0x39)
def g_nine(F):
    W = fw(F)
    g = six_shape(F, W, F.cap, F.oc, FS(F), FT(F))
    g.apply(T_rot180(W / 2, F.cap / 2))
    return g


@fig("seven", 0x37)
def g_seven(F):
    g = new("seven")
    W = fw(F)
    S, T, h = FS(F), FT(F), F.cap
    g.add(hstem(F, 0, W, h - T, h, True, True))
    t = S * F.get("seven_t", 0.94)
    xb = W * F.seven_xb
    if is_round(F):
        g.add(stroke(F, (W - t / 2, h - T / 2), (xb, t / 2), t, False, True))
    else:
        w = slant_w(t, W - xb, h)
        g.add(dquad((xb, 0), (W - w / 2, h - T * 0.5), w))
    return g


@fig("eight", 0x38)
def g_eight(F):
    g = new("eight")
    W = fw(F)
    S, T, h, o = FS(F), FT(F) * F.get("eight_t", 0.95), F.cap, F.oc
    m0 = h * F.eight_m - T / 2
    ryt = (h + o - m0) / 2
    cyt = m0 + ryt
    ryl = (m0 + T + o) / 2
    cyl = m0 + T - ryl
    rxt = W / 2 * F.eight_up
    g.add(oval(W / 2, cyt, rxt, ryt, F.kU))
    g.hole(oval(W / 2, cyt, rxt - S * 0.96, ryt - T, F.kiU))
    g.add(oval(W / 2, cyl, W / 2, ryl, F.kU))
    g.hole(oval(W / 2, cyl, W / 2 - S, ryl - T, F.kiU))
    return g
