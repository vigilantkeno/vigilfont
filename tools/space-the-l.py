#!/usr/bin/env python3
"""
Space the tailed l: a tight bearing everywhere, and kerns where the tail collides.

PR #26 made Figtree's tailed `l.ss02` the default `l`, and it arrived with
Figtree's advance: the tail's tip sits on the advance edge, so the roman `l`
carries a right sidebearing of 0, and from weight 500 up a negative one. No
kern pair in Vigil began with `l`, so nothing compensated.

A single sidebearing cannot fix this, and that is the whole difficulty. After
this tail a straight stem and a round letter want clearances about 30 units
apart, measured as closest ink-to-ink approach. Setting the bearing wide enough
for `lb` throws `lo` and `ll` 20-30 units past the font's own rhythm and drains
the life out of the letter; setting it for `lo` leaves `lb` tight. So the
bearing is set tight, at 0.35x the one `n` carries, which is where round
letters and `ll` land on rhythm, and space is given back only by kerning, to
the handful of glyphs the tail genuinely runs into.

Those are the glyphs with ink on the baseline at their left: period, comma,
colon, semicolon, and `x` and `z`, whose lower-left strokes reach the baseline.
The period is the one that matters. It is the tightest common pair in the font,
and on the download heading, which sets 700 at letter-spacing -0.03em, the
shipped clearance is 25 units against a tracked rhythm of 76. Negative tracking
eats a wider bearing but cannot eat a kern, which is why a kern is the only
thing that fixes that heading.

Kerns are stored the way this font already stores them, varying down the weight
axis through the GDEF variation store, so punctuation does not go slack at
Black. Statics get their own exact value per file.

The script only ever loosens, and skips any face already in rhythm. The italics
are already right, because the slant carries the plain l's ink out to its own
advance edge, so they take no metric change and need no kern. The same guard
catches VigilOutline-Regular, whose l overhangs its advance.

lacute, lcaron and uni013C are composites of `l` and follow its advance and its
kerns. In the variable fonts the right phantom point in gvar is retuned so the
bearing holds at both ends of the axis. Every file's version goes to 1.002,
including faces whose metrics did not move, so the family keeps one version.
Run from the repo root; rewrites fonts/ttf, fonts/otf and fonts/*.woff2.
"""
import glob
import sys

from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables as ot
from fontTools.varLib.builder import buildVarData
from fontTools.varLib.instancer import instantiateVariableFont

BASE_FRAC = 0.35          # right sidebearing, as a fraction of n's
PUNCT = {".": 1.20, ",": 1.20, ":": 1.20, ";": 1.20, "x": 1.70, "z": 1.30}
MIN_KERN = 5              # skip pairs needing less than this
TOL = 4
OLD, NEW = "1.001", "1.002"
TAILED = ["l", "lslash"]
ACCENTED = ["lacute", "lcaron", "uni013C"]


def xmax(glyphset, name):
    bp = BoundsPen(glyphset)
    glyphset[name].draw(bp)
    return bp.bounds[2] if bp.bounds else None


def geometry(font):
    """n's right sidebearing and the base target that follows from it."""
    gs = font.getGlyphSet()
    nrsb = font["hmtx"]["n"][0] - xmax(gs, "n")
    return gs, nrsb, int(round(BASE_FRAC * nrsb))


def bump(font):
    for rec in font["name"].names:
        if rec.nameID in (3, 5):
            s = rec.toUnicode()
            if OLD in s:
                rec.string = s.replace(OLD, NEW)
    font["head"].fontRevision = float(NEW)


def set_metrics(font, gs, base):
    h, moved = font["hmtx"], {}
    for g in TAILED:
        if g in h.metrics:
            moved[g] = int(round(xmax(gs, g) + base))
            h[g] = (moved[g], h[g][1])
    for a in ACCENTED:
        if a in h.metrics:
            h[a] = (h["l"][0], h[a][1])
    if "CFF " in font:
        cs = font["CFF "].cff.topDictIndex[0].CharStrings
        for g in list(moved) + ACCENTED:
            if g in cs:
                cs[g].width = h[g][0]
    return moved


def retune_gvar(font, path, new_default):
    axis = font["fvar"].axes[0]
    assert axis.axisTag == "wght", path
    want = {}
    for peak, wval in ((1.0, axis.maxValue), (-1.0, axis.minValue)):
        inst = instantiateVariableFont(TTFont(path), {axis.axisTag: wval})
        gs, _, base = geometry(inst)
        want[peak] = {g: int(round(xmax(gs, g) + base)) for g in TAILED if g in inst["hmtx"].metrics}
    var = font["gvar"].variations
    for g in list(want[1.0]):
        for tv in var[g]:
            peak = tv.axes["wght"][1]
            if peak in want:
                tv.coordinates[-3] = (want[peak][g] - new_default[g], 0)
    for a in ACCENTED:
        if a in var:
            for tv in var[a]:
                match = [t for t in var["l"] if t.axes == tv.axes]
                assert len(match) == 1, (path, a, tv.axes)
                tv.coordinates[-3] = match[0].coordinates[-3]


