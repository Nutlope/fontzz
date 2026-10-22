"""Reusable stroke constructions: stems, shoulders, bowls, ring arcs, terminals."""
import math
from core import (Path, rect, oval, quad_cubics, sub_cubics, reverse_cubic, cap_round,
                  line_param, split, bez, H, V, D, add, sub, mul, lerp, norm, perp, dot,
                  tension_handles)

ROUND = "round"


def is_round(F):
    return F.term == ROUND


# ---------------------------------------------------------------- stems

SERIF_FLAGS = ("L", "R", "B")
BEAK_FLAGS = ("U", "D", "B")


def has_serifs(F):
    """Serifs for the glyph being drawn. serif_only limits them to some glyphs
    (monospace i, l, r and friends in an otherwise sans family)."""
    if not F.get("serif"):
        return False
    only = F.get("serif_only")
    return not only or F.__dict__.get("cur") in only


def ring_pt(cx, cy, rx, ry, th):
    a = math.radians(th)
    return (cx + rx * math.cos(a), cy + ry * math.sin(a))


def ball(F, p, toward, edge=None):
    """Didone ball terminal at the stroke end p, pulled toward the inside of the
    curve (point `toward`) so its outer edge stays near the outline."""
    if not F.get("ball"):
        return []
    r = F.S * F.ball / 2
    edge = F.T / 2 if edge is None else edge
    v = (toward[0] - p[0], toward[1] - p[1])
    n = math.hypot(*v) or 1.0
    c = (p[0] + v[0] / n * (r - edge), p[1] + v[1] / n * (r - edge))
    return [oval(c[0], c[1], r, r, 0.5523)]


def rrect(x0, y0, x1, y1, rl, rr, k=0.5523):
    """Rectangle whose left and/or right ends are rounded with radius rl / rr."""
    p = Path((x0 + rl, y0)).L((x1 - rr, y0))
    if rr:
        p.C((x1 - rr + rr * k, y0), (x1, y0 + rr - rr * k), (x1, y0 + rr))
        p.L((x1, y1 - rr))
        p.C((x1, y1 - rr + rr * k), (x1 - rr + rr * k, y1), (x1 - rr, y1))
    else:
        p.L((x1, y1))
    p.L((x0 + rl, y1))
    if rl:
        p.C((x0 + rl - rl * k, y1), (x0, y1 - rl + rl * k), (x0, y1 - rl))
        p.L((x0, y0 + rl))
        p.C((x0, y0 + rl - rl * k), (x0 + rl - rl * k, y0), (x0 + rl, y0))
    else:
        p.L((x0, y0))
    return p


def bracket(cx, cy, dx, dy, br, k=0.56):
    """Concave fillet filling the corner at (cx, cy); dx/dy (+1/-1) point along the
    serif (x) and up the stem (y)."""
    a = (cx + dx * br, cy)
    b = (cx, cy + dy * br)
    c = (cx, cy)
    p = Path(c).L(a)
    p.C(lerp(a, c, k), lerp(b, c, k), b)
    return p


def stem_serifs(F, x0, x1, y, flag, top):
    """Serif shapes for a vertical stem end at height y (top=True for the upper end)."""
    if not has_serifs(F) or flag not in SERIF_FLAGS or (not top and F.get("sf_top_only")):
        return []
    ts, e = F.sf_t, F.sf_e
    br = min(F.get("sf_br", 0), e * 0.92)
    left = flag in ("L", "B")
    right = flag in ("R", "B")
    out = []
    sg = -1 if top else 1          # direction from the end into the stem
    yi = y + sg * ts               # inner edge of the serif
    if top and flag == "L" and F.get("sf_wedge"):
        slope = e * F.sf_wedge
        out.append(Path((x0 - e, y - slope - ts)).L((x1, y - slope - ts)).L((x1, y)).L((x0 - e, y - slope)))
        yi = y - slope - ts
        if br > 0:
            out.append(bracket(x0, yi, -1, -1, br))
        return out
    xl = x0 - e if left else x0
    xr = x1 + e if right else x1
    style = F.get("serif")
    if style == "wedge":
        # thin foot plus straight triangles running up the stem (Latin style)
        h = e * F.get("sf_wh", 1.0)
        out.append(rect(xl, min(y, yi), xr, max(y, yi)))
        if left:
            out.append(Path((x0 - e, yi)).L((x0 + 1, yi)).L((x0 + 1, yi + sg * h)))
        if right:
            out.append(Path((x1 + e, yi)).L((x1 - 1, yi)).L((x1 - 1, yi + sg * h)))
        return out
    if style == "soft":
        r = ts / 2 * F.get("sf_round", 1.0)
        br = min(br, max(0.0, e - r))   # keep the fillet clear of the rounded tip
        out.append(rrect(xl, min(y, yi), xr, max(y, yi), r if left else 0, r if right else 0))
    else:
        out.append(rect(xl, min(y, yi), xr, max(y, yi)))
    if br > 0:
        if left:
            out.append(bracket(x0, yi, -1, sg, br))
        if right:
            out.append(bracket(x1, yi, 1, sg, br))
    return out


