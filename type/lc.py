"""Lowercase letters."""
import math
from core import (dot, Glyph, Path, rect, oval, quad_cubics, H, V, D, lerp, T_rot180, add, sub,
                  mul, norm, split, line_param, tension_handles, cap_round)
from parts import (vstem, hstem, stroke, dot_shape, cut_line, arc_stroke, ring, shoulder, bowl,
                   is_round, junction)
from glyphs import glyph, sb, new

# ---------------------------------------------------------------- widths


def n_w(F):
    return 2 * F.S + F.n_c


def o_w(F):
    if F.get("o_circle"):
        return (F.xh + 2 * F.o) * F.o_circle
    return n_w(F) * F.o_w


def add_bowl(g, parts):
    for kind, p in parts:
        if kind == "fill":
            g.add(p)
        else:
            g.hole(p)


# ---------------------------------------------------------------- n family

@glyph("n", 0x6E)
def g_n(F):
    g = new("n")
    S, xh = F.S, F.xh
    W = n_w(F)
    g.add(vstem(F, 0, S, 0, xh, "B", "L"))
    g.add(shoulder(F, 0, S, W, S, "notch", capb=True))
    g.lsb = g.rsb = sb(F, "S")
    return g


@glyph("h", 0x68)
def g_h(F):
    g = new("h")
    S = F.S
    W = n_w(F)
    g.add(vstem(F, 0, S, 0, F.asc, "B", "L"))
    g.add(shoulder(F, 0, S, W, S, "crotch", capb=True))
    g.lsb = g.rsb = sb(F, "S")
    return g


@glyph("m", 0x6D)
def g_m(F):
    g = new("m")
    S, xh = F.S, F.xh
    c = F.n_c * F.m_c
    Sm = S * F.get("m_s", 0.96)
    x1 = S + c + Sm
    x2 = x1 + c + Sm
    g.add(vstem(F, 0, S, 0, xh, "B", "L"))
    g.add(shoulder(F, 0, S, x1, Sm, "notch", capb=True))
    inset = S * F.get("m_inset", 0.5)
    g.add(shoulder(F, x1 - Sm, x1 - inset, x2, Sm, "notch", capb=True,
                   xt=lerp(x1 - Sm, x2, F.sh_xt), xti=lerp(x1, x2 - Sm, F.sh_xti)))
    g.lsb = g.rsb = sb(F, "S")
    return g


@glyph("u", 0x75)
def g_u(F):
    g = g_n(F)
    g.name = "u"
    W = n_w(F)
    g.apply(T_rot180(W / 2, F.xh / 2))
    return g


def terminal_inner(F, Po, beta, Tt, style=None):
    """Inner point of a terminal whose outer point is Po, for a stroke travelling
    in direction beta (deg) with thickness Tt. The inner side is to the right of
    travel (clockwise)."""
    style = style or F.term
    b = math.radians(beta)
    if style in ("radial", "round"):
        return add(Po, mul(D(beta - 90), Tt))
    if style == "flat":
        cut = F.get("arm_cut", 90)
    elif style == "vertical":
        cut = 90
    else:
        cut = F.term_pen
    c = math.radians(cut)
    # move along cut direction (pointing to the inner side) until thickness Tt
    d = D(cut)
    n = D(beta - 90)
    if dot(d, n) < 0:
        d = mul(d, -1)
    s = abs(math.sin(c - b))
    return add(Po, mul(d, Tt / max(s, 0.2)))


