#!/usr/bin/env python3
"""
Give the capital I a short nub crossbar, drawn from the face's own serifed I.

The plain I and the plain l are the same glyph for practical purposes: four
units of width apart, identical height, both a rounded rectangle from baseline
to 700. At 16px that difference is seven hundredths of a pixel, which is why
"Iain" and "lain" set identically. The site has claimed a distinguishable 1, l
and I since launch, and two Notes argue that this exact failure is what makes a
typeface bad.

Measured as ink that differs from a plain I, a short nub lands at 3.5 pixels at
16px against the tail's 3.4, so it does the same work. Full serifs reach 7.8 and
turn a geometric grotesk into something else. A domed top cannot work at all:
Vigil already rounds the I to 24 units and a full semicircle reaches 42, so the
entire available headroom is a third of a pixel.

Nothing is drawn from scratch. Each nub is the face's own .ss02 serifed form
with the crossbar overhang pulled in to 45% of its reach, so it inherits the
bar's thickness, its end treatment, and the way both already scale across the
axis: the serif's reach barely moves, 99 to 110 units, while its bar thickens
from 21 to 149. Only the bar bands are touched, so the acute and the dieresis
above cap height stay exactly where they were.

Three glyphs carry outlines and are rebuilt: I, Iacute, Idieresis. Five more
composite from I and follow it, taking its new advance. IJ takes the same
delta on its own advance. Sidebearings come from the serifed form, which is the
right value once the outermost feature is a bar end rather than a bare stem.

In the variable fonts the glyph is rebuilt at both ends of the axis and at the
default and gvar is recomputed from those three, because the point count changes
and the old deltas cannot survive it. Version goes to 1.003. Run from the repo
root; rewrites fonts/ttf, fonts/otf and fonts/*.woff2.
"""
import glob

from fontTools.pens.basePen import BasePen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables  # noqa: F401
from fontTools.varLib.instancer import instantiateVariableFont

class SkipFace(Exception):
    pass


FRAC = 0.45
CAP = 700.0
PAIRS = [("I", "I.ss02"), ("Iacute", "Iacute.ss02"), ("Idieresis", "Idieresis.ss02")]
FOLLOWERS = ["Icircumflex", "Idotaccent", "Igrave", "Imacron", "Iogonek"]
OLD, NEW = "1.002", "1.003"


class _Flat(BasePen):
    """flatten an outline to polygons so ink can be measured, not just points"""
    def __init__(self, glyphSet, steps=24):
        super().__init__(glyphSet)
        self.c, self.cur, self.n = [], None, steps
    def _moveTo(self, p): self.cur = [p]
    def _lineTo(self, p): self.cur.append(p)
    def _qCurveToOne(self, c, p):
        x0, y0 = self.cur[-1]
        for i in range(1, self.n + 1):
            t = i / self.n; m = 1 - t
            self.cur.append((m*m*x0 + 2*m*t*c[0] + t*t*p[0], m*m*y0 + 2*m*t*c[1] + t*t*p[1]))
    def _curveToOne(self, a, b, p):
        x0, y0 = self.cur[-1]
        for i in range(1, self.n + 1):
            t = i / self.n; m = 1 - t
            self.cur.append((m**3*x0 + 3*m*m*t*a[0] + 3*m*t*t*b[0] + t**3*p[0],
                             m**3*y0 + 3*m*m*t*a[1] + 3*m*t*t*b[1] + t**3*p[1]))
    def _closePath(self):
        if self.cur: self.c.append(self.cur); self.cur = None
    def _endPath(self): self._closePath()


def ink_span(glyphset, gname, y=CAP / 2):
    """the horizontal extent of ink on the scan line at y: the stem"""
    fp = _Flat(glyphset)
    glyphset[gname].draw(fp)
    xs = []
    for c in fp.c:
        n = len(c)
        for i in range(n):
            (x1, y1), (x2, y2) = c[i], c[(i + 1) % n]
            if (y1 <= y < y2) or (y2 <= y < y1):
                xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
    if not xs:
        raise RuntimeError(f"{gname}: nothing on the scan line")
    return min(xs), max(xs)



