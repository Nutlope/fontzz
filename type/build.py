"""Build UFO masters, designspace, variable + static fonts for each family."""
import os
import sys
import shutil
import subprocess
import ufoLib2
from fontTools.designspaceLib import (DesignSpaceDocument, AxisDescriptor, SourceDescriptor,
                                      InstanceDescriptor)
from fam import FAMILIES, MASTERS, F
import glyphs
import lc  # noqa: F401 (registers glyphs)
try:
    import uc  # noqa: F401
except ImportError:
    pass
try:
    import figs  # noqa: F401
except ImportError:
    pass
try:
    import punct  # noqa: F401
except ImportError:
    pass
try:
    import marks  # noqa: F401
except ImportError:
    pass
from glyphs import REG, ORDER, COMP, CORDER, finish

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
REPO = "https://github.com/Luffixos/fontzz"
SITE_URL = "https://fontzz.vercel.app"
WEIGHT_NAMES = {100: "Thin", 200: "ExtraLight", 300: "Light", 400: "Regular", 500: "Medium",
                600: "SemiBold", 700: "Bold", 800: "ExtraBold", 900: "Black"}


def draw(path, pen):
    pen.moveTo(path.start)
    segs = list(path.segs)
    st = path.start
    if segs:
        last = segs[-1]
        end = last[-1]
        if abs(end[0] - st[0]) < 1e-6 and abs(end[1] - st[1]) < 1e-6:
            if last[0] == "L":
                segs = segs[:-1]
            else:
                segs[-1] = ("C", last[1], last[2], st)
    for s in segs:
        if s[0] == "L":
            pen.lineTo(s[1])
        else:
            pen.curveTo(s[1], s[2], s[3])
    pen.closePath()


def ink_bounds(g, gs, dx=0.0, dy=0.0, sc=1.0):
    """Bounds of a glyph including its components (component offsets resolved)."""
    bs = []
    b = g.bounds()
    if b is not None:
        bs.append((b[0] * sc + dx, b[1] * sc + dy, b[2] * sc + dx, b[3] * sc + dy))
    for c in g.comps:
        cs = c[3] if len(c) > 3 else 1.0
        cb = ink_bounds(gs[c[0]], gs, dx + c[1] * sc, dy + c[2] * sc, sc * cs)
        if cb is not None:
            bs.append(cb)
    if not bs:
        return None
    return (min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs))


# composites made of two full letters; flattened in every master so they stay compatible
MONO_FLATTEN = {"ae", "oe", "dcaron", "tcaron", "lcaron", "Lcaron"}


def flatten(g, gs, dx=0.0, dy=0.0, sc=1.0, into=None):
    """Replace components with copies of their outlines."""
    into = g if into is None else into
    for c in g.comps:
        cs = c[3] if len(c) > 3 else 1.0
        src = gs[c[0]]
        ox, oy, s2 = dx + c[1] * sc, dy + c[2] * sc, sc * cs
        for p, h in src.paths:
            into.paths.append((p.map(lambda q, ox=ox, oy=oy, s2=s2: (q[0] * s2 + ox, q[1] * s2 + oy)), h))
        flatten(src, gs, ox, oy, s2, into)
    if into is g:
        g.comps = []


def monospace(f, g, mw, gs=None):
    """Fixed advance: center the ink in one cell, squeezing
    anything wider than the cell allows."""
    if not g.width:
        return  # combining marks stay zero width
    b = ink_bounds(g, gs or {})
    W = mw
    room = W - 2 * f.get("mono_sb", 34)
    if g.comps and g.name in MONO_FLATTEN:
        flatten(g, gs)  # two letters in one cell: draw it out so it can be squeezed
        b = g.bounds()
    if b is None:
        g.width = W
        return
    ink = b[2] - b[0]
    if ink > room and not g.comps:
        s = room / ink
        x0 = b[0]
        g.apply(lambda p: (x0 + (p[0] - x0) * s, p[1]))
        b = g.bounds()
        ink = b[2] - b[0]
    dx = (W - ink) / 2 - b[0]
    g.apply(lambda p: (p[0] + dx, p[1]))
    g.comps = [(c[0], c[1] + dx) + tuple(c[2:]) for c in g.comps]
    g.width = W


