"""Geometry core for the parametric type generator.

Glyphs are built from closed cubic contours that may overlap (non-zero fill).
Every construction is deterministic in structure, so contours stay
point-compatible across weight masters and interpolate cleanly.
"""
import math

H = (1.0, 0.0)
V = (0.0, 1.0)


def D(deg):
    r = math.radians(deg)
    return (math.cos(r), math.sin(r))


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def mul(a, s):
    return (a[0] * s, a[1] * s)


def lerp(a, b, t):
    if isinstance(a, tuple):
        return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    return a + (b - a) * t


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def norm(v):
    l = math.hypot(v[0], v[1])
    return (v[0] / l, v[1] / l)


def perp(v):
    return (-v[1], v[0])


def intersect(p, d, q, e):
    """Intersection of line p + t*d and q + s*e. Returns (point, t, s) or None."""
    den = d[0] * e[1] - d[1] * e[0]
    if abs(den) < 1e-9:
        return None
    t = ((q[0] - p[0]) * e[1] - (q[1] - p[1]) * e[0]) / den
    s = ((q[0] - p[0]) * d[1] - (q[1] - p[1]) * d[0]) / den
    return (add(p, mul(d, t)), t, s)


def tension_handles(p0, p1, d0, d1, k0, k1=None):
    """Handles for a cubic from p0 to p1 with tangent d0 at p0 and d1 at p1.

    Handles sit at fraction k along the way to the corner where the two
    tangent lines meet (k=0.552 gives a circular quadrant, higher is squarer).
    """
    if k1 is None:
        k1 = k0
    d0 = norm(d0)
    d1 = norm(d1)
    chord = sub(p1, p0)
    if dot(d0, chord) < 0:
        d0 = mul(d0, -1)
    if dot(d1, chord) < 0:
        d1 = mul(d1, -1)
    hit = intersect(p0, d0, p1, d1)
    L = math.hypot(*chord)
    if hit is None or hit[1] <= 1e-6 or hit[2] >= -1e-6:
        # parallel tangents (S-curve) or corner behind: use chord-relative handles
        c1 = add(p0, mul(d0, k0 * L * 0.5))
        c2 = sub(p1, mul(d1, k1 * L * 0.5))
        return c1, c2
    corner = hit[0]
    c1 = lerp(p0, corner, k0)
    c2 = lerp(p1, corner, k1)
    return c1, c2


# ---------------------------------------------------------------- bezier math

def bez(p0, c1, c2, p1, t):
    mt = 1 - t
    a = mt * mt * mt
    b = 3 * mt * mt * t
    c = 3 * mt * t * t
    d = t * t * t
    return (a * p0[0] + b * c1[0] + c * c2[0] + d * p1[0],
            a * p0[1] + b * c1[1] + c * c2[1] + d * p1[1])


def split(p0, c1, c2, p1, t):
    a = lerp(p0, c1, t)
    b = lerp(c1, c2, t)
    c = lerp(c2, p1, t)
    ab = lerp(a, b, t)
    bc = lerp(b, c, t)
    m = lerp(ab, bc, t)
    return (p0, a, ab, m), (m, bc, c, p1)


def line_param(seg, p, d):
    """Parameter t where cubic seg crosses line through p with direction d."""
    n = perp(norm(d))
    f = lambda t: dot(sub(bez(*seg, t), p), n)
    N = 64
    prev = f(0.0)
    best = None
    for i in range(1, N + 1):
        t = i / N
        cur = f(t)
        if prev == 0:
            best = (i - 1) / N
            break
        if prev * cur <= 0:
            lo, hi = (i - 1) / N, t
            flo = prev
            for _ in range(60):
                mid = (lo + hi) / 2
                fm = f(mid)
                if flo * fm <= 0:
                    hi = mid
                else:
                    lo, flo = mid, fm
            best = (lo + hi) / 2
            break
        prev = cur
    if best is None:
        raise ValueError("line does not cross segment")
    return best


def solve_t_for(seg, axis, value):
    p = (value, 0) if axis == 0 else (0, value)
    d = V if axis == 0 else H
    return line_param(seg, p, d)


# ---------------------------------------------------------------- paths

