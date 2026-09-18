# vigil-font

A free softened geometric grotesk. Eight weights with matching italics, an outline style, and a continuous 200–900 variable axis.

```bash
npm install vigil-font
```

```css
@import "vigil-font/vigil.css";
```

Then `font-family: "Vigil", sans-serif`. The weight axis is continuous, so `font-weight: 437` is a real value.

No build step needed — you can skip npm entirely and use the hosted copy:

```html
<link rel="stylesheet" href="https://www.vigilfont.com/vigil.css">
```

Pairs with [Vigil Icons](https://www.vigilicons.com/) — 111 free stroke icons on the same 24px grid.

## Changes

**1.0.4 / fonts 1.004.** The tail comes off the lowercase `l` and the capital `I` takes a short crossbar instead. `ss02` goes back to giving the tailed `l`, as at 1.000, and now also gives the plain `I`.

**1.0.2 / fonts 1.002 (not released).** The tailed `l` is spaced properly: it shipped with no right sidebearing, so it crowded the next letter and above SemiBold its tail crossed into it. The bearing is now tight, with kerning giving space back before `.` `,` `:` `;` `x` `z`. No letterform changed.

**1.0.1 / fonts 1.001.** The lowercase `l` now has a tail by default, so `l` and `I` read apart; `ĺ ľ ļ` follow. Stylistic set 2 (`ss02`) is reversed and now gives the plain `l`. `ł` follows.

SIL Open Font License 1.1. Use it anywhere, commercial or not, no attribution required. Derived from [Figtree](https://github.com/erikdkennedy/figtree) by Erik Kennedy.
