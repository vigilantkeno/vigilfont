#!/usr/bin/env python3
"""
Take the tail back off the l, and let the capital I carry the distinction.

The tail went on in #26 to separate l from I, and it worked. It also turned out
to be the wrong half of the pair to change. The tail is a shape the eye reads as
a mirrored J when nothing follows it, which is exactly the situation in the
wordmark, and it lands on the most frequent lowercase letter in English. The
nub crossbar on the I does the same measured work, 3.5 pixels of differing ink
at 16px against the tail's 3.4, on a letter that appears far less often and in
a shape nothing else in the alphabet claims.

This reverses the swap rather than redrawing anything, so `l` is once again
Figtree's plain l and `ss02` once again yields the tailed one, which is the
arrangement Figtree ships and the one Vigil had at 1.000. `ł` and the accented
`ĺ ľ ļ` follow their base.

The kerning added in 1.002 goes with the tail rather than staying behind. Those
pairs exist because the tail collides with anything carrying ink on the baseline
at its left, so they are retargeted onto the .ss02 forms; a plain l needs none
of them, and leaving them would put 48 units of daylight before every period.

Version goes to 1.004. Run from the repo root; rewrites fonts/ttf, fonts/otf and
fonts/*.woff2.
"""
import glob

from fontTools.ttLib import TTFont

OLD, NEW = "1.003", "1.004"
PAIRS = [("l", "l.ss02"), ("lslash", "lslash.ss02"),
         ("lacute", "lacute.ss02"), ("lcaron", "lcaron.ss02"),
         ("uni013C", "uni013C.ss02")]


def swap_gvar(font, a, b):
    var = font["gvar"].variations
    if a in var and b in var:
        var[a], var[b] = var[b], var[a]


def swap_outlines(font, a, b):
    """swap the drawings; composites are left alone because their base flips with them"""
    if "glyf" in font:
        g = font["glyf"]
        if g[a].isComposite() or g[b].isComposite():
            return False
        g[a], g[b] = g[b], g[a]
    else:
        cs = font["CFF "].cff.topDictIndex[0].CharStrings
        if a not in cs or b not in cs:
            return False
        cs[a], cs[b] = cs[b], cs[a]
    return True


def retarget_kerns(font):
    """the 1.002 pairs belong to the tail, so they move to wherever the tail is"""
    if "GPOS" not in font:
        return 0
    moved = 0
    swap = {a: b for a, b in PAIRS}
    for lk in font["GPOS"].table.LookupList.Lookup:
        if lk.LookupType != 2:
            continue
        for st in lk.SubTable:
            cov = getattr(st, "Coverage", None)
            if not cov or getattr(st, "Format", None) != 1:
                continue
            if not set(cov.glyphs) <= set(swap) or "l" not in cov.glyphs:
                continue
            gid = {g: i for i, g in enumerate(font.getGlyphOrder())}
            pairs = list(zip(cov.glyphs, st.PairSet))
            renamed = [(swap[a], ps) for a, ps in pairs if swap[a] in gid]
            renamed.sort(key=lambda kv: gid[kv[0]])
            cov.glyphs = [a for a, _ in renamed]
            st.PairSet = [ps for _, ps in renamed]
            st.PairSetCount = len(st.PairSet)
            moved += len(renamed)
    return moved


def bump(font):
    for rec in font["name"].names:
        if rec.nameID in (3, 5):
            s = rec.toUnicode()
            if OLD in s:
                rec.string = s.replace(OLD, NEW)
    font["head"].fontRevision = float(NEW)


def process(path):
    font = TTFont(path)
    ver = font["name"].getDebugName(5)
    assert ver == f"Version {OLD}", f"{path}: version is {ver}, refusing to run twice"
    if "gvar" in font:
        var = font["gvar"].variations           # gvar decompiles lazily against the
        for a, b in PAIRS:                      # old point counts, so read it first
            for n in (a, b):
                if n in var:
                    _ = var[n]
    h = font["hmtx"]
    swapped = []
    for a, b in PAIRS:
        if a not in h.metrics or b not in h.metrics:
            continue
        if swap_outlines(font, a, b):
            swapped.append(a)
            if "gvar" in font:
                swap_gvar(font, a, b)
        h[a], h[b] = h[b], h[a]
    n = retarget_kerns(font)
    bump(font)
    font.save(path)
    font = TTFont(path)                         # bounds are recalculated on save
    if "glyf" in font:
        for a, b in PAIRS:
            for name in (a, b):
                if name in font["hmtx"].metrics and not font["glyf"][name].isComposite():
                    font["hmtx"][name] = (font["hmtx"][name][0], font["glyf"][name].xMin)
        font.save(path)
    return swapped, n


if __name__ == "__main__":
    files = sorted(glob.glob("fonts/*.woff2") + glob.glob("fonts/ttf/*.ttf") + glob.glob("fonts/otf/*.otf"))
    assert len(files) == 58, f"expected 58 font files, found {len(files)}"
    for p in files:
        sw, n = process(p)
        print(f"  {p:44s} outlines swapped {len(sw)}, kern pairs retargeted {n}")
    print(f"\n{len(files)} files reverted and bumped to {NEW}")
