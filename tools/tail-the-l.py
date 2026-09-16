#!/usr/bin/env python3
"""
Make the tailed l the default form, and the plain l the ss02 alternate.

The site says, in nine places, that Vigil's 1, l and I can be told apart. The
1 has its flag, but the default l was a rectangle identical to the I. Figtree
already draws a tailed l as stylistic set 2 (`l.ss02`), so this swaps the two
glyphs rather than drawing anything: outlines, metrics and, in the variable
fonts, the gvar deltas change places, so every kerning pair and feature that
named `l` keeps working and `ss02` now yields the plain form. No pair kerning
touched either glyph, and no ligature involves l, which is why the swap is
safe. The three accented composites that reference `l` (lacute, lcaron,
uni013C) take the tailed advance; in the CFF fonts, where accented glyphs are
subroutine-built outlines rather than composites, they are rebuilt from the
tailed l plus the accent at the composite offsets the TrueType statics record.
Version goes to 1.001. Run from the repo root; it rewrites fonts/ttf, fonts/otf
and fonts/*.woff2 in place.
"""
import glob
import os
import sys

from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ACCENTED = ["lacute", "lcaron", "uni013C"]
OLD, NEW = "1.000", "1.001"


def bump(font):
    for rec in font["name"].names:
        if rec.nameID in (3, 5):
            s = rec.toUnicode()
            if OLD in s:
                rec.string = s.replace(OLD, NEW)
    font["head"].fontRevision = float(NEW)


def fix_ttf(path):
    f = TTFont(path)
    assert "HVAR" not in f, path
    assert f["name"].getDebugName(5) == f"Version {OLD}", f"{path}: already at {f['name'].getDebugName(5)}, refusing to swap twice"
    g, h = f["glyf"], f["hmtx"]
    if "gvar" in f:                       # decompile against the original point counts first
        v = f["gvar"].variations
        keep = {n: v[n] for n in ["l", "l.ss02"] + ACCENTED}
    g["l"], g["l.ss02"] = g["l.ss02"], g["l"]
    h["l"], h["l.ss02"] = h["l.ss02"], h["l"]
    if "gvar" in f:
        v["l"], v["l.ss02"] = keep["l.ss02"], keep["l"]
    for n in ACCENTED:
        assert g[n].isComposite() and g[n].components[0].glyphName == "l", (path, n)
        h[n] = (h["l"][0], h[n][1])
        if "gvar" in f:
            for tv in f["gvar"].variations[n]:
                match = [t for t in f["gvar"].variations["l"] if t.axes == tv.axes]
                assert len(match) == 1, (path, n, tv.axes)
                tv.coordinates[-3] = match[0].coordinates[-3]      # right phantom point = advance
    bump(f)
    f.save(path)
    f = TTFont(path)                      # bboxes were recalculated on save; align lsb with them
    for n in ["l", "l.ss02"] + ACCENTED:
        f["hmtx"][n] = (f["hmtx"][n][0], f["glyf"][n].xMin)
    f.save(path)
    return f["hmtx"]["l"][0]


def fix_otf(path, ttf_path):
    f, t = TTFont(path), TTFont(ttf_path)
    assert f["name"].getDebugName(5) == f"Version {OLD}", f"{path}: already at {f['name'].getDebugName(5)}, refusing to swap twice"
    cff = f["CFF "].cff
    td = cff.topDictIndex[0]
    cs, h = td.CharStrings, f["hmtx"]
    cs["l"], cs["l.ss02"] = cs["l.ss02"], cs["l"]
    h["l"], h["l.ss02"] = h["l.ss02"], h["l"]
    width = h["l"][0]
    for n in ACCENTED:
        pen = T2CharStringPen(width, None)
        for c in t["glyf"][n].components:
            cs[c.glyphName].draw(TransformPen(pen, (1, 0, 0, 1, c.x, c.y)))
        new = pen.getCharString(private=td.Private, globalSubrs=cff.GlobalSubrs)
        new.private, new.globalSubrs = td.Private, cff.GlobalSubrs
        cs[n] = new
        h[n] = (width, int(round(new.calcBounds(cs)[0])))
    bump(f)
    f.save(path)


def woff2(ttf_path):
    name = os.path.basename(ttf_path)[:-4].replace("[wght]", "-wght-")
    f = TTFont(ttf_path)
    f.flavor = "woff2"
    f.save(f"fonts/{name}.woff2")


if __name__ == "__main__":
    ttfs = sorted(glob.glob("fonts/ttf/*.ttf"))
    for p in ttfs:
        adv = fix_ttf(p)
        print(f"  {os.path.basename(p):28} l advance now {adv}")
    for p in sorted(glob.glob("fonts/otf/*.otf")):
        fix_otf(p, "fonts/ttf/" + os.path.basename(p)[:-4] + ".ttf")
        print(f"  {os.path.basename(p):28} charstrings swapped, accented l rebuilt")
    for p in ttfs:
        woff2(p)
    print(f"  {len(glob.glob('fonts/*.woff2'))} woff2 regenerated")
