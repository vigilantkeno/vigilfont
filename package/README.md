# vigil-font

Two free companion typefaces. **Vigil**, a softened geometric grotesk, and **Vigil Serif**, reproportioned to share its cap height, x-height and line box so the two set as one system. Eight weights with matching italics each, an outline style, and continuous 200–900 variable axes.

```bash
npm install vigil-font
```

```css
@import "vigil-font/vigil.css";
```

Then `font-family: "Vigil", sans-serif` or `font-family: "Vigil Serif", serif`. One stylesheet declares both, plus `"Vigil Outline"`. The weight axes are continuous, so `font-weight: 437` is a real value.

Set the serif at 300 against the sans at 400 and they match stem for stem.

No build step needed — you can skip npm entirely and use the hosted copy:

```html
<link rel="stylesheet" href="https://www.vigilfont.com/vigil.css">
```

Pairs with [Vigil Icons](https://www.vigilicons.com/) — 111 free stroke icons on the same 24px grid.

## Changes

**1.4.0 / Vigil 1.005, Vigil Serif 1.300.** The sans's capital `I` goes back to a plain stem; the short crossbar read as a notch from Bold up. Turn on `ss02` (`font-feature-settings: "ss02" 1`) for a serifed `I` and a tailed `l` wherever the two must not be confused.

**1.3.0 / Vigil 1.004, Vigil Serif 1.300.** Vigil Serif gains the eight hooked letters Fulah and
Hausa need — `ɓ ɗ ƙ ƴ Ɓ Ɗ Ƙ Ƴ` — drawn in all four masters and carried through every weight, with
their spacing and kerning. The seven West African orthographies the font set out to cover now all
set, and the font passes Google Fonts' own quality profile without a failing check.

**1.2.0 / Vigil 1.004, Vigil Serif 1.200.** Vigil Serif gains the Latin letters seven West
African orthographies need — the open o and open e in both cases (`ɔ Ɔ ɛ Ɛ`), m and n with
acute and grave, and the combining vertical line below — so Yoruba, Bambara, Dyula, Fanti and
Akuapem Twi set correctly. Fulah and Hausa still want the hooked letters, which are planned.

**1.1.0 / Vigil 1.004, Vigil Serif 1.100.** Vigil Serif joins the package: `vigil.css` now declares it alongside the sans and the outline, and the serif's variable roman and italic ship with it. Its axis runs 200 to 900 — eight weights, an ExtraLight at each end of the pairing.

**1.0.4 / fonts 1.004.** The tail comes off the lowercase `l` and the capital `I` takes a short crossbar instead. `ss02` goes back to giving the tailed `l`, as at 1.000; the full-serif `I` stays on it.

**1.0.2 / fonts 1.002 (not released).** The tailed `l` is spaced properly: it shipped with no right sidebearing, so it crowded the next letter and above SemiBold its tail crossed into it. The bearing is now tight, with kerning giving space back before `.` `,` `:` `;` `x` `z`. No letterform changed.

**1.0.1 / fonts 1.001.** The lowercase `l` now has a tail by default, so `l` and `I` read apart; `ĺ ľ ļ` follow. Stylistic set 2 (`ss02`) is reversed and now gives the plain `l`. `ł` follows.

SIL Open Font License 1.1. Use it anywhere, commercial or not, no attribution required. Vigil and Vigil Outline are derived from [Figtree](https://github.com/erikdkennedy/figtree) by Erik Kennedy; Vigil Serif is derived from [Vollkorn](https://github.com/FAlthausen/Vollkorn-Typeface) by Friedrich Althausen. Both upstream copyrights travel in `OFL.txt` and in every font file.
