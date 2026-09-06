# Vigil

A softened geometric grotesk for body copy. Designed by Joaquin Keno Vigil, 2026.
Derived from Figtree (Erik Kennedy) under the SIL Open Font License 1.1.

## Files

Desktop formats and web formats are kept in separate folders, so you can select
everything inside any one folder without picking up files your system can't use.

- ttf/            16 static instances (ExtraLight → Black, roman + italic), hinted — install these
- otf/            the same 16 as CFF OpenType, plus Vigil Outline Regular + Italic — install these instead if you prefer OTF
- woff2/          the same 16 statics for the web — do not install these
- variable/ttf/   Vigil[wght] and Vigil-Italic[wght] — one axis, wght 200–900 — install these
- variable/woff2/ the same two for the web
- outline/ttf/    Vigil Outline Regular + Italic — a display style stroked from Bold; 40px and up only
- outline/woff2/  the same two for the web
- Vigil-specimen.html  single-file specimen with a live weight slider

## Install

Mac — open ttf/ (or otf/), select the files, double-click, Install Font.
Windows — open ttf/ (or otf/), select the files, right-click, Install.

Install either the 16 statics or the variable font, not both. Both declare the
family name "Vigil", so installing both gives you two entries competing for the
same name in your font menu.

Never install anything from a woff2/ folder. Those are web files; your system
will reject them.

## Weights
ExtraLight 200 is extrapolated beyond the drawn masters and is a display weight: 40px and above, never for body copy.
Vigil Outline is a separate style, not a point on the weight axis: a 22-unit round-joined stroke on the Bold outlines. Family name "Vigil Outline".
Static TTFs are hinted (ttfautohint) for Windows; OTF, variable, and Outline are unhinted.

## Web use
One line, no download:

    <link rel="stylesheet" href="https://www.vigilfont.com/vigil.css">

Then font-family: "Vigil". Or self-host the files in woff2/ with your own @font-face
block — the specimen has one you can copy.

## Design rules
- Base: Figtree geometric skeleton, large x-height, double-story a, single-story g
- Rounding by hierarchy: 22 units at exposed terminals, 10 at structural corners, 4 inside joins; none on punctuation; t and f held to the structural level
- Spacing and kerning inherited from Figtree unchanged

## License
SIL Open Font License 1.1 — free for personal and commercial use, including embedding and web use. See OFL.txt.