def make_glyphs(spec, mi, names=None):
    f = F(spec, mi)
    if spec.get("pixel_src"):
        import pixel
        gs = pixel.make(spec, f)
        return f, (gs if names is None else {k: v for k, v in gs.items() if k in names})
    out = {}
    want = names
    names = [n for n in ORDER] if names is None else [n for n in ORDER if n in names or True]
    for name in names:
        uni, fn = REG[name]
        f.__dict__["cur"] = name
        try:
            g = fn(f)
        except Exception as e:
            raise RuntimeError("glyph %s master %s: %s" % (name, f.master_name, e)) from e
        g.name = name
        g.uni = uni
        finish(g)
        out[name] = g
    slant = f.get("slant")
    if slant:
        t = __import__("math").tan(__import__("math").radians(slant))
        for name in names:
            out[name].apply(lambda p: (p[0] + p[1] * t, p[1]))
    mono = f.get("mono")
    if mono:
        for name in names:
            monospace(f, out[name], mono)
    for name in CORDER:
        uni, fn = COMP[name]
        f.__dict__["cur"] = name
        try:
            g = fn(f, out)
        except Exception as e:
            raise RuntimeError("composite %s master %s: %s" % (name, f.master_name, e)) from e
        g.name = name
        g.uni = uni
        if g.lsb is not None:
            finish(g)
        if mono:
            monospace(f, g, mono, out)
        out[name] = g
    if want is not None:
        return f, {k: v for k, v in out.items() if k in want}
    return f, out


def build_master(spec, mi):
    f, gs = make_glyphs(spec, mi)
    ufo = ufoLib2.Font()
    info = ufo.info
    info.familyName = spec["name"]
    info.styleName = MASTERS[mi][0]
    info.unitsPerEm = spec["upm"]
    info.ascender = spec["asc"]
    info.descender = spec["desc"]
    info.xHeight = spec["xh"]
    info.capHeight = spec["cap"]
    info.versionMajor, info.versionMinor = 1, 0
    info.copyright = "Copyright 2026 The %s Project Authors (%s)" % (spec["name"], REPO)
    info.openTypeNameDesigner = "Hassan and Youssef"
    info.openTypeNameManufacturer = "fontzz"
    info.openTypeNameManufacturerURL = SITE_URL
    info.openTypeNameDesignerURL = REPO
    info.openTypeNameLicense = ("This Font Software is licensed under the SIL Open Font License, "
                                "Version 1.1.")
    info.openTypeNameLicenseURL = "https://openfontlicense.org"
    info.openTypeOS2TypoAscender = 950
    info.openTypeOS2TypoDescender = -250
    info.openTypeOS2TypoLineGap = 0
    info.openTypeHheaAscender = 950
    info.openTypeHheaDescender = -250
    info.openTypeHheaLineGap = 0
    info.openTypeOS2WinAscent = 1060
    info.openTypeOS2WinDescent = 400
    info.openTypeOS2Selection = [7]  # USE_TYPO_METRICS
    info.openTypeOS2WeightClass = MASTERS[mi][1]
    info.openTypeOS2VendorID = "FNZZ"
    info.openTypeOS2Type = []  # installable embedding, as the OFL allows
    info.postscriptUnderlinePosition = -110
    info.postscriptUnderlineThickness = round(f.T * 0.8 + 10)
    order = [".notdef", "space"] + [n for n in ORDER] + [n for n in CORDER]
    ufo.lib["public.glyphOrder"] = order
    # .notdef
    nd = ufo.newGlyph(".notdef")
    nd.width = f.get("mono") or 560
    if f.get("slant"):
        info.italicAngle = -f.slant
    if f.get("mono"):
        info.postscriptIsFixedPitch = True
        info.openTypeOS2Panose = [2, 11, 5, 9, 0, 0, 0, 0, 0, 0]
    pen = nd.getPen()
    for (x0, y0, x1, y1, rev) in ((60, 0, 500, 720, False), (110, 50, 450, 670, True)):
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        if rev:
            pts = pts[::-1]
        pen.moveTo(pts[0])
        for p in pts[1:]:
            pen.lineTo(p)
        pen.closePath()
    sp = ufo.newGlyph("space")
    sp.width = f.get("mono") or round(f.get("space_w", 0.5 * (2 * f.S + f.n_c) + f.sb * 0.9))
    sp.unicodes = [0x20]
    for name in ORDER + CORDER:
        g = gs[name]
        ug = ufo.newGlyph(name)
        ug.width = round(g.width)
        if g.uni is not None:
            ug.unicodes = g.uni if isinstance(g.uni, list) else [g.uni]
        pen = ug.getPen()
        for p in g.oriented_paths():
            draw(p, pen)
        for c in g.comps:
            cname, dx, dy = c[0], c[1], c[2]
            sc = c[3] if len(c) > 3 else 1.0
            pen.addComponent(cname, (sc, 0, 0, sc, round(dx), round(dy)))
    if hasattr(sys.modules.get("kern"), "kerning"):
        pass
    return ufo, f, gs