class Path:
    """A closed contour made of line and cubic segments."""

    def __init__(self, p):
        self.start = (float(p[0]), float(p[1]))
        self.segs = []
        self.cur = self.start

    def L(self, p):
        p = (float(p[0]), float(p[1]))
        self.segs.append(("L", p))
        self.cur = p
        return self

    def C(self, c1, c2, p):
        self.segs.append(("C", c1, c2, (float(p[0]), float(p[1]))))
        self.cur = p
        return self

    def T(self, p, d0, d1, k=0.56, k1=None):
        """Tension curve to p, leaving with tangent d0 and arriving with d1."""
        c1, c2 = tension_handles(self.cur, p, d0, d1, k, k1)
        return self.C(c1, c2, p)

    def seg_cubic(self, cubic):
        """Append a cubic given as (p0, c1, c2, p1); p0 must equal current point."""
        self.segs.append(("C", cubic[1], cubic[2], cubic[3]))
        self.cur = cubic[3]
        return self

    def points(self):
        pts = [self.start]
        for s in self.segs:
            pts.extend(s[1:])
        return pts

    def map(self, fn):
        q = Path(fn(self.start))
        for s in self.segs:
            if s[0] == "L":
                q.segs.append(("L", fn(s[1])))
            else:
                q.segs.append(("C", fn(s[1]), fn(s[2]), fn(s[3])))
        q.cur = fn(self.cur)
        return q

    def flatten(self, steps=12):
        pts = [self.start]
        cur = self.start
        for s in self.segs:
            if s[0] == "L":
                pts.append(s[1])
                cur = s[1]
            else:
                for i in range(1, steps + 1):
                    pts.append(bez(cur, s[1], s[2], s[3], i / steps))
                cur = s[3]
        return pts

    def area(self):
        pts = self.flatten()
        a = 0.0
        for i in range(len(pts)):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % len(pts)]
            a += x0 * y1 - x1 * y0
        return a / 2

    def reversed(self):
        # rebuild walking backwards; drop a closing duplicate point
        segs = list(self.segs)
        nodes = [self.start] + [s[-1] for s in segs]
        closed_dup = len(nodes) > 1 and _close(nodes[-1], nodes[0])
        if not closed_dup:
            segs.append(("L", self.start))
            nodes.append(self.start)
        # now last node == start
        q = Path(nodes[-1])
        for i in range(len(segs) - 1, -1, -1):
            s = segs[i]
            target = nodes[i]
            if s[0] == "L":
                q.segs.append(("L", target))
            else:
                q.segs.append(("C", s[2], s[1], target))
        return q


def _close(a, b, eps=1e-6):
    return abs(a[0] - b[0]) < eps and abs(a[1] - b[1]) < eps


# ---------------------------------------------------------------- transforms

def T_translate(dx, dy):
    return lambda p: (p[0] + dx, p[1] + dy)


def T_scale(sx, sy, cx=0.0, cy=0.0):
    return lambda p: (cx + (p[0] - cx) * sx, cy + (p[1] - cy) * sy)


def T_rot180(cx, cy):
    return lambda p: (2 * cx - p[0], 2 * cy - p[1])


def T_rotate(deg, cx=0.0, cy=0.0):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return lambda p: (cx + (p[0] - cx) * c - (p[1] - cy) * s,
                      cy + (p[0] - cx) * s + (p[1] - cy) * c)


def T_skew(deg, cy=0.0):
    t = math.tan(math.radians(deg))
    return lambda p: (p[0] + (p[1] - cy) * t, p[1])


# ---------------------------------------------------------------- glyph

class Glyph:
    def __init__(self, name, uni=None):
        self.name = name
        self.uni = uni
        self.paths = []   # list of (Path, is_hole)
        self.comps = []   # list of (glyphname, dx, dy)
        self.width = 0
        self.lsb = None   # requested left side bearing (applied in finish)
        self.rsb = None
        self.anchors = {}

    def add(self, *paths, hole=False):
        for p in paths:
            if p is None:
                continue
            if isinstance(p, (list, tuple)):
                self.add(*p, hole=hole)
            else:
                self.paths.append((p, hole))
        return self

    def hole(self, *paths):
        return self.add(*paths, hole=True)

    def apply(self, fn):
        self.paths = [(p.map(fn), h) for p, h in self.paths]
        self.anchors = {k: fn(v) for k, v in self.anchors.items()}
        return self

    def mirror_x(self, cx):
        return self.apply(lambda p: (2 * cx - p[0], p[1]))

    def bounds(self):
        xs, ys = [], []
        for p, _ in self.paths:
            for q in p.flatten(16):
                xs.append(q[0])
                ys.append(q[1])
        if not xs:
            return None
        return min(xs), min(ys), max(xs), max(ys)

    def oriented_paths(self):
        """PostScript orientation: filled contours CCW, holes CW."""
        out = []
        for p, hole in self.paths:
            a = p.area()
            want_pos = not hole
            if (a > 0) != want_pos:
                p = p.reversed()
            out.append(p)
        return out


