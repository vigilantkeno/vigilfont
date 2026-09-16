#!/usr/bin/env python3
"""
Finish the tailed-l swap (follow-up to tools/tail-the-l.py, fonts 1.001).

Run on files in the state #26 left them: l and l.ss02 swapped, the three
accented composites (lacute, lcaron, uni013C) given the tailed advance but
still carrying the accent where the plain stem had it, and their .ss02
siblings untouched (tailed advance, tailed accent offset, plain base).

For each pair (X, X.ss02) the accent offsets and the gvar deltas change
places, so X shows Figtree's accent position for the tailed form and X.ss02
the plain one; the base components stay (X keeps `l`, tailed; X.ss02 keeps
`l.ss02`, plain). X.ss02 then takes the plain advance from `l.ss02`, in the
variable fonts including the advance deltas. Figtree also draws a tailed ł
as `lslash.ss02`, so ł is swapped the way l was. CFF fonts swap ł and rebuild
the six accented charstrings from base plus accent at the corrected offsets.

Done-marker: lacute.ss02 carrying l.ss02's advance. Refuses to run twice.
"""
import glob
import os

from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

PAIRS = [("lacute", "lacute.ss02"), ("lcaron", "lcaron.ss02"), ("uni013C", "uni013C.ss02")]
SWAP = [("lslash", "lslash.ss02")]
NAMES = [n for pair in PAIRS + SWAP for n in pair]


def phantom_right(tvs, axes):
    match = [t for t in tvs if t.axes == axes]
    assert len(match) == 1, axes
    return match[0].coordinates[-3]


def fix_ttf(path):
    f = TTFont(path)
    g, h = f["glyf"], f["hmtx"]
    assert f["name"].getDebugName(5) == "Version 1.001", path
    assert h["lacute.ss02"][0] != h["l.ss02"][0], f"{path}: already finished"
    gv = f["gvar"].variations if "gvar" in f else None
    keep = {n: gv[n] for n in NAMES + ["l", "l.ss02"]} if gv else {}
    for a, b in SWAP:
        g[a], g[b] = g[b], g[a]
        h[a], h[b] = h[b], h[a]
        if gv:
            gv[a], gv[b] = keep[b], keep[a]
    for a, b in PAIRS:
        assert g[a].components[0].glyphName == "l" and g[b].components[0].glyphName == "l.ss02", (path, a)
        ca, cb = g[a].components[1], g[b].components[1]
        (ca.x, ca.y), (cb.x, cb.y) = (cb.x, cb.y), (ca.x, ca.y)
        assert h[a][0] == h["l"][0], (path, a, "expected the tailed advance from #26")
        h[b] = (h["l.ss02"][0], h[b][1])
        if gv:
            gv[a], gv[b] = keep[b], keep[a]
            for tv in gv[b]:
                tv.coordinates[-3] = phantom_right(keep["l.ss02"], tv.axes)
            for tv in gv[a]:
                tv.coordinates[-3] = phantom_right(keep["l"], tv.axes)
    f.save(path)
    f = TTFont(path)
    for n in NAMES:
        f["hmtx"][n] = (f["hmtx"][n][0], f["glyf"][n].xMin)
    f.save(path)


def fix_otf(path, ttf_path):
    f, t = TTFont(path), TTFont(ttf_path)
    cff = f["CFF "].cff
    td = cff.topDictIndex[0]
    cs, h = td.CharStrings, f["hmtx"]
    assert h["lacute.ss02"][0] != h["l.ss02"][0], f"{path}: already finished"
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
    print(f"  {len(ttfs)} TrueType files: ł swapped, accent offsets exchanged, .ss02 widths plain")
    for p in sorted(glob.glob("fonts/otf/*.otf")):
        fix_otf(p, "fonts/ttf/" + os.path.basename(p)[:-4] + ".ttf")
    print("  18 OTFs: ł swapped, six accented charstrings rebuilt")
    for p in ttfs:
        woff2(p)
    print(f"  {len(glob.glob('fonts/*.woff2'))} woff2 regenerated")