def build_family(key, statics=True):
    spec = FAMILIES[key]
    name = spec["name"]
    fdir = os.path.join(OUT, key)
    shutil.rmtree(fdir, ignore_errors=True)
    os.makedirs(fdir)
    doc = DesignSpaceDocument()
    ax = AxisDescriptor()
    ax.tag, ax.name, ax.minimum, ax.default, ax.maximum = "wght", "Weight", 100, 400, 900
    doc.addAxis(ax)
    masters = []
    for mi, (sname, w) in enumerate(MASTERS):
        ufo, f, gs = build_master(spec, mi)
        masters.append((ufo, f, gs))
    if not spec.get("mono") and not spec.get("pixel_src"):
        import kern
        kern.apply(spec, masters)
    try:
        import features
        fea = features.build(spec, masters)
    except ImportError:
        fea = ""
    for mi, (sname, w) in enumerate(MASTERS):
        ufo = masters[mi][0]
        ufo.features.text = fea
        p = os.path.join(fdir, "%s-%s.ufo" % (name, sname))
        ufo.save(p, overwrite=True)
        s = SourceDescriptor()
        s.path = p
        s.location = {"Weight": w}
        s.familyName = name
        s.styleName = sname
        doc.addSource(s)
    for w, wn in WEIGHT_NAMES.items():
        i = InstanceDescriptor()
        i.familyName = name
        i.styleName = wn
        i.location = {"Weight": w}
        doc.addInstance(i)
    dsp = os.path.join(fdir, name + ".designspace")
    doc.write(dsp)
    vf = os.path.join(fdir, "%s[wght].ttf" % name)
    r = subprocess.run([os.path.join(HERE, "..", ".venv", "bin", "fontmake"), "-m", dsp, "-o",
                        "variable", "--output-path", vf, "--no-production-names"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-4000:], r.stderr[-4000:])
        raise SystemExit("fontmake failed")
    postprocess(vf)
    return vf


def postprocess(path):
    """Flag overlapping contours (needed by Apple and FreeType rasterizers) and add gasp."""
    from fontTools.ttLib import TTFont, newTable
    from fontTools.ttLib.tables._g_l_y_f import OVERLAP_COMPOUND, flagOverlapSimple
    f = TTFont(path)
    glyf = f["glyf"]
    for name in f.getGlyphOrder():
        g = glyf[name]
        if g.isComposite():
            g.components[0].flags |= OVERLAP_COMPOUND
        elif g.numberOfContours > 0:
            g.flags[0] |= flagOverlapSimple
    gasp = newTable("gasp")
    gasp.version = 1
    gasp.gaspRange = {0xFFFF: 0x000F}
    f["gasp"] = gasp
    f.save(path)


if __name__ == "__main__":
    keys = sys.argv[1:] or list(FAMILIES)
    for k in keys:
        print("built", build_family(k))
