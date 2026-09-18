#!/usr/bin/env python3
"""Build glyphs.json for /glyphs from the shipped web fonts.

Only the codepoint and the glyph name go in the file. The character follows
from the codepoint, the Unicode block follows from a table the page carries,
and the metrics are measured live in the browser with canvas measureText at
whatever weight is on screen — which is both smaller and better than shipping
a fixed table, because the numbers then move with the slider.

    python3 tools/build-glyph-index.py        # writes glyphs.json
"""
import json
import os
from fontTools.ttLib import TTFont

FAMILIES = {
    "sans":  {"roman": "fonts/Vigil-wght-.woff2",
              "italic": "fonts/Vigil-Italic-wght-.woff2"},
    "serif": {"roman": "fonts/VigilSerif-wght-.woff2",
              "italic": "fonts/VigilSerif-Italic-wght-.woff2"},
}

out = {}
for family, styles in FAMILIES.items():
    out[family] = {}
    for style, path in styles.items():
        f = TTFont(path)
        rows = [[cp, name] for cp, name in sorted(f.getBestCmap().items()) if cp >= 0x20]
        out[family][style] = rows
        print(f"{family:5s} {style:6s} {len(rows):5d} glyphs  {f['name'].getDebugName(5)}")

with open("glyphs.json", "w") as fh:
    json.dump(out, fh, separators=(",", ":"))
print(f"\nglyphs.json {os.path.getsize('glyphs.json')/1024:.0f} KB")