def arm(F, xs, xe, W, top=None, T=None, kind="notch", drop=None, Tt=None,
        xt=None, xti=None, ref_h=None):
    """Shoulder that ends in a terminal (r arm)."""
    from parts import jdir
    h = F.xh if ref_h is None else ref_h
    top = h + F.o if top is None else top
    T = F.T if T is None else T
    S = abs(xe - xs)
    drop = F.r_drop if drop is None else drop
    Tt = T * F.get("r_tt", 1.0) if Tt is None else Tt
    xt = lerp(xe, W, F.r_xt) if xt is None else xt
    xti = lerp(xe, W, F.r_xti) if xti is None else xti
    tp, ti = (xt, top), (xti, top - T)
    if F.junction == "smooth":
        yr = h * F.sh_yr
        Jo, do = (xs, yr), V
        Ji, di = (xe, yr), V
        kjo, kji = F.sh_k, F.sh_ki
    else:
        (Jo, co), (Ji, ci) = junction(F, kind, "top", xs, xe, h, S)
        do, di = jdir(Jo, tp, co), jdir(Ji, ti, ci)
        kjo = kji = F.jk
    Po = (W, top - drop)
    # outer tangent at the terminal aims back at a corner on the top line
    cxo = lerp(xt, W, F.r_co)
    to = sub(Po, (cxo, top))
    beta = math.degrees(math.atan2(to[1], to[0]))
    Pi = terminal_inner(F, Po, beta, Tt)
    cxi = lerp(xti, Pi[0], F.r_ci)
    p = Path(Jo)
    p.T(tp, do, H, kjo)
    p.T(Po, H, to, F.r_k)
    if is_round(F):
        for c in cap_round(Po, Pi, to):
            p.seg_cubic(c)
    else:
        p.L(Pi)
    p.T(ti, sub(Pi, (cxi, top - T)), H, F.r_ki)
    p.T(Ji, H, di, kji)
    return p


@glyph("r", 0x72)
def g_r(F):
    g = new("r")
    S, xh = F.S, F.xh
    W = S + F.n_c * F.r_w
    g.add(vstem(F, 0, S, 0, xh, "B", "L"))
    g.add(arm(F, 0, S, W))
    g.lsb = sb(F, "S")
    g.rsb = sb(F, "N") * F.get("r_rsb", 1.0)
    return g


# ---------------------------------------------------------------- round family

def o_ring(F, W, xh=None, o=None, S=None, T=None):
    xh = F.xh if xh is None else xh
    o = F.o if o is None else o
    S = F.S * F.get("o_sx", 1.03) if S is None else S
    T = F.T if T is None else T
    cx, cy = W / 2, xh / 2
    rxo, ryo = W / 2, xh / 2 + o
    return cx, cy, rxo, ryo, rxo - S, ryo - T


@glyph("o", 0x6F)
def g_o(F):
    g = new("o")
    W = o_w(F)
    cx, cy, rxo, ryo, rxi, ryi = o_ring(F, W)
    g.add(oval(cx, cy, rxo, ryo, F.k))
    g.hole(oval(cx, cy, rxi, ryi, F.ki))
    g.lsb = g.rsb = sb(F, "O")
    return g


def c_like(F, W, th_top, th_bot, xh=None):
    cx, cy, rxo, ryo, rxi, ryi = o_ring(F, W, xh)
    outer, inner = ring(F, cx, cy, rxo, ryo, rxi, ryi)
    rxm, rym = (rxo + rxi) / 2, (ryo + ryi) / 2
    p0, d0 = cut_line(F, cx, cy, rxm, rym, th_top, inner=(rxi, ryi))
    p1, d1 = cut_line(F, cx, cy, rxm, rym, th_bot, inner=(rxi, ryi))
    return arc_stroke(F, outer, inner, (0, p0, d0), (3, p1, d1))


@glyph("c", 0x63)
def g_c(F):
    g = new("c")
    W = o_w(F) * F.c_w
    g.add(c_like(F, W, F.c_th, F.c_thb))
    g.lsb = sb(F, "O")
    g.rsb = sb(F, "O") * F.get("c_rsb", 0.85)
    return g


@glyph("e", 0x65)
def g_e(F):
    g = new("e")
    W = o_w(F) * F.e_w
    S, T = F.S, F.T * F.get("e_T", 1.0)
    cx, cy, rxo, ryo, rxi, ryi = o_ring(F, W, T=T)
    outer, inner = ring(F, cx, cy, rxo, ryo, rxi, ryi)
    Tb = T * F.get("e_bar", 0.92)
    yb = cy - Tb * F.get("e_bar_pos", 0.42)
    rxm, rym = (rxo + rxi) / 2, (ryo + ryi) / 2
    p1, d1 = cut_line(F, cx, cy, rxm, rym, F.e_th, inner=(rxi, ryi))
    g.add(arc_stroke(F, outer, inner, (3, (cx, yb), H), (3, p1, d1), cap0=False))
    g.add(rect(cx - rxi - S * 0.5, yb, cx + rxi, yb + Tb))
    g.lsb = sb(F, "O")
    g.rsb = sb(F, "O") * F.get("e_rsb", 0.92)
    return g


