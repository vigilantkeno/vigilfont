# Install Vigil

Vigil is a free variable typeface under the SIL Open Font License 1.1. No account, no API key, no attribution required in your designs.

| | |
|---|---|
| CSS family name | `Vigil` |
| Weight axis | 200–900, continuous (`font-weight: 437` is valid) |
| Italic | Yes, on the same axis |
| Second family | `Vigil Outline` (weight 700, roman and italic) |
| Hosted stylesheet | `https://www.vigilfont.com/vigil.css` |
| CORS | `Access-Control-Allow-Origin: *` on fonts and CSS, so hotlinking works from any domain |
| License | SIL Open Font License 1.1 (`OFL-1.1`) |

## 1. One line of HTML

The fastest path. No download, no build step.

```html
<link rel="stylesheet" href="https://www.vigilfont.com/vigil.css">
```

```css
body { font-family: "Vigil", sans-serif; }
```

## 2. Plain CSS

Paste this anywhere. It works hotlinked as written, or change the URLs to your own paths after downloading the two files.

```css
@font-face {
  font-family: "Vigil";
  src: url("https://www.vigilfont.com/fonts/Vigil-wght-.woff2") format("woff2");
  font-weight: 200 900;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: "Vigil";
  src: url("https://www.vigilfont.com/fonts/Vigil-Italic-wght-.woff2") format("woff2");
  font-weight: 200 900;
  font-style: italic;
  font-display: swap;
}
```

Two files cover all eight weights and both slopes. You do not need the static files unless you are supporting browsers without variable font support.

## 3. Tailwind CSS

Tailwind v4, in your CSS entry point:

```css
@import "tailwindcss";
@import url("https://www.vigilfont.com/vigil.css");

@theme {
  --font-vigil: "Vigil", ui-sans-serif, system-ui, sans-serif;
}
```

Then use `font-vigil`. For Tailwind v3, in `tailwind.config.js`:

```js
export default {
  theme: {
    extend: {
      fontFamily: { vigil: ['Vigil', 'ui-sans-serif', 'system-ui', 'sans-serif'] },
    },
  },
}
```

## 4. Next.js

Self-hosted with `next/font/local`, which is the recommended path because it removes the network request and the layout shift. Download the two variable files into `app/fonts/` first.

```tsx
// app/layout.tsx
import localFont from "next/font/local";

const vigil = localFont({
  src: [
    { path: "./fonts/Vigil-wght-.woff2", weight: "200 900", style: "normal" },
    { path: "./fonts/Vigil-Italic-wght-.woff2", weight: "200 900", style: "italic" },
  ],
  variable: "--font-vigil",
  display: "swap",
});

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={vigil.variable}>
      <body style={{ fontFamily: "var(--font-vigil)" }}>{children}</body>
    </html>
  );
}
```

```bash
curl -O https://www.vigilfont.com/fonts/Vigil-wght-.woff2
curl -O https://www.vigilfont.com/fonts/Vigil-Italic-wght-.woff2
```

## 5. Vite, React, Svelte, or any bundler

Put the two woff2 files in your static or public directory, then paste the `@font-face` blocks from section 2 with local paths into your global stylesheet. Import that stylesheet once at your app entry point.

## 6. Desktop, for Figma, Sketch, Word or Illustrator

```
https://www.vigilfont.com/downloads/Vigil.zip
```

About 2.4 MB. Unzip it, select the `Vigil-*.ttf` files at the top level, and double-click to install. On Windows, extract the zip before installing; Windows will not install fonts from inside an archive. Figma and Sketch read your installed system fonts, so quit and reopen the desktop app afterwards. Figma in the browser needs their font installer running.

## Using the variable axis

The weight axis is continuous, so any integer between 200 and 900 is real.

```css
.lede { font-weight: 437; }
```

Named weights map as: ExtraLight 200, Light 300, Regular 400, Medium 500, SemiBold 600, Bold 700, ExtraBold 800, Black 900.

## Optional typographic features

```css
/* single-storey a */
.alt-a { font-feature-settings: "ss01" 1; }

/* tabular figures, for tables and timers */
.numbers { font-variant-numeric: tabular-nums; }
```

Vigil also carries fractions, superscripts and subscripts, and kerning throughout.

## Files

| Purpose | URL |
|---|---|
| Drop-in stylesheet | `https://www.vigilfont.com/vigil.css` |
| Variable roman | `https://www.vigilfont.com/fonts/Vigil-wght-.woff2` |
| Variable italic | `https://www.vigilfont.com/fonts/Vigil-Italic-wght-.woff2` |
| Outline roman | `https://www.vigilfont.com/fonts/VigilOutline-Regular.woff2` |
| Outline italic | `https://www.vigilfont.com/fonts/VigilOutline-Italic.woff2` |
| Full family zip | `https://www.vigilfont.com/downloads/Vigil.zip` |
| License text | `https://www.vigilfont.com/OFL.txt` |

Static WOFF2 for all sixteen roman and italic weights are at `https://www.vigilfont.com/fonts/Vigil-{Weight}.woff2`, for example `Vigil-SemiBoldItalic.woff2`. TTF and OTF are inside the zip.

## Character set

Latin Extended: Western and Central European, covering English, Spanish, French, German, Polish, Czech and Turkish among others.

## License

SIL Open Font License 1.1. You may use Vigil in commercial work, embed it in apps and websites, sell products set in it, and use it in a logo or trademark. You may modify and redistribute it. The one restriction is that you may not sell the font files on their own. No attribution is required in your designs.

Derived from [Figtree](https://github.com/erikdkennedy/figtree) by Erik Kennedy, under the same license.

## Related

Vigil Icons is a companion set of stroke icons drawn to match the typeface: <https://www.vigilicons.com/>

Homepage and interactive specimen: <https://www.vigilfont.com/>
