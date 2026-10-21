"""Automatic kerning from glyph side profiles (per master)."""
import numpy as np

STEP = 8
Y0, Y1 = -260, 1000
YS = np.arange(Y0, Y1 + 1, STEP, dtype=float)

UC = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
LC = set("abcdefghijklmnopqrstuvwxyz")

IRR_R = set("AKLPRTVWXYFkrtvwxyf") | {"quotesingle", "quotedbl", "quoteright", "quoteleft",
                                      "quotedblright", "quotedblleft", "period", "comma", "hyphen",
                                      "slash", "endash", "emdash"}
IRR_L = set("AJTVWXYvwxyj") | {"quotesingle", "quotedbl", "quoteright", "quoteleft",
                               "quotedblright", "quotedblleft", "period", "comma", "hyphen",
                               "slash", "endash", "emdash", "quotesinglbase", "quotedblbase"}
NAMES = {".": "period", ",": "comma", "-": "hyphen", "'": "quotesingle", '"': "quotedbl",
         "/": "slash"}

BASE_SET = list(UC) + list(LC) + ["period", "comma", "hyphen", "quotesingle", "quotedbl",
                                  "quoteright", "quoteleft", "quotedblright", "quotedblleft",
                                  "quotesinglbase", "quotedblbase", "slash", "endash", "emdash",
                                  "colon", "semicolon", "parenright", "parenleft", "question",
                                  "exclam", "ampersand", "zero", "one", "two", "three", "four",
                                  "five", "six", "seven", "eight", "nine", "germandbls",
                                  "guillemotleft", "guillemotright"]


def polys(g, gs, dx=0.0, dy=0.0, sc=1.0):
    out = []
    for p, _ in g.paths:
        pts = np.array(p.flatten(10), dtype=float)
        pts = pts * sc + np.array([dx, dy])
        out.append(pts)
    for c in g.comps:
        cs = c[3] if len(c) > 3 else 1.0
        out.extend(polys(gs[c[0]], gs, dx + c[1] * sc, dy + c[2] * sc, sc * cs))
    return out


def profile(g, gs):
    L = np.full(YS.shape, np.inf)
    R = np.full(YS.shape, -np.inf)
    for pts in polys(g, gs):
        a = pts
        b = np.roll(pts, -1, axis=0)
        for (x0, y0), (x1, y1) in zip(a, b):
            if y0 == y1:
                lo, hi = min(x0, x1), max(x0, x1)
                m = np.abs(YS - y0) < STEP / 2
                L[m] = np.minimum(L[m], lo)
                R[m] = np.maximum(R[m], hi)
                continue
            ylo, yhi = (y0, y1) if y0 < y1 else (y1, y0)
            m = (YS >= ylo) & (YS <= yhi)
            if not m.any():
                continue
            t = (YS[m] - y0) / (y1 - y0)
            x = x0 + t * (x1 - x0)
            L[m] = np.minimum(L[m], x)
            R[m] = np.maximum(R[m], x)
    return L, R


def apply(spec, masters):
    for ufo, f, gs in masters:
        names = [n for n in BASE_SET if n in gs]
        prof = {n: profile(gs[n], gs) for n in names}
        ext = {}
        for n in names:
            L, R = prof[n]
            ok = np.isfinite(L)
            ext[n] = (YS[ok].min(), YS[ok].max()) if ok.any() else (0, 0)
        depth = f.cap * 0.22
        sbl = f.sb
        strength = spec.get("kern_strength", 0.62)

        def stand_r(n):
            if n in IRR_R:
                return "n" if (n in LC or n not in UC) else "H"
            return n

        def stand_l(n):
            if n in IRR_L:
                return "n" if (n in LC or n not in UC) else "H"
            return n

        def gaps(a, b, lo, hi):
            Ra = prof[a][1]
            Lb = prof[b][0]
            m = (YS >= lo) & (YS <= hi) & np.isfinite(Ra) & np.isfinite(Lb)
            if m.sum() < 2:
                return None
            return (gs[a].width - Ra[m]) + Lb[m]

        kerning = {}
        for a in names:
            for b in names:
                if a not in IRR_R and b not in IRR_L:
                    continue
                lo = max(ext[a][0], ext[b][0], -40)
                hi = min(ext[a][1], ext[b][1], f.cap + 20)
                if hi - lo < STEP * 2:
                    # no vertical overlap (e.g. quote + period): skip
                    continue
                g = gaps(a, b, lo, hi)
                if g is None:
                    continue
                a2, b2 = stand_r(a), stand_l(b)
                gr = gaps(a2, b2, lo, hi)
                if gr is None:
                    continue
                avg = np.minimum(g, depth).mean()
                ref = np.minimum(gr, depth).mean()
                k = (ref - avg) * strength
                # never let ink come closer than a floor
                floor = sbl * 0.55
                k = max(k, floor - g.min())
                k = max(min(k, 40), -f.upm * 0.15)
                if a in LC and b in LC and b not in IRR_L:
                    k = max(k, -f.upm * (0.012 if b in set("nmrhbkliupj") else 0.03))
                if b in ("period", "comma") and a in LC:
                    k = max(k, -f.upm * 0.07)
                k = int(round(k / 2.0) * 2)
                if abs(k) >= 10:
                    kerning[(a, b)] = k
        ufo.kerning.clear()
        for (a, b), k in kerning.items():
            ufo.kerning[(a, b)] = k
        print("  kern %s: %d pairs" % (f.master_name, len(kerning)))