# ---------------------------------------------------------------- bowl + stem

def b_shape(F, up=True, mirror=False):
    """Stem on the left, bowl on the right (mirror=True puts the stem on the right).
    up=True: b/d, False: p/q."""
    S, xh, T, o = F.S, F.xh, F.T, F.o
    W = o_w(F) * F.get("b_w", 1.0)
    g = Glyph("b")
    kt, kb = ("crotch", "spur") if up else ("notch", "crotch_b")
    add_bowl(g, bowl(F, 0, S, W, xh + o, -o, T, T, kt, kb, Sside=S * F.get("o_sx", 1.03)))
    if mirror:
        g.mirror_x(0)
        xs0, xs1 = -S, 0
    else:
        xs0, xs1 = 0, S
    if up:
        g.add(vstem(F, xs0, xs1, 0, F.asc, "R" if mirror else False, "L"))
    else:
        g.add(vstem(F, xs0, xs1, F.desc, xh, "B", False if mirror else "L"))
    return g


@glyph("b", 0x62)
def g_b(F):
    g = b_shape(F, True)
    g.name = "b"
    g.lsb, g.rsb = sb(F, "S"), sb(F, "O")
    return g


@glyph("d", 0x64)
def g_d(F):
    g = b_shape(F, True, True)
    g.name = "d"
    g.lsb, g.rsb = sb(F, "O"), sb(F, "S")
    return g


@glyph("p", 0x70)
def g_p(F):
    g = b_shape(F, False)
    g.name = "p"
    g.lsb, g.rsb = sb(F, "S"), sb(F, "O")
    return g


@glyph("q", 0x71)
def g_q(F):
    g = b_shape(F, False, True)
    g.name = "q"
    g.lsb, g.rsb = sb(F, "O"), sb(F, "S")
    return g


# ---------------------------------------------------------------- stems & dots

def dot_size(F):
    return F.dotw


@glyph("dotlessi", 0x131)
def g_dotlessi(F):
    g = new("dotlessi")
    g.add(vstem(F, 0, F.S, 0, F.xh, "B", "L"))
    g.anchors["top"] = (F.S / 2, F.xh)
    g.lsb = g.rsb = sb(F, "S")
    return g


@glyph("i", 0x69)
def g_i(F):
    g = g_dotlessi(F)
    g.name = "i"
    w = dot_size(F)
    cy = F.i_dot_y + w / 2
    g.add(dot_shape(F, F.S / 2, cy, w))
    g.lsb = g.rsb = sb(F, "S") - max(0, (w - F.S) / 2)
    return g


@glyph("l", 0x6C)
def g_l(F):
    g = new("l")
    if F.l_tail:
        from parts import hook_ring
        S, T, o = F.S, F.T, F.o
        rxo, ryo = F.l_rx, F.l_ry
        cx, cy = rxo, -o + ryo
        outer, inner, rxm, rym, rxi, ryi = hook_ring(F, cx, cy, rxo, ryo, S, T * F.get("t_hT", 1.0))
        p1, d1 = cut_line(F, cx, cy, rxm, rym, F.l_th, F.get("hook_term"), inner=(rxi, ryi))
        g.add(arc_stroke(F, outer, inner, (2, 0.0, None), (3, p1, d1), cap0=False))
        g.add(vstem(F, 0, S, cy, F.asc, False, True))
        g.lsb, g.rsb = sb(F, "S"), sb(F, "N") * 2
        return g
    g.add(vstem(F, 0, F.S, 0, F.asc, "B", "L"))
    g.lsb = g.rsb = sb(F, "S")
    return g


