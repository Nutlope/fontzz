"""Uppercase letters."""
import math
from core import (Glyph, Path, rect, oval, quad_cubics, H, V, D, lerp, T_rot180, add, sub, mul,
                  norm, split, line_param, tension_handles, cap_round, intersect, reverse_cubic)
from parts import (vstem, hstem, stroke, dot_shape, cut_line, arc_stroke, ring, shoulder, bowl,
                   is_round, junction, vee, dquad, slant_w, hook_ring, hslab)
from glyphs import glyph, sb, new
import lc


def cw(F, r):
    return (2 * F.SU + F.H_c) * r


def bars_t(F):
    return F.TU


def cap_ring(F, W, S=None, T=None, h=None, o=None):
    h = F.cap if h is None else h
    o = F.oc if o is None else o
    S = F.SU * F.get("O_sx", 1.04) if S is None else S
    T = F.TU if T is None else T
    cx, cy = W / 2, h / 2
    rxo, ryo = W / 2, h / 2 + o
    return cx, cy, rxo, ryo, rxo - S, ryo - T


def S_(F, kind):
    return sb(F, kind, uc=True)


# ---------------------------------------------------------------- straight

@glyph("H", 0x48)
def g_H(F):
    g = new("H")
    S, cap, T = F.SU, F.cap, F.TU
    W = cw(F, 1.0)
    g.add(vstem(F, 0, S, 0, cap, "B", "B"))
    g.add(vstem(F, W - S, W, 0, cap, "B", "B"))
    yb = cap * F.get("H_bar", 0.5) - T / 2 + F.get("H_bar_d", 6)
    g.add(rect(S * 0.5, yb, W - S * 0.5, yb + T))
    g.lsb = g.rsb = S_(F, "S")
    return g


@glyph("I", 0x49)
def g_I(F):
    g = new("I")
    g.add(vstem(F, 0, F.SU, 0, F.cap, "B", "B"))
    g.lsb = g.rsb = S_(F, "S")
    return g


def E_like(F, W, bars, stem=("L", "L")):
    g = new("E")
    S, cap, T = F.SU, F.cap, F.TU
    g.add(vstem(F, 0, S, 0, cap, stem[0], stem[1]))
    beak = {"top": "D", "mid": "B", "bot": "U"}
    for b, wr in bars.items():
        if b == "top":
            g.add(hstem(F, S * 0.5, W * wr, cap - T, cap, False, beak[b]))
        elif b == "mid":
            yb = cap * F.get("E_mid", 0.5) - T / 2 + F.get("H_bar_d", 6)
            g.add(hstem(F, S * 0.5, W * wr, yb, yb + T, False, beak[b] if F.get("sf_midbeak", True) else True))
        elif b == "bot":
            g.add(hstem(F, S * 0.5, W * wr, 0, T, False, beak[b]))
    return g


@glyph("E", 0x45)
def g_E(F):
    W = cw(F, F.E_w)
    g = E_like(F, W, {"top": 1.0, "mid": F.get("E_midw", 0.93), "bot": 1.0})
    g.lsb, g.rsb = S_(F, "S"), S_(F, "D") * 2.6
    return g


@glyph("F", 0x46)
def g_F(F):
    W = cw(F, F.F_w)
    g = E_like(F, W, {"top": 1.0, "mid": F.get("F_midw", 0.93)}, ("B", "L"))
    g.lsb, g.rsb = S_(F, "S"), S_(F, "D") * 2.0
    return g


@glyph("L", 0x4C)
def g_L(F):
    W = cw(F, F.L_w)
    g = E_like(F, W, {"bot": 1.0}, ("L", "B"))
    g.lsb, g.rsb = S_(F, "S"), S_(F, "D")
    return g


@glyph("T", 0x54)
def g_T(F):
    g = new("T")
    S, cap, T = F.SU, F.cap, F.TU
    W = cw(F, F.T_w)
    g.add(hstem(F, 0, W, cap - T, cap, "D", "D"))
    g.add(vstem(F, W / 2 - S / 2, W / 2 + S / 2, 0, cap - T * 0.5, "B", False))
    g.lsb = g.rsb = S_(F, "D")
    return g


# ---------------------------------------------------------------- round

def O_w(F):
    if F.get("O_circle"):
        return (F.cap + 2 * F.oc) * F.O_circle
    return cw(F, F.O_w)