def vstem(F, x0, x1, y0, y1, cap0=False, cap1=False):
    """Vertical stem from y0 (bottom) to y1 (top).

    cap flags: False (joined), True (free end: round cap in rounded families),
    or "L"/"R"/"B" (free end that also takes a serif on the left, right or both
    sides in serif families).
    """
    if x0 > x1:
        x0, x1 = x1, x0
    extra = stem_serifs(F, x0, x1, y0, cap0, False) + stem_serifs(F, x0, x1, y1, cap1, True)
    if extra and is_round(F):
        # a serif closes the end, so the stem itself stays flat there
        cap0 = cap0 and cap0 not in SERIF_FLAGS
        cap1 = cap1 and cap1 not in SERIF_FLAGS
        if not (cap0 or cap1):
            return [rect(x0, y0, x1, y1)] + extra
    if not is_round(F):
        body = flared(x0, y0, x1, y1, F.flare, bool(cap0), bool(cap1)) if F.get("flare") else rect(x0, y0, x1, y1)
        return [body] + extra if extra else body
    r = (x1 - x0) / 2
    k = 0.5523
    cx = (x0 + x1) / 2
    p = Path((x1, y0 + (r if cap0 else 0)))
    if cap1:
        p.L((x1, y1 - r))
        p.C((x1, y1 - r + r * k), (cx + r * k, y1), (cx, y1))
        p.C((cx - r * k, y1), (x0, y1 - r + r * k), (x0, y1 - r))
    else:
        p.L((x1, y1)).L((x0, y1))
    if cap0:
        p.L((x0, y0 + r))
        p.C((x0, y0 + r - r * k), (cx - r * k, y0), (cx, y0))
        p.C((cx + r * k, y0), (x1, y0 + r - r * k), (x1, y0 + r))
    else:
        p.L((x0, y0)).L((x1, y0))
    return p


def bar_beak(F, x_end, y0, y1, flag, at_right):
    """Vertical serif at the free end of a horizontal arm."""
    if not has_serifs(F) or flag not in BEAK_FLAGS:
        return []
    bt, bh = F.sf_vt, F.sf_vh
    xa, xb = (x_end - bt, x_end) if at_right else (x_end, x_end + bt)
    lo = y0 - (bh if flag in ("D", "B") else 0)
    hi = y1 + (bh if flag in ("U", "B") else 0)
    out = [rect(xa, lo, xb, hi)]
    br = min(F.get("sf_br", 0) * 0.7, bh * 0.9)
    if br > 0:
        dx = -1 if at_right else 1
        xin = xa if at_right else xb
        if flag in ("D", "B"):
            out.append(bracket(xin, y0, dx, -1, br) if False else bracket_v(xin, y0, dx, -1, br))
        if flag in ("U", "B"):
            out.append(bracket_v(xin, y1, dx, 1, br))
    return out


def bracket_v(cx, cy, dx, dy, br, k=0.56):
    """Fillet for a beak: corner where the beak's inner side meets the bar."""
    a = (cx + dx * br, cy)
    b = (cx, cy + dy * br)
    c = (cx, cy)
    p = Path(c).L(a)
    p.C(lerp(a, c, k), lerp(b, c, k), b)
    return p


def flared(x0, y0, x1, y1, f, end0=True, end1=True):
    """Glyphic stem: straight, widening into a soft flare at each free end
    (Optima style). Joined ends stay square so bowls and arches meet cleanly."""
    h = y1 - y0
    w = x1 - x0
    L = min(h * 0.32, w * 2.6)
    d0 = w * f if end0 else 0.0
    d1 = w * f if end1 else 0.0
    p = Path((x0 - d0, y0)).L((x1 + d0, y0))
    p.C((x1 + d0 * 0.45, y0 + L * 0.22), (x1, y0 + L * 0.5), (x1, y0 + L))
    p.L((x1, y1 - L))
    p.C((x1, y1 - L * 0.5), (x1 + d1 * 0.45, y1 - L * 0.22), (x1 + d1, y1))
    p.L((x0 - d1, y1))
    p.C((x0 - d1 * 0.45, y1 - L * 0.22), (x0, y1 - L * 0.5), (x0, y1 - L))
    p.L((x0, y0 + L))
    p.C((x0, y0 + L * 0.5), (x0 - d0 * 0.45, y0 + L * 0.22), (x0 - d0, y0))
    return p


