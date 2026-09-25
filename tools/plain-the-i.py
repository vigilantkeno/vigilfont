#!/usr/bin/env python3
"""
Give the capital I back its plain stem: Figtree's own rounded rectangle.

The nub crossbar of 1.003 was drawn as the serifed .ss02 I with its overhang
pulled in to 45% at every weight. The serif's reach barely grows across the
axis (99 to 110 units) while its bar thickens from 21 to 149, so at Black the
nub is 52 units wide and 149 tall: a stub taller than it is wide, which reads
as a notch cut into the stem rather than as a crossbar. Keno chose the plain
stem over a nub that lengthens with weight (2026-09-25).

Distinguishing I from l and 1 moves onto ss02, which already carries the
full-serif I and the tailed l. The default I and l are once again the same
shape at different widths, as in Figtree, Helvetica and Inter.

Nothing is drawn. The nine glyphs the nub touched (I, Iacute, Idieresis, the
five accented composites and IJ) are copied back from the 1.002 files, the last
build before the nub, where they are still Figtree's: outlines, advances and,
in the variable fonts, their gvar deltas. Everything else stays at 1.004,
including the plain l and the kerning retargeted onto the .ss02 forms. OTF
outlines are replayed through a pen rather than copied, because the old
charstrings call local subroutines that belong to the old file.

Version goes to 1.005. Run from the repo root; rewrites fonts/ttf, fonts/otf
and the sans woff2 files in fonts/.
"""
import copy
import glob
import io
import subprocess

from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib import TTFont

SOURCE = "835d567^"          # 1.002: the last build with Figtree's plain I
GLYPHS = ["I", "Iacute", "Idieresis", "Icircumflex", "Idotaccent",
          "Igrave", "Imacron", "Iogonek", "IJ"]
OLD, NEW = "1.004", "1.005"


def old_font(path):
    return TTFont(io.BytesIO(subprocess.check_output(["git", "show", f"{SOURCE}:{path}"])))


def process(path):
    font = TTFont(path)
    ver = font["name"].getDebugName(5)
    assert ver == f"Version {OLD}", f"{path}: version is {ver}, refusing to run twice"
    src = old_font(path)
    assert src.getGlyphOrder() == font.getGlyphOrder(), f"{path}: glyph order moved since {SOURCE}"
    if "gvar" in font:
        assert src["fvar"].axes[0].__dict__ == font["fvar"].axes[0].__dict__
        var, svar = font["gvar"].variations, src["gvar"].variations
        for g in GLYPHS:
            _ = var[g], svar[g]      # decompile against the current point counts first
    if "glyf" in font:
        for g in GLYPHS:
            font["glyf"][g] = copy.deepcopy(src["glyf"][g])
    else:
        cs = font["CFF "].cff.topDictIndex[0].CharStrings
        sgs = src.getGlyphSet()
        for g in GLYPHS:
            rec = RecordingPen()
            sgs[g].draw(rec)
            pen = T2CharStringPen(src["hmtx"][g][0], None, roundTolerance=0)
            rec.replay(pen)
            cs[g] = pen.getCharString(private=cs[g].private)
    for g in GLYPHS:
        font["hmtx"][g] = src["hmtx"][g]
        if "gvar" in font:
            font["gvar"].variations[g] = copy.deepcopy(src["gvar"].variations[g])
    for rec in font["name"].names:
        if rec.nameID in (3, 5):
            s = rec.toUnicode()
            if OLD in s:
                rec.string = s.replace(OLD, NEW)
    font["head"].fontRevision = float(NEW)
    font.save(path)
    return src["hmtx"]["I"][0]


if __name__ == "__main__":
    files = sorted(p for p in glob.glob("fonts/*.woff2") + glob.glob("fonts/ttf/*.ttf")
                   + glob.glob("fonts/otf/*.otf") if "Serif" not in p)
    assert len(files) == 58, f"expected 58 sans font files, found {len(files)}"
    for p in files:
        print(f"  {p:44s} I advance -> {process(p)}")
    print(f"\n{len(files)} files rebuilt and bumped to {NEW}")