@glyph("O", 0x4F)
def g_O(F):
    g = new("O")
    W = O_w(F)
    cx, cy, rxo, ryo, rxi, ryi = cap_ring(F, W)
    g.add(oval(cx, cy, rxo, ryo, F.kU))
    g.hole(oval(cx, cy, rxi, ryi, F.kiU))
    g.lsb = g.rsb = S_(F, "O")
    return g


@glyph("Q", 0x51)
def g_Q(F):
    g = g_O(F)
    g.name = "Q"
    W = O_w(F)
    S, cap = F.SU, F.cap
    t = S * F.get("Q_t", 0.9)
    a = (W * F.get("Q_x0", 0.58), cap * F.get("Q_y0", 0.24))
    b = (W * F.get("Q_x1", 0.95), -cap * F.get("Q_y1", 0.06))
    if is_round(F):
        g.add(stroke(F, a, b, t, True, True))
    else:
        w = slant_w(t, b[0] - a[0], a[1] - b[1])
        g.add(dquad(b, a, w))
    # keep the O's spacing: the tail may hang into the right side bearing
    lsb = S_(F, "O")
    g.apply(lambda p: (p[0] + lsb, p[1]))
    g.width = lsb + W + S_(F, "O")
    g.lsb = None
    return g


def C_arc(F, W, th_top, th_bot):
    cx, cy, rxo, ryo, rxi, ryi = cap_ring(F, W)
    outer, inner = ring(F, cx, cy, rxo, ryo, rxi, ryi, F.kU, F.kiU)
    rxm, rym = (rxo + rxi) / 2, (ryo + ryi) / 2
    p0, d0 = cut_line(F, cx, cy, rxm, rym, th_top, inner=(rxi, ryi))
    p1, d1 = cut_line(F, cx, cy, rxm, rym, th_bot, inner=(rxi, ryi))
    return arc_stroke(F, outer, inner, (0, p0, d0), (3, p1, d1)), (cx, cy, rxo, ryo, rxi, ryi, outer,
                                                                     inner, rxm, rym)


@glyph("C", 0x43)
def g_C(F):
    g = new("C")
    W = cw(F, F.C_w)
    p, _ = C_arc(F, W, F.C_th, F.C_thb)
    g.add(p)
    g.lsb, g.rsb = S_(F, "O"), S_(F, "O") * 0.8
    return g


@glyph("G", 0x47)
def g_G(F):
    g = new("G")
    W = cw(F, F.G_w)
    S, T, cap = F.SU, F.TU, F.cap
    cx, cy, rxo, ryo, rxi, ryi = cap_ring(F, W)
    outer, inner = ring(F, cx, cy, rxo, ryo, rxi, ryi, F.kU, F.kiU)
    rxm, rym = (rxo + rxi) / 2, (ryo + ryi) / 2
    p0, d0 = cut_line(F, cx, cy, rxm, rym, F.G_th, inner=(rxi, ryi))
    g.add(arc_stroke(F, outer, inner, (0, p0, d0), (3, 1.0, None), cap1=False))
    bt = cap * F.G_bar
    g.add(rect(W - S * F.get("G_sx", 1.0), cy, W, bt))
    g.add(hstem(F, W * F.G_barx, W - S * 0.5, bt - T, bt, True, False))
    if F.G_spur:
        g.add(rect(W - S * F.get("G_sx", 1.0), 0, W, cy))
    g.lsb, g.rsb = S_(F, "O"), S_(F, "S") * F.get("G_rsb", 0.9)
    return g


def dbowl(F, x0, xR, y0, y1, S, T, k=None, ki=None, rxr=None):
    """D-style bowl: flat top/bottom from x0, round right side reaching xR."""
    k = F.kU if k is None else k
    ki = F.kiU if ki is None else ki
    h = y1 - y0
    ym = (y0 + y1) / 2
    rx = min(xR - x0 - S * 0.3, h / 2 * (F.D_rx if rxr is None else rxr))
    xc = xR - rx
    o = F.get("D_o", 0)
    outer = Path((x0, y0 - 0)).L((xc, y0))
    outer.T((xR + o, ym), H, V, k).T((xc, y1), V, H, k).L((x0, y1))
    xci = xc - F.get("D_ix", 0.0) * rx
    inner = Path((x0, y0 + T)).L((xci, y0 + T))
    inner.T((xR + o - S, ym), H, V, ki).T((xci, y1 - T), V, H, ki).L((x0, y1 - T))
    return outer, inner