def hstem(F, x0, x1, y0, y1, cap0=False, cap1=False):
    """Horizontal bar from x0 (left) to x1 (right). Flags "U"/"D"/"B" add beak
    serifs (up, down, both) at that end in serif families."""
    if y0 > y1:
        y0, y1 = y1, y0
    extra = bar_beak(F, x0, y0, y1, cap0, False) + bar_beak(F, x1, y0, y1, cap1, True)
    if not is_round(F):
        return [rect(x0, y0, x1, y1)] + extra if extra else rect(x0, y0, x1, y1)
    r = (y1 - y0) / 2
    k = 0.5523
    cy = (y0 + y1) / 2
    p = Path((x0 + (r if cap0 else 0), y0))
    if cap1:
        p.L((x1 - r, y0))
        p.C((x1 - r + r * k, y0), (x1, cy - r * k), (x1, cy))
        p.C((x1, cy + r * k), (x1 - r + r * k, y1), (x1 - r, y1))
    else:
        p.L((x1, y0)).L((x1, y1))
    if cap0:
        p.L((x0 + r, y1))
        p.C((x0 + r - r * k, y1), (x0, cy + r * k), (x0, cy))
        p.C((x0, cy - r * k), (x0 + r - r * k, y0), (x0 + r, y0))
    else:
        p.L((x0, y1)).L((x0, y0))
    return p


def hslab(F, xl, xr, y, up):
    """Horizontal serif for a diagonal stroke end spanning xl..xr at height y.
    up=True puts the serif above y (bottom ends), False below (top ends)."""
    if not has_serifs(F) or (up and F.get("sf_top_only")):
        return []
    ts, e = F.sf_t, F.sf_e * F.get("sf_de", 0.9)
    y0, y1 = (y, y + ts) if up else (y - ts, y)
    if F.get("serif") == "soft":
        r = ts / 2 * F.get("sf_round", 1.0)
        return [rrect(xl - e, y0, xr + e, y1, r, r)]
    return [rect(xl - e, y0, xr + e, y1)]


def stroke(F, a, b, w, cap0=False, cap1=False):
    """Straight stroke of width w (measured perpendicular) between points a and b."""
    if is_round(F):
        cap0 = cap1 = True
    d = norm(sub(b, a))
    n = mul(perp(d), w / 2)
    p0 = add(a, n)
    p1 = add(b, n)
    p2 = sub(b, n)
    p3 = sub(a, n)
    p = Path(p3)
    p.L(p2)
    if cap1 and is_round(F):
        for c in cap_round(p2, p1, d):
            p.seg_cubic(c)
    else:
        p.L(p1)
    p.L(p0)
    if cap0 and is_round(F):
        for c in cap_round(p0, p3, mul(d, -1)):
            p.seg_cubic(c)
    return p


def diag(F, bx0, bx1, by, tx0, tx1, ty):
    """Quadrilateral stroke defined by its bottom edge (bx0..bx1 at by) and top edge."""
    return Path((bx0, by)).L((bx1, by)).L((tx1, ty)).L((tx0, ty))


def dot_shape(F, cx, cy, w, h=None):
    h = w if h is None else h
    if F.dot == "round" or is_round(F):
        return oval(cx, cy, w / 2, h / 2, 0.5523 if F.dot == "round" or is_round(F) else F.k)
    if F.dot == "squircle":
        return oval(cx, cy, w / 2, h / 2, 0.80)
    return rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)


# ---------------------------------------------------------------- terminal cut lines

