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

**1.0.1 / fonts 1.001.** The lowercase `l` now has a tail by default, so `l` and `I` read apart; `ĺ ľ ļ` follow. Stylistic set 2 (`ss02`) is reversed and now gives the plain `l`. `ł` keeps its plain stem.

SIL Open Font License 1.1. Use it anywhere, commercial or not, no attribution required. Derived from [Figtree](https://github.com/erikdkennedy/figtree) by Erik Kennedy.