@glyph("D", 0x44)
def g_D(F):
    g = new("D")
    S, T, cap = F.SU, F.TU, F.cap
    W = cw(F, F.D_w)
    g.add(vstem(F, 0, S, 0, cap, "L", "L"))
    o, i = dbowl(F, S * 0.5, W, 0, cap, S * F.get("O_sx", 1.04), T, rxr=F.D_rx)
    g.add(o)
    g.hole(i)
    g.lsb, g.rsb = S_(F, "S"), S_(F, "O")
    return g


@glyph("B", 0x42)
def g_B(F):
    g = new("B")
    S, T, cap = F.SU, F.TU, F.cap
    W = cw(F, F.B_w)
    ym = cap * F.B_mid
    g.add(vstem(F, 0, S, 0, cap, "L", "L"))
    o, i = dbowl(F, S * 0.5, W * F.B_up, ym - T / 2, cap, S * 0.98, T, rxr=F.B_rx)
    g.add(o)
    g.hole(i)
    o, i = dbowl(F, S * 0.5, W, 0, ym + T / 2, S, T, rxr=F.B_rx)
    g.add(o)
    g.hole(i)
    g.lsb, g.rsb = S_(F, "S"), S_(F, "O") * 1.05
    return g


def P_bowl(F, W):
    S, T, cap = F.SU, F.TU, F.cap
    yb = cap * F.P_bot
    return dbowl(F, S * 0.5, W, yb, cap, S, T, rxr=F.P_rx), yb


@glyph("P", 0x50)
def g_P(F):
    g = new("P")
    S, cap = F.SU, F.cap
    W = cw(F, F.P_w)
    g.add(vstem(F, 0, S, 0, cap, "B", "L"))
    (o, i), _ = P_bowl(F, W)
    g.add(o)
    g.hole(i)
    g.lsb, g.rsb = S_(F, "S"), S_(F, "O")
    return g


@glyph("R", 0x52)
def g_R(F):
    g = new("R")
    S, T, cap = F.SU, F.TU, F.cap
    W = cw(F, F.R_w)
    Wb = W * F.R_bw
    g.add(vstem(F, 0, S, 0, cap, "B", "L"))
    (o, i), yb = P_bowl(F, Wb)
    g.add(o)
    g.hole(i)
    t = S * F.get("dg", 0.92)
    top = (lerp(S, Wb, F.R_lx), yb + T * 0.5)
    w = slant_w(t, W - top[0], top[1])
    if is_round(F):
        g.add(stroke(F, top, (W - t / 2, t / 2), t, False, True))
    else:
        g.add(dquad((W - w / 2, 0), top, w))
        g.add(hslab(F, W - w, W, 0, True))
    g.lsb, g.rsb = S_(F, "S"), S_(F, "D")
    return g


@glyph("U", 0x55)
def g_U(F):
    g = new("U")
    S, T, cap, o = F.SU, F.TU, F.cap, F.oc
    W = cw(F, F.U_w)
    rx = W / 2
    ry = cap * F.U_ry
    cy = ry - o
    outer, inner = ring(F, W / 2, cy, rx, ry, rx - S, ry - T, F.kU, F.kiU)
    g.add(arc_stroke(F, outer, inner, (2, 0.0, None), (3, 1.0, None), False, False))
    g.add(vstem(F, 0, S, cy, cap, False, "B"))
    g.add(vstem(F, W - S, W, cy, cap, False, "B"))
    g.lsb = g.rsb = S_(F, "S") * 0.96
    return g


@glyph("J", 0x4A)
def g_J(F):
    g = new("J")
    S, T, cap, o = F.SU, F.TU, F.cap, F.oc
    W = cw(F, F.J_w)
    rx = W / 2
    ry = cap * F.J_ry
    cy = ry - o
    outer, inner = ring(F, W / 2, cy, rx, ry, rx - S, ry - T, F.kU, F.kiU)
    rxm, rym = rx - S / 2, ry - T / 2
    p0, d0 = cut_line(F, W / 2, cy, rxm, rym, F.J_th, F.get("hook_term"), inner=(rx - S, ry - T))
    g.add(arc_stroke(F, outer, inner, (2, p0, d0), (3, 1.0, None), True, False))
    g.add(vstem(F, W - S, W, cy, cap, False, "L"))
    g.lsb, g.rsb = S_(F, "D") * 2, S_(F, "S")
    return g