def cut_line(F, cx, cy, rx, ry, theta, kind=None, inner=None):
    """Cut line through the point at angle theta on the mid ellipse.

    Returns (point, direction). The family's terminal style picks the angle.
    """
    th = math.radians(theta)
    p = (cx + rx * math.cos(th), cy + ry * math.sin(th))
    kind = kind or F.term
    if kind == "flat":
        d = H
        if inner is not None:
            p = (cx + inner[0] * math.cos(th), cy + inner[1] * math.sin(th))
    elif kind == "vertical":
        d = V
        if inner is not None:
            p = (cx + inner[0] * math.cos(th), cy + inner[1] * math.sin(th))
    elif kind in ("radial", ROUND):
        # blend of the true radial line (robust) and the ellipse normal (optical)
        tx, ty = -rx * math.sin(th), ry * math.cos(th)
        nrm = norm((ty, -tx))
        rad = norm((math.cos(th) * rx, math.sin(th) * ry))
        d = norm(lerp(rad, nrm, F.get("radial_mix", 0.5)))
    elif kind == "angled":
        tx, ty = -rx * math.sin(th), ry * math.cos(th)
        an = math.degrees(math.atan2(-tx, ty)) % 180.0
        a = an + (90.0 - an) * F.get("term_mix", 0.5)
        d = D(a)
        if inner is not None:
            pin = (cx + inner[0] * math.cos(th), cy + inner[1] * math.sin(th))
            p = lerp(p, pin, 0.85)
    else:
        raise ValueError(kind)
    return p, d


def find_cut(cubics, q, p, d):
    return (q, line_param(cubics[q], p, d))


def arc_stroke(F, outer, inner, start, end, cap0=True, cap1=True):
    """Stroke along a ring between two cuts, CCW on the outer contour.

    outer/inner: 4-cubic chains (from quad_cubics). start/end: (quadrant, p, d)
    cut lines or (quadrant, t, None) explicit parameters for outer & inner alike.
    cap flags mark free terminals (round caps in rounded families).
    """
    def resolve(cubics, c, which):
        q, a, b = c
        if b is None:
            return (q, a)
        if b == "tt":
            return (q, a[which])
        return (q, line_param(cubics[q], a, b))

    so, eo = resolve(outer, start, 0), resolve(outer, end, 0)
    si, ei = resolve(inner, start, 1), resolve(inner, end, 1)
    oc = sub_cubics(outer, so, eo)
    ic = sub_cubics(inner, si, ei)
    path = Path(oc[0][0])
    for c in oc:
        path.seg_cubic(c)
    o_end = oc[-1][3]
    i_end = ic[-1][3]
    if cap1 and is_round(F):
        last = oc[-1]
        out = sub(last[3], last[2])
        if math.hypot(*out) < 1e-6:
            out = sub(last[3], last[1])
        for c in cap_round(o_end, i_end, out):
            path.seg_cubic(c)
    else:
        path.L(i_end)
    for c in reversed(ic):
        path.seg_cubic(reverse_cubic(c))
    i_start = ic[0][0]
    o_start = oc[0][0]
    if cap0 and is_round(F):
        first = oc[0]
        out = sub(first[0], first[1])
        if math.hypot(*out) < 1e-6:
            out = sub(first[0], first[2])
        for c in cap_round(i_start, o_start, out):
            path.seg_cubic(c)
    else:
        path.L(o_start)
    return path


def ring(F, cx, cy, rxo, ryo, rxi, ryi, ko=None, ki=None):
    ko = F.k if ko is None else ko
    ki = F.ki if ki is None else ki
    return quad_cubics(cx, cy, rxo, ryo, ko), quad_cubics(cx, cy, rxi, ryi, ki)


# ---------------------------------------------------------------- junctions

def junction(F, kind, where, xs_out, x_edge, ext, S):
    """Outer and inner junction points for a stroke leaving a stem.

    kind: notch | crotch | spur | crotch_b.  where: top | bottom.
    Returns ((Jo, co), (Ji, ci)) where c is the corner fraction: the tangent at
    the junction aims at a point that fraction of the way toward the extreme.
    """
    sgn = -1 if where == "top" else 1
    d_o, c_o, d_i, c_i = F.get("j_" + kind)
    Jo = (x_edge, ext + sgn * d_o)
    Ji = (x_edge, ext + sgn * d_i)
    return (Jo, c_o), (Ji, c_i)


def jdir(J, ext, c):
    """Tangent at junction J aiming at the corner fraction c toward extreme ext."""
    aim = (lerp(J[0], ext[0], c), ext[1])
    return sub(aim, J)