def j_hook(F, x0, ytop):
    """Stem x0..x0+S from ytop down into a hook curling left at the descender."""
    S, T = F.S, F.T
    rxo = F.j_rx
    ryo = F.j_ry
    bot = F.desc - F.o
    cx = x0 + S - rxo
    cy = bot + ryo
    rxi, ryi = rxo - S, ryo - T
    outer, inner = ring(F, cx, cy, rxo, ryo, rxi, ryi)
    rxm, rym = (rxo + rxi) / 2, (ryo + ryi) / 2
    p0, d0 = cut_line(F, cx, cy, rxm, rym, F.j_th, F.get('hook_term'), inner=(rxi, ryi))
    g = []
    g.append(arc_stroke(F, outer, inner, (2, p0, d0), (3, 1.0, None), cap1=False))
    g.append(vstem(F, x0, x0 + S, cy, ytop, False, "L"))
    return g


@glyph("dotlessj", 0x237)
def g_dotlessj(F):
    g = new("dotlessj")
    x0 = F.j_rx - F.S + 0
    g.add(j_hook(F, x0, F.xh))
    # the stem keeps the i's side bearing; the hook hangs into the left
    hook = 2 * F.j_rx - F.S
    g.lsb = sb(F, "S") * 0.6 - hook * 0.5
    g.rsb = sb(F, "S")
    return g


@glyph("j", 0x6A)
def g_j(F):
    g = g_dotlessj(F)
    g.name = "j"
    w = dot_size(F)
    from glyphs import finish
    finish(g)
    xs = g.width - sb(F, "S") - F.S / 2
    g.lsb = None
    g.add(dot_shape(F, xs, F.i_dot_y + w / 2, w))
    return g


# ---------------------------------------------------------------- a

def a_double(F, W=None):
    from parts import hook_ring
    S, T, xh, o = F.S, F.T, F.xh, F.o
    W = n_w(F) * F.a_w if W is None else W
    parts = []
    # top hook: ring whose right side is the stem
    ryo = (xh + o) - xh * F.a_hy
    rxo = W * F.a_hx
    cx, cy = W - rxo, xh + o - ryo
    outer, inner, rxm, rym, rxi, ryi = hook_ring(F, cx, cy, rxo, ryo, S, T * F.get("a_tT", 1.0))
    p0, d0 = cut_line(F, cx, cy, rxm, rym, F.a_th, inner=(rxi, ryi))
    parts.append(arc_stroke(F, outer, inner, (0, 0.0, None), (1, p0, d0), cap0=False))
    parts.append(vstem(F, W - S, W, 0, cy, "R", False))
    # bowl, built with the stem on the left then mirrored
    bt = xh * F.a_bt
    Tb = T * F.get("a_bT", 0.95)
    g = Glyph("tmp")
    add_bowl(g, bowl(F, 0, S, W * F.get("a_bw", 1.0), bt, -o, Tb, T * F.get("a_bbT", 1.0), "abowl", "spur", h=bt,
                     Sside=S * F.get("a_bs", 1.0)))
    g.mirror_x(W / 2)
    return parts, g


def a_single(F, W=None):
    S, xh, T, o = F.S, F.xh, F.T, F.o
    W = o_w(F) * F.get("a1_w", 1.0) if W is None else W
    g = Glyph("tmp")
    g.add(vstem(F, 0, S, 0, xh, "L", True))
    add_bowl(g, bowl(F, 0, S, W, xh + o, -o, T, T, "notch", "spur", Sside=S * F.get("o_sx", 1.03)))
    g.mirror_x(W / 2)
    return g


@glyph("a", 0x61)
def g_a(F):
    g = new("a")
    if F.a_story == 2:
        parts, bw = a_double(F)
        g.add(parts)
        g.paths.extend(bw.paths)
        g.lsb = sb(F, "O") * F.get("a_lsb", 1.0)
        g.rsb = sb(F, "S")
    else:
        g.paths.extend(a_single(F).paths)
        g.lsb, g.rsb = sb(F, "O"), sb(F, "S")
    return g


# ---------------------------------------------------------------- g