@glyph("S", 0x53)
def g_S(F):
    g = new("S")
    W = cw(F, F.S_w)
    g.add(lc.s_shape(F, W, F.cap, F.oc, F.SU * F.get("S_S", 0.98), F.TU * F.get("S_T", 1.0),
                     F.S_tth, F.S_bth, F.kU, F.kiU))
    g.lsb = g.rsb = S_(F, "O") * 0.95
    return g


# ---------------------------------------------------------------- diagonal caps

def cdiag(F):
    return F.SU * F.get("dgU", 0.92)


@glyph("V", 0x56)
def g_V(F):
    g = new("V")
    W = cw(F, F.V_w)
    g.add(vee(F, 0, W, F.cap, 0, cdiag(F), apex=F.SU * F.get("V_apex", 0.6), serifs=True))
    g.lsb = g.rsb = S_(F, "D")
    return g


@glyph("A", 0x41)
def g_A(F):
    g = new("A")
    W = cw(F, F.A_w)
    cap = F.cap
    t = cdiag(F)
    a = F.SU * F.get("A_apex", 0.6)
    for p in vee(F, 0, W, 0, cap, t, apex=a, serifs=True):
        g.add(p)
    # crossbar between the stroke centerlines
    yb = cap * F.A_bar
    wx = slant_w(t, W / 2 - a / 2, cap)
    xl = wx / 2 + (W / 2 - a / 2) * (yb + F.TU / 2) / cap
    g.add(rect(xl, yb, W - xl, yb + F.TU * F.get("A_barT", 0.95)))
    g.lsb = g.rsb = S_(F, "D")
    return g


@glyph("W", 0x57)
def g_W(F):
    g = new("W")
    W1 = cw(F, F.W_w)
    t = cdiag(F) * F.get("W_t", 0.94)
    a = F.SU * F.get("V_apex", 0.6) * 0.9
    wx = slant_w(t, W1 / 2 - a / 2, F.cap)
    g.add(vee(F, 0, W1, F.cap, 0, t, apex=a, serifs=True))
    off = W1 - wx if not is_round(F) else W1 - t
    g.add(vee(F, off, W1, F.cap, 0, t, apex=a, serifs=True))
    g.lsb = g.rsb = S_(F, "D")
    return g


@glyph("X", 0x58)
def g_X(F):
    g = new("X")
    W = cw(F, F.X_w)
    t = cdiag(F)
    cap = F.cap
    if is_round(F):
        g.add(stroke(F, (t / 2, cap - t / 2), (W - t / 2, t / 2), t, True, True))
        g.add(stroke(F, (W - t / 2, cap - t / 2), (t / 2, t / 2), t, True, True))
    else:
        w = slant_w(t, W, cap)
        g.add(dquad((W - w / 2, 0), (w / 2, cap), w))
        w2 = w * F.get("diag_c", 1.0)
        g.add(dquad((w2 / 2, 0), (W - w2 / 2, cap), w2))
        g.add(hslab(F, 0, w, cap, False), hslab(F, W - w2, W, cap, False),
              hslab(F, W - w, W, 0, True), hslab(F, 0, w2, 0, True))
    g.lsb = g.rsb = S_(F, "D")
    return g


@glyph("Y", 0x59)
def g_Y(F):
    g = new("Y")
    W = cw(F, F.Y_w)
    S, cap = F.SU, F.cap
    t = cdiag(F)
    ym = cap * F.Y_mid
    if is_round(F):
        c = (W / 2, ym)
        g.add(stroke(F, (t / 2, cap - t / 2), c, t, True, False))
        g.add(stroke(F, (W - t / 2, cap - t / 2), c, t, True, False))
        g.add(vstem(F, W / 2 - S / 2, W / 2 + S / 2, 0, ym, True, False))
    else:
        for p in vee(F, 0, W, cap, ym, t, apex=S, serifs=True):
            g.add(p)
        g.add(vstem(F, W / 2 - S / 2, W / 2 + S / 2, 0, ym + 1, "B", False))
    g.lsb = g.rsb = S_(F, "D")
    return g