def shoulder(F, xs, xe, xR, Sr, kind="notch", top=None, T=None, yb=0.0, end="stem",
             yr=None, xt=None, xti=None, term_theta=None, k=None, ki=None, ref_h=None,
             capb=False):
    """Arch leaving a stem (spanning xs..xe, stem on the left) over the top and
    down the right side to yb (end='stem'), or ending in a terminal (end='term').

    xR: outer right edge. Sr: right stroke width.
    """
    S = abs(xe - xs)
    h = F.xh if ref_h is None else ref_h
    top = h + F.o if top is None else top
    T = F.T if T is None else T
    if yr is None:
        yr = (top - (xR - xs) / 2 * F.sh_round) if F.get("sh_round") else h * F.sh_yr
    k = F.sh_k if k is None else k
    ki = F.sh_ki if ki is None else ki
    xt = lerp(xs, xR, F.sh_xt) if xt is None else xt
    xti = lerp(xe, xR - Sr, F.sh_xti) if xti is None else xti
    yri = yr + F.get("sh_yri_d", 0)
    tp = (xt, top)
    ti = (xti, top - T)
    if F.junction == "smooth":
        Jo, do, kjo = (xs, yr), V, k
        Ji, di, kji = (xe, yri), V, ki
    else:
        (Jo, co), (Ji, ci) = junction(F, kind, "top", xs, xe, h, S)
        do, di = jdir(Jo, tp, co), jdir(Ji, ti, ci)
        kjo = kji = F.jk
    p = Path(Jo)
    p.T(tp, do, H, kjo)
    Qo = (tp,) + tension_handles(tp, (xR, yr), H, V, k) + ((xR, yr),)
    Qi = ((xR - Sr, yri),) + tension_handles((xR - Sr, yri), ti, V, H, ki) + (ti,)
    if end == "stem":
        p.seg_cubic(Qo)
        if capb and is_round(F):
            r = Sr / 2
            p.L((xR, yb + r))
            for c in cap_round((xR, yb + r), (xR - Sr, yb + r), (0, -1)):
                p.seg_cubic(c)
        else:
            p.L((xR, yb)).L((xR - Sr, yb))
        p.L((xR - Sr, yri))
        p.seg_cubic(Qi)
    else:
        # terminal on the right quadrant
        cpt, cd = term_theta
        to = line_param(Qo, cpt, cd)
        ti_ = line_param(Qi, cpt, cd)
        a = split(*Qo, to)[0]
        b = split(*Qi, ti_)[1]
        p.seg_cubic(a)
        if is_round(F):
            out = sub(a[3], a[2])
            for c in cap_round(a[3], b[0], out):
                p.seg_cubic(c)
        else:
            p.L(b[0])
        p.seg_cubic(b)
    p.T(Ji, H, di, kji)
    if end == "stem" and capb and has_serifs(F):
        return [p] + stem_serifs(F, xR - Sr, xR, yb, "B", False)
    return p


def bowl(F, xs, xe, xR, top, bot, T_top, T_bot, kt="crotch", kb="spur",
         xt=None, xti=None, xb=None, xbi=None, Sside=None, k=None, ki=None,
         cy=None, h=None):
    """Bowl attached to a stem on the left (stem spans xs..xe). Outer right
    extreme at xR. Returns a list of contours (path or ring pair)."""
    S = abs(xe - xs)
    Sside = S if Sside is None else Sside
    k = F.k if k is None else k
    ki = F.ki if ki is None else ki
    h = F.xh if h is None else h
    if cy is None:
        cy = (top + bot) / 2
    if F.junction == "smooth":
        rxo = (xR - xs) / 2
        cxo = xs + rxo
        rxi = (xR - Sside - xe) / 2
        cxi = xe + rxi
        ryo = (top - bot) / 2
        cyi = (top - T_top + bot + T_bot) / 2
        ryi = (top - T_top - bot - T_bot) / 2
        kk = F.get("bowl_ki", ki)
        outer = oval(cxo, cy, rxo, ryo, k)
        inner = oval(cxi, cyi, rxi, ryi, kk)
        return [("fill", outer), ("hole", inner)]
    xt = lerp(xs, xR, F.bw_xt) if xt is None else xt
    xti = lerp(xe, xR - Sside, F.bw_xti) if xti is None else xti
    xb = lerp(xs, xR, F.bw_xb) if xb is None else xb
    xbi = lerp(xe, xR - Sside, F.bw_xbi) if xbi is None else xbi
    (Jot, cot), (Jit, cit) = junction(F, kt, "top", xs, xe, h, S)
    (Job, cob), (Jib, cib) = junction(F, kb, "bottom", xs, xe, 0, S)
    dot_ = jdir(Jot, (xt, top), cot)
    dit = jdir(Jit, (xti, top - T_top), cit)
    dob = jdir(Job, (xb, bot), cob)
    dib = jdir(Jib, (xbi, bot + T_bot), cib)
    kjt = kjb = F.jk
    cyi = (top - T_top + bot + T_bot) / 2
    p = Path(Jot)
    p.T((xt, top), dot_, H, kjt)
    p.T((xR, cy), H, V, k)
    p.T((xb, bot), V, H, k)
    p.T(Job, H, dob, kjb)
    p.L(Jib)
    p.T((xbi, bot + T_bot), dib, H, kjb)
    p.T((xR - Sside, cyi), H, V, ki)
    p.T((xti, top - T_top), V, H, ki)
    p.T(Jit, H, dit, kjt)
    return [("fill", p)]


