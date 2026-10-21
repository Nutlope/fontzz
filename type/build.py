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


def make_glyphs(spec, mi, names=None):
    f = F(spec, mi)
    out = {}
    want = names
    names = [n for n in ORDER] if names is None else [n for n in ORDER if n in names or True]
    for name in names:
        uni, fn = REG[name]
        try:
            g = fn(f)
        except Exception as e:
            raise RuntimeError("glyph %s master %s: %s" % (name, f.master_name, e)) from e
        g.name = name
        g.uni = uni
        finish(g)
        out[name] = g
    for name in CORDER:
        uni, fn = COMP[name]
        try:
            g = fn(f, out)
        except Exception as e:
            raise RuntimeError("composite %s master %s: %s" % (name, f.master_name, e)) from e
        g.name = name
        g.uni = uni
        if g.lsb is not None:
            finish(g)
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
    info.copyright = "Copyright 2026 The %s Project Authors" % spec["name"]
    info.openTypeNameDesigner = "fontzz"
    info.openTypeNameLicense = ("This Font Software is licensed under the SIL Open Font License, "
                                "Version 1.1.")
    info.openTypeNameLicenseURL = "https://openfontlicense.org"
    info.openTypeOS2TypoAscender = 950
    info.openTypeOS2TypoDescender = -250
    info.openTypeOS2TypoLineGap = 0
    info.openTypeHheaAscender = 950
    info.openTypeHheaDescender = -250
    info.openTypeHheaLineGap = 0
    info.openTypeOS2WinAscent = 1050
    info.openTypeOS2WinDescent = 300
    info.openTypeOS2Selection = [7]  # USE_TYPO_METRICS
    info.openTypeOS2WeightClass = MASTERS[mi][1]
    info.openTypeOS2VendorID = "FNZZ"
    info.postscriptUnderlinePosition = -110
    info.postscriptUnderlineThickness = round(f.T * 0.8 + 10)
    order = [".notdef", "space"] + [n for n in ORDER] + [n for n in CORDER]
    ufo.lib["public.glyphOrder"] = order
    # .notdef
    nd = ufo.newGlyph(".notdef")
    nd.width = 560
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
    sp.width = round(f.get("space_w", 0.5 * (2 * f.S + f.n_c) + f.sb * 0.9))
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
    try:
        import kern
        kern.apply(spec, masters)
    except ImportError:
        pass
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