def g_hook(F, xr, W, top_stem):
    """Descender hook of g: stem on the right (xr-S..xr) curling left."""
    from parts import hook_ring
    S, T = F.S, F.T * F.get("g_hT", 0.96)
    bot = F.desc - F.o
    ryo = F.g_hy
    rxo = W * F.g_hx
    cx, cy = xr - rxo, bot + ryo
    outer, inner, rxm, rym, rxi, ryi = hook_ring(F, cx, cy, rxo, ryo, S, T)
    p0, d0 = cut_line(F, cx, cy, rxm, rym, F.g_th, F.get('hook_term'), inner=(rxi, ryi))
    return [arc_stroke(F, outer, inner, (2, p0, d0), (3, 1.0, None), cap1=False),
            vstem(F, xr - S, xr, cy, top_stem, False, "R")]


@glyph("g", 0x67)
def g_g(F):
    g = new("g")
    S, xh, T, o = F.S, F.xh, F.T, F.o
    W = o_w(F) * F.get("b_w", 1.0)
    tmp = Glyph("tmp")
    add_bowl(tmp, bowl(F, 0, S, W, xh + o, F.get("g_bb", -o), T, T, "notch", "gspur",
                       Sside=S * F.get("o_sx", 1.03)))
    tmp.mirror_x(W / 2)
    g.paths.extend(tmp.paths)
    g.add(g_hook(F, W, W, xh))
    g.lsb, g.rsb = sb(F, "O"), sb(F, "S")
    return g


# ---------------------------------------------------------------- f t

@glyph("f", 0x66)
def g_f(F):
    from parts import hook_ring
    g = new("f")
    S, T, xh = F.S, F.T, F.xh
    top = F.asc + F.o
    rxo, ryo = F.f_rx, F.f_ry
    x0 = 0.0
    cx, cy = x0 + rxo, top - ryo
    outer, inner, rxm, rym, rxi, ryi = hook_ring(F, cx, cy, rxo, ryo, S, T * F.get("f_hT", 1.0))
    p0, d0 = cut_line(F, cx, cy, rxm, rym, F.f_th, F.get('hook_term'), inner=(rxi, ryi))
    g.add(arc_stroke(F, outer, inner, (0, p0, d0), (1, 1.0, None), cap1=False))
    g.add(vstem(F, x0, x0 + S, 0, cy, "B", False))
    TB = F.get("TB", T)
    g.add(hstem(F, x0 - F.f_cl, x0 + S + F.f_cr, xh - TB, xh, True, True))
    g.lsb = sb(F, "N")
    g.rsb = F.get("f_rsb", -sb(F, "S") * 0.1)
    return g


@glyph("t", 0x74)
def g_t(F):
    from parts import hook_ring
    g = new("t")
    S, T, xh, o = F.S, F.T, F.xh, F.o
    rxo, ryo = F.t_rx, F.t_ry
    x0 = 0.0
    cx, cy = x0 + rxo, -o + ryo
    outer, inner, rxm, rym, rxi, ryi = hook_ring(F, cx, cy, rxo, ryo, S, T * F.get("t_hT", 1.0))
    p1, d1 = cut_line(F, cx, cy, rxm, rym, F.t_th, F.get('hook_term'), inner=(rxi, ryi))
    g.add(arc_stroke(F, outer, inner, (2, 0.0, None), (3, p1, d1), cap0=False))
    ttop = F.t_top
    if F.t_top_style == "slant":
        g.add(Path((x0, cy)).L((x0 + S, cy)).L((x0 + S, ttop)).L((x0, ttop - S * F.get("t_slant", 0.5))))
    else:
        g.add(vstem(F, x0, x0 + S, cy, ttop, False, True))
    TB = F.get("TB", T)
    g.add(hstem(F, x0 - F.t_cl, x0 + S + F.t_cr, xh - TB, xh, True, True))
    g.lsb = sb(F, "N")
    g.rsb = sb(F, "N")
    return g


# ---------------------------------------------------------------- k v w x y z

def diag_t(F):
    return F.S * F.get("dg", 0.92)


