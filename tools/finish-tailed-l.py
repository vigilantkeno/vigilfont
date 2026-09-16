#!/usr/bin/env python3
"""
Finish the tailed-l swap (follow-up to tools/tail-the-l.py, fonts 1.001).

Two things the first pass left half done. The accented composites were given
the tailed advance but kept the accent where the plain stem had it; Figtree
positions the comma of ļ differently under the tailed form (its `uni013C.ss02`
carries the offset), and the `.ss02` accented composites still had the tailed
advance on what is now the plain stem. Each pair (X, X.ss02) now exchanges
accent offsets, advances and, in the variable fonts, gvar deltas, while the
base component names stay (X keeps `l`, which is tailed; X.ss02 keeps `l.ss02`,
which is plain). And Figtree does draw a tailed ł as `lslash.ss02`, so ł is
swapped the same way l was. CFF fonts rebuild the six accented charstrings from
base plus accent at the corrected offsets. Refuses to run twice.
"""
import glob
import os

from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

PAIRS = [("lacute", "lacute.ss02"), ("lcaron", "lcaron.ss02"), ("uni013C", "uni013C.ss02")]
SWAP = [("lslash", "lslash.ss02")]


def fix_ttf(path):
    f = TTFont(path)
    g, h = f["glyf"], f["hmtx"]
    assert h["uni013C.ss02"][0] >= h["uni013C"][0] and g["lslash"].yMin >= 0, f"{path}: already finished"
    gv = f["gvar"].variations if "gvar" in f else None
    names = [n for pair in PAIRS + SWAP for n in pair]
    keep = {n: gv[n] for n in names} if gv else {}
    for a, b in SWAP:                                   # ł: whole glyph, like l
        g[a], g[b] = g[b], g[a]
        h[a], h[b] = h[b], h[a]
        if gv:
            gv[a], gv[b] = keep[b], keep[a]
    for a, b in PAIRS:                                  # accents: offsets and metrics, bases stay
        ca, cb = g[a].components[1], g[b].components[1]
        (ca.x, ca.y), (cb.x, cb.y) = (cb.x, cb.y), (ca.x, ca.y)
        h[a], h[b] = h[b], h[a]
        if gv:
            gv[a], gv[b] = keep[b], keep[a]
    f.save(path)
    f = TTFont(path)
    for n in names:
        f["hmtx"][n] = (f["hmtx"][n][0], f["glyf"][n].xMin)
    f.save(path)


def fix_otf(path, ttf_path):
    f, t = TTFont(path), TTFont(ttf_path)
    cff = f["CFF "].cff
    td = cff.topDictIndex[0]
    cs, h = td.CharStrings, f["hmtx"]
    assert h["uni013C.ss02"][0] >= h["uni013C"][0], f"{path}: already finished"
    for a, b in SWAP:
        cs[a], cs[b] = cs[b], cs[a]
        h[a], h[b] = h[b], h[a]
    for pair in PAIRS:
        for n in pair:
            width = t["hmtx"][n][0]
            pen = T2CharStringPen(width, None)
            for c in t["glyf"][n].components:
                cs[c.glyphName].draw(TransformPen(pen, (1, 0, 0, 1, c.x, c.y)))
            new = pen.getCharString(private=td.Private, globalSubrs=cff.GlobalSubrs)
            new.private, new.globalSubrs = td.Private, cff.GlobalSubrs
            cs[n] = new
            h[n] = (width, int(round(new.calcBounds(cs)[0])))
    f.save(path)


def woff2(ttf_path):
    name = os.path.basename(ttf_path)[:-4].replace("[wght]", "-wght-")
    f = TTFont(ttf_path)
    f.flavor = "woff2"
    f.save(f"fonts/{name}.woff2")


if __name__ == "__main__":
    ttfs = sorted(glob.glob("fonts/ttf/*.ttf"))
    for p in ttfs:
        fix_ttf(p)
    print(f"  {len(ttfs)} TrueType files: ł swapped, accented pairs exchanged")
    for p in sorted(glob.glob("fonts/otf/*.otf")):
        fix_otf(p, "fonts/ttf/" + os.path.basename(p)[:-4] + ".ttf")
    print("  18 OTFs: ł swapped, six accented charstrings rebuilt")
    for p in ttfs:
        woff2(p)
    print(f"  {len(glob.glob('fonts/*.woff2'))} woff2 regenerated")