# ---------------------------------------------------------------- primitives

def rect(x0, y0, x1, y1):
    if x0 > x1:
        x0, x1 = x1, x0
    if y0 > y1:
        y0, y1 = y1, y0
    return Path((x0, y0)).L((x1, y0)).L((x1, y1)).L((x0, y1))


def poly(*pts):
    p = Path(pts[0])
    for q in pts[1:]:
        p.L(q)
    return p


def quad_cubics(cx, cy, rx, ry, k):
    """Superellipse as 4 cubics, CCW from the right extreme.

    k may be a single tension or a 4-tuple (one per quadrant: TR, TL, BL, BR).
    """
    if not isinstance(k, (tuple, list)):
        k = (k, k, k, k)
    R = (cx + rx, cy)
    Tp = (cx, cy + ry)
    Lp = (cx - rx, cy)
    B = (cx, cy - ry)
    out = []
    for (a, b, kk) in ((R, Tp, k[0]), (Tp, Lp, k[1]), (Lp, B, k[2]), (B, R, k[3])):
        corner = (a[0], b[1]) if a[1] == cy else (b[0], a[1])
        if isinstance(kk, (tuple, list)):
            k0, k1 = kk
        else:
            k0 = k1 = kk
        out.append((a, lerp(a, corner, k0), lerp(b, corner, k1), b))
    return out


def oval(cx, cy, rx, ry, k=0.5523):
    q = quad_cubics(cx, cy, rx, ry, k)
    p = Path(q[0][0])
    for c in q:
        p.seg_cubic(c)
    return p


def ellipse_ring(cx, cy, rxo, ryo, rxi, ryi, ko, ki):
    return oval(cx, cy, rxo, ryo, ko), oval(cx, cy, rxi, ryi, ki)


def sub_cubics(cubics, start, end):
    """Sub-path of a closed CCW chain of cubics from (i0, t0) to (i1, t1), wrapping."""
    n = len(cubics)
    (i0, t0), (i1, t1) = start, end
    i0 %= n
    i1 %= n
    if i0 == i1 and t1 > t0:
        return [_sub(cubics[i0], t0, t1)]
    out = []
    if t0 < 1 - 1e-9:
        out.append(_sub(cubics[i0], t0, 1.0))
    i = (i0 + 1) % n
    while i != i1:
        out.append(cubics[i])
        i = (i + 1) % n
    if t1 > 1e-9:
        out.append(_sub(cubics[i1], 0.0, t1))
    return out


def _sub(c, ta, tb):
    if ta <= 1e-9 and tb >= 1 - 1e-9:
        return c
    if ta <= 1e-9:
        return split(*c, tb)[0]
    right = split(*c, ta)[1]
    if tb >= 1 - 1e-9:
        return right
    tt = (tb - ta) / (1 - ta)
    return split(*right, tt)[0]


def reverse_cubic(c):
    return (c[3], c[2], c[1], c[0])


def cap_round(p_out, p_in, outward):
    """Two quarter cubics forming a semicircle from p_out to p_in bulging toward outward."""
    m = lerp(p_out, p_in, 0.5)
    r = math.hypot(*sub(p_in, p_out)) / 2
    tip = add(m, mul(norm(outward), r))
    k = 0.5523
    d = norm(outward)
    a = sub(p_out, m)
    b = sub(p_in, m)
    c1 = (p_out, add(p_out, mul(d, r * k)), add(tip, mul(a, k)), tip)
    c2 = (tip, add(tip, mul(b, k)), add(p_in, mul(d, r * k)), p_in)
    return [c1, c2]