@glyph("k", 0x6B)
def g_k(F):
    from parts import dquad, slant_w, stroke
    g = new("k")
    S, xh = F.S, F.xh
    t = diag_t(F)
    gap = S * F.get("k_gap", (0.9, 0.62, 0.5))[F.mi] if not isinstance(F.get("k_gap"), (int, float)) else S * F.k_gap
    if F.get("serif"):
        gap = max(gap, 2 * F.sf_e * F.get("sf_de", 0.9) + S * 0.35)
    W = S + F.n_c * F.k_w
    yj = xh * F.k_j
    ax0, ay0 = S * 0.5, yj - xh * 0.06
    ta = t * F.get("k_arm", 0.94) * F.get("diag_c", 1.0)
    for _ in range(3):
        wa = slant_w(ta, W - ax0, xh - ay0)
        tc = (W - wa / 2, xh)
        lx0 = lerp(ax0, tc[0], F.k_lj)
        ly0 = lerp(ay0, xh, F.k_lj)
        wl = slant_w(t, W - lx0, ly0)
        need = S + gap + wl
        if W >= need - 0.5:
            break
        W = need
    g.add(vstem(F, 0, S, 0, F.asc, "B", "L"))
    if is_round(F):
        tr = min(t, S * 0.9)
        A = (S * 0.5, yj - 0.1 * xh)
        B = (W - tr / 2, xh - tr / 2)
        g.add(stroke(F, A, B, tr, False, True))
        L0 = lerp(A, B, F.k_lj)
        g.add(stroke(F, L0, (W - tr / 2, tr / 2), tr, False, True))
    else:
        dd = norm(sub(tc, (ax0, ay0)))
        nn = (-dd[1] * ta / 2, dd[0] * ta / 2)
        g.add(Path((ax0 + nn[0], ay0 + nn[1])).L((ax0 - nn[0], ay0 - nn[1]))
              .L((tc[0] + wa / 2, xh)).L((tc[0] - wa / 2, xh)))
        g.add(dquad((W - wl / 2, 0), (lx0, ly0), wl))
        from parts import hslab
        g.add(hslab(F, tc[0] - wa / 2, tc[0] + wa / 2, xh, False))
        g.add(hslab(F, W - wl, W, 0, True))
    g.lsb, g.rsb = sb(F, "S"), sb(F, "D")
    return g


@glyph("v", 0x76)
def g_v(F):
    from parts import vee
    g = new("v")
    W = F.n_c * F.v_w + 2 * F.S
    g.add(vee(F, 0, W, F.xh, 0, diag_t(F), serifs=True))
    g.lsb = g.rsb = sb(F, "D")
    return g


@glyph("w", 0x77)
def g_w(F):
    from parts import vee, slant_w
    g = new("w")
    W1 = F.n_c * F.w_w + 2 * F.S
    t = diag_t(F) * F.get("w_t", 0.94)
    a = F.S * F.get("v_apex", 0.55) * 0.9
    wx = slant_w(t, W1 / 2 - a / 2, F.xh)
    g.add(vee(F, 0, W1, F.xh, 0, t, apex=a, serifs=True))
    off = W1 - wx if not is_round(F) else W1 - t
    g.add(vee(F, off, W1, F.xh, 0, t, apex=a, serifs=True))
    g.lsb = g.rsb = sb(F, "D")
    return g


@glyph("x", 0x78)
def g_x(F):
    from parts import dquad, slant_w, stroke
    g = new("x")
    W = F.n_c * F.x_w + 2 * F.S
    t = diag_t(F)
    if is_round(F):
        g.add(stroke(F, (t / 2, F.xh - t / 2), (W - t / 2, t / 2), t, True, True))
        g.add(stroke(F, (W - t / 2, F.xh - t / 2), (t / 2, t / 2), t, True, True))
    else:
        w = slant_w(t, W, F.xh)
        wt = w * F.get("x_top", 1.0)
        g.add(dquad((W - w / 2, 0), (wt / 2, F.xh), w, wt))
        w2 = w * F.get("diag_c", 1.0)
        g.add(dquad((w2 / 2, 0), (W - w2 / 2, F.xh), w2, w2 * F.get("x_top", 1.0)))
        from parts import hslab
        g.add(hslab(F, 0, wt, F.xh, False), hslab(F, W - w2, W, F.xh, False),
              hslab(F, W - w, W, 0, True), hslab(F, 0, w2, 0, True))
    g.lsb = g.rsb = sb(F, "D")
    return g