# ---------------------------------------------------------------- diagonals

def slant_w(t, dx, dy):
    """Horizontal width of a diagonal stroke with perpendicular thickness t."""
    s = abs(dy) / math.hypot(dx, dy)
    return t / max(s, 0.2)


def dquad(bc, tc, wb, wt=None):
    """Diagonal stroke with horizontal ends. bc/tc: (x, y) centers of the bottom
    and top ends; wb/wt horizontal widths."""
    wt = wb if wt is None else wt
    return Path((bc[0] - wb / 2, bc[1])).L((bc[0] + wb / 2, bc[1])).L(
        (tc[0] + wt / 2, tc[1])).L((tc[0] - wt / 2, tc[1]))


def vee(F, x0, W, top, bot, t, apex=None, round_join=False, serifs=False):
    """A 'v' shape as one polygon (or two round-capped strokes for rounded
    families). top > bot gives v, top < bot gives the A form. Returns paths."""
    a = F.S * F.get("v_apex", 0.55) if apex is None else apex
    if is_round(F):
        r = t / 2
        sg = 1 if top > bot else -1
        bl = (x0 + W / 2, bot + sg * r)
        return [stroke(F, (x0 + r, top - sg * r), bl, t, True, True),
                stroke(F, (x0 + W - r, top - sg * r), bl, t, True, True)]
    c = F.get("diag_c", 1.0)
    tl, tr = (t, t * c) if top > bot else (t * c, t)
    xl = x0 + W / 2 - a / 2
    xr = x0 + W / 2 + a / 2
    wxl = slant_w(tl, xl - x0, top - bot)
    wxr = slant_w(tr, xl - x0, top - bot)
    from core import intersect
    hit = intersect((x0 + wxl, top), sub((xl + wxl, bot), (x0 + wxl, top)),
                    (x0 + W - wxr, top), sub((xr - wxr, bot), (x0 + W - wxr, top)))
    iv = hit[0]
    out = [Path((xl, bot)).L((xr, bot)).L((x0 + W, top)).L((x0 + W - wxr, top)).L(iv)
           .L((x0 + wxl, top)).L((x0, top))]
    if serifs:
        up = top < bot
        out += hslab(F, x0, x0 + wxl, top, up) + hslab(F, x0 + W - wxr, x0 + W, top, up)
    return out


def hook_ring(F, cx, cy, rxo, ryo, S, T, k=None, ki=None):
    rxi, ryi = rxo - S, ryo - T
    outer, inner = ring(F, cx, cy, rxo, ryo, rxi, ryi, k, ki)
    return outer, inner, (rxo + rxi) / 2, (ryo + ryi) / 2, rxi, ryi


def cubic_tangent_to(seg, target, lo=0.0, hi=1.0):
    """Parameter t on cubic seg where the tangent line passes through target."""
    from core import bez
    def f(t):
        p = bez(*seg, t)
        e = 1e-4
        q = bez(*seg, min(1, t + e))
        r = bez(*seg, max(0, t - e))
        d = sub(q, r)
        v = sub(target, p)
        return d[0] * v[1] - d[1] * v[0]
    N = 200
    prev = f(lo)
    for i in range(1, N + 1):
        t = lo + (hi - lo) * i / N
        cur = f(t)
        if prev * cur <= 0:
            a, b = t - (hi - lo) / N, t
            fa = prev
            for _ in range(50):
                m = (a + b) / 2
                fm = f(m)
                if fa * fm <= 0:
                    b = m
                else:
                    a, fa = m, fm
            return (a + b) / 2
        prev = cur
    raise ValueError("no tangent to target")


def zdiag(x0, x1, y0, y1, w):
    """Diagonal from bottom-left (x0, y0) to top-right (x1, y1), horizontal width w,
    ends flush with horizontal bars at y0 and y1."""
    return Path((x0, y0)).L((x0 + w, y0)).L((x1, y1)).L((x1 - w, y1))