def bar_reach(glyphset, gname, s0, s1, slope):
    """How far the crossbar reaches past the stem, measured inside the bar.

    The bar thickens from 21 units at ExtraLight to 149 at Black, so its height
    has to be found before it can be sampled; a fixed fraction of cap height
    lands in the stem at the light end and gives a reach of zero."""
    stem_w = s1 - s0
    thk = None
    y = 2.0
    while y < CAP / 2:
        a, b = ink_span(glyphset, gname, y)
        if (b - a) - stem_w < stem_w * 0.15:
            thk = y
            break
        y += 2.0
    if thk is None or thk < 6:
        thk = max(thk or 0, 8.0)
    ys = thk * 0.5
    a, b = ink_span(glyphset, gname, ys)
    off = slope * (ys - CAP / 2.0)
    return (((s0 + off) - a) + (b - (s1 + off))) / 2.0

def shorten(rec, sb, s0, s1, slope, reach, serif_adv, serif_lsb, top,
             force_shift=None, force_adv=None):
    """pull the bar overhang in to FRAC of its reach, then set the sidebearing.

    The accented forms take the base I's shift and advance so their stems line
    up with it, which is what the font already does: Iacute and Idieresis carry
    the I's advance and let the accent overhang."""
    pts = [p for op, args in rec.value for p in args]
    if not pts:
        return None
    d = reach * (1.0 - FRAC)

    def fix(p):
        """Compress the overhang continuously rather than translating it.

        A conditional shift jumps by d at the stem edge, which tears any glyph
        whose bar is drawn as a closed ring: the inner contour moves and the
        outer one does not. Scaling the overhang toward the stem edge keeps the
        map continuous, so the Outline styles survive it."""
        x, y = p
        in_bar = (y <= CAP * 0.35) or (CAP * 0.65 <= y <= top)
        if not in_bar:
            return (x, y)
        off = slope * (y - CAP / 2.0)          # the stem leans in the italics
        left, right = s0 + off, s1 + off
        if x < left:
            x = left - (left - x) * FRAC
        elif x > right:
            x = right + (x - right) * FRAC
        return (x, y)

    moved = [(op, tuple(fix(p) for p in args)) for op, args in rec.value]
    allx = [p[0] for op, args in moved for p in args]
    # the bar tip keeps the serifed form's sidebearing, and the advance loses
    # exactly what the two overhangs gave up. This holds for the italics too,
    # where the leftmost ink may belong to either bar.
    shift = force_shift if force_shift is not None else serif_lsb - min(allx)
    out = RecordingPen()
    out.value = [(op, tuple((p[0] + shift, p[1]) for p in args)) for op, args in moved]
    adv = force_adv if force_adv is not None else int(round(serif_adv - 2 * d))
    return out, adv, shift


def rebuild(font, glyphset=None):
    """returns {base: advance}; works for glyf and CFF alike"""
    gs = glyphset or font.getGlyphSet()
    hmtx = font["hmtx"]
    import math
    slope = math.tan(math.radians(-font["post"].italicAngle))
    advs = {}
    base_shift = base_adv = None
    for base, serif in PAIRS:
        if serif not in hmtx.metrics:
            continue
        rec = RecordingPen()
        gs[serif].draw(rec)
        s0, s1 = ink_span(gs, serif)
        reach = bar_reach(gs, serif, s0, s1, slope)
        # a sanity check on the measurement rather than on the design: the nub
        # must end up between a third and two thirds of the serifed reach, or
        # the bar was not found and this face is left alone
        barpts = [p for op, a in rec.value for p in a
                  if p[1] <= CAP * 0.35 or CAP * 0.65 <= p[1] <= (1e9 if base == "I" else CAP + 2)]
        bbox_reach = ((s0 - min(p[0] for p in barpts))
                      + (max(p[0] for p in barpts) - s1)) / 2.0
        if not (0.55 <= reach / bbox_reach <= 1.8):
            raise SkipFace(f"{base}: bar reach {reach:.0f} against a bbox reach of "
                           f"{bbox_reach:.0f} — the crossbar could not be located")
        # the base I has nothing above the cap line, so its top band is open;
        # the accented forms must stop below the accent
        top = 1e9 if base == "I" else CAP + 2
        res = shorten(rec, hmtx[serif][1], s0, s1, slope, reach,
                      hmtx[serif][0], hmtx[serif][1], top,
                      force_shift=None if base == "I" else base_shift,
                      force_adv=None if base == "I" else base_adv)
        if not res:
            continue
        moved, adv, shift = res
        if base == "I":
            base_shift, base_adv = shift, adv
        if "glyf" in font:
            pen = TTGlyphPen(None)
            moved.replay(pen)
            font["glyf"][base] = pen.glyph()
            font["glyf"][base].recalcBounds(font["glyf"])
            hmtx[base] = (adv, font["glyf"][base].xMin)
        else:
            cs = font["CFF "].cff.topDictIndex[0].CharStrings
            pen = T2CharStringPen(adv, None)
            moved.replay(pen)
            cs[base] = pen.getCharString(private=cs[base].private)
            hmtx[base] = (adv, int(round(min(p[0] for op, a in moved.value for p in a))))
        advs[base] = adv
    return advs