@glyph("y", 0x79)
def g_y(F):
    from parts import dquad, slant_w, stroke
    g = new("y")
    W = F.n_c * F.v_w + 2 * F.S
    t = diag_t(F)
    xh, desc = F.xh, F.desc
    a = F.S * F.get("v_apex", 0.55)
    # right stroke from the top right down through the baseline to the descender
    xm = W / 2 + F.get("y_shift", 0.08) * W  # apex center at baseline
    wx = slant_w(t, W - xm, xh)
    xr_top = W - wx / 2
    slope = (xr_top - xm) / xh
    xb = xm - slope * (0 - desc)
    if is_round(F):
        g.add(stroke(F, (W - t / 2, xh - t / 2), (xb + t * 0.2, desc + t / 2), t, True, True))
        g.add(stroke(F, (t / 2, xh - t / 2), (xm, t * 0.5), t, True, False))
    elif F.y_tail == "curved":
        from core import intersect
        g.add(dquad((xm, 0), (xr_top, xh), wx))
        # curved tail: continue down then hook left
        g.add(y_curved_tail(F, xm, wx, slope))
        wl = slant_w(t, xm - wx / 2, xh)
        g.add(dquad((xm, 0), (wl / 2, xh), wl))
    else:
        wxr = wx * F.get("diag_c", 1.0)
        g.add(dquad((xb, desc), (xr_top, xh), wxr))
        wl = slant_w(t, xm, xh)
        g.add(dquad((xm, 0), (wl / 2, xh), wl))
        from parts import hslab
        g.add(hslab(F, 0, wl, xh, False), hslab(F, xr_top - wxr / 2, xr_top + wxr / 2, xh, False),
              hslab(F, xb - wxr / 2, xb + wxr / 2, desc, True) if F.get("serif") == "slab" else None)
    g.lsb = g.rsb = sb(F, "D")
    return g


def y_curved_tail(F, xm, wx, slope):
    desc = F.desc
    T = F.T
    # right edge of the stroke continues down, bends into a short leftward tail
    xr0 = xm + wx / 2
    xl0 = xm - wx / 2
    yb = desc - F.o
    yk = desc + F.get("y_tk", 0.42) * (0 - desc)
    xr_k = xr0 - slope * (0 - yk)
    xl_k = xl0 - slope * (0 - yk)
    xend = xl_k - F.get("y_tail_len", 0.9) * wx
    p = Path((xl0, 1.0)).L((xr0, 1.0)).L((xr_k, yk))
    p.T((xr_k - wx * 1.0, yb), (-slope, -1), H, 0.6)
    p.L((xend, yb)).L((xend, yb + T))
    p.T((xl_k, yk + T * 0.6), H, (slope, 1), 0.6)
    return p


@glyph("z", 0x7A)
def g_z(F):
    from parts import dquad, slant_w, stroke
    g = new("z")
    W = F.n_c * F.z_w + 2 * F.S * 0.7
    T, xh = F.get("TB", F.T) * F.get("z_T", 1.0), F.xh
    t = diag_t(F) * F.get("z_t", 1.0)
    if is_round(F):
        r = T / 2
        g.add(hstem(F, 0, W, xh - T, xh, True, True))
        g.add(hstem(F, 0, W, 0, T, True, True))
        g.add(stroke(F, (W - r, xh - r), (r, r), t, False, False))
    else:
        g.add(rect(F.get("z_tl", 0.06) * W, xh - T, W, xh))
        g.add(rect(0, 0, W, T))
        from parts import zdiag
        w = slant_w(t, W, xh - 2 * T)
        g.add(zdiag(0, W, T, xh - T, w))
    g.lsb = g.rsb = sb(F, "D") + F.get("z_sb", 10)
    return g


