"""Build all families and package them for the site."""
import os
import sys
import json
import shutil
import zipfile
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.varLib.instancer import OverlapMode
import build
from fam import FAMILIES, MASTERS
from glyphs import REG

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, "..", "site", "public")
WEIGHTS = build.WEIGHT_NAMES

OFL = """Copyright 2026 The {name} Project Authors (https://github.com/Luffixos/fontzz)

This Font Software is licensed under the SIL Open Font License, Version 1.1.
This license is available with a FAQ at: https://openfontlicense.org

SIL OPEN FONT LICENSE Version 1.1 - 26 February 2007

PREAMBLE
The goals of the Open Font License (OFL) are to stimulate worldwide development of collaborative
font projects, to support the font creation efforts of academic and linguistic communities, and to
provide a free and open framework in which fonts may be shared and improved in partnership with
others.

The OFL allows the licensed fonts to be used, studied, modified and redistributed freely as long as
they are not sold by themselves. The fonts, including any derivative works, can be bundled,
embedded, redistributed and/or sold with any software provided that any reserved names are not used
by derivative works. The fonts and derivatives, however, cannot be released under any other type of
license. The requirement for fonts to remain under this license does not apply to any document
created using the fonts or their derivatives.

DEFINITIONS
"Font Software" refers to the set of files released by the Copyright Holder(s) under this license
and clearly marked as such. This may include source files, build scripts and documentation.

"Reserved Font Name" refers to any names specified as such after the copyright statement(s).

"Original Version" refers to the collection of Font Software components as distributed by the
Copyright Holder(s).

"Modified Version" refers to any derivative made by adding to, deleting, or substituting (in part or
in whole) any of the components of the Original Version, by changing formats or by porting the Font
Software to a new environment.

"Author" refers to any designer, engineer, programmer, technical writer or other person who
contributed to the Font Software.

PERMISSION & CONDITIONS
Permission is hereby granted, free of charge, to any person obtaining a copy of the Font Software,
to use, study, copy, merge, embed, modify, redistribute, and sell modified and unmodified copies of
the Font Software, subject to the following conditions:

1) Neither the Font Software nor any of its individual components, in Original or Modified Versions,
may be sold by itself.

2) Original or Modified Versions of the Font Software may be bundled, redistributed and/or sold with
any software, provided that each copy contains the above copyright notice and this license. These
can be included either as stand-alone text files, human-readable headers or in the appropriate
machine-readable metadata fields within text or binary files as long as those fields can be easily
viewed by the user.

3) No Modified Version of the Font Software may use the Reserved Font Name(s) unless explicit
written permission is granted by the corresponding Copyright Holder. This restriction only applies
to the primary font name as presented to the users.

4) The name(s) of the Copyright Holder(s) and the Author(s) of the Font Software shall not be used
to promote, endorse or advertise any Modified Version, except to acknowledge the contribution(s) of
the Copyright Holder(s) and the Author(s) or with their explicit written permission.

5) The Font Software, modified or unmodified, in part or in whole, must be distributed entirely
under this license, and must not be distributed under any other license. The requirement for fonts
to remain under this license does not apply to any document created using the Font Software.

TERMINATION
This license becomes null and void if any of the above conditions are not met.

DISCLAIMER
THE FONT SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
BUT NOT LIMITED TO ANY WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT OF COPYRIGHT, PATENT, TRADEMARK, OR OTHER RIGHT. IN NO EVENT SHALL THE COPYRIGHT
HOLDER BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, INCLUDING ANY GENERAL, SPECIAL,
INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF THE USE OR INABILITY TO USE THE FONT SOFTWARE OR FROM OTHER
DEALINGS IN THE FONT SOFTWARE.
"""


def outline_json(key, spec):
    """Design outlines per master for the site's construction view."""
    chars = ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
             "&@?!$%#*()[]{}/.,:;-+=<>'\"")
    byuni = {}
    for name, (uni, fn) in REG.items():
        if isinstance(uni, int) and chr(uni) in chars:
            byuni[chr(uni)] = name
    names = list(byuni.values())
    masters = []
    for mi in range(3):
        f, gs = build.make_glyphs(spec, mi)
        masters.append((f, gs))
    out = {"upm": spec["upm"], "xh": spec["xh"], "cap": spec["cap"], "asc": spec["asc"],
           "desc": spec["desc"], "masters": [m[1] for m in MASTERS], "glyphs": {}}
    for ch, name in byuni.items():
        rec = {"w": [], "c": []}
        for f, gs in masters:
            g = gs[name]
            rec["w"].append(round(g.width, 1))
            cs = []
            for p in g.oriented_paths():
                segs = [[round(p.start[0], 1), round(p.start[1], 1)]]
                for s in p.segs:
                    if s[0] == "L":
                        segs.append(["L", round(s[1][0], 1), round(s[1][1], 1)])
                    else:
                        segs.append(["C"] + [round(v, 1) for q in s[1:] for v in q])
                cs.append(segs)
            rec["c"].append(cs)
        # only keep glyphs whose structure matches across masters
        shapes = [[len(c) for c in m] for m in rec["c"]]
        if all(s == shapes[0] for s in shapes):
            out["glyphs"][ch] = rec
    return out