@glyph("Z", 0x5A)
def g_Z(F):
    g = new("Z")
    W = cw(F, F.Z_w)
    T, cap = F.TU, F.cap
    t = cdiag(F) * F.get("Z_t", 1.0)
    if is_round(F):
        r = T / 2
        g.add(hstem(F, W * 0.04, W, cap - T, cap, True, True))
        g.add(hstem(F, 0, W, 0, T, True, True))
        g.add(stroke(F, (W - r, cap - r), (r, r), t, False, False))
    else:
        g.add(hstem(F, W * F.get("Z_tl", 0.05), W * F.get("Z_tr", 0.98), cap - T, cap, "D", False))
        g.add(hstem(F, 0, W, 0, T, False, "U"))
        from parts import zdiag
        w = slant_w(t, W, cap - 2 * T)
        g.add(zdiag(0, W * F.get("Z_tr", 0.98), T, cap - T, w))
    g.lsb = g.rsb = S_(F, "D") * 1.6
    return g


@glyph("K", 0x4B)
def g_K(F):
    g = new("K")
    S, cap = F.SU, F.cap
    W = cw(F, F.K_w)
    t = cdiag(F)
    g.add(vstem(F, 0, S, 0, cap, "B", "B"))
    yj = cap * F.K_j
    ax0, ay0 = S * 0.5, yj
    tc_x = W * F.get("K_arm_x", 0.98)
    wa = slant_w(t * 0.96, tc_x - ax0, cap - ay0)
    if is_round(F):
        g.add(stroke(F, (ax0, ay0), (tc_x - t / 2, cap - t / 2), t, False, True))
        lx0, ly0 = lerp(ax0, tc_x, F.K_lj), lerp(ay0, cap, F.K_lj)
        g.add(stroke(F, (lx0, ly0), (W - t / 2, t / 2), t, False, True))
    else:
        ta = t * 0.96 * F.get("diag_c", 1.0)
        wa = slant_w(ta, tc_x - ax0, cap - ay0)
        tc = (tc_x - wa / 2, cap)
        dd = norm(sub(tc, (ax0, ay0)))
        nn = (-dd[1] * ta / 2, dd[0] * ta / 2)
        g.add(Path((ax0 + nn[0], ay0 + nn[1])).L((ax0 - nn[0], ay0 - nn[1]))
              .L((tc[0] + wa / 2, cap)).L((tc[0] - wa / 2, cap)))
        lx0, ly0 = lerp(ax0, tc[0], F.K_lj), lerp(ay0, cap, F.K_lj)
        wl = slant_w(t, W - lx0, ly0)
        g.add(dquad((W - wl / 2, 0), (lx0, ly0), wl))
        g.add(hslab(F, tc[0] - wa / 2, tc[0] + wa / 2, cap, False), hslab(F, W - wl, W, 0, True))
    g.lsb, g.rsb = S_(F, "S"), S_(F, "D")
    return g


@glyph("N", 0x4E)
def g_N(F):
    g = new("N")
    S, cap = F.SU * F.get("N_s", 0.94), F.cap
    W = cw(F, F.N_w)
    t = cdiag(F) * F.get("N_t", 0.98)
    g.add(vstem(F, 0, S, 0, cap, "B", "L"))
    g.add(vstem(F, W - S, W, 0, cap, True, "B"))
    if is_round(F):
        g.add(stroke(F, (S / 2, cap - S / 2), (W - S / 2, S / 2), t, False, False))
    else:
        w = slant_w(t, W - S, cap)
        g.add(Path((0, cap)).L((w, cap)).L((W, 0)).L((W - w, 0)))
    g.lsb = g.rsb = S_(F, "S")
    return g


@glyph("M", 0x4D)
def g_M(F):
    g = new("M")
    S, cap = F.SU * F.get("M_s", 0.94), F.cap
    W = cw(F, F.M_w)
    t = cdiag(F) * F.get("M_t", 0.92)
    g.add(vstem(F, 0, S, 0, cap, "B", "L"))
    g.add(vstem(F, W - S, W, 0, cap, "B", "R"))
    if is_round(F):
        c = (W / 2, S / 2)
        g.add(stroke(F, (S / 2, cap - S / 2), c, t, False, False))
        g.add(stroke(F, (W - S / 2, cap - S / 2), c, t, False, False))
    else:
        for p in vee(F, 0, W, cap, 0, t, apex=F.SU * F.get("M_apex", 0.6)):
            g.add(p)
    g.lsb = g.rsb = S_(F, "S")
    return g