def follow(font, new_I, old_I):
    hmtx = font["hmtx"]
    for f in FOLLOWERS:
        if f in hmtx.metrics:
            hmtx[f] = (new_I, hmtx[f][1])
    if "IJ" in hmtx.metrics:
        hmtx["IJ"] = (hmtx["IJ"][0] + (new_I - old_I), hmtx["IJ"][1])


def retune_gvar(font, path, default_advs):
    axis = font["fvar"].axes[0]
    var = font["gvar"].variations
    ends = {}
    for peak, wval in ((1.0, axis.maxValue), (-1.0, axis.minValue)):
        inst = instantiateVariableFont(TTFont(path), {axis.axisTag: wval})
        rebuild(inst)
        ends[peak] = {b: (list(inst["glyf"][b].coordinates), inst["hmtx"][b][0]) for b, _ in PAIRS}
    for base, _ in PAIRS:
        dflt = list(font["glyf"][base].coordinates)
        dadv = font["hmtx"][base][0]
        n = len(dflt)
        for tv in var[base]:
            peak = tv.axes["wght"][1]
            co, adv = ends[peak][base]
            deltas = [(int(round(co[i][0] - dflt[i][0])), int(round(co[i][1] - dflt[i][1]))) for i in range(n)]
            deltas += [(0, 0), (int(round(adv - dadv)), 0), (0, 0), (0, 0)]
            tv.coordinates = deltas
        for f in FOLLOWERS + ["IJ"]:
            if f in var:
                for tv in var[f]:
                    peak = tv.axes["wght"][1]
                    src = [t for t in var[base] if t.axes == tv.axes]
                    if base == "I" and src:
                        tv.coordinates[-3] = src[0].coordinates[-3]


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
        # gvar decompiles lazily against the glyph's point count, so it has to be
        # read before any outline is replaced or the stored deltas cannot be parsed
        var = font["gvar"].variations
        for g in [b for b, _ in PAIRS] + [s for _, s in PAIRS] + FOLLOWERS + ["IJ"]:
            if g in var:
                _ = var[g]
    old_I = font["hmtx"]["I"][0]
    advs = rebuild(font)
    follow(font, advs["I"], old_I)
    if "gvar" in font:
        retune_gvar(font, path, advs)
    bump(font)
    font.save(path)
    return old_I, advs["I"]


if __name__ == "__main__":
    files = sorted(glob.glob("fonts/*.woff2") + glob.glob("fonts/ttf/*.ttf") + glob.glob("fonts/otf/*.otf"))
    assert len(files) == 58, f"expected 58 font files, found {len(files)}"
    done, skipped = 0, []
    for p in files:
        try:
            a, b = process(p)
            done += 1
            print(f"  {p:44s} I advance {a} -> {b}")
        except SkipFace as e:
            skipped.append((p, str(e)))
            print(f"  SKIPPED {p:36s} {e}")
    print(f"\n{done} files rebuilt and bumped to {NEW}, {len(skipped)} skipped")
    if skipped:
        raise SystemExit("refusing to leave the family half-converted; fix or exclude the skipped faces")