# ---------------------------------------------------------------- s

def s_shape(F, W, h, o, S, T, top_th, bot_th, k=None, ki=None, ys=0.0):
    """S-curve from the top-right terminal to the bottom-left terminal."""
    from core import quad_cubics, reverse_cubic, split, line_param
    k = F.k if k is None else k
    ki = F.ki if ki is None else ki
    Ss = S * F.get("s_S", 1.0)
    Tt = T * F.get("s_T", 1.0)
    cyu = h * F.s_cyu
    cyl = h * F.s_cyl
    rxu = W * F.s_rxu / 2
    rxl = W / 2
    cxu = W * F.get("s_xu", 0.5) + W * 0.01
    cxl = W / 2
    ryou = h + o - cyu
    ryol = cyl + o
    Uo = quad_cubics(cxu, cyu, rxu, ryou, k)
    Ui = quad_cubics(cxu, cyu, rxu - Ss, ryou - Tt, ki)
    Lo = quad_cubics(cxl, cyl, rxl, ryol, k)
    Li = quad_cubics(cxl, cyl, rxl - Ss, ryol - Tt, ki)
    # terminals
    pt, dt = cut_line(F, cxu, cyu, rxu - Ss / 2, ryou - Tt / 2, top_th, inner=(rxu - Ss, ryou - Tt))
    pb, db = cut_line(F, cxl, cyl, rxl - Ss / 2, ryol - Tt / 2, bot_th, inner=(rxl - Ss, ryol - Tt))
    tuo = line_param(Uo[0], pt, dt)
    tui = line_param(Ui[0], pt, dt)
    tlo = line_param(Lo[2], pb, db)
    tli = line_param(Li[2], pb, db)
    # spine
    A3 = Uo[1][3]
    B5 = Ui[1][3]
    A5 = Li[0][0]
    B3 = Lo[0][0]
    cs = (W * F.get("s_xc", 0.5), h * F.get("s_yc", 0.5) + ys)
    ang = math.atan2(cyl - cyu, (W - Ss / 2) - (A3[0] + Ss / 2)) * F.s_flat
    d = (math.cos(ang), math.sin(ang))
    nrm = (-d[1], d[0])
    ts = Ss * F.get("s_spine", 0.96)
    A4 = (cs[0] - nrm[0] * ts / 2, cs[1] - nrm[1] * ts / 2)
    B4 = (cs[0] + nrm[0] * ts / 2, cs[1] + nrm[1] * ts / 2)
    ks = F.get("s_ks", 0.62)
    a = split(*Uo[0], tuo)[1]
    p = Path(a[0])
    p.seg_cubic(a)
    p.seg_cubic(Uo[1])
    p.T(A4, V, d, ks)
    p.T(A5, d, V, ks)
    p.seg_cubic(reverse_cubic(Li[3]))
    bi = split(*Li[2], tli)[1]
    p.seg_cubic(reverse_cubic(bi))
    bo = split(*Lo[2], tlo)[1]
    if is_round(F):
        out = sub(bi[0], bi[1])
        for c in cap_round(bi[0], bo[0], mul(sub(bo[1], bo[0]), -1)):
            p.seg_cubic(c)
    else:
        p.L(bo[0])
    p.seg_cubic(bo)
    p.seg_cubic(Lo[3])
    p.T(B4, V, d, ks)
    p.T(B5, d, V, ks)
    p.seg_cubic(reverse_cubic(Ui[1]))
    ui = split(*Ui[0], tui)[1]
    p.seg_cubic(reverse_cubic(ui))
    if is_round(F):
        for c in cap_round(ui[0], a[0], sub(ui[0], ui[1]) if False else sub(a[0], a[1])):
            p.seg_cubic(c)
    return p


@glyph("s", 0x73)
def g_s(F):
    g = new("s")
    W = n_w(F) * F.s_w
    g.add(s_shape(F, W, F.xh, F.o, F.S, F.T, F.s_tth, F.s_bth))
    g.lsb = g.rsb = sb(F, "O") * F.get("s_sb", 0.92)
    return g