def release(key):
    spec = FAMILIES[key]
    name = spec["name"]
    vf = build.build_family(key)
    fdir = os.path.dirname(vf)
    pkg = os.path.join(fdir, "pkg", name)
    shutil.rmtree(os.path.join(fdir, "pkg"), ignore_errors=True)
    os.makedirs(os.path.join(pkg, "variable"))
    os.makedirs(os.path.join(pkg, "static"))
    os.makedirs(os.path.join(pkg, "web"))
    shutil.copy(vf, os.path.join(pkg, "variable", os.path.basename(vf)))
    f = TTFont(vf)
    f.flavor = "woff2"
    wv = os.path.join(pkg, "web", "%s[wght].woff2" % name)
    f.save(wv)
    for w, wn in WEIGHTS.items():
        vfont = TTFont(vf)
        inst = instancer.instantiateVariableFont(vfont, {"wght": w}, overlap=OverlapMode.REMOVE,
                                                 updateFontNames=False)
        # names
        nt = inst["name"]
        fam_name = name if wn in ("Regular",) else "%s %s" % (name, wn)
        style = "Regular"
        if wn == "Bold":
            fam_name, style = name, "Bold"
        for rec in list(nt.names):
            if rec.nameID in (1, 2, 3, 4, 6, 16, 17, 25):
                nt.removeNames(nameID=rec.nameID)
        nt.setName(fam_name, 1, 3, 1, 0x409)
        nt.setName(style, 2, 3, 1, 0x409)
        nt.setName("%s-%s;fontzz" % (name, wn), 3, 3, 1, 0x409)
        nt.setName("%s %s" % (name, wn), 4, 3, 1, 0x409)
        nt.setName("%s-%s" % (name, wn), 6, 3, 1, 0x409)
        nt.setName(name, 16, 3, 1, 0x409)
        nt.setName(wn, 17, 3, 1, 0x409)
        inst["OS/2"].usWeightClass = w
        sel = inst["OS/2"].fsSelection & ~0b1100001  # clear italic/bold/regular
        if wn == "Bold":
            sel |= 0b100000
            inst["head"].macStyle = 1
        elif wn == "Regular":
            sel |= 0b1000000
            inst["head"].macStyle = 0
        else:
            inst["head"].macStyle = 0
        inst["OS/2"].fsSelection = sel | (1 << 7)
        for t in ("STAT",):
            if t in inst:
                del inst[t]
        sp = os.path.join(pkg, "static", "%s-%s.ttf" % (name, wn))
        inst.save(sp)
    with open(os.path.join(pkg, "OFL.txt"), "w") as fh:
        fh.write(OFL.format(name=name))
    with open(os.path.join(pkg, "README.txt"), "w") as fh:
        fh.write("%s by fontzz\n\nvariable/  one file, every weight from 100 to 900\n"
                 "static/    nine fixed weights (Thin to Black)\nweb/       WOFF2 for the web\n\n"
                 "CSS:\n@font-face {\n  font-family: \"%s\";\n  src: url(\"%s[wght].woff2\") "
                 "format(\"woff2\");\n  font-weight: 100 900;\n  font-display: swap;\n}\n"
                 % (name, name, name))
    # site assets
    os.makedirs(os.path.join(SITE, "fonts"), exist_ok=True)
    os.makedirs(os.path.join(SITE, "downloads"), exist_ok=True)
    os.makedirs(os.path.join(SITE, "outlines"), exist_ok=True)
    shutil.copy(wv, os.path.join(SITE, "fonts", "%s.woff2" % key))
    zp = os.path.join(SITE, "downloads", "%s.zip" % name)
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(pkg):
            for fn in files:
                full = os.path.join(root, fn)
                z.write(full, os.path.join(name, os.path.relpath(full, pkg)))
    data = outline_json(key, spec)
    with open(os.path.join(SITE, "outlines", "%s.json" % key), "w") as fh:
        json.dump(data, fh, separators=(",", ":"))
    print("released", name, os.path.getsize(wv) // 1024, "KB woff2")


def bundle():
    """fontzz-all.zip: every released family package in one download."""
    zp = os.path.join(SITE, "downloads", "fontzz-all.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for key, spec in FAMILIES.items():
            name = spec["name"]
            pkg = os.path.join(build.OUT, key, "pkg", name)
            if not os.path.isdir(pkg):
                raise SystemExit("missing package for %s, release it first" % name)
            for root, _, files in os.walk(pkg):
                for fn in files:
                    full = os.path.join(root, fn)
                    z.write(full, os.path.join("fontzz", name, os.path.relpath(full, pkg)))
    print("bundled", len(FAMILIES), "families,", os.path.getsize(zp) // 1024, "KB")


if __name__ == "__main__":
    keys = sys.argv[1:] or list(FAMILIES)
    for k in keys:
        release(k)
    bundle()