def kern_values(font, gs, nrsb, path):
    """{(first, second): (default_value, delta_at_max_weight_or_None)}"""
    cmap, h = font.getBestCmap(), font["hmtx"]
    firsts = [g for g in TAILED + ACCENTED if g in h.metrics]
    at_max = None
    if "fvar" in font:
        axis = font["fvar"].axes[0]
        inst = instantiateVariableFont(TTFont(path), {axis.axisTag: axis.maxValue})
        gsm, nrsbm, basem = geometry(inst)
        # the advances this file will carry at max weight once gvar is retuned
        advm = {g: xmax(gsm, g) + basem for g in TAILED if g in inst["hmtx"].metrics}
        for a in ACCENTED:
            if a in inst["hmtx"].metrics:
                advm[a] = advm["l"]
        at_max = (nrsbm, {g: advm[g] - xmax(gsm, g) for g in advm})
    pairs = {}
    for ch, factor in PUNCT.items():
        if ord(ch) not in cmap:
            continue
        second = cmap[ord(ch)]
        for first in firsts:
            eff = h[first][0] - xmax(gs, first)
            need = int(round(factor * nrsb - eff))
            if need < MIN_KERN:
                continue
            delta = None
            if at_max:
                nrsbm, effm = at_max
                delta = int(round(factor * nrsbm - effm[first])) - need
            pairs[(first, second)] = (need, delta)
    return pairs


def add_kerning(font, pairs):
    """Append one PairPos lookup and hook it into every kern feature."""
    if not pairs or "GPOS" not in font:
        return 0
    tbl = font["GPOS"].table
    gid = {g: i for i, g in enumerate(font.getGlyphOrder())}
    varstore = getattr(font["GDEF"].table, "VarStore", None) if "GDEF" in font else None

    def device(delta):
        if not delta or varstore is None:
            return None
        vd = buildVarData([0], [[delta]], optimize=False)     # region 0: default -> max weight
        varstore.VarData.append(vd)
        varstore.VarDataCount = len(varstore.VarData)
        d = ot.Device()
        d.DeltaFormat = 0x8000                               # VARIATION_INDEX
        d.StartSize = len(varstore.VarData) - 1              # outer index
        d.EndSize = 0                                        # inner index
        return d

    firsts = sorted({a for a, _ in pairs}, key=lambda g: gid[g])
    pp = ot.PairPos()
    pp.Format = 1
    pp.Coverage = ot.Coverage()
    pp.Coverage.glyphs = firsts
    pp.ValueFormat1 = 0x0004 | (0x0040 if varstore is not None else 0)   # XAdvance [+ XAdvDevice]
    pp.ValueFormat2 = 0
    pp.PairSet = []
    for a in firsts:
        ps = ot.PairSet()
        ps.PairValueRecord = []
        for b in sorted((b for (x, b) in pairs if x == a), key=lambda g: gid[g]):
            value, delta = pairs[(a, b)]
            rec = ot.PairValueRecord()
            rec.SecondGlyph = b
            v = ot.ValueRecord()
            v.XAdvance = value
            if varstore is not None:
                v.XAdvDevice = device(delta)
            rec.Value1, rec.Value2 = v, None
            ps.PairValueRecord.append(rec)
        ps.PairValueCount = len(ps.PairValueRecord)
        pp.PairSet.append(ps)
    pp.PairSetCount = len(pp.PairSet)

    lk = ot.Lookup()
    lk.LookupType, lk.LookupFlag = 2, 0
    lk.SubTable, lk.SubTableCount = [pp], 1
    tbl.LookupList.Lookup.append(lk)
    idx = len(tbl.LookupList.Lookup) - 1
    tbl.LookupList.LookupCount = len(tbl.LookupList.Lookup)
    hooked = 0
    for fr in tbl.FeatureList.FeatureRecord:
        if fr.FeatureTag == "kern":
            fr.Feature.LookupListIndex.append(idx)
            fr.Feature.LookupCount = len(fr.Feature.LookupListIndex)
            hooked += 1
    assert hooked, "no kern feature to hook into"
    return len(pairs)


def process(path):
    font = TTFont(path)
    ver = font["name"].getDebugName(5)
    assert ver == f"Version {OLD}", f"{path}: version is {ver}, refusing to run twice"
    gs, nrsb, base = geometry(font)
    before = int(round(font["hmtx"]["l"][0] - xmax(gs, "l")))
    moved, npairs = {}, 0
    if before < base - TOL:
        moved = set_metrics(font, gs, base)
        if "gvar" in font:
            retune_gvar(font, path, moved)
        gs, nrsb, base = geometry(font)
        npairs = add_kerning(font, kern_values(font, gs, nrsb, path))
    bump(font)
    font.save(path)
    return before, base, moved, npairs


if __name__ == "__main__":
    files = sorted(glob.glob("fonts/*.woff2") + glob.glob("fonts/ttf/*.ttf") + glob.glob("fonts/otf/*.otf"))
    assert len(files) == 58, f"expected 58 font files, found {len(files)}"
    fixed = skipped = 0
    for p in files:
        before, base, moved, npairs = process(p)
        if moved:
            fixed += 1
            print(f"  fixed   {p:42s} RSB {before:4d} -> {base:3d}   l adv {moved['l']:4d}   {npairs} kern pairs")
        else:
            skipped += 1
            print(f"  in step {p:42s} RSB {before:4d} (target {base})")
    print(f"\n{fixed} respaced, {skipped} already in rhythm, {len(files)} bumped to {NEW}")
